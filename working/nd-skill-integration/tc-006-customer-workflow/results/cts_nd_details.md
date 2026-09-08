# CTS Non-Determinism Details (MT prove-nd)

Source dashboard: `nd_mt_candidates_discovery.md` (candidates C1-C10)

Analysis context:

- `viewtool info`: unavailable in this workspace (command not on PATH).
- `.synmake` / `DEVROOTS`: absent; source root used is local workspace `c:\Users\carys\cts`.
- Tools used: CoreStory project `cts-code` (id 10), conversation 83; direct source reads; ripgrep caller sweeps.
- Scope notes: `dosMap.h` is outside this tree (include only); `elrfFloatValues::merge` body not in-tree. Pure `getenv` ND ignored. Secondary seeds S1-S5 recorded only, not fully proved.

## Summary Table

| Issue | Real? | MT refinement | Triggering controls / app options | Short summary |
|---|---|---|---|---|
| #1 C1 `_termValidSclkCache` | Dead/unused | MT-unreachable | `ctoProbGenEnhancementRev()>=3` for GLS skip; no MT gate on cache itself | Lazy `dosMap` fill is not thread-safe despite comment; no proven worker-body caller on shared `ctsInfra` |
| #2 C2 `ctoCGLat::getPhaseDelay` | Latent-only | Race-but-idempotent | `isUseClockGroupLatencyMT` / `_useCgLatMT`; `grpLatSpeedUp` prewarm | MT yes; exclusive `concurrent_hash_map` accessor on latency path; `_phaseDelays` is concurrent map; no proven divergent phase/cost |
| #3 C3 `processSccBagIntoCache` | Latent-only | Race-but-idempotent | `large_skew_group_limit_for_threading` (default 50) | MT via `ctsMtTaskRunner`; disjoint bags + assemble reorders by input; same-bag race not established |
| #4 C4 `runSccIteration` | Latent-only | (schedule early-exit) | same limit for `execPolicy::MultiThread` | Boolean AND/OR associative; bodies only local bool/log + timer reads; log string order can vary |
| #5 C5 `hardware_concurrency` grain | False positive | (schedule-only) | `_useCgLatMT && idx.size()>=2` | Grain sizes ranges only; `grpLat[i]` writes are index-disjoint |
| #6 C6 fmax TNS fold | Latent-only | Locked-but-order-dependent (thread-count only) | `maxThreads()` from `crmResources::getMaxThreadCount()` | Fixed-thread fold order is stable; FP association changes with thread count, not equivalent-run schedule |
| #7 C7 concurrent_vector median | Neutralized | Canonicalized-after-join | write-lock suspend; ST fallback | Push order discarded by `std::set` median |
| #8 C8 lazyTNS skew gather | Latent-only | Canonicalized-after-join | `crmResources::getMaxThreadCount()` | Parallel compute into per-thread buffers; serial merge in thread-index order |
| #9 C9 `insertDrcToCache` | Latent-only | Race-but-idempotent | `enable_cto_mt_task` (default true), `isQorTblUseDrcCache`, sclk count thresh, `!lazyUpdate` | Confirmed concurrent writers under QoR MT; `concurrent_hash_map` accessor serializes; values expected identical |
| #10 C10 `_collectSclkCache` | Dead/unused | MT-unreachable | GLS generator scope | Lazy `dosMap` on generator; callers are ST seed/critical-path prep, not worker bodies |

## Issue #1: Lazy mutable `dosMap` `_termValidSclkCache` on const getters

Dashboard ID: `C1`
Location: `ctsutil/ctsInfra.cc` (`isTermValidForSclk`, `getTermValidSclks`); field `ctsutil/ctsInfra.h` `_termValidSclkCache`

### Verdict

**Dead/unused (MT-unreachable)** for multi-threaded nondeterminism. The construct is a classic unsynchronized lazy cache (`dosMap`), and the source comment incorrectly claims thread-safety, but caller evidence places fills on sequential GLS/CTO paths, not inside `ctsMtTaskRunner` / `tbb::parallel_for` workers sharing one `ctsInfra`.

### Evidence

```7034:7074:ctsutil/ctsInfra.cc
ctsInfra::isTermValidForSclk(const ndmTerm* term, const ctsSclk& sclk) const
{
  auto it = _termValidSclkCache.find(term);
  if(it!=_termValidSclkCache.end()){
    ...
  }
  ...
  _termValidSclkCache[term] = validSclks;
  return rt;
}
...
  _termValidSclkCache[term] = validSclks;
  return _termValidSclkCache.at(term);
}
```

Type is `dosMap<const ndmTerm*, sclkValSetType>` (`ctsutil/ctsInfra.h`). No lock/atomic at the site. `dosMap` implementation is outside this depot; CoreStory did not establish internal synchronization.

### MT Reachability

Named parallel sites in GLS (`populateSharedSccCache` `doParallelFor`, `runSccIteration` `parallel_reduce`) do **not** call these getters. Documented call sites (`checkValidCandidate`, `calculateNetWorstLoadMargin`, `selectSeedCandidateUsingFlow`, `ctoFlowMgr::addTermsToUpTermsMapOfGrpTerm`, `ctomtUtil::getPathDelayAllCorner`) sit on sequential loops. CoreStory conversation 83 agreed: no worker-body invocation found.

Binding model: N/A (not on worker path).

### Race vs Ordering

If MT were reached: data race on non-concurrent `dosMap` (UB), not merely order dependence. Locking would be required. Not established under current call graph.

### Downstream Visibility

Gating empty valid-sclk sets can skip drivers (`checkValidCandidate`). That sink is real for correctness if raced, but not shown under concurrency.

### Controls / Gating

- `ctoProbGenEnhancementRev() >= 3` enables the empty-sclk skip in `checkValidCandidate`.
- Cache clear on skewgroup/cstrclock change is documented but not audited end-to-end here.

### Gate Audit

No lock claimed as neutralizer. Comment "thread-safe" fails inactive-gate / truthfulness check: no synchronization present.

### Code / Regression Setting Pass

Not run (`icc2query` / `nwtn/unit` unavailable in this client).

### Attribution

Comment author tag `rlwang` on the getters. Perforce annotate not run.

### Fix Direction

Only if a future MT caller is proved: replace with `tbb::concurrent_hash_map` (or precompute under ST before join). Do not pay for concurrent map on proven-ST hot paths. Performance: cache is meant to amortize `getSclksOnTerm` / `isTermIgnore`; keep hash lookup, avoid sorting.

### Missing evidence

Whole-product proof that no out-of-tree or future worker calls these on a shared `ctsInfra` concurrently; `dosMap` definition for any hidden sync.

## Issue #2: `ctoCGLat::getPhaseDelay` lazy write into concurrent map

Dashboard ID: `C2`
Location: `ctscto/ctscto.cc` `ctoCGLat::getPhaseDelay`; field `_phaseDelays`; callers `ctscto/ctoGrpLatCalc.cc`

### Verdict

**Latent-only (Race-but-idempotent)**. MT reachability is established. Same-corner miss-fill can theoretically race, but (a) latency queries hold an exclusive `cgLatMapMTType::accessor` across `getPhaseDelay`, (b) `_phaseDelays` is `tbb::concurrent_unordered_map`, (c) `calcGroupPhase` prewarm partitions unique map entries, (d) no evidence of divergent phase values reaching `grpLat` / flow cost across equivalent runs.

### Evidence

```5224:5259:ctscto/ctscto.cc
ctoCGLat::getPhaseDelay(ctscto* ctscto, cstrCorner corner) const
{
  ...
  auto it = _phaseDelays.find(corner);
  if (it != _phaseDelays.end()) {
    phase = it->second;
  } else {
    ...
    phase.merge(p);
    ...
    _phaseDelays.emplace(corner, phase);
  }
  return phase;
}
```

Latency path holds exclusive accessor:

```181:187:ctscto/ctoGrpLatCalc.cc
      cgLatMapMTType::accessor access;
      if(!_cgLatMapMT.find(access, key)){
        continue;
      }
      cgLat = &(access->second);
      phase = cgLat->getPhaseDelay(_ctscto, corner);
```

Batch MT dispatch:

```68:89:ctscto/ctoGrpLatCalc.cc
  if(_useCgLatMT && idx.size()>=2){
    ...
        tbb::parallel_for(tbb::blocked_range<size_t>(0, idx.size(), _step), [&](auto r) {
          for(auto i=r.begin(); i!=r.end(); ++i) {
            calcGrp(idx[i]);
          }
        });
```

### MT Reachability

- Dispatch: `tbb::parallel_for` in `calcGrpLatencyBatch`; `ctsMtTaskRunner::doParallelForEach` in `calcGroupPhase`; nested `parallel_for` in `getClockGroupLatencyPerSccPerTermMt`.
- Binding: blocked ranges / for_each over map entries (unique keys in prewarm). Dynamic TBB schedule, but outputs are per-index `grpLat[i]` or per-key cache fills.
- Gate: `_useCgLatMT` from `opt.isUseClockGroupLatencyMT()`.

### Race vs Ordering

Outcome class: concurrent miss-fill is **race-free at the container** (`concurrent_unordered_map`) and **serialized per `ctoCGLat`** on the query path (exclusive accessor). Ordering of float `merge` across sclks follows iterator/`set` order for a given corner; not shown to vary across equivalent runs. A mutex would not change associativity of any later max-ratio math; that path uses `replaceValueIfGreater` (associative max).

### Downstream Visibility

`phase.add(arrival)` -> `thisMaxLate` / threshold blend -> `grpLat[i]` -> `ctoFlow::getFlowCostMt` / `ctoFlowMgr` group-latency cost. Observable QoR cost if phase bits diverged; divergence not established.

### Controls / Gating

- `isUseClockGroupLatencyMT()`
- `grpLatSpeedUp` / `calcGroupPhase` prewarm (reduces miss-fill under MT)
- `ndmDesignWriteLock::suspend` fallback to ST if suspend fails

### Gate Audit

Accessor on query path: live (no thread-count gate disabling it). Prewarm path does **not** take an accessor while calling `getPhaseDelay` (API smell vs TBB accessor rules) but visits each map entry once under `doParallelForEach` and is sequenced before batch calc in flow init (CoreStory: phases not shown concurrent).

### Fix Direction

If elevating later: take `accessor` inside `calcGroupPhase` body, or compute phase under ST once. Prefer keeping concurrent map; avoid converting `_cgLatMapMT` to `std::map` on this hot path.

### Missing evidence

In-tree body of `elrfFloatValues::merge`; runtime 1-vs-N bit compare of `grpLat` / flow cost with MT on; proof `calcGroupPhase` never overlaps `calcGrpLatencyBatch` on the same map.

## Issue #3: `processSccBagIntoCache` check-then-act

Dashboard ID: `C3`
Location: `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc` `processSccBagIntoCache`, `populateSharedSccCache`

### Verdict

**Latent-only (Race-but-idempotent)** under documented invariants. MT populate is real; same-bag concurrent writers are not established; assemble path canonicalizes consumer order.

### Evidence

```2609:2668:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
  if (sharedCache.processedBags.find(bag) != sharedCache.processedBags.end()) {
    return;
  }
  ...
  sharedCache.processedBags.insert(bag);
}
...
  // note the input bags have no duplicates
  ...
  ctsMtTaskRunner task(...);
  task.doParallelFor([&](auto* bag) {
    processSccBagIntoCache(bag, sharedCache);
  });
```

```2671:2699:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
//! Iteration order is over the input bags then bag->getCorners() so the
//! resulting sccVec is deterministic regardless of cache insertion order.
```

### MT Reachability

`ctsMtTaskRunner::doParallelFor` when `newBags.size() >= large_skew_group_limit_for_threading` (default 50). Static-ish blocked ranges over unique `newBags`. Caller `spinOffSeed` / `isOnCriticalPathSolverAug` owns one `sharedSccCtx` and drives populate from the sequential seed loop (one populate at a time per cache).

### Race vs Ordering

Check-then-act exists, but workers get disjoint bags. Concurrent containers used. Duplicate fill would write the same `(bag,corner)` floats (timing frozen in scope). Consumer order neutralized by `assembleSccContextFromCache`. Locking would not change assemble output if values identical.

### Downstream Visibility

`evaluateCriticalPathSolverAug` -> seed eligibility / which GLS problems spawn. Order of cache insertion not consumed.

### Controls / Gating

`ctomtAppOptions::large_skew_group_limit_for_threading` (default 50).

### Gate Audit

Comment invariants (no duplicate bags; disjoint keys) are the real safety claim; not a lock.

### Missing evidence

Proof no overlapping concurrent `populateSharedSccCache` on one `sharedSccCtx` from two threads; that `getRootPathDelay` / `getSolverGlobalTargetLatency` cannot return different values under concurrent calls for the same bag.

## Issue #4: `runSccIteration` boolean `parallel_reduce`

Dashboard ID: `C4`
Location: `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h` `runSccIteration`

### Verdict

**Latent-only**. MT early-exit is intentional; boolean reduce is associative; bodies do not mutate shared eligibility state beyond local `sccEvalResult`.

### Evidence

`tbb::parallel_reduce` with `std::atomic<bool> globalDone`; `reduceAnd` / `reduceOr` on `bool`; `evaluateOneScc*` write `acc.value` / `acc.localLog` and call `infra->getPathDelay` (read-oriented timer query).

### MT Reachability

`execPolicy::MultiThread` when `ctx.sccVec.size() >= large_skew_group_limit_for_threading`. Work-stealing / blocked ranges; early break on `done()`.

### Race vs Ordering

Race: not shown on shared mutable GLS state. Ordering: which SCC runs when early-exit fires varies; final bool for AND/OR should not. `localLog` string concatenation order is schedule-dependent (diagnostic).

### Downstream Visibility

Boolean seed/load eligibility. Debug log text only for order sensitivity.

### Missing evidence

Whether `getPathDelay` lazy caches create observable divergent state when early-exit skips work (would be side-effect ND). Not traced into timer internals here.

## Issue #5: `hardware_concurrency` grain in `calcGrpLatencyBatch`

Dashboard ID: `C5`
Location: `ctscto/ctoGrpLatCalc.cc` ~80-81

### Verdict

**False positive** for equivalent-run MT ND. Host HW concurrency only sets TBB grain (`_step`); each job still writes a unique `grpLat[idx[i]]`.

### Evidence

```80:88:ctscto/ctoGrpLatCalc.cc
        size_t numT = std::thread::hardware_concurrency();
        _step = jobSize/numT+1;
        ...
        tbb::parallel_for(tbb::blocked_range<size_t>(0, idx.size(), _step), ...
```

Sibling `ctsMtTaskRunner` correctly uses `crmResources::getMaxThreadCount()` intersect arena concurrency for other sites.

### MT Reachability

Same as C2 batch path. Schedule-only effect of grain.

### Race vs Ordering

Schedule-only; result vector index-stable if `getClockGroupLatency` is pure per index (shared cache effects covered under C2).

### Downstream Visibility

None from grain alone.

## Issue #6: fmax TNS parallel partition + double fold

Dashboard ID: `C6`
Location: `ccd/ctsccd/fmax\include\fmaxTimingCostFunction.h` `evaluateTnsAndWnsParallel`, `calculateRanges`

### Verdict

**Latent-only** for equivalent-run ND; **thread-count-sensitive FP association** only. With fixed `maxThreads()` (`crmResources::getMaxThreadCount()`), ranges and thread-index fold order are deterministic. This is not schedule ND under same ENV/thread budget.

### Evidence

Per-thread `resultsPerThreadTNS[threadCount]+=...` then serial `resultTNS += resultsPerThreadTNS[threadIndex]` in index order. WNS uses min (associative). Violated-path vectors concatenated by stable thread offsets.

### MT Reachability

`tbb::parallel_for` over thread indices when `maxThreads() > 1`.

### Race vs Ordering

Ordering of float association across partitions depends on thread count (config), not on which worker finishes first for a fixed partition. Locking does not fix FP association.

### Downstream Visibility

`resultTNS` / violated path lists feed fmax cost / solver / reporting (`fmaxFlow`, integrators). Accept/reject sensitivity to ULP TNS diffs not proved.

### Missing evidence

Whether any consumer thresholds on bit-exact TNS; 1-vs-N A/B of accept/reject (would confirm config sensitivity, not equivalent-run ND).

## Issue #7: `concurrent_vector` arrivals then set median

Dashboard ID: `C7`
Location: `ctssch/ctsInterClockBalance.cc` ~741-780

### Verdict

**Neutralized (Canonicalized-after-join)**.

### Evidence

```741:780:ctssch/ctsInterClockBalance.cc
  tbb::concurrent_vector<float> arrivals1;
  ...
    tbb::parallel_for(... arrivals1.push_back(getArrival(...)));
  std::set<float> medianCal;
  for(float v : arrivals1){
    if(nwmathFloat::isUninit(v)) continue;
    medianCal.insert(v);
  }
  // median of unique values
```

### MT Reachability

Direct `tbb::parallel_for` after write-lock suspend (ST fallback if suspend fails).

### Race vs Ordering

Push order varies; membership of `std::set` does not. Median over unique floats is order-insensitive.

### Downstream Visibility

Returned median drives source-latency adjustment; order of `arrivals1` not consumed elsewhere in this function.

## Issue #8: lazyTNS MT skew-query gather then serial merge

Dashboard ID: `C8`
Location: `ctssc/lazytns/ctsLazyCostEp.cc` ~2023-2064

### Verdict

**Latent-only (Canonicalized-after-join)** assuming unique skew query keys.

### Evidence

Parallel fill of `finalStepEntries[thread]`; serial loops in thread-container order into `pathMap` / `initExtra` / `updateTracedPathBatch`. `initExtra` ratchets slack with `if (_slack > pathSlack ...)` (min-like), which is order-insensitive for the final min if all entries are applied.

### MT Reachability

`tbb::parallel_for` over `crmResources::getMaxThreadCount()` partitions of `skewQueries`.

### Race vs Ordering

No concurrent mutation of `pathMap`. Residual order sensitivity only if duplicate `(ep,qid,lchClkId)` keys carry different slacks (first `emplace` wins); not shown.

### Missing evidence

Proof `skewQueries` has unique keys; that `calculateSkewSlackWithQ` is pure given inputs.

## Issue #9: `ctscto::insertDrcToCache` find-then-insert

Dashboard ID: `C9`
Location: `ctscto/ctscto.cc` `insertDrcToCache`; consumers `ctscto/ctoLog.cc` `getDrcViolation`

### Verdict

**Latent-only (Race-but-idempotent)**. This is the strongest **confirmed MT writer** among C1-C10, but the concurrent_hash_map accessor protocol serializes per-`termId` mutation, and duplicate inserts of the same DRC key should store the same float.

### Evidence

```6167:6186:ctscto/ctscto.cc
  if(_cachedDrcData.find(access, termId)){
    access->second.insert(std::make_pair(key, value));
    return;
  }
  _cachedDrcData.insert(access, termId);
  access->second.insert(std::make_pair(key, value));
```

`_cachedDrcData` is `tbb::concurrent_hash_map<ctsTermId, std::map<mctKey,float>>`.

MT enablement:

```3455:3467:ctscto/ctscto.cc
  if(useDrcCache && sclks.size() > sizeThresh){
    setUseCachedDrcData(true);
  }
  ...
  if (_enableMtTask && !lazyUpdate) {
    printMultiClockSkewAndDrcMt(...);  // ctsMtMgr jobs -> ctoQorLog::collectInfo -> evaluateDrc
    setUseCachedDrcData(false);
```

`_enableMtTask` defaults from `getNewFeature("enable_cto_mt_task", true)`.

### MT Reachability

`ctsMtMgr::runTask` batches of `ctoQorLog` jobs in `printMultiClockSkewAndDrcMt` / `printQorCheckpointTables`. Multiple trees can touch overlapping terms -> concurrent `insertDrcToCache` / `getCachedDrc`.

### Race vs Ordering

Not a live data race on the hash map when accessors are used correctly. Find-miss/insert window is handled by `concurrent_hash_map::insert`. Inner `std::map` is mutated only under exclusive accessor. Result ND would require divergent `getDrcCost` values for the same key; not shown. Locking beyond the accessor is unnecessary for determinism of identical writes.

### Downstream Visibility

Cached DRC floats in QoR tables / reports when `isQorTblUseDrcCache` is on. Lookup by key in `getCachedDrc` (order-insensitive).

### Controls / Gating

- `enable_cto_mt_task` (default true)
- `isQorTblUseDrcCache()`
- `cto_qor_log_use_cached_thresh` (default 5)
- Disabled when lazy phase/arrival update flags set
- Cleared after MT print returns

### Gate Audit

Cache flag is live on the MT print path (set true before MT, false after). Not an inactive gate.

### Fix Direction

If TSAN ever flags the find/insert pattern: use a single `insert`+mutate under accessor without the separate find, or `emplace`-style API. No need to replace with ordered map.

### Missing evidence

TSAN on QoR MT path; confirmation overlapping jobs query identical `(term,type,mode,corner)` with identical `getDrcCost`.

## Issue #10: Mutable `_collectSclkCache` (`dosMap`) on GLS generator

Dashboard ID: `C10`
Location: `ctomtGlsProblemGenerator.cc` `collectSclkOnTerm`; field in `.h`

### Verdict

**Dead/unused (MT-unreachable)** for MT ND. Same pattern as C1 on the generator object; filled during ST `collectSclkOnTerm` before / outside worker bodies that evaluate SCCs.

### Evidence

```140:148:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
  auto cacheIt = _collectSclkCache.find(seedTerm);
  if (cacheIt != _collectSclkCache.end()) {
    sclkBagVec = cacheIt->second;
    return;
  }
  ...
  _collectSclkCache[seedTerm] = sclkBagVec;
```

Called from `isOnCriticalPathSolverAug` / seed collection on the sequential `spinOffSeed` path; parallel region is later `runSccIteration` / bag populate, which does not touch this cache.

### Missing evidence

Any future/refactor path calling `collectSclkOnTerm` from `doParallelFor` workers on a shared generator.

## Verification Notes

- Commands/tools: CoreStory `send_message` / `semantic_search` on project 10 conversation 83; local Read/Grep; no `viewtool`, `mgrep-agent`, `clangd_query.py`, `icc2query`, or `check-ascii` in this environment.
- Source roots: local `c:\Users\carys\cts` (and `include/` mirrors).
- ASCII: report authored ASCII-only; `check-ascii` not installed.
- Limitations: `dosMap` / `elrfFloatValues::merge` bodies out of tree; no runtime 1-vs-N or TSAN confirmation; secondary seeds S1-S5 not elevated.
- Strongest supported outcomes: **no candidate proved Real** for equivalent-run MT ND; **C9** is the strongest confirmed concurrent writer (latent/idempotent); **C2/C3** are real MT shapes neutralized or idempotent; **C1/C10** dismissed as MT-unreachable; **C7** neutralized; **C5** false positive; **C4/C6/C8** latent under associative or post-join serialization arguments.
