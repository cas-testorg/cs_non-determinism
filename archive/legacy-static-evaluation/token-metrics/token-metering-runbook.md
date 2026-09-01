---
title: Metering coding-agent token usage through LiteLLM
category: Windows setup · Internal
environment: Windows 10/11 · PowerShell · Python 3.10+ · LiteLLM proxy · Azure OpenAI · GPT-5.4
time: ~30 min
---

# Metering coding-agent token usage through LiteLLM

Put a local proxy between the coding agent and Azure OpenAI so every request's real token usage — input, cached input, output, and reasoning — lands in a file we can total per task and compare across agents.

**Tags:** Windows 10/11 · PowerShell · Python 3.10+ · LiteLLM proxy · Azure OpenAI · GPT-5.4 · ~30 min

## How the pieces fit

| Stage | Component | What it does |
|---|---|---|
| **Origin** | Coding agent | Codex CLI, pointed at a local base URL instead of Azure. |
| **Measurement point** | LiteLLM → localhost:4000 | Holds the Azure credentials, forwards the call, writes one JSON line per request. |
| **Upstream** | Azure OpenAI | Your existing resource and API version — nothing changes on the Azure side. |
| **Model** | GPT-5.4 deployment | Returns usage that separates cached input and reasoning tokens. |

## Contents

1. Install LiteLLM in a venv
2. Set the Azure credentials
3. Write the usage logger
4. Write the proxy config
5. Start the proxy
6. Smoke-test before touching the agent
7. Point Codex CLI at the proxy
8. Label runs so totals mean something
9. Roll the log up into a report
10. Run a comparison that's actually fair
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

```powershell
# Pick a home for this. Anywhere you like.
mkdir $HOME\token-metering
cd $HOME\token-metering

# Confirm Python first — 3.10 or newer.
py --version

# Virtual environment keeps this off your system Python.
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install "litellm[proxy]"
litellm --version
```

> **If activation is blocked:** PowerShell refuses unsigned scripts by default. `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` unblocks it for the current window only, which is the least invasive fix. You'll need it in every new terminal, or set the scope to `CurrentUser` once.

> **Every new terminal:** Re-run `.\.venv\Scripts\Activate.ps1` from the project folder. Most "`litellm` is not recognized" reports are a terminal where the venv isn't active.

---

## 02 · Set the Azure credentials

LiteLLM reads Azure config from `AZURE_*` variables — not `OPENAI_*`. Set them in the window you'll start the proxy from:

```powershell
$env:AZURE_API_KEY     = "<azure-openai-key>"
$env:AZURE_API_BASE    = "https://<your-resource>.openai.azure.com/"
$env:AZURE_API_VERSION = "<the api-version your Azure deployment uses>"
```

Use the same endpoint and API version the agent already talks to successfully today. Don't guess an API version — GPT-5.4 features get gated by it, and a version that's too old will silently drop `reasoning_effort` or reject tool calls.

> **After this is working:** Remove the Azure key from the coding agent's own config. From here on, LiteLLM is the only thing that holds the real credential; the agent authenticates to LiteLLM with a throwaway value.

These vanish when you close the terminal, which is the safer default. If you want them to persist, use `[Environment]::SetEnvironmentVariable("AZURE_API_KEY","<key>","User")` — but be aware that writes the key to your user registry hive in plain text.

---

## 03 · Write the usage logger

This is the part that makes the exercise useful. LiteLLM lets you register a callback class that fires after every completed request; ours pulls the usage object apart and appends one JSON line per call. Note that it handles *both* field-name conventions, because the Chat Completions and Responses APIs name the same numbers differently.

**`usage_logger.py`**

```python
import json, os, threading
from datetime import datetime, timezone
from pathlib import Path
from litellm.integrations.custom_logger import CustomLogger

LOG_PATH = Path(os.environ.get("TOKEN_LOG", "token_usage.jsonl"))
_lock = threading.Lock()


def _d(obj):
    # usage may arrive as a dict or as a pydantic model, depending on route
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

    # Chat Completions ....... prompt_tokens / completion_tokens
    # Responses API .......... input_tokens  / output_tokens
    inp   = u.get("prompt_tokens")     or u.get("input_tokens")  or 0
    out   = u.get("completion_tokens") or u.get("output_tokens") or 0
    total = u.get("total_tokens") or (inp + out)

    in_det  = _d(u.get("prompt_tokens_details")     or u.get("input_tokens_details"))
    out_det = _d(u.get("completion_tokens_details") or u.get("output_tokens_details"))

    cached    = in_det.get("cached_tokens")     or 0
    reasoning = out_det.get("reasoning_tokens")  or 0

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


# config.yaml refers to this instance by name
proxy_handler_instance = TokenUsageLogger()
```

> **On the run label:** The `x-run-label` header is the nicer path if your agent can send custom headers; the `RUN_LABEL` environment variable is the reliable fallback. Step 08 covers both.

---

## 04 · Write the proxy config

Two things here are worth understanding rather than copying blindly: how the Azure deployment is addressed, and why `base_model` is present.

**`config.yaml`**

```yaml
model_list:
  - model_name: gpt-5.4                          # what the agent asks for
    litellm_params:
      model: azure/<AZURE_DEPLOYMENT_NAME>       # your deployment, not the model name
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION
    model_info:
      base_model: azure/gpt-5.4                  # tells LiteLLM what it really is

litellm_settings:
  callbacks: usage_logger.proxy_handler_instance
  drop_params: true
```

### The deployment name is not the model name

In Azure, `litellm_params.model` must be `azure/` followed by *the deployment name you created in the portal*. If the deployment is called `coding-agent-gpt54-prod`, that line reads `azure/coding-agent-gpt54-prod`. The friendly `model_name: gpt-5.4` above it is purely what the agent sees.

> **Known sharp edge:** LiteLLM decides whether to apply GPT-5.4 behaviour — the Responses API bridge, `reasoning_effort`, tool-call handling — by pattern-matching the model string. A deployment name that doesn't plainly contain `gpt-5.4` has been reported to fall through that check and produce validation errors on tool calls. `model_info.base_model` is the supported way to declare the real identity, and it's also what makes cost attribution correct. If you still hit parameter-rejection errors, the cheapest fix is to create a second Azure deployment whose name contains `gpt-5.4`.

`drop_params: true` tells LiteLLM to strip parameters the target model doesn't accept instead of erroring. The GPT-5 series rejects `max_tokens` in favour of `max_completion_tokens`, and agents send the old one constantly.

---

## 05 · Start the proxy

```powershell
# from $HOME\token-metering, with the venv active
litellm --config .\config.yaml --port 4000
```

Leave this window open — it's the running proxy. Start the agent in a second terminal.

> **Confirm before moving on:** Startup output includes a line about loading the custom callback. If you don't see the logger mentioned, the import failed — almost always because you started `litellm` from a different folder than the one holding `usage_logger.py`.

It will print that it's listening on `0.0.0.0:4000`. That's the bind address, meaning "all interfaces". The address to give applications is `http://localhost:4000`.

> **Don't expose this:** Binding to `0.0.0.0` means anyone who can reach your machine on port 4000 can spend our Azure quota, with no authentication in this configuration. Keep it on the loopback interface: decline any Windows Firewall prompt asking to allow `python.exe` on private or public networks, or start it with `--host 127.0.0.1`.

---

## 06 · Smoke-test before touching the agent

Prove the proxy reaches Azure and that a row lands in the log. Do this in the *second* terminal.

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

Codex talks the Responses API, so test that route too — it exercises different code and different usage field names:

```powershell
$body = @{
    model = "gpt-5.4"
    input = "Say hello in one sentence."
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/responses" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 10
```

> **Confirm before moving on:** `Get-Content .\token_usage.jsonl -Tail 2` should show two rows with non-zero `input_tokens` and `output_tokens`. If the file doesn't exist, the callback never fired — go back to step 05.

---

## 07 · Point Codex CLI at the proxy

Codex reads `%USERPROFILE%\.codex\config.toml`. Add a custom provider and select it:

**`%USERPROFILE%\.codex\config.toml`**

```toml
model = "gpt-5.4"
model_provider = "litellm"

[model_providers.litellm]
name     = "LiteLLM (local)"
base_url = "http://localhost:4000/v1"
env_key  = "LITELLM_API_KEY"
wire_api = "responses"
```

Then, in the terminal you run Codex from:

```powershell
$env:LITELLM_API_KEY = "sk-local"
codex
```

> **About that key:** The proxy has no master key configured, so it accepts anything — but Codex refuses to start if the variable named by `env_key` is empty. Any non-empty string works.

> **If Codex errors on the wire protocol:** Recent Codex versions expect `wire_api = "responses"` for third-party providers. Older builds may only speak `"chat"`. If you see protocol or 404 errors on `/v1/responses`, flip it to `wire_api = "chat"` — the logger reads either shape, so your measurements stay valid. Check with `codex --version` and note which mode you ended up in, since it changes what the agent sends.

### If you also want to try Cursor

Cursor accepts a custom OpenAI base URL under Settings → Models — use `http://localhost:4000/v1` and any API key. Be aware it's a weaker measurement: not all of Cursor's traffic honours the override, so the log will undercount. Treat Codex CLI as the reference and Cursor as directional.

> **Confirm before moving on:** Ask the agent something trivial, then check the proxy window shows the request and the JSONL file grew. Once you see agent traffic in the log, the plumbing is done.

---

## 08 · Label runs so the totals mean something

Every row needs to say which task it belongs to, or the log is just an undifferentiated pile. Two ways, in order of preference:

### Environment variable — always works

Set a label, restart the proxy, run one task, stop. It's crude but it never fails:

```powershell
$env:RUN_LABEL = "codex--refactor-auth--run1"
litellm --config .\config.yaml --port 4000
```

Use a consistent naming scheme — `<agent>--<task>--<run>` makes the rollup readable and sortable.

### Request header — if your agent supports it

If your Codex version supports extra headers on a provider, add them and you can label without restarting:

```toml
[model_providers.litellm.http_headers]
"x-run-label" = "codex--refactor-auth--run1"
```

> **If the label comes through as "unlabeled":** LiteLLM's metadata shape shifts between versions. Add `print(json.dumps(meta, default=str)[:2000])` at the top of `_write`, send one request, and read where the headers actually landed — then fix the key. Remove the print afterwards.

---

## 09 · Roll the log up into a report

No extra dependencies — PowerShell parses the JSONL directly:

**`rollup.ps1`**

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

Which gives you the thing worth putting in front of people:

| Run | Calls | Input | Cached | Uncached | Output | Reasoning | Total |
|---|---|---|---|---|---|---|---|
| codex--refactor-auth--run1 | 18 | 1,284,392 | 943,104 | 341,288 | 74,821 | 51,440 | 1,359,213 |
| codex--refactor-auth--run2 | 16 | 1,141,006 | 988,220 | 152,786 | 68,004 | 46,110 | 1,209,010 |

*Illustrative shape, not real measurements. Note how much the second run benefits from a warm cache — which is exactly the trap in the next step.*

Add `| Export-Csv .\rollup.csv -NoTypeInformation` to the end of the pipeline when you want it in a spreadsheet.

---

## 10 · Run a comparison that's actually fair

The instrumentation is the easy half. Most agent comparisons go wrong in the experiment design, and the numbers look authoritative either way. Hold these constant:

- **Repository state.** Same commit for every run, and reset it between runs — `git stash` or a fresh clone. An agent that runs second against a half-fixed repo has an easier job.
- **Task text.** Byte-identical prompt for each agent. Paste from a file rather than retyping.
- **Reasoning effort.** If agents default to different `reasoning_effort` levels, you're measuring the setting, not the agent. Pin it — either in each agent's config, or centrally in `config.yaml` under `litellm_params`.
- **Cache state.** The big one. Azure's prompt cache means a repeat run of the same task can post dramatically lower uncached input. Either run each agent cold-first in alternating order, or run everything twice and report cold and warm separately. Never compare one agent's cold run to another's warm run.

And when reporting: lead with **uncached input**, **reasoning tokens**, and **request count**. Those three explain almost all of the variance between agents. `total_tokens` alone hides which agent is expensive and why.

> **Sanity check:** Spot-check one task against the Azure portal's own metrics for the deployment. They won't match to the token, but they should be within a few percent. A large gap means traffic is bypassing the proxy — usually a second agent config still pointed at Azure directly.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Rows land in the log but all token counts are `0` | Streaming response with no usage attached. On Chat Completions the client must send `stream_options: {"include_usage": true}`; you can force it centrally with `stream_options: {"include_usage": true}` under `litellm_params`. On the Responses API, usage rides on the final event — if it's missing, LiteLLM isn't aggregating the stream. |
| `reasoning_tokens` always 0, everything else populated | Either the API version predates reasoning-usage reporting, or the deployment isn't a reasoning model. Check `AZURE_API_VERSION` first. |
| `DeploymentNotFound` / 404 from Azure | `litellm_params.model` is set to the model name instead of the deployment name. It must be `azure/<deployment>`. |
| Unsupported parameter: `max_tokens` | GPT-5 series wants `max_completion_tokens`. Set `drop_params: true`. |
| `tool_choice` or `reasoning_effort` rejected | LiteLLM didn't recognise the deployment as GPT-5.4. Confirm `model_info.base_model`, upgrade LiteLLM, or rename the deployment so it contains `gpt-5.4`. |
| Codex exits immediately with a 401 | `$env:LITELLM_API_KEY` is unset in that terminal. Codex requires the variable named by `env_key` to be non-empty. |
| No `token_usage.jsonl` at all | The callback didn't import. Start `litellm` from the folder containing `usage_logger.py`, and check the `callbacks:` path spells the module and instance exactly. |
| `litellm`: The term `...` is not recognized | Virtual environment not activated in this terminal. |

---

## If we outgrow the JSONL file

LiteLLM ships an admin UI at `http://localhost:4000/ui` with spend tracking, virtual keys, and per-key reporting — but it's backed by a database. Without a Postgres connection configured, there's no persistent spend history to show, which is why this runbook doesn't rely on it.

For a single-machine comparison the flat file is genuinely better: it's greppable, diffable, and trivially shared. Move to the database setup when we want multiple people's usage in one place, per-developer keys, or cost figures rather than raw token counts.

---

*Questions or a step that didn't work as written — send the proxy window's output and the last few lines of `token_usage.jsonl`, that's usually enough to spot it.*
