# TC-005 Results — Concurrent Container Insertion / Iteration-Order Dependence

## Test status

```text
PASS
```

## Environment

```text
Date/time: 2026-09-04, run started about 14:08 CDT; exported 14:27:51 CDT
Agent/client: Cursor
Agent/client version: 3.18.25
Model: controlled Cursor test model; exact model not captured in exported artifact
CoreStory project/workspace: project_id 10
Repository/revision: CTS repository in the configured Cursor workspace; exact source revision not captured in exported artifact
Existing Cursor sessions backed up/preserved: YES — prior chat data was purged/restarted between tests
TC-005 started in a fresh Cursor chat: YES
Prior TC-005 conversation context in new chat: NO
Customer skill installed/available: YES — prove-nd-mt
CoreStory rule installed/active: YES
CoreStory MCP available: YES
Other relevant rules/skills active: prove-nd base skill availability remained uncertain; agent attempted discovery
```

## Prompt

The exact committed TC-005 prompt was used as the single initial prompt without follow-up steering.

## Agent final response

The agent concluded:

> Evidence is insufficient to classify any concurrent container-insertion / iteration-order path as Real.

The strongest paths examined all failed an order-sensitivity requirement or were deterministically neutralized before an observable consumer.

Closest near-misses:

- `fmaxLpSolver::mergeViolatedPathsOfSolutionsParallel` / `removeRedundantPathsParallel`: parallel production exists, but `std::sort` + `std::unique` with `ConstraintComparatorNew` canonicalizes the path collection before pruning; the downstream use is membership/slack based.
- `ctsInterClockBalance` `arrivals1`: concurrent insertion into `tbb::concurrent_vector<float>` exists, but values are converted to `std::set<float>` before the median calculation, removing arrival order.
- `soSolverUpdater` `clustersToTrace`: concurrent-vector insertion exists, but values are immediately transferred into `std::set<unsigned int> clustersNotTraced`.
- `ctsPathTracerInterf::findPathsMt`: MT jobs exist, but aggregation occurs by job index rather than completion order.

Missing for a Real claim was a full chain in which concurrent workers produce a variable insertion/merge order, the relevant container preserves that order, an order-sensitive consumer observes it, and no deterministic sort/set conversion/stable merge/canonicalization removes it.

## Cursor investigation trace

### User prompt sent

The exact TC-005 prompt from `README.md` was sent unchanged.

### CoreStory interactions

The agent used CoreStory before local repository exploration and opened conversation 81, `MT concurrent container insertion order ND`.

CoreStory work included:

- asking for a complete parallel producer -> shared/merged container -> order-sensitive consumer path,
- semantic search for concurrent insert/append order paths,
- refinement of `fmaxLpSolverIncremental` and `ctsPathTracer` candidates,
- asking for alternate locked-but-order-dependent shared-container candidates after initial candidates appeared neutralized,
- targeted investigation of `soSolverUpdater`, `fmaxTimingCostFunction`, GLS parallel buffer-plan paths, split-tree/merge paths, and concurrent-vector consumers,
- a final targeted pass asking specifically for shared insertion order that survives to an observable consumer.

CoreStory repeatedly distinguished concrete candidates from incomplete application-level paths and did not force a Real finding when the downstream order-sensitive relationship could not be established.

### First CoreStory-supplied candidate path

```text
Parallel dispatch / producer set: fmaxLpSolverIncremental parallel violated-path processing
Shared / merged container: violated-path vectors / fragmented containers
Insertion / arrival / merge order source: parallel per-worker/path contributions
Downstream consumer: redundant-path pruning / LP-related path handling
Canonicalizer / sort / reselection if any: std::sort + std::unique using ConstraintComparatorNew
```

The first candidate therefore looked structurally plausible but was neutralized before order could affect the downstream consumer.

### Local repository validation

Local validation remained tied primarily to CoreStory-generated candidates. The agent inspected or searched targeted portions of:

- `fmaxLpSolverIncremental.cc`
- `fmaxTimingCostFunction.h`
- `ctomtGlsParallelBufPlans.*`
- `ctsInterClockBalance`
- `soSolverUpdater`
- `ctsPathTracer`

The source checks validated sort/unique behavior, set conversion, job-index aggregation, and the absence of a preserved completion-order path into an order-sensitive consumer.

### Broad local discovery searches

```text
Were broad product-wide searches used: YES
If YES, when relative to CoreStory candidate selection: Late, after multiple CoreStory candidate/refinement passes failed to establish a Real path
Why the agent broadened: To spot-check whether an obvious concurrent-container surface had been missed after CoreStory could not close a complete causal chain
Patterns/areas searched: tbb::concurrent_vector / concurrent_vector and related concurrent container patterns
```

This was narrower and later than the broad mechanical searches observed in TC-001/TC-002, but it is a small regression from TC-003/TC-004 where local work stayed almost entirely within CoreStory-supplied paths.

### Unexpected agent/tool behavior

```text
No blocking MCP/tool failures were observed in the captured run.
The agent attempted to locate the base prove-nd skill, as in prior tests; its availability remained unclear.
```

## Candidate and causal evidence

```text
Candidate: fmaxLpSolver parallel violated-path collection / merge
File(s): fmaxLpSolverIncremental.cc and related fmax path-processing code
Symbol(s): mergeViolatedPathsOfSolutionsParallel, removeRedundantPathsParallel, ConstraintComparatorNew
Container type: per-worker/per-endpoint vectors merged for downstream pruning
```

### Parallel dispatch / concurrent producers

Parallel production was established for multiple examined paths, including TBB-backed path processing and concurrent-vector insertion sites.

### Shared / merged container

CoreStory identified shared or merged vectors/concurrent vectors for several candidates and the agent validated their concrete use locally.

### Why insertion / arrival / merge order can vary

For the concurrent-vector candidates, worker arrival/insertion order can be schedule dependent. For other candidates, the agent explicitly checked whether merges were completion ordered versus stable job/thread indexed.

### Container ordering semantics

The critical distinction was preserved: merely using `tbb::concurrent_vector` or performing parallel `push_back` was not treated as sufficient evidence. The agent traced what happened to the resulting ordering before consumption.

### Downstream order-sensitive consumer

No complete order-sensitive consumer was proven for the strongest candidates. Consumers were either membership/slack based, fed from a set, or received results merged by stable job index.

### Observable impact

Potential observable design/solver impact was investigated, but no causal path from variable container order to a differing application result survived the neutralizer audit.

### Sort / canonicalization / reselection audit

Neutralizers were specifically established:

- `std::sort` + `std::unique` for violated-path vectors,
- `std::set<float>` conversion for inter-clock arrivals,
- `std::set<unsigned int>` conversion for skew-opt cluster IDs,
- stable job-index aggregation in `findPathsMt`.

### Missing evidence identified by agent

A Real claim still requires all of:

1. actual concurrent producers,
2. variable insertion/merge order across equivalent runs,
3. preservation of that order,
4. an order-sensitive downstream consumer, and
5. no deterministic sort, stable-key merge, set conversion, canonicalization, or post-join recomputation before the observable result.

The run did not establish such an end-to-end path.

## Skill behavior assessment

```text
Container-order reasoning applied:                 YES
Actual concurrent producers established:           YES
Variable insertion/merge order established:        YES — for examined concurrent insertion surfaces; not for all candidates
Container ordering semantics verified:             YES
Order-sensitive consumer established:              PARTIAL — investigated, but no candidate satisfied it end to end
Observable sink investigated:                      YES
Canonicalization/reselection investigated:         YES
Missing evidence stated rather than guessed:       YES
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES
Queries preserved container-order objective:       YES
Producer/container/consumer path identified:       PARTIAL — concrete producer/container paths were identified; complete order-sensitive consumer chain was not
Targeted source used for validation:                YES
Causal evidence requirement preserved:             YES
Unsupported findings avoided:                      YES
```

## CoreStory narrowing assessment

```text
Candidate relationship path before broad grep:     YES
Parallel producer set identified:                  YES
Shared/merged container identified:                YES
Downstream consumer identified:                    PARTIAL
Canonicalizer/sort identified where relevant:      YES
Local proof remained targeted:                     YES
Broad product-wide container search required:      YES
```

Notes:

```text
CoreStory reduced the investigation to several concrete producer/container/consumer candidates and supplied enough context for targeted neutralizer checks. After repeated CoreStory refinement could not establish a complete Real path, Cursor performed one broader repository search for concurrent-vector patterns. That broadening occurred late and explicitly as a fallback, not as the initial discovery strategy.
```

## Cursor interaction observations

```text
CoreStory interactions: multiple conversation refinements plus semantic searches and an index filter
Local repository searches/reads: primarily candidate-focused; one late broad concurrent-container grep
Files inspected: fmax, path-tracing, inter-clock, skew-opt, and GLS candidate files
Broad repo-wide searches: YES — one late search for tbb::concurrent_vector / concurrent_vector patterns
Repeated/redundant searches: limited; most CoreStory follow-ups progressively refined the mechanism
Unexpected agent behavior: none materially affecting the test
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope.

## Test verdict

```text
PASS
```

### Rationale

```text
TC-005 passes as a workflow-integration test. The agent followed the prove-nd-mt container-order proof discipline, used CoreStory first, generated and refined concrete candidate paths, validated them in targeted source, audited sort/set/stable-merge neutralizers, and correctly declined to elevate a Real finding without an order-sensitive observable consumer.

The main caveat is that Cursor eventually performed a broader repository search for concurrent-vector patterns after CoreStory could not close a complete causal path. This is a small narrowing regression compared with TC-003/TC-004, but it occurred only after substantial CoreStory-guided investigation and did not replace the CoreStory-first workflow.
```

## Follow-up

```text
Recommended next change or next mechanism: Pause automatic expansion of the test suite and solicit internal feedback before defining TC-006.
Reason: Five controlled tests now show a consistent workflow pattern across distinct MT nondeterminism mechanisms. Additional mechanism tests are likely to have diminishing value unless the internal/customer team identifies a specific remaining risk or proof pattern they want exercised before the Tuesday meeting.
```
