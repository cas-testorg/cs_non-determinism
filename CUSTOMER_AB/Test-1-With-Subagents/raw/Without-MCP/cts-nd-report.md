# Non-Determinism Analysis Report — cts-nd-audit

**Generated:** 2026-09-15 07:00 UTC
**Module / Path:** `/remote/us01home05/carys/cts  (snapshot of nwtn/src/cts)`
**Search backend:** rg (branch: `main (depot attribution only; tree is a read-only snapshot)`)
**Patterns evaluated:** 21
**Files scanned (with hits):** 18
**Total findings:** 19

---

## Executive Summary

### Severity counts

| Severity | Count |
|---|---:|
| HIGH | 6 |
| MEDIUM | 13 |
| LOW | 0 |
| INFO (file already adopts hySet/hyMap) | 0 |
| **Total** | **19** |

### Findings by category

| Category | HIGH | MEDIUM | LOW | INFO | Total |
|---|---:|---:|---:|---:|---:|
| container | 2 | 5 | 0 | 0 | 7 |
| naming | 1 | 3 | 0 | 0 | 4 |
| parallel | 1 | 2 | 0 | 0 | 3 |
| iteration | 0 | 2 | 0 | 0 | 2 |
| hash | 1 | 0 | 0 | 0 | 1 |
| random | 0 | 1 | 0 | 0 | 1 |
| sorting | 1 | 0 | 0 | 0 | 1 |

### Top 5 hot files

| File | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|
| `mscts/drivers/msDrivers.cc` | 1 | 1 | 0 | 2 |
| `ctsmisc/ctsAutoBalancePoint.cc` | 1 | 0 | 0 | 1 |
| `ctscto/ctosc/ctoscGlobal.h` | 1 | 0 | 0 | 1 |
| `ctssc/ctskSize.cc` | 1 | 0 | 0 | 1 |
| `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc` | 1 | 0 | 0 | 1 |

---

## Defect Surface at a Glance

One row per real finding. `realness` is the Stage-2 classification; every row below is `real`, meaning a downstream consumer was traced that can observe the order or value. Non-real classifications are in their own section near the end.

| Sev | Site | Pattern | Realness | Issue | Triggering controls |
|---|---|---|---|---|---|
| HIGH | `ctsmisc/ctsAutoBalancePoint.cc:656` | 1.2 | `real` | Auto balance-point launch-chain processing order comes from a pointer-keyed std::map; std::sort tie-break is address-derived and feeds setCtsDelayPoint() | **Flow entry**: `ctsAutoBalancePoint::run()`-style entry points at `ctsmisc/ctsAutoBalancePoint.cc:170-175` and `ctsmisc/ctsAutoBalancePoint.cc:255-259`. |
| HIGH | `mscts/drivers/msDrivers.cc:8189` | 1.2 | `real` | Per-hierarchy tap insertion order derives from std::map<ndmHier*> because compareHierDepth is only a depth comparison, not a total order | Reached from `msClockDrivers::insertInstsMVAware()`; the ND branch is taken at `mscts/drivers/msDrivers.cc:8184`: So all three of the following must hold: 1. |
| HIGH | `ctscto/ctosc/ctoscGlobal.h:274` | 1.4 | `real` | sclkCornerHash hashes ctoSclkBag* address: load-partition weighted late-margin sum is order-dependent and reorders buffering sinks | Reached from `ctomtBuffer::runBuffering` path, `ctscto/ctosc/ctomt/ctomtBuffer.cc:846-852`: Guards: `ctsP->getFlowType() == CTO_GSKEW` (global skew optimization). |
| HIGH | `ctssc/ctskSize.cc:1384` | 2.2 | `real` | kneeMap keyed by lib-cell getFullName() inside the CCD/CTS sizing LEQ-filter inner loop | Reached whenever CCD/CTS cell sizing runs with `ccdConfig::get_knee_range() > 0` and the driver has >= 3 logically-equivalent cells (the normal case for any real clock buffer/inverter library). |
| HIGH | `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | 2.5 | `real` | fmax LP redundant-path dedup sorts by constraint VALUE but calls std::unique with POINTER equality | Reached by the incremental fmax LP flow (CCD fmax / clock-concurrent optimization) whenever `mergeViolatedPathsOfSolutionsParallel` runs, i.e. |
| HIGH | `ccd/skewopt/soSolverUpdater.cc:2100` | 3.2 | `real` | Concurrent std::map node insertion into the CG solver's log-sum-exp function maps from tbb::parallel_for_each over scenarios | *Not gated - this runs multi-threaded by default whenever there is more than one scenario.** There is no `enableMultiThreading` check, no `getMaxThreadCount()` check, no `isMultiThread` branch and no single-thread fallback around `soSolverUpdater.cc:2100/2107`. |
| MEDIUM | `ctscto/ctoFlowClone.cc:1884` | 1.2 | `real` | ctoFlow::restructFlow iterates std::set<ndmTerm*> candidate sets in address order, then clones/shields buffers and truncates at a 10% cap | Entry point `ctoFlow::flowPreOptRestruct()` (`ctscto/ctoFlowClone.cc:1862`) is called from exactly one place: App option: `cts.optimize.enable_latency_driven_pre_opt_restructuring`, registered at `ctsui/ctsuiOptimizeAppOptions.cc:1334` with **default `false`** and `cciuAppOptionMgr::UNLISTED`. |
| MEDIUM | `mscts/drivers/msDrivers.cc:11645` | 1.2 | `real` | Keepout margins are applied to a run-varying subset of clock lib cells because setKeepoutMarginForLibCell returns out of its std::set<ndmModule*> loop | Gated behind one app option, checked identically at every producer: Guards, all of the form `enableHtreeCellKeepoutMargin.length() != 0`: `mscts/drivers/msDrivers.cc:1602`, `mscts/drivers/msDrivers.cc:2324`, `mscts/drivers/msAutoTapFlow.cc:1307`, `:1322`, `:1342`, `mscts/msgts/msgtsFlow.cc:757`, `mscts/msgts/msgtsIrregGlobalTreeFlow.cc:537`, `:550`. |
| MEDIUM | `mscts/msmesh/msLevelBalancer.cc:1745` | 1.2 | `real` | MV-aware level balancing inserts buffers per power domain in std::map<ndmPowerDomain*> address order | Two conditions, both checked at the single call site `mscts/msmesh/msLevelBalancer.cc:1835`: 1. App option `enable_mv_aware_level_balancing`: This is `MSUI_HIDDEN` and defaults to **false**, so the whole function is unreachable on a default run. |
| MEDIUM | `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32` | 1.3 | `real` | Endpoint-optimization seed priorities are numbered by unordered_set<ndmTerm*> iteration, making the driver optimization order address-dependent | Flow gate: `ctomtGlsProblemGenerator::initializeCandidates()` only calls `initTargetDriverCandidate()` when `_flowType == CTO_ENDPOINT` (`ctomtGlsProblemGenerator.cc:567-570`). |
| MEDIUM | `ctsmisc/ctsIfsDataType.h:32` | 1.3 | `real` | IFS prepone endpoint set is an unordered_set<ndmTerm*>; its hash order becomes the GLS endpoint-optimization candidate numbering | **Flow gate (hard)**: `ctomtGlsProblemGenerator::initializeCandidates()` only calls `initTargetDriverCandidate()` when `_flowType == CTO_ENDPOINT` (`ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:567-570`). |
| MEDIUM | `ccd/ctsccd/cgbased/ccdcgSolver.cc:501` | 1.5 | `real` | CCD CG solver seeds candidate values from the process-global C `rand()` stream, which it also clobbers for every other module | Ungated. `seedAndPruneCands()` is called unconditionally from the CG solve path at `ccd/ctsccd/cgbased/ccdcgSolver.cc:363`; there is no app option, command flag, or threading guard on it. |
| MEDIUM | `ctsmisc/ctsICGCell.cc:514` | 2.2 | `real` | ICG signature/BDD traversal keys two per-net maps on getPathName(), rebuilt on every node visit | Reached by ICG merging (`ctsMergeIcg::runBDDMerge` / `runFlatNetMerge`, `icg/ctsMergeIcg.h:334-335`) during CTS. The non-BDD signature path (`_bddBased == false`) is the default; the BDD path is additionally compiled under `#ifdef USE_CUDD`. |
| MEDIUM | `ctssc/ctsXformProblems.cc:1130` | 2.2 | `real` | _instInfoMap snapshots pre-transform instance state by getFullName(); a rename is reported as a removed cell | Reached on the CTS/CCD transform-problem evaluation path whenever a transform snapshots and then re-checks its instance set. `updateRemovedCellsStats` is gated by `skipUpdateRemovedCellsStats()` (line 1277). |
| MEDIUM | `mscts/msutil/msInfra.cc:1255` | 2.2 | `real` | Clock latency and ideal-network constraints stored under getPathName(), then resolved back by findTerm() - silent drop on rename | Reached whenever multisource CTS (`create_clock_tree` / MSCTS flow) runs on a design carrying `set_clock_latency` or `set_ideal_network` constraints on clock pins. |
| MEDIUM | `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | 3.2 | `real` | fmax timing cost functions group their TNS partial sums by thread count, so the returned cost (and the WNS witness path on exact ties) changes with -max_cores | *Multi-threaded by default.** There is no enable flag: `fmaxTimingCostFunction.h:234` asserts `dvuAssertRelease(numberOfThreads > 1)` outright, i.e. |
| MEDIUM | `ctssc/lazytns/ctsLazyModel.cc:4834` | 3.5 | `real` | Lazy-TNS path-group tracing picks a different algorithm when the host has more than 32 cores | Gated by three things simultaneously, all of which default to something environment-shaped: `crmResources::get().getMaxThreadCount() > 32` - `set_host_options -max_cores`, or the machine default (which I could not read; `crm.h` is outside this snapshot). |
| MEDIUM | `ctssch/ctsTimingDrivenTransitionTargets.h:181` | 3.6 | `real` | compareTimInfo is not a strict weak ordering: arbitrary tie order in _sinkPinTimingInfoSet drives the 'N worst sinks' max_transition selection | Entry point: `ctsSch::runTDSinkTargetTransitionRecipe()` (`ctssch/ctsSch.cc:3733-3749`), which builds the manager and runs `_treeStructures->forEachTreeNode(false /*bottomUp*/, false /*exception*/, *_tdSinkTargetTran)`. |
| MEDIUM | `ctsutil/ctsUtils.cc:57` | 3.6 | `real` | The LEQ-order determinism guard `sortModulesByName()` is a no-op at its option's default, while its consumer drops arc-delay ties by input order | `cts.optimize.use_module_name_to_sort_libs` — **HIDDEN, default `false`**. When `true`, `sortModulesByName()` sorts by `getFullName()` and the exposure closes. |

---

## Critical Background: ID System

> See `references/id-system.md` for the full reference. Summary below.

```
+-------------------------+--------+--------------------------------------------------+
| Property                | Value  | Implication                                      |
+-------------------------+--------+--------------------------------------------------+
| getId() / getIdLong()   | O(1)   | Cheap - inline arithmetic only                   |
| getObjectType()         | O(1)   | Cheap - single lookup                            |
| getContextElement()     | O(1)   | Cheap - pointer retrieval                        |
| getFullName()           | O(d)   | EXPENSIVE - O(hierarchy depth) + string alloc    |
| getPathName()           | O(d)   | EXPENSIVE - O(hierarchy depth) + string alloc    |
+-------------------------+--------+--------------------------------------------------+
```

The gold-standard tools are:

- `ndmObjectHandleNS::compareObjPtr` — stable comparator for pointer keys.
- `dosContainer::keyHash` — context-chain-aware stable hasher.
- `ndmPtrMap<K,V>` — pointer-keyed map that uses the comparator above.
- `hySet<T, Cmp>` / `hyMap<K, V, Cmp>` (`util/export/hySet.h`,
  `util/export/hyMap.h`) — project-preferred deterministic AVL+linked-list
  container that **preserves insertion order** for iteration and is ~16%
  faster than `std::set::find()` on string keys. Use when iteration order
  must equal insertion order; use `compareObjPtr` instead when you need
  ID-stable ordering across runs with non-deterministic insertion sequence.

---

## Findings

## HIGH Severity Issues

_6 finding(s)._

### Pattern 1.2 — std::set / std::map with pointer key, default comparator  (×2)

### Issue 1.2.1 — Auto balance-point launch-chain processing order comes from a pointer-keyed std::map; std::sort tie-break is address-derived and feeds setCtsDelayPoint()

- **File:** `ctsmisc/ctsAutoBalancePoint.cc:656` (col 1)
- **Pattern:** 1.2 — std::set / std::map with pointer key, default comparator
- **Category:** container
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 1

**Why this is non-deterministic:**

`ctsAutoBalancePoint::generateBalancePointsBwdChain()` accumulates one entry per ICG *launch* term into `ltermMap`, a `std::map<ndmTerm*, std::pair<float, const cstrScenario*> >` with the default `std::less<ndmTerm*>`, so the map is ordered by raw pointer address.

The map is snapshotted into `ltermVec` in that address order (lines 811-814) and then sorted with `std::sort(ltermVec.begin(), ltermVec.end(), termCompare)` (line 815). `termCompare` (line 510) compares **only** `term1.second.first < term2.second.first`, i.e. the float `targetOffset`. It is therefore not a total order: every group of launch terms that share the same offset (extremely common - many terms land on the same clamped value, and `targetOffset` starts at a shared initial value) is left in an order that `std::sort` derives from the address-ordered input. `std::sort` is additionally not stable, so even the relative order of a tie group is unspecified.

That order is not cosmetic. Launch terms are processed sequentially and `getOffSetForLaunchChainIterative()` mutates the shared `_sinkInfoMap`; a later launch chain reads the offset a previous chain stored (`if(info._offSet != 0.0)`, line 1022 / line 1262) and takes a different branch because of it. The accumulated `_sinkInfoMap` is then walked and committed to the constraint database via `cstrMode::setCtsDelayPoint()` (line 933). Different heap layouts therefore produce different balance-point sets and values on the same design.

**Realness:** `real`

**Downstream observability proof:**

1. **Declaration** - `ctsmisc/ctsAutoBalancePoint.cc:656`: `ltermMap` is `std::map<ndmTerm*, std::pair<float, const cstrScenario*> >`, default `std::less<ndmTerm*>` => key order == address order.
2. **Population** - `ctsmisc/ctsAutoBalancePoint.cc:794-806`: one entry per ICG launch term (`ltermMap.insert` / `ltermMap[term].first = targetOffset`).
3. **Order escapes the map** - `ctsmisc/ctsAutoBalancePoint.cc:811-814`: the map is copied into `ltermVec` by iterating `ltermMap.begin()..end()`, i.e. in address order.
4. **Sort does not canonicalize** - `ctsmisc/ctsAutoBalancePoint.cc:815` calls `std::sort(..., termCompare)`; `ctsmisc/ctsAutoBalancePoint.cc:510-513` shows `termCompare` keys only on the float offset, so all equal-offset launch terms retain an address-derived (and, because `std::sort` is unstable, unspecified) permutation.
5. **Order-sensitive consumer** - `ctsmisc/ctsAutoBalancePoint.cc:816-853` iterates `ltermVec` and calls `getOffSetForLaunchChainIterative(term, avoidSinks, ...)` (`ctsmisc/ctsAutoBalancePoint.cc:1516`).
6. **Shared mutable state** - that traversal runs `ctsRegVisitor::visitNode*`, which writes `(*_sinkInfoMap)[term]._offSet` at `ctsmisc/ctsAutoBalancePoint.cc:972`, `:1043`, `:1049`, `:1060` and `:1185`.
7. **Cross-term feedback** - `ctsmisc/ctsAutoBalancePoint.cc:1022` (and the twin at `:1262`) reads the value a *previous* launch chain stored (`if(info._offSet != 0.0)`) and then takes a different branch: `achievedOffset = nwmathFloat::chooseLesser(targetOffset, -info._offSet)` (`:1034`) vs. `info._offSet = -targetOffset` (`:1043`/`:1049`). So processing order changes the computed offsets, not just the order in which they are computed.
8. **Observable sink (database write)** - `ctsmisc/ctsAutoBalancePoint.cc:878-935` walks `_sinkInfoMap`, drops entries with `offSet <= _minStageDelay * 1.5` (`ctsmisc/ctsAutoBalancePoint.cc:885`, a threshold test on the order-dependent value), and commits the survivors with `clock.getMode().setCtsDelayPoint(...)` at `ctsmisc/ctsAutoBalancePoint.cc:933`. CTS delay points (balance points) are persisted constraints that drive clock-tree latency balancing.
9. **Secondary sink (report)** - `printBalancePoint(clock, sink, primaryCorner, values)` at `ctsmisc/ctsAutoBalancePoint.cc:936` writes the auto-balance-point report file opened at `ctsmisc/ctsAutoBalancePoint.cc:253`, and the count printed at `ctsmisc/ctsAutoBalancePoint.cc:940` varies with it.

**Controls / gating:**

- **Flow entry**: `ctsAutoBalancePoint::run()`-style entry points at `ctsmisc/ctsAutoBalancePoint.cc:170-175` and `ctsmisc/ctsAutoBalancePoint.cc:255-259`.
- **C++ guard**: `_session->getOpt().getDebugBoolSetting("enable_auto_balance_points_bwd_chain", true)` at `ctsmisc/ctsAutoBalancePoint.cc:172` and `:256`. The default is **`true`**, so the affected `generateBalancePointsBwdChain()` path - not the legacy `generateBalancePoints()` - is the one that runs out of the box. Setting that debug bool to `false` routes around this finding.
- **Secondary guard**: `enable_auto_balance_points_bwd_chain_use_slack` (`ctsmisc/ctsAutoBalancePoint.cc:852`, default `true`) picks `visitNode` vs `visitNodeNoSlack`; both write `info._offSet`, so it does not mitigate.
- **Data condition**: needs >= 2 ICG launch terms that share a `targetOffset` value. `_minStageDelay * 1.5` (`ctsmisc/ctsAutoBalancePoint.cc:885`) is the filter that converts a small numeric wobble into a present/absent balance point.
- No `getAppOption`/`appOption` string gates this path; it is a `getDebugBoolSetting` (CTS debug-setting registry), which is why it is on by default.

**Performance-aware fix direction:**

`ltermMap` is only ever reached through `find()` / `operator[]` / `insert()` in the build loop, so changing its comparator does not change algorithmic complexity: it stays an O(log N) red-black tree either way. `ndmObjPtrCmpType` (= `ndmObjectHandleNS::compareObjPtr`) is a handle-id comparison rather than a raw pointer compare, so each node visit costs one extra indirection - negligible against the timer queries already performed per launch term in the same loop (`getOffSetLimit`, `getPathDelay`).

Version A adds nothing at all: `ltermVec` is already materialised and already sorted at line 815; only the comparator body changes. No new allocation, no new copy, no sorting inside an inner loop. N here is the number of ICG launch terms, orders of magnitude smaller than the sink count.

**Runtime benchmarking is not needed.** **QoR benchmarking IS needed**: the fix intentionally changes the processing order, so committed balance points will move relative to today's (arbitrary) baseline. Expect a QoR delta on the first run and validate that it is neutral on average rather than expecting bit-identical results against the old binary.

**Additional occurrences of the same root cause:**

- {'file': 'ctsmisc/ctsAutoBalancePoint.cc', 'line': 811, 'note': 'the iteration that lets the address order escape into ltermVec'}
- {'file': 'ctsmisc/ctsAutoBalancePoint.cc', 'line': 657, 'note': 'termIcgMap, same pointer-key defect; consumed only as a set union into avoidSinks (line 850) so latent on its own, but should be fixed together with ltermMap'}
- {'file': 'ctsmisc/ctsAutoBalancePoint.cc', 'line': 658, 'note': 'icgDownstreamMap, same pointer-key defect; lookup-only at line 849, fix together'}

**Current code:**

```cpp
  654 |   cstrDesign design = infra.getCstrDesign();
  655 |   cstrCorner primaryCorner = getPrimaryCorner();
> 656 |   std::map<ndmTerm*, std::pair<float, const cstrScenario*> > ltermMap;   <== pointer key, default std::less
  657 |   std::map<ndmTerm*, termSetType> termIcgMap;
  658 |   std::map<ndmTerm*, termSetType> icgDownstreamMap;
...
  794 |         if(ltermMap.find(term) == ltermMap.end()) {
  795 |           ltermMap.insert (std::pair<ndmTerm*,std::pair<float, const cstrScenario*> >(term, std::pair<float, const cstrScenario*>(targetOffset, scenario)));
...
  800 |           if(ltermMap[term].first > targetOffset) {
  801 |             ltermMap[term].first = targetOffset;
  802 |             ltermMap[term].second = scenario;
...
  810 |   std::vector<std::pair<ndmTerm*, std::pair<float, const cstrScenario*> > > ltermVec;
> 811 |   for (std::map<ndmTerm*, std::pair<float, const cstrScenario*> >::iterator it = ltermMap.begin();
  812 |       it!=ltermMap.end(); ++it) {
  813 |     ltermVec.push_back(*it);            <== snapshot taken in ADDRESS order
  814 |   }
> 815 |   std::sort(ltermVec.begin(), ltermVec.end(), termCompare);   <== partial key only; ties keep address order
  816 |   for (std::vector<std::pair<ndmTerm*, std::pair<float, const cstrScenario*> > >::iterator it=ltermVec.begin();
  817 |       it!=ltermVec.end(); ++it) {
  819 |     ndmTerm* term = it->first;
  820 |     float targetNoffset = it->second.first;
...
  853 |     getOffSetForLaunchChainIterative(term, avoidSinks, latchGraph, targetNoffset, achievedOffset, scenario, 0, useSlack);

  -- the comparator --
  510 | bool termCompare(std::pair<ndmTerm*, std::pair<float, const cstrScenario*> > term1, std::pair<ndmTerm*, std::pair<float, const cstrScenario*> > term2)
  511 | {
> 512 |   return term1.second.first < term2.second.first;   <== no tie-break on the term
  513 | }

  -- the sink --
  878 |   for (std::map<ndmTerm*, sinkInfo, ndmObjPtrCmpType>::iterator siIter = _sinkInfoMap.begin();
  879 |        siIter != _sinkInfoMap.end(); ++siIter) {
  880 |     ndmTerm* sink = siIter->first;
  881 |     float offSet = siIter->second._offSet;
...
  885 |     if (offSet <= _minStageDelay * 1.5) {
  889 |       continue;
> 933 |       bool overwrite = clock.getMode().setCtsDelayPoint(clock.getId(), sink, primaryCorner.getId(),
  934 | 						values, elrfFloatValues(), clock.getFileLineRef(), true /*isInternal*/);
```

**Suggested fix:**

_Site-specific fix variants were not provided; showing the generic pattern fix template instead._

**Option 1 (preferred for ndm objects) — use `ndmPtrMap`:**
```cpp
#include "ndmutil/ndmPtrMap.h"
ndmPtrMap<T*, V> myMap;   // already uses dosContainer::keyCompare
```

**Option 2 — explicit comparator:**
```cpp
std::set<T*, ndmObjectHandleNS::compareObjPtr> mySet;
std::map<T*, V, ndmObjectHandleNS::compareObjPtr> myMap;
```

**Option 3 — custom comparator for non-ndm types:**
```cpp
struct StableCmp {
    bool operator()(const T* a, const T* b) const {
        if (a == b) return false;
        if (!a) return true;
        if (!b) return false;
        if (a->getId() != b->getId()) return a->getId() < b->getId();
        return a->getObjectType() < b->getObjectType();
    }
};
std::set<T*, StableCmp> mySet;
```

**Why this fix:**

This is the only candidate in the slice where a pointer-ordered container feeds an order-sensitive *algorithm* (not a cleanup loop, not a membership test, not a log line) and ends in a database write. The three properties that make it real are all present in source: (a) the order escapes the map into a vector, (b) the sort key is a strict subset of the identity so ties survive, and (c) the loop body mutates state that the next iteration reads (`info._offSet != 0.0` at line 1022). Remove any one of the three and it would be latent.

HIGH is the right severity: `setCtsDelayPoint` writes persisted CTS constraints that drive latency balancing, the `offSet <= _minStageDelay * 1.5` filter can flip a balance point from present to absent, and the guard defaults to enabled.

**False-positive check:**

- **Comparator**: verified `ltermMap` is declared with **two** template arguments at line 656 - no third comparator argument. Contrast with `_sinkInfoMap` at `ctsmisc/ctsAutoBalancePoint.h:109` and `primaryCornerDelays` at `ctsmisc/ctsExclude.cc:634`, which *do* pass `ndmObjPtrCmpType` and which I dismissed for that reason.
- **Iterator spelling caveat checked**: in libstdc++ `std::map<K,V,C>::iterator` is `_Rb_tree_iterator<pair<const K,V>>` independent of `C`, so a two-argument iterator spelling does *not* prove a default comparator. I confirmed the finding against the **declaration** at line 656, not against the iterator spelling at line 811.
- **Not `#if 0`/commented**: lines 656 and 811-815 are live code; the nearby `/* purecov: begin deadcode */` block is at lines 860-875 (the `_applyLimit` loop), which I did **not** use as evidence for anything, and which is *after* the loop in question.
- **Not neutralized**: the `std::sort` at line 815 was the first thing I suspected of canonicalizing this. Reading `termCompare` at line 510 shows it keys only on the float, so the sort is not a canonicalization.
- **Not a test harness**: `ctsmisc/ctsAutoBalancePoint.cc` is product code; not under `test/`, not `*Test.cc`.
- **Reachability**: two live call sites at `ctsmisc/ctsAutoBalancePoint.cc:173` and `:257`, default-on guard.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctsmisc/ctsAutoBalancePoint.cc`
- **Primary logic (annotate):** `ltermMap` declaration at `:656` and 7 of 13 lines in the window belong to CL `3007535`.
- **Describe summary:** CL `3007535` is a **bulk branch merge** by `nwtnmgr@icc2_main_merge`, 2015-11-10, *"Merge from //synopsys/nwtn/k2015.06/sp to //synopsys/nwtn/main/dev using changelist number 3001507"*.
- **CMT chain:** resolved to CL `3001507` by **`lippens`**, 2015-11-04 — *"CBF 1604. Fix for PV crash star 9000967056"*.
- **Notes:** attribution here is **low confidence**. CL `3001507` is a PV crash fix in `msClockDrivers`, which does not obviously correspond to this balance-point code, so the bulk merge has almost certainly flattened the real authorship. Run `p4 filelog -i //...ctsAutoBalancePoint.cc` and annotate the pre-merge branch revision before assigning this one.

---

### Issue 1.2.2 — Per-hierarchy tap insertion order derives from std::map<ndmHier*> because compareHierDepth is only a depth comparison, not a total order

- **File:** `mscts/drivers/msDrivers.cc:8189` (col 1)
- **Pattern:** 1.2 — std::set / std::map with pointer key, default comparator
- **Category:** container
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 1

**Why this is non-deterministic:**

`msClockDrivers::insertInstsMVAware()` builds `std::map<ndmHier *, msDriverLoadInfo> inputParamMap` (msDrivers.cc:8189) keyed on `ndmHier*` with the default `std::less<ndmHier*>`, so the map is ordered by raw hierarchy-object address and its iteration order changes from run to run.

The code is *aware* of this: `convertToVector()` copies the map into a vector and sorts it, and the call site carries the comment `// convert map to vector for deterministic behaviour` (msDrivers.cc:8192). The mitigation is incomplete. `compareHierDepth` (msDrivers.cc:8136-8143) returns `elem1.first->getDepthFromTop() < elem2.first->getDepthFromTop()` and nothing else, so it is a strict weak ordering with large equivalence classes: every uncommitted hierarchy at the same depth from top (i.e. all sibling physical blocks, which is the normal case) compares equal. `std::sort` is not stable, so within each equal-depth class the surviving order is a permutation of the address-derived map order. The net effect is that the relative order of sibling uncommitted hierarchies is still non-deterministic after the 'deterministic' conversion.

**Realness:** `real`

**Downstream observability proof:**

Two independent observable sinks, both reached from the same ND iteration order.

**Hop 1 - declaration.** `std::map<ndmHier *, msDriverLoadInfo> inputParamMap` at `mscts/drivers/msDrivers.cc:8189`; filled by `segrigateLoadAndBufForHier()` (`mscts/drivers/msDrivers.cc:7998`, writes at `:8011` and `:8112` via `inputParamMap[hier]`).

**Hop 2 - ND iteration.** `msClockDrivers::convertToVector()` iterates the map at `mscts/drivers/msDrivers.cc:8124` and pushes into `infoInVector`. The subsequent `std::sort(infoInVector.begin(), infoInVector.end(), compareHierDepth)` at `mscts/drivers/msDrivers.cc:8131` only orders by `ndmHier::getDepthFromTop()` (`mscts/drivers/msDrivers.cc:8140-8142`), so hierarchies at equal depth retain an unstable, address-derived order.

**Hop 3a - database mutation sink.** `mscts/drivers/msDrivers.cc:8233` calls `insertInstsMVAwareForOneHier(cfgsIn, locsIn, namesIn, drvTerms, loadsIn, isLeaf, nDrv, nextLevelLoads, failed, assignLoads, unCommittedHier, NULL, topToSubBlock)` once per hierarchy, in that order. That path creates the tap/repeater instances and the nets that connect them; net and port names are handed out from the shared running counter `_nameCounters[prefix]` (read at `mscts/drivers/msDrivers.cc:10883`, written back at `mscts/drivers/msDrivers.cc:10923` inside `msClockDrivers::connectTerms`, declared `NameCounterTable _nameCounters` at `mscts/drivers/msDrivers.h:1268`). Swapping two equal-depth hierarchies therefore swaps which physical block gets which generated instance/net name, and changes the order in which legal placement sites are claimed.

**Hop 3b - algorithmic first-match sink.** `mscts/drivers/msDrivers.cc:8216-8232` implements orphan-load adoption: hierarchies with no buffer locations are parked in `noBuffHierInfo` (`mscts/drivers/msDrivers.cc:8217`), and their loads are merged into `loadsIn` of the **first** subsequently visited hierarchy that satisfies `unCommittedHier->contains(noBuffHier)` (`mscts/drivers/msDrivers.cc:8223`), after which the entry is erased (`mscts/drivers/msDrivers.cc:8227`). When more than one equal-depth candidate contains the orphan hierarchy, the winner is decided purely by the ND order, so the *load-to-driver assignment itself* changes run to run. The `(index == numHier-1)` fallback also depends on which hierarchy happens to land last.

**Hop 4 - propagation.** Loads that are not adopted flow into `nextLevelLoads` (`mscts/drivers/msDrivers.cc:8240`), which becomes the load set for the next H-tree level, so the divergence compounds down the tree.

**Controls / gating:**

Reached from `msClockDrivers::insertInstsMVAware()`; the ND branch is taken at `mscts/drivers/msDrivers.cc:8184`:

```cpp
if (_msgtsOptions.getUncommittedBlockInfo().empty() || !isLeaf || section) {
  l_rc = insertInstsMVAwareForOneHier(...);        // single-hier path, not affected
} else {
  std::map<ndmHier *, msDriverLoadInfo> inputParamMap;   // <-- ND path
```

So all three of the following must hold:
1. `_msgtsOptions.getUncommittedBlockInfo()` is non-empty - the design has uncommitted physical blocks (multi-level physical hierarchy / MLPH and MIM flows). Populated from `msgtsOptions`; the related app option is `enableMLPHFlow` (`mscts/msui/msuiAppOptions.cc:3990`, `mscts/msui/msuiAppOptions.h`).
2. `isLeaf == true` - leaf-level (tap) insertion.
3. `section == NULL` - not running the section-based H-tree path.

Data condition for the ND to actually change the answer: **two or more uncommitted hierarchies with the same `getDepthFromTop()`**, i.e. sibling physical blocks. This is the normal topology, not a corner case. With exactly one uncommitted hierarchy, or with all hierarchies at distinct depths, the sort is sufficient and the result is stable.

No dedicated `getAppOption` guard exists for this code; it is on by data, not by switch.

**Performance-aware fix direction:**

`inputParamMap` is keyed by hierarchy, not by pin, so its cardinality is the number of uncommitted physical blocks - tens at most, not the millions of pins that make CTS hot. All three fixes below are O(H log H) on that tiny set and run once per H-tree level, outside any inner loop. No lookup complexity changes: the map is only used with `operator[]` (`mscts/drivers/msDrivers.cc:8011`, `:8112`) and a single full traversal, so replacing `std::less<ndmHier*>` with an ID comparator keeps the same O(log H) insert/lookup and adds only a cheap `getIdLong()` load per comparison instead of a pointer compare.

`msDriverLoadInfo` is a value struct holding vectors of locs/cfgs/names/loads, so Version A's key snapshot must copy only the `ndmHier*` keys (8 bytes each), never the values - `infoInVector` already copies the values by value today (`mscts/drivers/msDrivers.cc:8127`), so Version B/C are strictly cheaper than the status quo.

No runtime benchmarking is required for the fix itself. **QoR benchmarking is required**, because the fix deliberately changes the visit order and therefore changes tap naming, site claiming and orphan-load adoption on MLPH designs. Expect a QoR delta on the first run after the fix; compare against baseline on a set of multi-block MLPH testcases and confirm the new result is stable across repeated identical runs (that stability is the point of the fix).

**Additional occurrences of the same root cause:**

- {'file': 'mscts/drivers/msDrivers.cc', 'line': 7998, 'note': 'msClockDrivers::segrigateLoadAndBufForHier() out-parameter - the producer that fills the map (writes at :8011 and :8112).'}
- {'file': 'mscts/drivers/msDrivers.cc', 'line': 8121, 'note': 'msClockDrivers::convertToVector() in-parameter - this is the function that performs the ND traversal at :8124.'}
- {'file': 'mscts/drivers/msDrivers.h', 'line': 868, 'note': 'Declaration of segrigateLoadAndBufForHier(); must change with the definition.'}
- {'file': 'mscts/drivers/msDrivers.h', 'line': 870, 'note': 'Declaration of convertToVector(); must change with the definition.'}

**Current code:**

```cpp
mscts/drivers/msDrivers.cc
  8187 |   } else {
  8188 |     // For each such hier, segrigate locs=>locsIn, cfgs=>cfgsIn, names=>namesIn, loads=>loadsIn
> 8189 |     std::map<ndmHier *, msDriverLoadInfo> inputParamMap;
  8190 |     ndmTerm* topLevelDrvTerm = getTopLevelDrvTerm(drvTerms);
  8191 |     segrigateLoadAndBufForHier(topLevelDrvTerm, locs, cfgs, names, loads, inputParamMap);
  8192 |     // convert map to vector for deterministic behaviour
  8193 |     std::vector<std::pair<ndmHier*, msDriverLoadInfo> >infoInVector ;
  8194 |     convertToVector(inputParamMap, infoInVector);

  8119 | void 
  8120 | msClockDrivers::convertToVector(
  8121 |   const std::map<ndmHier*, msDriverLoadInfo > &inputParamMap, 
  8122 |   std::vector<std::pair<ndmHier*, msDriverLoadInfo > > &infoInVector)
  8123 | {
> 8124 |   for (auto &itr : inputParamMap) {          // <-- ND map iteration
  8127 |     std::pair<ndmHier*, msDriverLoadInfo > vecElem(itr.first, itr.second);
  8128 |     infoInVector.push_back(vecElem);
  8129 |   }
  8130 |   if (infoInVector.size() > 1) {
> 8131 |     std::sort(infoInVector.begin(), infoInVector.end(), compareHierDepth);   // <-- partial key
  8132 |   }
  8133 | }

  8136 | msClockDrivers::compareHierDepth(
  8137 |   const std::pair<ndmHier*, msDriverLoadInfo> elem1,
  8138 |   const std::pair<ndmHier*, msDriverLoadInfo> elem2)
  8139 | {
  8140 |   int depth1 = elem1.first->getDepthFromTop();
  8141 |   int depth2 = elem2.first->getDepthFromTop();
> 8142 |   return (depth1<depth2);                    // ties keep ND order; std::sort is unstable
  8143 | }

  8199 |     for (auto &itr : boost::adaptors::reverse(infoInVector)) {
  8200 |       ndmHier *unCommittedHier = itr.first;
  8216 |       if (locsIn.empty()) {
  8217 |         noBuffHierInfo.push_back(itr);
  8218 |       } else {
  8219 |         if (noBuffHierInfo.size()) {
  8221 |           while (noBuffVecIter != noBuffHierInfo.end()) {
  8222 |             ndmHier *noBuffHier = noBuffVecIter->first;
> 8223 |             if (unCommittedHier->contains(noBuffHier) || (index == numHier-1)) {  // FIRST-MATCH
  8226 |               loadsIn.insert(orphanLoads.begin(), orphanLoads.end());
  8227 |               noBuffVecIter = noBuffHierInfo.erase(noBuffVecIter);
  8228 |             } else {
  8229 |               ++noBuffVecIter;
  8230 |             }
  8231 |           }
  8232 |         }
> 8233 |         l_rc &= insertInstsMVAwareForOneHier(cfgsIn, locsIn, namesIn, drvTerms, loadsIn, isLeaf,
       |                    nDrv, nextLevelLoads, failed, assignLoads, unCommittedHier, NULL, topToSubBlock);
  8235 |       ++index;
  8236 |     } // end for
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): make the existing canonicalisation a total order.
// Leave inputParamMap exactly as it is; only strengthen compareHierDepth so
// that equal-depth hierarchies get a stable, address-independent tie-break.
// mscts/drivers/msDrivers.cc:8136
bool
msClockDrivers::compareHierDepth(
  const std::pair<ndmHier*, msDriverLoadInfo> elem1,
  const std::pair<ndmHier*, msDriverLoadInfo> elem2)
{
  int depth1 = elem1.first->getDepthFromTop();
  int depth2 = elem2.first->getDepthFromTop();
  if (depth1 != depth2) {
    return (depth1 < depth2);
  }
  // Tie-break on a stable database id so that sibling uncommitted hierarchies
  // at the same depth are visited in the same order every run.
  return (elem1.first->getIdLong() < elem2.first->getIdLong());
}
```

**Version B (robust):**

```cpp
// Version B (robust): supply the project deterministic comparator on the map
// itself, so the container is never in address order to begin with.
// mscts/drivers/msDrivers.h:868-871
    void segrigateLoadAndBufForHier(
                     ndmTerm                                 *drvTerm,
                     const std::vector<ndmCoord>             &locs,
                     const std::vector<msConfigurationItem*> &cfgs,
                     const std::vector<std::string>          &names,
                     const termSetType                       &loads, //LINTER_BYPASS
                     std::map<ndmHier *, msDriverLoadInfo, ndmObjPtrCmpType> &inputParamMap);
    void convertToVector(
                     const std::map<ndmHier*, msDriverLoadInfo, ndmObjPtrCmpType> &inputParamMap,
                     std::vector<std::pair<ndmHier*, msDriverLoadInfo> > &infoInVector);

// mscts/drivers/msDrivers.cc:8189
    std::map<ndmHier *, msDriverLoadInfo, ndmObjPtrCmpType> inputParamMap;
    ndmTerm* topLevelDrvTerm = getTopLevelDrvTerm(drvTerms);
    segrigateLoadAndBufForHier(topLevelDrvTerm, locs, cfgs, names, loads, inputParamMap);

// ndmObjPtrCmpType is already typedef'd to ndmObjectHandleNS::compareObjPtr in
// ctsutil/ctsTypes.h:63 and is in scope in msDrivers.cc. Keep the existing
// std::sort by depth, and also give it the total order from Version A so the
// depth grouping cannot re-introduce ties.
```

**Version C:**

```cpp
// Version C: re-key by a stable id, so no comparator is needed at all.
// mscts/drivers/msDrivers.cc:8189
    std::map<ndmObjectId, msDriverLoadInfo> inputParamById;
    std::map<ndmObjectId, ndmHier *>        idToHier;
    ndmTerm* topLevelDrvTerm = getTopLevelDrvTerm(drvTerms);
    segrigateLoadAndBufForHier(topLevelDrvTerm, locs, cfgs, names, loads,
                               inputParamById, idToHier);

    // convert map to vector; id-keyed map is already in a run-stable order
    std::vector<std::pair<ndmHier*, msDriverLoadInfo> > infoInVector;
    infoInVector.reserve(inputParamById.size());
    for (const auto &itr : inputParamById) {
      infoInVector.push_back(std::make_pair(idToHier[itr.first], itr.second));
    }
    if (infoInVector.size() > 1) {
      std::sort(infoInVector.begin(), infoInVector.end(), compareHierDepth);
    }

// Callers write inputParamById[hier->getIdLong()] and idToHier[hier->getIdLong()] = hier
// in place of inputParamMap[hier] at msDrivers.cc:8011 and :8112.
```

**Why this fix:**

**Recommend Version A plus Version B together**, with Version A as the must-have.

Version A is a four-line change to a single static comparator, it is the smallest possible diff, and it fixes the actual defect: the author already decided that depth order is the intended visit order and already wrote the snapshot-and-sort idiom; the only thing missing is a tie-break. It also cannot change behaviour on designs that were already deterministic (distinct depths), which keeps the QoR blast radius as small as this fix can be.

Version B is worth adding on top because it removes the address-ordered container entirely, so any *future* traversal of `inputParamMap` added by someone who does not know about `convertToVector` is deterministic by construction. It uses `ndmObjPtrCmpType`, the idiom already used everywhere else in this file (for example `std::set<ndmModule*, ndmObjPtrCmpType>` at `mscts/drivers/msDrivers.cc:2234-2238` and `std::map<ndmTerm*, std::vector<ndmInst*>, ndmObjPtrCmpType>` at `mscts/drivers/msDrivers.cc:4542`), so it needs no new infrastructure and no reviewer education. On its own, though, Version B is *not* sufficient: the unstable `std::sort` by depth would still scramble equal-depth siblings, which is why it must be paired with A.

Version C is not recommended here. It touches three functions and two call sites, forces a parallel `idToHier` map, and buys nothing over B on a container of this size.

**False-positive check:**

- Confirmed the key is a raw pointer and the comparator is defaulted: `std::map<ndmHier *, msDriverLoadInfo>` at `mscts/drivers/msDrivers.cc:8189` and the matching declarations at `mscts/drivers/msDrivers.h:868` and `:870`. No third template argument anywhere, and `ndmHier` is not one of the types covered by the `TYPEDEF_CONTAINER_1(std::map, ...)` stable-comparator typedefs in `ctsutil/ctsTypes.h:103-137`.
- Checked whether the existing mitigation already neutralises it. It does not: I read `compareHierDepth` in full (`mscts/drivers/msDrivers.cc:8136-8143`) and it compares only `getDepthFromTop()`. `std::sort` (not `std::stable_sort`) is used at `:8131`, so equivalent elements are reordered arbitrarily. This is the reason I kept the finding despite the `// convert map to vector for deterministic behaviour` comment at `:8192` - that comment is a statement of intent, not a proof.
- Ruled out dead code: the enclosing `msClockDrivers::insertInstsMVAware()` is a live, non-`#if 0` member, and neither it nor `convertToVector`/`segrigateLoadAndBufForHier` sits behind any `#if`/`#ifdef`/build macro. There is no `purecov` marker on this range either.
- Ruled out an order-insensitive sink. I checked whether the loop body only writes into stable containers (which is how I dismissed the neighbouring `unassignLoads` map at `mscts/drivers/msDrivers.cc:4204`, whose only traversal at `:4344` feeds the `ndmObjPtrCmpType`-ordered `termSetType _unassignedLoads` declared at `mscts/drivers/msDrivers.h:1285`). It does not: this loop performs instance insertion at `mscts/drivers/msDrivers.cc:8233` and a genuine first-match selection at `:8223`.
- Verified the name counter really is shared and order-dependent rather than derived from the object: `_nameCounters[prefix]` is read at `mscts/drivers/msDrivers.cc:10883` and written back at `:10923`, so it is sequence-dependent state, not a function of the hierarchy.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/mscts/drivers/msDrivers.cc`
- **Line drift:** this file moved ~+255 lines between the audited snapshot and depot `main`; the snapshot's `:8189` region maps to depot `:8447`, and `compareHierDepth` maps to depot `:8386-8395`.
- **Primary logic (annotate):** CL `6890358` owns both the `std::sort(..., compareHierDepth)` call and the `// convert map to vector for deterministic behaviour` comment.
- **Describe summary:** CL `6890358` by **`sumanc`**, 2021-09-17 — *"Handle hierarchy with no buufer. PRS NA"*.
- **CMT chain:** `[ORIG_CLIENT:sumanc-nwtn-21.06-sp][CMT][merge from //synopsys/nwtn/s/dev@6890245]` — original authoring user is **`sumanc`**.
- **Notes:** the same CL introduced the determinism intent *and* the incomplete depth-only comparator, so the author of the mitigation is the right reviewer for completing it.

---

### Pattern 1.4 — Pointer-based hash functors  (×1)

### Issue 1.4.1 — sclkCornerHash hashes ctoSclkBag* address: load-partition weighted late-margin sum is order-dependent and reorders buffering sinks

- **File:** `ctscto/ctosc/ctoscGlobal.h:274` (col 1)
- **Pattern:** 1.4 — Pointer-based hash functors
- **Category:** hash
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 1

**Why this is non-deterministic:**

`sclkCornerHash` folds the raw address of `ctoSclkBag* pair.bag` into the hash of the `sclkCorner` key. Nine containers in ctscto use this functor. Eight of them are pure lookup caches, but `ctoscLoadPartition::_sinkDelayMapBySclk` and `_sinkDelayTargetMapBySclk` are *iterated*, and the loop bodies perform a non-associative floating-point accumulation:

```
margins[sink] += (lmargin * weight);
weights[sink] += weight;
```

The summation is taken over every `{sclkBag, corner}` (scc) that contains the sink. Because the outer container is an `unordered_map` whose bucket assignment is derived from the `ctoSclkBag*` address, the order in which the per-scc terms are added to `margins[sink]` changes from run to run. `float` addition is not associative, so the accumulated value differs in the low-order bits.

That value is not merely printed. It is the sort key for `_sinks` (`ctoscLoadPartition::init`, line 89-135), which is the ordered list of loads the GLS buffering engine partitions. When two sinks have avg-weighted margins that differ only by the accumulation error, their relative order flips, which changes `_spSinkPos`, the partition boundaries, and ultimately which loads end up under which inserted buffer.

**Realness:** `real`

**Downstream observability proof:**

Full chain, one hop per line:

1. `ctscto/ctosc/ctoscGlobal.h:274` - `sclkCornerHash::operator()` mixes `std::hash<ctoSclkBag*>()(pair.bag)` (raw address) into the hash.
2. `ctscto/ctosc/ctoscLoadPartition.h:172,173` - `_sinkDelayMapBySclk` / `_sinkDelayTargetMapBySclk` are `std::unordered_map<sclkCorner, ..., sclkCornerHash>`, so bucket index and therefore iteration order follow the bag address.
3. `ctscto/ctosc/ctoscLoadPartition.cc:773,777` - both maps are populated over the deterministic `ctoSclkMgr::sclkCornerIterator`, so *content* is deterministic; only *iteration order* is not.
4. `ctscto/ctosc/ctoscLoadPartition.cc:597` and `:654` - the two maps are iterated with a range-for.
5. `ctscto/ctosc/ctoscLoadPartition.cc:628-629` and `:677-678` - each iteration does `margins[sink] += (lmargin * weight)` and `weights[sink] += weight`. This is a sum of per-scc `float` terms whose addition order is exactly the ND iteration order. Non-associative FP accumulation -> value differs run to run.
6. `ctscto/ctosc/ctoscLoadPartition.cc:637` / `:686` - `avgWeightedLmargin[sink] = wlmargin / tweight` propagates the perturbed sum.
7. `ctscto/ctosc/ctoscLoadPartition.cc:81,85` - `ctoscLoadPartition::init()` captures both maps into `avgLateMargins` / `avgLateTargetMargins`.
8. `ctscto/ctosc/ctoscLoadPartition.cc:89-135` - `std::sort(_sinks...)` compares `avgLateTargetMargins.at(a) > avgLateTargetMargins.at(b)` (line 110) or `avgLateMargins.at(a) > avgLateMargins.at(b)` (line 119). A near-tie flips.
9. `ctscto/ctosc/ctoscLoadPartition.cc:136-155` - `std::min_element` over the reordered `_sinks` sets `_spSinkPos`.
10. `ctscto/ctosc/ctoscLoadPartition.cc:1416` - `std::copy_n(_sinks.begin(), boundary, group.begin())` turns the prefix of `_sinks` into the actual load group for a buffer-insertion solution; `:894,907,995,1146,1149,1232-1248` also index `_sinks` positionally for partition enumeration and skew cost.

Sink class: QoR-affecting selection (which loads are grouped under an inserted buffer) plus non-associative FP accumulation. Both qualify.

Note: the inner per-sink containers are `std::map<ndmTerm*, ..., ndmObjPtrCmpType>` (already stable), and `glate` uses `nwmathFloat::chooseGreater` (order-insensitive). The *only* ND contributor here is the outer `sclkCornerHash`-keyed map.

**Controls / gating:**

Reached from `ctomtBuffer::runBuffering` path, `ctscto/ctosc/ctomt/ctomtBuffer.cc:846-852`:

```
846 |   const bool useAvgLateMargin = (ctsP->getFlowType() == CTO_GSKEW) &&
847 |     ctsEnvVariable::getBool("CTOSC_LOAD_PART_USE_AVG_LATE_MARGIN", ctsP->isSolverAugLeafOnly());
848 |   part.setUseAvgLateMargin(useAvgLateMargin);
849 |   const bool useAvgTargetLateMargin = targetObj &&
850 |     (ctsP->isAdvancedSkewOpt() && (ctsP->getFlowType() == CTO_GSKEW)) &&
851 |     ctsEnvVariable::getBool("CTOSC_LOAD_PART_USE_AVG_TARGET_LATE_MARGIN", ctsP->isAdvancedSkewOpt());
852 |   part.setUseAvgTargetLateMargin(useAvgTargetLateMargin);
```

- Guards: `ctsP->getFlowType() == CTO_GSKEW` (global skew optimization).
- Env vars `CTOSC_LOAD_PART_USE_AVG_LATE_MARGIN` and `CTOSC_LOAD_PART_USE_AVG_TARGET_LATE_MARGIN` are *overrides*, not enables: their defaults are `ctsP->isSolverAugLeafOnly()` and `ctsP->isAdvancedSkewOpt()` respectively. So the path is ON by default in solver-augmented leaf-only GLS and in advanced skew-opt, which are mainstream MTCTO modes - this is not a debug-only gate.
- Data condition: needs >= 2 `{sclkBag, corner}` entries in `_sinkDelayMapBySclk` (multi-mode / multi-corner designs) and >= 2 sinks with near-equal weighted margins. Single-scc designs are immune.
- Related unaffected containers gated by the same functor: `ctoscFilter.h:349`, `ctoscGlobal.h:365` (`mapSccFloat`), `ctomtGlsProblemGenerator.h:255-257,274-277`, `ctomtXformProblem.h:381`, `ctoscLoadPartition.h:169,170` - all lookup-only today, but they are latent and a fix at the functor protects them too.

**Performance-aware fix direction:**

`ctoscLoadPartition::init()` runs once per buffering problem (per driver), not per candidate solution, so this is warm but not the innermost loop. Cost analysis of each option:

- Version A (snapshot + sort keys) adds one `std::vector<sclkCorner>` of size = number of sccs (typically 1-50, bounded by modes x corners) plus an `O(S log S)` sort, executed twice per `init()`. Negligible next to the timer queries already in the same function (`getPathDelay`, `getFlowWeight`). All `find`/`at` lookups stay `O(1)`.
- Version B (fix the hash functor) is the cheapest at runtime: it replaces one pointer hash with an ID hash of the same cost. It changes *no* container complexity - every one of the nine `sclkCornerHash` containers stays `O(1)`. This is the option I would ship.
- Version C (re-key to `std::map<sclkCornerType, ...>`) converts `O(1)` lookups to `O(log S)`. `_sinkDelayMapBySclk` is queried in `getSinkDelayBySclkCorner()` which is called from the `std::sort`/`std::min_element` comparators (lines 134, 139-152) - that is `O(N log N)` calls per problem. With S small (<= a few dozen) the log factor is tiny, but this is the only option with a real complexity change and it should be benchmarked.

Benchmarking: Version B needs no runtime benchmarking (same operation count). It *does* need QoR benchmarking, because changing the hash changes the bucket layout and therefore the iteration order, so accumulated margins will shift - the fix makes the result stable, not identical to any prior run. Run a standard MTCTO GLS skew-opt regression and compare skew/latency/buffer-count, and confirm two identical runs now produce byte-identical results.

**Additional occurrences of the same root cause:**

- `ctscto/ctosc/ctoscLoadPartition.h:172 (_sinkDelayMapBySclk declaration)`
- `ctscto/ctosc/ctoscLoadPartition.h:173 (_sinkDelayTargetMapBySclk declaration)`
- `ctscto/ctosc/ctoscLoadPartition.cc:597 (iteration in getAvgWeightedLateMargin)`
- `ctscto/ctosc/ctoscLoadPartition.cc:654 (iteration in getAvgWeightedLateTargetMargin)`

**Current code:**

```cpp
ctscto/ctosc/ctoscGlobal.h
    271 | // @brief custom hash function for sclkCorner
    272 | struct sclkCornerHash {
    273 |   std::size_t operator() (sclkCorner pair) const {
>   274 |     return std::hash<ctoSclkBag*>()(pair.bag) ^
    275 |       boost::hash<cstrCornerId>()(pair.corner.getId());
    276 |   }
    277 | };

ctscto/ctosc/ctoscLoadPartition.h
    169 |   std::unordered_map<sclkCorner, ctoscDelay, sclkCornerHash> _globalPathDelayBySclk;
    170 |   std::unordered_map<sclkCorner, float, sclkCornerHash> _globalPathDelayTargetBySclk;
>   172 |   std::unordered_map<sclkCorner, std::map<ndmTerm*, ctoscDelay, ndmObjPtrCmpType>, sclkCornerHash> _sinkDelayMapBySclk; //LINTER_BYPASS
>   173 |   std::unordered_map<sclkCorner, std::map<ndmTerm*, float, ndmObjPtrCmpType>, sclkCornerHash> _sinkDelayTargetMapBySclk; //LINTER_BYPASS
    174 |   std::vector<ndmTerm*> _sinks;

ctscto/ctosc/ctoscLoadPartition.cc  (getAvgWeightedLateMargin)
    594 |   std::map<const ndmTerm*, float, ndmObjPtrCmpType> margins;
    595 |   std::map<const ndmTerm*, float, ndmObjPtrCmpType> weights;
    596 |   std::map<const ndmTerm*, float, ndmObjPtrCmpType> avgWeightedLmargin;
>   597 |   for (const auto& scTerm : _sinkDelayMapBySclk) {     // <-- ND iteration order
    598 |     const auto& sc = scTerm.first;
    603 |     float weight = nwmathFloat::abs(
    604 |       flowMgr->getFlowWeight(sc.bag->getSclk(), true, false, true));
    621 |     for (const auto& sinkDelay : scTerm.second) {
    627 |       float lmargin = glate - late;
>   628 |       margins[sink] += (lmargin * weight);   // <-- non-associative FP accumulation
>   629 |       weights[sink] += weight;
    630 |     }
    631 |   }
    632 |   for (const auto& sinkMargin : margins) {
    635 |     float tweight = weights.at(sink);
    637 |       avgWeightedLmargin[sink] = wlmargin / tweight;
    640 |   return avgWeightedLmargin;

ctscto/ctosc/ctoscLoadPartition.cc  (getAvgWeightedLateTargetMargin)
>   654 |   for (auto& scTerm : _sinkDelayTargetMapBySclk) {     // <-- ND iteration order
    656 |     float weight = nwmathFloat::abs(
    657 |       flowMgr->getFlowWeight(sc.bag->getSclk(), true, false, true));
    676 |       float lmargin = sinkPathDelayTarget - sinkPathDelay;
>   677 |       margins[sink] += (lmargin * weight);
>   678 |       weights[sink] += weight;

ctscto/ctosc/ctoscLoadPartition.cc  (init - the observable sink)
     80 |   if (_useAvgLateMargin) {
     81 |     avgLateMargins = getAvgWeightedLateMargin();
     84 |   if (_useAvgTargetLateMargin && _targetObj) {
     85 |     avgLateTargetMargins = getAvgWeightedLateTargetMargin();
     88 |   // sort sinks by delay of registered {sclk, corner}
>    89 |   std::sort(_sinks.begin(), _sinks.end(), [&](ndmTerm* a, ndmTerm* b) {
>   110 |       return (avgLateTargetMargins.at(a) > avgLateTargetMargins.at(b));
>   119 |       return avgLateMargins.at(a) > avgLateMargins.at(b);
    135 |   });
    136 |   auto spSinkIt = std::min_element(_sinks.begin(), _sinks.end(), ...
    155 |   _spSinkPos = std::distance(_sinks.begin(), spSinkIt);

ctscto/ctosc/ctoscLoadPartition.cc  (sink order becomes the buffered group)
   1414 |   termVecType group;
   1415 |   group.resize(boundary);
>  1416 |   std::copy_n(_sinks.begin(), boundary, group.begin());
   1417 |   termSetType groupSet(group.begin(), group.end());
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): canonicalise only where the order is observed.
// ctscto/ctosc/ctoscLoadPartition.cc, getAvgWeightedLateMargin()
// Keep _sinkDelayMapBySclk as the O(1) lookup container; snapshot and sort the
// keys so the float accumulation happens in a run-independent order.
std::map<const ndmTerm*, float, ndmObjPtrCmpType>
ctoscLoadPartition::getAvgWeightedLateMargin() const
{
  ctoFlowMgr* flowMgr = _global->getFlowMgr();
  std::map<const ndmTerm*, float, ndmObjPtrCmpType> margins;
  std::map<const ndmTerm*, float, ndmObjPtrCmpType> weights;
  std::map<const ndmTerm*, float, ndmObjPtrCmpType> avgWeightedLmargin;

  // sclkCornerType has a stable, ID-based operator< (ctsutil/ctsTypes.h:753)
  std::vector<sclkCorner> sccOrder;
  sccOrder.reserve(_sinkDelayMapBySclk.size());
  for (const auto& scTerm : _sinkDelayMapBySclk) {
    sccOrder.push_back(scTerm.first);
  }
  std::sort(sccOrder.begin(), sccOrder.end(),
            [](const sclkCorner& l, const sclkCorner& r) {
              return sclkCornerType(l.bag->getSclk(), l.corner) <
                     sclkCornerType(r.bag->getSclk(), r.corner);
            });

  for (const sclkCorner& sc : sccOrder) {
    const auto& sinkDelays = _sinkDelayMapBySclk.at(sc);
    auto it = _globalPathDelayBySclk.find(sc);
    if (it == _globalPathDelayBySclk.end()) {
      continue;
    }
    float weight = nwmathFloat::abs(
      flowMgr->getFlowWeight(sc.bag->getSclk(), true, false, true));
    float glate = _globalPathDelayBySclk.at(sc).late;
    float maxSinkLate = nwmathFloat::getUninitValue();
    float maxRelaxedLate = nwmathFloat::getUninitValue();
    for (const auto& sinkDelay : sinkDelays) {
      const ndmTerm* sink = sinkDelay.first;
      const float late = sinkDelay.second.late;
      if (nwmathFloat::isUninit(late)) {
        continue;
      }
      float relaxedLate = glate;
      adjustGlobalLateTargetByRelax(sink, {sc.bag->getSclk(), sc.corner}, relaxedLate);
      maxSinkLate = nwmathFloat::chooseGreater(late, maxSinkLate);
      maxRelaxedLate = nwmathFloat::chooseGreater(relaxedLate, maxRelaxedLate);
    }
    glate = nwmathFloat::chooseGreater(glate,
              nwmathFloat::chooseGreater(maxSinkLate, maxRelaxedLate));
    for (const auto& sinkDelay : sinkDelays) {
      const ndmTerm* sink = sinkDelay.first;
      const float late = sinkDelay.second.late;
      if (nwmathFloat::isUninit(late)) {
        continue;
      }
      float lmargin = glate - late;
      margins[sink] += (lmargin * weight);
      weights[sink] += weight;
    }
  }
  for (const auto& sinkMargin : margins) {
    const ndmTerm* sink = sinkMargin.first;
    float tweight = weights.at(sink);
    if (tweight > 0) {
      avgWeightedLmargin[sink] = sinkMargin.second / tweight;
    }
  }
  return avgWeightedLmargin;
}
// Apply the identical snapshot+sort to getAvgWeightedLateTargetMargin()
// (ctoscLoadPartition.cc:654) over _sinkDelayTargetMapBySclk.
```

**Version B (robust, preferred):**

```cpp
// Version B (robust, preferred): stop hashing the pointer at all.
// ctscto/ctosc/ctoscGlobal.h:272-277
//
// ctsutil/ctsTypes.h:857 already provides a fully ID-based
// std::hash<ctsNS::sclkCornerType> (clock id ^ skew-group id ^ corner id).
// Reuse it so bucket assignment no longer depends on the ctoSclkBag address.
// operator== on sclkCorner stays pointer-identity based, which is still
// correct: two distinct bags sharing an {sclk, corner} simply collide.
//
// This single edit removes the address dependence from ALL nine containers:
//   ctoscGlobal.h:365          mapSccFloat
//   ctoscFilter.h:349          _globalDelayMap
//   ctoscLoadPartition.h:169-173 (4 maps)
//   ctomtGlsProblemGenerator.h:255-257, 274-277
//   ctomtXformProblem.h:381    _initCost

// @brief custom hash function for sclkCorner
struct sclkCornerHash {
  std::size_t operator() (sclkCorner pair) const {
    if (nullptr == pair.bag) {
      return boost::hash<cstrCornerId>()(pair.corner.getId());
    }
    // hash the clock / skew-group / corner IDs, never the bag address
    return std::hash<sclkCornerType>()(
             sclkCornerType(pair.bag->getSclk(), pair.corner));
  }
};
```

**Version C:**

```cpp
// Version C: re-key the two iterated containers by the stable value type.
// ctscto/ctosc/ctoscLoadPartition.h:172-173
//
// sclkCornerType is the project's existing value key (ctsutil/ctsTypes.h:751)
// and already backs sccDelayMapType / sccDelayUmapType.  std::map gives a
// deterministic iteration order for free, so getAvgWeightedLateMargin() and
// getAvgWeightedLateTargetMargin() need no change beyond the key construction.
// Cost: lookups go O(1) -> O(log S); see performance_note_md.

  std::map<sclkCornerType, std::map<ndmTerm*, ctoscDelay, ndmObjPtrCmpType>>
    _sinkDelayMapBySclk;
  std::map<sclkCornerType, std::map<ndmTerm*, float, ndmObjPtrCmpType>>
    _sinkDelayTargetMapBySclk;

// and at every access site replace
//     sclkCorner(sBag, corner)        -> sclkCornerType(sBag->getSclk(), corner)
//     _sinkDelayMapBySclk.find(_sclkCorner)
//                                     -> _sinkDelayMapBySclk.find(
//                                          sclkCornerType(_sclkCorner.bag->getSclk(),
//                                                         _sclkCorner.corner))
// (ctoscLoadPartition.cc:159, 187, 305, 308, 324, 388, 418, 569, 664, 773,
//  777, 893, 1146, 1218, 1231, 1233)
```

**Why this fix:**

This is the only candidate in the slice where a pointer-derived container order feeds a *floating-point accumulation* rather than a set of independent per-key writes. That matters because the perturbation survives: it is not a reordering that a later `std::sort` can normalise away, it is a numerically different value that then decides a `std::sort` comparison. The comparison result selects the load partition, and the partition is committed to the database as inserted buffers. Severity HIGH rather than MEDIUM because the enabling conditions are the defaults of two mainstream MTCTO GLS modes (`isSolverAugLeafOnly`, `isAdvancedSkewOpt`), not opt-in debug switches, and because the sink is direct QoR.

**False-positive check:**

Checked and ruled out:
- Not a stable comparator/hash: `sclkCornerHash` is the supplied hash and it explicitly calls `std::hash<ctoSclkBag*>()(pair.bag)` (ctoscGlobal.h:274). Verified there is no other `sclkCornerHash` definition (`rg sclkCornerHash` -> 1 definition, 9 container uses).
- Not neutralized: there is no `std::sort`/`stable_sort` between the map iteration and the `+=`. The only canonicalisation nearby is `nwmathFloat::chooseGreater` for `glate`, which is order-insensitive and does not cover the accumulation.
- Not a lookup-only container, unlike the other seven `sclkCornerHash` users: `ctoscLoadPartition.cc:597` and `:654` are genuine range-for iterations (grepped every use of both members; `:159,187,305,308,324,388,418,569,664,773,777,893,1146,1218,1231,1233` are keyed accesses, `:597` and `:654` are the only iterations).
- Not dead: `ctoscLoadPartition::init()` is the entry point of GLS load partitioning, called from `ctomtBuffer.cc` around line 840; `_useAvgLateMargin` / `_useAvgTargetLateMargin` are set at `ctomtBuffer.cc:848,852`. No `#if`/`#ifdef` exclusion anywhere in `ctoscLoadPartition.{h,cc}` or `ctoscGlobal.h` around these lines.
- Not order-insensitive: `margins[sink] += ...` is a running `float` sum with more than one contributing term whenever the sink is live in >= 2 sccs, which is the normal multi-mode/multi-corner case. Single-scc designs would make this benign, but that is a data condition, not a code guarantee.
- Consumer really observes order: `avgLateMargins.at(a) > avgLateMargins.at(b)` (line 119) is a strict float comparison with no epsilon, so any bit difference can flip it.
- One thing I could NOT verify from source alone: how often two sinks land close enough for the ULP-level difference to actually flip the sort. That requires a two-run experiment; I am claiming the mechanism, not a measured flip rate.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctscto/ctosc/ctoscGlobal.h`
- **Primary logic (annotate):** 12 of 13 lines in the `:268-280` window, including the whole `sclkCornerHash` functor, belong to CL `7023073`.
- **Describe summary:** CL `7023073` by **`yunjianj`**, 2021-11-02 — *"Fix global late delay caching bug in MTCTO ctoscFilter"*, with cts regression and GLS skew-optimization PRS links and swarm review `7020257` (`@rlwang`).
- **CMT chain:** `[ORIG_CLIENT:dgplt_r_dev.yunjianj.cost][CMT][merge from //synopsys/nwtn/s/dev@7023011]` — original authoring user is **`yunjianj`**.
- **Notes:** the functor was added as part of a caching fix, so the pointer key was incidental to the change rather than its subject. `ctsutil/ctsTypes.h:857` already provides an ID-based `std::hash<ctsNS::sclkCornerType>` that this functor could delegate to.

---

### Pattern 2.2 — getFullName() / getPathName() used as map key or hashed  (×1)

### Issue 2.2.1 — kneeMap keyed by lib-cell getFullName() inside the CCD/CTS sizing LEQ-filter inner loop

- **File:** `ctssc/ctskSize.cc:1384` (col 1)
- **Pattern:** 2.2 — getFullName() / getPathName() used as map key or hashed
- **Category:** naming
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 1

**Why this is non-deterministic:**

`kneeMap` is `std::map<std::string, boost::tuple<ndmModule*, float, float, float> >` keyed by the **full name of a library ref module**. The tuple's element `<0>` is *already the `ndmModule*` itself*, so the string key is pure overhead: every lookup rebuilds the module's hierarchical name and then does an O(log n) **string-compare** descent.

The hot site is the LEQ-filter loop in `kneeBasedFiltering()`. On every iteration of `while(kneeOrder.empty() == false)` the code takes `ndmModule* kneeMod = kneeOrder.begin()->second;` and then immediately calls `kneeMod->getFullName()` **twice** (lines 1384 and 1385) to look up the very tuple that holds `kneeMod`. The loop runs once per logically-equivalent cell in the LEQ set, and `kneeBasedFiltering()` is invoked once per driver being sized.

There is no non-determinism here: `std::map<std::string,...>` is lexicographically ordered, and `orderKneeData()` (ctsscKneeExtractor.cc:134/146) iterates it in name order to fill a `std::multimap<long, ndmModule*>`, whose equal-key order is insertion order (C++11 guarantee). That makes the sizing tie-break *stable by library-cell name*. The defect is therefore (a) a real cost on a hot path and (b) a name-stability dependency: any escaping/separator/hierarchy-rename change silently reorders `kneeOrder` and therefore reorders which equivalent cells are pushed into `leqSet`.

**Realness:** `real`

**Downstream observability proof:**

1. `ctssc/ctsscKneeExtractor.cc:217` - `kneeMap` is populated with one entry per LEQ cell, keyed by `(*it)->getFullName()`.
2. `ctssc/ctsscKneeExtractor.cc:134` and `:146` - `orderKneeData()` **iterates `kneeMap`** (lexicographic name order) to build `kneeOrder`, a `std::multimap<long, ndmModule*>`. Equal `long` knee distances therefore come out in library-cell-name order.
3. `ctssc/ctskSize.cc:1384-1385` - each loop iteration does two `getFullName()` + string-map lookups on `kneeMod`.
4. `ctssc/ctskSize.cc:1386` - `leqSet.push_back(kneeMod)`: **mutates the caller's LEQ set**, i.e. the candidate cell list the sizer is allowed to choose from.
5. `ctssc/ctskSize.cc:1348` - `kneeBasedFiltering(ndmTerm *driver, std::vector<ndmModule *> &leqSet)` takes `leqSet` by reference and clears it at 1356, so the filtered set is the sizer's whole search space -> the chosen cell size -> a `ndmInst` ref-module change in the NDM database. **QoR-affecting.**
6. Gate: `ctssc/ctskSize.cc:1349` - `if(ccdConfig::get_knee_range() <= 0 || leqSet.size() < 3) { return false; }`.

**Controls / gating:**

Reached whenever CCD/CTS cell sizing runs with `ccdConfig::get_knee_range() > 0` and the driver has >= 3 logically-equivalent cells (the normal case for any real clock buffer/inverter library). No env var or debug flag is required. `ctsscKneeExtractor::filterByKnee()` is the second entry point into the identical code. Cost scales as O(#sized-clock-cells x #LEQ-cells x 2) name constructions.

**Performance-aware fix direction:**

`ndmModule::getFullName()` walks the owner chain to the top and concatenates each level's name with the hierarchy separator, allocating (and usually heap-allocating, since lib-cell full names routinely exceed the 15-char SSO budget) a fresh `std::string` per call. Cost is O(hierarchy depth x avg name length) plus one malloc/free pair. `getIdLong()` is a single field load: O(1), zero allocation. The `std::map` lookup itself then costs O(log n) **string comparisons** instead of O(log n) integer comparisons.

The call is inside a loop, and worse, it is called **twice per iteration** on the same object (lines 1384 and 1385), so even without changing the key type, hoisting the name into a local would halve the cost. With a typical 30-cell LEQ set that is 60 name constructions per sized driver; across a design with 200k sized clock cells that is on the order of 10^7 redundant hierarchical-name builds. Switching the key to the `ndmModule*` removes 100% of them. Adding the key change costs nothing at runtime - `ndmObjPtrCmpType` (== `ndmObjectHandleNS::compareObjPtr`, see `ccd/util/ccdUtil.h:71`) is an integer ID compare.

Separately, `ctssc/ctskSize.cc:1374` and `ctssc/ctsscKneeExtractor.cc:684` are **dead stores**: `maxDelay` is unconditionally overwritten with `1000.0` on the next line (`low_power` is hardcoded `true` at ctskSize.cc:1362). Those two `getFullName()` calls can simply be deleted.

**Current code:**

```cpp
  1359 |   ndmModule* mod = driver->toConn()->getInst()->getRefModule();
  1360 |   std::string modname = (mod != nullptr) ? mod->getFullName() : "NA";
  1361 |   float maxPower = kneeMap[modname].get<2>();
  1362 |   bool low_power = true;
  ...
  1371 |   if(kneeOrder.empty() == false) {
  1372 |     bestKnee = kneeOrder.begin()->first;
> 1373 |     maxPower = std::max(maxPower, kneeMap[kneeOrder.begin()->second->getFullName()].get<2>());
> 1374 |     maxDelay = std::max(maxDelay, kneeMap[kneeOrder.begin()->second->getFullName()].get<1>());
  1375 |   }
  1376 |   if(low_power) {  maxDelay = 1000.0;  }   // <-- makes line 1374 a dead store
  ...
  1380 |   while(kneeOrder.empty() == false) {
  1381 |     float kneeDis = kneeOrder.begin()->first;
  1382 |     if(kneeDis > 0) { break;}
  1383 |     ndmModule* kneeMod = kneeOrder.begin()->second;      // <-- the pointer is right here
> 1384 |     if((kneeDis * range < bestKnee) || ( kneeMap[kneeMod->getFullName()].get<2>() <= maxPower &&
> 1385 |                                         kneeMap[kneeMod->getFullName()].get<1>() <= maxDelay)) {
  1386 |       leqSet.push_back(kneeMod);
  1387 |     }
  1388 |     if(kneeMod == mod && !low_power) { break; }
  1389 |     kneeOrder.erase( kneeOrder.begin() );
  1390 |   }

  -- ctsscKneeExtractor.cc (near-identical duplicate) --
   217 |     kneeMap.insert(std::make_pair((*it)->getFullName(), boost::make_tuple(*it, delay, sit->second, tran)));
   686 |   maxDelay = 1000.0;                       // <-- makes line 684 a dead store
   689 |   while(kneeOrder.empty() == false) {
   692 |     ndmModule* kneeMod = kneeOrder.begin()->second;
>  693 |     if((kneeDis * range < bestKnee) || ( kneeMap[kneeMod->getFullName()].get<2>() <= maxPower &&
>  694 |                                         kneeMap[kneeMod->getFullName()].get<1>() <= maxDelay)) {
   695 |       leqSet.push_back(kneeMod);
```

**Suggested fix:**

**Version A (recommended):**

```cpp
// Version A (recommended): key the map by the ndmModule* with the ID-stable
// comparator; the tuple's <0> element already held the module anyway.
// ctsscKneeExtractor.h / ctskSize.h
typedef std::map<ndmModule*, boost::tuple<ndmModule*, float, float, float>,
                 ndmObjPtrCmpType> kneeMapType;   // ndmObjPtrCmpType == ndmObjectHandleNS::compareObjPtr

// ctsscKneeExtractor.cc:217
kneeMap.insert(std::make_pair(*it, boost::make_tuple(*it, delay, sit->second, tran)));

// ctskSize.cc:1380-1390
while(kneeOrder.empty() == false) {
  float kneeDis = kneeOrder.begin()->first;
  if(kneeDis > 0) { break; }
  ndmModule* kneeMod = kneeOrder.begin()->second;
  const boost::tuple<ndmModule*, float, float, float>& knee = kneeMap[kneeMod];
  if((kneeDis * range < bestKnee) ||
     (knee.get<2>() <= maxPower && knee.get<1>() <= maxDelay)) {
    leqSet.push_back(kneeMod);
  }
  if(kneeMod == mod && !low_power) { break; }
  kneeOrder.erase(kneeOrder.begin());
}
```

**Version B:**

```cpp
// Version B: keep an integer key if the map must stay value-typed.
// getIdLong() is O(1) and stable across name/escaping changes.
typedef std::map<long, boost::tuple<ndmModule*, float, float, float> > kneeMapType;

// ctsscKneeExtractor.cc:217
kneeMap.insert(std::make_pair((*it)->getIdLong(),
                              boost::make_tuple(*it, delay, sit->second, tran)));

// ctskSize.cc:1383-1387
ndmModule* kneeMod = kneeOrder.begin()->second;
const boost::tuple<ndmModule*, float, float, float>& knee = kneeMap[kneeMod->getIdLong()];
if((kneeDis * range < bestKnee) ||
   (knee.get<2>() <= maxPower && knee.get<1>() <= maxDelay)) {
  leqSet.push_back(kneeMod);
}
```

**Version C (minimal, no type change):**

```cpp
// Version C (minimal, no type change): cache the name once per iteration and
// delete the two dead stores. Halves the cost without touching the container.
// ctskSize.cc:1371-1376
if(kneeOrder.empty() == false) {
  bestKnee = kneeOrder.begin()->first;
  const std::string& bestName = kneeOrder.begin()->second->getFullName();
  maxPower = std::max(maxPower, kneeMap[bestName].get<2>());
  // line 1374 deleted: maxDelay is overwritten on the next line
}
if(low_power) { maxDelay = 1000.0; }

// ctskSize.cc:1383-1387
ndmModule* kneeMod = kneeOrder.begin()->second;
const boost::tuple<ndmModule*, float, float, float>& knee = kneeMap[kneeMod->getFullName()];
if((kneeDis * range < bestKnee) ||
   (knee.get<2>() <= maxPower && knee.get<1>() <= maxDelay)) {
  leqSet.push_back(kneeMod);
}
```

**Why this fix:**

**Version A.** The tuple already stores the `ndmModule*`, so the string key carries zero information the pointer does not. `ndmObjPtrCmpType` is a typedef of `ndmObjectHandleNS::compareObjPtr` (`ccd/util/ccdUtil.h:71`), which compares object IDs, so the map stays deterministic *and* becomes rename-proof - a strictly better determinism story than today's name ordering. It removes every `getFullName()` call on this path, converts O(log n) string compares to O(log n) integer compares, and is a mechanical change confined to one typedef plus five call sites. Version C is the safe hot-fix if the type change is judged too invasive for the release branch; it still removes half the calls and both dead stores. Note that `ctskSize.cc` and `ctsscKneeExtractor.cc` are copy-paste duplicates of the same 25 lines - whichever fix is chosen must be applied to both, and the duplication itself is worth collapsing.

**False-positive check:**

Not a false positive as a *performance/stability* finding: the map is a live algorithmic container (`kneeMap[...]` results feed the `leqSet.push_back` decision at ctskSize.cc:1386), not a report. It **is** a false positive as a *non-determinism* finding, and I say so explicitly: `std::map<std::string,...>` is ordered, `std::multimap` preserves insertion order for equal keys since C++11, and nothing here is pointer-keyed or unordered, so the output is bit-reproducible run to run on a fixed netlist. The audit's own 2.2 guidance calls out performance as a first-class problem for this pattern, which is why this is filed rather than dismissed. I could not measure the actual runtime share of `kneeBasedFiltering()` - the quantification above is an operation count, not a profile.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctssc/ctskSize.cc`
- **Primary logic (annotate):** the two `kneeMap[kneeMod->getFullName()]` lines (`:1384-1385`) belong to CL `4151071`; the surrounding `kneeOrder` loop belongs to CL `3970076`.
- **Describe summary:** CL `4151071` by **`jwon`**, 2018-04-26 — *": Fixed non-deterministic behavior in ccd"*, touching `ctssc/ctskSize.cc`, `ctssc/ctsscKneeExtractor.cc`, `ctssc/ctsscKneeExtractor.h`.
- **CMT chain:** `[ORIG_CLIENT:jwon_1709_sp_dev][CMT][merge from //synopsys/nwtn/n2017.09_sp/dev@4151006]` — original authoring user is **`jwon`**.
- **Notes:** this is important context for the severity call. The `getFullName()` key **was the ND fix** — re-keying from a pointer to a stable name deliberately traded cost for determinism. This finding is therefore a **cost and name-stability** item, not an ND regression, and the same CL is the reason the duplicate exists at `ctsscKneeExtractor.cc:693`.

---

### Pattern 2.5 — std::unique on pointer vector without prior stable sort  (×1)

### Issue 2.5.1 — fmax LP redundant-path dedup sorts by constraint VALUE but calls std::unique with POINTER equality

- **File:** `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` (col 1)
- **Pattern:** 2.5 — std::unique on pointer vector without prior stable sort
- **Category:** sorting
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 1

**Why this is non-deterministic:**

`pathVector` is `std::vector<const I2V*>` where `I2V = std::map<int, float>` (a single LP constraint row: variable index -> coefficient). See `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:80` for `TimingRelationContainerLightVectorBased = std::vector< std::pair<int, std::vector<const I2V*> > >` and `ccd/ctsccd/fmax/fmaxLpModel.h:69` for `I2V`.

Line 5126 sorts with `fmaxLpModel::ConstraintComparatorNew()`, whose pointer overload (`fmaxLpModel.h:161-162`) **dereferences and compares constraint CONTENT**.

Line 5127 then calls `std::unique(pathVector.begin(), pathVector.end())` **with no predicate**, so the equality test is `operator==` on `const I2V*` - i.e. **raw address comparison**.

The sort key and the dedup key are different keys. Two consequences:

1. **The dedup never fires for the case it was written for.** Two distinct `I2V` objects with byte-identical content sort adjacent but are never equal by address, so duplicate LP constraint rows survive into the model. The function is literally named `removeRedundantPathsParallel`, so this defeats its stated purpose.
2. **When the same pointer does appear twice, whether it is removed is unspecified.** `std::sort` is not stable. Given a run like `[P, Q, P]` where `P`, `Q`, `R` all compare equivalent under `ConstraintComparatorNew` (identical content, different addresses), introsort may leave the two `P` entries non-adjacent, in which case `std::unique` removes nothing. Which permutation you get depends on the input order of `pathVector`, which is set by the thread-fragmentation in `mergeViolatedPathsOfSolutionsParallel` and therefore **varies with `_maxThreads`** (`ccd/ctsccd/fmax/fmaxCostFunction.cc:38`, driven by the host core count / `set_host_options`).

The surviving order and content then feed a **first-wins tie-break** at lines 5143 and 5147 (strict `<`), which selects `worstViolationAtA` / `worstViolationAtB`, which is the threshold every other path is filtered against at 5157-5158.

**Realness:** `real`

**Downstream observability proof:**

1. `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5126-5128` - suspect site: value-sort then address-unique on `pathVector`.
2. `:5143` / `:5147` - `worstViolationAtA` / `worstViolationAtB` are picked with **strict `<`**, so the first path achieving the minimum `.first` wins and its `.second` is carried along. Two paths tied on `.first` but differing on `.second` therefore yield a different `worstViolationAtA.second` depending on which one `std::sort` placed earlier.
3. `:5157-5158` - every other path is kept or dropped by comparing against `worstViolationAtA` / `worstViolationAtB`. A different `.second` shifts the threshold and flips keep/drop for other paths.
4. `:5165` - `vectorContainer[innerIndex].second = newPathVector;` **writes the filtered set back** into the `TimingRelationContainerLightVectorBased` owned by the timing cost function.
5. `:5338` - `removeRedundantPathsParallel(solutionPathsA.solution, solutionPathsB.solution, result);` is called at the end of `mergeViolatedPathsOfSolutionsParallel`.
6. `:4892` - `mergeViolatedPathsOfSolutionsParallel(*fromPaths, *toPaths, allViolatedPathsMapForParallelUse);` is on the **live incremental fmax LP path** (not env-gated, unlike the file-replay flow).
7. The resulting constraint set is what the CLP/HiGHS/cuOpt solver receives. Surviving duplicate rows change the simplex pivot sequence and can land on a different vertex among alternate optima; dropped/kept rows change the feasible region outright. Either way the LP solution drives CCD fmax buffer/size/skew decisions -> **QoR**.

**Controls / gating:**

Reached by the incremental fmax LP flow (CCD fmax / clock-concurrent optimization) whenever `mergeViolatedPathsOfSolutionsParallel` runs, i.e. whenever two candidate solutions A and B are merged during the LP line search. Requires `pathVector.size() > 1` (guard at 5124/5130). Runs inside `tbb::parallel_for` across `_maxThreads` threads; `_maxThreads` is set from the thread count passed to `fmaxCostFunction` (`ccd/ctsccd/fmax/fmaxCostFunction.cc:38`), which tracks the host core budget. Changing `-max_cores` / moving to a different machine changes the fragmentation in `mergeViolatedPathsOfSolutionsParallel` (`:5225-5240`) and therefore the pre-sort permutation of `pathVector`. No app option or env var disables this path.

**Performance-aware fix direction:**

Adding a correct predicate to `std::unique` costs nothing asymptotically - the comparator is already being called O(n log n) times by the sort on line 5126, and `std::unique` adds only O(n) more of the same comparisons. If anything the fix is a net *win*: today's broken dedup leaves duplicate constraint rows in the LP, and every duplicate row costs the simplex solver real time. Switching from address equality to `!comp(a,b) && !comp(b,a)` (or an explicit `SameConstraint` functor) is one extra argument at the call site.

**Current code:**

```cpp
  5121 |         auto &pathVector = vectorContainer[innerIndex].second;   // std::vector<const I2V*>
  5124 |         if(pathVector.size() == 1 ) {continue;}
  5125 |
  5126 |         std::sort(pathVector.begin(), pathVector.end(), fmaxLpModel::ConstraintComparatorNew());  // by VALUE
> 5127 |         auto newEndIterator = std::unique(pathVector.begin(), pathVector.end());                 // by ADDRESS
  5128 |         pathVector.erase(newEndIterator, pathVector.end());
  ...
  5136 |         for(auto & path : pathVector) {
  5138 |           float violationA = _fullModel->evaluateSlackOfPath(*path, solutionA);
  5139 |           float violationB = _fullModel->evaluateSlackOfPath(*path, solutionB);
  5141 |           violationsPerPath.emplace_back(violationA,violationB);
  5143 |           if(violationsPerPath.back().first < worstViolationAtA.first) {   // strict < => FIRST wins
  5144 |             worstViolationAtA = violationsPerPath.back();
  5145 |           }
  5147 |           if(violationsPerPath.back().second < worstViolationAtB.second) { // strict < => FIRST wins
  5148 |             worstViolationAtB = violationsPerPath.back();
  5149 |           }
  5150 |         }
  5153 |         std::vector<const I2V *> newPathVector;
  5155 |         for(size_t count = 0; count < pathVector.size(); ++count) {
  5157 |           if( (violationsPerPath[count].first > worstViolationAtA.first && violationsPerPath[count].second > worstViolationAtA.second)
  5158 |              || (violationsPerPath[count].first > worstViolationAtB.first && violationsPerPath[count].second > worstViolationAtB.second) ) {
  5159 |             continue;                                    // path DROPPED from the LP
  5160 |           } else {
  5161 |             newPathVector.push_back(pathVector[count]);
  5162 |           }
  5163 |         }
  5165 |         vectorContainer[innerIndex].second = newPathVector;   // MUTATION of the LP relation container

  -- ccd/ctsccd/fmax/fmaxLpModel.h --
   126 |   struct ConstraintComparatorNew {
   127 |     bool operator()(const I2V &constraintA, const I2V &constraintB) const { /* compares map contents */ }
   161 |     bool operator()(const I2V* constraintA, const I2V* constraintB) const
   162 |     { return this->operator()(*constraintA,*constraintB); }   // <-- dereferences: VALUE compare
```

**Suggested fix:**

**Version A (recommended):**

```cpp
// Version A (recommended): dedup with the SAME key the sort used.
// ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5126-5128
std::sort(pathVector.begin(), pathVector.end(), fmaxLpModel::ConstraintComparatorNew());
auto newEndIterator = std::unique(pathVector.begin(), pathVector.end(),
                                  [](const I2V* a, const I2V* b) {
                                    fmaxLpModel::ConstraintComparatorNew cmp;
                                    return !cmp(a, b) && !cmp(b, a);   // equivalence under the sort order
                                  });
pathVector.erase(newEndIterator, pathVector.end());
```

**Version B:**

```cpp
// Version B: give the model a named equality functor next to the comparator,
// so the sort key and the unique key can never drift apart again.
// ccd/ctsccd/fmax/fmaxLpModel.h, right after ConstraintComparatorNew (line 165)
struct SameConstraintNew {
  bool operator()(const I2V &a, const I2V &b) const { return a == b; }
  bool operator()(const I2V *a, const I2V *b) const { return *a == *b; }
};

// ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5126-5128
std::sort(pathVector.begin(), pathVector.end(), fmaxLpModel::ConstraintComparatorNew());
pathVector.erase(std::unique(pathVector.begin(), pathVector.end(),
                             fmaxLpModel::SameConstraintNew()),
                 pathVector.end());
```

**Version C:**

```cpp
// Version C: additionally make the tie-break itself explicit so the
// worst-violation pick no longer depends on vector position at all.
// ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5143-5149
const std::pair<float,float>& v = violationsPerPath.back();
if(v.first < worstViolationAtA.first ||
   (v.first == worstViolationAtA.first && v.second < worstViolationAtA.second)) {
  worstViolationAtA = v;
}
if(v.second < worstViolationAtB.second ||
   (v.second == worstViolationAtB.second && v.first < worstViolationAtB.first)) {
  worstViolationAtB = v;
}
```

**Why this fix:**

**Version B, plus Version C.** Version B is the real fix: the bug is that two different keys were used for one logical operation, and burying the equality next to the comparator in `fmaxLpModel.h` makes that class of mistake structurally harder to repeat. Version A is equivalent but inlines the equivalence test at the call site, where the next person to touch this code will not see it. Version C is worth taking alongside either one, because it removes the *remaining* positional dependence: even with a correct dedup, `worstViolationAtA` is currently chosen by `std::sort`'s arbitrary ordering of equivalent-value constraints, and a value-based tie-break makes the selection independent of `_maxThreads`. Together they make this block reproducible across core counts, which is the property the audit is actually after.

**False-positive check:**

I verified the element type really is a pointer (`fmaxTimingCostFunction.h:80`), that the comparator really does dereference (`fmaxLpModel.h:161-162`), and that `std::unique` really is called without a predicate (line 5127). So the key mismatch is certain, and the mutation sink at 5165 and the live caller at 4892 are traced.

What I could **not** verify, and want to be explicit about: I could not demonstrate an actual run-to-run divergence. The mismatch is a *certain* correctness defect (duplicate constraints are never removed). The *non-determinism* half of the claim rests on the pre-sort permutation of `pathVector` changing, which I traced to the thread-count-dependent fragmentation in `mergeViolatedPathsOfSolutionsParallel` (`:5225-5240`) but did not run. On a single machine with a fixed `_maxThreads`, `std::sort` is deterministic and this block will reproduce. I rated it HIGH because it sits on a hot `tbb::parallel_for` in the live LP path and mutates the LP constraint set, not because I have a reproducer.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc`
- **Primary logic (annotate):** all 13 lines of the `:5121-5133` window, including the `std::sort` / `std::unique` pair, belong to CL `9748335`.
- **Describe summary:** CL `9748335` by **`tsirogia`**, 2024-01-19 — *"Fix (UDEV) for STAR P10235709-88066 (no update on timing function weights). Also contains runtime improvement for issue P10235709-87627 (further parallelization of LP solver). Project Rolex Development."*
- **CMT chain:** `[ORIG_CLIENT:tsirogia_nwtn_dgplt_u_dev][CMT][merge from //synopsys/nwtn/v2023.12/rel@9748292]` — original authoring user is **`tsirogia`**.
- **Notes:** the comparator/equality mismatch arrived together with the LP-solver parallelization in the same CL, which is consistent with the dedup never having been exercised for the tied case it targets.

---

### Pattern 3.2 — Multi-threaded shared container writes  (×1)

### Issue 3.2.1 — Concurrent std::map node insertion into the CG solver's log-sum-exp function maps from tbb::parallel_for_each over scenarios

- **File:** `ccd/skewopt/soSolverUpdater.cc:2100` (col 1)
- **Pattern:** 3.2 — Multi-threaded shared container writes
- **Category:** parallel
- **Severity:** HIGH  (default: HIGH)
- **Tier:** 2

**Why this is non-deterministic:**

`soCgSolverUpdater::addLogSumExpFuncsToSolver()` fans out over scenarios with `tbb::parallel_for_each` and every worker ends up calling `soCgSolver::addLogSumExpFunc()`. The very first statement of that callee is

    soCgEpLogSumExpFuncMapType& funcs = funcsMap[scenario];

where `funcsMap` is the solver member `_setupLogSumExpFuncs` / `_holdLogSumExpFuncs`, typed `std::map<cstrScenario, soCgEpLogSumExpFuncMapType>` (soSolverFuncs.h:139). `std::map::operator[]` on an absent key **allocates a node and rebalances the red-black tree**. Nothing serialises that: there is no mutex, the map is a plain `std::map` (not a concurrent container), and it is not pre-populated anywhere before the parallel region. Two workers handling two different scenarios therefore perform concurrent structural modification of the same tree.

This is a data race in the C++ memory-model sense, i.e. undefined behaviour, not a 'merely unordered' result. The concrete observable failure modes are (a) a lost scenario bucket, so an entire scenario's log-sum-exp terms silently vanish from the CG objective, (b) a duplicated/overwritten node, so one scenario's terms are attributed to another, and (c) tree corruption leading to a crash or hang on the next traversal (e.g. soCG.cc:3204). Which of these happens depends purely on thread interleaving, so the same design + same options can converge to different clock trees or crash intermittently.

The inner per-scenario map is fine: each scenario is owned by exactly one worker, and `updateInfo::addLogSumExpFuncsToSolver()` already calls `func->reorderSlackFuncs(_updater->getInfoOrder())` (soSolverUpdater.cc:5248) to pin the slack-function order. Only the **outer** scenario-keyed map is unprotected.

Note the contrast forty lines below: `addStartPointLogSumExpFunc()` (soSolverUpdater.cc:2147) parallelises over the same scenario list but writes into `scenarioLogSumExpStartPointFuncs[i]`, a vector pre-sized before the loop, and merges afterwards. The safe idiom already exists in this file; this call site just does not use it.

**Realness:** `real`

**Downstream observability proof:**

1. **Parallel construct** - `ccd/skewopt/soSolverUpdater.cc:2100` (`tbb::parallel_for_each(setupScenarios, ...)`), and the hold twin at `ccd/skewopt/soSolverUpdater.cc:2107`. One task per scenario; a multi-corner / multi-mode design has many scenarios, so this really does run wide.
2. **Worker body** - `ccd/skewopt/soSolverUpdater.cc:2103` calls `updateInfo::addLogSumExpFuncsToSolver()`, defined at `ccd/skewopt/soSolverUpdater.cc:5240`, which calls `solver->addLogSumExpFunc(...)` at `ccd/skewopt/soSolverUpdater.cc:5249`.
3. **Shared state write** - `ccd/skewopt/soCG.cc:1086` does `funcsMap[scenario]` on the solver member `_setupLogSumExpFuncs` / `_holdLogSumExpFuncs` (`ccd/skewopt/soCG.h:510-511`). Type is `std::map` per `ccd/skewopt/soSolverFuncs.h:139` - no internal synchronisation. I found no pre-population of these maps anywhere before the parallel region (all other references in `soCG.cc` are reads at 1052/1169/2976/3004/3099/3155/3204/3294/3312/3451 or the `clearLogSumExpFuncs` teardown at 542-543), so on the first solver invocation every `operator[]` is a genuine insert.
4. **Consumer** - `ccd/skewopt/soCG.cc:1169` `initScenarioLSETable()` returns `funcs.size()` per scenario (drives solver statistics / sizing), and `ccd/skewopt/soCG.cc:3204` and `ccd/skewopt/soCG.cc:3451` iterate `_setupLogSumExpFuncs` end-to-end.
5. **Observable sink** - the log-sum-exp terms are the TNS/WNS part of the CG objective function evaluated in `soCgSolver::gradFuncArcBased()` (`ccd/skewopt/soCG.cc:1706`, `logSumExpGradFuncMtArcBased`). A lost or misattributed scenario bucket changes the objective, hence the skew solution, hence the committed clock latencies - a QoR-affecting database write. Tree corruption additionally shows up as an intermittent crash during the traversals at 3204/3451.

**Controls / gating:**

**Not gated - this runs multi-threaded by default whenever there is more than one scenario.** There is no `enableMultiThreading` check, no `getMaxThreadCount()` check, no `isMultiThread` branch and no single-thread fallback around `soSolverUpdater.cc:2100/2107`. Unlike almost every other MT site in this module, these two calls use raw `tbb::parallel_for_each` rather than `ccdUtil::parallel_for` (`ccd/util/ccdUtil.cc:3915`) or `ctsMtTaskRunner`, so they do not even go through the `ndmDesignWriteLock` suspend-or-fall-back-to-serial path that those wrappers provide.

The only thing that makes it benign is a design with a single active setup scenario and a single active hold scenario, in which case `setupScenarios.size() == 1` and there is no concurrency. Any multi-corner multi-mode (MCMM) run is exposed.

TBB's arena width is bounded by `crmResources::get().getMaxThreadCount()` (`set_host_options -max_cores`) elsewhere in CTS, so `-max_cores 1` would serialise it, but that is a global escape hatch, not a control on this code path. `crm.h` itself lives outside this snapshot, so I could not read the default value of `getMaxThreadCount()`.

**Performance-aware fix direction:**

The fix is essentially free. The parallel region is per-scenario and the expensive part is `updateInfo::addLogSumExpFuncsToSolver()` walking `_logSumExpFuncs` and cloning slack functions - that stays parallel. All that has to change is where the per-scenario bucket comes from.

Version A (pre-create the nodes) adds one single-threaded pass over the scenario list, which is O(number of scenarios) - a handful of map inserts, unmeasurable against a CG solve. It keeps 100% of the current parallelism.

Version B (per-scenario buffers merged in index order) costs one extra map move per scenario and additionally makes the merge order deterministic by construction. It is the same shape as `addStartPointLogSumExpFunc()` at soSolverUpdater.cc:2147, which is already in production in this file, so the runtime profile is known-good.

Version C (a mutex around the bucket lookup) is the smallest diff but takes a lock on every single `addLogSumExpFunc` call - that is once per (endpoint, scenario), i.e. millions of times on a large design. Do not use it in the hot path; it would serialise the very thing being parallelised. Version A is the right trade.

**Current code:**

```cpp
ccd/skewopt/soSolverUpdater.cc
  2093 |   std::vector<cstrScenario> setupScenarios, holdScenarios;
  2094 |   for (auto& it : _setupScenarioInfosMap) {
  2095 |     setupScenarios.emplace_back(it.first);
  2096 |   }
  2097 |   for (auto& it : _holdScenarioInfosMap) {
  2098 |     holdScenarios.emplace_back(it.first);
  2099 |   }
> 2100 |   tbb::parallel_for_each(setupScenarios, [&](cstrScenario& sc) {
  2101 |       updateInfoVecType& infos = _setupScenarioInfosMap[sc];
  2102 |       for (unsigned int i = 0; i < infos.size(); ++i) {
  2103 |         infos[i]->addLogSumExpFuncsToSolver(solver);
  2104 |       }
  2105 |     }
  2106 |   );
> 2107 |   tbb::parallel_for_each(holdScenarios, [&](cstrScenario& sc) {
  2108 |       updateInfoVecType& infos = _holdScenarioInfosMap[sc];
  2109 |       for (unsigned int i = 0; i < infos.size(); ++i) {
  2110 |         infos[i]->addLogSumExpFuncsToSolver(solver);
  2111 |       }
  2112 |     }
  2113 |   );

ccd/skewopt/soSolverUpdater.cc  (per-updateInfo, still inside the worker)
  5242 |   for (soCgEpLogSumExpFuncMapType::iterator it = _logSumExpFuncs.begin();
  5243 |        it != _logSumExpFuncs.end(); ++it) {
  5244 |     ndmTerm* ep = it->first;
  5245 |     soCgEpLogSumExpFunc* func = it->second;
  5248 |     func->reorderSlackFuncs(_updater->getInfoOrder());
> 5249 |     solver->addLogSumExpFunc(ep, func, _scenario, _isSetup);

ccd/skewopt/soCG.cc  (THE RACING LINE)
  1075 | soCgSolver::addLogSumExpFunc(ndmTerm* ep, soCgEpLogSumExpFunc* func,
  1076 |                              cstrScenario scenario, bool setup)
  1084 |   soCgEpLogSumExpFuncsMapType& funcsMap = setup ? _setupLogSumExpFuncs : _holdLogSumExpFuncs;
> 1086 |   soCgEpLogSumExpFuncMapType& funcs = funcsMap[scenario];   // <-- unguarded std::map insert
  1088 |   soCgEpLogSumExpFuncMapType::iterator it = funcs.find(ep);
  1090 |   if (it == funcs.end()) {
  1099 |     funcs[ep] = newFunc;

ccd/skewopt/soSolverFuncs.h
   138 | typedef std::map<ndmTerm*, soCgEpLogSumExpFunc*, ctsNS::ndmObjPtrCmpType> soCgEpLogSumExpFuncMapType;
   139 | typedef std::map<cstrScenario, soCgEpLogSumExpFuncMapType> soCgEpLogSumExpFuncsMapType;
```

**Suggested fix:**

**Version A:**

```cpp
// VERSION A - materialise every scenario bucket single-threaded, then make the
// parallel path lookup-only. Smallest behavioural delta, keeps all parallelism.

// ccd/skewopt/soCG.h  (new public method on soCgSolver)
void reserveLogSumExpScenarios(const std::vector<cstrScenario>& scenarios, bool setup);

// ccd/skewopt/soCG.cc
void
soCgSolver::reserveLogSumExpScenarios(const std::vector<cstrScenario>& scenarios, bool setup)
{
  soCgEpLogSumExpFuncsMapType& funcsMap = setup ? _setupLogSumExpFuncs : _holdLogSumExpFuncs;
  for (const cstrScenario& sc : scenarios) {
    funcsMap[sc];
  }
}

// ccd/skewopt/soCG.cc  soCgSolver::addLogSumExpFunc() - replace line 1086
  soCgEpLogSumExpFuncsMapType::iterator mapIt = funcsMap.find(scenario);
  dvuAssertRelease(mapIt != funcsMap.end());
  soCgEpLogSumExpFuncMapType& funcs = mapIt->second;

// ccd/skewopt/soSolverUpdater.cc  soCgSolverUpdater::addLogSumExpFuncsToSolver()
  solver->reserveLogSumExpScenarios(setupScenarios, true  /*setup*/);
  solver->reserveLogSumExpScenarios(holdScenarios,  false /*setup*/);
  tbb::parallel_for_each(setupScenarios, [&](cstrScenario& sc) {
      updateInfoVecType& infos = _setupScenarioInfosMap[sc];
      for (unsigned int i = 0; i < infos.size(); ++i) {
        infos[i]->addLogSumExpFuncsToSolver(solver);
      }
    }
  );
```

**Version B:**

```cpp
// VERSION B - per-scenario buffers merged back in fixed index order.
// Mirrors soSolverUpdater.cc:2147 (addStartPointLogSumExpFunc), which already
// uses exactly this shape. Deterministic by construction, solver never touched
// from a worker.

// ccd/skewopt/soSolverUpdater.cc
void
soCgSolverUpdater::addLogSumExpFuncsToSolver(soCgSolver* solver)
{
  std::vector<cstrScenario> setupScenarios, holdScenarios;
  for (auto& it : _setupScenarioInfosMap) { setupScenarios.emplace_back(it.first); }
  for (auto& it : _holdScenarioInfosMap)  { holdScenarios.emplace_back(it.first); }

  auto collect = [&](const std::vector<cstrScenario>& scenarios,
                     std::map<cstrScenario, updateInfoVecType>& infosMap,
                     bool isSetup) {
    std::vector<soCgEpLogSumExpFuncMapType> perScenarioFuncs(scenarios.size());
    tbb::parallel_for(size_t(0), scenarios.size(), [&](size_t i) {
      updateInfoVecType& infos = infosMap[scenarios[i]];
      for (unsigned int j = 0; j < infos.size(); ++j) {
        infos[j]->collectLogSumExpFuncs(perScenarioFuncs[i]);  // no solver access
      }
    });
    for (size_t i = 0; i < scenarios.size(); ++i) {
      solver->mergeLogSumExpFuncs(scenarios[i], perScenarioFuncs[i], isSetup);
    }
  };

  collect(setupScenarios, _setupScenarioInfosMap, true  /*isSetup*/);
  collect(holdScenarios,  _holdScenarioInfosMap,  false /*isSetup*/);
}
```

**Version C:**

```cpp
// VERSION C - lock only the bucket lookup. Smallest diff, but it takes a lock
// once per (endpoint, scenario). Listed for completeness; do NOT ship this in
// the hot path.

// ccd/skewopt/soCG.cc  soCgSolver::addLogSumExpFunc() - replace line 1086
  soCgEpLogSumExpFuncMapType* funcsPtr = nullptr;
  {
    tbb::spin_mutex::scoped_lock lock(_logSumExpMapMutex);  // new soCgSolver member
    funcsPtr = &funcsMap[scenario];
  }
  soCgEpLogSumExpFuncMapType& funcs = *funcsPtr;
```

**Why this fix:**

**Take Version A.** It is a three-line change at the racing site plus one trivial helper, it removes the undefined behaviour outright rather than papering over it, it keeps every bit of the existing parallelism, and the `dvuAssertRelease` turns any future caller that forgets to reserve into a loud failure instead of a silent race.

Version B is architecturally nicer - it also makes the merge order explicitly deterministic and matches the idiom already used by `addStartPointLogSumExpFunc()` - but it needs two new solver APIs (`collectLogSumExpFuncs`, `mergeLogSumExpFuncs`) and touches ownership of the cloned `soCgEpLogSumExpFunc*`, so it is a bigger review. Worth doing as a follow-up cleanup, not as the bug fix.

Version C is rejected: locking per endpoint-scenario would serialise the loop it is meant to protect.

**False-positive check:**

Checked and ruled out:
- *Is the map actually shared?* Yes. `_setupLogSumExpFuncs` / `_holdLogSumExpFuncs` are `soCgSolver` members (soCG.h:510-511) and every worker receives the same `solver` pointer.
- *Is it a concurrent container?* No. `soSolverFuncs.h:139` types it as a plain `std::map`. `tbb::concurrent_*` appears nowhere in this type.
- *Is it pre-populated, making `operator[]` a pure lookup?* I grepped every reference to `_setupLogSumExpFuncs` / `_holdLogSumExpFuncs` in `soCG.cc` and `soCG.h`. The only non-read uses are `clearLogSumExpFuncs()` at 542-543 (teardown) and the `operator[]` at 1086 itself. Nothing seeds the scenario keys beforehand.
- *Are setup and hold the same map?* No, and the two `parallel_for_each` calls are sequential, so they do not race against each other. The race is strictly between workers inside one call.
- *Could the scenarios collapse to one, making it single-threaded?* Yes on a single-corner single-mode design, and then it is harmless. That is what makes this intermittent rather than always-fatal - it is not a reason to dismiss it.
- *Is the inner map also racing?* No. One scenario is handled by exactly one worker, so `funcs.find(ep)` / `funcs[ep] = newFunc` at 1088-1099 are single-threaded per bucket.
- *Is this dead code?* No. It is reached from `soCgSolverUpdater::updateSolver()` at soSolverUpdater.cc:1492, on the main CCD skew-optimisation path.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ccd/skewopt/soSolverUpdater.cc`
- **Primary logic (annotate):** 10 of 13 lines in the `:2094-2106` window, including the `tbb::parallel_for_each` at `:2100` and the `_setupScenarioInfosMap[sc]` access at `:2101`, belong to CL `13914296`.
- **Describe summary:** CL `13914296` by **`matteod`**, 2026-06-15 — *"EoU Project: first batch of obsolete app options in CCD from DRI list — Remove legacy runtime branches in skewopt solver/CG/design code; drop soProcess and soPathTracingProcess plus MP-CUS LSE multi-path support; obsolete retired skewopt app options and accessors; regolden skewopt unit tests"*.
- **Notes:** the unguarded concurrent insert was introduced by an **app-option cleanup refactor**, not by a feature change. That is worth flagging to the author, because the removal of legacy runtime branches is exactly the kind of change where a previously single-threaded path silently becomes reachable under threads. The correct pre-sized per-scenario idiom already exists ~40 lines below at `:2147` in the same file.

---


## MEDIUM Severity Issues

_13 finding(s)._

### Pattern 1.2 — std::set / std::map with pointer key, default comparator  (×3)

### Issue 1.2.1 — ctoFlow::restructFlow iterates std::set<ndmTerm*> candidate sets in address order, then clones/shields buffers and truncates at a 10% cap

- **File:** `ctscto/ctoFlowClone.cc:1884` (col 1)
- **Pattern:** 1.2 — std::set / std::map with pointer key, default comparator
- **Category:** container
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ctoFlow::restructFlow()` collects two candidate driver sets as `std::set<ndmTerm*>` with the default `std::less<ndmTerm*>` comparator, i.e. ordered by raw `ndmTerm` address. It then walks both sets and, for each candidate, attempts `cloneBufferInverter(drvTerm)` and `bufShieldBufferInverter(drvTerm)`. Both are netlist mutations - `cloneBufferInverter` creates a new instance and registers it (`_ctoBuffers.insert(newInst)`, ctoFlowClone.cc:887).

Two distinct ND effects:

1. **Path dependence.** Cloning a driver changes fanout and path delays, and `isOffLongShortPaths(drvTerm, ...)` (line 2029) re-checks criticality *during* the loop. A candidate that is still critical when visited early may be skipped when visited late, and vice versa. So the set of accepted transforms depends on visit order even without the cap.
2. **Truncation.** The second loop stops early:

```
2052 |     countCands++;
2053 |     if (countCands > (int) (10 * maxClockTree / 100)) {
2057 |       break;
2058 |     }
```

Only the first ~10% of `maxClockTree` candidates are ever processed. Which candidates fall inside that prefix is decided purely by `ndmTerm` addresses.

**Realness:** `real`

**Downstream observability proof:**

1. `ctscto/ctoFlowClone.cc:1884,1885` - `candidates` and `lpCandidates` declared as `std::set<ndmTerm*>` with default `std::less<ndmTerm*>`; ordering is by raw address.
2. `ctscto/ctoFlowClone.cc:1966,1973` - populated from a deterministic walk (`_clocks` levelized list, `drvTerms` vector, `corners` vector), so membership is deterministic; only the set's internal ordering is not.
3. `ctscto/ctoFlowClone.cc:1993` - `lpCandidates` iterated in address order.
4. `ctscto/ctoFlowClone.cc:2006` -> `ctoFlow::cloneBufferInverter` (`ctoFlowClone.cc:599`) -> `ctoFlowClone.cc:884-887` inserts a newly created `newInst` into `_ctoOrigBuffers` / `_ctoCloneBuffers` / `_ctoBuffers` and calls `_flowMgr->updateFlowAfterInsertion(...)`. That is a database/netlist write.
5. `ctscto/ctoFlowClone.cc:2012` -> `ctoFlow::bufShieldBufferInverter` (`ctoFlowClone.cc:1287`), same class of mutation.
6. `ctscto/ctoFlowClone.cc:2025` - `candidates` iterated in address order.
7. `ctscto/ctoFlowClone.cc:2029` - `isOffLongShortPaths(drvTerm, ...)` reads *current* path delays, which the mutations at step 4/5 have already changed. Visit order therefore decides which later candidates are skipped.
8. `ctscto/ctoFlowClone.cc:2052-2058` - `countCands` cap at `10 * maxClockTree / 100` breaks out of the loop. The accepted subset is literally the address-ordered prefix.
9. `ctscto/ctoFlow.cc:9516` and the post-pass QoR report at `ctscto/ctscto.cc:853-855` (`printMultiClockSkewAndDrc(..., ctoQorLog::POST_PRE_OPT_RESTRUCTURING)`) observe the resulting tree.

Sink class: database mutation + first-N selection. Both qualify.

**Controls / gating:**

Entry point `ctoFlow::flowPreOptRestruct()` (`ctscto/ctoFlowClone.cc:1862`) is called from exactly one place:

```
ctscto/ctscto.cc
    844 |   // pre-phase2 restructuring optimization for latency improvement
    845 |   if (getRoutingMode() == ctscto::GLOBAL && opts.isUsePreOptReStructuringForLatency()) {
    850 |     flow->flowPreOptRestruct();
```

- App option: `cts.optimize.enable_latency_driven_pre_opt_restructuring`, registered at `ctsui/ctsuiOptimizeAppOptions.cc:1334` with **default `false`** and `cciuAppOptionMgr::UNLISTED`. Backing field `_enablePreOptReStructuringForLatency`, `ctsutil/ctsAppOptions.h:1702`, initialised `false` at `ctsutil/ctsAppOptions.cc:1644`, bound at `ctsutil/ctsAppOptions.cc:360`.
- Second guard: `getRoutingMode() == ctscto::GLOBAL`.
- Same option also flips `_flowPropSpeedUp` off at `ctscto/ctoFlowMgr.cc:208` and `_doPhaseTwoPreOpt` on at `ctscto/ctoRestruct.cc:135`.
- Internal knob: `_thresholdForCloning = 0.005` (`ctscto/ctoFlowClone.cc:44`) and the hard-coded 10% cap at line 2053.
- Data condition: needs >= 2 candidates whose relative order can change which ones survive the criticality re-check or the cap. On small clock trees `10 * maxClockTree / 100` can be 0, in which case exactly one candidate is processed - which makes the ND *worse*, not better, because it is fully decided by address.

Severity is MEDIUM rather than HIGH strictly because of the default-off, unlisted option gate. Impact when the option is on is HIGH-class (netlist structure).

**Performance-aware fix direction:**

`restructFlow()` runs once per CTO invocation (pre-optimization phase), not in an inner loop. Both candidate sets are bounded by the number of buffer/inverter drivers on the clock trees. Cost analysis:

- Version A adds one `std::vector<ndmTerm*>` copy plus an `O(C log C)` sort per set, where C is the candidate count. This is dwarfed by the `getPathDelay` timer queries already performed per candidate per corner in the collection loop (lines 1957-1978), and by `cloneBufferInverter` itself. Effectively free.
- Version B (`dosSet<ndmTerm*>` / `std::set<ndmTerm*, ndmObjPtrCmpType>`) keeps insertion and lookup at `O(log C)` but changes the comparator from a pointer compare to an ID compare, which is a handful of extra instructions per comparison on an `O(C log C)` total. Not measurable here. `_ctoBuffers` in the same class is already `dosSet<ndmInst*>` (`ctscto/ctoFlow.h:665`), so this matches local convention.
- Version C (vector of `ndmTermId` + explicit dedup) is the same order of cost.

No complexity regression in any option; no hash-to-tree downgrade is involved. QoR benchmarking IS needed, because fixing the order changes which candidates get cloned - results will move. Run with `cts.optimize.enable_latency_driven_pre_opt_restructuring true` on a latency-sensitive regression and compare `POST_PRE_OPT_RESTRUCTURING` QoR against baseline.

**Additional occurrences of the same root cause:**

- `ctscto/ctoFlowClone.cc:1885 (lpCandidates declaration)`
- `ctscto/ctoFlowClone.cc:1993 (iteration over lpCandidates)`
- `ctscto/ctoFlowClone.cc:2025 (iteration over candidates, with early break)`

**Current code:**

```cpp
ctscto/ctoFlowClone.cc
   1878 | void ctoFlow::restructFlow() {
   1883 |
>  1884 |   std::set<ndmTerm*> candidates;
>  1885 |   std::set<ndmTerm*> lpCandidates;
   1886 |   int maxClockTree = 0;
   1887 |   int candCount = 0;
   ...
   1965 |          if (late == rootLate[corner]) {
   1966 |            if (lpCandidates.insert(drvTerm).second) {
   ...
   1973 |            if (candidates.insert(drvTerm).second) {
   ...
   1992 |   // process the candidates along the LP(s)
>  1993 |   for (std::set<ndmTerm*>::iterator it = lpCandidates.begin(); it != lpCandidates.end(); ++it) {
   1994 |     const ndmTerm* drvTerm = *it;
   2004 |     bool enableCloning = true;
   2005 |     bool enableShielding = true;
>  2006 |     if (enableCloning && cloneBufferInverter(drvTerm)) {      // netlist mutation
   2007 |       acceptedCands++;
   2012 |     else if (enableShielding && bufShieldBufferInverter(drvTerm)) {  // netlist mutation
   2013 |       acceptedCands++;
   2019 |   }
   2023 |   // process remaining candidates
   2024 |   countCands = 0;
>  2025 |   for (std::set<ndmTerm*>::iterator it = candidates.begin(); it != candidates.end(); ++it) {
   2026 |     const ndmTerm* drvTerm = *it;
   2029 |     if (isOffLongShortPaths(drvTerm, true, false, _thresholdForCloning)) {
   2033 |       continue;                                              // state-dependent skip
   2034 |     }
>  2040 |     if (enableCloning && cloneBufferInverter(drvTerm)) {
   2045 |     } else if (enableShielding && bufShieldBufferInverter(drvTerm)) {
   2050 |     }
   2052 |     countCands++;
>  2053 |     if (countCands > (int) (10 * maxClockTree / 100)) {      // first-N truncation
   2057 |       break;
   2058 |     }
   2060 |   }

ctscto/ctoFlowClone.cc  (the mutation)
    599 | bool ctoFlow::cloneBufferInverter(const ndmTerm* drvTerm1) {
    ...
    883 |     // register clone instances
    884 |     _ctoOrigBuffers.insert(inst);
    885 |     _ctoCloneBuffers.insert(newInst);
    886 |     // register the new instnce as a CTO buffer
>   887 |     _ctoBuffers.insert(newInst);
    889 |     _flowMgr->updateFlowAfterInsertion(drvTerm, newDrvTerm, groupedLoadsTwo);
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): keep the fast set for dedup, snapshot + sort for the walk.
// ctscto/ctoFlowClone.cc:1878-2068

  std::set<ndmTerm*> candidates;
  std::set<ndmTerm*> lpCandidates;
  ...  // collection loop unchanged (lines 1888-1981)

  // Canonicalise before any transform is attempted: address order decides both
  // the path-dependent skips and the 10%-cap prefix below.
  auto byStableId = [](const ndmTerm* l, const ndmTerm* r) {
    return ndmObjectHandleNS::compareObjPtr{}(l, r);
  };
  std::vector<ndmTerm*> lpCandVec(lpCandidates.begin(), lpCandidates.end());
  std::sort(lpCandVec.begin(), lpCandVec.end(), byStableId);
  std::vector<ndmTerm*> candVec(candidates.begin(), candidates.end());
  std::sort(candVec.begin(), candVec.end(), byStableId);

  // process the candidates along the LP(s)
  for (const ndmTerm* drvTerm : lpCandVec) {
    bool enableCloning = true;
    bool enableShielding = true;
    if (enableCloning && cloneBufferInverter(drvTerm)) {
      acceptedCands++;
      ...
    }
    else if (enableShielding && bufShieldBufferInverter(drvTerm)) {
      acceptedCands++;
      countCands++;
      ...
    }
  }

  // process remaining candidates
  countCands = 0;
  for (const ndmTerm* drvTerm : candVec) {
    if (isOffLongShortPaths(drvTerm, true, false, _thresholdForCloning)) {
      continue;
    }
    ...
    countCands++;
    if (countCands > (int) (10 * maxClockTree / 100)) {
      break;
    }
  }
```

**Version B (robust):**

```cpp
// Version B (robust): make the containers deterministic at the declaration.
// ctscto/ctoFlowClone.cc:1884-1885
//
// dosSet is already the house type for exactly this in the same class:
//   ctscto/ctoFlow.h:665  dosSet<ndmInst*> _ctoBuffers;
// and ndmObjPtrCmpType == ndmObjectHandleNS::compareObjPtr
//   (ctsutil/ctsTypes.h:63) is the ID-based pointer comparator.
// No other code touches these two locals, so this is a two-line change plus
// the two iterator type names at lines 1993 and 2025.

  dosSet<ndmTerm*> candidates;
  dosSet<ndmTerm*> lpCandidates;
  ...
  for (dosSet<ndmTerm*>::iterator it = lpCandidates.begin(); it != lpCandidates.end(); ++it) {
  ...
  for (dosSet<ndmTerm*>::iterator it = candidates.begin(); it != candidates.end(); ++it) {

// Equivalent spelling without the dos wrapper:
//   std::set<ndmTerm*, ndmObjPtrCmpType> candidates;
//   std::set<ndmTerm*, ndmObjPtrCmpType> lpCandidates;
```

**Version C:**

```cpp
// Version C: re-key by the stable ndm ID and drop the pointer container entirely.
// ctscto/ctoFlowClone.cc:1884-1885, 1966, 1973, 1993, 2025

  std::set<ndmTermId> candidateIds;
  std::set<ndmTermId> lpCandidateIds;
  ...
  // collection (replaces lines 1966 / 1973)
  if (late == rootLate[corner]) {
    if (lpCandidateIds.insert(drvTerm->getId()).second) {
      ctsLog::printf("CTO:: pre-opt:: adding LP candidate %d/%lu:: ...", ...);
      candCount++;
    }
  } else if (...) {
    if (candidateIds.insert(drvTerm->getId()).second) { ... }
  }
  ...
  // walk (replaces lines 1993 / 2025); ndmTermId ordering is address independent
  ndmDesign* design = _ctscto->getDesign();
  for (ndmTermId tid : lpCandidateIds) {
    const ndmTerm* drvTerm = ndmTerm::get(design, tid);
    if (nullptr == drvTerm) { continue; }   // clone may have removed it
    ...
  }
// Bonus: this also removes the dangling-pointer hazard that the current code
// has, since cloneBufferInverter() can delete instances while the sets are
// still holding raw ndmTerm* into them.
```

**Why this fix:**

This is the clearest mutation sink in the slice: address order directly selects which drivers get cloned, and the 10%-cap `break` turns the ordering into an explicit first-N selection. It is not speculative - the loop body calls a function that inserts instances into the design. I graded it MEDIUM rather than HIGH only because `cts.optimize.enable_latency_driven_pre_opt_restructuring` defaults to `false` and is UNLISTED, so most production runs never execute this code. Anyone who does turn it on gets run-to-run netlist differences.

**False-positive check:**

Checked and ruled out:
- Really default-compared: `std::set<ndmTerm*>` at ctoFlowClone.cc:1884,1885, no third template argument. Confirmed the local `candidates`/`lpCandidates` are not the class members of the same name (they are function locals declared inside `restructFlow`).
- Not dead: `restructFlow()` is called by `flowPreOptRestruct()` (line 1866), which is called at `ctscto/ctscto.cc:850`. Reachable, just option-gated. No `#if`/`#ifdef` around it.
- Not neutralized: no sort or canonicalisation between the declarations and the two walks.
- Not lookup-only: lines 1993 and 2025 are explicit `begin()`/`end()` iterations.
- The sink is a real mutation, verified by reading `cloneBufferInverter` (ctoFlowClone.cc:599) down to the `_ctoBuffers.insert(newInst)` at line 887, not inferred from the name.
- Honest caveat about this file: `ctscto/ctoFlow.h:765` declares `void restructFlow(termSetType candidates, termSetType lpCandidates, int maxClockTree);` (3 args, `termSetType` = `std::set<ndmTerm*, ndmObjPtrCmpType>`) while `ctoFlowClone.cc:1878` defines a 0-arg `ctoFlow::restructFlow()`. Those two cannot both be the compiled entity. I treated the `.cc` definition as authoritative because it is the one that contains the executable logic and is called by `flowPreOptRestruct()` at line 1866; I could not compile the snapshot to confirm. If the header is the live version, the sets are already `ndmObjPtrCmpType` and this finding collapses to safe-adopter. See notes_md - the same header/implementation divergence shows up in six other places in this snapshot.
- The separate candidate `ctscto/ctoFlow.h:772` matching the same symbols is a commented-out line and is dismissed as a false positive.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctscto/ctoFlowClone.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Issue 1.2.2 — Keepout margins are applied to a run-varying subset of clock lib cells because setKeepoutMarginForLibCell returns out of its std::set<ndmModule*> loop

- **File:** `mscts/drivers/msDrivers.cc:11645` (col 1)
- **Pattern:** 1.2 — std::set / std::map with pointer key, default comparator
- **Category:** container
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`msClockDrivers::setKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells, float x, float y)` and its counterpart `removeKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells)` both take a `std::set<ndmModule*>` with the default `std::less<ndmModule*>`, so the set is ordered by the raw address of the reference-module objects and iterates in a different order every run.

Iterating a set of lib cells to stamp the same margin on each one would normally be order-insensitive. It is not here, because both loops contain an **early `return` out of the middle of the loop** on a per-cell data condition:

- `mscts/drivers/msDrivers.cc:11657-11660` - if a lib cell has no usable FRAME-view bounding box, the function prints a message and `return`s, abandoning every lib cell that had not yet been reached.
- `mscts/drivers/msDrivers.cc:11683` - `removeKeepoutMarginForLibCell` `return`s on the first lib cell with no FRAME view, abandoning the rest.

So when at least one lib cell in the set lacks a FRAME view, *which* lib cells end up with a keepout margin is decided by heap addresses. The `remove` variant is the more damaging half: a margin that was successfully set during CTS can be left behind on a reference block after CTS finishes, and whether it leaks depends on the run.

**Realness:** `real`

**Downstream observability proof:**

**Hop 1 - declarations.** Four independent producers build a default-compared `std::set<ndmModule*>` of clock lib cells:
- `mscts/drivers/msDrivers.cc:2233` (`allLibCells`, in driver-option validation)
- `mscts/drivers/msDrivers.cc:1604` (`libCells`, built from `unassignedLoads`)
- `mscts/drivers/msAutoTapFlow.cc:1306` (`allLibCells`, auto-tap flow)
- `mscts/msgts/msgtsOptions.cc:531` `msgtsOptions::getLibCells()` returns `std::set<ndmModule*>` by value (declared `mscts/msgts/msgtsOptions.h:192`), which is drained into `std::set<ndmModule*> _allLibCells` (`mscts/msgts/msgtsFlow.h:464`) at `mscts/msgts/msgtsFlow.cc:758-760`.

**Hop 2 - call sites.** Those sets are passed straight into the two consumers:
- set: `mscts/drivers/msDrivers.cc:2328`, `mscts/msgts/msgtsFlow.cc:764`, `mscts/drivers/msAutoTapFlow.cc:1325` region
- remove: `mscts/drivers/msDrivers.cc:1611`, `mscts/drivers/msAutoTapFlow.cc:1323` and `:1343`, `mscts/msgts/msgtsFlow.cc:1196` and `:5154`

**Hop 3 - ND iteration with a mid-loop exit.** `mscts/drivers/msDrivers.cc:11647` iterates the set. On the first element whose FRAME view or boundary bbox is missing, `mscts/drivers/msDrivers.cc:11659` returns. Elements are visited in `std::less<ndmModule*>` order, i.e. by the address of the `ndmModule` objects, so the prefix of the set that is processed before the bail-out is a run-varying subset. Same structure at `mscts/drivers/msDrivers.cc:11678` / `:11683`.

**Hop 4a - persisted database state.** `mscts/drivers/msDrivers.cc:11666` calls `refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, ...)` on the FRAME-view block of the reference module. That is a hard keepout halo stored on the reference library block, not a local variable: it changes where the placer and legalizer may place every instance of that reference for the remainder of the session. Which references carry a halo therefore differs run to run, which changes clock-cell placement and hence QoR.

**Hop 4b - state that outlives CTS.** `mscts/drivers/msDrivers.cc:11685` is the cleanup that zeroes the halo. Because `:11683` can return early, a halo set during CTS can survive past the CTS teardown calls at `mscts/msgts/msgtsFlow.cc:1196` and `:5154`, leaking a hard keepout into downstream place-and-route. Whether it leaks, and on which references, is address-dependent.

**Hop 4c - user-visible output.** `mscts/drivers/msDrivers.cc:11658` prints `"TCI: Insert Fail - valid lib cell bounding box not found ..skipped!"`. Because the loop stops at the first offending cell, the number of times this line appears across a session is order-dependent.

**Controls / gating:**

Gated behind one app option, checked identically at every producer:

```cpp
// mscts/msui/msuiAppOptions.cc:3882
    enableHtreeCellKeepoutMargin =
    initAppOption<std::string>(catMultisource, "htree_cell_keepout_factor",
                        "takes the value of halo factor required around htree cells",
                        /*default*/ "", MSUI_BASIC, design);
```

Guards, all of the form `enableHtreeCellKeepoutMargin.length() != 0`:
`mscts/drivers/msDrivers.cc:1602`, `mscts/drivers/msDrivers.cc:2324`, `mscts/drivers/msAutoTapFlow.cc:1307`, `:1322`, `:1342`, `mscts/msgts/msgtsFlow.cc:757`, `mscts/msgts/msgtsIrregGlobalTreeFlow.cc:537`, `:550`.

The option is a `MSUI_BASIC` (documented, user-facing) multisource option, declared as `std::string enableHtreeCellKeepoutMargin` at `mscts/msui/msuiAppOptions.h:667`; it holds the halo scale factors and is split by `StrUtils::splitStr` at e.g. `mscts/drivers/msDrivers.cc:2327`. Default is the empty string, so the code is **off unless the user sets `htree_cell_keepout_factor`**.

Additional data condition required for the ND to bite: at least one lib cell in the set must have no FRAME-view alternate view, or a FRAME block with an invalid boundary bbox. With a fully populated frame library the loop never bails out and the result is order-insensitive. Mixed libraries (some cells frame-only, some abstract-only) are the realistic trigger.

Flow steps that reach it: driver-option validation and H-tree driver insertion (`create_clock_drivers` / `synthesize_multisource_clock_trees` paths through `msClockDrivers`), the auto-tap flow (`mscts/drivers/msAutoTapFlow.cc`), and the msgts global-tree flow (`mscts/msgts/msgtsFlow.cc`, `mscts/msgts/msgtsIrregGlobalTreeFlow.cc`).

**Performance-aware fix direction:**

This is not hot-path code. The sets hold clock buffer/inverter *reference* modules - the lib-cell menu for one level of the tree, typically a handful to a few dozen entries - and the two functions are called once per level, not per instance or per pin. Both bodies already do design/view/block lookups and a database write per element, which dwarfs any comparator cost.

None of the fixes change lookup complexity. The sets are only ever populated with `insert` (`mscts/drivers/msDrivers.cc:2241`, `:1608`, `mscts/msgts/msgtsFlow.cc:759`), narrowed with `erase` (`mscts/drivers/msDrivers.cc:2322`), tested with `size`/`empty` (`:2332`), and traversed once. Version A adds one `std::vector<ndmModule*>` of pointers plus one `std::sort` per call - allocation and O(n log n) on a few-dozen-element vector, outside any inner loop. Version B changes `std::less<ndmModule*>` to `ndmObjPtrCmpType`, which swaps a pointer compare for an id compare in the red-black tree; on containers this small the difference is unmeasurable, and it matches what the four sibling sets at `mscts/drivers/msDrivers.cc:2234-2238` already pay.

Runtime benchmarking is not needed. QoR benchmarking **is** needed, but only for designs that set `htree_cell_keepout_factor` and have an incomplete frame library, since those are the only runs whose keepout halos change. Note that fixing the mid-loop `return` (Version A's companion change, and the part I would not ship without) will *increase* the number of references that receive a halo, which is a real QoR change and not just a determinism change - it should be measured separately from the ordering fix.

**Additional occurrences of the same root cause:**

- {'file': 'mscts/drivers/msDrivers.cc', 'line': 11676, 'note': 'removeKeepoutMarginForLibCell - same ND loop; its early return at :11683 can leave a hard keepout margin on a reference block after CTS.'}
- {'file': 'mscts/drivers/msDrivers.cc', 'line': 2233, 'note': 'Producer `allLibCells` in driver-option validation; passed to setKeepoutMarginForLibCell at :2328.'}
- {'file': 'mscts/drivers/msDrivers.cc', 'line': 1604, 'note': 'Producer `libCells` built from unassignedLoads; passed to removeKeepoutMarginForLibCell at :1611.'}
- {'file': 'mscts/drivers/msDrivers.h', 'line': 1137, 'note': 'Declaration of setKeepoutMarginForLibCell; signature must change for Version B.'}
- {'file': 'mscts/drivers/msDrivers.h', 'line': 1138, 'note': 'Declaration of removeKeepoutMarginForLibCell; signature must change for Version B.'}
- {'file': 'mscts/drivers/msAutoTapFlow.cc', 'line': 1306, 'note': 'Producer `allLibCells` in the auto-tap flow; passed to removeKeepoutMarginForLibCell at :1323 and :1343.'}
- {'file': 'mscts/msgts/msgtsOptions.h', 'line': 192, 'note': 'Declaration of msgtsOptions::getLibCells() returning std::set<ndmModule*> by value.'}
- {'file': 'mscts/msgts/msgtsOptions.cc', 'line': 531, 'note': 'Definition of msgtsOptions::getLibCells(); its result is drained into msgtsFlow::_allLibCells at msgtsFlow.cc:758-760 and then fed to setKeepoutMarginForLibCell at :764.'}

**Current code:**

```cpp
mscts/drivers/msDrivers.cc - producer (one of several, see additional_occurrences)
  2231 |       msuiAppOptions appOptions(nlInterf.getTopModule()->getDesign());
  2232 |       bool mixedPolarityLevel = false;
> 2233 |       std::set<ndmModule*> allLibCells;                              // default std::less<ndmModule*>
  2234 |       std::set<ndmModule*, ndmObjPtrCmpType> nonCtsPurposeLibCells;  // note: neighbours ARE stable
  2235 |       std::set<ndmModule*, ndmObjPtrCmpType> dontTouchLibCells;
  ...
  2241 |         allLibCells.insert(refModule);
  ...
  2324 |       if (appOptions.enableHtreeCellKeepoutMargin.length() != 0) {
  2325 |         std::vector<float> scaleVals;
  2326 |         std::string str = appOptions.enableHtreeCellKeepoutMargin;
  2327 |         StrUtils::splitStr(str,scaleVals);
> 2328 |         msClockDrivers::setKeepoutMarginForLibCell(allLibCells, scaleVals[0], scaleVals[1]);
  2329 |       }

mscts/drivers/msDrivers.cc - consumer with the mid-loop return
> 11645 | void msClockDrivers::setKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells, float x, float y) 
  11646 | {
> 11647 |   for(ndmModule* libCell: allLibCells) {        // <-- ND iteration order
  11648 |     ndmBBox lcBbox = ndmBBox();
  11649 |     ndmDesign* refDesign = 0;
  11650 |     ndmBlock* refBlock = 0;
  11651 | 
  11652 |     refDesign = libCell->getDesign()->getAlternateView(ndmView::TYPE_FRAME);
  11653 |     if (refDesign)
  11654 |       refBlock = refDesign->getBlock();
  11655 |     if (refBlock)
  11656 |       lcBbox = refBlock->getBoundary().getBBox();
  11657 |     if (!lcBbox.isValid()) {
  11658 |       userOutput::printf("TCI: Insert Fail - valid lib cell bounding box not found ..skipped!\n");
> 11659 |       return;                                    // <-- ABANDONS THE REST OF THE SET
  11660 |     }
  11661 | 
  11662 |     ndmDistance lcWidth = lcBbox.getWidth();
  11663 |     ndmDistance lcHeight = lcBbox.getHeight();
  11664 |     ndmDistance keepoutMarginHt = lcHeight*y;
  11665 |     ndmDistance keepoutMarginWd = lcWidth*x; 
> 11666 |     refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, keepoutMarginWd, keepoutMarginHt,
        |                                     keepoutMarginWd, keepoutMarginHt);   // <-- DB WRITE
  11667 |   }
  11668 | }

> 11676 | void msClockDrivers::removeKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells) 
  11677 | {
> 11678 |   for(ndmModule* libCell: allLibCells) {        // <-- ND iteration order
  11679 |     ndmBBox lcBbox = ndmBBox();
  11680 |     ndmDesign* refDesign = 0;
  11681 |     ndmBlock* refBlock = 0;
  11682 |     refDesign = libCell->getDesign()->getAlternateView(ndmView::TYPE_FRAME);
> 11683 |     if (!refDesign) return;                      // <-- ABANDONS THE REST; MARGIN LEAKS
  11684 |     refBlock = refDesign->getBlock();
> 11685 |     refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, 0, 0, 0, 0);          // <-- DB WRITE
  11686 |   }
  11687 | }
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): canonicalise the order where it is observed, and stop
// abandoning the rest of the set on a per-cell data problem.
// mscts/drivers/msDrivers.cc:11645
void msClockDrivers::setKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells, float x, float y)
{
  // Snapshot keys and sort by a stable database id: the loop below can skip
  // elements, so the visit order is observable.
  std::vector<ndmModule*> libCellVec(allLibCells.begin(), allLibCells.end());
  std::sort(libCellVec.begin(), libCellVec.end(),
            [](ndmModule* a, ndmModule* b) { return a->getIdLong() < b->getIdLong(); });

  for (ndmModule* libCell : libCellVec) {
    ndmBBox lcBbox = ndmBBox();
    ndmDesign* refDesign = 0;
    ndmBlock* refBlock = 0;

    refDesign = libCell->getDesign()->getAlternateView(ndmView::TYPE_FRAME);
    if (refDesign)
      refBlock = refDesign->getBlock();
    if (refBlock)
      lcBbox = refBlock->getBoundary().getBBox();
    if (!lcBbox.isValid()) {
      userOutput::printf("TCI: Insert Fail - valid lib cell bounding box not found ..skipped!\n");
      continue;                 // was: return -- skip this cell only
    }

    ndmDistance lcWidth  = lcBbox.getWidth();
    ndmDistance lcHeight = lcBbox.getHeight();
    ndmDistance keepoutMarginHt = lcHeight*y;
    ndmDistance keepoutMarginWd = lcWidth*x;
    refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, keepoutMarginWd, keepoutMarginHt,
                                    keepoutMarginWd, keepoutMarginHt);
  }
}

// mscts/drivers/msDrivers.cc:11676 -- same two changes
void msClockDrivers::removeKeepoutMarginForLibCell(std::set<ndmModule*> allLibCells)
{
  std::vector<ndmModule*> libCellVec(allLibCells.begin(), allLibCells.end());
  std::sort(libCellVec.begin(), libCellVec.end(),
            [](ndmModule* a, ndmModule* b) { return a->getIdLong() < b->getIdLong(); });

  for (ndmModule* libCell : libCellVec) {
    ndmDesign* refDesign = libCell->getDesign()->getAlternateView(ndmView::TYPE_FRAME);
    if (!refDesign) continue;   // was: return -- do not leak margins on later cells
    ndmBlock* refBlock = refDesign->getBlock();
    if (!refBlock) continue;
    refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, 0, 0, 0, 0);
  }
}
```

**Version B (robust):**

```cpp
// Version B (robust): declare every one of these sets with the project
// deterministic comparator, matching the sibling sets already in this file
// (msDrivers.cc:2234-2238 use std::set<ndmModule*, ndmObjPtrCmpType>).

// mscts/drivers/msDrivers.h:1137
    static void setKeepoutMarginForLibCell(std::set<ndmModule*, ndmObjPtrCmpType> allLibCells,
                                           float x, float y);
// mscts/drivers/msDrivers.h:1138
    static void removeKeepoutMarginForLibCell(std::set<ndmModule*, ndmObjPtrCmpType> allLibCells);

// mscts/drivers/msDrivers.cc:2233
      std::set<ndmModule*, ndmObjPtrCmpType> allLibCells;
// mscts/drivers/msDrivers.cc:1604
      std::set<ndmModule*, ndmObjPtrCmpType> libCells;
// mscts/drivers/msAutoTapFlow.cc:1306
  std::set<ndmModule*, ndmObjPtrCmpType> allLibCells;
// mscts/msgts/msgtsFlow.h:464  and  mscts/msgts/msgtsOptions.h:856
    std::set<ndmModule*, ndmObjPtrCmpType> _allLibCells;
// mscts/msgts/msgtsOptions.h:192  and  mscts/msgts/msgtsOptions.cc:531
    std::set<ndmModule*, ndmObjPtrCmpType> getLibCells(const bool p_fullMVAware) const;

// Keep the `continue`-instead-of-`return` correction from Version A as well;
// a stable comparator makes the subset reproducible but still wrong.
```

**Version C:**

```cpp
// Version C: re-key by a stable id so the container cannot be address-ordered.
// mscts/drivers/msDrivers.cc:11645
void msClockDrivers::setKeepoutMarginForLibCell(const std::map<ndmObjectId, ndmModule*>& allLibCells,
                                                float x, float y)
{
  for (const auto& entry : allLibCells) {       // ordered by stable id
    ndmModule* libCell = entry.second;
    ...                                          // body as in Version A, with `continue`
  }
}

// Producers key by id instead of inserting the pointer, e.g.
// mscts/drivers/msDrivers.cc:2241
        allLibCells[refModule->getIdLong()] = refModule;
// mscts/msgts/msgtsFlow.cc:759
      _allLibCells[lc->getIdLong()] = lc;
```

**Why this fix:**

**Recommend Version B, shipped together with the `return` -> `continue` correction from Version A.**

The two halves of this defect need different fixes and it is worth being explicit about that. The ND is caused by the address-ordered container, and Version B removes it at the source, for all four producers at once, using `ndmObjPtrCmpType` - the idiom the four sibling sets three lines below `mscts/drivers/msDrivers.cc:2233` already use. That consistency is the strongest argument for B over A: a reviewer looking at `mscts/drivers/msDrivers.cc:2233-2238` today sees one odd set among five, and B makes the odd one match. B is also the only version that protects the `msgtsOptions::getLibCells()` return value (`mscts/msgts/msgtsOptions.cc:531`), which is a by-value `std::set` that could acquire new consumers.

But B alone still leaves a real bug: a single frame-less lib cell silently drops the margin for an arbitrary but now *reproducible* set of other cells, and in `removeKeepoutMarginForLibCell` it reproducibly leaks a hard keepout past CTS. The `continue` change is what makes the loops do what their names say. Ship both.

Version A on its own is the right choice only if the reviewer wants to keep the diff inside the two consumer functions and not touch four producers in three modules. It is a legitimate fallback, and I would accept it, but it leaves four default-compared `std::set<ndmModule*>` declarations in the tree for the next person to trip over.

Version C is over-engineering for a container of a few dozen reference modules: it changes a public static signature, forces every producer to switch from `insert` to keyed assignment, and gains nothing that B does not already give.

**False-positive check:**

- Confirmed pointer key with defaulted comparator at every site: `std::set<ndmModule*>` at `mscts/drivers/msDrivers.cc:11645`, `:11676`, `:2233`, `:1604`, `mscts/drivers/msDrivers.h:1137`, `:1138`, `mscts/drivers/msAutoTapFlow.cc:1306`, `mscts/msgts/msgtsOptions.h:192`, `mscts/msgts/msgtsOptions.cc:531`. Contrast with `mscts/drivers/msDrivers.cc:2234-2238`, where the neighbouring sets *do* pass `ndmObjPtrCmpType` - that contrast is what convinced me the omission is accidental rather than a scanner artefact. Also checked `ctsutil/ctsTypes.h:129`: there is a stable `moduleSetType` typedef (`TYPEDEF_CONTAINER_1(std::set, Set, ndmModule*, module, Module, ndmObjPtrCmpType)`) that these sites simply are not using.
- Checked the type-mismatch angle, because `mscts/drivers/msDrivers.cc:2336` passes `invalidLibCells` (a `ndmObjPtrCmpType` set) to a function spelled `removeLibCells(const std::set<ndmModule*>&)`. Resolved: that call binds to `msConfigurationItem::removeLibCells(const std::set<ndmModule*, ndmObjPtrCmpType>&)` (`mscts/drivers/msDrivers.h:214`, defined `mscts/drivers/msDrivers.cc:1741`), which is a different overload from `msCstrDesign::IrregGroup::removeLibCells` (`mscts/msutil/msCstrDesign.h:880`). So no FP there, and the `msCstrDesign` `toRemove` family is dismissed separately as membership-only.
- Most important check: I did **not** accept this as real merely because a `set*` mutation is in the loop. A per-element mutation that stamps the same value on each element's own object is order-insensitive, and that is exactly how I dismissed the very similar `setAttributeOnPorts` loop at `mscts/msui/msuiCreateClockDrivers.cc:1110` down to LOW. I read both loop bodies to the closing brace and kept this finding only because of the mid-loop `return` at `mscts/drivers/msDrivers.cc:11659` and `:11683`, which makes the processed *subset* order-dependent.
- Verified the write is real database state and not a scratch object: `refBlock->setOuterKeepoutMargin(ndmKeepout::HARD, ...)` at `mscts/drivers/msDrivers.cc:11666` targets the block of `libCell->getDesign()->getAlternateView(ndmView::TYPE_FRAME)`, i.e. the reference library's frame block, shared by every instance of that reference.
- Ruled out dead code: all nine sites are live. Both consumers have real callers (`mscts/drivers/msDrivers.cc:1611`, `:2328`, `mscts/drivers/msAutoTapFlow.cc:1323`, `:1343`, `mscts/msgts/msgtsFlow.cc:764`, `:1196`, `:5154`), none is inside `#if 0`/`#ifdef`, and I confirmed `msgtsOptions::getLibCells()` has a live consumer at `mscts/msgts/msgtsFlow.cc:758`. This matters because I did dismiss a structurally similar map in this same file as dead - `connectUnassignedLoads` (`mscts/drivers/msDrivers.cc:3330`) has no caller anywhere in the tree - so "declared and defined" was not taken as sufficient.
- Confirmed the option gate is a genuine user switch and recorded it, rather than assuming the code always runs: `htree_cell_keepout_factor`, `MSUI_BASIC`, default `""` (`mscts/msui/msuiAppOptions.cc:3882-3885`). This is why the severity is MEDIUM and not HIGH.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/mscts/drivers/msDrivers.cc`
- **Line drift:** this file moved ~+255 lines between the audited snapshot and depot `main`; the snapshot's `:8189` region maps to depot `:8447`, and `compareHierDepth` maps to depot `:8386-8395`.
- **Primary logic (annotate):** CL `6890358` owns both the `std::sort(..., compareHierDepth)` call and the `// convert map to vector for deterministic behaviour` comment.
- **Describe summary:** CL `6890358` by **`sumanc`**, 2021-09-17 — *"Handle hierarchy with no buufer. PRS NA"*.
- **CMT chain:** `[ORIG_CLIENT:sumanc-nwtn-21.06-sp][CMT][merge from //synopsys/nwtn/s/dev@6890245]` — original authoring user is **`sumanc`**.
- **Notes:** the same CL introduced the determinism intent *and* the incomplete depth-only comparator, so the author of the mitigation is the right reviewer for completing it.

---

### Issue 1.2.3 — MV-aware level balancing inserts buffers per power domain in std::map<ndmPowerDomain*> address order

- **File:** `mscts/msmesh/msLevelBalancer.cc:1745` (col 1)
- **Pattern:** 1.2 — std::set / std::map with pointer key, default comparator
- **Category:** container
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`msLevelBalancer::insertBuffersByPowerDomain()` groups the loads of one level-balancer node by power domain into `std::map<ndmPowerDomain*, TermToUnsignedMap> domainToLoads` (`mscts/msmesh/msLevelBalancer.cc:1745`). The key is `ndmPowerDomain*` with the default `std::less<ndmPowerDomain*>`, so the map is ordered by the address of the power-domain objects.

The value type `TermToUnsignedMap` is itself deterministic - `std::map<ndmTerm *, unsigned, ndmObjPtrCmpType>` (`mscts/msmesh/msLevelBalancer.h:63`) - so the loads *within* a domain are handled in a stable order. Only the order of the domains themselves is non-deterministic, and that order is the order in which buffers are physically inserted into the design.

**Realness:** `real`

**Downstream observability proof:**

**Hop 1 - declaration.** `std::map<ndmPowerDomain*, TermToUnsignedMap> domainToLoads` at `mscts/msmesh/msLevelBalancer.cc:1745`, populated at `:1758` from `loadInst->getPowerDomain()`.

**Hop 2 - ND iteration.** `mscts/msmesh/msLevelBalancer.cc:1770` iterates the map. There is no snapshot and no sort between the declaration and this loop.

**Hop 3 - database mutation sink.** `mscts/msmesh/msLevelBalancer.cc:1791` calls `insertBuffers(node, driver, domainLoadVsBufferCount, clock, lbNode->getLBTree(), domainBufferCount, targetVA, checkOnly)` once per domain. That resolves to `msLevelBalancer::insertBuffers(msTreeNode*, ndmTerm*, TermToUnsignedMap&, cstrClock, msLBTree*, ...)` (`mscts/msmesh/msLevelBalancer.cc:1868`), which forwards to `insertBuffersMultiDriver` (`mscts/msmesh/msLevelBalancer.cc:1906`, defined at `:1931`) and to the load-level `insertBuffers(...)` overload (`mscts/msmesh/msLevelBalancer.cc:1927`, defined at `:2030`). Buffer instances are created there, named from the prefix built at `mscts/msmesh/msLevelBalancer.cc:2053` (`"mscts_levelize_"` or `getInfra()->getUserPrefix()+"_"`), and placed into a hierarchy chosen at `mscts/msmesh/msLevelBalancer.cc:2075`.

Why the order is observable rather than merely cosmetic: buffer insertion is stateful. Each per-domain call creates instances that occupy legal sites and consume name suffixes, so the domain processed first gets first claim on both. Two runs that visit `{PD_A, PD_B}` in opposite orders therefore produce different instance names and different placements for the same logical result.

**Hop 4 - aggregated result feeds the caller's control flow.** `totalInsertedBuffers` (`mscts/msmesh/msLevelBalancer.cc:1796`) is added to the caller's `inserted_buf_count` at `:1812`, and `anyDomainSuccess` (`:1803`) becomes the return value at `:1813`. The caller `msLevelBalancer::insertBuffers(msLBTreeNode*, ...)` returns that to `mscts/msmesh/msLevelBalancer.cc:1709`, where failure aborts balancing of the node (`:1714`) and success marks it balanced via `balancedNodes.insert(lbNode->getTreeNode())` at `:1719`. Because a partially-successful set of per-domain insertions can leave the design in different states depending on which domain ran before the failure, the node's balanced/not-balanced outcome is reachable from the ND order too.

**Controls / gating:**

Two conditions, both checked at the single call site `mscts/msmesh/msLevelBalancer.cc:1835`:

```cpp
// mscts/msmesh/msLevelBalancer.cc:1826  msLevelBalancer::insertBuffers(msLBTreeNode*, ...)
  // Enhanced MV-aware processing - filter loads by power domains
  if (getAppOptions().enableMVAwareLevelBalancing && lbNode->isCrossingMVBoundary()) {
    return insertBuffersByPowerDomain(lbNode, node, driver, loadVsBufferCount, clock,
                                      inserted_buf_count, checkOnly);
  }
```

1. App option `enable_mv_aware_level_balancing`:

```cpp
// mscts/msui/msuiAppOptions.cc:1412
  enableMVAwareLevelBalancing =
    initAppOption<bool>(catMultisource, "enable_mv_aware_level_balancing",
                        "true or false: enable multi-voltage aware level balancing with domain boundary detection",
                        /*default*/ false, MSUI_HIDDEN, design);
```

This is `MSUI_HIDDEN` and defaults to **false**, so the whole function is unreachable on a default run.

2. `lbNode->isCrossingMVBoundary()` - the level-balancer node must straddle a multi-voltage boundary.

3. Data condition for the ordering to matter: the node's loads must resolve to **two or more distinct power domains** at `mscts/msmesh/msLevelBalancer.cc:1757`. With a single domain the map has one entry and the iteration is trivially stable.

Also note the early exit at `mscts/msmesh/msLevelBalancer.cc:1705`: nothing runs if `loadsNBufferCount` is empty or the node is already in `balancedNodes`.

Severity is MEDIUM specifically because of the hidden, default-off option - if `enable_mv_aware_level_balancing` is ever promoted to default-on, this becomes HIGH, since buffer insertion is squarely on the level-balancing hot path and writes the database.

**Performance-aware fix direction:**

The container is keyed by power domain, so its size is the number of distinct power domains touched by one level-balancer node - single digits in practice. The function is called once per MV-crossing node, and each iteration already performs `getInfra()->getVoltageArea()` plus a full buffer-insertion pass, which is orders of magnitude more expensive than any key comparison.

No fix changes lookup complexity. `domainToLoads` is used only with `operator[]` at `mscts/msmesh/msLevelBalancer.cc:1758`, `size()` at `:1762`, and the one traversal at `:1770`, so swapping `std::less<ndmPowerDomain*>` for `ndmObjPtrCmpType` keeps O(log D) insert and lookup and costs one extra id load per compare.

One cost worth flagging that is *not* introduced by the fix but sits right next to it: `mscts/msmesh/msLevelBalancer.cc:1772` already deep-copies the whole `TermToUnsignedMap` per domain (`TermToUnsignedMap domainLoadVsBufferCount = domainPair.second; // Make a copy`). Version A's key snapshot adds only a vector of `ndmPowerDomain*` on top of that, which is negligible by comparison. Do not be tempted to "fix" the ordering by copying the values again.

Runtime benchmarking is not needed. QoR benchmarking is needed only for MV designs run with `enable_mv_aware_level_balancing true`, and on those the fix will change buffer names and placements by design; the check to run is that two identical runs now match, and that the QoR delta versus the old (arbitrary) order is neutral on average.

**Current code:**

```cpp
mscts/msmesh/msLevelBalancer.cc
  1744 |   // Group loads by their power domains
> 1745 |   std::map<ndmPowerDomain*, TermToUnsignedMap> domainToLoads;   // default std::less<ndmPowerDomain*>
  1746 | 
  1747 |   for (const auto& loadPair : loadVsBufferCount) {
  1748 |     ndmTerm* load = loadPair.first;
  1749 |     unsigned bufCount = loadPair.second;
  1752 |     ndmInst* loadInst = load->toConn()->getInst();
  1757 |     ndmPowerDomain* loadPD = loadInst->getPowerDomain();
  1758 |     domainToLoads[loadPD][load] = bufCount;
  1759 |   }
  ...
  1767 |   bool anyDomainSuccess = false;
  1768 |   unsigned totalInsertedBuffers = 0;
  1769 | 
> 1770 |   for (const auto& domainPair : domainToLoads) {                // <-- ND iteration order
  1771 |     ndmPowerDomain* targetPD = domainPair.first;
  1772 |     TermToUnsignedMap domainLoadVsBufferCount = domainPair.second; // Make a copy
  1774 |     ctsVoltageArea targetVA;
  1775 |     if (targetPD) {
  1776 |       targetVA = getInfra()->getVoltageArea(targetPD);
  1777 |     } else {
  1779 |       targetVA = getInfra()->getVoltageArea(node->getInst());
  1780 |     }
  1789 |     unsigned domainBufferCount = 0;
  1790 | 
> 1791 |     bool domainSuccess = insertBuffers(node, driver, domainLoadVsBufferCount, clock, 
  1792 |                                       lbNode->getLBTree(), domainBufferCount, 
  1793 |                                       targetVA, checkOnly);        // <-- DB MUTATION
  1794 | 
  1795 |     if (domainSuccess) {
  1796 |       totalInsertedBuffers += domainBufferCount;
  1803 |       anyDomainSuccess = true;
  1809 |     }
  1810 |   }
  1811 | 
  1812 |   inserted_buf_count += totalInsertedBuffers;
  1813 |   return anyDomainSuccess;

mscts/msmesh/msLevelBalancer.h
    63 |   typedef std::map<ndmTerm *, unsigned, ndmObjPtrCmpType>  TermToUnsignedMap;  // values ARE stable
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): snapshot the domain keys and sort by a stable id
// immediately before the loop that performs insertion.
// mscts/msmesh/msLevelBalancer.cc:1766
  // Process each domain separately
  bool anyDomainSuccess = false;
  unsigned totalInsertedBuffers = 0;

  // Buffer insertion is stateful (names, legal sites), so the domain visit
  // order is observable. Canonicalise it.
  std::vector<ndmPowerDomain*> domainVec;
  domainVec.reserve(domainToLoads.size());
  for (const auto& domainPair : domainToLoads) {
    domainVec.push_back(domainPair.first);
  }
  std::sort(domainVec.begin(), domainVec.end(),
            [](ndmPowerDomain* a, ndmPowerDomain* b) {
              // targetPD may legitimately be NULL (see the fallback at :1778)
              if (!a || !b) return (a < b) && (a == 0);
              return a->getIdLong() < b->getIdLong();
            });

  for (ndmPowerDomain* targetPD : domainVec) {
    TermToUnsignedMap domainLoadVsBufferCount = domainToLoads[targetPD]; // Make a copy
    ...                                                                  // body unchanged from :1773
  }
```

**Version B (robust):**

```cpp
// Version B (robust): give the map the project deterministic comparator, the
// same way TermToUnsignedMap already does (msLevelBalancer.h:63).
// mscts/msmesh/msLevelBalancer.cc:1745
  // Group loads by their power domains
  std::map<ndmPowerDomain*, TermToUnsignedMap, ndmObjPtrCmpType> domainToLoads;

// Nothing else in the function changes: :1758 (operator[]), :1762 (size) and
// the range-for at :1770 all keep working, and the loop now visits domains in
// a run-stable id order.
//
// If a NULL power domain can be a key here (the fallback at :1778 suggests it
// can), confirm ndmObjectHandleNS::compareObjPtr tolerates NULL before
// adopting this as-is; compareObjPtr dereferences its arguments -- the comment
// at msuiReconnectClockDrivers.cc:961-962 says exactly that -- so either
// guard the insert at :1758 or prefer Version A/C.
```

**Version C:**

```cpp
// Version C: re-key by a stable id, which also sidesteps the NULL-key
// question entirely.
// mscts/msmesh/msLevelBalancer.cc:1745
  // Group loads by their power domains, keyed by stable id (0 == no domain)
  std::map<ndmObjectId, TermToUnsignedMap> domainToLoads;
  std::map<ndmObjectId, ndmPowerDomain*>   idToDomain;

  for (const auto& loadPair : loadVsBufferCount) {
    ndmTerm* load = loadPair.first;
    unsigned bufCount = loadPair.second;
    ndmInst* loadInst = load->toConn()->getInst();
    if (!loadInst) {
      continue;
    }
    ndmPowerDomain* loadPD = loadInst->getPowerDomain();
    const ndmObjectId pdId = (loadPD ? loadPD->getIdLong() : 0);
    idToDomain[pdId] = loadPD;
    domainToLoads[pdId][load] = bufCount;
  }

  for (const auto& domainPair : domainToLoads) {   // stable id order
    ndmPowerDomain* targetPD = idToDomain[domainPair.first];
    TermToUnsignedMap domainLoadVsBufferCount = domainPair.second; // Make a copy
    ...                                                            // body unchanged
  }
```

**Why this fix:**

**Recommend Version C**, with Version A as the low-risk alternative.

This is the one finding in this slice where I would not reach for `ndmObjPtrCmpType` first. `mscts/msmesh/msLevelBalancer.cc:1775-1780` explicitly handles `targetPD == NULL` (`if (targetPD) ... else` falls back to the driver's voltage area), which means a NULL power domain can be a key in this map. `ndmObjectHandleNS::compareObjPtr` dereferences the pointers it compares - the comment at `mscts/msui/msuiReconnectClockDrivers.cc:961-962` says so directly, and that is why that file deliberately keeps a raw-pointer set. So Version B risks trading a determinism bug for a null dereference, and I am not willing to recommend it without first reading `compareObjPtr`, which is outside this snapshot.

Version C keys on `getIdLong()` with `0` reserved for "no domain", which is total, NULL-safe, needs no comparator, and keeps the domain order stable by construction rather than by a sort that a later edit could drop. The cost is one extra small `idToDomain` map, which is nothing next to the per-domain `TermToUnsignedMap` copy already happening at `:1772`.

Version A is the right pick if the reviewer wants the change confined to a few lines just above the loop; its NULL handling is explicit in the lambda. It is slightly more fragile than C only because the invariant lives in a sort call rather than in the container type.

Worth noting for the fix author: the loads *inside* each domain are already deterministic, because `TermToUnsignedMap` is `std::map<ndmTerm *, unsigned, ndmObjPtrCmpType>` (`mscts/msmesh/msLevelBalancer.h:63`). Only the outer key needs attention, so this is a genuinely small fix.

**False-positive check:**

- Confirmed the outer key is a raw pointer with a defaulted comparator: `std::map<ndmPowerDomain*, TermToUnsignedMap> domainToLoads` at `mscts/msmesh/msLevelBalancer.cc:1745`, no third template argument. Deliberately checked the *value* type as well and found it is already stable (`TermToUnsignedMap` = `std::map<ndmTerm *, unsigned, ndmObjPtrCmpType>`, `mscts/msmesh/msLevelBalancer.h:63`), so I scoped the finding to the domain order only rather than claiming the load order is also ND.
- Verified the map is actually traversed and not just used as a lookup table. The three uses are `operator[]` at `:1758`, `size()` at `:1762`, and the range-for at `:1770`. This is the distinction that pushed several other candidates in this slice into `latent-only` - for example `_wireDelays` (`mscts/msmesh/msmtmesh/msmtLatencyFlowProblemGenerator.h:284`) and `_targetLocTable` (`mscts/fishbone/fbPlacer.h:56`) are never traversed at all.
- Confirmed there is no canonicalisation between declaration and traversal: no `std::sort`, no `std::stable_sort`, no snapshot into a stable container anywhere in `:1745-1770`. This is what separates it from the neutralised cases I dismissed, such as `_hashTblDrivers` (`mscts/msmesh/msActivityRelocator.h:124`), whose traversal at `mscts/msmesh/msActivityRelocator.cc:456-458` only fills the stable `TreeNodeSet allDrivers` before any consumer runs.
- Confirmed the sink is a real mutation and not a per-key independent write. I followed `insertBuffers` from `mscts/msmesh/msLevelBalancer.cc:1791` into the overload at `:1868`, then to `insertBuffersMultiDriver` at `:1931` and the load-level overload at `:2030`, and found instance creation with a shared name prefix at `:2053` and hierarchy selection at `:2075`. Per-domain calls are therefore coupled through names and placement sites, which is why this is not order-insensitive the way `restoreDesignType()`'s `_cellTypes` loop (`mscts/drivers/msDrivers.cc:292-298`) is.
- Ruled out dead code: `insertBuffersByPowerDomain` has a live caller at `mscts/msmesh/msLevelBalancer.cc:1836`, is not inside any `#if`/`#ifdef`, and carries no build-macro exclusion.
- Located the real gate before assigning severity, rather than assuming the path always runs: `getAppOptions().enableMVAwareLevelBalancing && lbNode->isCrossingMVBoundary()` at `mscts/msmesh/msLevelBalancer.cc:1835`, with the option defined `MSUI_HIDDEN`, default `false`, at `mscts/msui/msuiAppOptions.cc:1412-1415`. That default-off hidden option is the sole reason this is MEDIUM rather than HIGH.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/mscts/msmesh/msLevelBalancer.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 1.3 — std::unordered_set / unordered_map with pointer key, default hash  (×2)

### Issue 1.3.1 — Endpoint-optimization seed priorities are numbered by unordered_set<ndmTerm*> iteration, making the driver optimization order address-dependent

- **File:** `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32` (col 1)
- **Pattern:** 1.3 — std::unordered_set / unordered_map with pointer key, default hash
- **Category:** container
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ctoEndpointOptimizationData::_targetEndpoints` is a `std::unordered_set<ndmTerm*>` with the default `std::hash<ndmTerm*>`, so its iteration order is a function of terminal addresses.

`ctomtGlsProblemGenerator::initTargetDriverCandidate()` iterates it and assigns a *sequential priority number* as it goes:

```
715 |   for (auto& ep : targetEndpoints) {
716 |     ndmTerm* driverTerm = _global.getFaninTerm(ep, 1, _global.getTimerInterf());
...
723 |     if (valid) {
724 |       _candidates.insert(std::make_pair( std::make_pair(dNum, dNum), driverTerm));
725 |       dNum++;
```

`_candidates` is `std::map<CKEY, ndmTerm*>` with `CKEY = std::pair<int,int> = (dNum, dNum)` (`ctomtGlsProblemGenerator.h:486`). The map is therefore ordered by `dNum`, and `dNum` is handed out in unordered-set iteration order. The drain loop at `ctomtGlsProblemGenerator.cc:1208-1297` consumes `_candidates` front-to-back to build xform problems, applying an overlap tracer and several `_candidates.erase(curIt)` filters as it goes. Because the overlap test is stateful (`tracer.setOverlapDis(2)`, `bugFixSeedOverlapCheck`), which seeds survive depends on which came first.

Note the codebase is already aware of this hazard for the sibling container: `ctomtGlsCostCalc.cc:801-805` copies `_driverToEndpointSetMap.at(driver)` into a `termSetType` (`std::set<ndmTerm*, ndmObjPtrCmpType>`) with the comment *"to shut up coverity for nd access to unordered_set container / dont have time to refactor this now :)"*. The same mitigation was never applied at the problem-generator site.

**Realness:** `real`

**Downstream observability proof:**

1. `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:50` - `_targetEndpoints` is `std::unordered_set<ndmTerm*>`, default `std::hash<ndmTerm*>` -> bucket index derived from the terminal address.
2. `ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1799` - constructed from `preponeData.getPreponeEps()` inside `prepareEndpointFlow()`.
3. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:709,715` - `initTargetDriverCandidate()` obtains it and iterates with a range-for.
4. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:724-725` - each accepted driver is inserted into `_candidates` with key `(dNum, dNum)` and `dNum` is post-incremented, so the key *is* the visit index.
5. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:486` - `_candidates` is `std::map<CKEY, ndmTerm*>`, i.e. sorted by that index. The map is deterministic given the indices, but the indices are not.
6. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:1208-1297` - the drain loop walks `_candidates` in key order, runs `tracer` overlap checks (`:1198-1202`) and `isOnCritialPath` (`:1272`), and erases candidates that fail. Because the tracer state and the design state both evolve as seeds are accepted, the surviving seed set is order-sensitive.
7. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:241` - the surviving problems get `p->setTargetDelayMap(_targetDelayMap)` and are handed to the GLS xform engine, which sizes/relocates/buffers real instances.

Sink class: algorithmic first-match / best-candidate selection feeding netlist transforms.

Explicitly NOT part of this chain (checked, all order-insensitive):
- `ctomtGlsFlow.cc:1835` iterates `targetEps` but only writes `targetLatencyMap[currClkCornerType][ep]`, one distinct key per iteration.
- `ctomtGlsResultIntegrator.cc:1198` iterates `targetEndpoints` inside an existential `return true` - the boolean result is the same regardless of order.
- `ctomtClone.cc:690` uses `find()` only.
- `ctomtGlsCostCalc.cc:799-805` copies into a stable `termSetType` before the float accumulation at `:819` - already neutralized.

**Controls / gating:**

- Flow gate: `ctomtGlsProblemGenerator::initializeCandidates()` only calls `initTargetDriverCandidate()` when `_flowType == CTO_ENDPOINT` (`ctomtGlsProblemGenerator.cc:567-570`).
- `CTO_ENDPOINT` is entered via `ctomtGlsFlow::prepareEndpointFlow()` (`ctomtGlsFlow.cc:1785`), which sets `_state.optType = CTO_ENDPOINT` and returns early unless `handler.hasDataProvider<ctsIfsNS::ctsIfsPreponeData>()` and `preponeData.getPreponeEps()` is non-empty (`ctomtGlsFlow.cc:1794-1798`). So the whole path requires IFS prepone data to be present - an uncommon, feature-specific flow.
- Data condition: >= 2 target endpoints mapping to >= 2 distinct valid driver terms. With a single endpoint the ordering is trivially stable.
- No `getAppOption` / `appOption` string guards this specific function; the gate is the IFS data provider plus the flow type. I searched `getAppOption`, `ctomtAppOptions::`, `ctsEnvVariable::` in `ctomtGlsProblemGenerator.cc` around `initTargetDriverCandidate` and found none - the only nearby knobs (`get_gls_use_unified_tiers`, `get_gls_generator_strict_check`) apply to the non-endpoint branches.
- Root-cause note: `preponeData.getPreponeEps()` may itself already be an unordered container. That source lives in the IFS layer and is outside this snapshot, so the truly minimal fix might belong there; the fix versions below are written against what is in scope.

**Performance-aware fix direction:**

`initTargetDriverCandidate()` runs once per GLS endpoint-optimization round, over the target-endpoint list only (typically tens to low hundreds of endpoints, not the full clock tree). It is not an inner loop.

- Version A adds a `std::vector<ndmTerm*>` of size E plus one `O(E log E)` sort. Negligible: the same loop already calls `_global.getFaninTerm(ep, 1, timerInterf)` per endpoint, which is a timer graph query costing far more than a comparison.
- Version B changes `_targetEndpoints` from `unordered_set` to `std::set<ndmTerm*, ndmObjPtrCmpType>`. This IS an `O(1)` -> `O(log E)` downgrade for `find()`. The membership queries are at `ctomtClone.cc:692` (inside `divideSinksTargetEp`, called per clone attempt over `mgSinks`) and `ctomtGlsCostCalc.cc:825` (`targetTerms.find(...)` - already a `std::set`, unaffected). `divideSinksTargetEp` is the only warm caller; with E in the hundreds, `log E` is ~8 comparisons of two `unsigned long` IDs. I would still call this out in review rather than assume it is free.
- Version C (re-key by `ndmTermId`) has the same `O(log E)` profile as B but avoids holding raw `ndmTerm*` across transforms that may delete terminals.

Recommendation: ship Version A. It leaves every container and every lookup complexity untouched and confines the change to the one function that observes order. QoR benchmarking is needed on an IFS-prepone endpoint-optimization regression, since the seed order (and therefore which seeds survive the overlap filter) will change.

**Additional occurrences of the same root cause:**

- `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:43 (getTargetEndpoints accessor)`
- `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:47 / :56 (_driverToEndpointSetMap, neutralized at the one consumer that iterates it)`
- `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:715 (the iteration)`
- `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:724 (dNum assignment)`

**Current code:**

```cpp
ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h
     30 |     ctoEndpointOptimizationData() {}
>    32 |     ctoEndpointOptimizationData(const std::unordered_set<ndmTerm*>& targetEndpoints,
     33 |                                 const std::unordered_map<sclkCornerType, std::unordered_map<ndmTerm*, float>>& targetEndpointsOffset)
     34 |         : _targetEndpoints(targetEndpoints),
>    43 |     const std::unordered_set<ndmTerm*>& getTargetEndpoints() const { return _targetEndpoints; }
>    47 |     const std::unordered_map<ndmTerm*, std::unordered_set<ndmTerm*>>& getDriverToEndpointSetMap() const { return _driverToEndpointSetMap; }
     48 |   private:
     49 |     // target endpoints for endpoint optimization
>    50 |     std::unordered_set<ndmTerm*> _targetEndpoints;
     56 |     std::unordered_map<ndmTerm*, std::unordered_set<ndmTerm*>> _driverToEndpointSetMap;

ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc  (the ND ordering)
    707 | ctomtGlsProblemGenerator::initTargetDriverCandidate()
    708 | {
    709 |   const auto& targetEndpoints = _endpointOptimizationData->getTargetEndpoints();
    710 |   int dNum = 0;
    711 |   _endpointOptimizationData->clearDriverToEndpointSetMap();
    712 |   if (targetEndpoints.empty()) {
    713 |     return;
    714 |   }
>   715 |   for (auto& ep : targetEndpoints) {          // <-- address-ordered iteration
    716 |     ndmTerm* driverTerm = _global.getFaninTerm(ep, 1, _global.getTimerInterf());
    717 |     if (!driverTerm) { ... continue; }
    721 |     _endpointOptimizationData->insertDriverToEndpointSetMap(driverTerm, ep);
    722 |     bool valid = checkValidCandidate(driverTerm);
    723 |     if (valid) {
>   724 |       _candidates.insert(std::make_pair( std::make_pair(dNum, dNum), driverTerm));
>   725 |       dNum++;                                 // <-- priority = visit index
    726 |     }
    727 |   }

ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h
    485 |    //std::map<CKEY, ndmTerm*, std::greater<CKEY> > _candidates; // bottomup
>   486 |    std::map<CKEY, ndmTerm* > _candidates; // topdown

ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc  (the consumer)
>  1208 |   std::map<CKEY, ndmTerm*>::iterator it = _candidates.begin();
   1209 |   size_t initQueueSize = _candidates.size();
   1210 |   while(_candidates.empty() == false) {
   1211 |     std::map<CKEY, ndmTerm*>::iterator curIt = it;
   1212 |     it++;
   1217 |     ndmTerm* driver = curIt->second;
   1219 |       _candidates.erase(curIt);
   1231 |         _candidates.erase(curIt);
   1241 |       _candidates.erase(curIt);
   1257 |         _candidates.erase(curIt);
   1271 |       std::map<CKEY, ndmTerm*>::iterator itFanout = findCandidateInMap(_candidates, load);
   1272 |       if (itFanout != _candidates.end() && isOnCritialPath(load, &sharedSccCache)) {
   1290 |       _candidates.erase(curIt);
   1296 |     _candidates.erase(curIt);

ctscto/ctosc/ctomt/gls/ctomtGlsCostCalc.cc  (how the sibling container was mitigated)
    799 |   const auto & targetEndpoints = _endpointOptimizationData->getDriverToEndpointSetMap().at(driver);
    800 |   termSetType targetTerms;
    801 |   // to shut up coverity for nd access to unordered_set container
    802 |   // dont have time to refactor this now :)
    803 |   for (const auto& term : targetEndpoints) {
    804 |     targetTerms.insert(const_cast<ndmTerm*>(term));
    805 |   }
```

**Suggested fix:**

**Version A (minimal):**

```cpp
// Version A (minimal): keep the O(1) set, canonicalise only the numbering loop.
// ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:707-728
void
ctomtGlsProblemGenerator::initTargetDriverCandidate()
{
  const auto& targetEndpoints = _endpointOptimizationData->getTargetEndpoints();
  int dNum = 0;
  _endpointOptimizationData->clearDriverToEndpointSetMap();
  if (targetEndpoints.empty()) {
    return;
  }
  // dNum below becomes the _candidates priority key, so the visit order is
  // observable.  Sort by stable ndm object id instead of by address.
  std::vector<ndmTerm*> orderedEps(targetEndpoints.begin(), targetEndpoints.end());
  std::sort(orderedEps.begin(), orderedEps.end(), ndmObjectHandleNS::compareObjPtr{});

  for (ndmTerm* ep : orderedEps) {
    ndmTerm* driverTerm = _global.getFaninTerm(ep, 1, _global.getTimerInterf());
    if (!driverTerm) {
      tmctomtGlsGeneratorBasic.print("[DBG] No driver found for endpoint %s\n", ep->getFullName().c_str());
      continue;
    }
    _endpointOptimizationData->insertDriverToEndpointSetMap(driverTerm, ep);
    bool valid = checkValidCandidate(driverTerm);
    if (valid) {
      _candidates.insert(std::make_pair( std::make_pair(dNum, dNum), driverTerm));
      dNum++;
    }
  }
  return;
}
```

**Version B (robust):**

```cpp
// Version B (robust): make the container itself deterministic.
// ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32, 43, 50
//
// termSetType == std::set<ndmTerm*, ndmObjPtrCmpType> (ctsutil/ctsTypes.h), i.e.
// ndmObjectHandleNS::compareObjPtr.  ctomtGlsCostCalc.cc:800 already converts to
// exactly this type to work around the same problem, so adopting it at the source
// lets that copy loop be deleted.
// Cost: find() goes O(1) -> O(log E); see performance_note_md.

    ctoEndpointOptimizationData(const termSetType& targetEndpoints,
                                const std::unordered_map<sclkCornerType, std::unordered_map<ndmTerm*, float>>& targetEndpointsOffset)
        : _targetEndpoints(targetEndpoints),
          _targetEndpointsOffset(targetEndpointsOffset) {}

    const termSetType& getTargetEndpoints() const { return _targetEndpoints; }

    // also re-type the per-driver fanout index so its iteration in
    // ctomtGlsCostCalc.cc:803 is stable without the manual copy:
    const std::map<ndmTerm*, termSetType, ndmObjPtrCmpType>&
      getDriverToEndpointSetMap() const { return _driverToEndpointSetMap; }

  private:
    termSetType _targetEndpoints;
    std::map<ndmTerm*, termSetType, ndmObjPtrCmpType> _driverToEndpointSetMap;

// If the O(log E) lookup cost in divideSinksTargetEp() is unacceptable, keep the
// unordered_set for membership AND add a sorted vector for the ordered walk:
//     std::unordered_set<ndmTerm*> _targetEndpoints;      // membership, O(1)
//     std::vector<ndmTerm*>        _targetEndpointOrder;  // id-sorted, for iteration
```

**Version C:**

```cpp
// Version C: re-key by stable ID, keeping O(1) hashing.
// ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:50
//
// dosContainer::keyHash() is the project's ndm-id-based pointer hash
// (see ctsutil/ctsTypes.h:701 and ctssch/ctsPowerDrivenGateRelocator.h:285
// for an existing unordered_map<ndmInst*, ndmInst*, dosContainer::keyHash>).
// Bucket assignment becomes id-derived, so iteration order is reproducible
// while find() stays O(1).

#include <util/dosContainer.h>   // for keyHash

    std::unordered_set<ndmTerm*, dosContainer::keyHash> _targetEndpoints;
    std::unordered_map<ndmTerm*, std::unordered_set<ndmTerm*, dosContainer::keyHash>,
                       dosContainer::keyHash> _driverToEndpointSetMap;

// Caveat worth stating in review: an id-based hash gives a *reproducible* order,
// not a *sorted* one, and the order still shifts if the bucket count changes
// (different endpoint count -> different rehash points).  That is fine for
// run-to-run reproducibility on a fixed design, which is what ND triage asks for,
// but Version A is the stronger guarantee.
```

**Why this fix:**

What makes this real rather than latent is the `dNum++` inside the iteration: the loop does not just visit endpoints, it stamps each one with its visit index and stores that index as the sort key of `_candidates`. So the ND is laundered through a `std::map` that *looks* deterministic. The consuming drain loop is stateful - it erases candidates based on an overlap tracer and on criticality that the already-accepted seeds have changed - so a different starting order yields a different surviving seed set and different transforms. MEDIUM rather than HIGH because reaching it requires the IFS-prepone endpoint-optimization flow, which is not the default CTS path.

**False-positive check:**

Checked and ruled out:
- Really default-hashed: `std::unordered_set<ndmTerm*>` at ctomtEndpointTypes.h:50 with no third template argument.
- Not lookup-only: `ctomtGlsProblemGenerator.cc:715` is a range-for over the set, not a `find`. I grepped all four consumers of `getTargetEndpoints()` (`ctomtGlsResultIntegrator.cc:1189`, `ctomtGlsProblemGenerator.cc:709`, `ctomtGlsFlow.cc:1819`, `ctomtClone.cc:690`) and read each; three are order-insensitive and are listed in downstream_observability_md.
- Not neutralized: unlike the sibling path at `ctomtGlsCostCalc.cc:800-805`, there is no copy into `termSetType` before the numbering.
- Not dead: `initTargetDriverCandidate()` is called at `ctomtGlsProblemGenerator.cc:568`; `_endpointOptimizationData` is populated at `ctomtGlsFlow.cc:1799`. No `#if`/`#ifdef` exclusion.
- Not already ID-ordered: `CKEY` is `std::pair<int,int>` built from `dNum`, not from any ndm ID. Verified `_candidates` is `std::map<CKEY, ndmTerm*>` at `ctomtGlsProblemGenerator.h:486` (the `std::greater<CKEY>` bottom-up variant on line 485 is commented out).
- What I could NOT verify: whether the drain loop's overlap/criticality filters actually reject a *different* seed for a given real design, versus accepting all candidates regardless of order. That would need a two-run experiment. The mechanism (stateful filter over an ND-ordered queue) is established from source; the magnitude is not.
- `ctomtEndpointTypes.h:47` (`_driverToEndpointSetMap`) is included in this finding as an occurrence, but on its own it is neutralized at its only iterating consumer; it is the same root object and should be fixed together.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Issue 1.3.2 — IFS prepone endpoint set is an unordered_set<ndmTerm*>; its hash order becomes the GLS endpoint-optimization candidate numbering

- **File:** `ctsmisc/ctsIfsDataType.h:32` (col 1)
- **Pattern:** 1.3 — std::unordered_set / unordered_map with pointer key, default hash
- **Category:** container
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ctsIfsPreponeData` carries the set of prepone endpoints across the CTS/CTO boundary as `std::unordered_set<ndmTerm*>` with the default `std::hash<ndmTerm*>`, which hashes the raw address. Bucket assignment - and therefore iteration order - changes with heap layout.

The set is produced in `ctsinterf/ctsIfsInterf.cc:2072` (`_preponeEps.emplace(currTerm)`), published at `ctsinterf/ctsIfsInterf.cc:2141`, handed to `ctoEndpointOptimizationData` at `ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1799`, and then **iterated** by `ctomtGlsProblemGenerator::initTargetDriverCandidate()`.

That loop assigns a sequential integer `dNum` per endpoint and uses it as the *key* of the `_candidates` work queue (`std::map<CKEY, ndmTerm*>` with `CKEY = std::pair<int,int>`). The queue is later drained in `dNum` order to generate GLS transformation problems, so the hash order of a pointer-keyed container decides the order in which clock drivers are buffered, sized, cloned and committed.

**Realness:** `real`

**Downstream observability proof:**

1. **Declaration** - `ctsmisc/ctsIfsDataType.h:32`: `std::unordered_set<ndmTerm*> _preponeEps` (default `std::hash<ndmTerm*>` = address hash). Same defect at the producing member, `ctsinterf/ctsIfsInterf.h:476`.
2. **Population** - `ctsinterf/ctsIfsInterf.cc:2072`: `_preponeEps.emplace(currTerm)` for every endpoint that successfully got a prepone balance point + latency.
3. **Publication** - `ctsinterf/ctsIfsInterf.cc:2141`: copied into a `ctsIfsPreponeData` and registered on the session's IFS data handler.
4. **Hand-off** - `ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1795-1799`: `prepareEndpointFlow()` reads it back and copies it into `ctoEndpointOptimizationData::_targetEndpoints` (`ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:50`, also an `std::unordered_set<ndmTerm*>`), so the address-hash ordering is preserved verbatim.
5. **Iteration** - `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:715`: `for (auto& ep : targetEndpoints)`.
6. **Order is captured as data** - `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:724-725`: `_candidates.insert({{dNum, dNum}, driverTerm}); dNum++;`. The hash position becomes the queue key. `_candidates` is `std::map<CKEY, ndmTerm*>` (`ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:486`), i.e. ordered by that number.
7. **Concrete sink (algorithmic ordering + netlist mutation)** - `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:1208-1297` drains `_candidates` from `begin()` and generates one GLS transformation problem per driver; `:1271-1272` makes an explicit **first-match / already-queued** decision (`findCandidateInMap(_candidates, load)` combined with `isOnCritialPath`), and `:1219/:1231/:1241/:1257/:1290/:1296` erase candidates as a function of that traversal. The problems produced drive `ctomtBuffer` / `ctomtClone` / sizing, which mutate the netlist, and `ctomtGlsResultIntegrator::commit()` persists the winners. Under a resource/iteration budget a different candidate order means a different set of committed transforms.
8. **Second iteration, benign** - `ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1835` also iterates the same set, but only writes `targetLatencyMap[currClkCornerType][ep] = epArrival - preponeOffset` - one independent key per endpoint, so that loop is order-insensitive and is **not** part of the proof.

**Controls / gating:**

- **Flow gate (hard)**: `ctomtGlsProblemGenerator::initializeCandidates()` only calls `initTargetDriverCandidate()` when `_flowType == CTO_ENDPOINT` (`ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc:567-570`). `_state.optType = CTO_ENDPOINT` is set in `ctomtGlsFlow::prepareEndpointFlow()` (`ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1789`). Outside the endpoint-optimization flow this code never runs.
- **Data gate**: `prepareEndpointFlow()` bails out at `ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc:1796-1798` when `getPreponeEps().empty()`, so the IFS prepone wrapper (`ctsIfsSetPreponeWrapper`) must actually have set prepone points. That in turn requires the MLE/IFS prepone path in `ctsinterf/ctsIfsInterf.cc` (a non-zero `currPreponeOffset` above `_resolution`, line 2044).
- **C++ data condition**: needs >= 2 prepone endpoints whose fanin drivers differ, and a GLS budget/stop condition that makes candidate order matter (stage iteration cap `ctomtAppOptions::get_gls_num_of_stage_iteration()`).
- **App options in the vicinity**: `ctomtAppOptions::get_gls_use_unified_tiers()`, `get_gls_latencyopt_for_skewopt_enhancement()`. I found no `getAppOption` string that independently disables the endpoint candidate path once `CTO_ENDPOINT` is active.

**Performance-aware fix direction:**

The set is used for membership at `ctscto/ctosc/ctomt/ctomtClone.cc:692` and iterated at `ctomtGlsProblemGenerator.cc:715` / `ctomtGlsFlow.cc:1835`.

- **Version A is free of complexity change**: keep the `unordered_set` (O(1) membership for `ctomtClone.cc:692` is preserved) and sort a `std::vector<ndmTerm*>` snapshot only inside `initTargetDriverCandidate()`. That adds one O(N log N) sort and one N-element vector per `initializeCandidates()` call, where N is the prepone endpoint count. It is **not** in an inner loop - the very next statement per element calls `_global.getFaninTerm(..., getTimerInterf())`, a timer query that dominates the comparison cost by orders of magnitude.
- **Version B does change complexity**: swapping to `std::set<ndmTerm*, ndmObjPtrCmpType>` turns the `ctomtClone.cc:692` membership test from O(1) to O(log N). `ctomtClone::...(mgSinks)` runs that test per sink per clone evaluation, so this is the one that genuinely needs measuring - prefer A or C over B here.
- **Version C keeps O(1)**: a custom hash over `getIdLong()` keeps the bucket lookup constant time. Note the precise claim: with a deterministic hash **and** a deterministic insertion sequence, libstdc++ `unordered_set` iteration is reproducible run-to-run because the bucket index is `hash % bucket_count` and both inputs become run-invariant. It is *not* sorted order, just stable order - which is all `dNum` needs.

**QoR benchmarking is needed** (candidate order changes => different committed transforms). Runtime benchmarking is only needed if Version B is chosen.

**Additional occurrences of the same root cause:**

- {'file': 'ctsmisc/ctsIfsDataType.h', 'line': 29, 'note': 'getPreponeEps() accessor - the scanner hit; same root cause'}
- {'file': 'ctsinterf/ctsIfsInterf.h', 'line': 476, 'note': "producing member _preponeEps, same defect (not in this slice's candidate list)"}
- {'file': 'ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h', 'line': 50, 'note': '_targetEndpoints, the copy that is actually iterated (outside this slice)'}

**Current code:**

```cpp
  -- declaration (this slice) --
   24 |   class ctsIfsPreponeData {
   27 |       ctsIfsPreponeData(const std::unordered_set<ndmTerm*>& preponeEps, const std::unordered_map<ctsNS::sclkCornerType, std::unordered_map<ndmTerm*, float>>& preponeOffsets)
   28 |       : _preponeEps(preponeEps), _preponeOffsets(preponeOffsets) {}
>  29 |       const std::unordered_set<ndmTerm*>& getPreponeEps() const { return _preponeEps; }
   31 |     private:
>  32 |       std::unordered_set<ndmTerm*> _preponeEps;      <== pointer key, default std::hash

  -- producer: ctsinterf/ctsIfsInterf.cc --
 2072 |   _preponeEps.emplace(currTerm);
 2141 |   handler.registerProvider<ctsIfsNS::ctsIfsPreponeData>(ctsIfsNS::ctsIfsPreponeData(_preponeEps, _preponeOffsets));
  (member decl: ctsinterf/ctsIfsInterf.h:476  std::unordered_set<ndmTerm*> _preponeEps;)

  -- hand-off: ctscto/ctosc/ctomt/gls/ctomtGlsFlow.cc --
 1794 |   if (handler.hasDataProvider<ctsIfsNS::ctsIfsPreponeData>()) {
 1795 |     auto& preponeData = handler.getData<ctsIfsNS::ctsIfsPreponeData>();
 1796 |     if (preponeData.getPreponeEps().empty()) {
 1797 |       return false;
 1798 |     }
 1799 |     _endpointOptimizationData = std::make_shared<ctoEndpointOptimizationData>(preponeData.getPreponeEps(), preponeData.getPreponeOffsets());

  -- the order-sensitive consumer: ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc --
  707 | ctomtGlsProblemGenerator::initTargetDriverCandidate()
  709 |   const auto& targetEndpoints = _endpointOptimizationData->getTargetEndpoints();
  710 |   int dNum = 0;
  712 |   if (targetEndpoints.empty()) {
  713 |     return;
  714 |   }
> 715 |   for (auto& ep : targetEndpoints) {          <== HASH-ORDER iteration
  716 |     ndmTerm* driverTerm = _global.getFaninTerm(ep, 1, _global.getTimerInterf());
  721 |     _endpointOptimizationData->insertDriverToEndpointSetMap(driverTerm, ep);
  722 |     bool valid = checkValidCandidate(driverTerm);
  723 |     if (valid) {
> 724 |       _candidates.insert(std::make_pair( std::make_pair(dNum, dNum), driverTerm));
> 725 |       dNum++;                                  <== sequence number == hash position
  726 |     }
  727 |   }

  -- the queue and its drain --
  (ctomtGlsProblemGenerator.h:486)  std::map<CKEY, ndmTerm* > _candidates; // topdown
 1208 |   std::map<CKEY, ndmTerm*>::iterator it = _candidates.begin();
 1210 |   while(_candidates.empty() == false) {
 1219 |       _candidates.erase(curIt);
 1271 |     std::map<CKEY, ndmTerm*>::iterator itFanout = findCandidateInMap(_candidates, load);
 1272 |     if (itFanout != _candidates.end() && isOnCritialPath(load, &sharedSccCache)) {
 1296 |     _candidates.erase(curIt);
```

**Suggested fix:**

_Site-specific fix variants were not provided; showing the generic pattern fix template instead._

**Provide a stable hash (and usually a stable equality):**
```cpp
struct StablePtrHash {
    template <class U>
    size_t operator()(const U* p) const {
        return p ? std::hash<uint64_t>{}(p->getIdLong()) : 0UL;
    }
};
std::unordered_set<T*, StablePtrHash> s;
```

**If iteration order matters, sort before iterating:**
```cpp
std::vector<T*> v(s.begin(), s.end());
std::sort(v.begin(), v.end(), ndmObjectHandleNS::compareObjPtr{});
for (T* x : v) { /* ... */ }
```

**Why this fix:**

The proof hinges on `dNum` at `ctomtGlsProblemGenerator.cc:725`. Most `unordered_set<T*>` in this slice are membership filters, where hash order is unobservable; here the iteration *position* is written into the key of a work queue that is subsequently drained in key order, so the address hash is laundered into a persistent processing order that survives into netlist-mutating transforms.

MEDIUM rather than HIGH because of the hard `_flowType == CTO_ENDPOINT` gate plus the `getPreponeEps().empty()` data gate - most runs never execute this loop. Inside the endpoint flow, however, the impact is HIGH-grade (candidate order for buffering/sizing/cloning), so I would not defer it below the `ctsAutoBalancePoint` finding by much.

**False-positive check:**

- **Hash confirmed default**: `ctsmisc/ctsIfsDataType.h:32` declares `std::unordered_set<ndmTerm*>` with a single template argument - no hash, no equality functor. Same at `ctsinterf/ctsIfsInterf.h:476` and `ctscto/.../ctomtEndpointTypes.h:50`. Contrast with the same-file sibling `std::unordered_map<ctsNS::sclkCornerType, ...>` (line 33), which is value-keyed and which I did not flag.
- **Not lookup-only**: I specifically checked whether the only use was `ctomtClone.cc:692`'s `find()`. It is not - there are two `for (auto& ep : ...)` loops (`ctomtGlsProblemGenerator.cc:715`, `ctomtGlsFlow.cc:1835`), and I discarded the second as order-insensitive rather than counting it.
- **Not neutralized**: no `std::sort`/`stable_sort` anywhere between the set and `dNum`; the vector `orderedEps` in my Version A does not exist today.
- **Copy preserves the defect**: verified the hand-off at `ctomtGlsFlow.cc:1799` copies into another default-hash `unordered_set`, so it does not re-order into anything canonical.
- **Not dead**: `initTargetDriverCandidate()` has a live caller at `ctomtGlsProblemGenerator.cc:568`; no `#if`/`#ifdef` exclusion; not under `test/`.
- **Honest limitation**: the sink lives in `ctscto/`, outside this slice's file list. I read those files directly in the same snapshot, so the chain is source-verified, but the fix spans three modules (`ctsmisc`, `ctsinterf`, `ctscto`) and must be landed together or Version B/C will silently re-hash by address at the `ctomtGlsFlow.cc:1799` copy.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctsmisc/ctsIfsDataType.h`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 1.5 — Random ops without deterministic seed  (×1)

### Issue 1.5.1 — CCD CG solver seeds candidate values from the process-global C `rand()` stream, which it also clobbers for every other module

- **File:** `ccd/ctsccd/cgbased/ccdcgSolver.cc:501` (col 1)
- **Pattern:** 1.5 — Random ops without deterministic seed
- **Category:** random
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ccdcgSolver::seedAndPruneCands()` calls `srand(100)` and then consumes `rand()` once per candidate to build the `randSeed` vector that initializes `_vals`. These are the **only** `rand()`/`srand()` calls in product CTS code — every other hit in the module is in a `*Test.cc` harness or in the uncompiled `skewgrp/` directory.

The seed itself is a fixed literal, so the sequence is reproducible in isolation. The defect is the use of **process-global mutable state** on a QoR-affecting path, which cuts both ways:

- **Inbound:** `rand()` draws from one global generator shared by the entire Fusion Compiler process. Any other module that consumes `rand()` between the `srand(100)` and the end of the loop — or concurrently from another thread, where glibc serializes access but does not make the *interleaving* reproducible — shifts this solver's sequence and therefore its candidate seeding.
- **Outbound:** `srand(100)` unconditionally resets the global generator. Any other module that had seeded its own stream loses it, so CTS can destabilize code it does not own.

The `/* coverity[dont_call] */` annotation on the `rand()` line shows the call was already flagged by static analysis and suppressed rather than replaced.

**Realness:** `real`

**Downstream observability proof:**

1. **Suspect source** — `ccd/ctsccd/cgbased/ccdcgSolver.cc:501-507`: `srand(100)` then `rand()` per candidate, feeding `randSeed[i]`.
2. **Consumer** — `:549` sets `_vals[index] = 1.0 - randSeed[index]`, the starting point of the conjugate-gradient solve.
3. **Observable sink** — `_vals` drives candidate selection: `:485-487` thresholds `_vals[i] > _args._candSelThresh` into the `selected` vector, and `seedAndPruneCands()` is called from the solve path at `:363`. Selected candidates are clock-data-delay transforms that are committed to the design, so this is a QoR-affecting choice.
4. **Neutralizer pass** — none. There is no re-seed after the loop and no canonicalization of `randSeed`.
5. **Scope limit, stated plainly** — within `nwtn/src/cts` this is deterministic today, because this is the sole `rand()` consumer and `ccdcgSolver.cc` contains no `parallel_for`, `std::thread` or OpenMP construct. I could not check the rest of `nwtn/src` for other `rand()` consumers, so the inbound half is **unverified**; the outbound half (clobbering other modules' streams) follows from the C standard's single-generator semantics and needs no further proof.

**Controls / gating:**

Ungated. `seedAndPruneCands()` is called unconditionally from the CG solve path at `ccd/ctsccd/cgbased/ccdcgSolver.cc:363`; there is no app option, command flag, or threading guard on it. `_args._seed` is a solver parameter, not a user-visible RNG seed control, and the `100` literal is not configurable.

**App-option defaults:**

None — no app option controls this path.

**Code / regression setters:**

No regression exercises the RNG behaviour specifically. The value `100` is hard-coded, so no test could vary it without a code change.

**Performance-aware fix direction:**

The fix is free. A function-local `std::mt19937` costs roughly the same per draw as `rand()`, is called `numVars` times once per solve rather than in an inner loop, and removes a process-global lock that `glibc`'s `rand()` takes on every call — so under threads it is marginally *faster*. No complexity change, no allocation beyond one engine object, no benchmarking required.

**Current code:**

```cpp
   494 | ccdcgSolver:: seedAndPruneCands()
   495 | {
   497 |   int numVars = _candidates.size();
   500 |   std::vector<float> randSeed( numVars );
>  501 |   srand( 100 );
   502 |   for( int i=0; i < numVars; ++i ) {
   503 |     float candSeed =  0.0;
   504 |     /* coverity[dont_call] */
   505 |     int r = rand();
   506 |     float rSeed = ((float)((r % 50001) + 50000))/1000000.0;
   507 |     randSeed[i] = rSeed;
   508 |     _vals[i] = (candSeed != -1.0) ? candSeed : (_args._seed - rSeed);
   ...
   549 |         _vals[index] = (float) 1.0 - randSeed[index];   // seeds the solve
```

**Suggested fix:**

**Version A (recommended) — use a local engine so no global state is touched:**

```cpp
// ccd/ctsccd/cgbased/ccdcgSolver.cc, seedAndPruneCands()
// A function-local engine cannot be perturbed by, and cannot perturb, any
// other module's use of the C global generator.
std::vector<float> randSeed( numVars );
std::mt19937 rng( 100 );                       // same fixed seed as before
std::uniform_int_distribution<int> dist( 0, 50000 );
for( int i=0; i < numVars; ++i ) {
  float candSeed = 0.0;
  float rSeed = ((float)(dist(rng) + 50000))/1000000.0;
  randSeed[i] = rSeed;
  _vals[i] = (candSeed != -1.0) ? candSeed : (_args._seed - rSeed);
  _wArea[i] = _zArea[i] = _wDelay[i] = _zDelay[i] = 1.0;
}
```
The `/* coverity[dont_call] */` suppression can be deleted along with the `rand()` call it was hiding.

**Version B (stronger) — derive the seed from the problem so it is reproducible *and* input-dependent:**

```cpp
// Seed from stable characteristics of the candidate set rather than a magic
// literal, so the sequence is reproducible for a given design but is not an
// arbitrary constant shared by every solve.
std::size_t seed = _candidates.size();
for (const ccdcgCand* cand : _candidates) {
  seed = seed * 1099511628211ULL + static_cast<std::size_t>(cand->index());
}
std::mt19937 rng( static_cast<std::mt19937::result_type>(seed) );
```
Use only if solver behaviour should track the problem; it will move QoR relative to today's fixed stream.

**Version C (minimal, if the literal must stay) — keep rand() but stop leaking state:**

```cpp
// Least invasive option: save and restore nothing (the C API offers no way to
// read the global state), so instead confine rand() use behind an accessor that
// documents the hazard and is easy to grep for.
// NOTE: this does not fix the inbound exposure -- prefer Version A.
```
Recorded for completeness only. The C library exposes no way to save and restore the global generator, so there is no correct minimal variant; Version A is the smallest *correct* change.

**Why this fix:**

Version A. It is a four-line, behaviour-preserving change that keeps the existing fixed seed — so QoR should be bit-identical to today in a single-threaded run — while removing both the inbound and outbound global-state exposure. Version B is a policy change and should be a separate discussion. Version C does not exist as a real option, which is worth stating explicitly rather than leaving a reader to look for one.

**False-positive check:**

Not a scanner artifact. A tree-wide grep for `rand`/`srand` excluding `*Test.cc`, `/test/` and `skewgrp/` returns exactly these two lines, so the single-consumer claim is enumerated rather than assumed. `ccdcgSolver.cc` was checked for `parallel_for`, `parallel_reduce`, `std::thread`, `concurrent_` and `omp` with no hits, which is what keeps this MEDIUM rather than HIGH. The site is live product code: `skewgrp/Master.make` has an empty `CPPFILES` list, but `ccd/ctsccd/cgbased/` does not, and the function has a caller at `:363`.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ccd/ctsccd/cgbased/ccdcgSolver.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 2.2 — getFullName() / getPathName() used as map key or hashed  (×3)

### Issue 2.2.1 — ICG signature/BDD traversal keys two per-net maps on getPathName(), rebuilt on every node visit

- **File:** `ctsmisc/ctsICGCell.cc:514` (col 1)
- **Pattern:** 2.2 — getFullName() / getPathName() used as map key or hashed
- **Category:** naming
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ctsmisc/ctsICGCell.h:313-314` declares the two working maps of the ICG signature / BDD engine:

```
std::map<std::string, void*>  _signatureMap;
std::map<std::string, bool>   _visitedSizeOnlyMap;
```

Both are keyed on `ndmNet::getPathName()` / `ndmTerm::getPathName()`. `ctsCalculateSignatureOnVisit::endVisitNode()` is a **per-node visitor** invoked for every pin and flat net in every ICG enable cone, and it rebuilds these hierarchical path strings on every single access. There are 121 `getPathName()` calls in this one file.

The worst concentration is lines 719-726, where a single statement builds three separate hierarchical names:

```
_visitedSizeOnlyMap[outputTermFlatNet->getNet()->getPathName()] =
  _visitedSizeOnlyMap[inputFlatNet->getNet()->getPathName()] || ... ;
```

These are live algorithmic state, not diagnostics: line 514 stores the computed BDD variable, line 692/696 read the fan-in signature that the current node's signature is derived from, and lines 705/715 propagate it through buffers and inverters. Neither map is ever iterated (I checked - only `operator[]`, `find`, `count` and `erase`), so there is **no non-determinism here**: `std::map<std::string,...>` is lexicographically ordered and the result is bit-reproducible. The defects are the per-visit cost and a rename/escaping sensitivity in the key space.

Two secondary problems in the same code, both worth fixing in the same change: lines 455-457, 465-467, 478-480 and 487-489 call `userOutput::printf` **unguarded by `_debug`**, each evaluating two or three more `getPathName()` calls per visit; and `operator[]` is used in boolean tests (line 454 `if (_signatureMap[...] != NULL)`, line 477), which **default-inserts a NULL entry** for every absent key and grows the map with junk.

**Realness:** `real`

**Downstream observability proof:**

1. `ctsmisc/ctsICGCell.cc:514`, `:544`, `:569`, `:599`, `:628`, `:654`, `:954`, `:984`, `:1014`, `:1218`, `:1283` - writes: the computed signature / BDD variable for a flat net or term is stored under its path name.
2. `ctsmisc/ctsICGCell.cc:692`, `:696` - reads: `inputSignature` for the node currently being evaluated is fetched by the fan-in's path name.
3. `ctsmisc/ctsICGCell.cc:705`, `:715` - the signature is propagated through buffers/inverters (`^ NEG_POLARITY`) and written back under the output net's path name. This is the recursion that computes the whole cone's signature.
4. `ctsmisc/ctsICGCell.cc:329`, `:332`, `:351`, `:354`, `:367`, `:373`, `:388` - `setSignatureValue(...)` / `setBddVar(...)` push the looked-up value into the visitor's state, which is what `ctsICGCell::calculateICGSignature` (`ctsmisc/ctsICGCell.h:195`) returns to the ICG merge engine via `enSignatureMM` / `seSignatureMM`.
5. Those signature multimaps are how `ctsMergeIcg` decides which clock gates have equivalent enable functions and may therefore be merged - an **NDM database mutation** (instances merged/deleted, nets rewired).

So the keys are on a genuinely non-trivial algorithmic path; they are simply a slow and rename-fragile way to name the objects.

**Controls / gating:**

Reached by ICG merging (`ctsMergeIcg::runBDDMerge` / `runFlatNetMerge`, `icg/ctsMergeIcg.h:334-335`) during CTS. The non-BDD signature path (`_bddBased == false`) is the default; the BDD path is additionally compiled under `#ifdef USE_CUDD`. `_debug` is a constructor argument (`ctsmisc/ctsICGCell.cc:38`, `:55`) and gates most - but not all - of the printf sites. Cost scales with (number of ICGs) x (nodes per enable cone) x (hierarchy depth).

**Performance-aware fix direction:**

`ndmNet::getPathName()` / `ndmTerm::getPathName()` walk up the hierarchy and concatenate each level, allocating a fresh `std::string` per call: O(depth x name length) plus a malloc/free. `getIdLong()` is a single field read, O(1), no allocation. The subsequent `std::map` descent then costs O(log n) **string** comparisons versus O(log n) integer comparisons - and because clock-network path names share long common prefixes (`u_core/u_clk/u_icg_bank_.../...`), each string compare runs nearly the full length of the key before diverging. This is the pathological case for string-keyed maps.

The calls are all inside a per-node visitor, i.e. the innermost loop of the traversal, and several statements call it 2-3 times on the same object (lines 342/346, 455-457, 465-467, 478-480, 487-489, 719-720). Keying by `getIdLong()` would eliminate every allocation and turn the comparisons into integer compares. Removing the four unguarded `userOutput::printf` blocks removes roughly 10 more name constructions per visited net **and** stops the tool from spraying "before erasing, count = ..." at every user. Fixing the `operator[]`-in-a-condition pattern at lines 454 and 477 stops the maps from silently growing a NULL entry per miss. None of these fixes costs anything at runtime.

**Current code:**

```cpp
  -- ctsmisc/ctsICGCell.h --
   313 |   std::map<std::string, void*>    _signatureMap;
   314 |   std::map<std::string, bool>     _visitedSizeOnlyMap;

  -- ctsmisc/ctsICGCell.cc, live reads that drive the computation --
   691 |     dvuAssert(_signatureMap.find(inputTerm->getPathName()) != _signatureMap.end());
>  692 |     inputSignature = _signatureMap[inputTerm->getPathName()];
   693 |   } else {
   694 |     inputFlatNet = inputNet->getFlatNet();
   695 |     dvuAssert(_signatureMap.find(inputFlatNet->getNet()->getPathName()) != _signatureMap.end());
>  696 |     inputSignature = _signatureMap[inputFlatNet->getNet()->getPathName()];
   697 |   }
   ...
>  705 |     _signatureMap[outputTermFlatNet->getNet()->getPathName()] = inputSignature;
   ...
>  715 |     _signatureMap[outputTermFlatNet->getNet()->getPathName()] = (void *)((unsigned long)inputSignature ^ NEG_POLARITY);
   716 |   }
   717 |
   718 |   if (inputFlatNet)
>  719 |     _visitedSizeOnlyMap[outputTermFlatNet->getNet()->getPathName()] =
>  720 |       _visitedSizeOnlyMap[inputFlatNet->getNet()->getPathName()] ||
   721 |       _infra.isInstSizeOnly(inst) ||
   722 |       _infra.isFlatNetSizeOnly(outputTermFlatNet);   // 3 hierarchical names in one statement

  -- write side --
   513 |   // insert bddVar into a map
>  514 |   _signatureMap[flatNet->getNet()->getPathName()] = bddVar;
   515 |
   516 |   if (_infra.isFlatNetSizeOnly(flatNet))
>  517 |     _visitedSizeOnlyMap[flatNet->getNet()->getPathName()] = true;
   518 |   else
>  519 |     _visitedSizeOnlyMap[flatNet->getNet()->getPathName()] = false;

  -- unguarded debug printf + operator[] default-insert --
   453 |     // entry may have been erased in the earlier iteration
>  454 |     if (_signatureMap[flatNet->getNet()->getPathName()] != NULL) {   // inserts a NULL entry if absent
   455 |       userOutput::printf("before erasing, count = %s find = %s\n",    // NOT guarded by _debug
   456 |                          _signatureMap.count(flatNet->getNet()->getPathName())>0?">0":"!>0",
   457 |                          _signatureMap.find(flatNet->getNet()->getPathName())!=_signatureMap.end()?"TRUE":"FALSE");
```

**Suggested fix:**

**Version A (recommended):**

```cpp
// Version A (recommended): key by the stable object id.
// ctsmisc/ctsICGCell.h:313-314
std::map<long, void*>  _signatureMap;
std::map<long, bool>   _visitedSizeOnlyMap;

// ctsmisc/ctsICGCell.cc:514-519
_signatureMap[flatNet->getNet()->getIdLong()] = bddVar;
_visitedSizeOnlyMap[flatNet->getNet()->getIdLong()] = _infra.isFlatNetSizeOnly(flatNet);

// ctsmisc/ctsICGCell.cc:692-696
if (inputNet == NULL) {
  inputSignature = _signatureMap[inputTerm->getIdLong()];
} else {
  inputFlatNet = inputNet->getFlatNet();
  inputSignature = _signatureMap[inputFlatNet->getNet()->getIdLong()];
}

// ctsmisc/ctsICGCell.cc:718-722 (3 name builds -> 2 id loads)
if (inputFlatNet) {
  const long outId = outputTermFlatNet->getNet()->getIdLong();
  const long inId  = inputFlatNet->getNet()->getIdLong();
  _visitedSizeOnlyMap[outId] = _visitedSizeOnlyMap[inId] ||
                               _infra.isInstSizeOnly(inst) ||
                               _infra.isFlatNetSizeOnly(outputTermFlatNet);
}
```

**Version B:**

```cpp
// Version B: key by the object pointer with the ID-stable comparator.
// Same determinism guarantee, and it keeps the object reachable from the key.
// ctsmisc/ctsICGCell.h:313-314
#include <ccdUtil.h>   // ndmObjPtrCmpType == ndmObjectHandleNS::compareObjPtr
std::map<const ndmObject*, void*, ndmObjPtrCmpType>  _signatureMap;
std::map<const ndmObject*, bool,  ndmObjPtrCmpType>  _visitedSizeOnlyMap;

// ctsmisc/ctsICGCell.cc:514-519
_signatureMap[flatNet->getNet()] = bddVar;
_visitedSizeOnlyMap[flatNet->getNet()] = _infra.isFlatNetSizeOnly(flatNet);

// ctsmisc/ctsICGCell.cc:454 -- and stop default-inserting NULLs
auto sigIt = _signatureMap.find(flatNet->getNet());
if (sigIt != _signatureMap.end() && sigIt->second != NULL) {
  if (_debug) {
    userOutput::printf("erased an existing 'en' Bdd variable 0x%lx for flat net '%s'\n",
                       (unsigned long)(sigIt->second),
                       flatNet->getNet()->getPathName().c_str());   // name only in the log line
  }
  _signatureMap.erase(sigIt);
}
```

**Version C (minimal, no header change):**

```cpp
// Version C (minimal, no header change): cache the name once per statement and
// guard the four unguarded printf blocks. Removes ~60% of the calls on its own.
// ctsmisc/ctsICGCell.cc:718-722
if (inputFlatNet) {
  const std::string& outName = outputTermFlatNet->getNet()->getPathName();
  const std::string& inName  = inputFlatNet->getNet()->getPathName();
  _visitedSizeOnlyMap[outName] = _visitedSizeOnlyMap[inName] ||
                                 _infra.isInstSizeOnly(inst) ||
                                 _infra.isFlatNetSizeOnly(outputTermFlatNet);
}

// ctsmisc/ctsICGCell.cc:453-468
const std::string& netName = flatNet->getNet()->getPathName();
auto sigIt = _signatureMap.find(netName);
if (sigIt != _signatureMap.end() && sigIt->second != NULL) {
  if (_debug) {                                    // <-- was missing
    userOutput::printf("erased an existing 'en' Bdd variable 0x%lx for flat net '%s'\n",
                       (unsigned long)(sigIt->second), netName.c_str());
  }
  _signatureMap.erase(sigIt);
}
```

**Why this fix:**

**Version A**, with the `_debug` guards and the `find`-instead-of-`operator[]` cleanups from Version B folded in. The `void*` values and the `#ifdef USE_CUDD` split make this file awkward to touch, but the key type is the one thing that is mechanical: every site is `map[<obj>->getPathName()]`, so the edit is a find-and-replace of `getPathName()` with `getIdLong()` across 48 sites plus two declarations. Version B is slightly nicer (the key still gets you back to the object) but requires pinning down a common base type across `ndmNet` and `ndmTerm`, which the current code sidesteps by stringifying both into one map - I would not want to do that type surgery in the same change. Version C is the zero-risk option for a release branch: it removes most of the redundant calls and stops the unconditional printf spam without touching any container type.

**False-positive check:**

Not a false positive as a performance/stability finding - these are live reads and writes of the signature state that drives ICG merge decisions, not diagnostics. I confirmed this by tracing lines 692/696 (read fan-in signature) into 705/715 (propagate to output) and out through `setSignatureValue`/`setBddVar` into `calculateICGSignature`.

Explicitly **not** a non-determinism finding: I grepped for `.begin()` / range-for over both maps and found none, so the lexicographic key order never leaks into any decision. Ten of the 58 raw hits in this file are genuinely report/assert/dead text and are dismissed separately (bucket B1) - lines 317 and 321 are inside an `#if 0`, 463 and 485 are commented out, 468 and 490 are `dvuAssert` arguments, and 342/346/460/483 are printf arguments. I did not profile ICG merge, so "hot" here is a structural claim (per-node visitor) rather than a measured one; that is why this is MEDIUM and not HIGH.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctsmisc/ctsICGCell.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Issue 2.2.2 — _instInfoMap snapshots pre-transform instance state by getFullName(); a rename is reported as a removed cell

- **File:** `ctssc/ctsXformProblems.cc:1130` (col 1)
- **Pattern:** 2.2 — getFullName() / getPathName() used as map key or hashed
- **Category:** naming
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`ctssc/ctsXformProblems.h:874` declares `std::map<std::string, origInstInfo> _instInfoMap;`, where `origInstInfo` is `boost::tuple<ndmModule*, ndmCoord, ndmBlkOrient, bool>` - the ref module, location, orientation and a driver flag captured for every instance **before** a transform, so the transform can be evaluated or undone afterwards.

The key is the instance's full hierarchical name. That creates two problems.

First, cost: line 1130 calls `inst->getFullName()` once per instance inside the snapshot loop, and the matching lookups at lines 993, 1019, 1064, 1105, 1203 and 1609 each build the name again. Every one of those sites already has the `ndmInst*` in hand.

Second, and more serious: `updateRemovedCellsStats()` at lines 1281-1288 iterates `_instInfoMap` and treats any key **not present in `finalInsts`** as a deleted cell. `finalInsts` is built at line 1195 from the *post*-transform instances, also by `getFullName()`. So an instance that merely got **renamed** by the transform - which is routine when CTS clones, splits or uniquifies clock cells - appears under one name in `_instInfoMap` and a different name in `finalInsts`, and is therefore recorded as removed. That write lands in `_ctsGlobal->_removedCells` and `_ctsGlobal->_aggremovedCells`, which are persisted stats printed into the user-facing CCD changed-cells report.

No non-determinism: `_instInfoMap` is an ordered `std::map` and `finalInsts` an ordered `std::set`, so the iteration at 1281 is lexicographic and reproducible.

**Realness:** `real`

**Downstream observability proof:**

1. `ctssc/ctsXformProblems.cc:1130` - snapshot: pre-transform `(refModule, loc, ori, driversHaveVLs)` keyed by the instance's full name.
2. `ctssc/ctsXformProblems.cc:1195` - `finalInsts` is filled with post-transform full names.
3. `ctssc/ctsXformProblems.cc:1203-1208` - `_instInfoMap.find(inst->getFullName())` plus `instNotChanged(inst, iit->second, g)` decides whether an instance counts as modified by the transform. A renamed instance misses the map and falls into the `else` branch.
4. `ctssc/ctsXformProblems.cc:1258` - `updateRemovedCellsStats(finalInsts, g)`.
5. `ctssc/ctsXformProblems.cc:1284-1288` - any `_instInfoMap` key absent from `finalInsts` is inserted into `_ctsGlobal->_removedCells` and `_ctsGlobal->_aggremovedCells`. **Persisted state.**
6. `ctssc/ctsscGlobal.cc:6707-6710` - `_aggremovedCells` is iterated and printed as the "Total number of removed cells" section of the CCD changed-cells `.rpt` file. **User-visible output.**

So a rename produces both a phantom entry in a user-facing report and a mis-classification of the instance as changed, which drives extra downstream work.

**Controls / gating:**

Reached on the CTS/CCD transform-problem evaluation path whenever a transform snapshots and then re-checks its instance set. `updateRemovedCellsStats` is gated by `skipUpdateRemovedCellsStats()` (line 1277). The report write at `ctsscGlobal.cc:6685` is itself gated by the changed-cell reporting being enabled. No env var is needed to reach the snapshot/compare at 1130/1203.

**Performance-aware fix direction:**

One `getFullName()` per instance at the snapshot (1130) and one per instance at each of the six lookup sites (993, 1019, 1064, 1105, 1203, 1609). `getFullName()` is O(hierarchy depth) with a string allocation; `getIdLong()` is O(1) with none. The map then does O(log n) string compares on names that share long hierarchical prefixes, versus O(log n) integer compares. With the instance set of a clock transform this is a few thousand name builds per transform invocation, and transforms run many times - noticeable but an order of magnitude below the ctsICGCell and kneeMap sites. As with those, keying by id costs nothing at runtime. The rename-robustness improvement is the main reason to make the change here.

**Current code:**

```cpp
  -- ctssc/ctsXformProblems.h --
   874 |   std::map<std::string, origInstInfo> _instInfoMap;
   899 |   std::set<std::string> _dirtyInsts;

  -- snapshot (inside a per-instance loop) --
  1128 |       }
  1129 |     }
> 1130 |     _instInfoMap.insert(std::make_pair(inst->getFullName(),  boost::make_tuple(inst->getRefModule(), loc, ori, driversHaveVLs)));
  1131 |   }

  -- the post-transform name set --
  1192 |   std::set<std::string> finalInsts;
  1193 |   for(instSetType::iterator it = mgInstSet.begin(); it != mgInstSet.end(); it++) {
  1194 |     ndmInst* inst = *it;
> 1195 |     finalInsts.insert(inst->getFullName());
  ...
  1203 |     std::map<std::string, origInstInfo>::iterator iit = _instInfoMap.find(inst->getFullName());
  1205 |     if(iit != _instInfoMap.end() && instNotChanged(inst, iit->second, g)) {
  ...
  1258 |   updateRemovedCellsStats(finalInsts, g);

  -- name-difference interpreted as deletion --
  1275 | void ctsXformProblem::updateRemovedCellsStats(std::set<std::string>& finalInsts, const ctsscGlobal& g)
  1281 |   for(std::map<std::string, origInstInfo>::iterator it = _instInfoMap.begin(); it != _instInfoMap.end(); it++)
  1282 |   {
  1283 |     std::set<std::string>::iterator module = finalInsts.find(it->first);
  1284 |     if(module == finalInsts.end()) {             // <-- renamed == removed
  1285 |       std::set<std::string>::iterator removed = _ctsGlobal->_removedCells.find(it->first);
  1286 |       if(removed == _ctsGlobal->_removedCells.end()) {
  1287 |         _ctsGlobal->_removedCells.insert(it->first);
  1288 |         _ctsGlobal->_aggremovedCells.insert(it->first);
```

**Suggested fix:**

**Version A (recommended):**

```cpp
// Version A (recommended): key by instance id; ids survive renames.
// ctssc/ctsXformProblems.h:874 / :899
std::map<ndmInstId, origInstInfo> _instInfoMap;
std::set<ndmInstId>               _dirtyInsts;

// ctssc/ctsXformProblems.cc:1130
_instInfoMap.insert(std::make_pair(inst->getId(),
                    boost::make_tuple(inst->getRefModule(), loc, ori, driversHaveVLs)));

// ctssc/ctsXformProblems.cc:1192-1203
std::set<ndmInstId> finalInsts;
for(instSetType::iterator it = mgInstSet.begin(); it != mgInstSet.end(); it++) {
  ndmInst* inst = *it;
  finalInsts.insert(inst->getId());
  ...
  std::map<ndmInstId, origInstInfo>::iterator iit = _instInfoMap.find(inst->getId());

// ctssc/ctsXformProblems.cc:1283-1288 -- resolve the name only when reporting
std::set<ndmInstId>::iterator module = finalInsts.find(it->first);
if(module == finalInsts.end()) {
  ndmInst* gone = g._ctsInfra->getInstById(it->first);
  const std::string goneName = gone ? gone->getFullName() : std::string("<deleted>");
  if(_ctsGlobal->_removedCells.find(goneName) == _ctsGlobal->_removedCells.end()) {
    _ctsGlobal->_removedCells.insert(goneName);
    _ctsGlobal->_aggremovedCells.insert(goneName);
  }
}
```

**Version B:**

```cpp
// Version B: key by the instance pointer with the ID-stable comparator.
// ctssc/ctsXformProblems.h:874
#include <ccdUtil.h>   // ndmObjPtrCmpType == ndmObjectHandleNS::compareObjPtr
std::map<ndmInst*, origInstInfo, ndmObjPtrCmpType> _instInfoMap;

// ctssc/ctsXformProblems.cc:1130
_instInfoMap.insert(std::make_pair(inst,
                    boost::make_tuple(inst->getRefModule(), loc, ori, driversHaveVLs)));

// ctssc/ctsXformProblems.cc:1203
std::map<ndmInst*, origInstInfo, ndmObjPtrCmpType>::iterator iit = _instInfoMap.find(inst);
```

**Version C (minimal):**

```cpp
// Version C (minimal): keep the string keys but hoist the name per iteration,
// and make the rename case visible instead of silently counting it as removed.
// ctssc/ctsXformProblems.cc:1193-1208
for(instSetType::iterator it = mgInstSet.begin(); it != mgInstSet.end(); it++) {
  ndmInst* inst = *it;
  const std::string instName = inst->getFullName();   // built once, used twice
  finalInsts.insert(instName);
  if (!g._ctsInfra->isInstSizable(inst) && !g._ctsInfra->isInstMovable(inst)) {
    continue;
  }
  std::map<std::string, origInstInfo>::iterator iit = _instInfoMap.find(instName);
  ...
}

// ctssc/ctsXformProblems.cc:1284 -- only count it removed if it is really gone
if(module == finalInsts.end() && g._ctsInfra->findInst(it->first) == NULL) {
  ...
}
```

**Why this fix:**

**Version A.** `ndmInstId` is what the rest of this subsystem already uses for exactly this purpose - `ctsscGlobal.cc:6687` stores `_aggsizedCells` as `std::map<ndmInstId, ndmModule*>` and only converts to names at report time - so this change makes `_instInfoMap` consistent with its neighbours rather than introducing a new convention. It fixes the rename-is-removal bug at the root, because ids survive renames, and it confines name construction to the one place that genuinely needs a string (the report). Version B is equally correct on determinism but holds raw pointers across a transform that may delete instances, which is a lifetime hazard I would not add here. Version C is the low-risk hot-fix: hoisting the name halves the calls in the loop and the extra `findInst` guard stops phantom removed-cell entries reaching the report, without any type change.

**False-positive check:**

Confirmed a live container key, not a diagnostic: the tuple is read back at line 1205 and passed to `instNotChanged(...)`, and the iteration at 1281 writes into persisted stats.

Not a non-determinism finding - `_instInfoMap` is `std::map<std::string,...>` and `finalInsts` is `std::set<std::string>`, both ordered, so line 1281 iterates lexicographically and reproducibly.

What I could not verify: I did not find a concrete CTS transform that renames an instance *between* the snapshot at 1130 and the check at 1203, so the phantom-removed-cell consequence is reasoned from the code shape (name captured, name compared, no id anywhere) rather than observed. If no transform on this path ever renames, the finding degrades to the performance half only. I also did not confirm that `ndmInst::getId()` returns `ndmInstId` in this branch - `ctsscGlobal.cc:6688` uses `getInstById(it->first)` on an `ndmInstId` key, which is the pattern Version A copies. The two sibling hits in this file (lines 1195 `finalInsts` and 1394 `_dirtyInsts`) are membership-only sets and are dismissed into bucket B3; they are listed in the fixes above only because they must move in step with the map.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctssc/ctsXformProblems.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Issue 2.2.3 — Clock latency and ideal-network constraints stored under getPathName(), then resolved back by findTerm() - silent drop on rename

- **File:** `mscts/msutil/msInfra.cc:1255` (col 1)
- **Pattern:** 2.2 — getFullName() / getPathName() used as map key or hashed
- **Category:** naming
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 1

**Why this is non-deterministic:**

`mscts/msutil/msInfra.h:54-60` declares three constraint-carrying maps, all keyed by pin path name:

```
typedef std::map<std::string, SourceLatencyVec>        TermToSourceLatencies;
typedef std::map<std::string, NetworkLatencyVec>       TermToNetworkLatencies;
typedef std::map<std::string, std::pair<bool, bool> >  TermToBoolPair;
```

These hold `set_clock_latency -source`, `set_clock_latency` (network) and `set_ideal_network` settings captured off the design before multisource CTS restructures it, so they can be re-applied afterwards.

The key is a **string round trip**: `msInfra` stores `term->getPathName()` on the way in, and on the way out `reapplyIdealNetworks()` iterates the map and calls `infra.findTerm(termName)` to get the object back. If the pin's path name changed in between - hierarchy uniquification, an escaped-name change, a boundary port punched or renamed, an ICG cloned and renamed - `findTerm` returns `NULL`, the `if (term)` guard at line 1182 skips it, and **the ideal-network setting is silently dropped with no message**. The same fragility applies to the latency maps, which propagate a source pin's latency to its destinations by name at lines 1044/1054/1064.

This is not a non-determinism finding: all three containers are ordered `std::map`, so the iteration at line 1179 runs in lexicographic name order and is reproducible. The defects are the silent-drop failure mode and the per-term name construction.

**Realness:** `real`

**Downstream observability proof:**

1. `mscts/msutil/msInfra.cc:1255` / `:1285` / `:1357` - capture: latency and ideal-network settings are keyed by `getPathName()`.
2. `mscts/msutil/msInfra.cc:1044` / `:1054` / `:1064` - propagation: a source pin's setting is copied to each destination pin, keyed by the destination's path name. Note line 1064 builds **two** hierarchical names in one statement.
3. `mscts/msutil/msInfra.cc:1105`, `:1130`, `:1152`, `:1430`, `:1441`, `:1495` - the query side (`getSourceLatency`, `getNetworkLatency`, `isIdealNetworkSource`, and the pairwise comparisons at 1430/1441/1495) all look up by `conn->getPathName()`. These feed the multisource CTS latency model.
4. `mscts/msutil/msInfra.cc:1179-1183` - `reapplyIdealNetworks()` iterates and calls `infra.findTerm(termName)`, then `idealMgr.setIdealNetwork(term, ...)`. This is a **constraint-database write**.
5. `mscts/msutil/msInfra.cc:1158` - the sibling `setIdealNetwork(conn, ...)` write on the query path.

Observable sink: a dropped ideal-network flag means the net is no longer treated as ideal, so CTS buffers and balances a network the user asked it to leave alone - a direct QoR and correctness consequence, delivered silently.

**Controls / gating:**

Reached whenever multisource CTS (`create_clock_tree` / MSCTS flow) runs on a design carrying `set_clock_latency` or `set_ideal_network` constraints on clock pins. `reapplyIdealNetworks()` is compiled inside an `#if` block (the `#endif` sits at line 1187), so confirm the surrounding conditional is active in the shipping build before rating the silent-drop half. The propagation at 1039-1066 runs per source pin per destination. The capture at 1357 runs per constrained term.

**Performance-aware fix direction:**

Each of these is one `getPathName()` per term per operation, and line 1064 does two in a single statement. `getPathName()` is O(hierarchy depth) with a string allocation; `getIdLong()` is O(1) with none. The lookups then cost O(log n) string compares over long common-prefix clock path names instead of O(log n) integer compares. The volume here is bounded by the number of *constrained* clock pins rather than by the whole netlist, so the raw cycle count is far smaller than the ctsICGCell case - this finding is filed primarily for the silent-drop failure mode, with the cost as a secondary benefit. Changing the key type costs nothing at runtime; keeping a parallel `std::map<long, std::string>` (Version C) costs one extra small map.

**Current code:**

```cpp
  -- mscts/msutil/msInfra.h --
    54 | typedef std::map<std::string, SourceLatencyVec>  TermToSourceLatencies;
    57 | typedef std::map<std::string, NetworkLatencyVec> TermToNetworkLatencies;
    60 | typedef std::map<std::string, std::pair<bool, bool> > TermToBoolPair ;
   196 |   TermToSourceLatencies    _termSourceLat;
   198 |   TermToNetworkLatencies   _termNetworkLat;
   202 |   TermToBoolPair           _idealNetworkSource;

  -- capture --
  1253 | {
  1254 |   msSourceLatency *s = new msSourceLatency(sl, scen);
> 1255 |   _termSourceLat[term->getPathName()].push_back(s);
  1256 |   _allSourceLat.push_back(s); // the owner of the latency structure
  1257 | }
  ...
  1284 |   msNetworkLatency *n = new msNetworkLatency(nl, scen);
> 1285 |   _termNetworkLat[term->getPathName()].push_back(n);
  ...
  1355 |     bool noPropagate = idealMgr.isIdealNetworkAsNoPropagate(term) ;
  1356 |     bool dontCarePlacement = idealMgr.isIdealNetworkAsDontCarePlacement(term) ;
> 1357 |     _idealNetworkSource[term->getPathName()] = std::make_pair(noPropagate, dontCarePlacement);

  -- propagate source -> destinations, by name --
  1039 |     TermToSourceLatencies::iterator its = _termSourceLat.find(src_conn->getPathName());
  1040 |     if (its != _termSourceLat.end()) {
  1042 |         ndmConn *dest_conn = ctsNL::getConnOf(dest, src_conn);
  1043 |         if (dest_conn) {
> 1044 |           _termSourceLat[dest_conn->getPathName()] = its->second;
  ...
> 1064 |           _idealNetworkSource[dest_conn->getPathName()] = _idealNetworkSource[src_conn->getPathName()];

  -- the reverse lookup: name -> object, silent drop on miss --
  1173 | msInfra::reapplyIdealNetworks()
  1179 |   for (TermToBoolPair::value_type val: _idealNetworkSource) {
  1180 |     std::string termName = val.first;
  1181 |     ndmTerm* term = infra.findTerm(termName) ;
  1182 |     if (term)                                     // <-- no else, no warning
  1183 |       idealMgr.setIdealNetwork(term, val.second.first, val.second.second);
  1184 |   }
```

**Suggested fix:**

**Version A (recommended):**

```cpp
// Version A (recommended): key by the stable object id, keep the term pointer
// in the value so reapply never needs a name lookup at all.
// mscts/msutil/msInfra.h:54-60
typedef std::map<long, SourceLatencyVec>   TermToSourceLatencies;
typedef std::map<long, NetworkLatencyVec>  TermToNetworkLatencies;
typedef std::map<long, std::pair<ndmTerm*, std::pair<bool, bool> > > TermToBoolPair;

// mscts/msutil/msInfra.cc:1255 / :1285 / :1357
_termSourceLat[term->getIdLong()].push_back(s);
_termNetworkLat[term->getIdLong()].push_back(n);
_idealNetworkSource[term->getIdLong()] =
    std::make_pair(term, std::make_pair(noPropagate, dontCarePlacement));

// mscts/msutil/msInfra.cc:1179-1184
for (TermToBoolPair::value_type val: _idealNetworkSource) {
  ndmTerm* term = val.second.first;                 // no findTerm(), no silent drop
  idealMgr.setIdealNetwork(term, val.second.second.first, val.second.second.second);
}
```

**Version B:**

```cpp
// Version B: key by the term pointer with the ID-stable comparator.
// mscts/msutil/msInfra.h:54-60
#include <ccdUtil.h>   // ndmObjPtrCmpType == ndmObjectHandleNS::compareObjPtr
typedef std::map<ndmTerm*, SourceLatencyVec,  ndmObjPtrCmpType> TermToSourceLatencies;
typedef std::map<ndmTerm*, NetworkLatencyVec, ndmObjPtrCmpType> TermToNetworkLatencies;
typedef std::map<ndmTerm*, std::pair<bool, bool>, ndmObjPtrCmpType> TermToBoolPair;

// mscts/msutil/msInfra.cc:1062-1065
ndmConn *dest_conn = ctsNL::getConnOf(dest, src_conn);
if (dest_conn) {
  _idealNetworkSource[dest_conn] = idealIt->second;   // was 2 getPathName() calls
}

// mscts/msutil/msInfra.cc:1179-1184
for (TermToBoolPair::value_type val: _idealNetworkSource) {
  idealMgr.setIdealNetwork(val.first, val.second.first, val.second.second);
}
```

**Version C (minimal):**

```cpp
// Version C (minimal): keep the string keys, but stop silently discarding
// settings whose pin was renamed, and cache the name at the two-call site.
// mscts/msutil/msInfra.cc:1062-1065
ndmConn *dest_conn = ctsNL::getConnOf(dest, src_conn);
if (dest_conn) {
  _idealNetworkSource[dest_conn->getPathName()] = idealIt->second;  // reuse idealIt
}

// mscts/msutil/msInfra.cc:1179-1184
for (TermToBoolPair::value_type val: _idealNetworkSource) {
  const std::string& termName = val.first;
  ndmTerm* term = infra.findTerm(termName);
  if (term) {
    idealMgr.setIdealNetwork(term, val.second.first, val.second.second);
  } else {
    userOutput::printf("Warning: ideal-network setting on '%s' was dropped; "
                       "the pin no longer exists under that name.\n", termName.c_str());
  }
}
```

**Why this fix:**

**Version A.** The reason a name is used here at all is that the capture and the re-apply are separated by the part of the flow that restructures the clock network - which is exactly the window in which names change. Storing the `ndmTerm*` alongside the value removes the `findTerm` round trip entirely, so there is no failure mode left to report. Version B is cleaner to read and is the right shape if the terms are guaranteed to outlive the map, but it drops the value-side pointer that Version A uses to make `reapplyIdealNetworks` total. Version C is the one-line safety net to land immediately regardless of which structural fix is chosen: today a dropped constraint is completely invisible, and even with the string keys retained, a warning turns a silent QoR regression into a debuggable message.

**False-positive check:**

Confirmed these are live container keys, not diagnostics: the values are read back at lines 1105, 1130, 1152, 1430, 1441 and 1495 to answer latency queries, and written into the constraint database at 1158 and 1183.

Not a non-determinism finding, and I checked specifically: `TermToBoolPair` is `std::map`, not `unordered_map` (`msInfra.h:60`), so the iteration at line 1179 is lexicographic and reproducible. I also confirmed the other 2.2 files in this slice have no *iterated* unordered string-keyed container.

What I could not verify: whether pin path names actually do change between capture and `reapplyIdealNetworks()` in the shipping MSCTS flow. The silent-drop hazard is structural (the `if (term)` with no `else` at line 1182 is unambiguous) but I have no failing case. I also did not resolve which `#if` encloses `reapplyIdealNetworks` - the `#endif` is at line 1187 but the opening directive is above the region I read, so this function may be conditionally compiled out.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/mscts/msutil/msInfra.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 3.2 — Multi-threaded shared container writes  (×1)

### Issue 3.2.1 — fmax timing cost functions group their TNS partial sums by thread count, so the returned cost (and the WNS witness path on exact ties) changes with -max_cores

- **File:** `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` (col 1)
- **Pattern:** 3.2 — Multi-threaded shared container writes
- **Category:** parallel
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 2

**Why this is non-deterministic:**

This is the mechanism described by pattern 3.5 (thread-count dependency) showing up at sites the scanner flagged as 3.2.

The cost functions stripe over a *thread index*: `tbb::parallel_for(size_t(0), numberOfThreads, size_t(1), [&](size_t threadCount){...})`, where `numberOfThreads = this->maxThreads()` and `_maxThreads` is initialised from `crmResources::get().getMaxThreadCount()` (fmaxLpSolver.h:91). The container is split into exactly `numberOfThreads` contiguous ranges by `calculateRanges(relations, numberOfThreads)` (fmaxTimingCostFunction.h:246).

The body itself is clean - it only ever touches `resultsPerThreadTNS[threadCount]`, `violatedPathsPerThreadTNS[threadCount]` etc., i.e. per-thread slots in vectors sized before the loop. The problem is the **merge**:

    for(size_t threadIndex=0; threadIndex < numberOfThreads; ++threadIndex) {
      resultTNS += resultsPerThreadTNS[threadIndex];

Each `resultsPerThreadTNS[t]` is itself a sequential `double` accumulation over its own range. So the final value is `(sum of range 0) + (sum of range 1) + ...`. Double addition is not associative: change `numberOfThreads` and the *grouping* changes, the rounding changes, and `resultTNS` comes out different in the last few ULPs. Running on a 16-core host and a 128-core host, or with two different `set_host_options -max_cores` values, gives two different TNS costs for byte-identical inputs.

There is a second, sharper consequence in the same merge loop - the WNS witness:

    if(resultWNS > resultsPerThreadWNS[threadIndex]) {
      resultWNS = resultsPerThreadWNS[threadIndex];
      mostViolatedPath = mostViolatedPathPerThreadWNS[threadIndex];
    }

The strict `>` means the lowest thread index wins an exact tie. Which paths land in which thread's range is decided by `numberOfThreads`, so when two paths have bit-identical worst slack, *which one becomes `mostViolatedPath`* - and therefore which constraint gets pushed into `violatedPathsWNS` and handed to the LP - moves with the core count.

To be precise about what is **not** broken here, because the code is otherwise carefully written: the order of `violatedPathsTNS` / `violatedPathsWNS` is *not* thread-count dependent. The merge uses prefix-sum offsets (`outputCountBeforeTNS`) into a pre-sized vector, and concatenating contiguous ranges in thread-index order reproduces exactly the sequential container order. This is genuinely correct per-thread-buffer code; the FP grouping and the tie-break are the two places where the thread count leaks into the result.

**Realness:** `real`

**Downstream observability proof:**

1. **Thread count source** - `ccd/ctsccd/fmax/fmaxLpSolver.h:91` initialises `_maxThreads` from `crmResources::get().getMaxThreadCount()`, surfaced via `ccd/ctsccd/fmax/fmaxCostFunction.h:69`.
2. **Partition** - `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:246` `calculateRanges(relations, numberOfThreads)` cuts the relation container into exactly `numberOfThreads` contiguous ranges.
3. **Parallel construct** - `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` strides over the thread index; each task walks its own range.
4. **Per-thread accumulation** - `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:322` `resultsPerThreadTNS[threadCount] += double(endpointSlack)` and `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:306-308` for the WNS witness.
5. **Merge (the ND hop)** - `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:337` sums the per-thread partials; `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:343-345` picks the WNS witness by lowest thread index.
6. **Observable sink (a) - cost value.** `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:1038` `this->setLastEvaluationResult(float(result+penalty))`. That value is the objective the fmax LP / CG solver minimises; the accept/reject comparison against `this->stopValue()` / `this->requiredValue()` (`ccd/ctsccd/fmax/fmaxTimingCostFunction.h:378-384`, `:1028-1035`) is an exact floating-point comparison, so a last-ULP difference can flip a move from accepted to rejected. That is a QoR-affecting choice.
7. **Observable sink (b) - constraint selection.** `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:375` pushes `mostViolatedPath` into `violatedPathsWNS`, which is the set of constraints handed back to the LP solver. A different witness on a tie means a different constraint row, i.e. a different LP and a different skew/latency solution committed to the database.

**Controls / gating:**

**Multi-threaded by default.** There is no enable flag: `fmaxTimingCostFunction.h:234` asserts `dvuAssertRelease(numberOfThreads > 1)` outright, i.e. the MT path is the *expected* path, and the guards at `fmaxTimingCostFunction.h:526`, `:767`, `:1061` are `if (this->maxThreads() > 1)` - a serial fallback exists only when the tool is explicitly restricted to one core.

The one real control is `set_host_options -max_cores`, which feeds `crmResources::get().getMaxThreadCount()`. Note that CTS's own wrapper `ctsscUtil::getMaxThreadCount()` (`ctssc/ctsscUtil.cc:415-424`) also honours the `CCDSC_THREADS` environment variable and clamps to `CTS_MAX_THREAD = 160`, but the fmax cost functions bypass that wrapper and read `crmResources` directly.

Honest limitation: `crm.h` is outside this snapshot, so I could not read what `getMaxThreadCount()` returns when the user never issues `set_host_options`. If it defaults to the host core count then this is straightforwardly machine-dependent; if it defaults to 1 then the exposure is limited to users who opt into multi-core. That default is the one fact worth confirming before triaging this further.

**Performance-aware fix direction:**

This is the hot inner loop of the fmax LP - `evaluateSlackOfPath` is called once per timing relation per cost evaluation, and cost evaluation happens on every LP iteration. Forcing a sequential reduction would be a real regression and is not on the table.

Version A (fixed chunk count) is the right trade and costs essentially nothing: the work is identical, only the number of ranges changes from `numberOfThreads` to a constant 256. With `parallel_for(0, 256, 1, ...)` TBB still load-balances across however many workers exist, and 256 chunks actually gives *better* balancing than one-chunk-per-thread when ranges are uneven. The merge loop goes from `numberOfThreads` iterations to 256 - irrelevant. This is the textbook 'fixed partition independent of hardware' fix.

Version B (compensated summation over the partials) is O(numberOfThreads) extra flops, i.e. a few dozen operations per cost evaluation - also free - but it only bounds the error, it does not make the grouping identical, so two machines still differ (just by less). Prefer A.

Version C (stable WNS tie-break) adds one `ConstraintComparatorNew()` call per thread in the merge loop, executed only on exact ties. Negligible. It should go in regardless of which of A/B is chosen, because it fixes a different sink.

**Current code:**

```cpp
ccd/ctsccd/fmax/fmaxCostFunction.h
    69 |     size_t maxThreads() const { return _maxThreads;}
ccd/ctsccd/fmax/fmaxLpSolver.h
    91 |   _maxThreads((crmResources::get()).getMaxThreadCount()), ...

ccd/ctsccd/fmax/fmaxTimingCostFunction.h
   233 |       size_t numberOfThreads = size_t(this->maxThreads());
   234 |       dvuAssertRelease( numberOfThreads > 1 );
   246 |         newRanges = calculateRanges(relations, numberOfThreads);
   270 |       std::vector<double > resultsPerThreadTNS(numberOfThreads, 0);
   271 |       std::vector<double > resultsPerThreadWNS(numberOfThreads, 0);
   275 |       std::vector< const I2V * > mostViolatedPathPerThreadWNS(numberOfThreads, NULL);
>  277 |       tbb::parallel_for (size_t(0), numberOfThreads, size_t(1), [&](size_t threadCount) {
   279 |         for(typename ContainerType::const_iterator currentIterator = (*iteratorRanges)[threadCount].first;
   280 |                                                    currentIterator != (*iteratorRanges)[threadCount].second;
   281 |                                                  ++currentIterator) {
   287 |             float pathSlack = referenceModel->evaluateSlackOfPath(relation);
   306 |             if(pathSlack < resultsPerThreadWNS[threadCount]) {
   307 |               resultsPerThreadWNS[threadCount] = pathSlack;
   308 |               mostViolatedPathPerThreadWNS[threadCount] = referenceModel->returnConstPointerToPath(relation);
   309 |             }
   322 |             resultsPerThreadTNS[threadCount]+=double(endpointSlack);
   326 |       }); // tbb::parallel_for (...)

   336 |       for(size_t threadIndex=0; threadIndex < numberOfThreads; ++threadIndex) {
>  337 |         resultTNS += resultsPerThreadTNS[threadIndex];        // <-- grouping follows -max_cores
   338 |         outputCountBeforeTNS[threadIndex] = outputPathsCountTNS;
   339 |         outputPathsCountTNS += violatedPathsPerThreadTNS[threadIndex].size();
>  343 |         if(resultWNS > resultsPerThreadWNS[threadIndex]) {    // <-- lowest thread index wins ties
   344 |           resultWNS = resultsPerThreadWNS[threadIndex];
   345 |           mostViolatedPath = mostViolatedPathPerThreadWNS[threadIndex];
   346 |         }
   348 |       }
   372 |       resultTNS+=double(nonTouchedViolationTNS);
   374 |       if(resultWNS < float(0) && resultWNS >= requiredValueWNS && (mostViolatedPath != NULL) ) {
   375 |         violatedPathsWNS.push_back(mostViolatedPath);
   376 |       }
```

**Suggested fix:**

**Version A:**

```cpp
// VERSION A - partition into a FIXED number of chunks so neither the partial-sum
// grouping nor the tie ownership follows the host core count. Recommended.
// ccd/ctsccd/fmax/fmaxTimingCostFunction.h (apply to each of the 4 evaluate* bodies)

      // Deterministic partition: the chunk count is a constant, so resultTNS is
      // summed in the same grouping on a 16-core and a 128-core host.
      static constexpr size_t kDeterministicChunkCount = 256;
      size_t numberOfChunks = std::min(kDeterministicChunkCount, relations->size());
      if (numberOfChunks == 0) { numberOfChunks = 1; }

      if (!inputRanges.size() || inputRanges.size() != numberOfChunks) {
        newRanges = calculateRanges(relations, numberOfChunks);
        iteratorRanges = &newRanges;
      }

      std::vector<std::vector<const I2V*> > violatedPathsPerThreadTNS(numberOfChunks, std::vector<const I2V*>());
      std::vector<std::vector<const I2V*> > violatedPathsPerThreadWNS(numberOfChunks, std::vector<const I2V*>());
      std::vector<double > resultsPerThreadTNS(numberOfChunks, 0);
      std::vector<double > resultsPerThreadWNS(numberOfChunks, 0);
      std::vector< const I2V * > mostViolatedPathPerThreadWNS(numberOfChunks, NULL);

      tbb::parallel_for (size_t(0), numberOfChunks, size_t(1), [&](size_t threadCount) {
        /* body unchanged */
      });

      for(size_t threadIndex=0; threadIndex < numberOfChunks; ++threadIndex) {
        resultTNS += resultsPerThreadTNS[threadIndex];
        /* ... unchanged ... */
      }
```

**Version B:**

```cpp
// VERSION B - Neumaier compensated summation of the per-thread partials.
// Bounds the error to ~1 ulp of the exact sum so the last-ULP drift across
// core counts stops mattering. Does NOT make the grouping identical.
// ccd/ctsccd/fmax/fmaxTimingCostFunction.h - replace the accumulation at line 337

      double resultTNSCompensation = 0.0;
      for(size_t threadIndex=0; threadIndex < numberOfThreads; ++threadIndex) {
        const double partial = resultsPerThreadTNS[threadIndex];
        const double sum     = resultTNS + partial;
        resultTNSCompensation += (std::abs(resultTNS) >= std::abs(partial))
                               ? ((resultTNS - sum) + partial)
                               : ((partial - sum) + resultTNS);
        resultTNS = sum;

        outputCountBeforeTNS[threadIndex] = outputPathsCountTNS;
        outputPathsCountTNS += violatedPathsPerThreadTNS[threadIndex].size();
        outputCountBeforeWNS[threadIndex] = outputPathsCountWNS;
        outputPathsCountWNS += violatedPathsPerThreadWNS[threadIndex].size();
      }
      resultTNS += resultTNSCompensation;
```

**Version C:**

```cpp
// VERSION C - stable WNS witness tie-break. Orthogonal to A/B; take it either way.
// ccd/ctsccd/fmax/fmaxTimingCostFunction.h - replace lines 343-346

        const double candidateWNS  = resultsPerThreadWNS[threadIndex];
        const I2V*   candidatePath = mostViolatedPathPerThreadWNS[threadIndex];

        // On an exact slack tie, fall back to the constraint's own ordering instead
        // of 'whichever chunk happened to be lower', which moves with -max_cores.
        if (candidatePath != NULL &&
            (mostViolatedPath == NULL ||
             candidateWNS < resultWNS ||
             (candidateWNS == resultWNS &&
              fmaxLpModel::ConstraintComparatorNew()(*candidatePath, *mostViolatedPath)))) {
          resultWNS        = candidateWNS;
          mostViolatedPath = candidatePath;
        }
```

**Why this fix:**

**Version A plus Version C.**

A is the cheap, structural fix: it severs the link between the host core count and the arithmetic entirely, rather than trying to make the arithmetic robust to a moving partition. It is also strictly better for load balancing than the current one-chunk-per-thread scheme, so it is unlikely to cost runtime and may recover a little. The constant 256 matches what `soCG.cc:1675`/`:1738` already do (`std::max(_variablesVec.size()/256UL, 256UL)`), so it is an idiom this codebase already uses.

C is independent and should go in regardless - it fixes constraint *selection*, which is a discrete QoR decision rather than a rounding difference, and it costs nothing.

B is a fallback if for some reason the chunk count must stay tied to the thread count. It reduces the divergence but does not eliminate it, so it is the weaker option.

**False-positive check:**

Checked and ruled out:
- *Is the parallel body writing to shared state?* No - every write is to `[threadCount]` in a vector sized before the loop. That part is correct and I am not claiming otherwise.
- *Is the violated-path list order ND?* **No**, and I want to be explicit because it looks like it should be. The merge at lines 336-348 computes prefix offsets and line 350 pre-sizes `violatedPathsTNS.assign(outputPathsCountTNS, NULL)`, then line 353 writes by index. Concatenating contiguous ranges in thread-index order reproduces the sequential container order exactly. This is not a defect.
- *Is the top-300 priority-queue merge ND?* No. The tournament at lines 934-962 pairs fixed indices (`nonEmptyPriorityQueues-threadCount-1` into `threadCount`), and `ViolationWithConstraintComparator` (fmaxLpModel.h:171-178) breaks slack ties with `ConstraintComparatorNew()` on constraint *content*, not on the raw pointer. Since each thread keeps its own top-`extendedCutOff`, the merged top-K is the global top-K regardless of partition. I checked this specifically because a pointer-keyed priority queue would have been a much worse bug; it is not one.
- *Is this run-to-run ND?* **No, and I am not claiming it is.** `_maxThreads` is fixed at construction and the thread-index striping is deterministic, so two runs on the same host with the same `-max_cores` give identical results. The defect is cross-machine / cross-configuration reproducibility. I am reporting it as MEDIUM rather than HIGH for exactly this reason.
- *Verification depth:* I read the `:277` body and its merge line by line. The siblings at `:436`, `:667`, `:1213` and the `.cc` cost functions were matched on the identical `std::vector<double> resultsPerThread(numberOfThreads, 0)` + `for(threadIndex...) result += resultsPerThread[threadIndex]` idiom (confirmed present at h:433-434/471-473 and h:664-665/716-718 by grep), not re-read in full.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ccd/ctsccd/fmax/fmaxTimingCostFunction.h`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 3.5 — Thread-count dependency in algorithm sizing  (×1)

### Issue 3.5.1 — Lazy-TNS path-group tracing picks a different algorithm when the host has more than 32 cores

- **File:** `ctssc/lazytns/ctsLazyModel.cc:4834` (col 1)
- **Pattern:** 3.5 — Thread-count dependency in algorithm sizing
- **Category:** parallel
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 2

**Why this is non-deterministic:**

This is a textbook instance of triage question 3.5.1 - the thread count flows into a **conditional branch that selects a different implementation**, not merely into a chunk size:

    const size_t maxThreads = (crmResources::get()).getMaxThreadCount();
    const bool disableParallelPrgTrace = !ccdConfig::is_128_core() && !(ccdConfig::get_enable_runtime_improvements() > 1);
    if (maxThreads > 32 && candidates.size() > 1 && !disableParallelPrgTrace) {
      ... doPrgTracePerScenParallel(...) ...
    } else {
      ... doPrgTracePerScen(...) ...
    }

Two entirely separate tracing routines. On a 24-core host the run takes the serial branch; on a 64-core host, the same design with the same script takes the parallel branch. Whether those two routines produce bit-identical traced path slacks is an assumption, not something the code checks, and `doPrgTracePerScenParallel` additionally builds its own graph (`results[round].graph`) rather than reusing the shared one.

`ccdConfig::is_128_core()` in the same predicate is a second machine-shaped input.

Note that the *merge* is done properly - `mergePrgTraceResult(results[i], ...)` at line 4845 runs single-threaded over `i` in index order, so given the parallel branch the result is reproducible. The defect is purely the branch itself: the tool silently changes algorithm based on the machine it lands on. On a heterogeneous compute farm that means the same job can produce two different clock trees depending on which host the scheduler picked.

**Realness:** `real`

**Downstream observability proof:**

1. **Thread count source** - `ctssc/lazytns/ctsLazyModel.cc:4827` reads `crmResources::get().getMaxThreadCount()`, i.e. `set_host_options -max_cores` or its machine-derived default.
2. **Branch** - `ctssc/lazytns/ctsLazyModel.cc:4834` compares it against the magic constant 32 and combines it with `ccdConfig::is_128_core()` from `ctssc/lazytns/ctsLazyModel.cc:4828`.
3. **Two different implementations** - `doPrgTracePerScenParallel()` at `ctssc/lazytns/ctsLazyModel.cc:4841` versus `doPrgTracePerScen()` at `ctssc/lazytns/ctsLazyModel.cc:4853`.
4. **Consumer** - `mergePrgTraceResult()` at `ctssc/lazytns/ctsLazyModel.cc:4845` folds the parallel results back into the lazy-TNS model state.
5. **Observable sink** - the PRG trace populates the lazy-TNS endpoint/startpoint path data that `costGroup::calculateTnsDelta()` (`ctssc/lazytns/ctsLazyCostGroup.cc:966`) and `traceLazyPaths()` (`ctssc/lazytns/ctsLazyModel.cc:2235`) consume to compute the TNS cost driving CCD skew optimisation. Any divergence between the two tracers is a QoR-affecting difference in the committed clock tree, selected by the host core count.

**Controls / gating:**

Gated by three things simultaneously, all of which default to something environment-shaped:
- `crmResources::get().getMaxThreadCount() > 32` - `set_host_options -max_cores`, or the machine default (which I could not read; `crm.h` is outside this snapshot).
- `ccdConfig::is_128_core()` - a machine-class config predicate.
- `ccdConfig::get_enable_runtime_improvements() > 1` - a tool config knob.

The parallel branch is reachable **by default** on a large host: with `is_128_core()` true, `disableParallelPrgTrace` is false without any user opt-in, so only `maxThreads > 32` and `candidates.size() > 1` remain, both of which are ordinary conditions. There is no way to pin the algorithm choice from the script other than clamping `-max_cores` to 32 or below, which is not something a user would think to do for reproducibility.

**Performance-aware fix direction:**

The `maxThreads > 32` gate exists for a reason - `doPrgTracePerScenParallel` builds a per-scenario graph copy (`PrgTraceResult::graph`, torn down at line 4848), so it trades memory and setup cost for parallelism, and that trade only pays off with enough cores. Deleting the gate outright would regress small-host runtime and peak memory.

Version A therefore keeps a gate but moves it onto a *configuration* input (`get_enable_runtime_improvements()`) rather than the core count, so the choice is reproducible from the script alone and can be recorded in the run log. No runtime cost; it is the same code either way, just selected differently.

Version C (always take the parallel implementation) is the most reproducible but pays the graph-copy cost on small hosts; only worth it if the two tracers are known to be equivalent and the copy is cheap.

Version B costs nothing in production - the cross-check is behind `#ifdef Synopsys_Develop` and an environment variable - but it does not fix anything on its own, it just tells you whether there is anything to fix.

**Current code:**

```cpp
ctssc/lazytns/ctsLazyModel.cc
  4827 |   const size_t maxThreads = (crmResources::get()).getMaxThreadCount();
  4828 |   const bool disableParallelPrgTrace = !ccdConfig::is_128_core() && !(ccdConfig::get_enable_runtime_improvements() > 1);
> 4834 |   if (maxThreads > 32 && candidates.size() > 1 && !disableParallelPrgTrace) {
  4835 |     tmLazyModelBasic.print("PrgTrace: parallel mode with %d threads, %d scenarios\n",
  4836 |                            int(maxThreads), int(candidates.size()));
  4838 |     std::vector<PrgTraceResult> results(candidates.size());
  4840 |     ccdUtil::parallel_for(size_t(0), candidates.size(), [&candidates, &results, this](size_t round) {
  4841 |       results[round] = doPrgTracePerScenParallel(candidates[round].first, candidates[round].second);
  4842 |     });
  4844 |     for (size_t i = 0; i < results.size(); ++i) {
  4845 |       mergePrgTraceResult(results[i], candidates[i].first, candidates[i].second);
  4846 |     }
> 4848 |     tbb::parallel_for(size_t(0), results.size(), mtContext::task([&results](size_t i) {
  4849 |       results[i].graph.reset();
  4850 |     }));
  4851 |   } else {
  4852 |     for(size_t round=0; round< candidates.size(); ++round) {
  4853 |       doPrgTracePerScen(candidates[round].first, candidates[round].second);
  4854 |     }
  4855 |   }
```

**Suggested fix:**

**Version A:**

```cpp
// VERSION A - make the algorithm choice a configuration decision, not a
// property of whichever host the job landed on.
// ctssc/lazytns/ctsLazyModel.cc

  const size_t maxThreads = (crmResources::get()).getMaxThreadCount();

  // The implementation is selected from config only, so the same script produces
  // the same trace on a 24-core and a 128-core host. maxThreads still controls how
  // wide we run, not which algorithm runs.
  const bool useParallelPrgTrace =
    (ccdConfig::get_enable_runtime_improvements() > 1) && (candidates.size() > 1);

  if (useParallelPrgTrace) {
    tmLazyModelBasic.print("PrgTrace: parallel mode with %d threads, %d scenarios\n",
                           int(maxThreads), int(candidates.size()));
    std::vector<PrgTraceResult> results(candidates.size());
    ccdUtil::parallel_for(size_t(0), candidates.size(), [&candidates, &results, this](size_t round) {
      results[round] = doPrgTracePerScenParallel(candidates[round].first, candidates[round].second);
    });
    for (size_t i = 0; i < results.size(); ++i) {
      mergePrgTraceResult(results[i], candidates[i].first, candidates[i].second);
    }
    tbb::parallel_for(size_t(0), results.size(), mtContext::task([&results](size_t i) {
      results[i].graph.reset();
    }));
  } else {
    for (size_t round = 0; round < candidates.size(); ++round) {
      doPrgTracePerScen(candidates[round].first, candidates[round].second);
    }
  }
```

**Version B:**

```cpp
// VERSION B - keep the gate, but prove the two tracers agree before trusting it.
// ctssc/lazytns/ctsLazyModel.cc - inside the parallel branch, after the merge loop

#ifdef Synopsys_Develop
    // The >32-core gate silently swaps implementations. Until the two are known to
    // agree, allow a regression run to diff them.
    if (ctsEnvVariable::getBool("CTS_PRGTRACE_CHECK_EQUIVALENCE", false)) {
      const TermCriticalityMap parallelCriMap = _criMap;
      for (size_t round = 0; round < candidates.size(); ++round) {
        doPrgTracePerScen(candidates[round].first, candidates[round].second);
      }
      dvuAssertRelease(parallelCriMap == _criMap &&
                       "PrgTrace parallel/serial divergence");
    }
#endif
```

**Version C:**

```cpp
// VERSION C - always use the parallel implementation. With one scenario it
// degenerates to one task, so 1 core and 128 cores execute the same code path.
// ctssc/lazytns/ctsLazyModel.cc

  std::vector<PrgTraceResult> results(candidates.size());
  ccdUtil::parallel_for(size_t(0), candidates.size(), [&candidates, &results, this](size_t round) {
    results[round] = doPrgTracePerScenParallel(candidates[round].first, candidates[round].second);
  });
  for (size_t i = 0; i < results.size(); ++i) {
    mergePrgTraceResult(results[i], candidates[i].first, candidates[i].second);
  }
  tbb::parallel_for(size_t(0), results.size(), mtContext::task([&results](size_t i) {
    results[i].graph.reset();
  }));
```

**Why this fix:**

**Version A, with Version B landed first as a diagnostic.**

A preserves the performance intent (don't pay the graph-copy cost unless runtime improvements are on) while removing the machine from the decision. The `maxThreads > 32` test is doing double duty today - it is both a perf heuristic and, accidentally, a correctness-visible switch - and splitting those is the actual fix.

B is worth landing first because it answers the question this finding cannot: *do the two tracers actually diverge?* If a regression sweep shows they are bit-identical, this drops to a hygiene issue and A becomes a cleanup. If they diverge, A becomes urgent. Running B is cheaper than reasoning about it.

C is the most reproducible but I would not pick it blind - it forces the graph-copy path onto small hosts, and I have no runtime data to justify that.

**False-positive check:**

Checked and ruled out:
- *Is the parallel body itself racy?* No. `results[round]` is an index write into a vector sized at line 4838, and `mergePrgTraceResult` at 4845 runs single-threaded in index order. Given the branch, the parallel path is internally deterministic. The finding is about the branch, not the body.
- *Is line 4848 (the flagged candidate) a problem?* No - it is a parallel destructor call (`results[i].graph.reset()`) on disjoint elements after all consumers are done. That specific line is a false positive; it is what led me to the branch above it.
- *Is this dead code?* No. `ccdConfig::is_128_core()` being true is enough to clear `disableParallelPrgTrace`, so the parallel branch is live on large hosts without any user opt-in.
- *What I could NOT verify:* whether `doPrgTracePerScenParallel` and `doPrgTracePerScen` actually produce identical results. Proving or refuting that needs either a careful read of both implementations or an A/B regression run. I am reporting the branch as the defect because a thread-count-selected algorithm swap is a reproducibility hazard whether or not the two happen to agree today - nothing keeps them agreeing as they are maintained.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctssc/lazytns/ctsLazyModel.cc`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Pattern 3.6 — Post-collection use without canonical ordering  (×2)

### Issue 3.6.1 — compareTimInfo is not a strict weak ordering: arbitrary tie order in _sinkPinTimingInfoSet drives the 'N worst sinks' max_transition selection

- **File:** `ctssch/ctsTimingDrivenTransitionTargets.h:181` (col 1)
- **Pattern:** 3.6 — Post-collection use without canonical ordering
- **Category:** iteration
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 2

**Why this is non-deterministic:**

`timingInfoSet` is `std::set<timingInfo*, compareTimInfo>` (`ctssch/ctsTimingDrivenTransitionTargets.h:192`) and is the container behind `_sinkPinTimingInfoSet` (`:294`). Its comparator is **not a strict weak ordering**:

```
int cmpVal = nwmathFloat::compare(lhs->getScore(), rhs->getScore(), 0.0001);
if (cmpVal <= 0) return true;
```

When two scores are equal within the 1e-4 tolerance, `cmpVal == 0`, so the functor returns `true` for **both** `comp(a,b)` and `comp(b,a)`, and also for `comp(a,a)`. That violates irreflexivity and asymmetry, which `std::set` requires, so the resulting element order is unspecified by the standard and in practice is decided purely by the red-black-tree insertion sequence rather than by any key.

Ties are not a corner case here, they are the common case. The score is built in `ctssch/ctsTimingDrivenTransitionTargets.cc:304-314` as the sum of three slack terms, each clamped to `0.0` when the slack is non-negative. Every sink that is not timing-critical therefore scores exactly `0.0`, which on a real design is the large majority of clock sinks. If the `sortByCriticality` option is off, `setScore()` is never called at all and *every* element scores `0.0` (`_score` is value-initialised to `0.0` at `:60`), so the set degenerates completely.

The order-sensitive consumer is `targetNWorstSinks()` (`ctssch/ctsTimingDrivenTransitionTargets.cc:833-848`): it walks the set from `begin()` and admits entries into `_tightTransitionSinkPinSet` only while `counter < sinksToTarget`. That is a first-N cut. Whenever the number of genuinely critical sinks is below `sinksToTarget` the cut lands inside the equal-score group, so *which* sinks are selected is decided by the arbitrary tie order.

**Realness:** `real`

**Downstream observability proof:**

1. **Unstable ordering source** - `ctssch/ctsTimingDrivenTransitionTargets.h:181-189`: `compareTimInfo` returns `true` on ties, so it is not a strict weak ordering and the set's element order is unspecified / insertion-sequence dependent.
2. **Tie population** - `ctssch/ctsTimingDrivenTransitionTargets.cc:304-314`: `criticalityScore` clamps each non-negative slack term to `0.0`, so all non-critical sinks collide on score `0.0`.
3. **Collection** - `ctssch/ctsTimingDrivenTransitionTargets.h:226-230` (`addSinkTimingInfo`) inserts every sink's `timingInfo*` into `_sinkPinTimingInfoSet`; called from `ctssch/ctsTimingDrivenTransitionTargets.cc:183`.
4. **Order-sensitive consumer (first-N cut)** - `ctssch/ctsTimingDrivenTransitionTargets.cc:833-848`: iteration from `begin()` with `if (counter < sinksToTarget)` selects a prefix of the set into `_tightTransitionSinkPinSet`.
5. **Propagation to the constraint store** - `ctssch/ctsTimingDrivenTransitionTargets.cc:598-614`: `getTightTransitionSinkSet()` is walked and each selected term is recorded via `storeOriginalTransition(*itr, transitionsDataVec)` into `_storeHouse`.
6. **Observable sink: database write** - `ctssch/ctsTimingDrivenTransitionTargets.cc:259-260`: `drcMgr.setCstr(term->toConn(), cstrDrcType::MAX_TRANSITION, targetTrans)` writes a tightened max_transition DRC constraint into the scenario's `cstrDrcMgr` for exactly the selected terms. Those constraints then drive CTS buffering/sizing, so the selection is QoR-affecting and persists in the constraint database. The restore path at `:243` writes the original value back for the same set.
7. **Secondary user-visible sink** - `ctssch/ctsTimingDrivenTransitionTargets.cc:845` prints `Score %f %s` per element in set order when `_verbose` is on, and `:851` reports the resulting targeted-sink percentage.

**Controls / gating:**

- Entry point: `ctsSch::runTDSinkTargetTransitionRecipe()` (`ctssch/ctsSch.cc:3733-3749`), which builds the manager and runs `_treeStructures->forEachTreeNode(false /*bottomUp*/, false /*exception*/, *_tdSinkTargetTran)`.
- **Data condition gate**: the recipe body only runs when a negative setup or hold slack exists; `ctssch/ctsSch.cc:3741-3748` skips it and prints "All slacks are positive or cannot be queried at this stage" otherwise.
- **App-option gates** (all via `_session->getOpt().getTDsinkTranOption(...)`):
  - `sortByCriticality` (default `true`) - gates both `setScore()` at `ctssch/ctsTimingDrivenTransitionTargets.cc:303` and the `targetNWorstSinks()` call at `:593`. With it **off**, scores stay `0.0` for every element, which is the worst case for this defect.
  - `degradationAverse` (default `true`) - extra filter inside the selection loop at `:836`.
  - `sortAllNegativeAreaPenalty` (default `0.05`) and `TransRatioMultiplier` (default `1.0`) - set `sinksToTarget` at `:818-823`, i.e. where the first-N cut lands.
  - `nominalTransMultiplier`, `tightenCTSTransFurther` - affect the value written at `:253-258`.
- C++ guard: none. There is no sort or canonicalisation between the set and the selection.

**Performance-aware fix direction:**

Adding a stable tie-break costs essentially nothing. The comparator is already invoked O(log n) times per insert; adding a second key comparison only on the tie path is a few extra instructions and does not change the asymptotics. The set holds one `timingInfo*` per clock sink pin in the current module, and it is built once per `runTDSinkTargetTransitionRecipe()` invocation inside a single DFS (`ctssch/ctsClockTree.h:2401-2438`), not in a nested or hot inner loop. The consumer `targetNWorstSinks()` is a single linear pass. A cheaper stable tie-break is strictly preferable to re-sorting: because the primary key already exists, adding `ndmObjectHandleNS::compareObjPtr` (which orders by ndmType + ndmID, see `ctsutil/ctsTypes.h:721`) on the sink term as a secondary key is O(1) extra work per tie and needs no additional container.

**Current code:**

```cpp
ctssch/ctsTimingDrivenTransitionTargets.h
  181 |   struct  compareTimInfo
  182 |   {
  183 |     bool operator()(const timingInfo *lhs, const  timingInfo *rhs) const
  184 |   {
  185 |     int cmpVal = nwmathFloat::compare(lhs->getScore(), rhs->getScore(), 0.0001);
  186 |     if (cmpVal <= 0) return true;   // <-- true for BOTH (a,b) and (b,a) on a tie
  187 |     else return false;
  188 |   }
  189 |   };
  192 |   typedef std::set<timingInfo*, compareTimInfo> timingInfoSet;
  294 |     _sinkPinTimingInfoSet;

ctssch/ctsTimingDrivenTransitionTargets.cc  (order-sensitive consumer)
  831 |   _tightTransitionSinkPinSet.clear();
  832 |   int counter = 1;
  833 |   std::set<timingInfo*>::iterator itr = _sinkPinTimingInfoSet.begin();
  834 |   for (; itr != _sinkPinTimingInfoSet.end(); itr++) {
  835 |     timingInfo* timInfo = *itr;
  841 |     if (counter < sinksToTarget) {
  842 |       _tightTransitionSinkPinSet.insert(timInfo->getTerm());
  843 |     }
  847 |     counter++;
  848 |   }
```

**Suggested fix:**

**Version A (preferred):**

```cpp
// Version A (preferred): make compareTimInfo a real strict weak ordering with a
// stable secondary key. File: ctssch/ctsTimingDrivenTransitionTargets.h:181
struct  compareTimInfo
{
  bool operator()(const timingInfo *lhs, const  timingInfo *rhs) const
  {
    const int cmpVal = nwmathFloat::compare(lhs->getScore(), rhs->getScore(), 0.0001);
    if (cmpVal < 0) return true;
    if (cmpVal > 0) return false;
    // Scores tie within tolerance: break on stable object identity (ndmType + ndmID)
    // so the first-N cut in targetNWorstSinks() is reproducible.
    return ndmObjectHandleNS::compareObjPtr()(
             const_cast<timingInfo *>(lhs)->getTerm(),
             const_cast<timingInfo *>(rhs)->getTerm());
  }
};
```

**Version B:**

```cpp
// Version B: keep the set for lookup, but canonicalise into a vector and sort with an
// explicit stable key before the top-N cut.
// File: ctssch/ctsTimingDrivenTransitionTargets.cc:831
  _tightTransitionSinkPinSet.clear();
  std::vector<timingInfo*> rankedSinks(_sinkPinTimingInfoSet.begin(),
                                       _sinkPinTimingInfoSet.end());
  std::sort(rankedSinks.begin(), rankedSinks.end(),
            [](timingInfo* a, timingInfo* b) {
              const int c = nwmathFloat::compare(a->getScore(), b->getScore(), 0.0001);
              if (c != 0) return c < 0;
              return ndmObjectHandleNS::compareObjPtr()(a->getTerm(), b->getTerm());
            });
  int counter = 1;
  for (timingInfo* timInfo : rankedSinks) {
    if (_session->getOpt().getTDsinkTranOption("degradationAverse", true)) {
      if (!isGoodCandidate(timInfo->getTerm(), true)) {
        continue;
      }
    }
    if (counter < sinksToTarget) {
      _tightTransitionSinkPinSet.insert(timInfo->getTerm());
    }
    if (_verbose) {
      userOutput::printf("Score %f %s\n", timInfo->getScore(),
                         timInfo->getTerm()->getFullName().c_str());
    }
    counter++;
  }
```

**Version C:**

```cpp
// Version C: change the container so ties are representable and ordering is total.
// File: ctssch/ctsTimingDrivenTransitionTargets.h:190-192
  // Primary key = criticality score (ascending, most negative first);
  // secondary key = stable ndm identity of the sink term.
  typedef std::map<ndmTerm*, timingInfo*, ndmObjPtrCmpType> sinkPinTimingInfoMap;
  typedef std::multimap<float, timingInfo*>                 timingInfoSet;
  // ... and at the insertion site (ctsTimingDrivenTransitionTargets.h:226):
  void addSinkTimingInfo(timingInfo* timInfo)
  {
    _sinkPinTimingInfoSet.insert(std::make_pair(timInfo->getScore(), timInfo));
    _termTimingInfoMap.insert(std::make_pair(timInfo->getTerm(), timInfo));
  }
  // std::multimap keeps equal keys in insertion order (C++11), which is the DFS
  // visit order from ctsClockTree.h:2401 -- stable, but still weaker than Version A.
```

**Why this fix:**

**Version A is recommended.** It fixes the actual defect - the comparator - at its single definition site, so every one of the three consumers (`ctsTimingDrivenTransitionTargets.cc:78`, `:628`, `:833`) becomes well-defined at once, and it removes the undefined behaviour of handing `std::set` a non-strict-weak comparator. It is a three-line change with no container churn, no extra allocation, and no behaviour change for non-tied elements. `ndmObjectHandleNS::compareObjPtr` is already the project's idiom for a stable pointer order (ordering by ndmType + ndmID, documented at `ctsutil/ctsTypes.h:721`) and is already used in this same header via `ndmObjPtrCmpType` at `:190`.

Version B is a reasonable fallback if touching the shared comparator is considered risky, but it only fixes the one call site and leaves the UB in place for the other two iterations. Version C is the weakest: `std::multimap` makes the ordering well-defined and ties resolve to DFS insertion order, but the tie-break is then implicit in the traversal rather than tied to a stable object key, so it silently regresses if the traversal is ever parallelised or reordered.

**False-positive check:**

**What I proved:** the comparator is genuinely not a strict weak ordering (ties return `true` both ways and `comp(a,a)` is `true`); ties are the common case because non-critical sinks all score exactly `0.0`; and the set's iteration order feeds a first-N cut whose output is written to the constraint database via `drcMgr.setCstr(..., MAX_TRANSITION, ...)` at `ctssch/ctsTimingDrivenTransitionTargets.cc:259`.

**What I could NOT prove - and this is why I rated MEDIUM, not HIGH:** I could not demonstrate *run-to-run* variance on a fixed binary. The insertion order is a deterministic DFS (`ctssch/ctsClockTree.h:2401-2438`, over `getClockTreeIterator()` / `getRootNodeIterator()` / `ctsDfsIterator`), the per-node load order comes from `node->getLoadTermIterator()` (`ctssch/ctsTimingDrivenTransitionTargets.cc:324-331`), and `_score` is properly value-initialised to `0.0` at `:60`, so there is no uninitialised read. Given a fixed insertion sequence, libstdc++'s red-black tree will place the tied elements the same way every run. So the concrete exposure today is an **arbitrary, unspecified tie-break at a QoR sink plus standard-level UB**, not an observed ND. It becomes observable ND the moment the traversal order changes, the sink collection is parallelised, or the STL implementation changes; and building with `_GLIBCXX_ASSERTIONS` / `_GLIBCXX_DEBUG` would trip the irreflexivity check.

**Assumption I could not verify in this snapshot:** `nwmathFloat::compare` is not defined anywhere under `/remote/us01home05/carys/cts`, so I inferred its `-1 / 0 / +1` return convention from the `cmpVal <= 0` / `cmpVal > 0` usage and from its tolerance argument. If `compare` never returned `0` the tie path would not exist - but then the `<= 0` test would be pointless, and the tolerance parameter would have no purpose.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctssch/ctsTimingDrivenTransitionTargets.h`
- **Notes:** MEDIUM severity — ownership attribution is recommended but was deprioritized for this pass; the depot path above resolves, so `p4 annotate -c` plus `p4 describe -s` will complete it.

---

### Issue 3.6.2 — The LEQ-order determinism guard `sortModulesByName()` is a no-op at its option's default, while its consumer drops arc-delay ties by input order

- **File:** `ctsutil/ctsUtils.cc:57` (col 1)
- **Pattern:** 3.6 — Post-collection use without canonical ordering
- **Category:** iteration
- **Severity:** MEDIUM  (default: MEDIUM)
- **Tier:** 2

**Why this is non-deterministic:**

`ctsUtils::sortModulesByName()` exists specifically to canonicalize the order of logically-equivalent (LEQ) library-cell vectors. It opens with an early return:

```cpp
if (!useModNameToSortLibs()) {
  return;                     // no sort performed
}
```

`useModNameToSortLibs()` reads `cts.optimize.use_module_name_to_sort_libs`, which is registered **HIDDEN with default `false`** (`ctsui/ctsuiOptimizeAppOptions.cc:2130`, `ctsutil/ctsAppOptions.cc:2124`). So in the default flow the helper returns without touching the vector, at all 7 of its call sites.

This matters because at least one consumer is order-sensitive in a way that silently discards data. `ccdSinkSize::filterLeqForSink()` funnels the LEQ vector through `std::map<float, ndmModule*> sortedLeqMap` keyed on characterized arc delay. `std::map::insert` **rejects** a duplicate key, so when two lib cells characterize to the same `newArcDelay` — routine among cells that differ only in a non-timing attribute — only the one appearing **first in the input vector** survives into `passedSet`. The input order is therefore a silent tie-break on the register-sizing candidate set.

The companion call site states the risk in its own comment: `ccd/ctsccd/ccdscGlobal.cc:3454` reads `// Merge from different sources can perturb order` immediately above the inert `sortModulesByName(leqVec)` call.

**Realness:** `real`

**Downstream observability proof:**

Chain, with each hop cited:

1. **Guard is inert** — `ctsutil/ctsUtils.cc:57-59` returns before sorting whenever `cts.optimize.use_module_name_to_sort_libs` is false, which is its registered default (`ctsui/ctsuiOptimizeAppOptions.cc:2130`, `ctsutil/ctsAppOptions.cc:2124`).
2. **Call sites that therefore do nothing** — `ctsutil/ctsRef.cc:482` (`refSet`), `ccd/ctsccd/ccdscGlobal.cc:3455` (`leqVec`), `ccd/ctsccd/fmax/fmaxProblemGeneratorPower.cc:304`, `ccd/ctsccd/fmax/fmaxVariable.cc:275`, `:305`, `:320`, `:425`.
3. **Vector reaches the consumer** — `ccd/ctsccd/ccdscGlobal.cc:3396` `getCcdLeqVec()` fills `leqVec` from `ctsRef::getContextCompatibleSet()` (`ctsutil/ctsRef.cc:446`, itself ending in the inert sort at `:482`); callers are `ccd/ctsccd/ccdSinkSize.cc:296`, `:355`, `:526`, `ccd/ctsccd/fmax/fmaxMasterXform.cc:382`, `ccd/ctsccd/fmax/fmaxProblemGeneratorWns.cc:1291`, `ccd/ctsccd/fmax/fmaxProblemGenerator.cc:840`, `ccd/ctsccd/fmax/fmaxProblemGeneratorPower.cc:258`.
4. **Observable sink** — `ccd/ctsccd/ccdSinkSize.cc:301-337`: `std::map<float, ndmModule*>::insert` drops every lib cell whose `newArcDelay` ties an already-inserted one, so input order decides the survivor. `passedSet` then goes to `getCcdGlobal()->passedPowerFilter(...)` at `:341` and becomes the register-sizing candidate set — a QoR-affecting choice, not a report.

**Honest limit on the ND half.** What is *proven* here is (a) the guard does not run at its default, and (b) the consumer resolves arc-delay ties purely by input position. What is **not** proven is that the upstream order actually varies run to run: the base order comes from `_leq->getContextCompatibleSet(...)` in the `opt` module (`ctsutil/ctsRef.cc:456`), which is outside this snapshot. The one in-tree path that demonstrably perturbs order — the `optLeqs` merge at `ccd/ctsccd/ccdscGlobal.cc:3446-3453`, flagged by its own comment — is itself behind the hidden, false-by-default `ccd.register_sizing_includes_opt_purpose_lib_cells` (`ccd/ctsccd/ccdscGlobal.cc:3413`). Closing this needs one read of `optLeq::getContextCompatibleSet` in `nwtn/src/opt`.

**Controls / gating:**

- `cts.optimize.use_module_name_to_sort_libs` — **HIDDEN, default `false`**. When `true`, `sortModulesByName()` sorts by `getFullName()` and the exposure closes.
- `ccd.register_sizing_includes_opt_purpose_lib_cells` — **HIDDEN, default `false`** (CL `12637589`). Gates the in-tree order-perturbing merge; when `false`, `getCcdLeqVec()` early-returns at `ccd/ctsccd/ccdscGlobal.cc:3413` before the merge and before the sort call.
- No command-level or flow-level guard: the consumer path is ordinary CCD register sizing (`ccdSinkSize`) and fmax problem generation, reached in the default CCD flow.
- Not gated by threading.

**App-option defaults:**

- `cts.optimize.use_module_name_to_sort_libs`: default `false`, HIDDEN (`ctsui/ctsuiOptimizeAppOptions.cc:2130`).
- `ccd.register_sizing_includes_opt_purpose_lib_cells`: default `false`, HIDDEN (`ccd/ccdui/ccduiAppOptions.cc:5288`, accessor `ccd/ccdui/ccdCommon.h:4941`).

**Code / regression setters:**

No `nwtn/unit` regression is visible from this snapshot. CL `13530532` cites an IREG synreg run and a `Pre_CI_ex207` PRS flowset, which indicates the fix was validated with the option **on** rather than at its shipped default.

**Performance-aware fix direction:**

The author of CL `13530532` gated the sort precisely because of cost, and that concern is legitimate: `getFullName()` is O(hierarchy depth) plus a string allocation per comparison, so an N log N sort over LEQ vectors costs 2·N log N hierarchical name builds. Called per instance during register sizing, that is a real runtime item — which is exactly why Version A below sorts on `getIdLong()` instead. An ID sort is O(1) per comparison with no allocation, so it is strictly cheaper than the name sort the option already enables, and it can be turned on unconditionally. Version B is cheaper still: it fixes the tie-drop at the consumer, touches one function, and adds no sort at all. Neither version changes any lookup complexity. Expect a one-time QoR shift on the first run after the fix, since cell selection among ties will change; the acceptance criterion is run-to-run stability, not QoR neutrality.

**Current code:**

```cpp
  ctsutil/ctsUtils.cc
    54 | void
    55 | ctsUtils::sortModulesByName(std::vector<ndmModule*>& modules)
    56 | {
>   57 |   if (!useModNameToSortLibs()) {
    58 |     return;
    59 |   }
    60 |   std::sort(modules.begin(), modules.end(), [](const ndmModule* left, const ndmModule* right) {
    65 |     return left->getFullName().compare(right->getFullName()) < 0;
    66 |   });
    67 | }

  ccd/ctsccd/ccdSinkSize.cc  (order-sensitive consumer)
   296 |   if (not getCcdGlobal()->getCcdLeqVec(inst, sizes)) {
   301 |   std::map<float, ndmModule*> sortedLeqMap;
>  302 |   for(unsigned int i=0; i < sizes.size(); i++) {
   303 |     ndmModule *newSize = sizes[i];
   326 |     newArcDelay = (p[4] + p[5])/2;
   332 |     sortedLeqMap.insert(std::make_pair(newArcDelay, newSize));   // tie -> insert rejected
   336 |   for(std::map<float, ndmModule*>::iterator itt = sortedLeqMap.begin(); itt != sortedLeqMap.end(); itt++) {
   337 |     passedSet.push_back(itt->second);

  ccd/ctsccd/ccdscGlobal.cc  (the author's own warning, guard inert)
  3454 |     // Merge from different sources can perturb order
  3455 |     ctsUtils::sortModulesByName(leqVec);
```

**Suggested fix:**

**Version A (recommended) — make the guard unconditional and sort on stable IDs:**

```cpp
// ctsutil/ctsUtils.cc
// Sort by stable lib-cell identity, always. getIdLong() is O(1) with no
// allocation, so this is cheaper than the getFullName() sort the app option
// already enables and it no longer needs to be opt-in.
void
ctsUtils::sortModulesByName(std::vector<ndmModule*>& modules)
{
  if (useModNameToSortLibs()) {
    // Preserve the documented name-ordered behaviour when explicitly requested.
    std::sort(modules.begin(), modules.end(), [](const ndmModule* l, const ndmModule* r) {
      if (l == r) {
        return false;
      }
      return l->getFullName().compare(r->getFullName()) < 0;
    });
    return;
  }

  // Default path: canonical, cheap, and no longer a no-op.
  std::sort(modules.begin(), modules.end(), ndmObjPtrCmpType{});
}
```
`ndmObjPtrCmpType` is the in-tree alias for `ndmObjectHandleNS::compareObjPtr` (`ccd/util/ccdUtil.h:71`) and orders by `(ndmType, ndmID)`, not by address.

**Version B (smallest blast radius) — stop the consumer from discarding ties:**

```cpp
// ccd/ctsccd/ccdSinkSize.cc, filterLeqForSink()
// std::map<float, ndmModule*>::insert() silently rejects a duplicate key, so
// cells that characterise to the same arc delay were dropped by input position.
// Key the ordering on (arcDelay, stable-cell-id) so every cell is retained and
// ties resolve identically on every run.
struct ArcDelayThenId {
  bool operator()(const std::pair<float, ndmModule*>& a,
                  const std::pair<float, ndmModule*>& b) const {
    if (a.first != b.first) {
      return a.first < b.first;
    }
    return a.second->getIdLong() < b.second->getIdLong();
  }
};

std::set<std::pair<float, ndmModule*>, ArcDelayThenId> sortedLeqMap;
// ... unchanged characterisation loop ...
sortedLeqMap.insert(std::make_pair(newArcDelay, newSize));

for (const auto& entry : sortedLeqMap) {
  passedSet.push_back(entry.second);
}
```
This also fixes a genuine data-loss bug independent of determinism: tied lib cells were never reaching `passedSet` at all.

**Version C (belt and braces) — do both, and assert the invariant:**

```cpp
// Apply Version A and Version B together, then make the contract checkable so
// the guard cannot silently regress to a no-op again.
void
ctsUtils::sortModulesByName(std::vector<ndmModule*>& modules)
{
  // ... Version A body ...
  dvuAssert(std::is_sorted(modules.begin(), modules.end(), ndmObjPtrCmpType{})
            || useModNameToSortLibs());
}
```
Consider renaming to `canonicalizeModuleOrder()`. The present name promises a sort that the default configuration does not perform, which is how seven call sites came to rely on a guard that does nothing.

**Why this fix:**

Version A is the right fix. It removes the option dependence entirely, and because it sorts on `getIdLong()` rather than `getFullName()` it is *cheaper* than the behaviour the option already enables — so the cost objection recorded in CL `13530532` (*"Should better modify ctsModuleCompare as it check lib id, but this could cost a lot"*) does not apply to it. Version B should land regardless of Version A, because the `std::map<float, ...>` tie-drop is a data-loss bug in its own right: tied lib cells never reach `passedSet` no matter how the input is ordered. Fixing only A leaves that silent pruning in place; fixing only B leaves six other inert call sites.

**False-positive check:**

Verified rather than assumed: the early return and the option's `false` default were read directly (`ctsutil/ctsUtils.cc:57`, `ctsutil/ctsAppOptions.cc:2124`, `ctsui/ctsuiOptimizeAppOptions.cc:2130`); the `std::map<float, ndmModule*>` declaration and its iteration were read at `ccd/ctsccd/ccdSinkSize.cc:301-337`; and all 7 call sites of `sortModulesByName` plus all 8 callers of `getCcdLeqVec` were enumerated by grep. Three call sites were deliberately **excluded** as safe: `fmaxVariable.cc:275`, `:305`, `:320` build their vectors from `std::map<int, ndmModule*>`, an integer-keyed ordered map, so the source is already canonical and the inert sort costs nothing there. The sibling helper `sortModulesByLongKey()` (`ctsutil/ctsUtils.cc:70`) is *not* included: its `else` branch uses `std::stable_sort`, which preserves input order for ties rather than randomizing it.

**Code ownership (Perforce):**

- **Depot:** `//synopsys/nwtn/main/dev/nwtn/src/cts/ctsutil/ctsUtils.cc`
- **Primary logic (annotate):** all 13 lines of the `:51-63` window — `useModNameToSortLibs()`, `sortModulesByName()` and its early return — belong to CL `13530532`.
- **Describe summary:** CL `13530532` by **`zhejia`**, 2026-04-16 — *"Sort leq to prevent ND. Reuse the existing app option cts.optimize.use_module_name_to_sort_libs (Should better modify ctsModuleCompare as it check lib id, but this could cost a lot)"*, with IREG synreg and Pre_CI_ex207 PRS links; `jira_id: P10235709-211831`.
- **CMT chain:** `zhejia@CMT_dgplt_dgplt_main` — no `ORIG_CLIENT` tag, so `zhejia` is the authoring user.
- **Related sites, same CL:** the call site and its comment at `ccd/ctsccd/ccdscGlobal.cc:3454-3455` (`// Merge from different sources can perturb order`) are also CL `13530532`.
- **Consumer ownership:** the order-sensitive `std::map<float, ndmModule*>` loop in `ccd/ctsccd/ccdSinkSize.cc:301-302` belongs to CL `2593396` by **`tao`**, 2014-08-22 (*"Reorganizing CCD code and app variables"*). The OPT-purpose merge block in `getCcdLeqVec` belongs to CL `12637589` by **`pengchou`**, 2025-10-29, which wrapped it in the hidden, false-by-default `ccd.register_sizing_includes_opt_purpose_lib_cells`.
- **Notes:** `zhejia` is the right owner. The CL text shows the author knowingly chose the cheaper option-gated form over the stable-ID comparator, and this finding is that the chosen form is inert at the option's default.

---


## LOW Severity Issues

_No low severity findings._


## INFO Severity Issues

_No info severity findings._


---

## Generic Fix Patterns

> See `references/fix-recipes.md` for the full set. Excerpts most relevant
> to this module:

The recurring shapes in this module, and the idiom that fixes each:

**1. Partial-key comparator leaves ties in address order.** The single most
common real defect here. A vector is snapshotted out of a pointer-keyed
container and sorted by one float or one int, so every tie group retains the
address-derived input permutation — and `std::sort` is not stable, so even the
tie group's internal order is unspecified.

```cpp
// BEFORE: ties keep whatever order the address-ordered map produced
std::sort(vec.begin(), vec.end(), [](const auto& a, const auto& b) {
  return a.second.offset < b.second.offset;
});

// AFTER: complete the order with a stable identity tie-break
std::sort(vec.begin(), vec.end(), [](const auto& a, const auto& b) {
  if (a.second.offset != b.second.offset) {
    return a.second.offset < b.second.offset;
  }
  return a.first->getIdLong() < b.first->getIdLong();   // O(1), no alloc
});
```

**2. Pointer-keyed container that is genuinely iterated.** Keep the fast
lookup structure; add stable order only at the point where order is observed.
Do **not** convert `unordered_*` to `std::map` in hot code — that trades O(1)
for O(log N) on every lookup to fix an iteration that may happen once.

```cpp
// Keep the O(1) container for lookups.
std::unordered_map<ndmTerm*, float> cache;

// Canonicalise only at the consumer that observes order.
std::vector<ndmTerm*> keys;
keys.reserve(cache.size());
for (const auto& kv : cache) {
  keys.push_back(kv.first);
}
std::sort(keys.begin(), keys.end(), ndmObjPtrCmpType{});   // (ndmType, ndmID)
for (ndmTerm* t : keys) {
  consume(t, cache[t]);
}
```

**3. Declaration-level fix when the container is small or cold.**
`ndmObjPtrCmpType` is the in-tree alias for `ndmObjectHandleNS::compareObjPtr`
(`ccd/util/ccdUtil.h:71`) and compares identity, not address.

```cpp
std::map<ndmTerm*, Info, ndmObjPtrCmpType> m;   // was std::map<ndmTerm*, Info>
std::set<ndmModule*, ndmObjPtrCmpType>     s;   // was std::set<ndmModule*>
// or, for ndm objects, prefer the project container outright:
ndmPtrMap<ndmTerm*, Info> m2;
```

**4. Pointer mixed into a hash functor.** Hash the stable ID, not the address.
Check first whether an ID-based hash already exists — in this module
`ctsutil/ctsTypes.h:857` already provides `std::hash<ctsNS::sclkCornerType>`.

```cpp
// BEFORE
return std::hash<ctoSclkBag*>()(pair.bag) ^ boost::hash<cstrCornerId>()(pair.corner.getId());

// AFTER
std::size_t h = 0;
boost::hash_combine(h, pair.bag->getIdLong());
boost::hash_combine(h, pair.bag->getObjectType());
boost::hash_combine(h, pair.corner.getId());
return h;
```

**5. Shared-container writes under `tbb::parallel_for`.** Write by pre-sized
index, or use per-thread buffers concatenated in deterministic index order.
Never `operator[]` a shared `std::map` from a parallel body — that is a data
race, not just an ordering problem.

```cpp
// BEFORE: concurrent operator[] rebalances a shared red-black tree -> UB
tbb::parallel_for_each(scenarios, [&](cstrScenario& sc) {
  auto& infos = _scenarioInfosMap[sc];          // RACE
  ...
});

// AFTER: pre-populate outside the loop, then index read-only inside
for (const cstrScenario& sc : scenarios) {
  _scenarioInfosMap[sc];                        // create all nodes serially
}
tbb::parallel_for_each(scenarios, [&](cstrScenario& sc) {
  auto& infos = _scenarioInfosMap.at(sc);       // no structural modification
  ...
});
```

**6. Thread-count-dependent chunking.** Chunk sizes derived from
`hardware_concurrency()` / `max_concurrency()` make results machine-dependent.
Use a fixed grainsize, or a configured count
(`crmResources::get().getMaxThreadCount()`), and keep partial sums grouped by
a fixed partition rather than by thread.

**7. `std::unique` and float-keyed maps silently drop data.** `std::unique`
removes only *adjacent* duplicates, so it must be preceded by a sort on the
same key its equality uses. A `std::map<float, T*>` rejects duplicate keys
outright, so tied entries are discarded by input position — see
`ccd/ctsccd/ccdSinkSize.cc:301`.

Full catalog: `references/fix-recipes.md` and `references/id-system.md`.

---

## Coding Guidelines

### DO

1. Use `ndmPtrMap<K,V>` for pointer-keyed maps of ndm objects.
2. Use `std::map<T*, V, ndmObjectHandleNS::compareObjPtr>` for non-ndmPtr
   pointer-keyed maps.
3. Use `hySet<T*, hySetPtrCmp<T>>` / `hyMap<K*, V, hySetPtrCmp<K>>` when
   iteration must follow insertion order (the most common ND-prone case).
4. Use `std::mt19937` with a seed derived from input data.
5. Compare by `getIdLong()` + `getObjectType()` (both O(1)).
6. Hash by `getIdLong()` + `getObjectType()` via `boost::hash_combine`.
7. Sort `unordered_*` contents into a `std::vector` before iterating when
   order matters.

### DON'T

1. Use `std::set<T*>` / `std::map<T*, V>` with the default comparator.
2. Use `std::unordered_*<T*>` with default hash and expect stable iteration.
3. Use `std::random_shuffle` (deprecated).
4. Use `rand()` / `srand()` directly.
5. Use `getFullName()` / `getPathName()` for comparison (O(d) + alloc).
6. Assume IDs are globally unique — they can collide across types/contexts.

---

## Module-Specific Summary

`nwtn/src/cts` is, on the whole, **determinism-aware code that has been
worked on repeatedly** — and that shapes both the findings and the noise.

Three signals make the point. First, the module is full of deliberate
determinism machinery: `ndmPtrSet` / `ndmPtrMap` (ordered by
`dosContainer::keyCompare`, i.e. by `(ndmType, ndmID)`) account for 97 of the
141 project-wrapper hits, `nwcInsOrdMap` is documented in-tree as the
insertion-order remedy, and several concurrent containers carry a literal
`// need to make sure the order is deterministic` comment before being drained
into a sorted structure. Second, the dominant dismissal reason across every
slice was **membership-only use**: roughly 200 of the pointer-keyed containers
flagged are `visited` guards, dedup sets, or lookup caches that are never
iterated, so their address ordering is unobservable. Third, several of the
findings sit *on top of* a previous ND fix rather than in virgin code.

That third point is the theme worth taking away. The most valuable findings in
this report are not "someone used `std::set<T*>` by accident" — they are
**incomplete or inert mitigations**:

- `mscts/drivers/msDrivers.cc` converts a map to a vector `// for deterministic
  behaviour`, then sorts it with a comparator that only compares hierarchy
  depth, so sibling blocks at equal depth keep their address-derived order.
- `ctsutil/ctsUtils.cc` has a helper written expressly to "sort leq to prevent
  ND" (CL `13530532`) whose body begins with an early return at the app
  option's default value, making it a no-op in the default flow at all seven
  call sites.
- `ctssc/ctskSize.cc` keys on `getFullName()` *because* that was the ND fix
  (CL `4151071`, ": Fixed non-deterministic behavior in ccd"); the residual
  issue is the O(depth)+allocation cost it bought, not a reproducibility bug.
- `ctssch/ctsTimingDrivenTransitionTargets.h` sorts by criticality but its
  comparator is not a strict weak ordering, so the tie-break it was meant to
  impose is unspecified.

The two genuinely *new* defects are in recently-touched parallel code:
an unguarded concurrent `std::map` insertion in the skewopt CG solver
(introduced by an app-option cleanup refactor, CL `13914296`, with the correct
pre-sized idiom already present forty lines below), and thread-count-dependent
partial-sum grouping in the fmax cost functions.

**Where to start.** Fix `ccd/skewopt/soSolverUpdater.cc:2100` first — it is
undefined behaviour, not merely an ordering issue, and can corrupt the
red-black tree or silently drop a scenario from the CG objective. Then
`ctsmisc/ctsAutoBalancePoint.cc:656` and `mscts/drivers/msDrivers.cc`, both of
which are default-on and reach a database write, and both of which are
five-line comparator tie-breaks. `ctsutil/ctsUtils.cc:57` is the cheapest
high-leverage change in the report: making the guard unconditional and keying
it on `getIdLong()` instead of `getFullName()` is *faster* than the behaviour
the option already enables, which removes the cost objection its own author
recorded in the CL.

**What this audit cannot tell you.** Every finding here is established from
source only. Nothing was compiled, run, or A/B'd, so no run-to-run variance
has been *demonstrated* for any row — the claims are that the mechanism is
present and that the order reaches an observable sink. Several findings also
depend on code outside `nwtn/src/cts` (the `opt` LEQ provider, `timerInterf`,
`crm.h` thread defaults, `util/dos*.h` wrapper definitions), which this
snapshot does not contain. The per-finding sections say which.

---

## Methodology

This report was produced by the `nd-code-analyzer` skill in three stages:

1. **Mechanical scan (`scan_nd.py`):** loads
   `references/nd-patterns.yaml` and runs each pattern's regex over the
   target path using ripgrep (or mgrep for Perforce branches).
2. **LLM triage:** for each candidate, the LLM reads ±10 lines of
   surrounding context, confirms it's a real positive (filtering against
   `false_positive_hints_md`), and assigns a severity tailored to the call
   site.
3. **Tier 2 deep-read:** for parallel / FP-reduction / unordered-iteration
   patterns, the LLM follows data-flow to confirm the result actually
   affects output.
4. **Render:** this report is generated from a template.

To re-run with different filters:

```bash
~/.claude/skills/nd-code-analyzer/scripts/scan_nd.py \
    --path /remote/us01home05/carys/cts  (snapshot of nwtn/src/cts) \
    --min-severity HIGH \
    --tier 1 \
    --out candidates.json
```

To extend with a new ND pattern: add an entry to
`~/.claude/skills/nd-code-analyzer/references/nd-patterns.yaml` and the
narrative mirror in `nd-patterns.md`. No code changes required.

---

## Dismissed Buckets

The funnel, so the filtering can be spot-checked without re-triaging every site:

| Stage | Candidates in | Dismissed | Out |
|---|---:|---:|---:|
| Stage 1 mechanical narrowing | 11,427 | 9,857 | 1,570 |
| Stage 2/3 deep-read triage | 1,570 | 1,370 | 200 |
| Grouped into findings | 200 | — | **19 defects + 24 LOW** |


### Stage 1 — mechanical narrowing

Applied by `narrow_nd.py` using the skill's documented Stage-1 rules: balanced template-argument parsing to detect a supplied comparator or hash, pointer-vs-value key resolution, and a tree-wide index of which symbols are ever iterated. No LLM judgement involved, so these are cheap to re-verify.

| Count | Dismissal reason | Samples |
|---:|---|---|
| 4199 | 3.6 bare identifier word hit (`module`/`rows`/`leq`), not a collection site | `ips/ipsSplitter.cc:182`, `ips/ipsManager.h:80`, `ips/ipsManager.cc:1166` |
| 3001 | 3.3 iterated symbol is not a pointer-keyed unordered_* in this file | `ctsmisc/ctsMark.cc:176`, `ctsmisc/ctsExclude.cc:3498`, `ctsmisc/ctsExclude.cc:3508` |
| 1177 | 1.2 custom comparator/hash supplied (non-default) | `irs/irsContext.h:74`, `irs/irsContext.h:151`, `ctsui/ctsuiSyn.cc:1020` |
| 547 | 1.2 container never iterated (membership/lookup only) | `irs/irsBCT.h:43`, `irs/irsMgr.h:62`, `irs/irsMgr.cc:78` |
| 274 | 1.1 explicit comparator supplied (needs read, not default-ptr sort) | `ctsmisc/ctsLatencyBottleneckChecker.cc:142`, `cts/ctsManager.cc:4987`, `cts/ctsManager.cc:5025` |
| 227 | 1.3 container never iterated (membership/lookup only) | `cts/ctsManager.h:307`, `cts/ctsManager.h:308`, `cts/ctsManager.h:359` |
| 108 | 1.2 key is a value type, not a pointer | `ctsmisc/ctsLatencyBottleneckChecker.h:74`, `ctsmisc/ctsLatencyBottleneckChecker.cc:185`, `ccd/ctsccd/twns/ccdtwnsProblemGenerator.h:720` |
| 73 | 3.7 wrapper already declares stable comparator/hash | `ips/ipsManager.cc:300`, `ips/ipsManager.cc:323`, `ips/ipsManager.cc:324` |
| 70 | 1.1 sorted element type is a value type (not pointer) | `ctsinterf/ctsIfsDelayOffsetData.cc:101`, `ccd/util/ccdOutputUtil.h:64`, `mscts/mstap/msClustering.cc:671` |
| 54 | 1.2 stable project comparator/hash already supplied | `ccd/util/ccdDPAMgr.cc:53`, `ccd/util/ccdDPAMgr.h:86`, `ccd/util/ccdUtil.h:240` |
| 48 | 1.1 element type unresolved in same file | `ctsinterf/ctsIfsInterf.cc:880`, `mscts/mstap/msTapSubtreeSyn.cc:285`, `mscts/mstap/msTapSubtreeSyn.cc:805` |
| 31 | 1.3 key is a value type, not a pointer | `ctsinterf/ctsInterf.h:142`, `ctsinterf/ctsInterf.cc:1707`, `ctsinterf/ctsIfsInterf.h:477` |
| 20 | 1.3 stable project comparator/hash already supplied | `ctssch/ctsPowerDrivenGateRelocator.h:285`, `ccd/skewopt/soClockGateOpt.cc:958`, `ccd/skewopt/soClockGateOpt.cc:959` |
| 13 | 1.3 custom comparator/hash supplied (non-default) | `ctssc/lazytns/ctsLazyModel.cc:2305`, `ctssc/lazytns/ctsLazyModel.cc:2421`, `ccd/skewopt/soClockGateOpt.h:135` |
| 9 | 3.3 loop body has no order-propagating side effect | `ctscto/ctoFlowMgr.cc:2167`, `ctsutil/ctsObjId.cc:49`, `ctsutil/ctsPortPunchAnalyzer.cc:1502` |
| 6 | 1.1 could not resolve sorted container expression | `rlx/core/util/cnm/cnmNetwork.cc:1607`, `ctsrpt/ctsGetClockTreePins.cc:4390`, `mscts/mstap/msFlexibleTapPartition.cc:365` |


### Stage 2/3 — deep-read dismissals

73 buckets covering 1,802 rows. These required reading the code. Note that the pattern-1.1 row is a **cross-stage summary** of all 403 sort hits (398 removed mechanically above, 5 survivors read individually), so it overlaps the Stage-1 table by design rather than adding to it.


### Pattern 1.1

| Count | Bucket | Why dismissed |
|---:|---|---|
| 403 | Pointer-vector sorts that already carry a deterministic comparator or rely on stable_sort | All 403 pattern-1.1 hits were resolved without promoting one. The scanner's second regex is a bare `std::sort\s*\(`, so it matches every sort in the module. Mechanical narrowing accounted for 398: 274 pass an explicit comparator, 70 sort a value type rather than a pointer, 48 have an element type that is not resolvable in the same translation unit, and 6 have an unparseable container expression. The 5 survivors were read individually and are all false positives of the narrowing itself — the paren walker mis-split multi-line lambdas. `ctsutil/ctsUtils.cc:60` and `:73` compare `getFullName()` strings, a total order; `:86` and `ctsutil/dly/dlyCoreUtil.cc:1873` use `std::stable_sort`, which preserves input order for ties instead of randomizing it; and `ctssc/ctsscMvMgr.cc:681` takes a caller-supplied `ctsscMvMgr::RefCellCmp`. Note that the two `stable_sort` sites are deterministic *given* a deterministic input order, so they inherit rather than create instability. |


### Pattern 1.2 — std::set / std::map with pointer key, default comparator

| Count | Bucket | Why dismissed |
|---:|---|---|
| 15 | ccdResultIntegrator `pMaps` / `slacks` / `preSlacks` / `postSlacks` - find+insert+erase only | This bucket looked like the most promising HIGH in the whole slice - a pointer-keyed map in the code that reverts committed CCD transforms - so I traced it end to end. `std::map<ndmTerm*, ctsXformProblem*> pMaps` (`ccd/ctsccd/ccdResultIntegrator.cc:70`) has a default comparator, but it is never iterated: the only accesses are `insert` during construction (`ccd/ctsccd/ccdResultIntegrator.cc:75-88`) and `find`/`erase` inside `revertOnPath()` (`ccd/ctsccd/ccdResultIntegrator.cc:175-181`). The revert order is set by `badVec`, a `std::vector` filled while walking the timer's critical-path iterator (`ccd/ctsccd/ccdResultIntegrator.cc:174`), and consumed in vector order at `ccd/ctsccd/ccdResultIntegrator.cc:190-199` where `ctsUndoCommit` / `setFoundSolution(false)` actually mutate state - so the mutation sequence is timer-driven, not address-driven. I also checked the duplicate-key hazard: `pMaps.insert` does not overwrite, so which problem wins for a shared driver term is decided by the deterministic `problems[i]` and `connIterator` order, not by the comparator. The three `getRootSlacks` overloads and `isSlackWorseBy`/`isSlackNegative` (`ccd/ctsccd/ccdResultIntegrator.cc:356`, `:362`, `:386`, `:407`, `:423`, `:447`) likewise only `find`/`insert` on `std::map<ndmTerm*, std::vector<float>>`, indexing slack vectors by term. Header rows are the matching signatures. Samples: `ccd/ctsccd/ccdResultIntegrator.cc:70`, `ccd/ctsccd/ccdResultIntegrator.cc:128`, `ccd/ctsccd/ccdResultIntegrator.cc:167`. |
| 14 | Stale header / local-iterator type text - the owning container supplies a stable comparator | In each case the scanner matched a declaration or a local iterator typedef spelled `std::map<T*, V>` / `std::set<T*>`, but the object that actually owns the data is declared with a deterministic comparator. Verified each owning declaration:  - `ctscto/ctoFlow.h:577,581,582,585,586,588,589,590` (8 sites) - the `netDrcMap` parameters. Every definition in `ctscto/ctoBB.cc` uses `std::map<ndmNet*, ctoDrc*, ndmObjPtrCmpType>` (`ctoBB.cc:356,565,688,766,797,850,902,929`) and both owning objects are declared that way (`ctoBB.cc:252,326`). The iteration at `ctoBB.cc:905` is therefore ID-ordered. - `ctscto/ctoFlowMgr.cc:1464` and `ctscto/ctoFlow.cc:1704` (2 sites) - `termClockGroupMap`. Owner is `ctoCost.h:328` `std::map<ndmTerm*, ctsClockGroup*, ndmObjPtrCmpType> _termClockGroupMap`; `getTermClockGroupMap()` at `ctoCost.h:382,386` returns that type. `ctoGrpLatCalc.cc:46` spells it correctly. - `ctscto/ctoFlow.cc:5332` (1 site) - `loadLongSlackMap`. Owner signature is `std::map<ctsSclk*, termFloatMapType, ctsPtrObjCompare<ctsSclk>>` (`ctoFlow.cc:5799`); `ctsPtrObjCompare` dereferences and uses `*lhs < *rhs` (`ctsutil/ctsTypes.h:545-550`), a value comparison on the `ctsSclk` handle. - `ctscto/ctoRestruct.cc:203` (1 site) - `_flow->_ctoBuffers` is `dosSet<ndmInst*>` (`ctscto/ctoFlow.h:665`). - `ctscto/ctoLocalSkewMgr.cc:3497` (1 site) - `_sinkInfoMap` is `termInfoMapType` = `std::map<ndmTerm*, sinkInfo*, ndmObjPtrCmpType>` (`ctoLocalSkewMgr.h:44`). Its many iterations (`:3030,3116,3169,3428,3460,3760,3776,3793`) are ID-ordered. - `ctssc/ctsscBufInfoMgr.cc:744` (1 site) - `_nCoveredSinks` is `std::map<ctsscHierNode*, int, ctsscHierNodePtrCmp>` (`ctsscBufInfoMgr.h:260`); `ctsscHierNodePtrCmp` compares `node->getTerm()->getId().ulong()` (`ctsscBufInfoMgr.h:188-196`). The `+=` at `:745` is an integer sum anyway.  All six of these are safe-adopter. Flagged for the reader: in every case the short spelling and the owning declaration are *different C++ types* and could not both compile, so this snapshot is textually inconsistent - see notes_md.  Sample sites: `ctscto/ctoFlow.h:589`, `ctscto/ctoFlow.cc:5332`, `ctssc/ctsscBufInfoMgr.cc:744`. |
| 9 | multimap equal-range traversal only - lower_bound/upper_bound on one key, insertion order preserved within a key | These sites never walk the whole multimap; they bracket a single key with `lower_bound(k)` / `upper_bound(k)` and walk that range. Since C++11, `std::multimap` guarantees that elements with equivalent keys stay in insertion order, so the traversal order inside a bracket is deterministic. The address-ordered comparator only decides where the bracket sits in the tree, which is never observed.  - `ctssc/ctsscConflictChecker.cc:98,99,104,128,129,161,162` (7 sites) - `_lvmap` (`std::multimap<ndmTerm*, LVLM>`, `ctsscConflictChecker.h:118`). `addRecord` (`:96-115`), `isMarked` (`:125-148`), `markSelected` (`:157-...`) all bracket one `fanout`/`term`. Insertion is a single `_lvmap.insert` at `:114`. Verified there is no full-range iteration anywhere: the only other touches are `clear` (`.h:81`, `.cc:51`), `erase(bit1)` inside a bracket (`:106`), and `empty()` (`:127,159`). - `ctscto/ctoSize.cc:656,657` (2 sites) - `_altInstModuleMap` (`std::multimap<ndmInst*, ndmModule*>`, `ctoSize.h:247`). Bracketed on `inst`; `prunedVector.push_back(lit->second)` at `:659` therefore emits in the insertion order established at `:709`, which follows the module vector. Other uses are `clear` (`:187`) and `find` (`:620`).  Sample sites: `ctssc/ctsscConflictChecker.cc:98`, `ctscto/ctoSize.cc:656`. |
| 8 | Declaration is inside a /* */ comment block - scanner matched commented-out code | Eight candidates are text inside comments, not compiled declarations. The scanner's regex matched the container spelling without tracking comment state.  Representative: `mscts/msmesh/msInstSnapper.h:31` and `:39` - the whole parameter list, including `std::map<ndmNet*, ndmGeoMask> &netShapes`, sits inside a `/* ... */` block that comments out two declarations of `snapInstsToShapeGrid`. Same at `mscts/msmesh/msInstSnapper.cc:62` and `:104` (the matching commented-out definitions), `mscts/msmesh/msInterfSnap.cc:39`, `mscts/mscore/msInterf.h:122`, `mscts/drivers/msDriverRemoval.h:201` and `mscts/msutil/msInfra.cc:2268`.  Verified by reading the surrounding lines at each site to locate the opening `/*` and closing `*/`. No `#if 0` involved - these are ordinary comments, so the classification is **false-positive**, not dead/unused. |
| 8 | false-positive: match text is inside a comment, or is an unused local variable | Not live code.  - `ips/ipsManager.cc:2166/2260/2273/2282` are the commented-out `clkArrEnSlackMap` remnants of a refactor; the live replacement on the adjacent lines is `std::vector<std::pair<ndmTerm *, std::pair<float, float> > > clkArrEnSlackVec` (`ips/ipsManager.cc:2167`), iterated at `:2274` in **vector** order - i.e. the developer already replaced the pointer-keyed map with a vector. Nothing to fix. - `ctsmisc/ctsAutoBalancePoint.cc:1678` is a `//`-commented `getNodes()` line. - `ctssch/ctsGuideBufferMgr.cc:2696` is `//`-commented and `:2851` sits inside the `/* ... */` block opened at `ctssch/ctsGuideBufferMgr.cc:2850`. Note this one *would* have been real if live - the commented body calls `mode.removeCtsDelayPoint(...)` at `:2853`, a DB mutation driven by map order. - `ctsutil/ctsBufChainReducer.cc:596` declares `std::set<ndmModule*> prunedSet;` which is **never used** anywhere in `getAllCandidateModules()` - the function works on `prunedVector` instead. `rg 'prunedSet' ctsutil/ctsBufChainReducer.cc` returns exactly one line, the declaration. Dead local; candidate for deletion. |
| 7 | safe-adopter / false-positive: container IS declared with ndmObjPtrCmpType or another stable custom comparator; the scanner matched a comparator-less ITERATOR spelling | This is the single largest source of noise in the slice and it has one root cause: in libstdc++, `std::map<K,V,C>::iterator` is `_Rb_tree_iterator<pair<const K,V>>` and `std::set<K,C>::iterator` is `_Rb_tree_const_iterator<K>`, both **independent of the comparator `C`**. So code can legally (and here does) write `std::map<ndmTerm*, float>::iterator it = someMap.find(...)` against a map declared with a third comparator argument. Matching on the iterator spelling therefore proves nothing; only the declaration does.  Verified declarations: - `ips/ipsManager.cc:1867` -> `guideBPTable` is `std::map<ndmTerm *, float, ndmObjPtrCmpType>` at `ips/ipsManager.cc:1586`. Its commit loop at `ips/ipsManager.cc:1691` (which does reach `setCtsDelayPoint`-class writes at `:1697+`) is therefore already deterministic. This one mattered most to check, because the sink is a real DB write. - `ctsmisc/ctsExclude.cc:694,726` -> `primaryCornerDelays` is `std::map<ndmTerm*, ctsBalancePointValues, ndmObjPtrCmpType>` at `ctsmisc/ctsExclude.cc:634`; `primaryCornerBalanceTerms` is `termSetType` (`:640`). - `ctsmisc/ctsCheckReporting.cc:2337` -> `_mapCheck909` is `std::map<ndmTerm*, ctsCheck909*, ndmObjPtrCmpType>` at `ctsmisc/ctsCheckReporting.h:685`, so the CTS-909 report loops at `ctsmisc/ctsCheckReporting.cc:2279` and `:2349` are ordered. - `ctsmisc/ctsAbstraction.cc:1314` -> `_netDelays` is `std::map<ndmTerm*, netDelayInfo, ndmObjPtrCmpType>` at `ctsmisc/ctsAbstraction.h:220`. - `ctsutil/ctsLocalSkew.cc:186,190` -> `clkNode::_sp_pairs` / `_ep_pairs` are `std::set<clkNode *, clkNodePtrCmp>` at `ctsutil/ctsLocalSkew.h:95-96`, and `clkNodePtrCmp` (`ctsutil/ctsLocalSkew.h:62-70`) compares `id()`. |
| 3 | Commented-out declarations and an iterator type that omits the container's real comparator | Three genuine scanner artifacts. `ccd/ctsccd/voltagedrop/ccdvdFilter.h:126` is the comment line `//std::map<ndmInst*, ccdvdPD> _inst2pw_map;` and `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:328` is the comment `//void filterForPower(cstrScenario scenario, std::map<ndmModule*, float>& size2pod,` - neither declares a container. The third is the most instructive: at `ccd/ctsccd/drc/ccddrcResultIntegrator.cc:763` the loop spells its iterator as `std::map<ndmTerm*, std::pair<ctsXformProblem*, float> >::iterator`, with no comparator, which is what the scanner matched - but the container it iterates is declared 50 lines earlier at `ccd/ctsccd/drc/ccddrcResultIntegrator.cc:713` as `std::map<ndmTerm*, std::pair<ctsXformProblem*, float>, ndmObjPtrCmpType> pMaps;`, i.e. **with** a stable comparator. The mismatch compiles because in libstdc++ `std::map<K,V,C>::iterator` is `_Rb_tree_iterator<pair<const K,V>>` and does not depend on `C`. `ndmObjPtrCmpType` is `typedef ndmObjectHandleNS::compareObjPtr` (`ccd/util/ccdUtil.h:71`, `ctsutil/ctsTypes.h:63`), so this revert path - which does mutate state via `setFoundSolution(false)` at `ccd/ctsccd/drc/ccddrcResultIntegrator.cc:775` - is already deterministic. Worth noting for future scans: match the declaration, not the iterator spelling. Samples: `ccd/ctsccd/voltagedrop/ccdvdFilter.h:126`, `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:328`, `ccd/ctsccd/drc/ccddrcResultIntegrator.cc:763`. |
| 3 | Pointer-keyed map iterations in functions with no reachable caller | Three iteration sites are unreachable because their enclosing member function is never called anywhere in the tree. `getTotalInitialPower()` sums `std::map<ndmInst*, float> _initialPower` in address order at `ccd/ctsccd/power/ccdpwProblemGenerator.h:181` and `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:182` - a genuine non-associative float accumulation, and the strongest HIGH candidate in the slice on inspection. A tree-wide search for `getTotalInitialPower` returns only these two definitions (`ccd/ctsccd/power/ccdpwProblemGenerator.h:179`, `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:180`) and no call site; it is also not virtual and has no base declaration in `ctssc/ctsscProblemGenerator.h` (unlike the sibling `addInitialPower`, which is virtual at `ctssc/ctsscProblemGenerator.h:326`), so there is no dispatch route to it either. The `awp/` and `drc/` copies of the class do not even define the function. Similarly `ccdawpFilter::dumpPowerDelta` iterates the default-comparator `std::map<ndmInst*, ccdpwPD> _inst2pw_map` (`ccd/ctsccd/awp/ccdawpFilter.h:120`) at `ccd/ctsccd/awp/ccdawpFilter.cc:540` to build a report - and the `awp` variant has no caller, while its `power/` and `voltagedrop/` twins are called (`ccd/ctsccd/power/ccdpwFilter.cc:198`, `ccd/ctsccd/voltagedrop/ccdvdFilter.cc:207`) and the `power/` copy already carries `ndmObjPtrCmpType` (`ccd/ctsccd/power/ccdpwFilter.h:148`). **Recommendation:** these are latent landmines rather than defects - if any is ever wired up it becomes a real finding, so the cheap hardening is to add `ndmObjPtrCmpType` to `ccd/ctsccd/awp/ccdawpFilter.h:120` (matching its already-fixed `power/` twin) and to accumulate `getTotalInitialPower` over a sorted snapshot. Per the brief I counted only real `#if`/build-macro exclusion or absent callers as dead; no `purecov`/Coverity comment was used as evidence. Samples: `ccd/ctsccd/awp/ccdawpFilter.h:120`, `ccd/ctsccd/power/ccdpwProblemGenerator.h:181`, `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:182`. |
| 3 | Dead or unused - no reachable caller, or typedef never instantiated | Three candidates have no reachable consumer.  `mscts/drivers/msDrivers.cc:3335` and `:3350` are `std::map<ndmBlkNet*, std::vector<ndmTerm*> > nets` inside `msClockDrivers::connectUnassignedLoads`. This was my closest call in the slice: the traversal genuinely reaches `connectTerms`, which hands out generated names from the shared `_nameCounters[prefix]` counter (`mscts/drivers/msDrivers.cc:10883`, `:10923`), so had the function been live this would have been a real finding on naming. But `connectUnassignedLoads` has exactly two occurrences in the entire tree - its declaration and its definition. I searched all of `/remote/us01home05/carys/cts`, not just `mscts/`, and found no call site, no function-pointer reference and no Tcl binding. It is compiled but unreachable.  `mscts/drivers/msPDXingMgr.h:64` is a `termIndexMap` typedef with a default comparator - notable because it shadows the stable `termSetType`/index idioms used elsewhere - but the typedef is never instantiated anywhere in the tree, so no container of this type exists.  Note on method: I did **not** use `purecov` or Coverity annotations as evidence of dead code anywhere in this slice (for example `mscts/drivers/msDrivers.cc:5899` carries one and was judged on its own merits). These three rest on caller search and instantiation search.  Classification: **dead/unused**. If `connectUnassignedLoads` is ever wired up, `mscts/drivers/msDrivers.cc:3335` should be re-opened as a real naming-order defect. |
| 3 | Dead code - commented out, unused type alias, or unused local | - `ctscto/ctoFlow.h:772` - the whole line is a `//` comment: `//void restructFlow(std::set<ndmTerm*> candidates, std::set<ndmTerm*> lpCandidates, int maxClockTree);`. Scanner matched comment text. False positive. - `ctscto/totalskew/ctoAbsTree.h:124` - `using cnmNodeToNodePathVecMap = std::multimap<cnmNetwork::Node*, pathVecType>;` is an alias with zero uses. `rg cnmNodeToNodePathVecMap` across the whole tree returns only the definition. No object of this type is ever constructed. Dead/unused. (For contrast, the alias's neighbours `cnmNodeSetType` / `cnmEdgeSetType` resolve to `std::set<Node*, Node::comparePtr>` and `std::set<Edge*, Edge::comparePtr>` at `rlx/core/util/cnm/cnmNetwork.h:228,330`, i.e. already safe.) - `ctscto/totalskew/ctoAbsTreeTest.cc:377` - `std::map<ctoAbsVariable*, float> varDelayMap;` is declared inside `testUpdatePathVariable` and never read or written in that function; the loop body only touches `pathVar` and `delay`. Unused local.  Sample sites: `ctscto/ctoFlow.h:772`, `ctscto/totalskew/ctoAbsTree.h:124`, `ctscto/totalskew/ctoAbsTreeTest.cc:377`. |
| 3 | false-positive: timingInfoSet supplies a custom comparator (but see the adjacent non-ND comparator defect noted in notes_md) | `_sinkPinTimingInfoSet` is `timingInfoSet`, typedef'd at `ctssch/ctsTimingDrivenTransitionTargets.h:192` as `std::set<timingInfo*, compareTimInfo>` - a score-based comparator (`ctssch/ctsTimingDrivenTransitionTargets.h:182-189`), not `std::less<timingInfo*>`. The three scanner hits all spell `std::set<timingInfo*>::iterator`, which is comparator-independent. So no pointer-address ordering: **false-positive for patterns 1.2/1.3**.  I looked hard at this one because the consumer is genuinely order-sensitive: `targetNWorstSinks()` (`ctssch/ctsTimingDrivenTransitionTargets.cc:833-848`) takes the **first N** elements (`int counter = 1; ... if (counter < sinksToTarget)`) into `_tightTransitionSinkPinSet`, which decides which sinks get a tight `max_transition` target - a QoR-affecting choice. Had the comparator been defaulted, this would have been a HIGH. It isn't, so it is dismissed here. A separate, non-ND correctness defect in that comparator is recorded in `notes_md`. |
| 2 | Iterator type spelled without the comparator argument, but the container's typedef supplies a stable one | Two candidates are iterator declarations whose *spelling* omits the comparator while the container they are assigned from is stable.  `mscts/msmesh/msBufferInserter.cc:749` declares `std::set<ndmNet*>::iterator` and assigns from a `netSetType`, which `ctsutil/ctsTypes.h:127` defines as `std::set<ndmNet*, ndmObjPtrCmpType>`. `mscts/msmesh/msBufferInserter.cc:805` does the same against a `BlkNetPhyStatusMap`.  This compiles because in libstdc++ `std::set<T,Cmp>::iterator` does not depend on `Cmp` - both spellings name `_Rb_tree_const_iterator<T>` - so the two iterator types are the same type. The underlying container is comparator-stable, so iteration is deterministic. I flagged this as a distinct FP class early and re-checked every remaining `std::set<...>::iterator` / `::const_iterator` candidate in the slice against its container's typedef for the same trap. Classification: **false-positive / safe-adopter**. |
| 2 | Consumer outside the snapshot - could not verify, not claiming real | `ctssc/ctsscResultIntegrator.cc:634` and `:1005` declare `std::vector<std::map<ndmHier*, int>> legalStateVec(problems.size())`. The outer container is a vector indexed by problem number, so the *sequence* is deterministic. Each element is filled by `xformEngine::otfLegalization::getCurrentLegalState(legalStateVec[i])` (`:638,745,820,873,1010,1112`) and replayed by `restoreLegalState(...)` / `undoOTFLegalization(...)` (`:266,268,353,1061,1966`).  Whether the inner `std::map<ndmHier*, int>` iteration order is observable depends entirely on how `xformEngine::otfLegalization` replays it, and `opt/xformEngine.h` is not in this `cts` snapshot (`rg '::restoreLegalState/::undoOTFLegalization'` returns no definition anywhere under `/remote/us01home05/carys/cts`). I am not claiming this as real and not claiming it as latent - it is unverified.  Worth noting for whoever picks it up: `ctssc/ctsXform.h:274` defines `using localOtfStateType = std::map<ndmHier*, int, dosContainer::keyCompare>;` for the same legal-state shape, and `ctssc/ctsBuffer.h:688` uses `std::map<ndmHier*,int,dosContainer::keyCompare>& startState`. So the stable-comparator version of this exact map already exists in the module; the `ctsscResultIntegrator` declarations (and the `//LINTER_BYPASS` ones at `ctsscResultIntegrator.h:133,197`) are the odd ones out and should probably be aligned regardless of the ND answer.  Sample sites: `ctssc/ctsscResultIntegrator.cc:634`, `ctssc/ctsscResultIntegrator.cc:1005`. |
| 1 | Could not verify - order escapes into an API outside this snapshot | One candidate I am not able to resolve from this snapshot, reported as unverified rather than guessed.  `mscts/drivers/msDriverRemoval.cc:150` declares a pointer-keyed container whose traversal at `:180` filters `l_conns` into `l_finalConns`, which is then passed to `getGenericTimer()->removeCstrsFrom(l_finalConns, ...)`. The order of `l_finalConns` is therefore address-derived and does reach an external call.  Whether that is observable depends on whether the generic timer's constraint-removal API is order-sensitive - for instance whether removing constraints in a different sequence can leave different residual constraints, or emit messages in a different order. The timer lives outside `/remote/us01home05/carys/cts`, so I cannot read it here.  **Recommendation:** ask the timer owners whether `removeCstrsFrom` is order-insensitive. If it is, this is `latent-only`; if it is not, this is a real MEDIUM finding and the fix is the standard snapshot-and-sort on `l_finalConns` before the call. I have deliberately not counted it as a defect in the HIGH/MEDIUM totals. |


### Pattern 1.2, 1.3

| Count | Bucket | Why dismissed |
|---:|---|---|
| 31 | visited / dedup / membership sets - find, count, insert, erase only; never iterated | The single largest bucket: 31 candidates that are pure membership sets. Each is queried with `find`/`count`/`contains`, written with `insert`/`erase`, and sometimes `clear`ed or `size`d - but never traversed, so no consumer can observe the address order. Where such a set gates a traversal, the traversal order comes from a vector or from tree-successor iteration, not from the set.  The canonical case is `std::set<msLoadGroup*> visited` at `mscts/mstap/msTapSynthesis.cc:1551`: used only at `:1555` (`find`), `:1567` and `:1570` (`insert`); the node order actually fed to clustering comes from the `msTreeInputVec inputs` **vector**. This same set is what makes the mt19937 verdict (F7) safe, so it was worth checking carefully rather than dismissing on the variable name.  Sites, grouped by module: - tap synthesis / partitioning: `mscts/mstap/msTapSynthesis.cc:1551`, `mscts/mstap/msFlexibleTapPartition.cc:2121`, `:2279` - mesh / split / level balancing: `mscts/msmesh/msmtmesh/msmtLatencyFlowProblemGenerator.cc:418`, `mscts/msmesh/msSplit.cc:8284` (`visited`), `:8411` (`allVioNodes`, only `.size()` is read), `mscts/msmesh/msLevelBalancer.cc:2638`, `mscts/msmesh/msInterfSplit.cc:421` - core / data model: `mscts/mscore/msTreeNode.cc:4593`, `:4628`, `:4667`, `:4819`, `mscts/mscore/msDataModel.cc:10520`, `:11471`, `mscts/mscore/msDataModel.h:536` - constraint design (`toRemove` family, `find`-only): `mscts/msutil/msCstrDesign.h:665`, `:718`, `:726`, `:880`, `mscts/msutil/msCstrDesign.cc:5022`, `:5034`, `:5046`, `:6672` - interface API (`drivers`/`ignoredTerms` out-params, `insert`-only): `mscts/mscore/msInterfApi.h:40`, `mscts/mscore/msInterfApi.cc:698` - fishbone / routing: `mscts/fishbone/prMain.cc:459`, `mscts/fishbone/fbRouteInterf.cc:286`, `mscts/fishbone/fbMain.cc:239` - misc: `mscts/drivers/msDrivers.cc:10179`, `mscts/msgts/msgtsUtil.cc:2063`, `mscts/msui/msuiReconnectClockDrivers.cc:963`  Two worth calling out. `mscts/msui/msuiReconnectClockDrivers.cc:963` (`hierPortsRaw`) carries an explicit comment at `:961-962` explaining that a *raw* pointer comparator is deliberate, because `ndmObjectHandleNS::compareObjPtr` dereferences its arguments and the ports may already be freed - a stable comparator would crash here. `mscts/msmesh/msInterfSplit.cc:421` passes an `ignoredTerms` set that is always empty at the call site.  Classification: **latent-only**. These would become real if anyone added a traversal, which is the argument for eventually switching the declarations to `ndmPtrSet`/`ndmObjPtrCmpType` - but there is no defect today and 31 speculative edits to hot membership sets are not worth the risk. |
| 31 | Iterated, but every consumer is order-insensitive | Thirty-one candidates *are* traversed, but I read each loop body to its closing brace and confirmed the result cannot depend on the visit order. Four sub-shapes:  **(a) Per-key independent write.** Each iteration touches only the object it is visiting, with no shared state and no early exit. `mscts/drivers/msDrivers.cc:711` (`_cellTypes`, `restoreDesignType()` restores each design's own recorded type), `mscts/msui/msuiSynRegClkTree.h:95` with the traversal at `mscts/msui/msuiSynRegClkTree.cc:2227` (`_regGroupOptionsMap`; each group sets only its own top drivers, repeaters and h-tree repeaters). This is the same shape as finding F5's `setAttributeOnPorts`, and the presence of a `set*` call in the loop is *not* by itself enough to make it real - what separates F1 from this bucket is F1's mid-loop `return`.  **(b) Result inserted into a stable-comparator container.** The traversal order is erased by the destination. `mscts/drivers/msDrivers.cc:4204` (`unassignLoads`, traversed at `:4344` into the `ndmObjPtrCmpType`-ordered `termSetType _unassignedLoads` at `mscts/drivers/msDrivers.h:1285`), `mscts/drivers/msDrivers.h:417`, `:493`, `:1308` (`_loadNetSet` and friends, into `termSetType`), `mscts/drivers/msDrivers.cc:10309`, `mscts/mscore/msCharacterizer.cc:410` (`ELCPLibCells` into a stable set used only for `find` and an assertion), `mscts/mscore/msInterfApi.h:50` with `mscts/mscore/msInterfApi.cc:990`, `mscts/mscore/msInterf.h:71` with `mscts/mscore/msInterf.cc:1692`.  **(c) Commutative fold or existence test - the boolean or total is order-invariant.** `mscts/drivers/msDrivers.cc:9145` (`hierSet`, a set-union merge), `:2471`, `:7107` (`l_restrcited`, feeding `setMap` containers whose contents are order-independent at both levels), `mscts/drivers/msFlexibleTree.cc:430` (the `hierMap` loop at `:475` breaks on the first zero-tap entry, but the *boolean* outcome is the same whatever the order), `:1293`, `:1295` (`hierSinkMap` populated with zero values), `mscts/drivers/msFlexibleTree.h:137`, `mscts/msutil/msInfra.cc:2511`, `:2512`, `:2666`, `:2667` (unordered_set equality comparison, which is order-independent by definition), `mscts/mstap/msFlexibleTapPartition.cc:1872`, `:1881`.  **(d) Keyed lookup whose only observable is a count.** `mscts/msui/msuiReadGlobalTree.h:96`, `:103`, `mscts/msui/msuiReadGlobalTree.cc:331`, `:789`, `:906` (`unassignLoads` is indexed by key and `push_back`ed to; only `.size()` is read), `mscts/msmesh/msmtmesh/msmtLatencyFlowProblemGenerator.h:298`.  One in this bucket deserves its own note. `mscts/drivers/msDrivers.cc:2471` includes a `clusterGroupSet` whose elements are **deleted** in traversal order. Deletion order is not observable through any program value, but it does change the allocator's free-list shape, which can perturb the addresses handed out by later allocations - a second-order amplifier for every other address-ordered container in the flow. I recorded it as latent-only rather than real because there is no direct sink, but it is the one entry here I would revisit if the team ever chases residual ND after fixing F1-F3.  Classification: **latent-only**. |
| 12 | Lookup caches and side tables - find / operator[] / clear / size only; never iterated | Twelve candidates are pointer-keyed *maps* used purely as caches or side tables. Every access is a keyed lookup, an insert through `operator[]`, a `clear()` or a `size()`; none is traversed, so the hash or address order is never exposed.  - `mscts/msutil/msPreserve.cc:531` - preserve-status table. - `mscts/msutil/msInfra.h:350` - term-index side table. - `mscts/fishbone/fbBaseRouter.h:206` with `mscts/fishbone/fbBaseRouter.cc:2825` - `_table`, a mutex-protected router lookup; `find`-only under the lock. - `mscts/fishbone/fbPlacer.cc:98` - `_targetLocTable` (declared `mscts/fishbone/fbPlacer.h:56`); `find`-only. - `mscts/msgts/msgtsFlow.h:491` with `mscts/msgts/msgtsFlow.cc:5375` - sink-to-centre-location map. - `mscts/msmesh/msmtmesh/msmtLatencyFlowProblemGenerator.h:284` - `_wireDelays`; only `clear()`ed and written through a setter, never read in bulk. - `mscts/drivers/msDrivers.cc:4619`, `:4620` - `_configInstLevelMap1` / `_configInstLevelMap2`; insert and `find` only. - `mscts/drivers/msDrivers.cc:7337` - `_hasPrerouteStatus`; `find`-only. - `mscts/mscore/msCharacterizer.cc:424` - the `_ELCPLibCellMap` `find()` call; the map's key traversal is neutralized (bucket B3).  Also checked and dismissed here: `_seedDriverToWorstViolatorMap` (`mscts/msmesh/msmtmesh/msmtLatencyFlowProblemGenerator.h:298`, counted in B6) - its dedup check in `addSizingSeed` can never fire across distinct keys because each entry's key *is* its `_seedDriver`, and the destination `_seedMap` has a stable comparator.  Classification: **latent-only**. |
| 5 | Neutralized - order canonicalized by a stable sort before any consumer | Five candidates are pointer-keyed but the code already snapshots them and sorts by a deterministic key before anything observes the order. These are the *correct* version of the idiom that finding F2 gets wrong.  - `mscts/drivers/msDrivers.h:1309` - `_unusedTemplateCells`; copied to a vector and sorted by an id comparator before use. - `mscts/mscore/msCharacterizer.h:71` - `_ELCPLibCellMap`; the only direct access is `find()` (`mscts/mscore/msCharacterizer.cc:424`), and the keys are consumed through a snapshot sorted by a lib-cell comparator. - `mscts/msmesh/msIncrMerger.cc:242` - `outputNodeSet`; the traversal is preceded by a sort by tree-node id, with a comment stating that the sort exists because the set is pointer-ordered. - `mscts/msmesh/msActivityRelocator.h:124` - `_hashTblDrivers`; its traversal at `mscts/msmesh/msActivityRelocator.cc:456-458` only fills the stable-comparator `TreeNodeSet allDrivers`, which is what every consumer reads. - `mscts/msui/msuiReportPowerTaps.cc:698` - `std::unordered_set<ndmBlkInst*> seen` used for de-duplication, then `taplist.assign(seen.begin(), seen.end())`; canonicalized by `taplist.sort(compareByOrigin)` at `:712` before `reportTapsForShieldShape`.  **Caveat on the last one, stated honestly:** `compareByOrigin` orders by origin coordinate, which is not a total order - two tap instances at identical origins compare equal. `std::list::sort` is stable, so such ties retain the `unordered_set` bucket order. Coincident tap origins should not survive legalization, so I classified it neutralized, but if duplicate origins are possible in practice this one site would become a LOW report-order finding. |


### Pattern 1.2,1.3

| Count | Bucket | Why dismissed |
|---:|---|---|
| 22 | Membership / dedup only - find, count, insert, clear; never iterated | Each of these pointer-keyed containers is a visited-set or presence guard. I grepped every use of each symbol across the tree and confirmed no `begin()`/`end()`/range-for on the container itself; the actual ordering always comes from a `std::vector`, `std::deque` or `std::queue` alongside it.  1.2 sites (13): - `ctssc/lazytns/ctsSkewSlackCollector.h:212,213` - `_fromTerms` / `_toTerms`; only `insert` (`:151,155`) and `find` (`ctsSkewSlackCollector.cc:327,349`). - `ctssc/lazytns/ctsLazyModel.cc:2131` - `visited` in `findNetFanins`; dedup while walking `grArc` iterators, the returned value is a `std::set<grNodeId>`. - `ctscto/ctosc/ctoNfoProblemGenerator.cc:240` - `bagSet`; `insert(...).second` guard on a `std::queue` BFS. (Separately: `collectFaninBags` takes `faninBags` by value at `:236`, so its results are discarded entirely - a real bug, but not an ND one.) - `ctssc/ctsscMvMgr.cc:239,292` - `hierSet`; guards pushes into `_sgHierVec` and `hierMap`, whose order follows the `resistors` map / `lv` vector. - `ctssc/ctsXformProblems.cc:2557` - `_tMsgCount.find(&m)` in `tmsgCount`, a counter bump. - `ctssc/ctsscGlobal.h:641` - `_evaMap`; only `insert` (`:638`) and `find` (`:641`). - `ctssc/ctsscProblemGenerator.h:916` - `_t2p_map`; only `clear` (`:678`) and `find` (`:916`). No insert exists anywhere, so `getProblem()` always returns NULL - effectively dead as well. - `ctscto/ctoFlow.cc:14442,14510` - `MPWvioMap`; only `find` (`:14442,14510`), `insert` (`:14529`), `clear` (`:14476`). - `ctssc/ctsscConflictChecker.cc:228,244` - `_netmap`; only `find` and `insert` across all of `:197,198,212,228,244,280,285,311,316,380,385,408,413`.  1.3 sites (9): - `ctscto/dcd/ctoDcdFix.cc:470` - `terms` inside `_doneClock2Terms`; `insert(...).second` as a processed-guard. - `ctscto/ctosc/ctoscLevelFlow.h:134`, `ctoscLevelFlow.cc:325,395` - `seedMap`; `addNewSeed` (`ctoscLevelFlow.cc:328-331`) does `find` then `insert`, and the real ordering lives in `std::deque<seedOpt>& queueWork` via `push_front`. - `ctscto/ctosc/ctomt/ctomtAreaLevelFlow.cc:186` - same `seedMap` pattern, single `addNewSeed` call. - `ctscto/ctosc/ctomt/ctomtClone.cc:1711` - `compatibleSet`; built from `leqVecFromInst` purely so `:1716` can do an `O(1) find` in an erase-remove filter over a vector. - `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:503` - `_roots`; only `clear` (`:627`), `find`/`insert` (`:648,649`), `find` (`:687`, and `isClockRoot` at `.h:436`). - `ctscto/ctosc/ctomt/ctomtBufferAddDelay.cc:640` - `originalLoadSet`; `find` at `:656,662` and `.size()` at `:720`. - `ctssc/ctsscUskewLimit.cc:2551` - `sinks`, `sinksVioPre`, `sinksVioPost`; inserted at `:2559,2709,2715` and consumed only via `.size()` in the summary prints at `:2751-2753`.  Sample sites: `ctscto/ctosc/ctoscLevelFlow.cc:395`, `ctssc/ctsscProblemGenerator.h:916`, `ctssc/ctsscUskewLimit.cc:2551`. |
| 21 | Iterated, but the consumer is order-insensitive (distinct-target writes, min/max, existential, count, or destructor delete) | These containers genuinely are iterated in address/hash order, but I traced the loop body and the effect does not depend on the order.  - `ctscto/totalskew/ctoAbsTree.h:1122,1123` (2) - `_nodeData` / `_edgeData`; the only iteration is `~ctoAbsTree()` (`ctoAbsTree.cc:8078,8081`) doing `delete data`. Nothing else in the run observes it. Other uses are `emplace`/`find`/`erase` (`:8123,8141,8159-8164,8181-8186`). - `ctscto/totalskew/ctoAbsTreeTest.h:43`, `ctoAbsTreeTest.cc:311,335` (3) - `varDelayMap`. Iterated at `ctoAbsTreeTest.cc:319`, but each key is a distinct `ctoAbsVariable*` receiving its own `setSolution(getSolution() + it.second)`; `std::map::emplace` guarantees unique keys, so no two iterations touch the same object. Additionally the whole `ctoAbsTreeTester` path is guarded by `if (not tmClkAbsTreeConflictTest.ok_to_print()) return;` (`ctoAbsTreeTest.cc:37`), i.e. debug-only. - `ctscto/ctoFlow.cc:5804,5842` (2) - `allCkgSet`. Iterated at `:5842-5846`, but the body is `if (canInsertSet.find(*cgIter) == canInsertSet.end()) return true;` - a pure existential over clock groups. Same result in any order. `canInsertSet` is `find`-only. - `ctssc/ctsXformProblems.h:926` (1) - `_tMsgCount`. Iterated at `ctsXformProblems.cc:330-333` doing `tm->set_count(tm->get_count() + it->second)`. One distinct `tMessage*` per key, integer addition. - `ctscto/ctoLocalSkew.cc:596,617` (2) - `bagSet`. Iterated at `:617-620` doing `(*it)->setScheduled(true)` - idempotent, one distinct bag per element. The BFS `break` at `:604` is driven by the `std::queue`, not by `bagSet`, so the set's *contents* at break time are deterministic. - `ctssc/lazytns/ctsLazyModelMtUtil.h:78,139` and `ctssc/lazytns/ctsLazyModel.cc:2306,2310,2422,2426` (6) - `tracedPaths` (`std::map<costEp*, lazyTns::clockIdSlack>`) and `pathMap2` (`std::map<costEp*, std::map<nodeClockId, ...>>`). Traced the full chain: (a) the inner accumulation is `ep->getRange()[7] = std::min(ep->getRange()[7], slack)` (`ctsLazyModel.cc:2337-2341`), a min - order-free; (b) `pathMap1[ep].emplace_back(...)` / `pathMap2[ep].emplace(...)` append at most once per ep per job, so the per-ep sequence order is set by the deterministic `jobsPerMode` map and job vector, not by `tracedPaths`; (c) the vector overload of `updateTracedPathBatch` copies into a `std::map<nodeClockId, ...>` before use, with an explicit comment that this is to make it identical to the map path (`ctsLazyCostEp.cc:462-471`); (d) `updateTracedPathBatch(map)` (`ctsLazyCostEp.cc:478-511`) only mutates `this` (`_sleepTPaths`, `_allTPaths`, `_topTPaths`, `_range`) and issues read-only `mdl->findDeltaCmt` queries, so processing eps in any order gives the same per-ep state. Also noted: `costEpHash` (`ctsLazyCostEp.h:363-367`) hashes `c->getId()`, not the address, and `costEpCompare` (`ctsLazyCostEp.h:369`) exists as a ready-made stable comparator if these are ever hardened. - `ctscto/ctosc/ctomt/ctomtBufferAddDelay.cc:382,560,609` and `ctomtBuffer.h:326,327` (5) - `loadDelayTargetMap`. The outer container is `std::vector<std::pair<sclkCornerType, unordered_map<ndmTerm*, ...>>>` - a vector, so its order is deterministic. The inner `unordered_map<ndmTerm*, ...>` is never range-iterated: `:526` does `loadTargetMap[load]` while walking the `loadsToAddDelay` vector, and `:690` does `loadTargetMap.find(load)` while walking the `expandedSet` vector. The reductions are `replaceValueIfLesser` / `replaceValueIfGreater` (`:528-529`) and a strict `>` best-partition pick over a vector index (`:694-706`).  Sample sites: `ctscto/ctoFlow.cc:5842`, `ctssc/lazytns/ctsLazyModel.cc:2306`, `ctscto/ctosc/ctomt/ctomtBufferAddDelay.cc:560`. |


### Pattern 1.2,1.3,1.4

| Count | Bucket | Why dismissed |
|---:|---|---|
| 19 | Lookup-only value caches keyed by pointer - find / at / operator[] / clear, no iteration | Same disposition as the dedup bucket, but these carry payloads rather than just membership. Every access is by key.  - `size2pod` (7 sites): `ctssc/ctsscGlobal.cc:5846,5859,5870,5912,5936,5958` and `ctssc/ctsscGlobal.h:421`. `std::map<ndmModule*, float>` used only via `find` (`:5859,5870,5936,5958`) and `operator[]` (`:5960`). The ordered output is built into `std::multimap<float, ndmModule*> leqs` (`:5858`) keyed by power delta and drained at `:5875-5878`; ties preserve insertion order, and insertion follows the `sizes` vector. - `validModuleSet` (6 sites): `ctscto/ctosc/ctomt/ctomtBuffer.h:287`, `ctomtBuffer.cc:2365,2590,3150`, `ctssc/ctsBuffer.h:638`, `ctsBuffer.cc:2832`. Traced into `ctsCharacterizer::getPrunnedRepeaters` (`ctsutil/ctsCharacterizer.cc:1153`) and `ctsCharDataForContext::getPrunnedDefault` (`ctsutil/ctsCharacterizer.cc:733`); the set appears exactly once, at `:746`, as a `find` filter while iterating `_charData`. The result vector is then `std::stable_sort`ed by driving strength at `:779`. - `ctscto/totalskew/ctoAbsTree.h:816,910` (2 sites): `termSccDelayUmapType` (`_termElrfArrivalMap`, `_termElrfPathDelayMap`, `_termElrfBpDelayMap`) and `termLevelMap` (`_termTargetLevelMap`). The `ndmTerm*` level is only `find`/`count`/`operator[]`/`emplace` (`ctoAbsTree.cc:8344,9507,10591,10598-10600,10623`). The inner maps that *are* iterated (`ctoAbsTree.cc:10596,10633`) are `sccElrfValUmapType`, keyed by the value type `sclkCornerType`, and the outer driving loops walk `_intTermSclkSetVec` / `_sinkTermSclkSetVec`. - `ctscto/ctosc/ctomt/gls/ctomtGlsParallelBufPlans.cc:66,67` (2 sites): `driverInfoMap` and `planGenIndex`. Built by `operator[]` while iterating `evalProblems` / `planGenProblems` (both index-based vectors, `:73-88` and `:95-99`), consumed only by `find` (`:136,146,163`). - `ctscto/ctosc/ctoscFilter.h:334,335` (2 sites): the `tuple_hash` functor and its one container `std::unordered_map<keyInstModule, T, tuple_hash> _mapModuleCost` (`ctoscFilter.h:340`). Every use is `find`, `operator[]` or `clear` (`ctoscFilter.cc:761,1071,1093,1094,1107,1111,1112,1137,1165,1166,1200,1204,1205` and `ctoscFilter.h:265`). It is never iterated. The best-module selection runs through `std::priority_queue<keyInstModule, std::vector<...>, std::function<...>> _queueModulesBest` (`ctoscFilter.h:243-245`), which is fed by explicit pushes in program order; its comparator `compareModule` (`ctoscFilter.h:214`) only *reads* the cache by key. `updateBestModule` (`ctoscFilter.cc:1257`) likewise takes the key as an argument.  Sample sites: `ctssc/ctsscGlobal.cc:5846`, `ctssc/ctsBuffer.cc:2832`, `ctscto/ctosc/ctoscFilter.h:334`. |


### Pattern 1.2/1.3

| Count | Bucket | Why dismissed |
|---:|---|---|
| 69 | latent-only: lookup / membership only - find(), operator[], insert(), emplace(), erase(), size(), empty(); the container is never iterated anywhere in the tree | Real pointer-keyed containers with no comparator/hash, but the order never becomes observable: no `begin()`/`end()`/range-for/`std::copy` over them anywhere in the tree. They are caches, dedup guards, DFS visited-sets and sort-comparator side tables. Representative verifications:  - **Sort side-tables (`find()` only, plus a deterministic tie-break in the comparator)**: `ips/ipsManager.cc:176-191` `cmpDelay` and `icg/ctsICGMergeHelper.cc:48-62` `cmpDistance` and `icg/ctsICGCloningHelper.cc:813-826` `cmpCriticality` all only `find()` in the map. Better still, `cmpDistance` (`icg/ctsICGMergeHelper.cc:58-60`) and `cmpCriticality` (`icg/ctsICGCloningHelper.cc:822-824`) break ties on `getId()` / `getFirstDriverTerm()->getId()`, and the three `cmpDelay` call sites (`ips/ipsManager.cc:282`, `:388`, `:436`) use `std::stable_sort` over vectors whose contents come from `std::set<ndmTerm *, ndmObjectHandleNS::compareObjPtr>` (`ips/ipsManager.cc:300`, `:323-324`, `:352`). These paths are deterministic end to end. - **`ips/ipsGlobalTiming.h` (14 hits, the biggest single file)**: `_adjMap`, `_parentMap`, `_nodeDataMap`, `_cloneIcgMap`, `_cloneDriverMap`, `_icgClocks`. The only iteration of any of them is the destructor delete loop at `ips/ipsGlobalTiming.cc:261`. The accessors `getAdjMap()` (`:151`), `getNodeDataMap()` (`:156`), `getICGClocks()` (`:158`), `getEnableFanouts()` (`:159`), `getICGEnableDriver()` (`:160`) have **no caller** except `getNodeDataMap()`, which is passed to `ipsSplitter::shouldSplit()` (`ips/ipsSplitter.cc:829` -> `:89`) where it is used for lookup only. `getAdjSet()` is called once, at `ips/ipsSplitter.cc:261`, and the returned set is only `insert()`ed into (`ips/ipsSplitter.cc:346`) and `.size()`-printed (`ips/ipsGlobalTiming.cc:331-334`). - **`ips/ipsManager.cc:72` `_subIcgDelayMap`**: static member, written at `:2396`, `.size()`-printed at `:2440`, `clear()`ed at `:1726`. Never read back - the code comment even says "Should be removed!!". - **DFS visited-sets**: `ctssch/ctsMultiClockAnalysis.cc:733/933/2030` and `ctssch/ctsClockTree.cc:554` are `find()`/`insert()` guards; the traversal order comes from `ctsDfsIterator`/`ctsTreeNodeNgbr`, not from the set. - **Dedup guards feeding an order-preserving vector**: `ctssch/ctsSchCts.cc:3549` `driverSet` and `ctssch/ctsSch.cc:380` `driverSet` gate pushes into `netlinkDrivers` / drive per-net work, but the output order comes from the `driverTerms` **vector** (`ctssch/ctsSchCts.cc:3557-3558`, `ctssch/ctsSch.cc:396-397`). - **Membership filters**: `ctsutil/ctsCharacterizer.cc:746` (`validModuleSet->find`), `cts/ctsManager.cc:2874` (`newCellSet.find`, reached from `:2925`), `ctsutil/ctsAddDelay.cc:2350` (`legalRefModules.find`), `ctsrpt/ctsGetClockTreePins.cc:1125/1171` (`_stopNetsSet->find`), `ctsrpt/ctsGetClockTreePins.cc:1957` (`_drivers.find`, so `msWrapperBase.h:55`'s `drivers` out-param is never iterated), `ctsutil/ctsPortPunchAnalyzer.cc:1670/1678` (`_loads`/`_sideLoads`.find), `ctsmisc/ctsCheck.cc:3925/3927` (`terms.find`/`emplace`), `ctsmisc/ctsCheck.cc:185/189` (`ignoredLayers.find`), `cts/ctsManager.cc:3884` (`_sinksLevelTable.find`). - **`ctsmisc/ctsAutoBalancePoint.h:168` `_nodes`**: `getNodes()` is called at `ctsmisc/ctsAutoBalancePoint.cc:1522`, `:1797`, `:1867` and used only for `insert()` (`:1527`) and `find()` (`:1805`, `:1874`). - **`ctsutil/ctsDelayLookup.cc:943` `m2`**: only `find()` (`:952`) and `operator[]` (`:957`); the map that *is* iterated on the adjacent line (`m1`, `:939`) carries `ctsModuleCompare`. - **`ctsutil/ctsTestCmds.cc:10092/10107` `_costs`**: `find()`/`operator[]` cache inside a sort comparator, and the file is the `cts_test` command harness rather than a flow path - LOW by location as well as by use. |
| 38 | DFS/BFS `visited` and `visitedSeeds` guards - membership-only | Largest single bucket. Every one of these is a pointer-keyed `std::set`/`std::unordered_set`/`unordered_map` used purely as a cycle/revisit guard in a graph traversal: the only operations are `insert`, `emplace`, `find`, `count` and `clear`, and in the common idiom the insert's `.second` is the branch condition (e.g. `if (!visited.insert(term).second) return;` at `ccd/ctsccd/fmax/fmaxClockGraph.cc:297` and `ccd/skewopt/soClockGraph.cc:234`). None is iterated, so the address-dependent order is never observed. Traversal *output* order in these functions is set by the caller's deterministic driver - a `std::vector`, a `grGraph::nodeIterator`, or a `std::map<..., ndmObjPtrCmpType>` - not by the guard. Two near-misses I checked and dismissed explicitly: `ccd/ccdui/ccduiReport.cc:1260` and `ccd/ctsccd/cgbased/ccdptProblemGenerator.cc:2177` each have a same-named container that *is* iterated elsewhere in the file (`ccd/ccdui/ccduiReport.cc:4416`, `ccd/ctsccd/cgbased/ccdptProblemGenerator.cc:3317`), but those are different variables - a `std::set<grNodeId>` (value key) declared at `ccd/ccdui/ccduiReport.cc:4412` and a `std::list<ccdptProblemSeed*>` declared at `ccd/ctsccd/cgbased/ccdptProblemGenerator.cc:3290`. Also includes `fmaxProblemGenerator.h:105` `termSet`, a dedup guard whose output vector is appended in input order. Samples: `ccd/ccdui/ccduiReport.cc:1260`, `ccd/ccdui/ccduiReport.cc:3290`, `ccd/ccdui/ccduiReport.cc:3499`. |
| 29 | Problem-generator power/size lookup tables (`size2pod`, `_leqMap`, `_initialPower`, `old_md`, `capAllowance`) - keyed lookup only | Four near-identical copies of the CCD problem generator (`power/`, `voltagedrop/`, `drc/`, `awp/`) each carry the same pointer-keyed lookup tables, which is why this bucket is large. All are memo tables read by key and never iterated. `std::map<ndmModule*, float> size2pod` (`ccd/ctsccd/power/ccdpwProblemGenerator.cc:1367`, `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.cc:1603`) is only `find`-ed or written via `operator[]` (`ccd/ctsccd/power/ccdpwProblemGenerator.cc:1382`, `:1395`, `:1442`, `:1463`, `:1518`); the power values it feeds are per-libcell, so no accumulation crosses keys. `_leqMap` (`ccd/ctsccd/power/ccdpwProblemGenerator.h:365`, `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:354`) is `find`/`operator[]`/`clear` only - the equivalent-libcell *vectors* it stores carry their own order. `_initialPower` accessors `addInitialPower`/`getInitialPower` (`ccd/ctsccd/power/ccdpwProblemGenerator.h:171`, `:174`) are insert/find, and the per-instance deltas consumed at `ccd/ctsccd/power/ccdpwFilter.cc:639-644` are indexed by `getSeedInsts()[0]`, not by traversal. `old_md` (`ccd/ctsccd/power/ccdpwResultIntegrator.cc:546`) and `capAllowance` (`ccd/ctsccd/fmax/fmaxMooCreator.cc:2590`, find + `it->second--`) are the same shape. Header rows are declarations and signatures. The two commented-out rows and the two dead iteration sites in this family are bucketed separately below. Samples: `ccd/ctsccd/power/ccdpwProblemGenerator.cc:1367`, `ccd/ctsccd/power/ccdpwProblemGenerator.cc:1382`, `ccd/ctsccd/power/ccdpwProblemGenerator.cc:1395`. |
| 15 | fmax budget/seed and dot-export membership sets - find/size/count only | `std::set<fmaxProblemSeed*>` returned by `getZeroBudgetDebankSeeds` (`ccd/ctsccd/fmax/fmaxBudgetModel.cc:1483`, `:1526`) is consumed only as `filteredSeeds.find(pSeed) != filteredSeeds.end()` at `ccd/ctsccd/fmax/fmaxBudgetModelPrivate.cc:159`; the `zeroBudgetSeeds.push_back(pSeed)` that follows walks `newXps[i]` by index (`ccd/ctsccd/fmax/fmaxBudgetModelPrivate.cc:155`), so the seed-clearing order is problem-vector order, not address order - worth stating because every other `zeroBudgetSeeds` in the module is already a `std::vector`. `_badSeeds` (`ccd/ctsccd/fmax/fmaxBudgetModel.h:288`) is find/insert only across its five users (`ccd/ctsccd/fmax/fmaxProblemGenerator.cc:814`, `:931`, `:2791`; `ccd/ctsccd/fmax/fmaxProblemGeneratorPower.cc:228`, `:353`). `_batch2Drivers` (`ccd/ctsccd/fmax/fmaxBudgetModel.h:309`) is used via `empty()`, `size()`, `find()`, `clear()` only (`ccd/ctsccd/fmax/fmaxProblemGeneratorTrial.cc:151`, `:152`, `:272`; `ccd/ctsccd/fmax/fmaxFlow.cc:298`, `:373`). `originalSet` (`ccd/ctsccd/fmax/fmaxFlow.cc:1137`) *is* iterated at `ccd/ctsccd/fmax/fmaxFlow.cc:1156`, but only to increment a counter, and a count is permutation-invariant. The `seedDrivers` sets in the `.dot` exporters are `find`-only at `ccd/ctsccd/fmax/fmaxBudgetModelPrivate.cc:334`, with the dump order coming from `std::map<ndmObject*, std::set<grNodeId>, ndmObjPtrCmpType> obj2nodesMap` (`ccd/ctsccd/fmax/fmaxBudgetModel.h:263`) - already stable. `criticalVariables` (`ccd/ctsccd/fmax/fmaxProblemSeed.cc:2611`), `wnsMap` (`ccd/ctsccd/fmax/fmaxProblemGeneratorWns.cc:132`) and `allLeqs` (`ccd/ctsccd/fmax/fmaxSize.cc:88`) are find/insert/erase only. Samples: `ccd/ctsccd/fmax/fmaxBudgetModel.cc:1480`, `ccd/ctsccd/fmax/fmaxBudgetModel.cc:1483`, `ccd/ctsccd/fmax/fmaxBudgetModel.h:184`. |


### Pattern 1.2/1.3/1.4

| Count | Bucket | Why dismissed |
|---:|---|---|
| 25 | Misc single-site lookup tables, memoisation caches and pointer-hash functors | Tail of unrelated one-off containers, each resolved individually. `criticalSinks` (`ccd/ctsccd/ccdBuffer.cc:3593`) insert+find; `clusters` (`ccd/skewopt/soMacroBank.cc:537`) consumed only as `clusters.size()` (`ccd/skewopt/soMacroBank.cc:576`). `_nodeBBoxMap` (`ccd/ctsccd/ccdFindReparentDrivers.h:35`) is filled by a visitor and read by `find` (`ccd/ctsccd/ccdFindReparentDrivers.cc:84`). `_pos_signatures`/`_neg_signatures` (`ccd/ctsccd/ccdMergeIcg.h:147-148`) are ICG signature tables accessed only via `find` and `operator[]` (`ccd/ctsccd/ccdMergeIcg.cc:735`, `:740`, `:769`, `:774`). `eps` (`ccd/skewopt/soSolverAnalyzer.cc:1690`) is a dedup guard; the output `_info._eps` is appended in `refCheckNodes[i]` vector order (`ccd/skewopt/soSolverAnalyzer.cc:1691-1698`). `soPredictiveCcd`'s per-scenario slack maps (`ccd/skewopt/soPredictiveCcd.cc:524`, `ccd/skewopt/soPredictiveCcd.h:137`) sit inside a `std::vector`, are filled by iterating `_allEps` with `replaceValueIfLesser` (a min - order-safe, `ccd/skewopt/soPredictiveCcd.cc:562-568`), and where the inner map *is* iterated (`ccd/skewopt/soPredictiveCcd.cc:587`) the sink is a per-key write `_endpointDelayPotential.at(scenario)[ep] = delayPotential` (`ccd/skewopt/soPredictiveCcd.cc:618`) - permutation-invariant. `inst2ck` (`ccd/util/ccdUtil.cc:2632`) is subtle and worth recording: it is a `std::multimap<ndmInst*, const ndmTerm*>` with a default comparator, walked forward from `find(*it)` until the key changes (`ccd/util/ccdUtil.cc:2650-2657`). Address order decides *where* each key's run sits in the tree, but `multimap::insert` appends at the equal-range upper bound, so the run's internal order is insertion order - here the deterministic `grGraph::nodeIterator` - and the outer loop iterates `std::set<ndmInst*, ndmObjectHandleNS::compareObjPtr> latches` (`ccd/util/ccdUtil.cc:2634`, `:2649`), already stable. So no address dependence reaches `latchSinks`. The four pattern-1.4 functors (`ccd/skewopt/soLogicCone.h:375`, `:400`, `:401`, `:402`) hash pointers into `NodeOfTermCache` and `DeltaCapCache`, `tbb::enumerable_thread_specific` memoisation caches whose only operations are `.local()` and `.clear()` (`ccd/skewopt/soLogicCone.h:450`, `:453`, `:456`; `ccd/skewopt/soLogicCone.cc:850-852`); they are never iterated and each value is a pure function of its key, so bucket order cannot change a result. `lcPwrMap` (`ccd/skewopt/soLogicCone.cc:1216`, `:1498`, `:2216`; `ccd/skewopt/soLogicCone.h:343`) is `find`-only (`ccd/skewopt/soLogicCone.cc:2221`). Samples: `ccd/ctsccd/ccdBuffer.cc:3593`, `ccd/ctsccd/ccdFindReparentDrivers.cc:24`, `ccd/ctsccd/ccdFindReparentDrivers.cc:28`. |


### Pattern 1.2/1.4

| Count | Bucket | Why dismissed |
|---:|---|---|
| 12 | latent-only: the container IS iterated, but the loop body is order-insensitive - destructor/cleanup delete, existential any-match, or a set-valued filter | Iteration exists, but the result is provably invariant under permutation:  - **Cleanup delete loops** (final state = everything freed, no cross-element interaction): `ips/ipsGlobalTiming.cc:261-264` (`~ipsGlobalTiming`, `delete data`), `ctsutil/ctsLocalSkew.cc:270-282` (`deleteAllNodes`; the `uniqueNodes` set exists purely to de-duplicate before `delete`), `ctsutil/ctsLayerOpt.cc:400-402` (`delete rule` over `ctsRtRules`; the companion `origRtRules` at `:270` is lookup-only at `:372`). - **Existential quantifier - any-match short-circuit** (the *set* of matches, not the order, decides the answer): `cts/ctsManager.cc:3602-3609` returns `true` if **any** reference module `isRefModuleInverter(ref)`; `ctssch/ctsIntSkewGroupBal.cc:632-638` (`isSclkInProcessedGroup`) returns `true` if **any** processed group `isAtClockList(sclk)`. All other `_processedGroups` uses are `find()`/`insert()`/`size()` (`ctssch/ctsIntSkewGroupBal.cc:335`, `:394`, `:482`, `:485`, `:652`). - **Set-valued filter** (collects every element satisfying a predicate into another container, no first-match, no counter): `ctsmisc/ctsRemove.cc:560-563` scans `_inverterSet` for all `inv->getRefInst() == refInst` into `instSetType insts_to_be_removed` (`ctsmisc/ctsRemove.cc:559`, which is `std::set<ndmInst*, ndmObjPtrCmpType>`) and then erases them at `:567-569`. The membership uses at `:375`, `:448`, `:483`, `:812`, `:819`, `:850`, `:881` are all `find`/`insert`/`erase`. - **Per-key independent writes**: `ctsinterf/ctsGuiQorInterf.cc:34-56` iterates `_args._skewGroups` but the work is `modes.insert(mode).second` de-duplication followed by `_modeClocksMap[mode].push_back(clock)` where the clocks come from `mode.getClockIter()` (`:46-53`) - so the same mode yields the same clock list no matter which skew group reached it first, and `_modeClocksMap` is keyed by the value type `cstrMode`. - **`ctscstr/ctscstrDesign.h:92`** - the pattern-1.4 pointer-hash functor. See the dedicated verdict in `notes_md`; the only iteration of the container it serves is the destructor detach+delete loop at `ctscstr/ctscstrDesign.cc:234-241`. |


### Pattern 1.3 — std::unordered_set / unordered_map with pointer key, default hash

| Count | Bucket | Why dismissed |
|---:|---|---|
| 10 | skewopt shared pointer-keyed typedefs (`termToSinkMapType`, `termToGateMapType`, `termToPortMapType`, `termToOffsetType`, `sinkToSinkVecUmapType`) - find-only across all users | These are the classic 'one header declares it, twenty sites use it' shape the grouping instruction warns about, so I resolved every consumer rather than each declaration. The typedefs are declared three times over (`ccd/skewopt/soDesign.h:70-74`, `ccd/skewopt/soClockGateOpt.h:32-34`, `ccd/skewopt/soSink.h:51-52`) and are all `std::unordered_map<ndmTerm*, ...>` with the default hash. Across every use in `ccd/skewopt/` the access is a keyed `find()`: `ccd/skewopt/soDesign.cc:3632`, `:3637`, `:3642`, `:7038`, `:7043`, `:8412`, `:8423`; `ccd/skewopt/soSolverUpdater.cc:2864`, `:3110`, `:4365`, `:4369`, `:4373`; `ccd/skewopt/soClockGraph.cc:1598`, `:1614`; `ccd/skewopt/soSink.cc:624`. None is iterated. `termToOffsetType` deserved extra scrutiny since it feeds clock-offset reconstruction: in `soClockGraph::reconstructArcOffsets` the map is only indexed as `termToOffsetArcMap[term]` inside loops driven by `getNumArcs()` index order (`ccd/skewopt/soClockGraph.cc:290-296`, `:301-312`) and by `termsToProcess`, a `std::iota` vector sorted by term depth (`ccd/skewopt/soClockGraph.cc:467-471`) - both deterministic. While there I also checked the first-parent pick `std::begin(parents)->second->getTerm()` (`ccd/skewopt/soClockGraph.cc:501`), which would have been a real HIGH; `termInfoMapType` is `std::map<ndmTerm*, soCtsTermInfo*, ndmObjPtrCmpType>` (`ccd/skewopt/soClockGraph.h:44`), i.e. already stable, so that selection is deterministic. Samples: `ccd/skewopt/soDesign.h:70`, `ccd/skewopt/soDesign.h:71`, `ccd/skewopt/soDesign.h:72`. |
| 8 | fmaxClockGraph `seedMap` - emplace/find only | `std::unordered_map<ndmTerm*, fmaxProblemSeed*> seedMap` (`ccd/ctsccd/fmax/fmaxClockGraph.cc:97`) is a term-to-seed side table threaded through clock-graph construction. It is populated by `seedMap.emplace(term, seed)` at `ccd/ctsccd/fmax/fmaxClockGraph.cc:101` while walking a deterministic seed list, and read only by key: `seedMap.find(term)` in `addSeedToTermInfo` (`ccd/ctsccd/fmax/fmaxClockGraph.cc:195`) and in `shouldAddToGraph` (`ccd/ctsccd/fmax/fmaxClockGraph.cc:214`). It is never iterated, so the graph shape does not depend on bucket order. The clock-graph build order itself comes from `buildClockGraphRecursive` descending through `termInfoMapType`, which is `std::map<ndmTerm*, fmaxTermInfo*, ndmObjPtrCmpType>` (`ccd/ctsccd/fmax/fmaxClockGraph.h:37`) - a stable comparator. Remaining rows in this bucket are the matching function signatures in the `.cc` and `.h`. Samples: `ccd/ctsccd/fmax/fmaxClockGraph.cc:97`, `ccd/ctsccd/fmax/fmaxClockGraph.cc:150`, `ccd/ctsccd/fmax/fmaxClockGraph.cc:192`. |
| 6 | soSolverUpdater solver-side index maps and `fixedTerms` - size/find/at only | Traced because assigning solver variable indices from a hash order would be a clear HIGH. It is not what happens. `std::unordered_map<ndmTerm*, unsigned int> termIndexMap` (`ccd/skewopt/soSolverUpdater.cc:3280`) is *written* as `termIndexMap[term] = i` where `i` is the arc index from a counted loop (`ccd/skewopt/soSolverUpdater.cc:3345`) and *read* only as `termIndexMap.at(term)` (`ccd/skewopt/soSolverUpdater.cc:3445`) - the index values come from the graph, not from iteration. `std::unordered_set<ndmTerm*> drivers` (`ccd/skewopt/soSolverUpdater.cc:3323`) is consumed only as `solver->setNumDrivers(drivers.size())` (`ccd/skewopt/soSolverUpdater.cc:3392`), a cardinality. `fixedTerms` (`ccd/skewopt/soSolverUpdater.cc:2659`, `:3915`) is insert-only inside `setFixedVars` (`ccd/skewopt/soSolverUpdater.cc:4055-4300`) - the variable fixing itself is done by `solver->setVariableFixedByUser(index)` using indices, and the set is then passed to `msCtsNS::deriveOffsetLimits` (`ccd/skewopt/soSolverUpdater.cc:2664`, `:3920`), which forwards it to `msDataModel::backPropagateCUSLimit` (`mscts/mscore/msInterfApi.cc:721`), where the only use is `ignoredTerms.find(clkInputTerm)` (`mscts/mscore/msDataModel.cc:11496`, `:11507`) - membership. Notably the same function declares its *iterated* maps with `ndmObjPtrCmpType` (`ccd/skewopt/soSolverUpdater.cc:3272-3277`), showing the authors drew this line deliberately. Samples: `ccd/skewopt/soSolverUpdater.cc:2659`, `ccd/skewopt/soSolverUpdater.cc:3280`, `ccd/skewopt/soSolverUpdater.cc:3323`. |
| 4 | Order canonicalized by an explicit sort before any consumer | Four sites materialise a pointer-keyed hash container into a vector and then canonicalize it, so no consumer ever sees hash order. `gatherAllSizableCells()` copies `std::unordered_set<ndmInst*> allCells` (`ccd/skewopt/soLogicCone.cc:618`) into a vector and immediately sorts it - with the comment *"Copy to a vector and sort to avoid ND"* - `std::sort(sizableCells.begin(), sizableCells.end(), ndmObjPtrCmpType{});` (`ccd/skewopt/soLogicCone.cc:638-640`); the later `remove_if` prune (`ccd/skewopt/soLogicCone.cc:642-673`) preserves that order. `buildLutsForGates()` does the same for `libCellsSet` (`ccd/skewopt/soLogicCone.cc:2235`): `std::sort(libCellsVec.begin(), libCellsVec.end(), ndmObjPtrCmpType());` at `ccd/skewopt/soLogicCone.cc:2244-2245` before `soDelayLut` is constructed. `ccdscGlobal.cc:3443` merges optimization libcells using `std::unordered_set<ndmModule*> allLeqs` purely for `find` and then calls `ctsUtils::sortModulesByName(leqVec)` under the comment *"Merge from different sources can perturb order"* (`ccd/ctsccd/ccdscGlobal.cc:3449-3451`). `soDataPowerOptimizer::_potentials` (`ccd/skewopt/soDataPowerOptimizer.h:99`) is iterated at `ccd/skewopt/soDataPowerOptimizer.cc:355`, but only the `pot.reg` *values* are collected and they are then sorted by value (`std::sort(pots.begin(), pots.end(), std::greater<float>{})`, `ccd/skewopt/soDataPowerOptimizer.cc:363`) before `computeKneePoints(pots)` and before the `std::accumulate` at `ccd/skewopt/soDataPowerOptimizer.cc:374` - so even the float accumulation runs over a canonical sequence. Equal float values are indistinguishable, so the sort is a total order for this purpose. Samples: `ccd/ctsccd/ccdscGlobal.cc:3443`, `ccd/skewopt/soLogicCone.cc:618`, `ccd/skewopt/soLogicCone.cc:2235`. |
| 1 | dead/unused: the only iteration is excluded by a real build macro (#ifdef DEBUG_ctsPortPunchAnalyzer) | `newDriverHiers` is a genuine `std::unordered_map<ndmHier*, ndmTerm*>` with the default address hash (`ctsutil/ctsPortPunchAnalyzer.cc:1477`), and it *is* iterated - at `ctsutil/ctsPortPunchAnalyzer.cc:1502`. But that loop sits inside the `#ifdef DEBUG_ctsPortPunchAnalyzer` block that opens at `ctsutil/ctsPortPunchAnalyzer.cc:1494` and closes at `:1506`, and its body is a `ctsLog::printf` trace. `DEBUG_ctsPortPunchAnalyzer` is not defined anywhere in the tree. This is the one dismissal in my slice that rests on real preprocessor exclusion rather than on a `purecov`/Coverity comment.  In the shipped configuration the map's only remaining use is `find()` at `ctsutil/ctsPortPunchAnalyzer.cc:1621-1622`, i.e. lookup-only. If anyone ever defines that macro, the printed trace order becomes ND - a LOW, log-only issue. |


### Pattern 1.3/3.3

| Count | Bucket | Why dismissed |
|---:|---|---|
| 3 | Already using a project deterministic hash idiom | `ccd/ctsccd/fmax/fmaxOnRouteBufferLowEffort.cc:432` and `:436` iterate `targetedSideLoadCPObjs` and `targetedCPObjs`, but both are declared `std::unordered_set<ndmObject*, dosContainer::keyHash>` (`ccd/ctsccd/fmax/fmaxOnRouteBufferLowEffort.cc:417`, `:452`; also the signatures at `ccd/ctsccd/fmax/fmaxOnRouteBuffer.h:147` and `ccd/ctsccd/fmax/fmaxMasterXform.h:217`), i.e. they already pass the project's deterministic hash functor; the scanner matched the bare `for (auto& it : ...)` without resolving the declaration. Independently, the functional consumer `doPseudoLinearRegression` only does `targetedCPObjs.find(obj)` (`ccd/ctsccd/fmax/fmaxMasterXformLowEffort.cc:230`), so these loops are print-only anyway. `ccd/skewopt/soClockGateOpt.cc:1039` iterates `fOSinks`, declared `std::unordered_set<soSink*, soSinkHash>` (`ccd/skewopt/soClockGateOpt.cc:1034`, returned by `ccd/skewopt/soClockGateOpt.h:135`), and `soSinkHash` hashes a stable ordinal, not an address: `return sink ? std::hash<unsigned long>{}((unsigned long)(sink->getIndex()+1)) : 0;` (`ccd/skewopt/soClockGateOpt.h:78-82`). Its consumer is order-insensitive regardless - the `sinkTerms` vector feeds `infra.getTermsBBox(sinkTerms, bB)` (`ccd/skewopt/soClockGateOpt.cc:1041`), and a bounding box is a min/max reduction. Caveat: `dosContainer::keyHash` is only forward-declared inside this snapshot (`ccd/ctsccd/fmax/fmaxOnRouteBuffer.h:47`, `ccd/skewopt/soClockGateOpt.cc` region), so I took its determinism from the project idiom list rather than reading its body. Samples: `ccd/ctsccd/fmax/fmaxOnRouteBufferLowEffort.cc:432`, `ccd/ctsccd/fmax/fmaxOnRouteBufferLowEffort.cc:436`, `ccd/skewopt/soClockGateOpt.cc:1039`. |


### Pattern 1.5 — Random ops without deterministic seed

| Count | Bucket | Why dismissed |
|---:|---|---|
| 11 | rand() in ctsui/*RandomTest.cc — deliberate randomized test commands, seeded from stable IDs | `ctsui/ctsuiscRandomTest.cc` and `ctsui/ctsuiCtoRandomTest.cc` are randomized test drivers whose whole purpose is to perturb the design. They are also already deterministic by intent: `srand(0)` at `ctsuiCtoRandomTest.cc:140`, and `srand(drvTerm->getIdLong())` at `:368`, `:373`, `:378`, with comments reading `// deterministically random`. `ctsuiscRandomTest.cc:195` and `:431` seed from `getCkt()->getSeedTerms()[0]->getId()`. Test infrastructure, correctly seeded; not product ND. |
| 11 | rand() in ctsutil/test/ctsGfxDrawTest.cc — test harness, and unseeded rand() is deterministic anyway | Eleven `rand()` draws generate random rectangles and colours in a graphics-canvas test under `ctsutil/test/`. Two independent reasons to dismiss: it is a test harness, and the file never calls `srand`, so the C library uses its fixed default seed of 1 and the sequence is identical on every run. An *unseeded* `rand()` is reproducible; only a time- or PID-seeded one is not. |
| 1 | boost::random::mt19937 in mscts/mstap/msClustering.h — default-constructed, so fixed seed 5489 | `_rand` is never explicitly seeded, which is what the scanner flagged. But default construction of `boost::random::mersenne_twister_engine` uses its compile-time `default_seed` constant (5489), so the draw sequence is byte-identical every run. The engine is also a per-object member of a function-local clustering object, so no state carries between clustering problems. The clustering result genuinely does reach QoR (centroids become physical tap locations via `createTap(loc)`), which is why the seed mattered enough to check — but there is no entropy or time source anywhere in `mscts/`. |


### Pattern 2.1

| Count | Bucket | Why dismissed |
|---:|---|---|
| 6 | srand(time(NULL)) in skewgrp/ — directory is not compiled into the product | `skewgrp/ctsSkewgroup.cc:152` and `skewgrp/ctsDStest.cc:150` call `srand(time(NULL))` and then draw `rand()` four more times — textbook pattern 2.1/1.5 hits, and the only time-seeded RNG anywhere in CTS. They are dismissed on **build evidence**, not on a judgement call: `skewgrp/Master.make` declares `CPPFILES =` and `HFILES =` **empty**, so nothing in the directory is compiled; `Master.make:57` explicitly excludes `*/skewgrp/*` from linting; `skewgrp/ctsDStest.h:17` declares its own `int main(...)` and `skewgrp/ctsDSmain.cc` provides it; and a tree-wide grep for `ctsSkewgroup`/`ctsDStest` returns only the five files inside `skewgrp/` itself. This is a standalone disjoint-set experiment, not product code. Per the skill's rule this is real build-system exclusion, not a `purecov`-style analysis hint. |


### Pattern 2.2 — getFullName() / getPathName() used as map key or hashed

| Count | Bucket | Why dismissed |
|---:|---|---|
| 18 | Membership-only name set - only .find()/.count() is ever called, never iterated | Full membership: `ccdvdProblemGenerator.cc:99` (`_seedNames`), `ccdtwnsProblemGenerator.cc:475`, `ccdpwProblemGenerator.cc:105`, `ccddrcProblemGenerator.cc:81` and `:83`, `ccdptProblemGenerator.cc:521`, `msscProblemGenerator.cc:407` (`_manualInsts`), `ctoscGlobal.cc:2844` and `:3008` (`newSgSinks`), `ctomtGlsCostCalc.cc:725` (`notBufferedSinks`), `ccdInfra.cc:1647` (`changingNets`), `bgtProblemGenerator.cc:1927` (`_fixedPrepones`) and `:3702` (`_removedInv`), `msTapCellMgr.cc:3057` and `:3105`, `msAutoTapFlow.cc:3737` (`l_removedNames`), `ctsXformProblems.cc:1195` (`finalInsts`) and `:1394` (`_dirtyInsts`).  Every one is a name set consulted only through `.find()` or `.count()` - `ccddrcProblemGenerator.cc:660`, `:716`, `:720`; `ccdInfra.cc:1499`, `:1558`; `bgtProblemGenerator.cc:1275`, `:1820`, `:1910`, `:3615`; `msTapCellMgr.cc:3094`, `:3128`; `msAutoTapFlow.cc:3767`; `ctoscGlobal.cc:2867`, `:3034`; `ctomtGlsCostCalc.cc:747`; `fmaxProblemGenerator.cc:810`, `:926`. I checked for iteration over each and found none, so no key order ever reaches a decision. Set membership on a string is order-free, so there is no non-determinism regardless of whether the container is `std::set` or `std::unordered_set` - and I confirmed the `unordered_set` cases (`ctoscGlobal.cc:2832`/`:2996`, `ctomtGlsCostCalc.cc:718`, `msTapCellMgr.cc:3046`/`:3049`) are membership-only too.  The residual cost is one `getFullName()` per insert and one per query. Keying by `getIdLong()` would be cheaper, but with no correctness or determinism consequence these do not meet the bar for a defect. Two special cases: `msAutoTapFlow.cc:3737` is additionally gated by `_reportInsertedDrivers` and exists only to support driver-insertion reporting; `ctsXformProblems.cc:1195` and `:1394` are membership-only in isolation but must move together with `_instInfoMap` if that finding's fix is adopted, which is why they are listed in its fix versions. Samples: `ccd/ctsccd/cgbased/ccdptProblemGenerator.cc:521`, `ccd/ctsccd/drc/ccddrcProblemGenerator.cc:81`, `ccd/ctsccd/power/ccdpwProblemGenerator.cc:105`. |
| 10 | getFullName()/getPathName() appears only in report, log, assert, #if 0 or commented-out text | The pattern's own guidance exempts reports and user-visible diagnostics. Lines 317 and 321 sit inside an `#if 0 ... #endif` block (opened at :313, closed at :325). Lines 463 and 485 are commented-out `// Cudd_PrintDebug(...)` calls. Lines 468 and 490 are `dvuAssert` arguments, compiled out of production builds. Lines 342, 346, 460 and 483 are `userOutput::printf` arguments inside `if (_debug)` blocks. None of the ten feeds a live container lookup.  Caveat worth carrying forward: the *neighbouring* printf blocks at 455-457, 465-467, 478-480 and 487-489 are **not** guarded by `_debug` and do issue live `count()`/`find()` calls. Those did not appear as separate candidates in this slice, but they are called out in the `ctsmisc/ctsICGCell.cc:514` finding because they should be fixed in the same change. Samples: `ctsmisc/ctsICGCell.cc:317`, `ctsmisc/ctsICGCell.cc:321`, `ctsmisc/ctsICGCell.cc:342`. |
| 6 | The name IS the required external/persisted key (clone-map file, SVF file, ML cache file) | **safe-adopter.** In all six the string is not an internal convenience - it is the serialization key of an external file format, so it could not be replaced by an id without breaking the format.  `ctsSplitMgr::exportCloneMap` (`:888-913`) builds `stringToInstVecMapType masterToClonesVecMap` (`ctsSplitMgr.h:130`, `std::map<std::string, std::vector<ndmInst*>>`) whose only consumers are `ctsIcgLatencyDrivenCloning::writeCloneMapFile` (`icg/ctsICGCloningHelper.h:148`) and `writeSvfFile` (`:149`), called from `icg/ctsICGCloningHelper.cc:997`. SVF is a formal-verification interchange format that identifies instances by name; the clone-map file is read by downstream tools. Note also that the loop it iterates, `_cloneMap`, is an `instToInstVecMapType` = `std::map<ndmInst*, std::vector<ndmInst*>, ndmObjPtrCmpType>` (`ctsSplitMgr.h:131`) - already id-ordered, so the traversal is deterministic before the name is ever taken.  `mlRecord.cc:534` (`_mostCommonLeq`, `mlRecord.h:109`) and `bgtProblemGenerator.cc:398` (`leq`, fed straight into `bgtMLCache::readFromFile(leq)` at `:400`) key the budget ML cache by library-cell name, which is how the on-disk cache matches entries across runs and across designs. Replacing the key with an id would make the cache unusable.  The only residual cost is `exportCloneMap` calling `getFullName()` up to three times per cloned ICG in the loop at `:891-911`; that could be hoisted into a local, but the loop is bounded by the clone count and the name is needed anyway. Samples: `ctssplit/ctsSplitMgr.cc:898`, `ctssplit/ctsSplitMgr.cc:903`, `ctssplit/ctsSplitMgr.cc:906`. |
| 2 | Deliberate name-sorted report map - this is the ND cure, not the disease | Both sites take an **id-keyed** map (`_aggsizedCells` / `_aggaddedCells`, declared `std::map<ndmInstId, ndmModule*>`) and copy it into a temporary `std::map<std::string, ndmModule*>` named `sortedaggsizedCells` / `sortedaggaddedCells` for the sole purpose of emitting the CCD changed-cells report in lexicographic name order (`fprintf(fp, "  %s\n", (it->first).c_str())` at :6693 and :6704). The instance is fetched via `_ctsInfra->getInstById(it->first)` at :6688 and :6698, so the id remains the source of truth throughout.  This is exactly the idiom the audit recommends elsewhere: keep ids internally, resolve to names only at the report boundary, and sort the report by a stable user-visible key. Flagging it would be backwards. The cost is one `getFullName()` per changed cell, once per report, which is the minimum possible for a report that must print names. Samples: `ctssc/ctsscGlobal.cc:6690`, `ctssc/ctsscGlobal.cc:6700`. |
| 2 | Dead store - the value computed from the name lookup is unconditionally overwritten on the next line | Both lines compute `maxDelay = std::max(maxDelay, kneeMap[kneeOrder.begin()->second->getFullName()].get<1>());` and both are immediately clobbered.  At `ctsscKneeExtractor.cc:686` the very next statement is a bare `maxDelay = 1000.0;`. At `ctskSize.cc:1376` it is `if(low_power) { maxDelay = 1000.0; }`, and `low_power` is hardcoded `true` two lines earlier at `:1362` (`bool low_power = true;`, with the original `getenv("CCD_KNEE_ALLOW_LOW_POWER")` commented out on the following line). So the assignment is unconditional in both files.  The `getFullName()` call on each of these lines is therefore pure waste and both lines can simply be deleted. They are dismissed as candidates in their own right and folded into the `ctssc/ctskSize.cc:1384` finding, whose Version C fix removes them. The same dead `low_power` condition also makes `ctskSize.cc:1388` (`if(kneeMod == mod && !low_power) { break; }`) unreachable - noted for the owner, outside this slice. Samples: `ctssc/ctskSize.cc:1374`, `ctssc/ctsscKneeExtractor.cc:684`. |
| 1 | Dead code - the entire enclosing function is inside a block comment | **dead/unused.** `fmaxOnRouteBuffer::intensifyTargetRangeSolo` is enclosed in a `/* ... */` block that opens at line 1148 and closes at line 1181. The body still contains two bare `TODO:` markers at :1161 and :1163. Nothing in it compiles.  This is not a `purecov`/Coverity annotation - it is a literal C block comment, which I verified by reading the surrounding lines rather than inferring from a marker.  Worth recording as a positive signal: the **live** siblings of this code already use the recommended idiom. `ccd/ctsccd/fmax/fmaxOffRouteBuffer.cc:529` declares `std::map<ctsTermId, std::set<ndmModule*, ndmObjPtrCmpType> > driver2leq` - id-keyed - and `ccd/ctsccd/fmax/fmaxOffRouteBufferFinal.cc:198` and `:242` use `std::map<ndmTerm*, std::vector<ndmModule*>, ndmObjPtrCmpType>` - pointer-keyed with the ID-stable comparator. The commented-out `std::map<std::string, ...>` version at :1152 is the abandoned older design. Samples: `ccd/ctsccd/fmax/fmaxOnRouteBuffer.cc:1169`. |


### Pattern 2.4

| Count | Bucket | Why dismissed |
|---:|---|---|
| 8 | Only the VALUE of *min_element/*max_element is consumed - position and ties are irrelevant | **false-positive.** Every one of these immediately dereferences the returned iterator and uses only the scalar. Which of several tied elements produced that scalar cannot matter, because all tied elements yield the same value by definition.  `ctsrptTransitionHistogram.cc:259` - `unsigned maxCount = *std::max_element(bins.begin(), bins.end());` over a `std::vector<unsigned>` of histogram counts, used to scale bar widths. `ctoFlow.cc:121-122` - `int maxLevel = (*lIter) > 0 ? (*lIter) : 0;` over a `std::vector<int>` of clock levels, used only to size `_clocks`. `ctoscLoadPartition.cc:967` - `size_t minBoundary = *std::min_element(_solutions.begin(), _solutions.end());` over a `std::vector<size_t>`, passed as a scalar to `appendBinaryPartitions`. `msFlexibleTapPartition.cc:911`, `:945`, `:1019`, `:1029` - all four are `*(std::max_element(_tapLatencies.begin(), _tapLatencies.end()))` over a `std::vector` of floats, consumed as a `printf` argument. Two of the four (`:945`, `:1019`) are additionally inside `if (_debug)`. Report-only on top of value-only. `soClockGraph.cc:733-734` - `return (*std::max_element(..., [](const auto &lhs, const auto &rhs) { return lhs.size() < rhs.size(); })).size();` - the comparator ranks by `.size()` and the result is `.size()`, so every tied element returns the identical number.  None of these holds pointers, and none uses `std::distance` to recover a position. Samples: `ctsrpt/ctsrptTransitionHistogram.cc:259`, `ctscto/ctoFlow.cc:121`, `ctscto/ctosc/ctoscLoadPartition.cc:967`. |
| 5 | Vector is indexed by a canonical scenario ID, so first-max means lowest ID - deterministic | **false-positive.** All five are the same idiom: `int worstScenId = std::distance(worstScenarioCnt.begin(), std::max_element(worstScenarioCnt.begin(), worstScenarioCnt.end()));` followed by `worstScenId = (worstScenarioCnt[worstScenId] == 0) ? -1 : worstScenId;`.  The position *is* used, so this does not fall into the value-only bucket - but `worstScenarioCnt` is a `std::vector<int>` **indexed by scenario id**, not an arbitrarily-ordered list. I confirmed this at the fill sites (`ccdSubtree.cc:697`, `:704`, `:708`: `worstScenarioCnt[qScenId]++` and `worstScenarioCnt[dScenId]++`), where the subscript is the scenario id itself. The vector's layout is therefore canonical and identical on every run.  `std::max_element` returns the **first** maximum, so on a tie the winner is the **lowest scenario id** - a stable, meaningful, reproducible tiebreak that happens to be exactly what an explicit tiebreak would have been written to do. The element type is `int`, not a pointer, so there is no address comparison anywhere. The resulting `critScen` is deterministic. Samples: `ccd/ctsccd/ccdSubtree.cc:715`, `ccd/ctsccd/ccdSubtree.cc:834`, `ccd/ctsccd/ccdSubtree.cc:1524`. |


### Pattern 2.5 — std::unique on pointer vector without prior stable sort

| Count | Bucket | Why dismissed |
|---:|---|---|
| 14 | Preceding sort uses a stable total-order key, so std::unique is correct and deterministic | **false-positive / safe-adopter.** In every case I read the lines immediately preceding the `std::unique` and confirmed the sort key is stable and the dedup key is consistent with it.  **Plain integers, default `<` (fully ordered, dedup exact):** `msAutoTapFlow.cc:7519-7522` (`gridX`/`gridY`, `std::vector<int>` coordinates); `soSolverUpdater.cc:272-273` and `:331-332` (`selectedToInfos`, `std::vector<int>` indices); `ccduiReport.cc:5802-5803` (`_icgEnNodes`, graph node IDs).  **ID-stable pointer comparator:** `msMerge.cc:250-251` and `soClockGateOpt.cc:401-402` both sort with `ndmObjPtrCmpType()` before `std::unique`. This looked like the classic address-order trap, so I resolved it: `ccd/util/ccdUtil.h:71` reads `typedef ndmObjectHandleNS::compareObjPtr ndmObjPtrCmpType;` - it compares object **IDs**, not addresses, as the comment at `ips/ipsManager.cc:300` ("compared by Id") confirms. Identical pointers have identical ids, so equal elements are contiguous after the sort and `std::unique` removes them correctly and reproducibly.  **Sorted by coordinate, deduped by index, and the two agree:** `msTapCellMgr.cc:4568-4583` sorts `std::vector<int> nodes` by `graph.nodes[i].coord` (X then Y, or Y then X) and then uniques by `int` equality. That is only safe if equal coordinates imply equal indices - and they do: `ensureShieldComponentNode` (`:3852-3869`) looks up a `NodeKey{x, y, layer}` in `graph.nodeLookup` and returns the existing index when present, so one coordinate maps to exactly one index. Equal-comparing elements are therefore identical elements, contiguous after sorting, correctly deduped.  **Value-sorted with an explicit anti-pointer comment:** `soMacroDelay.cc:438-442` uses `std::stable_sort` with `return *s1 < *s2;` and the author's own comment "Don't sort by pointer, but by cstrScenario::operator<". The subsequent `std::unique` does compare `const cstrScenario*` by address, but `getScenario(mode, corner)` (`:431`) returns a canonical pointer per (mode, corner) pair, so equal-valued entries are the same pointer and land contiguously.  **Name-keyed and consistent:** `msuiCommands.cc:202-205`, `:652-655`, `:738-739` pair `std::stable_sort(..., GroupBase::LessName())` with `std::unique(..., GroupBase::SameName())` - same key for both operations, and `stable_sort` preserves input order among same-name groups.  **Value-typed, single-field key:** `msPreroutes.cc:909-910` sorts `msTracks` with `CompareTracks` (`msPreroutes.cc:787-790`: `track1.getCenterTrack() < track2.getCenterTrack()`) over `msTrack` **values**, not pointers. `soDesign.cc:9122-9123` sorts `std::vector<cstrClock> masterClocks` with default `<` over handle values.  None of these is pointer-address-ordered and none has an absent sort. Samples: `mscts/preroutes/msPreroutes.cc:910`, `mscts/msutil/msTapCellMgr.cc:4583`, `mscts/drivers/msAutoTapFlow.cc:7520`. |


### Pattern 2.6

| Count | Bucket | Why dismissed |
|---:|---|---|
| 3 | Duplicate grep hit on the loop's closing-brace comment, not a distinct site | Each of these three lines is the closing brace of a loop already counted at its opening line, carrying a trailing comment that repeats the loop header text: `} // for (const auto & entry : std::filesystem::directory_iterator(parentFolderPath))`. The scanner matched the comment.  So the eight raw 2.6 candidates cover only **five** distinct iteration sites: `ctsTest.cc:985`, `ctsTest.cc:1646`, and `fmaxLpSolverCompressedEndpoints.cc:2176`, `:2606`, `:2632`. Worth noting for the scanner's own accounting, since it inflates this pattern's apparent hit count by 60%. Samples: `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2191`, `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2621`, `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2640`. |
| 2 | Directory order neutralized downstream, or names are unique within a directory | **neutralized.**  `fmaxLpSolverCompressedEndpoints.cc:2606` (`runLpSequenceFromFiles`) collects `.mps` files in directory order exactly as its ICG sibling at `:2176` does, but the consumer differs: `executeFlowBasedOnFiles` calls `std::sort(allModels.begin(), allModels.end(), IsSmallerAdHocModel())` at **line 2101**, before any solve. `IsSmallerAdHocModel` (`ccd/ctsccd/fmax/fmaxLpSolver.h:209-274`) is a genuine total order - variable count, then constraint count, then a stage score parsed from the filename (OPTIMISTIC/POWER/R2R_TNS/HOLD_TNS/R2R_WNS/IO_TNS), and finally `modelA.name < modelB.name` at `:267`. With a full name tiebreak there are no residual ties, so the model sequence is identical regardless of inode order. This is why the ICG variant at `:2176` is a finding and this one is not - the difference between them is the missing sort.  The `baselineFilenames` half of that function is unsorted, but it is inert: `allBaselines` is built at `:2087-2093` and never read, and `hasBaseline` is computed at `:2149-2151` and never used. I grepped every occurrence of both names to confirm. `matchModelsWithBaselines` (`:2030-2062`) keys `modelToBaseline` by model name and iterates `firstModelsPerStage`, a `std::set<std::string>` - ordered - so even that mapping is deterministic.  `ctsTest.cc:1646` scans each `$PATH` component with `readdir` to build `_unixMap` (command name -> full path), inserting only when absent: `if (_unixMap.find(lname) == _unixMap.end())` at `:1656`. Filenames are unique within a single directory, so `readdir` order cannot change which entry wins inside one component; and precedence **between** components is carried by the outer `while (s1 != std::string::npos)` loop at `:1638`, which walks `$PATH` left to right. Correct shell precedence is preserved and the result is deterministic. (Its sibling at `:985` is a different matter and is filed as a LOW finding.) Samples: `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2606`, `ctsutil/ctsTest.cc:1646`. |


### Pattern 3.1,3.2

| Count | Bucket | Why dismissed |
|---:|---|---|
| 35 | non_code_include_or_comment | `#include` lines, doc comments, and `}); // tbb::parallel_for` closing-brace comments. These match the grep signature textually but contain no executable parallel construct at all. The scanner is matching `tbb::parallel_for` inside a trailing comment that the authors add to mark the end of a long lambda - a stylistic convention in `ccd/ctsccd/fmax/` that alone accounts for 26 of these hits. Zero analysis value. |


### Pattern 3.2 — Multi-threaded shared container writes

| Count | Bucket | Why dismissed |
|---:|---|---|
| 44 | job_dispatch_disjoint_per_job_state | `parallel_for` over a job/index vector where each task owns its own job object and the results are folded back single-threaded in index order afterwards - the dominant idiom in `soCG.cc`, `soSolverUpdater.cc`, `fmaxcgSolverImpl.cc` and `ctsLazyCostGroup.cc`. The job vectors themselves are built from ordered containers (`std::map` / `std::multimap` traversal), so the dispatch order is deterministic and the fold order is fixed. Verified representatives: `ctsLazyCostGroup.cc:597`/`:622` dispatch `populateMtJob`s and fold at `:632-644` in index order, appending to `_q2d` with a comment noting the D ids arrive already increasing; `ctsLazyCostGroup.cc:1045` dispatches `collectLazyPathForTracing` (the producer half of the latent-only finding, listed there); `ctsLazyModel.cc:2413` folds `traceLazyPathMtJob`s at `:2423-2463` walking the ordered `jobsPerMode` map; `soSolverUpdater.cc:2100`/`:2107` are **excluded** from this bucket because they write the shared solver directly - that is the HIGH finding. |
| 37 | presized_index_write_or_per_thread_buffer | Bodies that write only `v[i] = ...` into a vector sized before the loop, or into a per-thread buffer that is concatenated back in fixed index order. Both are on the explicit safe list. Representative checks: `soCG.cc:1675`/`:1738` use a **fixed** grainsize `std::max(_variablesVec.size()/256UL, 256UL)` that does not depend on the core count and write `grads[i]` / `tempArcVals[j]` by index; the `soCG.cc` gradient functors (`parallelTnsGradAdd`, `parallelIOTnsGrad`, `parallelHoldTNSGrad` at `soCG.cc:6194-6243`) parallelise over the **variable index** and accumulate over jobs `j` in fixed job order, so the floating-point summation sequence is identical under any range split - this is the correct way to write a parallel FP reduction and it is worth noting the codebase already does it; `ctsLazyCostEp.cc:2029` computes explicit chunk bounds (`threadCount*averageQueryCount + std::min(carry, threadCount)`) and drains `finalStepEntries` in thread order at `:2042`, which reproduces the original `skewQueries` order exactly; `fmaxProblemGeneratorPower.cc:574` chunks against a **hardcoded** `maxThreads = 250` (`:562`), not the hardware; `fmaxLpSolverIncremental.cc:5117` precomputes index ranges at `:5111-5115` and `std::sort`s each path vector at `:5126`; `ctsIfsInterf.cc:986` merges `perEpResults` in index order at `:991-993`. |
| 13 | prepopulated_container_element_write | `tbb::parallel_for_each` (or an indexed `parallel_for`) over a container whose **structure is fixed before the parallel region**, where each task writes only its own mapped value. No structural modification, no cross-task sharing. Verified: `soLogicCone.cc:1875` is preceded by a serial `try_emplace` fill at `:1871-1874`; `soLogicCone.cc:1940` by `_libCellToGraph[libCell]` at `:1935-1938`; `soLogicCone.cc:1963` by the `emplace` fill at `:1953-1960`; `ctoAbsTree.cc:10453` by `cTermDelayMap.emplace(term, ...)` at `:10448-10451`; `soPdmDataRetriever.cc:130` by the `_endPointSetupInfo.emplace_back` loop at `:120-128`; `ctsLazyModel.cc:3407` by the explicit `// make sure that dst map has all entries (to avoid changes to the map structure in MT)` fill at `:3400-3404`. This is precisely the discipline that `soSolverUpdater.cc:2100` (the HIGH finding) fails to observe. |
| 12 | declaration_only_no_parallel_body | `typedef` / `using` aliases, class member declarations, and function parameter lists that mention a `tbb::concurrent_*` type. The declaration says a concurrent container exists somewhere; it says nothing about whether any iteration of it is result-affecting. Each was followed to its actual use site, and those use sites are triaged under the other buckets or under a finding. |
| 9 | concurrent_container_neutralized_by_sort_or_ordered_sink | Concurrent containers that are genuinely filled in scheduling-dependent order, but whose **only** consumer re-establishes a total order before anything result-affecting happens. This is the pattern the codebase gets right, repeatedly and deliberately - several sites carry an explicit `// need to make sure the order is deterministic` comment immediately above the sort. Verified individually: `ctsLazyCostGroup.cc:914` copies `allDsSet` out and `std::sort`s it (`:931-932`); `ctsLazyCostGroup.cc:1801` drains `touched` into a `std::set<grNodeId>` (`:1826`); `soSolverUpdater.cc:1953` drains `clustersToTrace` into a `std::set<unsigned int>` (`:2021-2024`); `fmaxCgSolver.cc:452-454` builds a `std::set<cstrCornerId>` (`:490`) and a `std::sort`ed vector (`:516-517`); `ctsInterClockBalance.cc:741` feeds `arrivals1` into a `std::set<float>` before taking the median (`:759-780`). Classification: neutralized. |
| 2 | generic_wrapper_definition | The definition of `ccdUtil::parallel_for` itself - an ndm-friendly wrapper that suspends the `ndmDesignWriteLock` and forwards to `tbb::parallel_for`. It takes a caller-supplied `std::function` and touches no state of its own, so whether any given call is safe is a property of the callback, not of the wrapper. The callbacks are triaged at their own call sites. |
| 1 | develop_only_debug_hook | `ctsSession.cc:302` is a deliberate two-thread crash inside `#ifdef Synopsys_Develop`, further gated by the `ctsSessionTestAssertionHandlerForceAssert` debug setting. It exists to test that the assertion handler prints exactly one stack trace when two threads fault simultaneously. Not present in a production build and not a computation. |


### Pattern 3.6 — Post-collection use without canonical ordering

| Count | Bucket | Why dismissed |
|---:|---|---|
| 263 |  |  Samples: `ctsui/ctsuiscRandomTest.cc:314`, `ctsui/ctsuiscRandomTest.cc:354`, `ctsui/ctsuiscRandomTest.cc:1068`. |
| 82 |  |  Samples: `mscts/preroutes/msPreroutes.cc:2424`, `ctsmisc/ctsExclude.h:281`, `ctsmisc/ctsExclude.h:350`. |
| 70 |  |  Samples: `mscts/msutil/msTapCellMgr.cc:3015`, `ctsutil/ctsGateModeling.cc:1133`, `mscts/mstap/msClustering.cc:447`. |
| 67 |  |  Samples: `ctsui/ctsuiscRandomTest.cc:1150`, `ctsmisc/ctsDcWrapper.cc:389`, `ctsui/ctsuiCtsCstr.cc:176`. |
| 26 |  |  Samples: `ctsui/ctsuiReport.cc:1006`, `ctsui/ctsuiReport.cc:2925`, `ctscto/totalskew/ctoAbsTree.cc:1719`. |
| 24 |  |  Samples: `mscts/msutil/msIOUtils.cc:190`, `mscts/mstap/msTapSynthesis.cc:2914`, `ctsutil/ctsLpSolverWrapperImplCore.cc:1983`. |
| 23 |  |  Samples: `icg/ctsIcgRelocationLpCommitSplitInternal.h:168`, `mscts/msutil/msTapCellMgr.cc:4680`, `ctsutil/ctsDelayLookup.cc:455`. |
| 3 |  |  Samples: `ccd/skewopt/soClockGateOpt.cc:1009`, `ccd/skewopt/soClockGateOpt.cc:1054`, `ccd/ctsccd/power/ccdpwResultIntegrator.cc:299`. |
| 2 |  |  Samples: `ctssc/lazytns/ctsLazyModel.cc:2334`, `ctssc/lazytns/ctsLazyModel.cc:2451`. |
| 1 |  |  Samples: `ctsutil/ctsLocalSkew.cc:317`. |
| 1 |  |  Samples: `mscts/msmesh/msIncrMerger.cc:284`. |
| 1 |  |  Samples: `ctsmisc/ctsRestrictionReporter.cc:201`. |


### Pattern 3.7

| Count | Bucket | Why dismissed |
|---:|---|---|
| 97 |  |  Samples: `mscts/msutil/msUtil.h:402`, `mscts/msutil/msUtil.cc:2077`, `mscts/msutil/msCstrDesign.h:730`. |
| 23 |  |  Samples: `icg/ctsICGCloningHelper.h:172`, `ctssch/ctsTask.h:652`, `ctssch/ctsTask.h:653`. |
| 15 |  |  Samples: `mscts/msgts/msgtsClustering.cc:104`, `mscts/msgts/msgtsClustering.cc:146`, `mscts/msgts/msgtsClustering.cc:147`. |
| 6 |  |  Samples: `icg/ctsICGReclusterHelper.h:84`, `mscts/msui/msuiReportPowerTaps.cc:71`, `ctssc/ctsscProblemGenerator.h:974`. |


---

## Non-Real Classifications (deep-read verdicts)

These required tracing rather than a regex filter, and each was a plausible
defect until the chain was followed. They are recorded because the reasoning is
the reusable part.

| Site | Verdict | Evidence |
|---|---|---|
| `ctscstr/ctscstrDesign.h:92` | **latent-only** | `std::hash<const ndmDesign*>` feeds exactly one container, `_subDesignObserverHash`, via a typedef 335 lines away. Its only iteration is the destructor at `ctscstrDesign.cc:234-241`, which does `observer->detach(design); delete observer;` per entry on independent design/observer pairs — commutative, so the final state is permutation-invariant. The in-code comment about `spacing_rules.tcl` "under 1 thread" describes an **ASAN memory-safety** reproducer, not non-determinism; single-threaded reproducibility argues *against* ND. |
| `ctscto/ctosc/ctoscFilter.h:334` | **latent-only** | `tuple_hash` xor-combines `std::hash<const ndmInst*>` and `std::hash<const ndmModule*>`, but its single container `_mapModuleCost` has 13 use sites and all are `find`, `operator[]`, or `clear`. Best-module selection runs through a `std::priority_queue` fed by explicit pushes in program order. Worth hardening opportunistically; no order is observed today. |
| `mscts/mstap/msClustering.h:284` | **false-positive** | Unseeded `boost::random::mt19937` uses the compile-time `default_seed` of 5489, so the draw sequence is byte-identical every run. The clustering result genuinely reaches QoR via `createTap(loc)`, which is why it was worth checking, but no entropy or time source exists anywhere in `mscts/`. |
| `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:312` | **false-positive** (as a float reduction) | All four instantiations use `sccEvalResult` = `{bool value; std::string localLog;}` combined with `&&`/`||` — not a floating-point reduction. `done(init)` fires only once the boolean has reached the operator's absorbing element, so neither dropping operands nor reordering joins can change it. The `localLog` string concatenation *is* order-dependent but only reaches a debug tracer. |
| `ctsutil/ctsMtTaskRunner.h:81` | **dead/unused** | `step` is computed from `max_concurrency()` and clamped, but the `blocked_range` at `:87` is constructed with only `(begin, end)` — the grainsize argument is never passed, so the value is discarded and TBB's auto-partitioner does the splitting. |
| `ctscto/ctoGrpLatCalc.cc:80` | **latent-only** | `_step` really is used as the grainsize, so chunk boundaries follow `hardware_concurrency()`. But the body writes `grpLat[i]` by index, and the only cross-thread state (`maxLate`, `worstRatio` under `mtSpinMutex`) are max-reductions with no witness captured — max is commutative, so regrouping cannot change the result. **Separate non-ND bug worth filing:** `hardware_concurrency()` ignores `set_host_options -max_cores`, so a core-limited run sizes its partition for hardware it cannot use. |
| `ctsroute/ctsRouter.cc` (`_nets`) | **dead/unused, low confidence** | The strongest ND chain found anywhere in the audit on paper — `updateAllRoutes()` routes nets in address order against a shared congestion map and writes results to NDM via `writeShapes()`, which is textbook route-order ND affecting QoR. Classified dead because nothing constructs it: `ctsRouter` is built only by `ctsRouterInterf`, which has no constructor call in this snapshot, and `ctsRouter.h` is not exported. **But `ctsRouterInterf.h` *is* exported and the snapshot is `cts`-only**, so a caller elsewhere in `nwtn/src` cannot be ruled out. Close with `rg 'ctsRouterInterf' nwtn/src`; if a caller exists this becomes a HIGH and the chain is already documented. |
| `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2606` | **neutralized** | `executeFlowBasedOnFiles` sorts the models at `:2101` with `IsSmallerAdHocModel`, a total order ending in a full filename comparison, so `directory_iterator` order is fully canonicalized. The unsorted baseline list is inert: `allBaselines` and `hasBaseline` are written and never read. |
| `ctssc/lazytns/ctsLazyModel.cc:2520` | **latent-only** | Left non-real on one unresolved fact: whether duplicate `(LPKEY, D-node)` entries with differing path groups can occur. A one-line debug assertion would close it either way. |
| `ctoUtil.cc:4384`, `ctomtReloc.cc:868`, `:882` | **latent-only** | Three `min/max_element` sites with real positional tie-breaks feeding real placement mutations, but their vectors are ordered by timing-graph arc iteration (`grArc` / `grGraph` / `ctsOutArcIterator`), which is outside this snapshot. If that iteration turns out to be pointer-keyed, `ctoUtil.cc:4384` should be re-rated MEDIUM — its index is a single-load hard veto on every relocation candidate. |

### Adjacent non-ND defects found while tracing

Recorded because they are real bugs, but they are deterministic and therefore
out of scope for an ND audit:

- **`ccd/ctsccd/ccdSinkSize.cc:301`** — `std::map<float, ndmModule*>::insert`
  rejects duplicate keys, so lib cells that characterize to the same arc delay
  never reach `passedSet` at all. This is silent data loss independent of
  ordering, and it is why the pattern-3.6 MEDIUM recommends fixing the consumer
  regardless of the guard.
- **`ctscto/ctoGrpLatCalc.cc:80`** — `hardware_concurrency()` bypasses
  `set_host_options -max_cores`.
- **`ctssch/ctsTimingDrivenTransitionTargets.h:182-189`** — `compareTimInfo`
  returns `true` for `cmp(a,a)`, violating strict weak ordering. This is UB for
  a `std::set` comparator. It is *promoted* to a MEDIUM finding in this report
  because the arbitrary tie order reaches a `max_transition` constraint write,
  but note that the UB itself is a defect even on a fixed binary.

---

## CL-Mined Semantic Checklist Coverage

The Stage-3 checklist families that regexes do not reach. Each was searched;
the outcome is either a promoted finding or a stated dismissal.

| # | Family | Outcome |
|---|---|---|
| 1 | Post-collection canonicalization | **2 findings promoted** (`ctsTimingDrivenTransitionTargets.h:181`, `ctsUtils.cc:57`). A scripted backward pass resolved each collection loop's *source container* through a tree-wide typedef map, reducing 563 seeds to 6 sites with a genuinely unstable pointer-keyed source; all 6 were then read in full. |
| 2 | Project wrapper containers | **No findings.** `ndmPtrSet`/`ndmPtrMap` (97 of 141 seeds) are ordered by `dosContainer::keyCompare` on `(ndmType, ndmID)` and are the project's determinism *fix*; `nwcInsOrdMap` (15) is documented in-tree as the insertion-order remedy and all uses were correct; `dosUnorderedSet`/`dosUnorderedMap` (29) had only 3 sites that iterate at all. Notably `dosHash`, `hyHash`, `hyHashI`, `hySet`, `hyMap` **do not occur anywhere** in the CTS tree, so 5 of the 10 wrapper names in the pattern are dead vocabulary here. |
| 3 | Graph / geometry traversal canonicalization | **No findings.** Exclusion-traversal and geometry-sort comparators were read; traversal boundaries and tie-break keys were complete at every site inspected. `mscts/mscore/msDataModel.cc:10066` came closest — an address-hashed `unorderedNodeSet` flattened and then sorted by clock level only with a non-stable `std::sort`, leaving address order inside each level's tie group — but its consumer is a commutative set comprehension, so it stayed LOW/latent. |
| 4 | Stale cached state / deleted index cleanup | **No findings.** Lookup caches dominated the dismissals (roughly 30 buckets' worth across slices); none was shown to leak phase-local state into a later deterministic computation. |
| 5 | Delay-sharing / cross-scene state reuse | **Not closed — outside snapshot.** `mscts/drivers/msDriverRemoval.cc:150` passes an ND-ordered `l_finalConns` into `getGenericTimer()->removeCstrsFrom(...)`; the timer is not in this tree. One question to its owners decides whether that is latent or a real MEDIUM. |
| 6 | Concurrency / write-lock discipline | **1 HIGH promoted** (`soSolverUpdater.cc:2100`) — the only genuine data race found. Otherwise this code is unusually disciplined: the `soCG.cc` gradient functors parallelize over the *output* index and accumulate over jobs in fixed order, so the floating-point sequence never moves, and five separate concurrent containers are sorted or drained into a `std::set` before use. |
| 7 | Deterministic control-path normalization | **1 MEDIUM promoted** (`ctsUtils.cc:57`) — a determinism guard gated off at its own default. This is the checklist family that paid off best in this module. |
| 8 | Checksum / ND observability | **No findings.** No `dumpChecksum` / `reportChecksum` payload assembly in CTS was shown to be unstable. |
| 9 | Explicit `.begin()`/`.end()` on an ND container | **Applied as a dismissal rule, as intended.** Two independent slices had to re-derive the same libstdc++ subtlety: `std::map<K,V,C>::iterator` does not depend on `C`, so an iterator *spelled* without a comparator proves nothing about its container. 7+2 candidates were dismissed as safe-adopters on that basis after checking the declaration instead of the iterator. |

---

## Verification Notes

**Tooling.** Stage 1 used `scan_nd.py` with `rg` over the local snapshot
(`--min-severity MEDIUM`, `--max-per-pattern 8000`), giving 11,427 candidates
across 16 of the 21 patterns. A purpose-written narrowing pass
(`narrow_nd.py`) then applied the skill's documented Stage-1 rules
mechanically — balanced template-argument parsing to detect a supplied
comparator/hash, pointer-vs-value key resolution, and a tree-wide
"is this symbol ever iterated" index — cutting the pool to 1,570. Stage 2/3
ran as 7 parallel triage subagents, one per scope. Stage 4b used
`p4 annotate -c` on a ±6-line window per HIGH site, then `p4 describe -s` on
the dominant CL, resolving `[ORIG_CLIENT:...]`/CMT chains where present.

**Scope actually covered.** 2,391 C++ files, 52 MB, 23 subdirectories.
Candidate density by subdirectory was `mscts` 965, `ccd` 518, `ctsutil` 247,
`ctscto` 221, `icg` 159, `ctssch` 152, `ctsmisc` 119, `ips` 116, `ctssc` 111,
with the remainder under 100 each.

**Known limits, stated plainly:**

1. **Nothing was built or run.** No finding has a demonstrated run-to-run
   diff. Every claim is that the mechanism is present in source and that the
   order or value reaches an observable sink. Confirming any given row needs a
   two-run A/B on a real design.
2. **The snapshot is `cts`-only.** `nwtn/src/opt`, `util/crm.h`,
   `util/dos*.h`, `ndm/ndmPtr*.h`, `timerInterf`, `grArc`/`grGraph`, and
   `xformEngine` are not present. Wrapper semantics for `ndmPtrSet`/`ndmPtrMap`
   were inferred from in-tree comments (`msTapCellMgr.cc:3086-3093`,
   `ctsTypes.h:721`) rather than read from their definitions. Several
   latent-only verdicts would flip to real if a cross-module caller exists —
   `ctsroute/ctsRouter` is the most consequential.
3. **The snapshot is stale relative to depot `main`.** It is a tarball
   extraction dated 2026-07-19 with read-only files, no `.p4config`, and no
   usable `viewtool` client. Depot paths resolve cleanly under
   `//synopsys/nwtn/main/dev/nwtn/src/cts/`, and annotate content matched the
   snapshot line-for-line at 8 of 9 attributed sites. The exception is
   `mscts/drivers/msDrivers.cc`, which has drifted about +255 lines; its
   attribution was re-anchored by searching depot for `compareHierDepth`.
4. **One ownership attribution is unreliable.**
   `ctsmisc/ctsAutoBalancePoint.cc:656` annotates to CL `3007535`, a bulk
   branch merge whose referenced source CL (`3001507`, `lippens`) is a PV crash
   fix in unrelated code. Treat that author as unconfirmed and re-annotate the
   pre-merge branch revision before assigning.
5. **MEDIUM ownership was deprioritized.** Per the skill's severity policy,
   line-window attribution was run for HIGH sites and for the two main-agent
   findings. MEDIUM rows carry the resolved depot path so
   `p4 annotate -c` + `p4 describe -s` completes them cheaply.
6. **Pattern caps.** Patterns 3.3 and 3.6 exceeded the default 500-hit cap on
   the first pass (3,014 and 4,762 raw). The scan was re-run with an 8,000 cap
   so no Tier-1 pattern was truncated.
7. **Coverage gap in the pattern set itself.** The address-ordered family that
   actually appears in this tree is raw `std::tr1::unordered_set<T*>` /
   `unordered_map<T*,...>` with default hashes — `unorderedNodeSet`,
   `unorderedInstSet`, `unorderedTermSet`, `unorderedTapSetType`. Pattern 3.7's
   vocabulary names only project wrappers, so these were reachable only
   incidentally through 3.6. They deserve a Tier-1 pattern of their own.
8. **Two sites recorded as unverified rather than dismissed:** the
   `xformEngine::otfLegalization` replay path (`legalStateVec`, 2 sites) is not
   in this tree. Seven `timerInterf` endpoint-order seeds were dismissed on
   their consumers instead of on their source.
9. **`purecov` / Coverity annotations were not used as reachability
   evidence**, per the skill's rule. The one dead/unused call
   (`ctsutil/ctsPortPunchAnalyzer.cc`) rests on a real `#ifdef
   DEBUG_ctsPortPunchAnalyzer` exclusion, and the `skewgrp/` dismissal rests on
   an empty `CPPFILES` list in its `Master.make`.

**Artifacts.** Candidate and triage JSON, the narrowing and assembly scripts,
and the per-slice subagent outputs are all under
`/u/ranjithp/folders/coreStory/snps/nd-analysis/`.

