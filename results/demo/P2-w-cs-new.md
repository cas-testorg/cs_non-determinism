One elevated concurrency gap in the same family as the exemplar; several similar patterns are mitigated and not elevated. Full breakdown is in the canvas [shared-state-concurrency](shared-state-concurrency.canvas.tsx).

### Elevated: incomplete `_upTermsMapOfGrpTerm` pre-cache contract

**Shared state:** `ctoFlowMgr::_upTermsMapOfGrpTerm` — non-thread-safe `std::map`, lazy-filled by `getUpTermsForGrpTermsOfSclk`.

**Parallel path:** `optimizeDriver` / `optimizeDriverWithPlanSplit` → `runAccurate` (write lock suspended) → `ctomtBuffer::runAddDelay` → `calculateTargetDelayForSingleFanout` → `getGrpLatency(..., useCached)`.

**Gap:** `findNextProblem` pre-caches only when buffering + `!solverAugLeafOnly` + (`enhancement_revision>1` **or** `exclude_near_grplat`). `TargetDlyConfig` enables cached access when `runtime_improvement_revision>1` and claims the same conditions — they are not the same.

Concrete mismatch: `enhancement_revision==1`, `runtime_improvement>1`, `exclude_near_grplat==false` → no pre-cache, but single-fanout delay still calls `getGrpLatency(..., true)` from parallel workers → concurrent miss-and-insert.

**Classification:** strongly supported conflicting-access gap (DATA RACE–class). Not confirmed as always-on under default options (revisions default to 0). Nondeterminism plausible (crash or schedule-dependent group-latency / delay targets) pending TSan/runtime under that option set.

### Exemplar (not a defect as designed)

When buffering + enhancement/exclude flags match, pre-cache runs; `ctoscLoadPartition::isNearLongest` explicitly relies on that for MT-safe cached reads. Post-commit `addTermsToUpTermsMapOfGrpTerm` is serial via `notifyStatus`.

### Rejected / mitigated

| Candidate | Why not elevated |
|---|---|
| `populateMtJob::updateCache` | Serial post-process after parallel prepare batches |
| `ctoscFilter::_timerCache` | Per-xform clone via `cloneCore()` |
| `_onClockCache` | `tbb::concurrent_unordered_map` |
| `soMonitor` / `msProfiler` | No proven MT worker use |
| `ctoGrpLatCalc` unlock / `ctsMtMgr` lifecycle / off-track mutex | Ownership / join paths established |

**Next validation:** align the `TargetDlyConfig` predicate with pre-cache (or pre-cache whenever any MT caller uses `useCached=true`), then TSan under the gap option set with multi-problem single-fanout buffering.
