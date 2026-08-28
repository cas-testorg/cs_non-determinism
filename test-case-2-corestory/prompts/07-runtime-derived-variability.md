# 7. Runtime-Derived Variability

Search for runtime-derived values that may introduce different behavior across equivalent executions.

Include:

- PRNGs with unfixed or runtime-derived seeds
- `std::random_device`
- `rand()` / `srand()` seeded from time or process state
- wall-clock time and timestamps
- timeouts and elapsed-time decisions
- performance counters
- process, thread, object, or address-derived seeds
- environment or runtime state used in decisions
- runtime entropy sources

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**File:** `ccd/ctsccd/fmax/fmaxLpSolver.cc`  
**Symbol:** `fmaxLpSolver::selectActiveVariableSubset`

```cpp
std::random_device rd;
std::mt19937 generator(rd());
std::uniform_int_distribution<> uniform(1, cumulativeOccurences.back());

while (currentCount < requiredCount && (!occurenceVector.empty())) {
  size_t count = size_t(uniform(generator));
  size_t resultIndex = findWithBinarySearch(count, cumulativeOccurences);
  result.insert(occurenceVector[resultIndex].second);
  currentCount += occurenceVector[resultIndex].first;
}
```

This example establishes a runtime entropy source that seeds a PRNG and influences subset selection. The source proves that the seed is not fixed. It does not by itself establish how far a different selected subset propagates into an observable application result.

The important investigation question is not merely whether runtime entropy or time is read. It is whether the runtime-derived value reaches a meaningful decision, calculation, state change, or output.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the runtime-dependent source, such as:
   - PRNG seed
   - `random_device`
   - wall clock
   - timestamp
   - timeout
   - performance counter
   - environment value
   - process/thread/object identity
   - runtime-generated ordering input
2. Identify the immediate consumer of that value.
3. Trace whether the value affects:
   - control flow
   - subset or candidate selection
   - algorithm initialization
   - tie breaking
   - retry/timeout behavior
   - numerical calculation
   - persistent state
   - application output
4. Determine whether a fixed seed, injected clock, configuration value, deterministic replay mechanism, or normalization restores reproducibility.
5. Distinguish production behavior from tests, diagnostics, logging, benchmarking, or dead/unused paths.
6. Trace the causal chain where supported:

   **runtime-derived value**  
   → **consumer**  
   → **decision, selection, or calculation**  
   → **downstream state**  
   → **observable application result**

7. Classify each candidate as:
   - confirmed runtime-derived application nondeterminism;
   - runtime variability with plausible application impact;
   - runtime variability limited to tests/diagnostics/output metadata;
   - runtime source with effective determinism control;
   - insufficient evidence.

Do not report a finding solely because `random_device`, a clock, timestamp, timeout, or PRNG exists. Establish the downstream application effect.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- runtime-dependent source
- seed/time/runtime-state logic
- immediate consumer
- relevant application execution path
- downstream decision/state/output
- fixed-seed, injected-clock, configuration, or other mitigation
- whether the path is production or test/diagnostic only
- whether equivalent-run nondeterminism is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.
