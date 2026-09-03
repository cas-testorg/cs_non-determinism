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

1. Can Cursor route its custom GPT-5.4 model traffic through the validated LiteLLM proxy?
2. If model routing works, can Cursor inspect local repository files despite the endpoint policy that blocked Codex child-process execution?

Do **not** introduce CoreStory MCP yet. The goal is to isolate Cursor first.

Do not change multiple variables at once. If a step fails, preserve the exact evidence and stop before changing unrelated settings.

---

## Phase A — Cursor model routing only

### 1. Record the existing Cursor custom-model configuration

Before changing Cursor, record the current non-secret configuration below.

Do **not** paste API keys, bearer tokens, customer credentials, or other secrets.

Record only values such as:

```text
Cursor version:
Current custom model name:
Current OpenAI-compatible base URL:
Any visible custom-model/provider options:
```

### Existing Cursor configuration

```text
Model Name = corestory-genai-gtp-5.4.  This is a custom model.
Current OpenAI Base URL = https://corestory-genai-sa.openai.azure.com/openai/v1
Override is Enabled.
```

If possible, take a screenshot for your own records, but do not commit a screenshot if it contains credentials or customer-sensitive information.

### 2. Stop the previous LiteLLM process

If LiteLLM is still running from Test 014, stop it:

```text
Ctrl+C
```

Do not change `config.yaml` or `usage_logger.py`.

### 3. Start LiteLLM for Cursor

From the token-metering PowerShell window:

```powershell
Set-Location $env:USERPROFILE\token-metering
$env:RUN_LABEL="test-015-cursor-litellm"
litellm --config .\config.yaml --port 4000
```

Leave this window visible so the request path can be observed.

### LiteLLM startup result

```text
←[32mINFO←[0m:     Started server process [←[36m%d←[0m]
←[32mINFO←[0m:     Waiting for application startup.

   ██╗     ██╗████████╗███████╗██╗     ██╗     ███╗   ███╗
   ██║     ██║╚══██╔══╝██╔════╝██║     ██║     ████╗ ████║
   ██║     ██║   ██║   █████╗  ██║     ██║     ██╔████╔██║
   ██║     ██║   ██║   ██╔══╝  ██║     ██║     ██║╚██╔╝██║
   ███████╗██║   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║
   ╚══════╝╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝


←[1;37m#------------------------------------------------------------#←[0m
←[1;37m#                                                            #←[0m
←[1;37m#            'The thing I wish you improved is...'            #←[0m
←[1;37m#        https://github.com/BerriAI/litellm/issues/new        #←[0m
←[1;37m#                                                            #←[0m
←[1;37m#------------------------------------------------------------#←[0m

 Thank you for using LiteLLM! - Krrish & Ishaan



←[1;31mGive Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new←[0m


←[32mLiteLLM: Proxy initialized with Config, Set models:←[0m
←[32m    gpt-5.4←[0m
←[92m13:39:12 - LiteLLM:WARNING←[0m: utils.py:2898 - register_model: model=8b0a4659cf250fb2135b7940dee052bf2fc834d62511964ba0574efcad031c37 not in built-in cost map and no prefix/region variant matched; cache cost fields will default to 0. To track cache cost, add cache_creation_input_token_cost and cache_read_input_token_cost to model_info
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
```

### 4. Configure the Cursor custom model to use LiteLLM

Use Cursor's existing custom OpenAI/OpenAI-compatible model configuration and change only what is necessary to point it at the local proxy.

Target values:

```text
Model:    gpt-5.4
Base URL: http://localhost:4000/v1
API key:  sk-local
```

`sk-local` is only the throwaway client value used for this local LiteLLM test. Do not commit the actual contents of any customer API-key field.

Important:

- Keep the model name `gpt-5.4`.
- Do not change the Azure configuration behind LiteLLM.
- Do not enable CoreStory MCP for this test if it can be disabled without disturbing the customer's normal setup.
- Do not change Cursor rules, skills, or other agent configuration merely to make the test pass.

### Cursor LiteLLM configuration result

```text
PASTE NON-SECRET RESULT OR NOTES HERE
```

### 5. Record the token-log boundary

Before sending anything from Cursor:

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl -Tail 3 -ErrorAction SilentlyContinue
```

### Token log before Cursor

```text
{"ts": "2026-09-02T21:39:43.024979+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 4.81, "input_tokens": 14625, "cached_input_tokens": 14080, "uncached_input_tokens": 545, "output_tokens": 310, "reasoning_tokens": 235, "visible_output_tokens": 75, "total_tokens": 14935}
{"ts": "2026-09-02T21:39:52.095795+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 9.047, "input_tokens": 19230, "cached_input_tokens": 14464, "uncached_input_tokens": 4766, "output_tokens": 592, "reasoning_tokens": 541, "visible_output_tokens": 51, "total_tokens": 19822}
{"ts": "2026-09-02T21:39:57.695767+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 5.42, "input_tokens": 15276, "cached_input_tokens": 14976, "uncached_input_tokens": 300, "output_tokens": 435, "reasoning_tokens": 335, "visible_output_tokens": 100, "total_tokens": 15711}
```

### 6. Send a trivial Cursor prompt

Start a **new Cursor chat/session** to minimize contamination from prior context.

Select the custom `gpt-5.4` model that was pointed at LiteLLM.

Send exactly:

```text
Reply with exactly: CURSOR_LITELLM_OK
```

Do not ask Cursor to inspect files yet.

### Cursor routing result

```text
PASTE CURSOR RESPONSE/ERROR HERE
```

### 7. Immediately inspect the LiteLLM console

This is the most important diagnostic boundary in Phase A.

Record the request path and HTTP status generated by Cursor.

Examples:

```text
POST /v1/responses HTTP/1.1        200 OK
```

or:

```text
POST /v1/chat/completions HTTP/1.1 ...
```

### LiteLLM request path result

```text
PASTE RELEVANT REQUEST/STATUS LINES HERE
```

Do not change LiteLLM if Cursor uses a different endpoint. Preserve the result first.

### 8. Capture Cursor token rows

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl |
    Select-String '"run": "test-015-cursor-litellm"'
```

### Phase A token rows

```text
PASTE RESULT HERE
```

### Phase A decision

Continue to Phase B only if Cursor successfully reaches LiteLLM and receives a valid GPT-5.4 response.

If Cursor does **not** reach LiteLLM, stop. The next investigation is Cursor custom-provider routing, not Azure or the logger.

If Cursor reaches LiteLLM but receives an error, preserve the exact LiteLLM request path and error before changing anything.

---

## Phase B — Cursor local repository inspection

Run this phase only after Phase A succeeds.

### 9. Open the existing neutral repository in Cursor

Open:

```text
C:\Users\carys\codex-metering-test
```

This is the tiny repository created for Test 014. It contains:

```text
README.md
app.py
calculator.py
```

Do not use customer source yet.

### 10. Start a fresh Cursor chat/session

Use the same custom `gpt-5.4` model routed through LiteLLM.

Do not change the LiteLLM process or run label.

Before sending the prompt, note the current number of Test 015 token rows if useful.

### 11. Ask Cursor to inspect one known file

Send:

```text
Read calculator.py in the currently open repository. What concrete behavioral limitation exists in the multiply function? Do not modify any files. Answer in two sentences or fewer.
```

Expected substance:

```text
The implementation uses range(b) and repeated addition. A negative value for b produces an empty range, so negative multipliers are not handled correctly.
```

Exact wording is not important.

### Cursor repository-inspection result

```text
PASTE CURSOR RESPONSE/ERROR HERE
```

If Cursor reports a policy/tool-execution error, preserve it exactly. Do not broaden permissions or bypass endpoint controls.

### 12. Capture the LiteLLM request lines from Phase B

### Phase B LiteLLM request result

```text
PASTE RELEVANT REQUEST/STATUS LINES HERE
```

### 13. Capture all Test 015 token rows

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl |
    Select-String '"run": "test-015-cursor-litellm"'
```

### All Test 015 token rows

```text
PASTE RESULT HERE
```

Preserve every row. Cursor may make multiple model requests for one user interaction.

### 14. Calculate aggregate Test 015 usage

```powershell
$rows = Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl |
    ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object { $_.run -eq "test-015-cursor-litellm" }

[pscustomobject]@{
    Requests            = @($rows).Count
    InputTokens         = ($rows | Measure-Object input_tokens -Sum).Sum
    CachedInputTokens   = ($rows | Measure-Object cached_input_tokens -Sum).Sum
    UncachedInputTokens = ($rows | Measure-Object uncached_input_tokens -Sum).Sum
    OutputTokens        = ($rows | Measure-Object output_tokens -Sum).Sum
    ReasoningTokens     = ($rows | Measure-Object reasoning_tokens -Sum).Sum
    VisibleOutputTokens = ($rows | Measure-Object visible_output_tokens -Sum).Sum
    TotalTokens         = ($rows | Measure-Object total_tokens -Sum).Sum
} | Format-List
```

### Aggregate Test 015 usage

```text
PASTE RESULT HERE
```

---

## Validation criteria

### Phase A passes when

```text
Cursor custom model is gpt-5.4
Cursor is configured to use http://localhost:4000/v1
Cursor returns CURSOR_LITELLM_OK
LiteLLM records the Cursor request
Azure GPT-5.4 returns successfully
The token logger records non-zero usage
```

### Phase B passes when

```text
Cursor can inspect calculator.py
Cursor correctly identifies the multiply limitation
No repository files are modified
LiteLLM records the model traffic generated by the interaction
Token usage is captured for the interaction
```

## Interpretation matrix

| Phase A | Phase B | Interpretation |
|---|---|---|
| Pass | Pass | Cursor is viable for the measured customer workflow. Next step can introduce CoreStory MCP. |
| Pass | Blocked by policy | Model metering works, but customer endpoint controls also constrain Cursor repository access. Preserve as an environment prerequisite/blocker. |
| Fail before LiteLLM | Not run | Cursor custom-model/provider routing is the remaining problem. Azure/LiteLLM/logger are already independently proven. |
| Reaches LiteLLM but fails | Not run | Diagnose the exact Cursor request shape/path against the known-good LiteLLM Responses configuration. |

## Important methodology note

A successful Test 015 does **not** prove that every Cursor model call traverses the custom endpoint. It proves that the tested Cursor interaction does. During later benchmark runs, LiteLLM request logs and token rows remain the evidence for which calls were actually observed.

Likewise, do not use Codex Test 014 token totals as a direct Cursor baseline. Codex and Cursor are different agents with different context construction and tool behavior.

## Result summary

```text
PHASE A: PENDING
PHASE B: PENDING
OVERALL: PENDING
```

Commit this file with the results before introducing CoreStory MCP or customer source.
