# TC-002 Results — Worker-State Carryover / Boundary Reset

## Test status

```text
PASS
```

## Environment

```text
Date/time: 2026-09-04, completed before 10:49 CDT export
Agent/client: Cursor
Agent/client version: 3.18.25
Model: custom Azure GPT-5.4 configuration used for the test
CoreStory project/workspace: cts-code / project id 10
Repository/revision: CTS working tree used for the controlled test
Existing Cursor sessions backed up/preserved: YES
TC-002 started in a fresh Cursor chat: YES
Prior TC-002 conversation context in new chat: NONE
Customer skill installed/available: YES
CoreStory rule installed/active: YES
CoreStory MCP available: YES
Other relevant rules/skills active: customer prove-nd-mt skill; CoreStory code-analysis rule
```

## Prompt

The exact prompt from `README.md` was used as a single initial prompt without follow-up steering.

## Agent final response

Cursor concluded that the available evidence was insufficient for a Real worker-state carryover finding.

Key conclusions:

- `ctsMtMgr` / `ctsMtThreads` / `ctsMtTask` establish long-lived workers and dynamic work assignment.
- `fmaxcgSolverImpl` per-thread gradient state was investigated as a near-candidate, but `consolidateTimingGradient` zeroes updated `_grads` slots after merge, so that surface was treated as **Neutralized**.
- `ctoscLoadPartition` was rejected because source inspection showed it is stack-local per call rather than a long-lived pooled worker object.
- Other worker/cache/engine leads were not elevated because the full carryover chain was not proven.
- No candidate established all of: worker reuse, variable binding, retained mutable state, missing entry/exit restoration, and observable downstream impact.

## Cursor investigation trace

### User prompt sent

The exact TC-002 prompt from `README.md` was sent once.

### CoreStory interactions

Cursor used CoreStory before broad local exploration. Observed interactions included:

- `list_projects`
- creation of a dedicated CoreStory conversation for worker-state carryover
- targeted `send_message` queries for long-lived workers, worker pools, dynamic assignment, mutable worker state, lifecycle entry/exit methods, accessors, and downstream consumers
- targeted semantic searches for worker reuse, thread-server / maze patterns, per-thread state, and specific near-candidates
- iterative refinement asking CoreStory to distinguish true pooled-worker state from flow-level or job-local state

CoreStory interactions: multiple targeted interactions; exact count not mechanically scored for this workflow test.

### Local repository operations

Cursor then used local `Grep`, `Glob`, and `Read` operations to validate candidate lifecycle and reset behavior. The source validation included:

- `ctsMtMgr` worker/thread management and queueing
- `fmaxcgSolverImpl` per-thread gradient lifecycle and post-merge clearing
- `ctoscLoadPartition` construction/lifetime
- searches for thread-local/per-thread caches, engines, reset/flush/start/end methods, and worker-associated state

A substantial number of broad product-wide lifecycle/reset searches still occurred after CoreStory had produced candidate areas.

### Unexpected agent/tool behavior

No material tooling failure changed the outcome. The main workflow observation is that CoreStory produced useful candidate areas, but Cursor still performed repeated broad repository searches for generic worker-state and lifecycle patterns.

## Candidate and causal evidence

```text
Candidate: strongest near-miss was ctsMtMgr / ctsMtThreads / ctsMtTask worker infrastructure
Worker class/object: long-lived ctsMtMgr-managed workers
File(s): ctsutil/ctsMtMgr.cc and related worker/task definitions; fmaxcgSolverImpl.cc for the strongest mutable-state near-candidate
Symbol(s): queueWork / nqTaskManagerHybrid; threadSpecificQGradMap::_grads; consolidateTimingGradient
```

### Worker creation and reuse

Established for `ctsMtMgr`: workers/threads are created and reused rather than reconstructed per work item.

### Parallel dispatch / variable worker assignment

Established at the worker-pool level through `queueWork` / `nqTaskManagerHybrid`; dynamic binding is plausible and supported by the inspected thread/task infrastructure.

### Mutable per-worker state

The strongest concrete mutable-state near-candidate was `fmaxcgSolverImpl` per-thread gradient storage (`threadSpecificQGradMap::_grads`).

### Accessor / alias sweep

Cursor searched uses of the per-thread gradient maps and related update/clear behavior. Additional broad searches were performed for per-thread holders, thread-local state, engines, caches, and worker-associated objects.

### Entry-side reset / initialization

No Real candidate was established where a stale member survived into a new work item without adequate initialization/restoration.

### Exit-side reset / cleanup

For the strongest concrete near-candidate, `consolidateTimingGradient` zeroes each updated gradient slot after merge.

### Reset / clear / flush semantics

Cursor verified actual behavior rather than trusting lifecycle method names. The `fmaxcgSolverImpl` candidate was therefore classified as neutralized rather than elevated.

### Downstream consumer / observable impact

No candidate established the required stale-state path into an observable application result.

### Missing evidence identified by agent

The agent explicitly stated that it lacked a concrete worker member that is written by work item A, survives the boundary, is consumed by work item B, and can affect an observable result. It recommended runtime instrumentation of `(worker id, work-item id, candidate member)` if the strongest infrastructure path is pursued further.

## Skill behavior assessment

```text
Worker-carryover reasoning applied:                YES
Worker reuse established:                          YES
Variable work-item assignment established:         YES
Entry-side boundary inspected:                     YES
Exit-side boundary inspected:                      YES
Reset semantics verified:                          YES
Accessors/aliases investigated where relevant:     YES
Observable sink investigated:                      YES
Missing evidence stated rather than guessed:       YES
```

Notes:

```text
The skill's core anti-false-positive discipline was preserved. Cursor distinguished pooled-worker infrastructure from job-local or stack-local state and verified a concrete neutralizer before dismissing the strongest mutable-state near-candidate.
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES
Queries preserved carryover mechanism/objective:   YES
Worker lifecycle relationships identified:         YES
Application relationships used to narrow source:   PARTIAL
Targeted source used for validation:                YES
Causal evidence requirement preserved:             YES
Unsupported findings avoided:                      YES
```

Notes:

```text
CoreStory surfaced plausible worker/state areas and helped focus the first source checks. However, it did not narrow the proof space enough to eliminate substantial product-wide grep activity for lifecycle, reset, per-thread, cache, and engine patterns.
```

## CoreStory narrowing assessment

```text
Did CoreStory identify a candidate worker/lifecycle path before broad grep?  YES
Did CoreStory narrow member/accessor/reset validation?                       PARTIAL
Did Cursor still require broad product-wide lifecycle/reset searches?        YES
Did local proof work remain focused on CoreStory-supplied candidates?         PARTIAL
```

Notes:

```text
CoreStory successfully established useful candidate areas, but TC-002 did not yet demonstrate a material reduction in the mechanical sweep burden. Cursor repeatedly broadened back out to repository-wide searches for generic worker-state and lifecycle signatures.
```

## Cursor interaction observations

```text
CoreStory interactions: multiple targeted calls and refinements
Local repository searches/reads: substantial targeted + broad grep/read activity
Files inspected: multiple worker-management, solver, partition, and per-thread-state files
Broad repo-wide searches: YES
Repeated/redundant searches: some repeated searches across lifecycle/per-thread/engine/cache patterns
Unexpected agent behavior: none material; breadth of local mechanical search remains the main observation
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope for TC-002.

## Test verdict

```text
PASS
```

### Rationale

```text
TC-002 passed as a workflow-integration test. Cursor used CoreStory early, applied the customer's worker-carryover proof discipline, distinguished pooled-worker infrastructure from job-local or stack-local state, verified reset/neutralization behavior in source, and declined to manufacture a Real finding when the causal chain was incomplete.

The result also exposes the next workflow question: CoreStory generated useful leads but did not yet materially reduce broad local proof searches. TC-003 should therefore test a mechanism where CoreStory's relationship tracing can be evaluated more directly.
```

## Follow-up

```text
Recommended next change or next mechanism: Commit-order dependence / first-writer-wins
Reason: Test whether CoreStory can identify a complete parallel producer -> competing commit -> shared destination -> downstream consumer path before local source inspection, reducing broad discovery grep and leaving Cursor primarily with targeted proof work.
```
