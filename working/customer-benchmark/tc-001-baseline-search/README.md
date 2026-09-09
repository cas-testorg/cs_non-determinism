# TC-001 — Baseline ND Search (No CoreStory)

## Purpose

Establish the baseline discovery result for the controlled Synopsys nondeterminism comparison before CoreStory is introduced.

This run uses the Synopsys-authored `nd-code-analyzer` workflow as-is and must not expose the held-out TSan/Coverity ground-truth data to the agent.

The matching CoreStory run will repeat this test with the same source scope, prompt, model, and session controls. The intended experimental variable is CoreStory MCP + the CoreStory governing rule.

## Test arm

**Baseline / without CoreStory**

- CoreStory MCP: disabled
- CoreStory governing rule (`code-analysis-v2.mdc`): absent or disabled
- Synopsys skills: enabled and unmodified
- Ground truth: hidden
- Sub-agent delegation: disabled for this controlled run
- Model selection: pinned; never `auto`

## Skill under test

Primary skill:

```text
/nd-code-analyzer
```

The skill performs mechanical candidate discovery followed by triage/deeper confirmation and false-positive filtering. Do not replace or rewrite the customer's workflow.

## Source scope

Set the exact source scope before execution and keep it identical for the CoreStory arm.

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

Choose a scope small enough to complete in a practical test window without triggering broad sub-agent fan-out, while still being representative of CTS C++ code.

Do not select or narrow the scope based on the held-out TSan/Coverity locations.

## Model

Search/discovery model:

```text
Claude Opus 4.8 — High
```

If the exact label in Cursor differs, record the exact displayed model/version below before starting.

```text
ACTUAL_MODEL=Claude Opus 4.8.
THINKING_MODE=Name does not indicate thinking mode.  Model name above is exactly how it is displayed in Cursor. 
```

## Run record

Record the execution boundary in UTC. Start time should be captured immediately before submitting the test prompt; end time should be captured when the agent has completed the requested analysis/report.

```text
START_TIME_UTC=Wednesday, September 9, 2026 11:00:40 AM
END_TIME_UTC=Wednesday, September 9, 2026 11:06:42 AM
WALL_CLOCK_RUNTIME=
```

Cursor Request Traces must be enabled at `Trace` level before the run so request/composer identifiers and timestamps can be correlated with Cursor Usage telemetry afterward.

```text
REQUEST_TRACE_LOG_LEVEL=Trace
```

## Prompt

Use `prompt.md` exactly as written after replacing only `<CTS_SCOPE>` with the agreed source scope.

Do not add hints from TSan, Coverity, prior CoreStory runs, prior discovery sessions, or known defect locations.

## Session controls

Before execution:

1. Start from a fresh Cursor conversation/session.
2. Confirm the intended CTS workspace/code view is open.
3. Confirm `nd-code-analyzer` is available.
4. Confirm CoreStory MCP is disabled or unavailable to this session.
5. Confirm the CoreStory-specific `code-analysis-v2.mdc` rule is not active.
6. Confirm the model is pinned to Opus 4.8 High and not `auto`.
7. Confirm the held-out ground-truth CSV/files are not present in the workspace or conversation context.
8. Confirm Cursor Request Traces are enabled and the log level is set to `Trace`.
9. Record `START_TIME_UTC` immediately before submitting the prompt.

## Execute

Run the prompt in `prompt.md` once.

Do not interactively steer the analysis unless the agent requires a strictly environmental clarification such as resolving the local source path. Record any such intervention because it is a test deviation.

When the requested analysis/report is complete, record `END_TIME_UTC` and calculate `WALL_CLOCK_RUNTIME`.

## Required output

Preserve the complete final ND report/candidate output from `nd-code-analyzer`.

At minimum, the result should retain the customer's normal classification/evidence fields needed to distinguish elevated findings from non-real candidates and false positives.

Store run artifacts under this directory using the following shape:

```text
results/
  cursor-transcript.md
  nd-report.md
  cursor-output.log
  usage-events.csv
  run-metadata.md
```

If Cursor or the skill generates `candidates.json` / `findings.json`, preserve them as well.

## Metrics to capture

Record the following without interpreting the ground truth yet:

- UTC start time
- UTC end time
- Wall-clock runtime
- Exact model/version
- Source scope and code commit/view
- Candidate count before deeper filtering, if available
- Final/elevated finding count
- Non-real / dismissed classification count, if available
- Local repository/tool calls, when recoverable from transcript/log
- Fresh input tokens
- Cache-read tokens
- Output tokens
- Total tokens
- Any failed tool calls or retries
- Any human intervention

Token data may be correlated after the run from Cursor Usage CSV + Cursor `output.log`; lack of direct in-session token counters is not a test failure.

## Blind-test rule

The TSan and Coverity reference findings are scoring artifacts only.

They must not be used to:

- seed the prompt,
- choose candidate locations,
- steer discovery,
- confirm/reject findings during this phase,
- or select files for deeper analysis.

Ground-truth comparison happens only after both baseline and CoreStory discovery/verification arms are complete.

## Pass criteria

TC-001 passes as an experimental run when:

- the run completes using the pinned model,
- Synopsys `nd-code-analyzer` is used without modification,
- CoreStory is not available to the agent,
- ground truth remains hidden,
- the exact prompt/scope are recorded,
- the discovery output is preserved,
- runtime and available token telemetry are captured,
- and no material prompt/scope steering occurs during the run.

A low finding count or zero findings is still a valid experimental result and is not itself a test failure.

## Matching CoreStory arm

The later CoreStory discovery test must duplicate this run except for:

```text
CoreStory MCP: enabled
CoreStory governing rule: enabled
```

Everything else — prompt, source scope, model, thinking mode, workspace/code version, and blind-ground-truth controls — should remain the same.
