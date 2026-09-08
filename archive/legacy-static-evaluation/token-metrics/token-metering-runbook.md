---
title: Metering coding-agent token usage through LiteLLM
category: Windows / Linux setup · Internal
environment: Windows 10/11 or AlmaLinux 8.10 VM · Python 3.12 · LiteLLM proxy · Azure OpenAI · GPT-5.4
time: ~30 min
---

# Metering coding-agent token usage through LiteLLM

Put a proxy between the coding agent and Azure OpenAI so every request's usage can be captured at a common measurement point and totaled per task.

The proxy can run either:

- **locally on the Windows workstation**, or
- **on a Linux VM in the same customer environment**, with Cursor/Codex reaching it directly or through SSH local port forwarding.

For the current customer environment, the preferred topology is the **AlmaLinux 8.10 VM**. The Windows workstation is locked down, while the Linux host gives us a cleaner place to run the proxy and keeps the measurement point inside the customer environment.

> **Current host note:** the AlmaLinux VM reports Python **3.4.3**. Do not use or replace that interpreter for LiteLLM. AlmaLinux 8.10 provides Python 3.12 as a parallel-installable package. Install and invoke `python3.12` explicitly so system tooling that depends on the existing Python installation is left alone.

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
| request count | Number of model calls used to complete the task. |

The meaningful comparison is the **whole task**, not an individual request.

---

## 01 · Install LiteLLM

### AlmaLinux 8.10 — current environment

First verify the host and existing interpreters:

```bash
cat /etc/almalinux-release
python3 --version
which python3
python3.12 --version 2>/dev/null || true
```

The currently observed `python3` version is 3.4.3. That is too old for this proxy setup and should be treated as a system/legacy interpreter, not upgraded in place.

AlmaLinux 8.10 includes Python 3.12 packages that can be installed alongside the existing interpreter.

If you have sudo, install Python 3.12 and its matching pip package:

```bash
sudo dnf install -y python3.12 python3.12-pip
```

If `dnf` is unavailable but `yum` is present:

```bash
sudo yum install -y python3.12 python3.12-pip
```

Verify the new interpreter explicitly:

```bash
python3.12 --version
python3.12 -m pip --version
```

Expected Python version:

```text
Python 3.12.x
```

> **Important:** do not change `/usr/bin/python`, `/usr/bin/python3`, alternatives, or the existing Python 3.4.3 installation. Use `python3.12` explicitly for the token-proxy environment.

Create a dedicated user-owned working directory and virtual environment:

```bash
mkdir -p "$HOME/token-metering"
cd "$HOME/token-metering"

python3.12 -m venv .venv
source .venv/bin/activate

python --version
python -m pip install --upgrade pip
python -m pip install "litellm[proxy]"
litellm --version
```

Once the venv is active, `python` and `pip` should resolve inside `.venv` and use Python 3.12.

Confirm:

```bash
which python
which pip
which litellm
```

They should point under:

```text
$HOME/token-metering/.venv/
```

#### If Python 3.12 packages are not visible

Check the enabled repositories and package availability before changing repository configuration:

```bash
sudo dnf repolist
sudo dnf list --available 'python3.12*'
```

If `python3.12` is not available, stop and confirm which AlmaLinux repositories are approved/enabled for the VM. Do not download an arbitrary Python build or replace the system interpreter simply to make the proxy work.

#### If `python3.12 -m venv` fails

First confirm the Python 3.12 installation:

```bash
rpm -qa | grep '^python3.12'
python3.12 -m pip --version
```

Do not fall back to Python 3.4.3. Resolve the Python 3.12 package/venv issue instead.

#### No sudo

If `python3.12` is already installed, no sudo is needed after that point; create the venv under your home directory as shown above.

If only Python 3.4.3 is available and you cannot install an approved newer interpreter, stop here. Do not modify the system Python. An administrator-installed Python 3.12 package or another approved runtime/container is required.

> **Every new shell:** run `source ~/token-metering/.venv/bin/activate` before using `litellm`.

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

Use the same Azure endpoint, deployment, and API version that the custom model already uses successfully.

### Linux / Bash

```bash
export AZURE_API_KEY="<azure-openai-key>"
export AZURE_API_BASE="https://<your-resource>.openai.azure.com/"
export AZURE_API_VERSION="<the api-version your Azure deployment uses>"
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

---

## 04 · Write the proxy config

Create `~/token-metering/config.yaml`:

```yaml
model_list:
  - model_name: gpt-5.4
    litellm_params:
      model: azure/<AZURE_DEPLOYMENT_NAME>
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION
    model_info:
      base_model: azure/gpt-5.4

litellm_settings:
  callbacks: usage_logger.proxy_handler_instance
  drop_params: true
```

`azure/<AZURE_DEPLOYMENT_NAME>` must use the actual Azure deployment name. `model_name: gpt-5.4` is the friendly model name exposed to the client.

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
ss -ltn | grep ':4000'
```

Expected shape:

```text
LISTEN ... 127.0.0.1:4000 ...
```

---

## 06 · Smoke-test before touching Cursor

From the Linux VM:

```bash
curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-local' \
  -d '{
    "model": "gpt-5.4",
    "messages": [
      {"role": "user", "content": "Say hello in one sentence."}
    ]
  }'
```

Then confirm a usage row was written:

```bash
tail -n 2 "$HOME/token-metering/token_usage.jsonl"
```

Do not change Cursor configuration until this succeeds and the log contains non-zero usage.

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
| `python3 --version` shows 3.4.3 | Expected on the current host. Do not use it. Install/use `python3.12` explicitly. |
| `python3.12: command not found` | Install `python3.12` and `python3.12-pip` from approved AlmaLinux 8.10 repositories. |
| `dnf` cannot find `python3.12` | Check enabled repositories with `dnf repolist` and package visibility with `dnf list --available 'python3.12*'`; do not replace system Python. |
| `python3.12 -m venv .venv` fails | Verify the Python 3.12 RPM stack and pip installation; do not fall back to Python 3.4.3. |
| `litellm: command not found` | Activate the venv: `source ~/token-metering/.venv/bin/activate`. |
| Linux `curl 127.0.0.1:4000` fails | Verify LiteLLM startup output and `ss -ltn \| grep ':4000'`. |
| SSH forwarding fails | Run `ssh -v -L 4000:127.0.0.1:4000 <user>@<linux-vm>`; check whether TCP forwarding is allowed and whether local port 4000 is already used. |
| Windows cannot reach Linux directly | Prefer SSH `-L`; otherwise request an approved firewall/network path. |
| Rows exist but token counts are zero | Verify the upstream API response actually includes usage and, for streaming APIs, that final usage is returned/aggregated. |
| `reasoning_tokens` is always zero | The deployment/API may not expose reasoning usage separately. Do not infer a value that was not returned. |
| Azure returns deployment 404 | Use the actual Azure deployment name in `azure/<deployment-name>`. |
| No `token_usage.jsonl` | Verify `usage_logger.py` is in the working directory and the callback imports successfully at LiteLLM startup. |
| Cursor prompt succeeds but no row appears | Cursor bypassed the proxy for that request; do not treat the proxy measurement as complete. |

---

## Stop conditions

Stop rather than altering the customer environment if any of the following are true:

- Python 3.12 cannot be installed through an approved repository and no approved runtime already exists.
- SSH forwarding is disabled and direct port access is not approved.
- Cursor cannot route the relevant custom-model requests through the proxy.
- The upstream model response does not expose the usage data required for the comparison.

Capture the LiteLLM startup output, connectivity test result, and last few JSONL rows when a step fails. Those usually identify whether the problem is installation, network reachability, proxy routing, or usage capture.