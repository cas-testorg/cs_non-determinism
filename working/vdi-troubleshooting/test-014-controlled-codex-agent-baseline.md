# Test 014 — Controlled Codex Agent Baseline

## Purpose

Test 013 proved the complete transport and metering path:

```text
Codex CLI → LiteLLM /v1/responses → Azure GPT-5.4 → token_usage.jsonl
```

This test moves one step beyond connectivity and measures a small, reproducible agent task against a deliberately tiny local repository.

This is still **not** the Synopsys nondeterminism benchmark and does **not** use CoreStory. Its purpose is to establish what token accounting looks like when Codex actually inspects source files and answers a code-understanding question.

We want to learn:

1. Whether Codex can inspect a repository successfully through the validated LiteLLM route.
2. How many model calls a simple repository-understanding task generates.
3. How much input, cached input, output, reasoning, and total token usage the task consumes.
4. Whether the logger captures every model request consistently.

Do not use customer source for this test.

## 1. Stop the Test 013 LiteLLM process

If LiteLLM is still running from Test 013, stop it with:

```text
Ctrl+C
```

Do not change `config.yaml`, `usage_logger.py`, the Azure settings, or the Codex provider configuration.

## 2. Create a tiny neutral test repository

Open PowerShell and run:

```powershell
$testRepo = Join-Path $env:USERPROFILE "codex-metering-test"

if (Test-Path $testRepo) {
    Remove-Item $testRepo -Recurse -Force
}

New-Item -ItemType Directory -Path $testRepo -Force | Out-Null
Set-Location $testRepo

git init | Out-Null
```

Create `calculator.py`:

```powershell
@'
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    result = 0
    for _ in range(b):
        result += a
    return result


def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b
'@ | Set-Content .\calculator.py -Encoding UTF8
```

Create `app.py`:

```powershell
@'
from calculator import add, subtract, multiply, divide


def calculate(operation, left, right):
    if operation == "add":
        return add(left, right)
    if operation == "subtract":
        return subtract(left, right)
    if operation == "multiply":
        return multiply(left, right)
    if operation == "divide":
        return divide(left, right)
    raise ValueError(f"unknown operation: {operation}")
'@ | Set-Content .\app.py -Encoding UTF8
```

Create `README.md`:

```powershell
@'
# Calculator Metering Test

A deliberately small Python repository used only to validate Codex agent token metering.

`app.py` dispatches calculator operations to functions implemented in `calculator.py`.
'@ | Set-Content .\README.md -Encoding UTF8
```

Commit the neutral repository so Codex sees a normal Git workspace:

```powershell
git add .
git -c user.name="Metering Test" -c user.email="metering-test@example.invalid" commit -m "Create metering test repository" | Out-Null

git status --short
```

Expected `git status --short` output is empty.

### Repository setup result

```text
PS C:\Users\carys\codex-metering-test> git add .
PS C:\Users\carys\codex-metering-test> git -c user.name="Metering Test" -c user.email="metering-test@example.invalid" commit -m "Create metering test repository" | Out-Null
PS C:\Users\carys\codex-metering-test> git status --short
PS C:\Users\carys\codex-metering-test>
```

## 3. Start LiteLLM with a dedicated run label

In the token-metering PowerShell window:

```powershell
Set-Location $env:USERPROFILE\token-metering
$env:RUN_LABEL="test-014-codex-agent-baseline"
litellm --config .\config.yaml --port 4000
```

Leave this window running.

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
←[1;37m#           'It would help me if you could add...'            #←[0m
←[1;37m#        https://github.com/BerriAI/litellm/issues/new        #←[0m
←[1;37m#                                                            #←[0m
←[1;37m#------------------------------------------------------------#←[0m

 Thank you for using LiteLLM! - Krrish & Ishaan



←[1;31mGive Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new←[0m


←[32mLiteLLM: Proxy initialized with Config, Set models:←[0m
←[32m    gpt-5.4←[0m
←[92m16:32:23 - LiteLLM:WARNING←[0m: utils.py:2898 - register_model: model=8b0a4659cf250fb2135b7940dee052bf2fc834d62511964ba0574efcad031c37 not in built-in cost map and no prefix/region variant matched; cache cost fields will default to 0. To track cache cost, add cache_creation_input_token_cost and cache_read_input_token_cost to model_info
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
```

## 4. Confirm the Codex client key in the Codex window

In the PowerShell window that will run Codex:

```powershell
$env:LITELLM_API_KEY="sk-local"
Write-Host "LITELLM_API_KEY set = $([bool]$env:LITELLM_API_KEY)"
```

Expected:

```text
LITELLM_API_KEY set = True
```

## 5. Record the token-log boundary

Before running Codex:

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl -Tail 3 -ErrorAction SilentlyContinue
```

### Token log before Test 014

```text
{"ts": "2026-09-02T19:25:16.086260+00:00", "run": "test-012-proxy-validation", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.173, "input_tokens": 12, "cached_input_tokens": 0, "uncached_input_tokens": 12, "output_tokens": 6, "reasoning_tokens": 0, "visible_output_tokens": 6, "total_tokens": 18}
{"ts": "2026-09-02T20:56:10.445383+00:00", "run": "test-013-codex-litellm", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 3.709, "input_tokens": 10399, "cached_input_tokens": 0, "uncached_input_tokens": 10399, "output_tokens": 27, "reasoning_tokens": 14, "visible_output_tokens": 13, "total_tokens": 10426}
```

## 6. Run one controlled read-only repository-understanding task

From the tiny test repository:

```powershell
Set-Location $env:USERPROFILE\codex-metering-test

codex exec --sandbox read-only "Inspect this repository. Identify the public calculator operations, state which files implement the dispatch logic and arithmetic logic, and identify one concrete behavioral limitation in the multiply implementation. Do not modify any files. Keep the answer under 120 words."
```

Because this is now a Git repository, do **not** use `--skip-git-repo-check` unless Codex unexpectedly rejects the newly initialized repository. If it does reject it, preserve the exact error before retrying.

The expected substance is approximately:

```text
Operations: add, subtract, multiply, divide.
Dispatch: app.py.
Arithmetic implementations: calculator.py.
Multiply limitation: range(b) means the repeated-addition implementation does not correctly support negative multipliers.
```

Exact wording is not important. We care that Codex correctly inspects the files and identifies the concrete limitation.

### Codex result

```text
 codex exec --sandbox read-only "Inspect this repository. Identify the public calculator operations, state which files implement the dispatch logic and arithmetic logic, and identify one concrete behavioral limitation in the multiply implementation. Do not modify any files. Keep the answer under 120 words."
OpenAI Codex v0.152.1
--------
←[1mworkdir:←[0m C:\Users\carys\codex-metering-test
←[1mmodel:←[0m gpt-5.4
←[1mprovider:←[0m litellm
←[1mapproval:←[0m never
←[1msandbox:←[0m read-only
←[1mreasoning effort:←[0m medium
←[1mreasoning summaries:←[0m none
←[1msession id:←[0m 01a0640f-75c3-7603-99b0-f000caa41b4b
--------
←[36muser←[0m
Inspect this repository. Identify the public calculator operations, state which files implement the dispatch logic and arithmetic logic, and identify one concrete behavioral limitation in the multiply implementation. Do not modify any files. Keep the answer under 120 words.
←[35m←[3mcodex←[0m←[0m
Inspecting the repository structure first, then I’ll trace where calculator operations are exposed and how dispatch and arithmetic are split.
←[2m2026-09-02T21:38:56.534677Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `"C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -Command 'git status --short'`: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\windows\\\\\\\\System32\\\\\\\\WindowsPowerShell\\\\\\\\v1.0\\\\\\\\powershell.exe\\\" -NoProfile -Command 'git status --short'` rejected: blocked by policy\")" }
←[2m2026-09-02T21:38:56.534966Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `"C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -Command 'rg --files'`: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\windows\\\\\\\\System32\\\\\\\\WindowsPowerShell\\\\\\\\v1.0\\\\\\\\powershell.exe\\\" -NoProfile -Command 'rg --files'` rejected: blocked by policy\")" }
←[35m←[3mcodex←[0m←[0m
Terminal execution is blocked in this environment, so I’m switching to direct file inspection through available tooling paths.
←[2m2026-09-02T21:38:59.513053Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `"C:\\windows\\system32\\cmd.exe" /c dir`: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\windows\\\\\\\\system32\\\\\\\\cmd.exe\\\" /c dir` rejected: blocked by policy\")" }
←[2m2026-09-02T21:39:01.494965Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `"C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -Command Get-ChildItem`: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\windows\\\\\\\\System32\\\\\\\\WindowsPowerShell\\\\\\\\v1.0\\\\\\\\powershell.exe\\\" -NoProfile -Command Get-ChildItem` rejected: blocked by policy\")" }
←[1mweb search:←[0m
←[1mweb search:←[0m "codex-metering-test" github
←[35m←[3mcodex←[0m←[0m
I haven’t found a direct local file-read tool. I’m checking whether there’s an alternate repository-inspection capability exposed in this session before I answer.
←[1mweb search:←[0m
←[1mweb search:←[0m "codex-metering-test"
←[2m2026-09-02T21:39:38.184454Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `"C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -Command Get-ChildItem`: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\windows\\\\\\\\System32\\\\\\\\WindowsPowerShell\\\\\\\\v1.0\\\\\\\\powershell.exe\\\" -NoProfile -Command Get-ChildItem` rejected: blocked by policy\")" }
←[1mweb search:←[0m
←[1mweb search:←[0m
←[2m2026-09-02T21:39:43.013412Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mapproval policy is Never; reject command — you cannot ask for escalated permissions if the approval policy is Never
←[1mweb search:←[0m
←[1mweb search:←[0m "metering-test" calculator github
←[2m2026-09-02T21:39:52.224671Z←[0m ←[31mERROR←[0m ←[2mcodex_core::tools::router←[0m←[2m:←[0m ←[3merror←[0m←[2m=←[0mexec_command failed for `cmd.exe /c ls`: CreateProcess { message: "Rejected(\"`cmd.exe` rejected: blocked by policy\")" }
←[35m←[3mcodex←[0m←[0m
I can’t inspect this repository from the current session: local command execution is blocked and there’s no alternate local file-read tool exposed, so I can’t reliably identify the operation list, dispatch file, arithmetic file, or the multiply limitation without guessing.

If you want a precise answer, send:
- `rg --files`
- the calculator entrypoint file
- the file that defines `multiply`

Then I can answer in one short pass under your requested word limit.
←[2mtokens used←[0m
22,122
```

Preserve the Codex summary line showing total `tokens used`.

## 7. Capture all Test 014 token rows

Immediately after Codex completes:

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl | Select-String '"run": "test-014-codex-agent-baseline"'
```

### Test 014 token rows

```text
{"ts": "2026-09-02T21:38:56.412340+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 3.025, "input_tokens": 10438, "cached_input_tokens": 0,
"uncached_input_tokens": 10438, "output_tokens": 193, "reasoning_tokens": 43, "visible_output_tokens": 150, "total_tokens": 10631}
{"ts": "2026-09-02T21:38:59.479044+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 2.816, "input_tokens": 10839, "cached_input_tokens":
10624, "uncached_input_tokens": 215, "output_tokens": 210, "reasoning_tokens": 131, "visible_output_tokens": 79, "total_tokens": 11049}
{"ts": "2026-09-02T21:39:01.484024+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.946, "input_tokens": 11117, "cached_input_tokens":
11008, "uncached_input_tokens": 109, "output_tokens": 60, "reasoning_tokens": 10, "visible_output_tokens": 50, "total_tokens": 11177}
{"ts": "2026-09-02T21:39:03.106503+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.603, "input_tokens": 11279, "cached_input_tokens":
11136, "uncached_input_tokens": 143, "output_tokens": 48, "reasoning_tokens": 15, "visible_output_tokens": 33, "total_tokens": 11327}
{"ts": "2026-09-02T21:39:06.397810+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 3.271, "input_tokens": 11344, "cached_input_tokens":
11264, "uncached_input_tokens": 80, "output_tokens": 204, "reasoning_tokens": 173, "visible_output_tokens": 31, "total_tokens": 11548}
{"ts": "2026-09-02T21:39:22.678594+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 16.216, "input_tokens": 13670, "cached_input_tokens":
11520, "uncached_input_tokens": 2150, "output_tokens": 332, "reasoning_tokens": 260, "visible_output_tokens": 72, "total_tokens": 14002}
{"ts": "2026-09-02T21:39:38.187274+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 15.491, "input_tokens": 14150, "cached_input_tokens":
13568, "uncached_input_tokens": 582, "output_tokens": 410, "reasoning_tokens": 356, "visible_output_tokens": 54, "total_tokens": 14560}
{"ts": "2026-09-02T21:39:43.024979+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 4.81, "input_tokens": 14625, "cached_input_tokens":
14080, "uncached_input_tokens": 545, "output_tokens": 310, "reasoning_tokens": 235, "visible_output_tokens": 75, "total_tokens": 14935}
{"ts": "2026-09-02T21:39:52.095795+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 9.047, "input_tokens": 19230, "cached_input_tokens":
14464, "uncached_input_tokens": 4766, "output_tokens": 592, "reasoning_tokens": 541, "visible_output_tokens": 51, "total_tokens": 19822}
{"ts": "2026-09-02T21:39:57.695767+00:00", "run": "test-014-codex-agent-baseline", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 5.42, "input_tokens": 15276, "cached_input_tokens":
14976, "uncached_input_tokens": 300, "output_tokens": 435, "reasoning_tokens": 335, "visible_output_tokens": 100, "total_tokens": 15711}
```

Do not collapse multiple rows. If Codex makes multiple model requests, preserve every row.

## 8. Capture LiteLLM request lines

From the LiteLLM console, preserve the request/status lines generated by this Codex invocation.

### LiteLLM request result

```text
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
←[32mINFO←[0m:     127.0.0.1:54039 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54046 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54049 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54052 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54056 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54059 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54062 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54065 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54068 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:54074 - "←[1mPOST /v1/responses HTTP/1.1←[0m" ←[32m200 OK←[0m
```

## 9. Calculate aggregate usage

Run:

```powershell
$rows = Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl |
    ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object { $_.run -eq "test-014-codex-agent-baseline" }

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

### Aggregate usage result

```text
 .\calculate_usage.ps1

Requests            : 10
InputTokens         : 131968
CachedInputTokens   : 112640
UncachedInputTokens : 19328
OutputTokens        : 2794
ReasoningTokens     : 2099
VisibleOutputTokens : 695
TotalTokens         : 134762
```

## Validation criteria

Test 014 passes when:

```text
Codex runs against the tiny Git repository
Codex uses model gpt-5.4 / provider litellm
Codex correctly identifies the repository structure and multiply limitation
No files are modified
LiteLLM receives one or more /v1/responses requests
Every successful model request produces a token_usage.jsonl row
Token rows contain non-zero input/output/total counts
Aggregate TotalTokens is consistent with the Codex-reported usage for the completed run, accounting for how Codex reports multi-call totals
```

After Codex completes, verify the repository remains unchanged:

```powershell
git status --short
```

### Final repository status

```text
No results. Clean
```

Expected: no output.

## Interpretation

- **Pass:** We have a measured, real agent baseline and can move to a controlled comparison involving CoreStory/MCP or the first customer benchmark case.
- **Correct answer but unexpectedly large token usage:** preserve it. That is measurement evidence, not an infrastructure failure.
- **Multiple model calls:** preserve all rows. The number of calls is part of the agent-cost baseline.
- **Codex modifies files despite the prompt:** preserve the result and verify sandbox behavior before any customer-code test.
- **Token aggregate does not reconcile with Codex:** do not proceed to benchmarking until the discrepancy is understood.

## Result summary

```text
RESULT: PENDING
```

Commit this file with the results before moving to CoreStory-assisted or customer-code testing.
