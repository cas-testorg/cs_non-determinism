# P2-Shared-State_Concurrency_Non-Thread-Safe_Access-no-CS
_Exported on 8/31/2026 at 12:48:34 CDT from Cursor (3.17.19)_

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

Perform a new investigation. In this investigation do NOT attempt to invoke any MCP tools such as CoreStory. 

---

**Cursor**

I'll investigate shared-state concurrency from source, starting with the exemplar cache pattern and then searching for equivalent unprotected concurrent access elsewhere. CoreStory is out of scope for this run.

Next I’ll read the exemplar and hunt for the same lazy-cache / parallel-access shape elsewhere in the tree.

Focusing on other lazy mutable caches on `ctoFlowMgr` and whether parallel paths can still populate them.

Checking one more consumer path, then consolidating the elevated findings.

**Verdict:** One elevated incomplete-mitigation pattern on the exemplar’s `_upTermsMapOfGrpTerm` cache; one weaker dosMap lazy-cache claim elsewhere. No established thread leak or unlock-without-ownership. No confirmed schedule-dependent result without further runtime evidence.

---

### Finding 1 — `_upTermsMapOfGrpTerm` lazy cache: pre-cache vs MT consumers (elevated)

**Shared state:** `ctoFlowMgr::_upTermsMapOfGrpTerm` (`mutable std::map<ctsSclk, termToConstTermSetMap>`, values are `dosMap`)  
**Files/symbols:** `ctoFlowMgr::getUpTermsForGrpTermsOfSclk`, `ctomtGlsProblemGenerator::findNextProblem`, `ctomtBuffer::calculateTargetDelayForSingleFanout` / `TargetDlyConfig`, `ctoscLoadPartition::isNearLongest`

**Mechanism (same as exemplar):** miss path inserts into the shared non-thread-safe map:

```5473:5495:ctscto/ctoFlowMgr.cc
ctoFlowMgr::getUpTermsForGrpTermsOfSclk(const ctsSclk& sclk) const
{
  if(_upTermsMapOfGrpTerm.find(sclk)!=_upTermsMapOfGrpTerm.end()){
    return _upTermsMapOfGrpTerm.at(sclk);
  }
  // ...
  _upTermsMapOfGrpTerm[sclk] = {};
  // ... populate ...
  return _upTermsMapOfGrpTerm.at(sclk);
}
```

**Intended mitigation:** serial pre-cache in `findNextProblem` before parallel buffering:

```256:267:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
    //the cache is based on non-thread-safe dosMap and may cause race condition or crash
    //to avoid race condition, pre-cache this upstream for grpTerms
    if(isBufferingStage() && useCachedGrpUpTerms) {
      for(const ctoSclkBag* cbag : p->sclkbagsOnTerm()) {
        const ctsSclk& sclk = cbag->getSclk();
        (void)flowMgr->getUpTermsForGrpTermsOfSclk(sclk);
```

Pre-cache gate: `isBufferingStage() && !solverAugLeafOnly && (gls_clock_group_latency_enhancement_revision()>1 || gls_exclude_near_grplat_longest_sinks_from_partition())`.

**MT entry points / conflicting ops:**
| Consumer | When | Cache flag | Conflict if miss under MT |
|---|---|---|---|
| `ctoscLoadPartition::isNearLongest` | buffering / load split | **hardcodes `true`** (`"should be mt safe now since ... already cached"`) | concurrent insert into `_upTermsMapOfGrpTerm` |
| `TargetDlyConfig` / single-fanout `getGrpLatency` | `runAddDelay` in GLS buffer workers | `gls_generator_runtime_improvement_revision()>1` | same |
| Comment on BufferAddDelay | claims “same conditions” as `findNextProblem` | **does not match** | — |

**Causal chain (when miss can still happen under workers):**  
parallel GLS buffering (`runAddDelay` / load partition) → `getGrpLatency(..., useCached=true)` → `getUpTermsForGrpTermsOfSclk` miss → unprotected map/dosMap insert → race / crash / corrupt group-latency inputs → wrong delay targets / partition decisions.

**Classification:**
- **Effectively protected** when pre-cache runs and covers all sclks later queried (notably LoadPartition + `exclude_near_grplat`, which shares that option with the pre-cache OR).
- **Incomplete mitigation / suspicious concurrency** when consumers enable caching without the pre-cache gate: BufferAddDelay keys off `gls_generator_runtime_improvement_revision` (default `0`, not set by EIM tags), while pre-cache keys off latency-enhancement / exclude-near-grplat. LoadPartition always passes `true` and relies entirely on prior pre-population.
- **Data race:** not established under default/EIM-aligned options; **plausible** under mismatched option settings or uncovered sclk keys.
- **Nondeterminism:** not established; would require a confirmed concurrent miss that changes observable latency/partition outcomes.

**Confidence:** medium (mechanism clear; overlap depends on options/coverage).  
**Missing evidence:** TSan under `generator_runtime_improvement_revision>1` with `latency_enhancement_revision<=1` and `exclude_near_grplat=false`; confirm all sclks used in MT `getGrpLatency` are in `sclkbagsOnTerm()` pre-cache set.

---

### Finding 2 — `_termValidSclkCache`: dosMap lazy cache labeled “thread-safe” (weaker)

**Shared state:** `ctsInfra::_termValidSclkCache` (`dosMap<const ndmTerm*, sclkValSetType>`)  
**Symbols:** `ctsInfra::isTermValidForSclk`, `ctsInfra::getTermValidSclks`

Comment claims thread-safety; type is the same non-thread-safe `dosMap` called out in the exemplar. Lazy find-then-assign on miss.

**Classification:** suspicious pattern; **concurrent miss under MT not established** (callers seen in generator/seed paths are largely serial). Not elevated to data race.

**Confidence:** low–medium for defect; high that the comment contradicts the dosMap hazard.

---

### Patterns inspected and not elevated

| Pattern | Why not a finding |
|---|---|
| `sharedSccCtx` + `populateSharedSccCache` MT | TBB concurrent maps; docs require disjoint bag keys |
| `setMarginForTerms` | bags created serially, then `parallel_for_each` only fills per-term margins |
| `populateMtJob::updateCache` | explicitly post-MT, single-threaded merge |
| `dlyFlow::preRunBatches` / estimate-time `getOrCreateBlockageMap` | main-thread pre-init before workers |
| `soCgSolver::updateSlacksForAllScenarios` | map slots pre-created before MT jobs |
| Nested `ccdUtil::parallel_for` | lazyTNS uses inner `tbb::parallel_for` after outer suspend (matches documented rule) |
| Mutex unlock sites (`ctoGrpLatCalc`, `msSecondaryCost`, `fbRouteStatusTable`) | acquisition/unlock pairs observed; no unlock-without-ownership |
| Raw thread leak | no orphaned `std::thread` create/detach/join gaps found; work is TBB/`ctsMtTaskRunner` |

---

### Bottom line

The application repeatedly uses **eager/serial pre-population** to keep non-thread-safe caches off the MT miss path (exemplar, margins, blockage map, slack maps). The strongest remaining concern is that **`_upTermsMapOfGrpTerm`’s safety still depends on option/gate alignment**, and at least one MT consumer (`LoadPartition`) and one delayed-path consumer (`BufferAddDelay`) do not share the same gate as the pre-cache. Align those conditions (or make the cache concurrent / lock-protected) and validate with TSan under the mismatched option matrix above.

