# Test 013 — Codex CLI → LiteLLM → Azure GPT-5.4

## Purpose

Test 012 validated the metering layer for LiteLLM Responses API calls. This test adds Codex as the client and proves the complete path:

```text
Codex CLI
  → LiteLLM localhost:4000
  → Azure OpenAI GPT-5.4
  → token_usage.jsonl
```

This is an integration smoke test, not a benchmark. Use a trivial prompt and do not involve the customer codebase yet.

The test is successful if:

1. Codex uses the local LiteLLM provider.
2. LiteLLM receives a Responses API request.
3. Azure GPT-5.4 returns a valid answer.
4. `token_usage.jsonl` receives one or more rows from the Codex request with non-zero input/output usage.

Do not commit credentials, API keys, customer source, or sensitive prompt/response content.

## Current status

The initial Codex invocation stopped locally before making a model request:

```text
Not inside a trusted directory and --skip-git-repo-check was not specified.
```

`codex exec --help` confirms that Codex 0.152.1 supports `--skip-git-repo-check` specifically to allow `exec` outside a Git repository. The continuation below uses that narrow option. Do not use `--dangerously-bypass-approvals-and-sandbox`; this test does not require bypassing sandbox or approval controls.

## 1. Confirm Codex is available

```powershell
codex --version
```

Previously confirmed:

```text
codex-cli 0.152.1
```

## 2. Keep the existing Test 013 Codex configuration

Do not change `%USERPROFILE%\.codex\config.toml` from the Test 013 configuration:

```toml
model = "gpt-5.4"
model_provider = "litellm"
model_reasoning_effort = "medium"

[model_providers.litellm]
name = "LiteLLM (local)"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_API_KEY"
wire_api = "responses"
```

LiteLLM's Azure configuration must also remain exactly as validated in Test 012.

## 3. Confirm the local LiteLLM client key in the Codex PowerShell window

```powershell
$env:LITELLM_API_KEY="sk-local"
Write-Host "LITELLM_API_KEY set = $([bool]$env:LITELLM_API_KEY)"
```

Expected:

```text
LITELLM_API_KEY set = True
```

Do not print the value itself.

## 4. Keep LiteLLM running with the Test 013 run label

In the PowerShell window used to run LiteLLM:

```powershell
$env:RUN_LABEL="test-013-codex-litellm"
litellm --config .\config.yaml --port 4000
```

If the existing Test 013 LiteLLM process is still running with this label, leave it running. Do not restart it unnecessarily.

## 5. Record the token-log tail before the retry

From the token-metering directory:

```powershell
Get-Content .\token_usage.jsonl -Tail 3 -ErrorAction SilentlyContinue
```

The failed trust-check attempt should not have generated a new LiteLLM token row because Codex stopped before making a model request.

### Token log before retry

```text
{"ts": "2026-09-02T19:25:16.086260+00:00", "run": "test-012-proxy-validation", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.173, "input_tokens": 12, "cached_input_tokens": 0, "uncached_input_tokens": 12, "output_tokens": 6, "reasoning_tokens": 0, "visible_output_tokens": 6, "total_tokens": 18}
```

## 6. Retry the trivial Codex request with only the Git repository check bypassed

Run from the same neutral directory used previously:

```powershell
codex exec --skip-git-repo-check "Reply with exactly: CODEX_LITELLM_OK"
```

This option only allows `codex exec` to run outside a Git repository. It does not disable Codex sandboxing or approval controls.

### Codex retry result

```text
PS C:\Users\carys\token-metering> codex exec --skip-git-repo-check "Reply with exactly: CODEX_LITELLM_OK"
OpenAI Codex v0.152.1
--------
←[1mworkdir:←[0m C:\Users\carys\token-metering
←[1mmodel:←[0m gpt-5.4
←[1mprovider:←[0m litellm
←[1mapproval:←[0m never
←[1msandbox:←[0m read-only
←[1mreasoning effort:←[0m medium
←[1mreasoning summaries:←[0m none
←[1msession id:←[0m 01a063e8-55b8-7ad2-8ce5-ac0c56268fb7
--------
←[36muser←[0m
Reply with exactly: CODEX_LITELLM_OK
←[35m←[3mcodex←[0m←[0m
CODEX_LITELLM_OK
←[2mtokens used←[0m
10,426
```

A successful result should include:

```text
CODEX_LITELLM_OK
```

Preserve enough CLI output to show the selected model/provider if Codex displays it.

If a different error occurs, stop there and preserve the exact error. Do not change `config.toml`, LiteLLM, Azure credentials, or sandbox settings yet.

## 7. Capture the LiteLLM token log immediately after the retry

```powershell
Get-Content .\token_usage.jsonl -Tail 10
```

### Token log after Codex retry

```text
{"ts": "2026-09-02T19:25:16.086260+00:00", "run": "test-012-proxy-validation", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.173, "input_tokens": 12, "cached_input_tokens": 0, "uncached_input_tokens": 12, "output_tokens": 6, "reasoning_tokens": 0, "visible_output_tokens": 6, "total_tokens": 18}
{"ts": "2026-09-02T20:56:10.445383+00:00", "run": "test-013-codex-litellm", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 3.709, "input_tokens": 10399, "cached_input_tokens": 0, "uncached_input_tokens": 10399, "output_tokens": 27, "reasoning_tokens": 14, "visible_output_tokens": 13, "total_tokens": 10426}
```

For a successful Codex path, look for one or more new rows with:

```text
run       = test-013-codex-litellm
model     = gpt-5.4
call_type = aresponses
```

There may be more than one model request for a single Codex command. Preserve all rows generated by this one command.

## 8. Capture the LiteLLM request result

From the LiteLLM console, copy only the relevant request/status or error lines associated with this retry.

### LiteLLM request result

```text
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
←[32mINFO←[0m:     127.0.0.1:55601 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
```

## Validation criteria

This test passes when all of the following are true:

```text
Codex gets past the local repository trust check
Codex command succeeds
Codex returns CODEX_LITELLM_OK
LiteLLM receives the request
Azure GPT-5.4 answers successfully
One or more new JSONL rows are written
New JSONL rows contain non-zero input/output/total token counts
Run label is test-013-codex-litellm
```

## Interpretation

- **Codex succeeds and JSONL rows appear:** the complete Codex → LiteLLM → Azure → metering path is proven. Move to a controlled agent task next.
- **A new Codex error appears before LiteLLM receives anything:** preserve it. Diagnose the Codex client/configuration layer without changing LiteLLM or Azure.
- **LiteLLM receives the request but returns an error:** preserve the proxy error. Test 012 remains the known-good control.
- **Codex succeeds but no JSONL rows appear:** verify Codex did not bypass the custom provider and inspect the LiteLLM console before changing the logger.
- **Authentication failure against LiteLLM:** verify `LITELLM_API_KEY` exists in the same PowerShell process launching Codex.

## Previous attempt

The original invocation was:

```powershell
codex exec "Reply with exactly: CODEX_LITELLM_OK"
```

Result:

```text
Not inside a trusted directory and --skip-git-repo-check was not specified.
```

This is retained as evidence that the initial attempt stopped at Codex's local repository check and did not yet test the LiteLLM/Azure path.

## Result summary

```text
RESULT: RETRY PENDING — use --skip-git-repo-check
```

Commit this file with the retry result before moving to a real agent task or customer-code benchmark.
