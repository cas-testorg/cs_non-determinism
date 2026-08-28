# 2. Shared-State Concurrency and Non-Thread-Safe Access

Search for shared mutable state that may be accessed concurrently by multiple threads or tasks without sufficient synchronization.

Include:

- global or static mutable state
- shared containers
- lazy initialization
- shared caches
- concurrent reads and writes
- non-thread-safe functions or APIs called from parallel execution
- object-lifetime interactions involving shared state
- synchronization whose coverage or ordering may be insufficient

## Concrete Exemplar

Use the following source pattern as a **concrete exemplar, not as a known defect**.

**Files:** `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc`, `ctscto/ctoFlowMgr.cc`  
**Symbols:** `ctomtGlsProblemGenerator::findNextProblem`, `ctoFlowMgr::getUpTermsForGrpTermsOfSclk`

The application contains a lazily populated mutable cache. The source explicitly documents that concurrent lazy updates could race or crash, and therefore pre-populates the cache before parallel work:

```cpp
// the cache is based on non-thread-safe dosMap and may cause race condition or crash
// to avoid race condition, pre-cache this upstream for grpTerms
if (isBufferingStage() && useCachedGrpUpTerms) {
  for (const ctoSclkBag* cbag : p->sclkbagsOnTerm()) {
    const ctsSclk& sclk = cbag->getSclk();
    (void)flowMgr->getUpTermsForGrpTermsOfSclk(sclk);
  }
}
```

The corresponding accessor populates shared cache state when an entry is missing:

```cpp
if (_upTermsMapOfGrpTerm.find(sclk) != _upTermsMapOfGrpTerm.end()) {
  return _upTermsMapOfGrpTerm.at(sclk);
}

_upTermsMapOfGrpTerm[sclk] = {};
// ... populate entries ...
return _upTermsMapOfGrpTerm.at(sclk);
```

This example demonstrates a pattern where shared mutable state would be unsafe if lazy population occurred concurrently, but the application contains an explicit pre-cache mechanism intended to prevent that condition.

The important investigation question is not merely whether mutable state is reachable from parallel code.

The question is whether multiple threads or tasks can actually reach conflicting operations on that state without an effective synchronization, ownership, pre-initialization, or lifecycle mechanism.

Use this exemplar to identify semantically equivalent patterns elsewhere in the application.

## Investigation Requirements

For each candidate:

1. Identify the shared object, variable, container, cache, singleton, static state, or external resource.

2. Identify the relevant thread, task, worker, callback, or parallel entry points.

3. Identify the operations performed on the shared state, including:
   - reads
   - writes
   - insertion or removal
   - lazy initialization
   - mutation through a `const` accessor
   - destruction or invalidation
   - calls into potentially non-thread-safe functions or APIs

4. Determine whether those operations can overlap in time.

5. Identify synchronization or lifecycle mechanisms, including:
   - mutexes or locks
   - atomics
   - barriers or joins
   - thread confinement
   - immutable publication
   - pre-population or eager initialization
   - ownership rules
   - task ordering

6. Trace the causal chain where supported:

   **concurrent execution**  
   → **shared state or non-thread-safe operation**  
   → **conflicting access without sufficient protection**  
   → **corrupted, stale, invalid, or schedule-dependent state**  
   → **observable application impact**

7. Distinguish among:
   - shared state that is effectively protected;
   - suspicious concurrency pattern with incomplete evidence of overlap;
   - established conflicting access;
   - established data race or invalid synchronization;
   - schedule-dependent execution with a deterministic final result;
   - plausible nondeterministic manifestation requiring additional evidence;
   - confirmed schedule-dependent application result.

8. For any nondeterminism claim, identify what can vary across equivalent executions and how that variation reaches an observable result.

Do not report a finding solely because:

- code executes in parallel;
- mutable state exists;
- a global, static, cache, or singleton is present;
- a function lacks an obvious local lock;
- an API is generally known to be non-thread-safe without establishing concurrent use;
- different workers access the same object only for independent or read-only operations.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- relevant source location
- shared state or non-thread-safe operation
- thread, task, or worker entry points
- conflicting operations
- evidence that operations can overlap
- synchronization, ownership, pre-initialization, or mitigation mechanism, if present
- relevant application execution path
- downstream application impact
- whether a data race or synchronization defect is established
- whether nondeterministic behavior is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.
