# Test 015 — Cursor → LiteLLM → Azure GPT-5.4

## Purpose

Tests 012–014 established several important facts:

```text
Azure GPT-5.4 Responses API                 WORKING
LiteLLM → Azure GPT-5.4                     WORKING
LiteLLM token logger                        WORKING
Codex → LiteLLM → Azure                     WORKING
Codex local repository inspection on VDI    BLOCKED BY CLIENT POLICY
```

Test 015 moves to Cursor, which is the more relevant client for the customer workflow.

This test answers two separate questions:

1. Can Cursor route its GPT-5.4 model traffic through the validated LiteLLM proxy?
2. If model routing works, can Cursor inspect local repository files despite the endpoint policy that blocked Codex child-process execution?

Do **not** introduce CoreStory MCP yet. The goal is to isolate Cursor first.

---

## Phase A — Cursor model routing

### Starting Cursor configuration

The pre-test configuration was recorded as:

```text
Model Name = corestory-genai-gtp-5.4 (custom model)
Current OpenAI Base URL = https://corestory-genai-sa.openai.azure.com/openai/v1
Override OpenAI Base URL = enabled
```

No API keys or customer credentials are recorded in this document.

### LiteLLM startup

LiteLLM was started with:

```powershell
Set-Location $env:USERPROFILE\token-metering
$env:RUN_LABEL="test-015-cursor-litellm"
litellm --config .\config.yaml --port 4000
```

Observed startup:

```text
LiteLLM: Proxy initialized with Config, Set models:
    gpt-5.4
Application startup complete.
```

The existing LiteLLM cache-cost-map warning was also present. This warning was already shown not to block request routing or token measurement in earlier tests.

### Cursor test configuration

Cursor was changed to the following intended test state:

```text
Model selected/enabled: GPT-5.4
OpenAI API key: sk-local
Use OpenAI API key: enabled
Override OpenAI Base URL: enabled
OpenAI Base URL: http://localhost:4000/v1
```

The settings were closed and reopened to confirm persistence. Cursor was also restarted and the test repeated without changing the configuration.

When `Use OpenAI API key` was enabled, Cursor displayed an orange `1` indicator next to Models. This is recorded only as an observed UI state; no interpretation is assigned to it.

### Control prompt

A new Cursor chat was started and the following prompt was sent:

```text
Reply with exactly: CURSOR_LITELLM_OK
```

### Cursor result

```text
CURSOR_LITELLM_OK
```

Cursor returned the requested response successfully. There were no visible model/provider errors or other notable errors.

### LiteLLM result

```text
No request observed in the LiteLLM console.
No Test 015 row written to token_usage.jsonl.
```

The test was repeated after restarting Cursor, with the same result.

### Negative control

To determine whether Cursor was honoring the configured OpenAI Base URL at all, the Base URL was temporarily changed to a deliberately unused local endpoint:

```text
http://127.0.0.1:65534/v1
```

A new Cursor chat was started and the following prompt was sent:

```text
Reply with exactly: CURSOR_NEGATIVE_CONTROL_OK
```

Cursor successfully returned:

```text
CURSOR_NEGATIVE_CONTROL_OK
```

Because the configured endpoint was deliberately unreachable, a successful response demonstrates that this tested Cursor model path did not depend on the configured OpenAI Base URL.

### Phase A evidence summary

```text
Configured LiteLLM Base URL:      http://localhost:4000/v1
Use OpenAI API key:               enabled
Override OpenAI Base URL:         enabled
Cursor response:                  CURSOR_LITELLM_OK
LiteLLM request observed:         NO
Test 015 JSONL row observed:      NO

Negative-control Base URL:        http://127.0.0.1:65534/v1
Negative-control Cursor response: CURSOR_NEGATIVE_CONTROL_OK
```

### Phase A conclusion

**PHASE A: FAIL — selected Cursor model path did not honor the configured OpenAI Base URL.**

This failure occurs before the validated LiteLLM boundary. It does **not** indicate a failure in Azure GPT-5.4, LiteLLM routing, the Responses API path, or the token logger; those components were independently proven in Tests 009–013.

The negative control materially strengthens the conclusion: Cursor continued to answer successfully when configured with an unreachable local Base URL.

A plausible remaining distinction is whether the selected `GPT-5.4` entry is a Cursor-managed model path while the previously configured `corestory-genai-gtp-5.4` entry represents a distinct custom/BYOK path. This is a hypothesis to test, not a conclusion.

---

## Phase A follow-up — custom model routing check

Before moving to repository inspection, restore:

```text
OpenAI Base URL: http://localhost:4000/v1
```

Then inspect the model selector in the actual Cursor chat.

If both the built-in/managed GPT-5.4 entry and the previously configured custom model are available, explicitly select the custom model:

```text
corestory-genai-gtp-5.4
```

With LiteLLM still running, start a new chat and send:

```text
Reply with exactly: CURSOR_CUSTOM_MODEL_OK
```

Record:

```text
Exact model name shown in chat:
Cursor response/error:
LiteLLM request path/status:
Test 015 JSONL row, if any:
```

### Custom model routing result

```text
PENDING
```

Do not proceed to Phase B until a Cursor interaction is actually observed by LiteLLM.

---

## Phase B — Cursor local repository inspection

**NOT RUN.**

Phase B remains blocked on proving Cursor → LiteLLM routing.

Once routing is proven, open:

```text
C:\Users\carys\codex-metering-test
```

and ask:

```text
Read calculator.py in the currently open repository. What concrete behavioral limitation exists in the multiply function? Do not modify any files. Answer in two sentences or fewer.
```

Expected substance:

```text
The implementation uses range(b) and repeated addition. A negative value for b produces an empty range, so negative multipliers are not handled correctly.
```

---

## Important methodology note

A successful future Cursor test will prove only that the tested Cursor interaction traversed LiteLLM. It should not automatically be interpreted as proof that every internal Cursor model call uses the custom endpoint. During later benchmark runs, LiteLLM request logs and JSONL token rows remain the evidence for which calls were actually observed.

Likewise, Codex token totals should not be used as a direct Cursor baseline. Codex and Cursor are different agents with different context construction and tool behavior.

## Result summary

```text
PHASE A: FAIL — Cursor answered normally but no traffic reached LiteLLM.
NEGATIVE CONTROL: CONFIRMED — Cursor answered normally with an unreachable Base URL.
CUSTOM MODEL FOLLOW-UP: PENDING
PHASE B: NOT RUN
OVERALL: BLOCKED ON CURSOR ROUTING
```
