# TC-001B — CoreStory Discovery

## Purpose

Run the same CTS nondeterminism discovery as TC-001A with CoreStory enabled, while holding the local environment, prompt, source scope, Cursor settings, and Synopsys skill installation constant.

TC-001B is the matching local CoreStory arm for the immediate directional comparison with TC-001A. It is **not** the final Synopsys-owned apples-to-apples benchmark.

## Comparison rule

The intended experimental change from TC-001A is only:

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
```

Everything else should remain the same unless Cursor itself changes behavior.

## Test arm

**With CoreStory**

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
CoreStory governing rule file=code-analysis-v2.mdc
Explore Subagent Model=Disabled
Ground truth=Hidden
```

Synopsys skills remain enabled and unmodified.

## Source scope

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

Use the same CTS source state used by TC-001A.

## Model controls

Use the same visible model configuration used for TC-001A.

```text
UI_SELECTED_MODEL=Claude Opus 4.8
CURSOR_USAGE_RECORDED_MODEL=
VERIFIED_EXECUTION_MODEL=
```

Do not intentionally select Auto. Because the baseline showed that Cursor may autonomously create child sessions even when Explore Subagent Model is disabled, record the model attribution of parent and child sessions separately where telemetry permits.

Do not change model settings during the run in an attempt to normalize Cursor behavior.

## CoreStory controls

Before execution:

1. Enable the CoreStory MCP connection and confirm it is connected.
2. Enable/apply `code-analysis-v2.mdc` as the governing CoreStory rule for this workspace/session.
3. Do not modify the rule content for this test.
4. Do not add CoreStory-specific language to the user prompt.
5. Do not manually direct the agent to specific CoreStory MCP tools.
6. Let the governing rule and available MCP intelligence influence the investigation naturally.
7. Preserve evidence of CoreStory MCP calls, including tool names/counts and any failed/retried calls where recoverable.

## Environment controls

Before starting:

1. Confirm sufficient free disk space exists on `C:` for the complete run and report artifacts.
2. Start a fresh Cursor conversation.
3. Confirm the intended CTS workspace is open.
4. Confirm `/nd-code-analyzer` is available.
5. Confirm CoreStory MCP is enabled and connected.
6. Confirm `code-analysis-v2.mdc` is active.
7. Confirm Explore Subagent Model is disabled.
8. Explicitly select Claude Opus 4.8; confirm the UI is not set to Auto.
9. Confirm held-out TSan/Coverity files are not available to the agent.
10. Enable Cursor Request Traces at `Trace` level.
11. Record the start time immediately before submitting the prompt.

### Skill-package control

Do **not** change the installed Synopsys skill package between TC-001A and TC-001B.

TC-001A showed that `scan_nd.py` was unavailable and Cursor created its own PowerShell/ripgrep Stage-1 scanner from the pattern catalog. That remains part of the local test environment for TC-001B. Correcting or adding those scripts only for this arm would invalidate the immediate comparison.

The final Synopsys-owned benchmark should validate the intended skill package and dependencies before execution.

## Run record

```text
START_TIME_LOCAL=Wednesday, September 9, 2026 2:42:49 PM
END_TIME_LOCAL=Wednesday, September 9, 2026 3:01:55 PM
WALL_CLOCK_RUNTIME=
REQUEST_TRACE_LOG_LEVEL=Trace
```

## Prompt

Use `prompt.md` exactly as written.

The resolved prompt must be identical to TC-001A:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

Do not add phrases such as "use CoreStory," "reduce tokens," "avoid grep," known defects, specific files, or prior TC-001/TC-001A findings.

## Execution rules

Run the prompt once.

Do not steer the analysis after submission unless a strictly environmental clarification is required. Record any intervention as a deviation.

If Cursor autonomously creates child analysis sessions, allow the run to proceed and preserve those sessions. Do not manually force or prevent decomposition after the prompt has been submitted.

If CoreStory MCP fails and Cursor falls back to local-only analysis, preserve the evidence and record the failure rather than silently restarting or correcting the session.

## Required artifacts

Store artifacts under:

```text
results/
  cursor-transcript.md
  nd-report.md
  cursor-output.log
  usage-events.csv
  run-metadata.md
```

Also preserve:

```text
parent/child conversation JSONL exports
candidates.json / findings.json / narrowed packs, if generated
CoreStory MCP call evidence or trace excerpts, where recoverable
```

## Metrics to capture

Capture the same metrics as TC-001A plus CoreStory-specific activity:

- UTC/local start and end time
- wall-clock runtime
- UI-selected model
- telemetry-recorded model(s)
- parent/child session count
- successful/failed child sessions
- source scope/code view
- raw candidate count
- narrowed candidate volume, if available
- HIGH/MEDIUM finding count
- dismissed/non-real classifications
- local repository/tool-call count
- CoreStory MCP call count
- CoreStory MCP failures/retries
- fresh input tokens
- cache-read tokens
- output tokens
- total tokens
- failed/retried local tool calls
- human interventions
- whether the same Stage-1 fallback occurred

## What to compare with TC-001A

The local directional comparison should examine:

- total runtime,
- total Cursor token/context consumption,
- parent/child orchestration behavior,
- broad local `Glob` / `Grep` / `Read` activity,
- CoreStory retrieval activity,
- raw/narrowed candidate volume,
- final elevated finding count,
- false-positive/dismissal burden,
- overlap/difference in discovered findings,
- failures/retries and operational friction.

Do not claim a precise CoreStory percentage improvement if Cursor model attribution or orchestration remains unresolved. Report such measurements as directional observations from this local environment.

## Blind-test rule

TSan/Coverity reference findings remain held-out scoring data for TC-001B.

They must not be used to:

- seed the prompt,
- choose candidate locations,
- steer CoreStory queries,
- identify files for deeper analysis,
- confirm/reject findings during discovery.

Ground-truth comparison occurs only after both discovery arms are preserved.

## Interpretation

TC-001B can provide useful evidence about how access to the CoreStory Intelligence Layer changes Cursor's investigation strategy and economics under the same visible test configuration.

Because TC-001A demonstrated autonomous orchestration variance in Cursor, this pair remains a **directional local comparison**. The authoritative quantitative A/B test should be repeated by Synopsys in their controlled environment with verified model/orchestration telemetry and the intended customer skill package.
