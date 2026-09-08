---
title: Metering coding-agent token usage through LiteLLM
category: Windows / Linux setup · Internal
environment: Windows 10/11 or Linux VM · Python 3.10+ · LiteLLM proxy · Azure OpenAI · GPT-5.4
time: ~30 min
---

# Metering coding-agent token usage through LiteLLM

Put a proxy between the coding agent and Azure OpenAI so every request's real token usage — input, cached input, output, and reasoning — lands in a file we can total per task and compare across agents.

The proxy can run either:

- **locally on the Windows workstation**, or
- **on a Linux VM in the same customer environment**, with Cursor/Codex reaching it directly or through SSH local port forwarding.

The Linux-VM topology is preferred when the Windows workstation is locked down but a nearby Linux host can run Python and LiteLLM.

**Tags:** Windows 10/11 · Linux · PowerShell · Bash · Python 3.10+ · LiteLLM proxy · Azure OpenAI · GPT-5.4 · ~30 min

## How the pieces fit

### Local Windows proxy

| Stage | Component | What it does |
|---|---|---|
| **Origin** | Coding agent | Codex CLI or Cursor, pointed at a local base URL instead of Azure. |
| **Measurement point** | LiteLLM → localhost:4000 | Holds the Azure credentials, forwards the call, writes one JSON line per request. |
| **Upstream** | Azure OpenAI | Your existing resource and API version — nothing changes on the Azure side. |
| **Model** | GPT-5.4 deployment | Returns usage that separates cached input and reasoning tokens. |

### Linux VM proxy

```text
Windows workstation / Cursor
        │
        │ OpenAI-compatible requests
        ▼
Linux VM :4000
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

## Contents

1. Install LiteLLM in a venv
2. Set the Azure credentials
3. Write the usage logger
4. Write the proxy config
5. Start the proxy
6. Smoke-test before touching the agent
7. Connect the coding agent to the proxy
8. Label runs so totals mean something
9. Roll the log up into a report
10. Run a comparison that's actually fair
- Linux VM connectivity options
- Troubleshooting
- If we outgrow the JSONL file

---

## What we're actually measuring

The number a coding agent shows in its own status line is not comparable across agents — each one counts differently, and some don't count reasoning tokens at all. The only trustworthy source is the `usage` object Azure returns on each API response, which is exactly what a proxy sits in a position to capture.

Two things make this worth the setup effort rather than eyeballing a console:

- **Reasoning tokens are billed as output tokens** but are never shown to the user. A three-line answer can carry tens of thousands of them. Any comparison that ignores them is wrong in the direction that matters for cost.
- **One task is many requests.** An agent fixing a bug will inspect, read files, plan, patch, run tests, and correct — each a separate call. The meaningful unit is the whole task, not a single request.

So the goal is a per-request log we can total per task, broken out into the columns that drive cost:

| Field | Why it's separate |
|---|---|
| `input_tokens` | Everything sent: system prompt, files, tool schemas, conversation so far. |
| `cached_input_tokens` | The slice Azure served from prompt cache — billed at a discount. |
| `uncached_input_tokens` | Input minus cached. This is the real input cost driver. |
| `output_tokens` | Everything generated, reasoning included. |
| `reasoning_tokens` | Hidden thinking. Usually the largest surprise in an agent workload. |
| `visible_output_tokens` | Output minus reasoning — what actually reached the editor. |
| request count | How chatty the agent's loop is. Varies more between agents than per-call size does. |

---

## 01 · Install LiteLLM in a virtual environment

Do this in a dedicated folder. The proxy needs to run from the folder holding the config and the logger script, because it imports the logger by module name.

### Windows / PowerShell

```powershell
mkdir $HOME\token-metering
cd $HOME\token-metering

py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install "litellm[proxy]"
litellm --version
```

> **If activation is blocked:** PowerShell refuses unsigned scripts by default. `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` unblocks it for the current window only, which is the least invasive fix.

> **Every new terminal:** Re-run `.\.venv\Scripts\Activate.ps1` from the project folder.

### Linux / Bash

First check what is already available:

```bash
python3 --version
which python3
```

Python 3.10 or newer is preferred.

Create a dedicated working directory and virtual environment:

```bash
mkdir -p "$HOME/token-metering"
cd "$HOME/token-metering"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install "litellm[proxy]"
litellm --version
```

If `python3 -m venv` fails because the venv package is missing, install the distribution package if you have sudo:

**Ubuntu / Debian:**

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
```

**RHEL / Rocky / Alma / CentOS Stream / Fedora:**

```bash
sudo dnf install -y python3 python3-pip
```

On older RPM-based systems where `dnf` is unavailable:

```bash
sudo yum install -y python3 python3-pip
```

Then retry:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "litellm[proxy]"
```

> **No sudo?** If `python3`, `pip`, and `venv` are already available, no sudo is required. If `venv` is missing and you cannot install packages, stop here rather than modifying system Python. A user-local Python environment or approved container may be needed.

> **Every new shell:** Run `source ~/token-metering/.venv/bin/activate` before using `litellm`.

---

## 02 · Set the Azure credentials

LiteLLM reads Azure config from `AZURE_*` variables — not `OPENAI_*`. Use the same endpoint and API version the agent already talks to successfully today.

### Windows / PowerShell

```powershell
$env:AZURE_API_KEY     = "<azure-openai-key>"
$env:AZURE_API_BASE    = "https://<your-resource>.openai.azure.com/"
$env:AZURE_API_VERSION = "<the api-version your Azure deployment uses>"
```

### Linux / Bash

```bash
export AZURE_API_KEY="<azure-openai-key>"
export AZURE_API_BASE="https://<your-resource>.openai.azure.com/"
export AZURE_API_VERSION="<the api-version your Azure deployment uses>"
```

Confirm the variables are present without printing the key itself:

```bash
printf 'AZURE_API_BASE=%s\n' "$AZURE_API_BASE"
printf 'AZURE_API_VERSION=%s\n' "$AZURE_API_VERSION"
[ -n "$AZURE_API_KEY" ] && echo "AZURE_API_KEY is set"
```

> **After this is working:** Remove the Azure key from the coding agent's own config. LiteLLM should be the component holding the real credential; the agent can authenticate to LiteLLM with a throwaway local value if required by the client.

These environment variables disappear when the shell closes. That is the safer default. Do not commit credentials into `config.yaml`, scripts, shell history, or Git.

---

## 03 · Write the usage logger

This is the part that makes the exercise useful. LiteLLM lets you register a callback class that fires after every completed request; ours pulls the usage object apart and appends one JSON line per call. It handles both field-name conventions because Chat Completions and Responses APIs name the same numbers differently.

**`usage_logger.py`**

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

    inp   = u.get("prompt_tokens")     or u.get("input_tokens")  or 0
    out   = u.get("completion_tokens") or u.get("output_tokens") or 0
    total = u.get("total_tokens") or (inp + out)

    in_det  = _d(u.get("prompt_tokens_details")     or u.get("input_tokens_details"))
    out_det = _d(u.get("completion_tokens_details") or u.get("output_tokens_details"))

    cached    = in_det.get("cached_tokens")     or 0
    reasoning = out_det.get("reasoning_tokens") or 0

    return {
        "input_tokens":          inp,
        "cached_input_tokens":   cached,
        "uncached_input_tokens": max(inp - cached, 0),
        "output_tokens":         out,
        "reasoning_tokens":      reasoning,
        "visible_output_tokens": max(out - reasoning, 0),
        "total_tokens":          total,
    }


class TokenUsageLogger(CustomLogger):

    def _write(self, kwargs, response_obj, start_time, end_time):
        meta    = (kwargs.get("litellm_params") or {}).get("metadata") or {}
        headers = meta.get("headers") or {}

        row = {
            "ts":        datetime.now(timezone.utc).isoformat(),
            "run":       headers.get("x-run-label") or os.environ.get("RUN_LABEL", "unlabeled"),
            "model":     kwargs.get("model"),
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

**`config.yaml`**

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

### The deployment name is not the model name

In Azure, `litellm_params.model` must be `azure/` followed by the deployment name configured in Azure. If the deployment is `coding-agent-gpt54-prod`, use:

```yaml
model: azure/coding-agent-gpt54-prod
```

`model_name: gpt-5.4` is the friendly model name exposed to the client.

`drop_params: true` tells LiteLLM to strip unsupported parameters rather than failing the whole request.

---

## 05 · Start the proxy

### Windows — local only

```powershell
litellm --config .\config.yaml --host 127.0.0.1 --port 4000
```

### Linux — local-only first

Start with loopback only until the proxy itself is proven:

```bash
cd "$HOME/token-metering"
source .venv/bin/activate
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

Leave this shell open.

From a second Linux shell, confirm it is listening:

```bash
ss -ltn | grep ':4000'
```

Expected shape:

```text
LISTEN ... 127.0.0.1:4000 ...
```

> **Security:** Do not bind an unauthenticated proxy to `0.0.0.0` until you know exactly which hosts can reach it. Anyone who can reach the proxy could potentially consume the configured Azure quota.

---

## 06 · Smoke-test before touching the agent

### Linux / Bash — Chat Completions

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

### Linux / Bash — Responses API

```bash
curl -sS http://127.0.0.1:4000/v1/responses \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-local' \
  -d '{
    "model": "gpt-5.4",
    "input": "Say hello in one sentence."
  }'
```

Then confirm rows were written:

```bash
tail -n 2 token_usage.jsonl
```

You should see non-zero `input_tokens` and `output_tokens`.

### Windows / PowerShell — local proxy

```powershell
$body = @{
    model    = "gpt-5.4"
    messages = @( @{ role = "user"; content = "Say hello in one sentence." } )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 10
```

> Do not change Cursor/Codex configuration until the local Linux smoke test succeeds and `token_usage.jsonl` is growing.

---

## 07 · Connect the coding agent to the proxy

### Option A — Windows can reach the Linux VM directly

If the Windows workstation can reach an approved TCP port on the Linux VM, bind LiteLLM to the Linux VM interface:

```bash
litellm --config ./config.yaml --host 0.0.0.0 --port 4000
```

Find the Linux VM's address:

```bash
hostname -I
```

From Windows, test connectivity before changing the agent:

```powershell
Test-NetConnection <LINUX_VM_IP> -Port 4000
```

Then smoke-test the API from Windows:

```powershell
$body = @{
    model    = "gpt-5.4"
    messages = @( @{ role = "user"; content = "Say hello in one sentence." } )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://<LINUX_VM_IP>:4000/v1/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 10
```

If that works, the client base URL is:

```text
http://<LINUX_VM_IP>:4000/v1
```

> Only use direct network exposure if it is approved for the environment. Prefer firewall/network controls that limit access to the Windows workstation rather than opening port 4000 broadly.

### Option B — use SSH local port forwarding

This is preferred when Windows can SSH to the Linux VM but cannot or should not access port 4000 directly.

Keep LiteLLM bound to loopback on Linux:

```bash
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

From Windows PowerShell:

```powershell
ssh -L 4000:127.0.0.1:4000 <user>@<linux-vm>
```

Leave that SSH session open.

Now Windows `localhost:4000` tunnels to Linux `localhost:4000`.

Test from a second PowerShell window:

```powershell
Test-NetConnection localhost -Port 4000
```

Then call the proxy:

```powershell
$body = @{
    model    = "gpt-5.4"
    messages = @( @{ role = "user"; content = "Say hello in one sentence." } )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 10
```

If this succeeds, the coding agent can continue to use:

```text
http://localhost:4000/v1
```

while LiteLLM remains inaccessible directly from the network.

### Codex CLI

Codex reads `%USERPROFILE%\.codex\config.toml`:

```toml
model = "gpt-5.4"
model_provider = "litellm"

[model_providers.litellm]
name     = "LiteLLM proxy"
base_url = "http://localhost:4000/v1"
env_key  = "LITELLM_API_KEY"
wire_api = "responses"
```

Then:

```powershell
$env:LITELLM_API_KEY = "sk-local"
codex
```

If using direct Linux-VM access rather than SSH forwarding, replace `localhost` with the Linux VM IP or approved hostname.

### Cursor

Configure the custom OpenAI base URL in Cursor to point at the proxy:

```text
SSH-forwarded proxy:  http://localhost:4000/v1
Direct Linux proxy:   http://<LINUX_VM_IP>:4000/v1
```

Use the same custom model name that LiteLLM exposes (`gpt-5.4` in the example).

> **Important measurement caveat:** confirm empirically that the Cursor requests you care about appear in the LiteLLM logs. If some Cursor traffic bypasses the custom OpenAI base URL, the proxy will undercount that workflow. Do not treat the measurement as complete until a trivial Cursor prompt is visible in `token_usage.jsonl`.

---

## 08 · Label runs so the totals mean something

Every row needs to say which task it belongs to.

### Windows

```powershell
$env:RUN_LABEL = "cursor--nd-baseline--run1"
```

### Linux

Set the label in the shell that launches LiteLLM:

```bash
export RUN_LABEL="cursor--nd-baseline--run1"
litellm --config ./config.yaml --host 127.0.0.1 --port 4000
```

For the simplest controlled test, run one task per proxy session and restart LiteLLM with a new `RUN_LABEL` between runs.

A useful naming convention is:

```text
<agent>--<workflow>--<run>
```

Examples:

```text
cursor--customer-baseline--run1
cursor--corestory-assisted--run1
```

---

## 09 · Roll the log up into a report

### Linux / Python

The following uses only the Python standard library:

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

### Windows / PowerShell

```powershell
$rows = Get-Content .\token_usage.jsonl | ForEach-Object { $_ | ConvertFrom-Json }

$rows | Group-Object run | ForEach-Object {
    [pscustomobject]@{
        Run       = $_.Name
        Calls     = $_.Count
        Input     = ($_.Group | Measure-Object input_tokens          -Sum).Sum
        Cached    = ($_.Group | Measure-Object cached_input_tokens   -Sum).Sum
        Uncached  = ($_.Group | Measure-Object uncached_input_tokens -Sum).Sum
        Output    = ($_.Group | Measure-Object output_tokens         -Sum).Sum
        Reasoning = ($_.Group | Measure-Object reasoning_tokens      -Sum).Sum
        Visible   = ($_.Group | Measure-Object visible_output_tokens -Sum).Sum
        Total     = ($_.Group | Measure-Object total_tokens          -Sum).Sum
    }
} | Sort-Object Run | Format-Table -AutoSize
```

---

## 10 · Run a comparison that's actually fair

Hold these constant:

- **Repository state.** Same commit for every run; reset between runs.
- **Task text.** Byte-identical prompt for each workflow.
- **Model.** Same deployed model.
- **Reasoning effort.** Pin it if possible.
- **Cache state.** Avoid comparing a cold run against a warm run.
- **Tool availability.** Make sure the only intended workflow difference is the one being evaluated.

For the ND comparison, a practical structure is:

```text
Run A — customer workflow baseline
Run B — customer workflow + CoreStory application intelligence
```

Use the same repository snapshot, prompt, custom model, Cursor version, skills, and task scope.

Report at minimum:

- request count,
- input tokens,
- cached input tokens,
- uncached input tokens,
- output tokens,
- reasoning tokens,
- total task completion result.

Do not interpret a token difference by itself as quality improvement. Pair the measurement with the validation outcome and work performed.

---

## Linux VM connectivity options

Use these in order of preference:

1. **Local-only Linux proxy + SSH `-L` forwarding** — preferred when SSH is available; proxy is not network-exposed.
2. **Direct private-network access** — acceptable when Windows can reach the Linux VM and the environment permits the port.
3. **External tunneling such as ngrok** — only if approved and the first two options are unavailable.

Do not introduce an external tunnel simply to bypass customer network controls. Treat rejected SSH forwarding or blocked ports as environment constraints that need approval, not as controls to evade.

### SSH forwarding fails

Run from Windows with verbose output:

```powershell
ssh -v -L 4000:127.0.0.1:4000 <user>@<linux-vm>
```

Common causes:

- SSH server has `AllowTcpForwarding no`,
- local port 4000 is already in use on Windows,
- LiteLLM is not listening on Linux port 4000,
- SSH reaches a different host/network namespace than the proxy process.

To use a different Windows-side port while keeping Linux on 4000:

```powershell
ssh -L 4100:127.0.0.1:4000 <user>@<linux-vm>
```

Then point Cursor/Codex at:

```text
http://localhost:4100/v1
```

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Linux `python3 -m venv .venv` fails | Install the distribution's venv package if allowed, or use an approved user-local Python environment. |
| `litellm: command not found` on Linux | The venv is not active. Run `source ~/token-metering/.venv/bin/activate`. |
| `curl localhost:4000` fails on Linux | LiteLLM is not running/listening, or it started on a different port. Check `ss -ltn \| grep 4000`. |
| Windows cannot reach Linux port 4000 | Keep the proxy on `127.0.0.1` and use `ssh -L`, or request an approved firewall/network path. |
| SSH tunnel opens but Windows call fails | Verify Linux can call `127.0.0.1:4000` locally first; then use `ssh -v` to inspect forwarding. |
| Rows land in the log but all token counts are `0` | Streaming response with no usage attached. On Chat Completions the client must send `stream_options: {"include_usage": true}`; on Responses API verify LiteLLM aggregates the final usage event. |
| `reasoning_tokens` always 0, everything else populated | API version may predate reasoning-usage reporting, or the deployment may not expose reasoning usage. |
| `DeploymentNotFound` / 404 from Azure | `litellm_params.model` must use `azure/<deployment-name>`, not the friendly model name. |
| Unsupported parameter errors | Keep `drop_params: true`; also verify LiteLLM recognizes the actual base model. |
| No `token_usage.jsonl` at all | The callback did not import. Start LiteLLM from the folder containing `usage_logger.py` and verify the callback path. |
| Cursor prompt succeeds but no proxy row appears | That request bypassed the configured custom base URL. The proxy measurement is incomplete for that Cursor workflow. |

---

## If we outgrow the JSONL file

LiteLLM can use database-backed spend tracking and an admin UI, but the flat JSONL file is preferable for this controlled comparison because it is simple, auditable, greppable, and easy to share.

Move to persistent database-backed tracking only when we need multiple users, longer-term history, per-developer keys, or centralized cost reporting.

---

*If a step fails, capture the LiteLLM startup output, the exact connectivity test result, and the last few lines of `token_usage.jsonl`. That is usually enough to identify whether the problem is installation, network reachability, proxy routing, or usage capture.*