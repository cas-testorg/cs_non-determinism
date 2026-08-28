# 10. External-Library and Dependency Variability

Search for application behavior that depends on external libraries, solver engines, runtimes, cryptographic implementations, or other third-party dependencies whose algorithms, threading, floating-point behavior, version, platform implementation, or runtime configuration could alter observable results.

Include:

- solver backends
- numerical libraries
- external runtime libraries
- cryptographic APIs
- third-party threading models
- library-provided PRNG or entropy behavior
- version-dependent algorithms
- platform-specific dependency implementations
- external libraries whose results feed application decisions, optimization, QoR, ordering, or persisted output

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**Files:** `ccd/ctsccd/fmax/fmaxWrapper.cc`, `ctssch/ctsSchFinalCts.cc`  
**Symbols:** `fmaxWrapper::runSolver`, `fmaxWrapper::runCcdOpt`

The application delegates clock-tree optimization to an external FMAX solver flow and consumes the resulting QoR back into the application:

```cpp
std::unique_ptr<fmaxFlow> f;
if (ctsscSolverApi::isCusMode()) {
  f = std::make_unique<fmaxCusFlow>();
} else {
  f = std::make_unique<fmaxFlow>();
}

f->run(&global);

global.printQoR("After FMAX optimization:" + ctsscSolverApi::getSolverName(),
                skipPrintPowerForMooDrc);
ctsscQorData qor = ctsscUtil::getQor(global._ctsInfra, global.getTimerInterf());
```

This example establishes a real dependency boundary and shows that solver output reaches meaningful application QoR and flow behavior.

It does **not** establish that different solver versions, platforms, or runtime configurations actually produce different results.

The important investigation question is therefore not merely whether an external dependency exists. It is whether dependency-specific variability is grounded and whether the resulting difference propagates into application behavior.

Use this exemplar to identify semantically equivalent dependency boundaries elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the external library, solver, runtime, API, or dependency boundary.
2. Identify the application call site and the inputs passed across the boundary.
3. Identify outputs, callbacks, shared state, error codes, ordering, numerical results, or side effects returned to the application.
4. Trace how those outputs influence downstream application logic.
5. Identify the proposed source of dependency variability, such as:
   - library version
   - platform implementation
   - internal threading
   - floating-point behavior
   - solver heuristics
   - runtime configuration
   - dependency-specific PRNG or entropy
   - algorithm changes
6. Determine what evidence exists locally for that variability. Do not assume external behavior that the repository does not establish.
7. Identify dependency pinning, engine ordering, checksums, deterministic modes, configuration controls, result normalization, tolerances, or other mitigations.
8. Trace the causal chain where supported:

   **dependency-specific variability**  
   → **different external result or side effect**  
   → **application consumer**  
   → **different downstream state, decision, calculation, or output**  
   → **observable application result**

9. Distinguish carefully among:
   - equivalent-run nondeterminism under identical dependency/environment conditions;
   - version sensitivity;
   - platform sensitivity;
   - dependency-configuration sensitivity;
   - plausible external variability requiring documentation/runtime evidence.

10. Classify each candidate as:
   - confirmed dependency-driven application variability;
   - plausible dependency-driven behavior requiring external evidence;
   - dependency boundary with meaningful application impact but unproven variability;
   - dependency behavior with effective determinism control;
   - insufficient evidence.

Do not report a finding solely because a third-party library, solver, crypto API, or runtime is present.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- external dependency or boundary
- application inputs to the dependency
- dependency outputs/side effects consumed by the application
- proposed source of variability
- local evidence supporting or limiting that claim
- relevant application execution path
- downstream application impact
- version/configuration/determinism mitigation
- classification as equivalent-run ND vs version/platform/configuration sensitivity
- confidence
- missing external documentation, runtime, version, or environment evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.
