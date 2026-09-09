# TC-001A — Clean Baseline Control Rerun (No CoreStory)

## Status

**Completed baseline — usable for the immediate directional comparison, with orchestration variance noted.**

```text
RUN_CLASSIFICATION=COMPLETED_WITH_ORCHESTRATION_VARIANCE
VALID_FOR_DIRECTIONAL_COMPARISON=YES
VALID_AS_FINAL_CUSTOMER_A_B_BENCHMARK=NO
GROUND_TRUTH_EXPOSED=NO
```

TC-001A completed without the disk-space interruption that affected TC-001 and produced the full staged discovery artifacts. However, Cursor autonomously changed execution topology by decomposing the work into multiple child analysis sessions despite the visible controls intended to limit subagent behavior. This limits claims about deterministic model/orchestration control and reinforces the need for the final Synopsys-owned apples-to-apples benchmark.

## Purpose

Repeat the baseline nondeterminism discovery after resolving the environmental issue encountered in TC-001.

TC-001A is the clean local control to use for the immediate directional comparison with **TC-001B — CoreStory Discovery**. It does **not** replace the need for the final Synopsys-owned apples-to-apples benchmark in their controlled environment.

## Relationship to TC-001

TC-001 is retained as a pilot with limitations. TC-001A started from a fresh Cursor conversation and sufficient disk space while keeping the discovery task and CTS scope unchanged.

No TSan/Coverity ground-truth locations were intentionally exposed to the discovery run.

## Test arm

**Baseline / without CoreStory**

```text
CoreStory MCP=Disabled
CoreStory governing rule=Disabled
Explore Subagent Model=Disabled
Ground truth=Hidden
```

Synopsys skills remained enabled and unmodified.

## Source scope

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

Use the same source state for TC-001B.

## Model controls

The target model was explicitly selected in Cursor rather than intentionally using Auto.

```text
UI_SELECTED_MODEL=Claude Opus 4.8
CURSOR_USAGE_RECORDED_MODEL=TO_BE_CORRELATED
VERIFIED_EXECUTION_MODEL=UNRESOLVED
```

TC-001 previously showed a discrepancy between the selected model and Cursor Usage telemetry. TC-001A also demonstrated that Cursor may create separate analysis sessions as part of its orchestration. Therefore model attribution must be evaluated per parent/child execution where telemetry permits; do not infer that every generated session used the UI-selected model.

## Environment controls used

- Sufficient disk space was available for the complete run and artifacts.
- Fresh Cursor conversation.
- Intended CTS workspace open.
- `/nd-code-analyzer` available.
- CoreStory MCP disabled/unavailable.
- `code-analysis-v2.mdc` disabled/absent.
- Explore Subagent Model disabled in Cursor settings.
- Claude Opus 4.8 explicitly selected in the UI; Auto not intentionally selected.
- Held-out TSan/Coverity ground truth not supplied to the agent.
- Cursor Request Traces configured at `Trace` level.

## Run record

```text
START_TIME_LOCAL=2026-09-09T13:52:23-05:00
END_TIME_LOCAL=2026-09-09T14:07:39-05:00
WALL_CLOCK_RUNTIME=00:15:16
REQUEST_TRACE_LOG_LEVEL=Trace
```

This runtime is suitable for the immediate local directional comparison because no disk-space intervention was required during the run. It is not a production benchmark result.

## Prompt

The exact discovery prompt was:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

Do not change this prompt for TC-001B.

## Observed execution behavior

### Stage 1 fallback remained

`scan_nd.py` was still unavailable in the installed skill tree. Rather than using the simpler manual grep path seen in TC-001, Cursor generated its own PowerShell/ripgrep Stage-1 scanner from the ND pattern catalog and created structured intermediate artifacts.

This behavior must be held constant as an environmental condition for TC-001B; do not modify the installed Synopsys skill package between the two arms.

### Cursor autonomously decomposed the analysis

After the parent discovery session created narrowed pattern packs, Cursor created multiple separate triage sessions with generated prompts covering different ND pattern groups. Examples included:

- patterns 1.1 / 1.9 / 1.11,
- patterns 1.2 / 1.3 / 1.7 / 3.7,
- patterns 1.4 / 1.5 / 1.6 / 1.12 / 3.x / 4.x.

Some child attempts encountered runtime/tool failures and fallback behavior while performing their triage.

This occurred even though Explore Subagent Model was disabled and the user had configured the visible model controls. The preserved JSONL artifacts show distinct generated child-analysis conversations rather than a single uninterrupted parent-only execution.

Impact:

- agent orchestration is an uncontrolled variable in the local Cursor test harness,
- model selection for generated child sessions cannot be assumed from the parent UI selection,
- local token/runtime measurements remain useful directionally but should not be represented as a final controlled model-specific benchmark,
- TC-001B should preserve the same visible Cursor controls and record whatever orchestration Cursor actually performs rather than changing settings again.

## Results

The completed report records:

```text
RAW_STAGE_1_CANDIDATES=4535 hits across 817 files
REAL_HIGH_FINDINGS=1
REAL_MEDIUM_FINDINGS=6
TOTAL_REAL_FINDINGS=7
DISMISSED_BUCKETS=23
PATTERNS_EVALUATED=22 of 27 catalog entries
```

The seven elevated findings were concentrated in pointer-container ordering and equal-key/equal-delay tie-breaking behavior. The HIGH finding was an address-ordered `std::set<ndmTerm*>` path in `ctscto/ctoFlowClone.cc`; six MEDIUM findings involved deterministic tie-breaking in MSCTS/CTO sorting and min/max selection paths.

The report also records that many random, filesystem, parallel-reduction, concurrency-shape, membership-only container, and already-deterministic comparator candidates were dismissed as test-only, latent, neutralized, lookup-only, or otherwise non-real for the analyzed execution paths.

Ground-truth scoring remains deferred.

## Preserved artifacts

The results directory contains the completed analysis and structured intermediate/final artifacts, including:

```text
nd_analysis_cts_20260909.md
nd_cts_candidates.json
nd_cts_narrowed_packs.json
nd_cts_findings.json
multiple JSONL parent/child conversation exports
```

The Stage-1 candidate artifact is approximately 1.39 MB and the narrowed-pack artifact approximately 314 KB, providing useful evidence of the amount of local repository context generated before final triage.

## Metrics still to correlate

Before using token data in the readout, correlate available Cursor Usage telemetry and request traces with the parent and child sessions. Capture where possible:

- parent versus child session count,
- successful versus failed child sessions,
- UI-selected versus telemetry-recorded model,
- local repository/tool calls,
- fresh input tokens,
- cache-read tokens,
- output tokens,
- total tokens,
- retries/failures.

Do not collapse child-session usage into a model-specific claim unless the telemetry supports that attribution.

## Blind-test rule

TSan/Coverity reference findings remain held-out scoring data. They must not be used to choose scope, seed prompts, identify files, steer discovery, or confirm/reject findings during TC-001A or TC-001B.

## Matching CoreStory arm — TC-001B

TC-001B must duplicate this run as closely as possible, changing only:

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
```

Keep the same CTS source state, exact prompt, Cursor settings, UI-selected model, Explore Subagent setting, installed Synopsys skill package, disk/resources, and blind-ground-truth controls.

If Cursor again creates child sessions, preserve and measure them. If CoreStory changes the amount or shape of local search/orchestration, that is an observed result rather than something to manually normalize during the run.

The TC-001A / TC-001B pair is intended to provide directional evidence and operational learning. The final quantitative apples-to-apples validation remains a Synopsys-owned test in their controlled environment.
