# Test 011 — Inspect LiteLLM Callback kwargs for Usage Metadata

## Purpose

Test 010 proved that the successful Responses API HTTP response contains the full token breakdown, but the `ResponsesAPIResponse.usage` object delivered to `async_log_success_event` contains only `total_tokens`.

This test checks whether LiteLLM preserves the authoritative token breakdown elsewhere in the callback `kwargs`.

The diagnostic is deliberately restricted to token/usage-related fields and structural metadata. It must not write prompts, generated output, request headers, API keys, authorization values, or request bodies.

## 1. Confirm the Test 010 logger was restored

Test 010 instructed us to restore the original logger. From the token-metering directory, confirm the files exist:

```powershell
Get-Item .\usage_logger.py
Get-Item .\usage_logger.py.test009.bak
```

Do not print the file contents if they contain anything you do not want committed.

## 2. Stop LiteLLM

If the proxy is running, stop it with:

```text
Ctrl+C
```

## 3. Back up the current logger

```powershell
Copy-Item .\usage_logger.py .\usage_logger.py.test011.bak -Force
```

## 4. Temporarily replace `usage_logger.py`

Replace its contents with:

```python
import json
from datetime import datetime, timezone
from pathlib import Path
from litellm.integrations.custom_logger import CustomLogger

LOG_PATH = Path("usage_kwargs_diagnostic.jsonl")

TOKEN_TERMS = (
    "usage",
    "token",
    "cache",
    "cost",
)


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
                return value if isinstance(value, dict) else {}
            except Exception:
                pass
    raw = getattr(obj, "__dict__", None)
    return raw if isinstance(raw, dict) else {}


def _token_fields(value, depth=0):
    """Keep only token/usage/cache/cost-related fields and safe structural metadata."""
    if depth > 5:
        return "<max-depth>"

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    data = _safe_dict(value)
    if not data:
        if isinstance(value, (list, tuple)):
            return [_token_fields(v, depth + 1) for v in value[:20]]
        return {"type": type(value).__name__}

    result = {}
    for key, item in data.items():
        key_text = str(key)
        key_lower = key_text.lower()

        # Explicitly exclude fields that could contain user/customer content or secrets.
        if any(term in key_lower for term in (
            "prompt", "message", "input", "output", "content",
            "header", "authorization", "api_key", "apikey",
            "request", "response", "body"
        )):
            # Token counters such as input_tokens/output_tokens are safe and required.
            if "token" not in key_lower:
                continue

        if any(term in key_lower for term in TOKEN_TERMS):
            result[key_text] = _token_fields(item, depth + 1)
        elif isinstance(item, dict):
            nested = _token_fields(item, depth + 1)
            if isinstance(nested, dict) and nested:
                result[key_text] = nested

    return result


class UsageKwargsLogger(CustomLogger):
    def _write(self, kwargs, response_obj):
        response_usage = _safe_dict(getattr(response_obj, "usage", None))

        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "call_type": kwargs.get("call_type"),
            "response_type": type(response_obj).__name__,
            "response_usage": _token_fields(response_usage),
            "kwargs_top_level_keys": sorted(str(k) for k in kwargs.keys()),
            "kwargs_token_fields": _token_fields(kwargs),
        }

        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj)
        except Exception as e:
            print(f"[usage_kwargs_logger] skipped diagnostic row: {e}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj)
        except Exception as e:
            print(f"[usage_kwargs_logger] skipped diagnostic row: {e}")


proxy_handler_instance = UsageKwargsLogger()
```

Keep `config.yaml` unchanged from the successful Test 009 configuration.

## 5. Remove any old diagnostic file

```powershell
Remove-Item .\usage_kwargs_diagnostic.jsonl -ErrorAction SilentlyContinue
```

## 6. Start LiteLLM

```powershell
litellm --config .\config.yaml --port 4000
```

Leave this window running.

## 7. Send exactly one Responses API request

In a second PowerShell window:

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
    -Body $body | Select-Object model,status,usage | ConvertTo-Json -Depth 10
```

### Proxy response summary

```text
PASTE RESULT HERE
```

## 8. Capture the callback kwargs diagnostic

```powershell
Get-Content .\usage_kwargs_diagnostic.jsonl -Tail 2
```

Paste the output below.

### Callback kwargs diagnostic

```text
PASTE RESULT HERE
```

Before committing, quickly inspect the diagnostic line. It should contain structural keys and token/usage/cache/cost values only. If you see prompt text, generated response text, credentials, authorization values, or headers, do not commit the file/output.

## 9. Restore the logger

Stop LiteLLM, then restore the logger that existed before this test:

```powershell
Copy-Item .\usage_logger.py.test011.bak .\usage_logger.py -Force
```

Do not begin a Codex benchmark yet.

## Interpretation

- **Full input/output/total usage appears somewhere in `kwargs_token_fields`:** update the production logger to read that authoritative location, then validate it with one final proxy smoke test.
- **Only `total_tokens` appears everywhere:** `async_log_success_event` is not a sufficient measurement point for Responses API usage in this LiteLLM path. Move token capture to another supported hook or layer rather than inferring input/output counts.
- **Cached/reasoning token details appear:** preserve their exact location for the production logger because these fields matter to the benchmark economics.

## Result summary

```text
RESULT: PENDING
```
