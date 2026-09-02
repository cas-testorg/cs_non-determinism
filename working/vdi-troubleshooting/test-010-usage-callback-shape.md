# Test 010 — Inspect LiteLLM Responses Usage Callback Shape

## Purpose

Test 009 proved that LiteLLM can successfully forward `/v1/responses` to Azure GPT-5.4. The proxy response contains correct usage:

```text
input_tokens  = 12
output_tokens = 6
total_tokens  = 18
```

However, the custom logger wrote:

```text
input_tokens  = 0
output_tokens = 0
total_tokens  = 18
```

Before changing the logger logic, this test captures the token-related shape LiteLLM actually passes to `async_log_success_event` for a Responses API call.

This test must not log prompts, responses, credentials, or headers. It records only object type and usage fields.

## 1. Stop LiteLLM

In the PowerShell window running the proxy:

```text
Ctrl+C
```

## 2. Back up the current logger

From the token-metering directory:

```powershell
Copy-Item .\usage_logger.py .\usage_logger.py.test009.bak
```

## 3. Temporarily replace `usage_logger.py`

Replace the file contents with the following diagnostic logger:

```python
import json
from datetime import datetime, timezone
from pathlib import Path
from litellm.integrations.custom_logger import CustomLogger

LOG_PATH = Path("usage_callback_diagnostic.jsonl")


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


def _usage_only(response_obj):
    response_dict = _safe_dict(response_obj)
    usage_obj = response_dict.get("usage")
    if usage_obj is None:
        usage_obj = getattr(response_obj, "usage", None)

    usage_dict = _safe_dict(usage_obj)

    # Only retain token/count fields. Never write prompt/output content.
    allowed = {
        "prompt_tokens",
        "completion_tokens",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "prompt_tokens_details",
        "completion_tokens_details",
        "input_tokens_details",
        "output_tokens_details",
    }

    return {
        key: value
        for key, value in usage_dict.items()
        if key in allowed
    }


class UsageShapeLogger(CustomLogger):
    def _write(self, kwargs, response_obj):
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "call_type": kwargs.get("call_type"),
            "response_type": type(response_obj).__name__,
            "response_dict_keys": sorted(_safe_dict(response_obj).keys()),
            "usage": _usage_only(response_obj),
        }

        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj)
        except Exception as e:
            print(f"[usage_shape_logger] skipped diagnostic row: {e}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            self._write(kwargs, response_obj)
        except Exception as e:
            print(f"[usage_shape_logger] skipped diagnostic row: {e}")


proxy_handler_instance = UsageShapeLogger()
```

The existing `config.yaml` should remain unchanged from Test 009.

## 4. Remove any old diagnostic file

```powershell
Remove-Item .\usage_callback_diagnostic.jsonl -ErrorAction SilentlyContinue
```

## 5. Start LiteLLM

```powershell
litellm --config .\config.yaml --port 4000
```

Leave the proxy running.

## 6. Send one Responses API request

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
{
    "model":  "gpt-5.4",
    "status":  "completed",
    "usage":  {
                  "input_tokens":  12,
                  "input_tokens_details":  {
                                               "audio_tokens":  null,
                                               "cached_tokens":  0,
                                               "text_tokens":  null,
                                               "cache_write_tokens":  0
                                           },
                  "output_tokens":  6,
                  "output_tokens_details":  {
                                                "reasoning_tokens":  0,
                                                "text_tokens":  null
                                            },
                  "total_tokens":  18,
                  "cost":  null
              }
```

## 7. Capture the callback diagnostic

From the token-metering directory:

```powershell
Get-Content .\usage_callback_diagnostic.jsonl -Tail 2
```

Paste the output below.

### Callback diagnostic result

```text
{"ts": "2026-09-02T18:58:08.068238+00:00", "call_type": "aresponses", "response_type": "ResponsesAPIResponse", "response_dict_keys": ["background", "completed_at", "content_filters", "created_at", "error", "frequency_penalty", "id", "incomplete_details", "instructions", "max_output_tokens", "max_tool_calls", "metadata", "model", "moderation", "object", "output", "parallel_tool_calls", "presence_penalty", "previous_response_id", "prompt_cache_key", "prompt_cache_retention", "reasoning", "safety_identifier", "service_tier", "status", "store", "temperature", "text", "tool_choice", "tool_usage", "tools", "top_logprobs", "top_p", "truncation", "usage", "user"], "usage": {"total_tokens": 18}}
```

## 8. Restore the original logger after capturing the result

Stop LiteLLM, then:

```powershell
Copy-Item .\usage_logger.py.test009.bak .\usage_logger.py -Force
```

Do not start the next benchmark run yet. Commit this test result first so we can update the logger based on the actual callback shape.

## Interpretation

The key question is whether the callback receives:

- Responses-style fields: `input_tokens` / `output_tokens`
- Chat-style normalized fields: `prompt_tokens` / `completion_tokens`
- a partially normalized object where only `total_tokens` survives
- a wrapper/object shape that requires reading usage from somewhere other than `response_obj.usage`

The diagnostic result determines the smallest safe fix to `usage_logger.py`.

## Result summary

```text
RESULT: PENDING
```
