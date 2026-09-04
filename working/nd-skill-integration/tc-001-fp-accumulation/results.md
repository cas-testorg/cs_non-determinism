# TC-001 Results — Race-Free Floating-Point Accumulation

## Test status

```text
PASS
```

## Environment

```text
Date/time: 2026-09-04, run began approximately 09:23 CDT
Agent/client: Cursor
Agent/client version: 3.18.25
Model: Not captured in exported artifacts
CoreStory project/workspace: cts-code, project id 10
Repository/revision: CTS local repository; exact revision not captured in exported artifacts
Existing Cursor sessions backed up/preserved: Not evidenced in exported artifacts
TC-001 started in a fresh Cursor chat: Consistent with exported single-prompt transcript; not independently proven by artifact
Prior TC-001 conversation context in new chat: None visible in exported transcript
Customer skill installed/available: YES — read from C:\Users\carys\.cursor\skills\non-determinism\SKILL.md
CoreStory rule installed/active: YES — behavior was consistent with the CoreStory-first rule
CoreStory MCP available: YES
Other relevant rules/skills active: prove-nd-mt attempted to load its base prove-nd dependency; exact base-skill availability was not fully captured
```

## Prompt

The exact TC-001 prompt from `README.md` was used without visible follow-up steering in the exported transcript.

## Agent final response

```text
Verdict: available evidence is insufficient to classify any site as Real for race-free, order-dependent floating-point accumulation under multi-threading.

Live solver/QoR paths such as fmaxcgSolverImpl::calculateTns* and TimingCostFunction::evaluateTnsAndWnsParallel use per-job or per-range partials that are merged in fixed job/thread-index order after the join. For fixed thread count and fixed partitioning, the association order was not shown to vary across equivalent runs, so criterion (2) was not established.

The closest non-elevated surface was the ctoscGlobal harness std::atomic<float> totals, which would fit the Locked-but-order-dependent pattern if concurrently exercised. The agent found that enable_pre_opt_harness defaults false, the members are associated with a purecov deadcode region, and the observed sink is diagnostic printHarnessSummary rather than a default-on production QoR/solver path. Criteria (1) and (3) therefore were not established.

The agent identified the missing evidence required for a Real finding: a proven live concurrent shared float/double accumulation path, a production observable consumer, no complete deterministic canonicalization, and an appropriate runtime confirmation.
```

## Cursor investigation trace

### User prompt sent

```text
Investigate the repository for multi-threaded nondeterminism caused by race-free but order-dependent floating-point accumulation.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start by using CoreStory to identify likely parallel execution paths, shared floating-point accumulators or reductions, and their downstream consumers.

For any candidate, do not classify it as Real until you establish:
1. the code actually executes under multi-threading,
2. accumulation order can vary,
3. the value reaches an observable consumer, and
4. no complete deterministic canonicalization occurs before that consumer.

Return only the strongest supported candidate, or state that the available evidence is insufficient.
```

### CoreStory interactions

Observed CoreStory sequence included:

```text
1. list_projects
2. create_conversation for project id 10
3. semantic_search for parallel floating-point accumulators/reductions
4. semantic_search for race-free order-dependent worker reductions
5. send_message asking for causal context around fmaxcgSolverImpl, TimingCostFunction, TNS/WNS, wirelength/cost sums, MT dispatch, downstream consumers, and post-join canonicalization
6. send_message refining specifically for arrival-order-dependent locked/atomic float accumulation
7. semantic_search for ctoscGlobal atomic float harness accumulators
8. send_message asking CoreStory to establish harness MT reachability and search for other live locked/atomic float accumulators
9. semantic_search for mutex-guarded float wirelength sums
```

CoreStory was used at the beginning of the investigation and repeatedly refined as local source evidence rejected or narrowed candidates.

### Local repository operations

The agent used targeted and broad `Read`, `Glob`, and `Grep` operations after CoreStory identified candidate areas. Local inspection included:

```text
- fmaxTimingCostFunction.h
- fmaxcgSolverImpl.cc
- fmaxBufferCountCostFunction.cc
- ctoscGlobal.h
- ctoscGlobal.cc
- ctomtAreaLevelFlow.cc
- ctomtGlsProblemGenerator.h
- related ctomt flow/dispatch files
```

Searches checked:

```text
- mutex/spin_mutex/lock_guard patterns
- shared sum/wl/tns/cost += operations
- std::atomic<float>/double
- harness option gates and consumers
- parallel_reduce/combinable patterns
- MT dispatch/runTask/thread-pool indicators
```

The agent did perform several repository-wide greps under `c:\Users\carys\cts`. These were used as mechanical validation after CoreStory narrowed the defect mechanism, but they are worth tracking in later tests because one goal is to see whether CoreStory can reduce the breadth of local proof work.

### Unexpected agent/tool behavior

```text
No blocking tool failures were observed.

The agent attempted to locate/load the base prove-nd skill referenced by prove-nd-mt. The exported trace does not establish whether the full base skill was available.

The agent explored multiple plausible candidates before concluding none met the proof threshold. This was expected behavior and did not result in speculative elevation.
```

## Candidate and causal evidence

```text
Candidate: ctoscGlobal harness std::atomic<float> totals (closest non-elevated candidate)
File(s): include/ctoscGlobal.h; ctscto/ctosc/ctoscGlobal.cc; related ctomt flow files
Symbol(s): _total_path_over_margin and related harness totals; harnessCheck/doPreOptoHarness*/printHarnessSummary family
```

### Parallel dispatch / MT reachability

```text
The agent investigated ctomt worker/flow code and MT dispatch indicators and found evidence suggesting harness updates can occur from worker paths. However, it also found the harness is gated by enable_pre_opt_harness, which defaults false, and did not establish that this path is live in default production execution.
```

### Floating-point accumulation/reduction

```text
The harness contains std::atomic<float> totals. The agent correctly recognized that concurrent floating-point atomic accumulation can be race-free while remaining order-dependent because floating-point addition is non-associative.
```

### Why accumulation order can vary

```text
For the harness candidate, concurrent worker arrival order would be sufficient to vary the association order of atomic float accumulation. However, because live MT reachability through the option gate was not established, the candidate was not elevated.

For the live solver/QoR reductions, the agent found per-job/per-range partials merged in fixed job/thread-index order. With fixed N and fixed partitioning, it did not establish run-to-run merge-order variation.
```

### Synchronization / race-vs-ordering determination

```text
The agent distinguished race-freedom from determinism. Atomic or locked accumulation was not treated as a determinism guarantee. The candidate mechanism was explicitly evaluated as Locked-but-order-dependent rather than as a data race.
```

### Downstream consumer / observable impact

```text
For the harness candidate, the observed consumer was diagnostic printHarnessSummary rather than a proven default-on production QoR/solver consumer. Observable production impact was therefore not established.
```

### Canonicalization / neutralizer audit

```text
The agent explicitly investigated post-join canonicalization and stable merge order. The live solver/QoR paths were rejected because their partial results were merged in a fixed order. No incomplete canonicalizer was proven for a live candidate.
```

### Missing evidence identified by agent

```text
A default-on or otherwise proven-live path where concurrent workers perform shared float/double accumulation under mutex/atomic semantics, the result reaches an observable production consumer, and no complete index-ordered recomputation covers all contributors. The agent also recommended runtime confirmation appropriate to the ordering claim.
```

## Skill behavior assessment

```text
MT-specific reasoning applied:                     YES
Data race vs order dependence distinguished:       YES
MT reachability established:                       YES — investigated and used as a rejection criterion
Lock treated correctly:                            YES
Canonicalization investigated:                     YES
Observable sink investigated:                      YES
Missing evidence stated rather than guessed:       YES
```

Notes:

```text
The strongest positive result is restraint: the agent found plausible floating-point ND surfaces but did not force a Real finding when MT reachability, variable merge order, or production observability was not established.

The customer skill's anti-false-positive discipline was preserved, especially the distinction between race-free order dependence and data races, live MT reachability, and canonicalization/neutralization checks.
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES
Queries preserved defect mechanism/objective:      YES
Application relationships used to narrow source:   YES
Targeted source used for validation:                YES
Causal evidence requirement preserved:             YES
Unsupported findings avoided:                      YES
```

Notes:

```text
CoreStory was used to identify candidate regions and application relationships before targeted source inspection. The agent refined CoreStory queries as evidence evolved instead of using CoreStory only once at the beginning.

Local validation still included multiple broad repository-wide greps. This is not a TC-001 failure because the customer skill requires mechanical source validation, but it creates a useful follow-up question: can later tests use CoreStory to reduce the breadth of those proof sweeps while preserving rigor?
```

## Cursor interaction observations

```text
CoreStory interactions: approximately 9 distinct MCP calls visible in the exported trace
Local repository searches/reads: multiple targeted reads plus several broad Grep/Glob operations
Files inspected: at least the fmax, ctoscGlobal, and ctomt files listed above
Broad repo-wide searches: YES
Repeated/redundant searches: Some overlapping searches were used to refine candidate coverage; not clearly wasteful from the artifact alone
Unexpected agent behavior: None blocking; base prove-nd dependency availability remains unclear
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL analysis, request counts, and token-efficiency metrics are out of scope for TC-001.

## Test verdict

```text
PASS
```

### Rationale

```text
TC-001 passed as a workflow-integration test.

The combined Cursor + prove-nd-mt + CoreStory rule workflow used CoreStory early, preserved the customer's MT-specific proof discipline, validated candidate mechanisms with source inspection, investigated synchronization and determinism-restoring behavior, and refused to elevate a plausible candidate without sufficient evidence.

The lack of a Real defect is not a test failure. The test's objective was to evaluate workflow behavior, not to guarantee discovery of a defect. The agent's evidence-based insufficient-evidence verdict is consistent with the test's success criteria.
```

## Follow-up

```text
Recommended next mechanism: Worker-state carryover / work-item boundary reset
Reason: This exercises a different class of race-free MT nondeterminism and a different CoreStory value proposition: tracing worker reuse, entry/exit lifecycle methods, accessor usage, state reset behavior, and downstream consumers across files/components. It also directly tests whether CoreStory can narrow the customer's required entry-side/exit-side boundary census and accessor sweep before local validation.
```
