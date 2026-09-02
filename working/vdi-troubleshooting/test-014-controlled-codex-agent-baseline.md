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
PASTE RESULT HERE
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
PASTE ONLY RELEVANT STARTUP/ERROR OUTPUT HERE
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
PASTE RESULT HERE
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
PASTE RESULT HERE
```

Preserve the Codex summary line showing total `tokens used`.

## 7. Capture all Test 014 token rows

Immediately after Codex completes:

```powershell
Get-Content $env:USERPROFILE\token-metering\token_usage.jsonl | Select-String '"run": "test-014-codex-agent-baseline"'
```

### Test 014 token rows

```text
PASTE RESULT HERE
```

Do not collapse multiple rows. If Codex makes multiple model requests, preserve every row.

## 8. Capture LiteLLM request lines

From the LiteLLM console, preserve the request/status lines generated by this Codex invocation.

### LiteLLM request result

```text
PASTE RELEVANT REQUEST/STATUS LINES HERE
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
PASTE RESULT HERE
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
PASTE RESULT HERE
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
