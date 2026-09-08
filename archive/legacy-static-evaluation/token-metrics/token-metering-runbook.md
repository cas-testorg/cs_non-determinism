---
title: Metering coding-agent token usage through LiteLLM
category: Windows / Linux setup · Internal
environment: Windows 10/11 or AlmaLinux 8.10 VM · Python 3.12 · LiteLLM proxy · Azure OpenAI · GPT-5.4
time: ~30–60 min
---

# Metering coding-agent token usage through LiteLLM

Put a proxy between the coding agent and Azure OpenAI so every request's usage can be captured at a common measurement point and totaled per task.

The proxy can run either:

- **locally on the Windows workstation**, or
- **on a Linux VM in the same customer environment**, with Cursor/Codex reaching it directly or through SSH local port forwarding.

For the current customer environment, the preferred topology is the **AlmaLinux 8.10 VM**. The Windows workstation is locked down, while the Linux host gives us a cleaner place to run the proxy and keeps the measurement point inside the customer environment.

> **Validated current host:** AlmaLinux 8.10, login shell `/bin/tcsh`, system `python3` = **3.6.8**, no sudo access. Python **3.12.14** was successfully built from source and installed under `$HOME/.local/python3.12` without modifying the system Python.

## How the pieces fit

### Preferred Linux VM topology

```text
Windows workstation / Cursor
        │
        │ OpenAI-compatible requests
        ▼
Linux VM / AlmaLinux 8.10
┌─────────────────────────┐
│ LiteLLM token proxy     │
│ - forwards requests     │
│ - captures usage        │
│ - writes JSONL          │
└────────────┬────────────┘
             │
             ▼
       Azure OpenAI
```

If Windows cannot reach port 4000 directly, keep LiteLLM bound to loopback on Linux and tunnel it over SSH:

```text
Windows localhost:4000
        │
        │ ssh -L
        ▼
Linux localhost:4000
        │
        ▼
LiteLLM → Azure OpenAI
```

This avoids exposing the proxy to the network and keeps the metering point inside the customer environment.

## What we're measuring

The goal is a per-request log that can be totaled per task. Capture, when returned by the upstream API:

| Field | Purpose |
|---|---|
| `input_tokens` | Total request input. |
| `cached_input_tokens` | Input served from prompt cache. |
| `uncached_input_tokens` | Input minus cached input. |
| `output_tokens` | Generated output, including reasoning where reported that way. |
| `reasoning_tokens` | Reasoning usage when exposed by the API. |
| `visible_output_tokens` | Output minus reasoning. |
| `total_tokens` | Total input plus output reported by the API. |
| request count | Number of model calls used to complete the task. |

The meaningful comparison is the **whole task**, not an individual request.

---

## 01 · Install LiteLLM

### AlmaLinux 8.10 — validated no-sudo path

The current login shell is `tcsh`. The commands in this runbook use Bash syntax, so start Bash first:

```bash
bash
```

Verify the host and existing interpreter:

```bash
cat /etc/almalinux-release
python3 --version
which python3
python3.12 --version 2>/dev/null || true
```

Observed on the current host:

```text
AlmaLinux release 8.10 (Cerulean Leopard)
Python 3.6.8
/bin/python3
```

Do not replace `/bin/python3` or change system alternatives.

Python 3.12 packages are visible in the AlmaLinux repositories, but the current user does not have permission to install them with `sudo dnf`. The validated alternative is a user-local source build.

Before compiling, verify the required compiler and development libraries are already installed:

```bash
gcc --version
make --version
openssl version
rpm -q gcc make openssl-devel zlib-devel libffi-devel bzip2-devel xz-devel readline-devel sqlite-devel
```

The current host has the required packages, including GCC 8.5, GNU Make 4.2.1, OpenSSL 1.1.1k, and the required development libraries.

Download and build Python 3.12.14 under the user's home directory:

```bash
mkdir -p "$HOME/token-metering"
cd "$HOME/token-metering"

curl -O https://www.python.org/ftp/python/3.12.14/Python-3.12.14.tgz
tar -xzf Python-3.12.14.tgz
cd Python-3.12.14

./configure --prefix="$HOME/.local/python3.12" --with-ensurepip=install
make -j2
make install
```

`-j2` intentionally limits build parallelism on the shared/customer VM.

Verify the user-local interpreter and pip:

```bash
$HOME/.local/python3.12/bin/python3.12 --version
$HOME/.local/python3.12/bin/python3.12 -m pip --version
```

Validated output:

```text
Python 3.12.14
pip 25.0.1 from /u/carys/.local/python3.12/lib/python3.12/site-packages/pip (python 3.12)
```

Create the LiteLLM virtual environment using that exact interpreter:

```bash
cd "$HOME/token-metering"
$HOME/.local/python3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate

python --version
python -m pip install --upgrade pip
python -m pip install "litellm[proxy]"
litellm --version
```

Confirm the environment resolves locally:

```bash
which python
which pip
which litellm
```

They should point under:

```text
$HOME/token-metering/.venv/
```

> **Every new shell:** if the account starts in `tcsh`, run `bash` first, then `source ~/token-metering/.venv/bin/activate`.

### AlmaLinux alternative when sudo is available

AlmaLinux 8.10 exposes Python 3.12 packages. If administrative installation is approved:

```bash
sudo dnf install -y python3.12 python3.12-pip
python3.12 --version
python3.12 -m pip --version
```

Then create `.venv` with `python3.12 -m venv .venv`. Do not replace the system Python.

### Windows / PowerShell alternative

```powershell
mkdir $HOME\token-metering
cd $HOME\token-metering

py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install "litellm[proxy]"
litellm --version
```

---

## 02 · Set the Azure credentials

Use the same Azure endpoint, model/deployment, and API version that the custom model already uses successfully.

The validated custom-model configuration uses:

```text
model = gpt-5.4
provider = azure
wire API = responses
reasoning effort = medium
base URL = https://corestory-genai-sa.openai.azure.com/openai/v1
```

For LiteLLM, export the Azure values in the shell that launches the proxy:

```bash
export AZURE_API_KEY="<azure-openai-key>"
export AZURE_API_BASE="https://corestory-genai-sa.openai.azure.com/"
export AZURE_API_VERSION="2025-04-01-preview"
```

Confirm the variables without printing the key:

```bash
printf 'AZURE_API_BASE=%s\n' "$AZURE_API_BASE"
printf 'AZURE_API_VERSION=%s\n' "$AZURE_API_VERSION"
[ -n "$AZURE_API_KEY" ] && echo "AZURE_API_KEY is set"
```

Do not commit credentials into Git, `config.yaml`, scripts, or shell history.

---

## 03 · Write the usage logger

Create `~/token-metering/usage_logger.py`:

```python
import json, os, threading
from datetime import datetime, timezone
from pathlib import Path
from litellm.integrations.custom_logger import CustomLogger

LOG_PATH = Path(os.environ.get("TOKEN_LOG", "token_usage.jsonl"))
_lock = threading.Lock()


def _d(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    return getattr(obj, "__dict__", {}) or {}


def _usage(response_obj):
    u = _d(_d(response_obj).get("usage") or getattr(response_obj, "usage", None))
    inp = u.get("prompt_tokens") or u.get("input_tokens") or 0
    out = u.get("completion_tokens") or u.get("output_tokens") or 0
    total = u.get("total_tokens") or (inp + out)
    in_det = _d(u.get("prompt_tokens_details") or u.get("input_tokens_details"))
    out_det = _d(u.get("completion_tokens_details") or u.get("output_tokens_details"))
    cached = in_det.get("cached_tokens") or 0
    reasoning = out_det.get("reasoning_tokens") or 0
    return {
        "input_tokens": inp,
        "cached_input_tokens": cached,
        "uncached_input_tokens": max(inp - cached, 0),
        "output_tokens": out,
        "reasoning_tokens": reasoning,
        "visible_output_tokens": max(out - reasoning, 0),
        "total_tokens": total,
    }


class TokenUsageLogger(CustomLogger):
    def _write(self, kwargs, response_obj, start_time, end_time):
        meta = (kwargs.get("litellm_params") or {}).get("metadata") or {}
        headers = meta.get("headers") or {}
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run": headers.get("x-run-label") or os.environ.get("RUN_LABEL", "unlabeled"),
            "model": kwargs.get("model"),
            "call_type": kwargs.get("call_type"),
            "latency_s": round((end_time - start_time).total_seconds(), 3)
                         if start_time and end_time else None,
            **_usage(response_obj),
        }
        with _lock, LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj, start_time, end_time)
        except Exception as e:
            print(f"[usage_logger] skipped a row: {e}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj, start_time, end_time)
        except Exception as e:
            print(f"[usage_logger] skipped a row: {e}")


proxy_handler_instance = TokenUsageLogger()
```

The logger supports both Chat Completions-style usage names and Responses API usage names, including `input_tokens_details.cached_tokens` and `output_tokens_details.reasoning_tokens`.

---

## 04 · Write the proxy config

Create `~/token-metering/config.yaml`:

```yaml
model_list:
  - model_name: gpt-5.4
    litellm_params:
      model: azure/gpt-5.4
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION

litellm_settings:
  callbacks: usage_logger.proxy_handler_instance
  drop_params: true
```

This configuration has been validated against the current Azure GPT-5.4 deployment.

---

## 05 · Start the proxy locally on AlmaLinux first

Do not expose the proxy to Windows yet. First prove the entire proxy-to-Azure path locally:

```bash
cd "$HOME/token-metering"
source .venv/bin/activate
export RUN_LABEL="linux-smoke-test"
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

Leave that shell open.

From a second SSH/Linux shell:

```bash
bash
cd "$HOME/token-metering"
source .venv/bin/activate
ss -ltn | grep ':4000'
```

Validated listener shape:

```text
LISTEN ... 127.0.0.1:4000 ...
```

---

## 06 · Smoke-test the Responses API before touching Cursor

The working custom model uses the OpenAI Responses API, so the primary smoke test should exercise `/v1/responses` and preserve the configured reasoning effort:

```bash
curl -sS http://127.0.0.1:4000/v1/responses \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-local' \
  -d '{
    "model": "gpt-5.4",
    "input": "Reply with exactly: proxy test successful",
    "reasoning": {
      "effort": "medium"
    }
  }'
```

A successful response should contain:

```text
proxy test successful
```

and a `usage` object containing non-zero token counts.

Then confirm the custom logger wrote a row:

```bash
cat "$HOME/token-metering/token_usage.jsonl"
```

Validated example:

```json
{"ts":"<timestamp>","run":"unlabeled","model":"gpt-5.4","call_type":"aresponses","latency_s":1.815,"input_tokens":13,"cached_input_tokens":0,"uncached_input_tokens":13,"output_tokens":22,"reasoning_tokens":13,"visible_output_tokens":9,"total_tokens":35}
```

The exact counts can vary between calls. What matters at this checkpoint is that the proxy succeeds and the logger records the upstream usage breakdown, including reasoning and visible-output tokens.

At this point the following measurement path is proven:

```text
local curl → LiteLLM :4000 → Azure OpenAI / GPT-5.4 → Responses API → token_usage.jsonl
```

Do not change Cursor configuration until this succeeds.

---

## 07 · Connect Windows / Cursor to the Linux proxy

### Option A — SSH local port forwarding (preferred)

Keep LiteLLM bound to `127.0.0.1:4000` on Linux.

From Windows PowerShell:

```powershell
ssh -L 4000:127.0.0.1:4000 <user>@<linux-vm>
```

Leave the SSH session open. In a second PowerShell window:

```powershell
Test-NetConnection localhost -Port 4000
```

Cursor's custom OpenAI base URL becomes:

```text
http://localhost:4000/v1
```

This topology does not require opening port 4000 on the Linux VM.

### Option B — direct private-network access

Only use this if the environment permits the Windows workstation to connect directly to the Linux VM.

Start LiteLLM on the Linux host with:

```bash
litellm --config ./config.yaml --host 0.0.0.0 --port 4000
```

Find the VM address:

```bash
hostname -I
```

From Windows:

```powershell
Test-NetConnection <LINUX_VM_IP> -Port 4000
```

Cursor base URL:

```text
http://<LINUX_VM_IP>:4000/v1
```

Do not expose an unauthenticated proxy broadly. Prefer SSH forwarding or approved firewall rules restricted to the workstation.

### Option C — external tunnel

Use ngrok or another external tunnel only if explicitly approved and both SSH forwarding and approved private-network access are unavailable. Do not use an external tunnel to bypass customer network controls.

---

## 08 · Prove Cursor is actually using the proxy

Before running a baseline, send one trivial Cursor prompt through the custom model.

On Linux:

```bash
tail -f "$HOME/token-metering/token_usage.jsonl"
```

A new row must appear when Cursor sends the prompt.

If Cursor succeeds but no row appears, the request bypassed the configured custom base URL. The proxy is not a valid measurement point for that workflow until that routing issue is resolved.

---

## 09 · Label controlled runs

Set the label in the Linux shell that launches LiteLLM:

```bash
export RUN_LABEL="cursor--customer-baseline--run1"
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

For the CoreStory-assisted run:

```bash
export RUN_LABEL="cursor--corestory-assisted--run1"
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

For the simplest controlled test, use one task per proxy session and restart LiteLLM with a new label between runs.

---

## 10 · Roll the JSONL into totals

From the active Python 3.12 venv:

```bash
python - <<'PY'
import json
from collections import defaultdict

fields = [
    "input_tokens",
    "cached_input_tokens",
    "uncached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "visible_output_tokens",
    "total_tokens",
]

runs = defaultdict(lambda: {"calls": 0, **{f: 0 for f in fields}})

with open("token_usage.jsonl", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        row = json.loads(line)
        r = runs[row.get("run", "unlabeled")]
        r["calls"] += 1
        for field in fields:
            r[field] += int(row.get(field) or 0)

header = ["run", "calls", *fields]
print("\t".join(header))
for name in sorted(runs):
    r = runs[name]
    print("\t".join(str(x) for x in [name, r["calls"], *(r[f] for f in fields)]))
PY
```

---

## 11 · Run a fair comparison

Hold these constant:

- repository state,
- task text,
- model/deployment,
- reasoning effort where configurable,
- cache state or explicitly account for cached input,
- Cursor version,
- customer skills,
- task scope,
- intended tool availability.

For the ND comparison:

```text
Run A — customer workflow baseline
Run B — customer workflow + CoreStory application intelligence
```

Report at minimum:

- request count,
- input tokens,
- cached input tokens,
- uncached input tokens,
- output tokens,
- reasoning tokens when reported,
- task completion / validation result.

Do not interpret token difference by itself as a quality improvement. Pair usage with the validation outcome and work performed.

---

## Troubleshooting

| Symptom | Cause / next check |
|---|---|
| Bash redirection reports `Ambiguous output redirect` | The account is probably still in `tcsh`. Run `bash` before using the Bash commands in this runbook. |
| `python3 --version` shows 3.6.8 | Expected on the current host. Do not use or replace it for LiteLLM. Use the user-local Python 3.12 installation. |
| `python3.12: command not found` and sudo is unavailable | Verify build dependencies with the `rpm -q` command above, then use the validated user-local Python 3.12 source-build path. |
| Python source build lacks SSL/zlib/etc. | Stop and verify the matching `*-devel` packages before continuing; do not accept a partially functional Python build. |
| `litellm: command not found` | Start Bash if needed and activate the venv: `source ~/token-metering/.venv/bin/activate`. |
| Linux `curl 127.0.0.1:4000` fails | Verify LiteLLM startup output and `ss -ltn \| grep ':4000'`. |
| Responses API request fails while another API works | Confirm the custom model's wire API and test `/v1/responses`; the validated configuration uses Responses API. |
| SSH forwarding fails | Run `ssh -v -L 4000:127.0.0.1:4000 <user>@<linux-vm>`; check whether TCP forwarding is allowed and whether local port 4000 is already used. |
| Windows cannot reach Linux directly | Prefer SSH `-L`; otherwise request an approved firewall/network path. |
| Rows exist but token counts are zero | Verify the upstream API response actually includes usage and, for streaming APIs, that final usage is returned/aggregated. |
| `reasoning_tokens` is always zero | The deployment/API may not expose reasoning usage separately. Do not infer a value that was not returned. |
| Azure returns deployment 404 | Confirm the model/deployment mapping. The current validated LiteLLM mapping is `azure/gpt-5.4`. |
| No `token_usage.jsonl` | Verify `usage_logger.py` is in the working directory and the callback imports successfully at LiteLLM startup. |
| Cursor prompt succeeds but no row appears | Cursor bypassed the proxy for that request; do not treat the proxy measurement as complete. |

---

## Stop conditions

Stop rather than altering the customer environment if any of the following are true:

- Required source-build dependencies are absent and cannot be installed through an approved path.
- SSH forwarding is disabled and direct port access is not approved.
- Cursor cannot route the relevant custom-model requests through the proxy.
- The upstream model response does not expose the usage data required for the comparison.

Capture the LiteLLM startup output, connectivity test result, and last few JSONL rows when a step fails. Those usually identify whether the problem is installation, network reachability, proxy routing, or usage capture.
