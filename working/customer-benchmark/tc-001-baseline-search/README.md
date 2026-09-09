# TC-001 — Baseline ND Search (No CoreStory)

## Status

**Pilot run completed — retain for diagnostic/directional evidence, but do not use as the authoritative baseline for the final A/B comparison.**

TC-001 exposed several environmental and telemetry limitations that make its quantitative results unsuitable for a controlled apples-to-apples benchmark. The artifacts are intentionally preserved because they provide useful evidence about the workflow, token economics, model-attribution challenges, and controls required for subsequent testing.

A clean control rerun is defined separately as **TC-001A**.

## Purpose

Establish the baseline discovery result for the controlled Synopsys nondeterminism comparison before CoreStory is introduced.

This run uses the Synopsys-authored `nd-code-analyzer` workflow and must not expose the held-out TSan/Coverity ground-truth data to the agent.

The matching CoreStory run will repeat the test with the same source scope, prompt, model selection, and session controls. The intended experimental variable is CoreStory MCP + the CoreStory governing rule.

## Test arm

**Baseline / without CoreStory**

- CoreStory MCP: disabled
- CoreStory governing rule (`code-analysis-v2.mdc`): absent or disabled
- Synopsys skills: enabled and unmodified
- Ground truth: hidden
- Sub-agent delegation: disabled for this controlled run
- Model selection: intended to be pinned; never intentionally `auto`

## Skill under test

Primary skill:

```text
/nd-code-analyzer
```

The intended workflow is mechanical candidate discovery followed by triage/deeper confirmation and false-positive filtering. Do not intentionally replace or rewrite the customer's workflow.

## Source scope

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

Do not select or narrow the scope based on held-out TSan/Coverity locations.

## Model

Intended search/discovery model:

```text
Claude Opus 4.8
```

Cursor displayed Claude Opus 4.8 as the selected model for the run. However, the corresponding Cursor Usage telemetry recorded the large benchmark events as `auto`. The exported conversation JSONL does not independently identify the underlying model for each assistant turn. Therefore model attribution for TC-001 is **unresolved** and the run must not be represented as a verified Claude Opus 4.8 execution.

```text
UI_SELECTED_MODEL=Claude Opus 4.8
CURSOR_USAGE_RECORDED_MODEL=auto
VERIFIED_EXECUTION_MODEL=UNKNOWN
```

## Run record

```text
START_TIME_UTC=2026-09-09T16:00:40Z
END_TIME_UTC=2026-09-09T16:06:42Z
WALL_CLOCK_RUNTIME=NOT_VALID_FOR_COMPARISON
```

The nominal execution boundary above is retained from the run record, but wall-clock runtime should not be used for comparison because disk exhaustion interrupted report persistence and required subsequent human intervention.

Cursor Request Traces were intended to be enabled at `Trace` level for correlation with Cursor Usage telemetry.

```text
REQUEST_TRACE_LOG_LEVEL=Trace
```

## Prompt

The discovery prompt was:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

No TSan/Coverity defect locations were intentionally supplied to the discovery prompt.

## Observed result

The run produced a shareable report with four elevated findings:

- 2 HIGH
- 2 MEDIUM

The findings covered RNG behavior, pointer-container ordering, parallel floating-point accumulation, and hardware-concurrency-dependent behavior.

These findings remain useful as preliminary discovery output. Ground-truth scoring is intentionally deferred until the appropriate comparison phase.

## Known limitations / deviations

### 1. Disk exhaustion interrupted the run

The `C:` drive exhausted available space while Cursor attempted to persist the report. Cursor reported that the file could not be saved reliably. Disk space was then cleared and a follow-up user message requested that the report be written to file.

Impact:

- the run was not uninterrupted,
- human intervention occurred,
- end-to-end runtime is not representative,
- report-writing behavior cannot be compared cleanly with another arm.

### 2. Intended skill scripts were unavailable

During execution Cursor attempted to locate `scan_nd.py` and `render_report.py`, reported that they were not present in the installed skill tree, and substituted a manual workflow using repository search/ripgrep plus manual Stage 2–3 triage.

Impact:

- the run did not execute the intended scripted workflow exactly as expected,
- the substitution must be held constant in any immediate directional comparison unless the environment is corrected before both arms,
- the authoritative customer-run benchmark should validate that the intended skill package and dependencies are installed consistently.

### 3. Model attribution is unresolved

The Cursor UI was configured for Claude Opus 4.8, but Cursor Usage telemetry labeled the associated large requests as `auto`.

Impact:

- the actual underlying model cannot be proven from the preserved artifacts,
- precise model-specific token/cost attribution is not defensible,
- subsequent tests must record both the UI-selected model and the model reported by authoritative telemetry.

### 4. Token data is diagnostic, not a final benchmark result

The two large Cursor Usage events associated with the benchmark session were approximately 2.98M and 710K total tokens, or approximately 3.69M combined. Much of that usage was cache-read context.

Impact:

- TC-001 demonstrates that repository-scale agentic discovery can involve substantial context/token consumption,
- these numbers are useful for understanding token economics,
- they must not be presented as the authoritative baseline for a CoreStory percentage-reduction claim because of the run deviations and unresolved model attribution.

### 5. Cursor output log artifact is empty

The preserved `tc-001-baseline-search-cursor.log` is zero bytes. The conversation JSONL and Usage CSV remain available for diagnostic analysis, but the expected log artifact cannot be used for request-level correlation.

## Artifact retention

Preserve all TC-001 artifacts. Do not overwrite this run with the clean rerun.

The pilot remains useful for:

- demonstrating environmental constraints encountered during testing,
- understanding Cursor's local repository investigation behavior,
- illustrating token economics,
- investigating Cursor model-selection/telemetry behavior,
- and defining the controls required for the Synopsys-owned apples-to-apples benchmark.

## Disposition

```text
RUN_CLASSIFICATION=PILOT_WITH_LIMITATIONS
VALID_FOR_FINAL_A_B_METRICS=NO
VALID_FOR_DIRECTIONAL_ANALYSIS=YES
GROUND_TRUTH_EXPOSED=NO
```

The next baseline run is **TC-001A — Clean Baseline Control Rerun**. The matching CoreStory discovery run should use the same environment and controls as TC-001A, changing only CoreStory MCP + the CoreStory governing rule.
