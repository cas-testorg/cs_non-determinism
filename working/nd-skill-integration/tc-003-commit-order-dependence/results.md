# TC-003 Results — Commit-Order Dependence / First-Writer-Wins

## Test status

```text
PASS
```

## Environment

```text
Date/time: 2026-09-04, approximately 11:09–11:28 CDT
Agent/client: Cursor Agent
Agent/client version: 3.18.25
Model: not captured in exported artifact
CoreStory project/workspace: cts-code, project id 10
Repository/revision: CTS local working tree; exact revision not captured in exported artifact
Existing Cursor sessions backed up/preserved: YES, per test setup
TC-003 started in a fresh Cursor chat: YES
Prior TC-003 conversation context in new chat: NO
Customer skill installed/available: YES
CoreStory rule installed/active: YES
CoreStory MCP available: YES
Other relevant rules/skills active: base prove-nd was searched for but not confirmed from the artifact
```

## Prompt

The exact prompt from `README.md` was used as a single initial prompt without follow-up steering.

## Agent final response

```text
Verdict: available evidence is insufficient for a Real multi-threaded commit-order / first-writer-wins finding.

Strongest CoreStory path examined: ctomtGlsParallelBufPlans / driverInfo::_winner.
Local validation showed that the path is neutralized / not actually a concurrent first-writer commit surface:
- parallel producers exist,
- _winner is written in a post-join serial aggregation path,
- deterministic selectBestPerDriver arbitration occurs first,
- _winner is a stats sink rather than the commit authority,
- evalProblems order appears to come from fixed construction order rather than completion order.

Other CoreStory-directed probes did not establish a live concurrent shared-winner path that survives deterministic arbitration into an observable result.
```

## Cursor investigation trace

### User prompt sent

The exact committed TC-003 prompt was sent without additional user steering.

### CoreStory interactions

Cursor used CoreStory before local discovery and kept most subsequent exploration inside CoreStory until concrete paths were available for validation. Observed interactions included:

```text
1. list_projects
2. create_conversation — MT commit-order first-writer-wins ND
3. semantic_search — first-writer/first-finder shared winner patterns
4. semantic_search — parallel commit-order dependence paths
5. send_message — strongest complete causal path request
6. semantic_search — if (!found) / best / first-writer patterns
7. send_message — refine ctomtGlsParallelBufPlans / _winner path
8. filter_chunks — ctomtGlsParallelBufPlans
9. send_message — search for stronger concurrent first-writer candidate
10. send_message — probe search-driver / LP / transform candidates
11. semantic_search — mutex first-found patterns
12. send_message — final budget / early-exit / concurrent append-order pass
```

### First CoreStory-supplied candidate path

```text
Parallel dispatch / producer set:
_xformSuite->runAccurate(evalProblems) in the GLS parallel evaluation flow.

Competing producer(s):
Expanded per-plan evaluation problems for the same driver.

Shared destination / commit / selection site:
ctomtGlsParallelBufPlans::driverInfo::_winner / aggregateDriverInfo, with selectBestPerDriver in the surrounding selection path.

Downstream consumer:
GLS per-driver selection / consolidation and related stats/disposal handling.

CoreStory evidence for relationship:
CoreStory connected the parallel evaluation path to _winner and then identified selectBestPerDriver as a possible deterministic neutralizer that required local verification.
```

### Local repository validation

Local work was primarily tied to the CoreStory-supplied candidate path and related named sites. Observed operations included:

```text
- Glob/read ctomtGlsParallelBufPlans.*
- Read ctomtGlsParallelBufPlans.cc
- Grep aggregateDriverInfo / selectBestPerDriver / _winner / consolidateGlsPerDriver / expandGlsBuffering
- Read ctomtGlsLevelFlow.cc around the parallel evaluation path
- Read ctomtGlsResultIntegrator.cc around downstream handling
- Read ctomtGlsParallelBufPlans.h
- Read fmaxTimingCostFunction.h for one final narrow comparison
```

### Broad local discovery searches

```text
Were broad product-wide searches used: NO
If YES, when relative to CoreStory candidate selection: N/A
Why the agent broadened: N/A
Patterns/areas searched: CoreStory-named sites only
```

### Unexpected agent/tool behavior

```text
No material tool failure or bypass was observed.
The agent searched for the base prove-nd skill but the artifact does not establish that it was separately available.
```

## Candidate and causal evidence

```text
Candidate: ctomtGlsParallelBufPlans / driverInfo::_winner
File(s): ctomtGlsParallelBufPlans.cc/.h, ctomtGlsLevelFlow.cc, ctomtGlsResultIntegrator.cc
Symbol(s): driverInfo::_winner, aggregateDriverInfo, selectBestPerDriver, expandGlsBufferingProblems, disposeEvalProblems
```

### Parallel dispatch / concurrent producers

Phase 2 evaluates expanded plan problems through `_xformSuite->runAccurate(evalProblems)`, establishing a real parallel producer set.

### Competing valid results

Per-plan problems can produce different valid candidate solutions for the same driver. That made the surface plausible enough to warrant proving the selection mechanism.

### Shared destination / commit / selection point

`driverInfo::_winner` initially appeared to represent the winner selection point, but source validation showed that `aggregateDriverInfo` updates it after the parallel work rather than workers concurrently committing to it.

### Why completion / commit order can vary

The test sought evidence that worker completion or commit order could affect winner selection. No such evidence was established for this candidate because the shared winner update is post-join and `evalProblems` appears to retain deterministic construction order.

### Race vs race-free ordering determination

The candidate was rejected as a concurrent first-writer ordering surface. Workers do not race or arrive serially at `_winner`; the relevant aggregation is post-join.

### Downstream consumer / observable impact

The candidate path reaches GLS selection/consolidation handling, but `_winner` itself was shown to be a stats-oriented sink rather than the authoritative commit decision.

### Arbitration / tie-break / canonicalization audit

`selectBestPerDriver` runs before consolidation and selects via `costVector::compare`; losing candidates are cleared with `setFoundSolution(false)`. This constitutes a deterministic arbitration step that neutralizes the suspected commit-order mechanism.

### Missing evidence identified by agent

```text
A live path where concurrent workers update the same shared winner/found field, or append in completion order, where the ordering can vary across equivalent runs and the chosen value reaches design/QoR output without complete deterministic re-selection.
```

## Skill behavior assessment

```text
Commit-order reasoning applied:                    YES
Actual concurrent producers established:           YES
Competing valid outcomes established:              YES
Variable completion/commit order established:      PARTIAL
Race vs ordering distinguished:                    YES
Shared destination/selection identified:           YES
Observable sink investigated:                      YES
Arbitration/canonicalization investigated:         YES
Missing evidence stated rather than guessed:       YES
```

Notes:

```text
The agent applied the intended proof discipline and did not treat the mere existence of parallel producers plus a winner-like field as a Real finding. It explicitly tested whether workers actually committed concurrently and whether deterministic selection neutralized the candidate.
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES
Queries preserved commit-order objective:          YES
Cross-file relationship path identified:           YES
Targeted source used for validation:                YES
Causal evidence requirement preserved:             YES
Unsupported findings avoided:                      YES
```

Notes:

```text
CoreStory supplied a concrete application-level relationship path early enough that local source work could focus on proving or dismissing that path instead of discovering the mechanism from scratch.
```

## CoreStory narrowing assessment

```text
Complete candidate relationship path before broad grep:        YES
Dispatch/producers identified by CoreStory:                     YES
Commit/selection site identified by CoreStory:                  YES
Downstream consumer identified by CoreStory:                    YES
Broad repository discovery before path validation:              NO
Broad grep used only after CoreStory evidence was insufficient: N/A
```

Notes:

```text
This was the clearest narrowing result in the sequence so far. Local work was primarily validation, not product-wide discovery. After the first candidate was neutralized, Cursor continued to ask CoreStory targeted follow-ups for stronger first-writer, first-finder, budget, early-exit, and concurrent-append paths rather than switching to broad repository-wide grep.
```

## Cursor interaction observations

```text
CoreStory interactions: approximately 12 application-intelligence/tool interactions
Local repository searches/reads: targeted validation only
Files inspected: primarily GLS candidate-path files plus one narrow follow-up
Broad repo-wide searches: 0 observed
Repeated/redundant searches: low; refinements were mechanism-specific
Unexpected agent behavior: none material
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope.

## Test verdict

```text
PASS
```

### Rationale

```text
TC-003 validated both the customer's commit-order proof discipline and the intended CoreStory-first workflow. Cursor obtained a concrete parallel-producer -> selection-site -> downstream-consumer path from CoreStory, used targeted source inspection to disprove the candidate through post-join aggregation and deterministic arbitration, and avoided broad product-wide discovery searching. It correctly returned insufficient evidence rather than elevating a plausible but neutralized surface.

The most important outcome is narrowing: compared with TC-001 and especially TC-002, CoreStory provided enough relationship context that local work was predominantly verification rather than discovery.
```

## Follow-up

```text
Recommended next change or next mechanism: Gate-inactive / determinism-control propagation
Reason: Test whether CoreStory can trace a determinism or threading control from option/configuration definition through propagation and call sites to the actual parallel execution path, then let local source inspection verify whether the gate is live, bypassed, compiled out, default-disabled, or otherwise ineffective.
```
