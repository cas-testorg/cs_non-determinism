# TC-001B — CoreStory Discovery

## Status

**Completed — strong qualification signal, not valid for clean A/B economics.**

```text
RUN_CLASSIFICATION=COMPLETED_WITH_QUALIFICATION_SIGNAL
VALID_FOR_FINAL_A_B_METRICS=NO
VALID_FOR_DIRECTIONAL_ANALYSIS=YES
GROUND_TRUTH_EXPOSED=NO
```

TC-001B materially changed the defect qualification outcome compared with TC-001A, but the run also reused prior local ND artifacts and Cursor model/orchestration telemetry remained uncontrolled. Treat the result as directional evidence about qualification quality, not as a defensible token/cost benchmark.

## Purpose

Run the same CTS nondeterminism discovery as TC-001A with CoreStory enabled, while holding the local environment, prompt, source scope, Cursor settings, and Synopsys skill installation constant.

TC-001B is the matching local CoreStory arm for the immediate directional comparison with TC-001A. It is **not** the final Synopsys-owned apples-to-apples benchmark.

## Intended experimental change from TC-001A

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
```

Everything else was intended to remain unchanged.

## Test arm

**With CoreStory**

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
CoreStory governing rule file=code-analysis-v2.mdc
Explore Subagent Model=Disabled
Ground truth=Hidden
```

Synopsys skills remained enabled and unmodified.

## Source scope

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

## Model controls

The visible model selection was intended to match TC-001A.

```text
UI_SELECTED_MODEL=Claude Opus 4.8
CURSOR_USAGE_RECORDED_MODEL=auto / composer-2.5-fast events observed
VERIFIED_EXECUTION_MODEL=UNKNOWN
```

Cursor Usage telemetry again did not provide clean attribution to the intended fixed model. Because execution involved `auto` and `composer-2.5-fast` events, model-specific cost attribution is not defensible for this run.

## Run record

```text
START_TIME_LOCAL=Wednesday, September 9, 2026 2:42:49 PM
END_TIME_LOCAL=Wednesday, September 9, 2026 3:01:55 PM
WALL_CLOCK_RUNTIME=00:19:06
REQUEST_TRACE_LOG_LEVEL=Trace
```

The preserved Cursor log artifact is zero bytes, so request-level correlation is incomplete.

## Prompt

The prompt was identical to TC-001A:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

No CoreStory-specific wording, known defects, or TSan/Coverity locations were added to the user prompt.

## Observed execution behavior

The installed `scan_nd.py` / `render_report.py` scripts were still absent. Cursor used ripgrep plus manual narrowing and source triage, then incorporated CoreStory application intelligence.

During execution Cursor explicitly reported that it:

- checked CoreStory plus the repository layout,
- found existing ND scan artifacts from earlier that day,
- reused those artifacts as part of the investigation,
- re-verified previously promoted findings,
- and applied caller/build/observability checks before final classification.

This reuse means TC-001B was **not a clean independent discovery run**. It is better characterized as a CoreStory-assisted discovery plus re-triage/qualification pass.

## Final result

The final CoreStory-assisted report concluded:

```text
HIGH=0
MEDIUM=0
```

No production-reachable equivalent-run HIGH or MEDIUM defects were confirmed after deeper build, caller, and observability checks.

## Comparison with TC-001A

TC-001A produced:

```text
Raw Stage-1 candidates=4535 hits / 817 files
HIGH=1
MEDIUM=6
```

TC-001B reduced the final promoted set to:

```text
HIGH=0
MEDIUM=0
```

The important signal is not that CoreStory "found zero defects." The important signal is that application context changed defect qualification.

### Representative qualification changes

#### `ctoFlowClone.cc` pointer-set finding

TC-001A promoted a HIGH finding involving address-ordered `std::set<ndmTerm*>` iteration in `ctoFlowClone.cc`.

TC-001B determined that:

- `ctoFlowClone.cc` is not included in `ctscto/Master.make`,
- the production path uses `ctoRestruct.cc`,
- the production implementation uses `termSetType`,
- and `termSetType` uses `ndmObjPtrCmpType` for deterministic pointer ordering.

Disposition: **dead / not in production build; production path is a safe adopter.**

#### `fmaxLpSolver` random-device finding

A previously promoted HIGH finding used `std::random_device` in `selectActiveVariableSubset`.

TC-001B found the only call site was commented out and no other live references were present.

Disposition: **dead / unused.**

#### Parallel TNS fold

Previously treated as a possible MEDIUM result-ND issue.

TC-001B classified it as **configuration sensitivity**, with fixed range partitioning and thread-index merge behavior for a fixed thread count.

#### `hardware_concurrency` grain

Previously treated as MEDIUM.

TC-001B found disjoint `grpLat[i]` writes and no demonstrated result nondeterminism.

Disposition: **false positive for result ND.**

## What this run supports

TC-001B provides directional evidence that CoreStory can improve **candidate qualification and false-positive reduction** by adding application-wide evidence such as:

- build inclusion,
- caller/reachability context,
- production-vs-dead implementation distinctions,
- type/container semantics,
- and downstream observability.

This is a stronger result for the quality/precision hypothesis than for token/runtime hypotheses.

## Limitations

### 1. Existing discovery artifacts were reused

Cursor found and reused prior ND artifacts from the same day. Therefore the CoreStory arm was not independent from the prior baseline discovery state.

Impact: do not claim a clean apples-to-apples discovery comparison.

### 2. Model/orchestration telemetry remained uncontrolled

Cursor Usage contains `auto` and `composer-2.5-fast` events despite the intended fixed-model setup.

Impact: do not claim precise model-specific cost or token reduction.

### 3. Skill scripts remained absent

The intended scanner/report scripts were not installed, so Cursor continued using a generated/manual fallback workflow.

Impact: the authoritative customer benchmark must validate the intended skill package first.

### 4. Cursor trace artifact is incomplete

The preserved Cursor log is empty.

Impact: request-level model/tool correlation is incomplete.

## Interpretation

The strongest preliminary result from TC-001A vs TC-001B is **quality/precision**, not economics:

> CoreStory-assisted analysis materially changed which candidate findings survived build, reachability, and observability checks.

The local pair does **not** prove a precise percentage improvement in token consumption, runtime, or cost. Those measurements remain contaminated by Cursor model routing, autonomous orchestration, and workflow variance.

## Required next step

Synopsys should perform the final apples-to-apples test in their controlled environment using:

1. the same CTS source/view for both arms,
2. the same verified Synopsys skill package and dependencies,
3. the same prompt,
4. a verified/pinned model with authoritative telemetry,
5. clean sessions/workspaces with no prior discovery artifacts available,
6. stable CoreStory MCP connectivity,
7. held-out TSan/Coverity reference findings used only after both runs,
8. repeated runs if needed to account for agent nondeterminism,
9. and consistent capture of runtime, token usage, local search/tool calls, CoreStory calls, candidates, verified defects, and false-positive burden.

The customer-owned benchmark remains the authoritative test for H1/H2 token/runtime economics and final H3 recall/precision scoring.
