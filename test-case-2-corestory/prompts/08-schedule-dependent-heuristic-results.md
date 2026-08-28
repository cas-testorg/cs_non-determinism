# 8. Schedule-Dependent and Heuristic Result Selection

Search for parallel, opportunistic, heuristic, or early-exit algorithms where thread scheduling, completion order, traversal order, or first-winner behavior may influence which result is selected or which work is performed.

Include:

- first-result-wins or first-completed-wins logic
- atomic first-claim patterns
- schedule-dependent early termination
- parallel search
- opportunistic branching
- heuristic candidate selection
- tie breaking
- parallel reductions with non-commutative state
- worker-local results merged in variable order
- algorithms whose stopping condition depends on partial progress

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h`  
**Symbol:** `ctomtGlsProblemGenerator::runSccIteration`

The implementation uses parallel SCC evaluation with an atomic early-exit flag:

```cpp
std::atomic<bool> globalDone{false};

return tbb::parallel_reduce(
    tbb::blocked_range<size_t>(0, n),
    init,
    [&](const tbb::blocked_range<size_t>& r, stateType localS)->stateType {
      for (size_t i = r.begin(); i != r.end(); ++i) {
        if (globalDone.load(std::memory_order_relaxed)) {
          break;
        }
        body(i, localS);
        if (localS.done(init)) {
          globalDone.store(true, std::memory_order_relaxed);
          break;
        }
      }
      return localS;
    },
    [&](const stateType& a, const stateType& b)->stateType {
      stateType merged = reduce(a, b);
      if (merged.done(init)) {
        globalDone.store(true, std::memory_order_relaxed);
      }
      return merged;
    });
```

This example makes schedule-dependent execution possible: worker scheduling can affect which SCCs are evaluated before `globalDone` is set and can affect diagnostic merge order. However, when the final reduction is a commutative boolean OR/AND, the application-level boolean result may remain deterministic.

The important investigation question is therefore not merely whether work completion order varies. It is whether that variation changes a committed application result rather than only work performed, runtime, or diagnostics.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the parallel, heuristic, opportunistic, or early-exit algorithm.
2. Identify what scheduling, completion, traversal, or tie-breaking order can vary.
3. Identify the state or result selected, merged, committed, or discarded.
4. Determine whether the final operation is order-independent or order-sensitive.
5. Identify determinism-restoring mechanisms such as:
   - commutative/associative reduction
   - stable post-sort
   - deterministic tie breaker
   - fixed worker-index merge
   - complete join before selection
   - invariant final state despite variable work
6. Separate effects on:
   - application result
   - internal work performed
   - diagnostics/log ordering
   - performance/runtime
7. Trace the causal chain where supported:

   **schedule/completion/traversal variation**  
   → **different candidate, merge, early-exit, or winner**  
   → **different committed downstream state**  
   → **observable application result**

8. Classify each candidate as:
   - confirmed schedule-dependent application result;
   - plausible schedule-dependent result requiring additional evidence;
   - schedule-dependent execution with deterministic final result;
   - diagnostic/performance-only variation;
   - insufficient evidence.

Do not report a finding solely because parallel execution, atomics, early exit, or heuristics are present.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- parallel/heuristic entry point
- variable schedule/completion/traversal mechanism
- selected or merged state
- determinism-restoring mechanism, if present
- relevant application execution path
- downstream committed result
- whether only work/log/performance varies
- whether equivalent-run application nondeterminism is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.
