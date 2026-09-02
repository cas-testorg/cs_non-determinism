# Test 012 — Fix and Validate the Production Usage Logger

## Purpose

Tests 009–011 established the following:

- LiteLLM `/v1/responses` successfully routes to Azure GPT-5.4.
- The HTTP response contains the correct token usage.
- LiteLLM's success callback exposes normalized usage fields as `prompt_tokens` and `completion_tokens`.
- Cached-input and reasoning-token details are available under the normalized token-detail objects.

This test updates the production `usage_logger.py` to use those normalized fields while retaining Responses-style fallbacks, then validates the complete token record with one known request.

Do not commit credentials, prompts from customer workloads, generated customer content, or request headers.

## Expected validation result

For the existing one-sentence smoke test, the previous successful requests returned:

```text
input_tokens           = 12
cached_input_tokens    = 0
uncached_input_tokens  = 12
output_tokens          = 6
reasoning_tokens       = 0
visible_output_tokens  = 6
total_tokens           = 18
```

Exact output-token counts can vary if Azure generates different text. The important validation is that the logger's input/output/total values match the `usage` object returned by the proxy and that the derived cached/uncached/reasoning/visible fields are internally consistent.

## 1. Stop LiteLLM

If the proxy is running:

```text
Ctrl+C
```

Test 011 should already have restored the production logger.

## 2. Back up the production logger

From the token-metering directory:

```powershell
Copy-Item .\usage_logger.py .\usage_logger.py.pre-test012.bak -Force
```

## 3. Replace `usage_logger.py`

Replace the production logger with the following implementation:

```python
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from litellm.integrations.custom_logger import CustomLogger

LOG_PATH = Path("token_usage.jsonl")


def _safe_dict(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj

    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                value = fn()
                if isinstance(value, dict):
                    return value
            except Exception:
                pass

    raw = getattr(obj, "__dict__", None)
    return raw if isinstance(raw, dict) else {}


def _first_int(*values):
    for value in values:
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return 0


def _usage_dict(response_obj, kwargs):
    # LiteLLM normalizes Responses API usage to prompt/completion token names
    # in the callback response object. Prefer that authoritative object.
    usage = _safe_dict(getattr(response_obj, "usage", None))

    if not usage:
        response_dict = _safe_dict(response_obj)
        usage = _safe_dict(response_dict.get("usage"))

    # Fallback to LiteLLM's standard logging object if required.
    if not usage or not any(
        key in usage
        for key in (
            "prompt_tokens",
            "completion_tokens",
            "input_tokens",
            "output_tokens",
        )
    ):
        standard = _safe_dict(kwargs.get("standard_logging_object"))
        metadata = _safe_dict(standard.get("metadata"))
        metadata_usage = _safe_dict(metadata.get("usage_object"))

        if metadata_usage:
            usage = metadata_usage
        elif standard:
            usage = standard

    return usage


def _run_label(kwargs):
    # Preserve the existing environment-based run labeling mechanism.
    # A request-specific label can be added later if the agent path proves
    # that the desired header is available safely in callback metadata.
    return os.environ.get("RUN_LABEL", "unlabeled")


class UsageLogger(CustomLogger):
    def _write(self, kwargs, response_obj, start_time, end_time):
        usage = _usage_dict(response_obj, kwargs)

        prompt_details = _safe_dict(
            usage.get("prompt_tokens_details")
            or usage.get("input_tokens_details")
        )
        completion_details = _safe_dict(
            usage.get("completion_tokens_details")
            or usage.get("output_tokens_details")
        )

        input_tokens = _first_int(
            usage.get("prompt_tokens"),
            usage.get("input_tokens"),
        )
        output_tokens = _first_int(
            usage.get("completion_tokens"),
            usage.get("output_tokens"),
        )
        total_tokens = _first_int(
            usage.get("total_tokens"),
            input_tokens + output_tokens,
        )

        cached_input_tokens = _first_int(
            prompt_details.get("cached_tokens"),
            usage.get("cached_input_tokens"),
        )
        reasoning_tokens = _first_int(
            completion_details.get("reasoning_tokens"),
            usage.get("reasoning_tokens"),
        )

        uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)
        visible_output_tokens = max(output_tokens - reasoning_tokens, 0)

        latency_s = None
        try:
            latency_s = round((end_time - start_time).total_seconds(), 3)
        except Exception:
            pass

        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run": _run_label(kwargs),
            "model": kwargs.get("model"),
            "call_type": kwargs.get("call_type"),
            "latency_s": latency_s,
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
            "visible_output_tokens": visible_output_tokens,
            "total_tokens": total_tokens,
        }

        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj, start_time, end_time)
        except Exception as e:
            print(f"[usage_logger] skipped usage row: {e}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj, start_time, end_time)
        except Exception as e:
            print(f"[usage_logger] skipped usage row: {e}")


proxy_handler_instance = UsageLogger()
```

Keep `config.yaml` unchanged from the successful Test 009 configuration.

## 4. Start with a clean validation log

Preserve any existing token log before testing:

```powershell
if (Test-Path .\token_usage.jsonl) {
    Copy-Item .\token_usage.jsonl .\token_usage.pre-test012.jsonl -Force
}

Remove-Item .\token_usage.jsonl -ErrorAction SilentlyContinue
```

## 5. Set a validation run label

```powershell
$env:RUN_LABEL="test-012-proxy-validation"
```

## 6. Start LiteLLM

```powershell
litellm --config .\config.yaml --port 4000
```

Leave this PowerShell window running.

### Proxy startup result

```text
PASTE RELEVANT STARTUP OUTPUT HERE
```

## 7. Send exactly one Responses API request

In a second PowerShell window:

```powershell
$body = @{
    model = "gpt-5.4"
    input = "Say hello in one sentence."
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/responses" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body

$response | Select-Object model,status,usage | ConvertTo-Json -Depth 10
```

Paste the output below.

### Proxy response usage

```text
PASTE RESULT HERE
```

## 8. Capture the production token log

```powershell
Get-Content .\token_usage.jsonl -Tail 2
```

Paste the output below.

### Production token log result

```text
PASTE RESULT HERE
```

## 9. Validate the numbers

Compare the proxy response `usage` with the JSONL row.

The following must hold:

```text
JSONL input_tokens  == proxy usage input_tokens
JSONL output_tokens == proxy usage output_tokens
JSONL total_tokens  == proxy usage total_tokens

uncached_input_tokens == input_tokens - cached_input_tokens
visible_output_tokens == output_tokens - reasoning_tokens
```

For the known smoke test, a likely successful row is:

```json
{"run":"test-012-proxy-validation","model":"gpt-5.4","call_type":"aresponses","input_tokens":12,"cached_input_tokens":0,"uncached_input_tokens":12,"output_tokens":6,"reasoning_tokens":0,"visible_output_tokens":6,"total_tokens":18}
```

Timestamp and latency fields are omitted from this example only for readability.

## Interpretation

- **All values match:** production metering for LiteLLM Responses calls is validated. Proceed to Codex → LiteLLM → Azure.
- **Input/output/total match but cached or reasoning does not:** inspect only the corresponding detail object before changing the logger.
- **Only total is populated again:** preserve the result; the fallback selection in `_usage_dict` needs adjustment based on Test 011's `standard_logging_object.metadata.usage_object`.
- **Request itself fails:** do not modify the logger. Return to the last known-good Test 009 proxy configuration first.

## Result summary

```text
RESULT: PENDING
```

After the test, commit this file with the proxy usage and JSONL row. Do not begin the Codex benchmark until the metering result has been reviewed.
