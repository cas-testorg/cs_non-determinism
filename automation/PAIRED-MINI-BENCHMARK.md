# Paired Mini-Benchmark

This harness is a short controlled comparison intended to isolate the incremental effect of CoreStory while keeping prompt quality constant.

## Experimental design

For each selected enhanced v2 prompt, run two fresh Cursor CLI investigations against the same source workspace:

1. **local** — v2 rule + enhanced prompt + local repository, with CoreStory MCP explicitly disabled.
2. **corestory** — the exact same v2 rule + exact same enhanced prompt + local repository, with CoreStory MCP explicitly enabled and approved.

The intended condition variable is CoreStory availability. The default mini-benchmark uses four mechanism-oriented prompts:

- P01 — uninitialized / indeterminate state
- P02 — shared-state concurrency
- P04 — pointer-dependent ordering
- P08 — schedule-dependent / heuristic results

Independent secondary validation is deliberately excluded from this short benchmark. Outputs are discovery results and must not be described as independently validated defects.

## Controls

The runner:

- pins `gpt-5.4-high` by default;
- uses the same prompt file for both sides of each pair;
- assumes the same active v2 Cursor workspace rule for both conditions;
- explicitly disables or enables the workspace-scoped CoreStory MCP before every invocation;
- uses `--approve-mcps --force` only for the CoreStory condition;
- runs each condition as a fresh `agent -p` invocation (no resume/continue conversation state);
- records MCP state per condition;
- records start, completion, elapsed time, exit code, timeout state, and status;
- checkpoints metadata and `comparison.csv` after each condition;
- continues after an individual condition fails;
- restores CoreStory to enabled before exit.

## Run

From the repository root:

```powershell
.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -CoreStoryMcp "corestory"
```

The default per-invocation timeout is 90 minutes. Override it if necessary:

```powershell
.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -TimeoutMinutes 120
```

### P01-only control test

Before launching all eight investigations, run only P01:

```powershell
.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -PromptIds P01
```

Verify both `P01/local` and `P01/corestory` before launching the default four-prompt set.

## Resume

If a run is interrupted, `-Resume` selects the newest run directory and skips condition directories whose metadata status is `completed`:

```powershell
.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -Resume
```

Failed or timed-out conditions are attempted again.

## Optional token telemetry

Token collection is optional and does not change the experiment when disabled. If the existing LiteLLM usage logger is active and Cursor traffic is reaching it, pass the JSONL log path:

```powershell
.\automation\run-paired-mini-benchmark.ps1 `
  -SourceRoot "C:\Users\carys\cts" `
  -EnableTokenMetrics `
  -TokenLogPath "$HOME\token-metering\token_usage.jsonl"
```

For each serial invocation, the runner snapshots the current JSONL line count and copies rows appended during that invocation into `token-usage.jsonl`. It also creates `token-metrics.json` with request count and summed input, cached input, uncached input, output, reasoning, visible-output, and total tokens.

This is intentionally a lightweight integration with the existing metering setup. It does **not** change Cursor model routing or start/reconfigure LiteLLM. Because Cursor may not route all traffic through a custom OpenAI base URL, Cursor token totals can undercount and should be described as directional unless routing has been independently verified. Avoid other traffic through the same LiteLLM logger during the serial benchmark because appended rows are attributed to the active condition by time/sequence.

## Output

Each run is written under:

```text
results/paired-mini/<run-id>/
```

Example:

```text
metadata.json
mcp-initial.txt
mcp-final.txt
comparison.csv
P01/
  local/
    discovery.md
    metadata.json
    mcp-state.txt
    token-usage.jsonl       # when enabled
    token-metrics.json      # when enabled
  corestory/
    discovery.md
    metadata.json
    mcp-state.txt
    token-usage.jsonl       # when enabled
    token-metrics.json      # when enabled
P02/
P04/
P08/
```

`comparison.csv` is an operational summary. It includes prompt, condition, status, elapsed time, and token totals when token collection is enabled.

## Interpretation

The clean comparison is:

> Same model. Same source. Same enhanced prompt. Same v2 rule. CoreStory availability is the intended difference.

Do not compare raw candidate counts as though they were validated defect counts. For a demo or interim readout, useful observations include investigation time, measured token usage, breadth/depth of source paths investigated, candidate findings, mitigated/rejected patterns, and qualitative application context. Independent source validation remains the appropriate next step for any finding that needs to be presented as a confirmed defect.
