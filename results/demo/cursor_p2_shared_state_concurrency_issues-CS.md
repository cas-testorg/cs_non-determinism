# Shared-state concurrency issues
_Exported on 8/31/2026 at 13:06:07 CDT from Cursor (3.17.19)_

---

**User**

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
- thread or task creation without a proven join, detach, shutdown, or lifecycle-completion path
- mutex unlock operations without a proven corresponding acquisition and ownership path

## Relevant Defect Patterns

This investigation includes source patterns associated with:

- ThreadSanitizer `DATA RACE`
- ThreadSanitizer `THREAD LEAK`
- ThreadSanitizer `UNLOCK OF AN UNLOCKED MUTEX`

Treat these names as investigation patterns, not as evidence that a corresponding ThreadSanitizer defect exists. Establish the source mechanism and application impact independently.

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

1. Identify the shared object, variable, container, cache, singleton, static state, external resource, thread/task object, or synchronization primitive.

2. Identify the relevant thread, task, worker, callback, or parallel entry points.

3. Identify the operations performed on the shared state or synchronization/lifecycle object, including:
   - reads
   - writes
   - insertion or removal
   - lazy initialization
   - mutation through a `const` accessor
   - destruction or invalidation
   - calls into potentially non-thread-safe functions or APIs
   - thread/task creation, join, detach, cancellation, shutdown, or destruction
   - lock acquisition, ownership transfer, unlock, and error paths

4. Determine whether conflicting operations can overlap in time, whether a created thread/task can outlive its intended lifecycle, or whether an unlock can occur without ownership.

5. Identify synchronization or lifecycle mechanisms, including:
   - mutexes or locks
   - atomics
   - barriers or joins
   - detach or explicit shutdown semantics
   - thread confinement
   - immutable publication
   - pre-population or eager initialization
   - ownership rules
   - RAII lock ownership
   - task ordering

6. Trace the causal chain where supported:

   **concurrent execution or lifecycle/synchronization event**  
   → **shared state, thread/task, or mutex operation**  
   → **conflicting access, incomplete lifecycle, or invalid synchronization**  
   → **corrupted, stale, leaked, invalid, or schedule-dependent state**  
   → **observable application impact**

7. Distinguish among:
   - shared state that is effectively protected;
   - suspicious concurrency pattern with incomplete evidence of overlap;
   - established conflicting access;
   - established data race;
   - thread/task lifecycle that is correctly joined, detached, or shut down;
   - established thread leak or incomplete thread lifecycle;
   - mutex ownership that is correctly paired;
   - established unlock-without-ownership or invalid synchronization;
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
- a thread or task is created without tracing its full lifecycle;
- an unlock call exists without tracing the matching acquisition/ownership path;
- different workers access the same object only for independent or read-only operations.

## Evidence Requirements

For each elevated candidate provide:

- file and symbol
- relevant source location
- shared state, thread/task lifecycle, or synchronization operation
- thread, task, or worker entry points
- conflicting operations or lifecycle/synchronization sequence
- evidence that operations can overlap, a thread can leak, or mutex ownership is invalid
- synchronization, ownership, pre-initialization, join/detach/shutdown, RAII, or other mitigation mechanism, if present
- relevant application execution path
- downstream application impact
- whether a data race, thread leak, or synchronization defect is established
- whether nondeterministic behavior is established
- confidence
- missing evidence required for confirmation

Prefer a smaller number of well-supported findings over a larger number of speculative candidates.

For this test, do not use previously generated nondeterminism analysis documents, prior analysis artifacts, or prior investigation results.

Perform a new investigation using current CoreStory application intelligence and targeted source inspection.

---

**Cursor**

I'll investigate shared-state concurrency using CoreStory application intelligence first, then validate candidate mechanisms in source—starting from the exemplar pattern and looking for equivalent cases elsewhere.

Using the latest `cts-code` project, I'll open a CoreStory conversation and run targeted searches for the exemplar pattern and equivalent shared-state risks.

Digging into the strongest candidates with follow-up CoreStory queries and local source validation.

Inspecting the strongest source candidates—static `_onClockCache`, explicit "not thread safe" sites, and parallel call paths.

Confirming `_onClockCache` uses a concurrent map with serial merge — looking next at mutex unlock paths and other NOT-thread-safe APIs that may lack that protection.

Verifying `populateMtJob` call discipline and checking MT paths around `MinMaxEqLibCellAreaCache` and predictive CCD.

Preparing a canvas summarizing the investigation: no established unmitigated race, with protected patterns and incomplete-evidence candidates.

**No established unmitigated shared-state race** was proven. The strongest exemplar-equivalent sites use pre-cache, concurrent containers, thread-local staging, or serial merge after join.

Structured results: [shared-state-concurrency](C:\Users\carys\.cursor\projects\c-Users-carys-cts\canvases\shared-state-concurrency.canvas.tsx) (open beside chat for the full table).

### Protected patterns (same class as the exemplar)
| Pattern | Mitigation |
|---|---|
| `getUpTermsForGrpTermsOfSclk` / `_upTermsMapOfGrpTerm` | Pre-cache in `findNextProblem` before MT buffering |
| `_onClockCache` + `groupSlackCache` in `getClockArrivalKeys` | `tbb::concurrent_unordered_map`; serial `updateCache()` after `parallel_for` |
| `populateMtJob` → `QsmcCache` | Serial `updateCache()` between batches; explicit “not thread-safe / don’t call in MT” |
| `ctsSkewSlackCollector::collectClockArrival` → `caMap` | Serial `insert` after `runTask` |
| predictive CCD `_tmpMt` | `precomputeInfoForMulti` + MT-safe APIs; annotate/restore serial |
| `soLogicCone` lookup caches | `tbb::enumerable_thread_specific` |

### Not elevated (incomplete overlap)
- `_collectSclkCache`, `ctoscTimerCache` / filter `_timerCache` — non-thread-safe caches, shared concurrent use not shown  
- `soMonitor` static maps — MT-forbidden by comment; call sites sit outside `parallel_for`  
- Nested `ccdUtil::parallel_for` — documented lock race hazard; no nested call found  
- Thread leak / unlock-without-ownership — not established (`ctoGrpLatCalc` locks are paired)

### Nondeterminism
Not established: nothing showed schedule-dependent variation reaching an observable result under equivalent runs.

**Next validation:** TSan on lazyTns clock-arrival/populate and GLS buffering with `useCachedGrpUpTerms` off; watch for nested `ccdUtil::parallel_for`.

