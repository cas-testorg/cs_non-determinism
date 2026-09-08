# CTS MT-ND Discovery Candidates (not prove-nd)

**Scope:** CTS module (`c:\Users\carys\cts`), catalog Tier-2 MT/concurrency patterns  
**Method:** nd-code-analyzer Stage-1 seeds + Stage-3 deep-read + CoreStory project `cts-code` (id 10), conversation 82  
**Classification:** **candidates only** — do not treat as Real until prove-nd-mt  
**Scanner note:** `scan_nd.py` not present in skill tree; mechanical scan used catalog regexes via ripgrep

**Controls surfaced (for verifier):** `ctomtAppOptions::large_skew_group_limit_for_threading` (default 50), `opt.isUseClockGroupLatencyMT()`, `opt.grpLatSpeedUp()`, `ctsscUtil::getMaxThreadCount()` / `crmResources::getMaxThreadCount()`, `ctsMtTaskRunner` + `ndmDesignWriteLock::suspend`, `bugFixGlsQueryFlowPathForLpspCheck`

**No Stage-1 hits:** 4.3 (mutable non-atomic counters), 4.5 (condvar lost-wakeup), 4.6 (address-keyed lock striping)

---

## C1 — 4.2 / 4.4 / 3.7 | Lazy mutable `dosMap` cache on const path (claimed thread-safe)

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 4.2 first-touch materialization; 4.4 check-then-act; 3.7 wrapper (`dosMap`) |
| **File / symbol** | `ctsutil/ctsInfra.cc` — `ctsInfra::isTermValidForSclk`, `getTermValidSclks`; field `ctsutil/ctsInfra.h` `_termValidSclkCache` (`termSclksMapType = dosMap<const ndmTerm*, sclkValSetType>`) |
| **Why matched** | `mutable` cache; const getters do find → compute → assign; comment asserts thread-safety but type is `dosMap`, not a concurrent container |
| **MT reachability evidence** | Callers include `ctomtGlsProblemGenerator.cc` (~928, ~3220), `ctomtUtil.cc`, `ctoFlowMgr.cc`, `ctoscGlobal.cc` — same GLS/CTO surfaces that use `ctsMtTaskRunner` / MT critical-path checks |
| **Shared / mutable state** | `_termValidSclkCache` on shared `ctsInfra` |
| **Downstream / observable** | Term/sclk validity gates filtering, fanout/critical-path decisions, flow updates (exact QoR sink TBD) |
| **Known control / neutralizer** | Comment: clear cache on skewgroup/cstrclock change; **no lock/atomic found at site** |
| **Missing evidence** | Prove concurrent callers under `parallel_for`; confirm `dosMap` is not internally synchronized; show divergent validity / filter outcome across runs |
| **CoreStory to validate** | Call graph from MT GLS/CTO workers → `getTermValidSclks` / `isTermValidForSclk`; invalidation vs design mutation timing |

---

## C2 — 4.2 / 4.4 | `ctoCGLat::getPhaseDelay` lazy write into concurrent map

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 4.2 first-touch in `const` getter; 4.4 find-then-`emplace` without held write accessor |
| **File / symbol** | `ctscto/ctscto.cc` — `ctoCGLat::getPhaseDelay`; field `_phaseDelays` (`mutable tbb::concurrent_unordered_map<cstrCorner, elrfFloatValues>`) in `ctscto/ctscto.h` |
| **Why matched** | Const method: `_phaseDelays.find` miss → merge phase delays → `_phaseDelays.emplace` |
| **MT reachability evidence** | Called under `_useCgLatMT` from `ctoGrpLatCalc::getClockGroupLatencyPerScc` while holding `cgLatMapMTType::accessor`; batch MT via `calcGrpLatencyBatch` + `tbb::parallel_for` |
| **Shared / mutable state** | Per-`ctoCGLat` `_phaseDelays`; entries live in shared `_cgLatMapMT` |
| **Downstream / observable** | Phase + arrival → `thisMaxLate` / worst-ratio → group latency → CTO cost / skew-latency decisions (`ctoFlow::getFlowCostMt`, `ctoFlowMgr`) |
| **Known control / neutralizer** | Gated by `isUseClockGroupLatencyMT` / `_useCgLatMT`; `clearCachedCGLat` / `clearCachedValues`; sibling `calcGroupPhase` pretends to warm cache to avoid MT lock contention |
| **Missing evidence** | Whether two threads can miss-cache the same corner concurrently; whether `elrfFloatValues::merge` / sclk iteration is commutative; observability of bit-level vs logical latency divergence |
| **CoreStory to validate** | `ctoGrpLatCalc` ↔ `getPhaseDelay` ↔ `getFlowCostMt` / flow bag latency consumers; relationship of `calcGroupPhase` pre-warm to getter races |

---

## C3 — 4.4 | `processSccBagIntoCache` concurrent check-then-act

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 4.4 compound op on concurrent containers (find processed → write maps → insert processed) |
| **File / symbol** | `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc` — `processSccBagIntoCache`, `populateSharedSccCache` |
| **Why matched** | `processedBags.find(bag)` early return, then writes `glateTarget` / `rootLateEarly` / `targetSkews`, then `processedBags.insert(bag)` — not one atomic accessor scope |
| **MT reachability evidence** | `populateSharedSccCache` runs `ctsMtTaskRunner::doParallelFor` when `newBags.size() >= large_skew_group_limit_for_threading` |
| **Shared / mutable state** | `sharedSccCtx` concurrent set/maps |
| **Downstream / observable** | `assembleSccContextFromCache` (documents deterministic bag/corner walk) → `evalGskew*` / `evalGlate` / `isOnCriticalPathSolverAug` → problem eligibility |
| **Known control / neutralizer** | App option threshold; comment claims disjoint keys for distinct bags; assemble path reorders by input bag vector |
| **Missing evidence** | Same bag in `newBags` twice or overlapping populate calls; torn visibility if insert of `processedBags` races with find; any consumer that iterates concurrent maps directly (bypassing assemble) |
| **CoreStory to validate** | `spinOffSeed` / `findNextProblem` shared cache lifetime; callers of `buildsccContext` vs `populateSharedSccCache` |

---

## C4 — 3.1 (weak) / schedule early-exit | `runSccIteration` `tbb::parallel_reduce`

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | Catalog 3.1 seed (`tbb::parallel_reduce`); **operand is `bool` AND/OR, not FP** — weak 3.1; still schedule-dependent early exit via `globalDone` |
| **File / symbol** | `ctomtGlsProblemGenerator.h` — `runSccIteration`; used by `evalGskewBuffering`, `evalGskewNotBuffering`, `evalGlate` |
| **Why matched** | Only `parallel_reduce` hit in module; MultiThread policy + early break on `done()` |
| **MT reachability evidence** | Policy `MultiThread` when SCC count ≥ `large_skew_group_limit_for_threading` |
| **Shared / mutable state** | Per-reduce local `sccEvalResult`; `std::atomic<bool> globalDone` |
| **Downstream / observable** | Boolean eligibility of drivers/loads for GLS problem generation → which xforms are spawned |
| **Known control / neutralizer** | Boolean AND/OR is associative; ST path available; early-exit intended |
| **Missing evidence** | Side effects inside body (`getPathDelay`, logging) that make skipped work observable; mismatch ST vs MT when early exit fires |
| **CoreStory to validate** | `isOnCriticalPathSolverAug` → eval\* → `findNextProblem` / integrator selection |

---

## C5 — 3.5 | `hardware_concurrency` sizes parallel grain

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 3.5 thread-count-dependent algorithm sizing |
| **File / symbol** | `ctscto/ctoGrpLatCalc.cc` — `calcGrpLatencyBatch` (`numT = std::thread::hardware_concurrency(); _step = jobSize/numT+1`) |
| **Why matched** | Live HW concurrency sets TBB `blocked_range` grain size |
| **MT reachability evidence** | Same function’s MT branch under `_useCgLatMT` |
| **Shared / mutable state** | Writes `grpLat[i]` / per-index calc (likely index-stable) |
| **Downstream / observable** | Group latency vector feeding CTO cost (if grain only affects schedule, may be neutralized) |
| **Known control / neutralizer** | Possible neutralization if per-index writes are independent; sibling `ctsMtTaskRunner` uses `crmResources::getMaxThreadCount()` ∩ `max_concurrency()` instead |
| **Missing evidence** | Any order-sensitive shared mutation inside `calcGrp` beyond indexed outputs; machine-to-machine result diffs with identical logical thread budget |
| **CoreStory to validate** | Compare with configured `getMaxThreadCount` paths; `grpLat` consumers in `ctoFlow` / `ctoFlowMgr` |

---

## C6 — 3.5 / 3.1-adjacent | Fmax timing cost parallel partition + double TNS fold

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 3.5 partition by `maxThreads()`; parallel per-thread `double` TNS accumulation then sequential fold (FP association across partitions) |
| **File / symbol** | `ccd/ctsccd/fmax/include/fmaxTimingCostFunction.h` — `calculateRanges`, `evaluate` (`tbb::parallel_for` over thread indices) |
| **Why matched** | Range split uses `ceil(allPathsCount/threadCount)`; per-thread `resultsPerThreadTNS` summed in thread-index order; violated-path vectors concatenated by thread index |
| **MT reachability evidence** | Explicit MT evaluate path when `numberOfThreads > 1` |
| **Shared / mutable state** | Per-thread local vectors/scalars; merge into `violatedPaths*` / `resultTNS` / `resultWNS` |
| **Downstream / observable** | Cost / violated-path sets → fmax solver / problem generator / QoR |
| **Known control / neutralizer** | Fixed thread-index merge order; WNS is min (associative); TNS FP sum order depends on partition |
| **Missing evidence** | Whether `maxThreads()` tracks host vs configured budget; whether TNS bit-diffs affect accept/reject; path-list order sensitivity downstream |
| **CoreStory to validate** | `fmaxFlow` / `fmaxSolver` / `fmaxCgSolver` consumption of evaluate outputs |

---

## C7 — 3.2 | `concurrent_vector` push from `parallel_for` (median path)

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 3.2 shared concurrent container writes under `parallel_for` |
| **File / symbol** | `ctssch/ctsInterClockBalance.cc` — arrival collection into `tbb::concurrent_vector<float> arrivals1` |
| **Why matched** | Workers `push_back(getArrival(...))` without stable index |
| **MT reachability evidence** | Direct `tbb::parallel_for` after write-lock suspend |
| **Shared / mutable state** | `arrivals1` |
| **Downstream / observable** | Values inserted into `std::set<float> medianCal` → median return (order of push likely neutralized by set) |
| **Known control / neutralizer** | **Likely neutralized** by value-set median; keep as candidate until verifier confirms no other consumer of `arrivals1` order |
| **Missing evidence** | Any use of vector order before set; duplicate/uninit handling differences |
| **CoreStory to validate** | Callers of this median helper → source-latency adjustment QoR |

---

## C8 — 3.2 / 3.5 / 3.6 | lazyTNS MT skew-query gather then serial merge

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 3.2/3.5 per-thread buffers sized by `getMaxThreadCount`; 3.6 post-collection merge into `pathMap` without explicit sort |
| **File / symbol** | `ctssc/lazytns/ctsLazyCostEp.cc` — MT skew query block (~2023–2064) |
| **Why matched** | Partition by thread count; `finalStepEntries[thread]` then nested loops into `pathMap` / `initExtra` / `updateTracedPathBatch` |
| **MT reachability evidence** | Explicit `tbb::parallel_for` over `numberOfThreads` |
| **Shared / mutable state** | Per-thread vectors; serial mutation of `pathMap` and `costEp` |
| **Downstream / observable** | Traced path / slack updates on lazy model endpoints |
| **Known control / neutralizer** | Serial postprocess in thread-index order; map keyed inserts may be order-insensitive if values identical |
| **Missing evidence** | Whether `initExtra` / `updateTracedPathBatch` are order-sensitive; `_enableMt*` flags gating this path |
| **CoreStory to validate** | `lazyTnsModel::traceLazyPathsMt` / `ctsLazyModelMtUtil` job chain; `populateMtJob::updateCache` “not thread-safe” sibling boundary |

---

## C9 — 4.4 | `ctscto::insertDrcToCache` find-then-insert

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 4.4 concurrent_hash_map check-then-act across two operations |
| **File / symbol** | `ctscto/ctscto.cc` — `insertDrcToCache` on `ccMap` (`tbb::concurrent_hash_map`) |
| **Why matched** | `find(access)` then mutate; on miss `insert(access)` then mutate — window between find miss and insert |
| **MT reachability evidence** | DRC cache on shared `ctscto`; used from CTO/CCD timing/DRC paths (MT extent TBD) |
| **Shared / mutable state** | `_cachedDrcData` |
| **Downstream / observable** | Cached DRC values via `getCachedDrc` |
| **Known control / neutralizer** | Insert uses accessor; need proof whether duplicate concurrent inserts lose updates |
| **Missing evidence** | Concurrent writers for same `termId`; impact on DRC decisions |
| **CoreStory to validate** | Writers/readers of `_cachedDrcData` under CCD/CTO MT |

---

## C10 — 4.2 / 3.7 | Mutable `_collectSclkCache` (`dosMap`) on GLS generator

| Field | Detail |
| --- | --- |
| **Pattern / mechanism** | 4.2 lazy cache fill; 3.7 `dosMap` wrapper |
| **File / symbol** | `ctomtGlsProblemGenerator.h/.cc` — `_collectSclkCache`; sibling `ctoscProblemGenerator` |
| **Why matched** | `mutable dosMap<ndmTerm*, vector<ctoSclkBag*>>`; find → build → assign |
| **MT reachability evidence** | Lives on GLS problem generator used in MT GLS flow; **need proof cache is touched from worker threads vs only ST seed prep** |
| **Shared / mutable state** | Generator-owned cache |
| **Downstream / observable** | Sclk-bag vectors for seed/problem construction |
| **Known control / neutralizer** | None established at site |
| **Missing evidence** | Concurrent access; whether bag vector order is consumed order-sensitively |
| **CoreStory to validate** | Which threads call the collect-sclk helper during `findNextProblem` / critical-path filtering |

---

## Secondary / lower priority seeds (record only)

| ID | Pattern | Site | Note |
| --- | --- | --- | --- |
| S1 | 3.5 | `ctsutil/ctsMtTaskRunner.h` `doParallelFor` | Uses configured max threads ∩ arena concurrency for grain; likely scheduling-only |
| S2 | 3.7 | `dosUnorderedMap` in `ctssch/ctsTask*`, ICG helpers | Pointer-keyed unordered wrapper; MT reachability unclear |
| S3 | 3.7 | `nwcInsOrdMap` in `ccd/skewopt/soSkewPotentialDcrt*` | Insertion-order map; confirm MT + order-sensitive iteration |
| S4 | 4.2 | `ctoFlowMgr` `_sccCompareResultCache` / `_strEqvCache` / `_termsBelowGrpCache` | Mutable caches; likely ST relax analyzer — confirm no MT |
| S5 | 3.2 | Many `tbb::parallel_for` in `ccd/skewopt/*`, `ctsLazyModel.cc` | Stage-1 flood; promote only after shared-write + order-sensitive sink proof |

---

## Explicitly empty catalog buckets (this pass)

- **4.3** mutable non-atomic counter RMW — no regex hits  
- **4.5** condvar lost-wakeup — no hits  
- **4.6** address-keyed lock striping — no hits  
- **True 3.1 FP `parallel_reduce`** — none; only boolean reduce (C4)

---

## Verifier handoff checklist

1. Start with **C1, C2, C3** (strongest static MT-cache / check-then-act shapes).  
2. Use prove-nd-mt / TSan for concurrent const-getter materialization and concurrent_hash_map TOCTOU.  
3. Re-validate CoreStory edges: `ctsMtMgr` / `ctsMtTaskRunner` → GLS/lazyTNS/CTO workers → shared caches above.  
4. Confirm controls: `isUseClockGroupLatencyMT`, `large_skew_group_limit_for_threading`, max-thread options.  
5. Do **not** elevate C4/C5/C7 without proving observable divergence (known neutralizers present).
