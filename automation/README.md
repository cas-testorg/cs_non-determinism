# Cursor Automation Smoke Test

This directory contains an initial PowerShell harness for testing one complete automated investigation cycle:

**P01 discovery → independent source validation → exported artifacts**

The smoke test intentionally runs only P01. Do not scale to all prompts until the discovery and validation outputs have been reviewed.

## Prerequisites

- Windows PowerShell 5.1 or later
- Cursor Agent CLI available as `agent`
- Cursor CLI authenticated
- CoreStory MCP configured and authenticated in Cursor
- The target C/C++ source repository available locally
- The Test Case 2 rule installed in the target source workspace as an active Cursor project rule

Cursor CLI supports non-interactive execution with `agent -p` and MCP enable/disable commands. The harness uses Ask mode so the analysis should remain read-only.

## Determine the CoreStory MCP Identifier

Before running the harness:

```powershell
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

1. Records the current MCP list.
2. Enables the configured CoreStory MCP server.
3. Runs Test Case 2 P01 in a fresh non-interactive Cursor invocation.
4. Saves the discovery result.
5. Disables the CoreStory MCP server.
6. Records MCP state for the validation phase.
7. Builds an independent-validation prompt containing the discovery candidate set.
8. Runs validation in a new Cursor invocation against local source only.
9. Saves discovery, validation, exact validation input, MCP-state snapshots, and run metadata.
10. Re-enables CoreStory in a `finally` block even if the test fails.

## Output

Each run creates a timestamped directory under:

```text
results/p01-smoke/<timestamp>/
```

with:

```text
metadata.json
mcp-before.txt
mcp-validation.txt
P01.discovery.md
P01.validation-prompt.md
P01.validation.md
README.md
```

The `results/` directory should remain local and should not be committed as test input.

## Independence Check

Disabling CoreStory before validation is stronger than relying on the prompt prohibition alone. Still review:

- `mcp-validation.txt`
- the Cursor CLI/session transcript, if available in the installed CLI version
- the validation output for any indication that CoreStory/MCP/prior artifacts were used

Do not score the validation as independent if CoreStory was available or invoked during that validation run.

## First-Test Success Criteria

The smoke test is successful if:

- discovery completes with CoreStory enabled;
- the discovery result is saved;
- CoreStory is disabled before validation;
- validation completes in a separate invocation;
- validation is grounded in local source rather than simply agreeing with discovery;
- all expected artifacts are exported;
- CoreStory is re-enabled after the script exits.

Once P01 passes these checks, the same harness can be generalized to iterate serially over all 10 Test Case 2 prompts and produce a normalized report dataset.

## Real Example
```powershell
cd C:\Users\carys\cs_non-determinism-main\cs_non-determinism-main
agent mcp list
agent models
.\automation\run-p01-smoke-test.ps1 -SourceRoot "C:\PATH\TO\CUSTOMER\SOURCE" -CoreStoryMcp "corestory"
.\automation\run-p01-smoke-test.ps1 `
  -SourceRoot "C:\path\to\customer-source" `
  -CoreStoryMcp "corestory" `
  -AgentCommand "cursor-agent"
```
