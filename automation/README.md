# Cursor Automation Smoke Test

This directory contains an initial PowerShell harness for testing one complete automated investigation cycle:

**P01 discovery → independent source validation → exported artifacts**

The smoke test intentionally runs only P01. Do not scale to all prompts until the discovery and validation outputs have been reviewed.

## Prerequisites

- Windows PowerShell 5.1 or later
- Cursor Agent CLI available as `agent`
- Cursor CLI authenticated
- CoreStory MCP configured and authenticated in the **target source workspace**
- The target C/C++ source repository available locally
- The Test Case 2 rule installed in the target source workspace as an active Cursor project rule

Cursor CLI supports non-interactive execution with `agent -p` and MCP enable/disable commands. The harness uses Ask mode so the analysis should remain read-only.

## Model Control

The harness explicitly pins the same model for discovery and validation.

Default:

```text
gpt-5.4-high
```

The selected model is passed with `--model` on every Cursor invocation and recorded in `metadata.json`. This prevents the smoke test from silently using Cursor `auto` model selection.

The model can be overridden with `-Model` if a future controlled run requires a different model.

## MCP Control

The CoreStory MCP configuration is treated as **workspace-scoped** for this experiment.

Discovery runs with:

```text
--approve-mcps
```

so a non-interactive `agent -p` session is explicitly allowed to invoke the configured CoreStory MCP tools.

Validation deliberately does **not** pass `--approve-mcps`, and CoreStory is disabled before that session starts.

The script also restores CoreStory while it is still running from the source workspace. This matters because enabling or disabling MCP from another working directory can act on a different workspace context.

## Determine the CoreStory MCP Identifier

From the target source workspace, run:

```powershell
cd C:\path\to\customer-source
agent mcp list
```

Use the exact CoreStory server identifier shown by Cursor. The script defaults to `corestory`, but it can be overridden.

## Run

From the `cs_non-determinism` repository:

```powershell
.\automation\run-p01-smoke-test.ps1 `
  -SourceRoot "C:\path\to\customer-source" `
  -CoreStoryMcp "corestory"
```

If the CLI command is named `cursor-agent` instead:

```powershell
.\automation\run-p01-smoke-test.ps1 `
  -SourceRoot "C:\path\to\customer-source" `
  -CoreStoryMcp "corestory" `
  -AgentCommand "cursor-agent"
```

## What the Script Does

1. Changes into the target source workspace.
2. Records the current MCP list.
3. Enables the configured CoreStory MCP server.
4. Records the MCP state immediately before discovery.
5. Runs Test Case 2 P01 in a fresh non-interactive Cursor invocation using the explicitly selected model and `--approve-mcps`.
6. Saves the discovery result.
7. Disables the CoreStory MCP server.
8. Records MCP state for the validation phase.
9. Builds an independent-validation prompt containing the discovery candidate set.
10. Runs validation in a new Cursor invocation against local source only, using the same model as discovery and without MCP approval.
11. Saves discovery, validation, exact validation input, MCP-state snapshots, model selection, and run metadata.
12. Re-enables CoreStory in the source workspace in a `finally` block even if the test fails.
13. Records the final MCP state after restoration.

## Output

Each run creates a timestamped directory under:

```text
results/p01-smoke/<timestamp>/
```

with:

```text
metadata.json
mcp-before.txt
mcp-discovery.txt
mcp-validation.txt
mcp-after.txt
P01.discovery.md
P01.validation-prompt.md
P01.validation.md
README.md
```

The `results/` directory should remain local and should not be committed as test input.

## Independence Check

Disabling CoreStory before validation is stronger than relying on the prompt prohibition alone. Still review:

- `mcp-discovery.txt` — CoreStory should be enabled/ready before discovery
- `mcp-validation.txt` — CoreStory should be disabled for validation
- `mcp-after.txt` — CoreStory should be enabled/ready after restoration
- the Cursor CLI/session transcript, if available in the installed CLI version
- the validation output for any indication that CoreStory/MCP/prior artifacts were used

Do not score the validation as independent if CoreStory was available or invoked during that validation run.

## First-Test Success Criteria

The smoke test is successful if:

- discovery starts with CoreStory enabled;
- the non-interactive discovery session is explicitly allowed to invoke MCP tools;
- discovery output confirms CoreStory was actually used rather than unavailable or unapproved;
- `gpt-5.4-high` (or the explicitly supplied `-Model`) is used for both stages;
- the discovery result is saved;
- CoreStory is disabled before validation;
- validation completes in a separate invocation;
- validation is grounded in local source rather than simply agreeing with discovery;
- all expected artifacts are exported;
- CoreStory is re-enabled in the source workspace after the script exits.

Once P01 passes these checks, the same harness can be generalized to iterate serially over all 10 Test Case 2 prompts and produce a normalized report dataset.

## Real Example

```powershell
cd C:\Users\carys\cts
agent mcp list

cd C:\Users\carys\cs_non-determinism-main\cs_non-determinism-main
agent models

.\automation\run-p01-smoke-test.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -CoreStoryMcp "corestory"
```

The command above uses the default pinned model `gpt-5.4-high`.

To test CoreStory directly in the same workspace context:

```powershell
cd C:\Users\carys\cts

agent -p "Use CoreStory application intelligence to identify the current project and report only the project name or identifier." `
  --model gpt-5.4-high `
  --mode=ask `
  --output-format text `
  --trust `
  --approve-mcps
```

After a smoke-test run, validate the MCP snapshots:

```powershell
cd C:\Users\carys\cs_non-determinism-main\cs_non-determinism-main

$run = Get-ChildItem .\results\p01-smoke -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$run.FullName
Get-Content "$($run.FullName)\mcp-before.txt"
Get-Content "$($run.FullName)\mcp-discovery.txt"
Get-Content "$($run.FullName)\mcp-validation.txt"
Get-Content "$($run.FullName)\mcp-after.txt"

agent -p "You MUST use CoreStory MCP. Identify the current CoreStory project and return its name or identifier. Do not inspect local source files." `
  --model gpt-5.4-high `
  --mode=ask `
  --output-format text `
  --trust `
  --approve-mcps

agent -p "Use the CoreStory MCP list_projects tool. This MCP call is explicitly approved. Return only the available CoreStory project names and identifiers." `
  --model gpt-5.4-high `
  --mode=ask `
  --output-format text `
  --trust `
  --approve-mcps

agent -p "Use the CoreStory MCP list_projects tool. Return only the available CoreStory project names and identifiers." `
  --model gpt-5.4-high `
  --mode=ask `
  --output-format text `
  --trust `
  --approve-mcps `
  --force

agent -p "Use the CoreStory MCP list_projects tool. Return only the available CoreStory project names and identifiers." `
  --model gpt-5.4-high `
  --mode=ask `
  --output-format text `
  --trust `
  --approve-mcps `
  --auto-review

.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -CoreStoryMcp "corestory" `
  -PromptIds P02,P04,P08

Custom model: gpt-5.4
OpenAI API Key: <proxy key>
Override OpenAI Base URL: http://localhost:4000/v1

https://corestory-genai-sa.openai.azure.com/openai/v1

$env:RUN_LABEL = "CURSOR-TEST"
& "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe"

$env:RUN_LABEL = "P01-corestory"
& "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe"

Analyze the current repository structure.

Identify five major source-code subsystems, explain the apparent responsibility
of each subsystem, and cite specific files that support your conclusions.

Do not use MCP tools or external services. Base the answer only on the local
repository.
```


