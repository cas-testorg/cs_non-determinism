# CTS Non-Determinism Details

Source dashboard: none for this run. Issue list came from the six user-provided confirmed CTS findings, preserved in the requested order.

Analysis context:

- `viewtool info` summary: skipped by instruction. This tree is a plain source slice, not a Perforce view; `viewtool info` is known to fail with `View cts was not created by viewtool`.
- `.synmake` / `DEVROOTS` summary: skipped by instruction. Reference-client resolution and `p4 annotate` attribution are unavailable from this tree.
- Source root used: `/remote/us01home05/carys/cts`.
- Tools used: direct source reads, `rg`, `/remote/u/binghui/bin/icc2query -a`.
- Scope notes: `util/dosMap.h`, `util/dosUnorderedSet.h`, and `tcl/clct.h` are included from outside this source slice and are not readable at `/remote/us01home05/carys/cts/util/dosMap.h`, `/remote/us01home05/carys/cts/util/dosUnorderedSet.h`, or a local Tcl implementation file.
- Methodology note: missing stable tie-breaks after deterministic vector input were not promoted. A sort-based finding below is considered real only where the input order comes from an address-ordered container first.

## Summary Table

| Issue | Severity | Real? | MT refinement | Triggering controls / app options | Short summary |
|---|---|---|---|---|---|
| #1 MT float reduction, thread-count dependent | Medium | Real | `Locked-but-order-dependent` equivalent: race-free, per-slot, thread-count-dependent reduction | FMAX incremental LP paired TNS/WNS path; `_maxThreads >= 2` at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2360`; thread count from `crmResources::get().getMaxThreadCount()` at `ccd/ctsccd/fmax/fmaxLpSolver.h:91`, commonly controlled outside this slice by `set_host_options -max_cores`; `icc2query -a set_host_options` returned no app-option row | Per-partition slots are reduced deterministically, but the partition count is `maxThreads()`, so changing thread count changes floating-point grouping and can change TNS low bits. |
| #2 `findDriverTerm` returns last driver in address order | Medium in default config; High impact when enabled | Real when gated on | n/a | `cts.multisource.enable_mlph_flow` default false, basic, block-scoped; data gates `loadNetSet && loadNetSet->size() > 1 && leafLevel` at `mscts/drivers/msDrivers.cc:712` | `_loadNetSet` is a raw-pointer `std::set<ndmNet*>`; `findDriverTerm` returns the last address-ordered driver's term, and auto-tap paths use that returned term to seed clock/sink context. Default-off MLPH gate downgrades the default-config severity from High. |
| #3 `get_power_taps` returns a Tcl collection in hash order | Medium | Real, scoped to collection order | n/a | User command `get_power_taps` at `mscts/msui/msuiGetPowerTaps.cc:172`; no app-option gate found | A `dosUnorderedSet<ndmBlkInst*>` is drained directly into the returned Tcl collection at `mscts/msui/msuiGetPowerTaps.cc:879`, so scripts can observe varying collection order. |
| #4 MV-aware driver insertion ordered by hier address | Medium | Real when equal-depth uncommitted hiers exist | n/a | Requires `_msgtsOptions.getUncommittedBlockInfo()` non-empty, `isLeaf` true, and no section at `mscts/drivers/msDrivers.cc:8185`; equal-depth sibling uncommitted hierarchies accepted by `-uncommitted_hierarchy_boundary` parsing at `mscts/msui/msuiCreateClockDrivers.cc:692` | A default `std::map<ndmHier*, ...>` is drained before a depth-only sort; equal-depth hiers keep address order and drive insertion order. |
| #5 Buffer insertion ordered by power-domain address | Medium | Real when MV-aware level balancing is enabled | n/a | `cts.multisource.enable_mv_aware_level_balancing` default false, hidden, block-scoped; `lbNode->isCrossingMVBoundary()` at `mscts/msmesh/msLevelBalancer.cc:1835`; group balance setting at `mscts/msmesh/msLevelBalancer.cc:755` | `domainToLoads` is a default `std::map<ndmPowerDomain*, ...>` and iteration order drives per-domain buffer insertion, name allocation, and placement-site consumption near the same driver. |
| #6 Load connection ordered by block-net address | Medium | Real | n/a | MLPH unassigned-load path; no separate app option beyond callers' flow gates found | A default `std::map<ndmBlkNet*, vector<ndmTerm*>>` orders `connectTerms` calls by block-net address, consuming shared net/port counters in varying order. |

## Issue #1: MT Float Reduction, Thread-Count Dependent

Dashboard ID: n/a
Location: `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:233`

### Verdict

Real, with a narrower mechanism than an arrival-order race. The `tbb::parallel_for` work can execute dynamically on TBB workers, but each loop index owns a stable partition slot, and the final TNS reduction walks those slots in index order at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:336`. That neutralizes worker arrival order. The remaining defect is that `numberOfThreads = this->maxThreads()` at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:233` changes the number of partitions, and `calculateRanges` computes `averagePathCount` from that thread count at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:126`. TNS is a floating-point sum, so regrouping the same endpoint slacks can change low-order bits across thread-count settings.

### Evidence

- `calculateRanges` totals endpoint path counts, divides by `threadCount`, and emits exactly `threadCount` ranges at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:120`, `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:126`, and `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:150`.
- The parallel dispatch is `tbb::parallel_for(size_t(0), numberOfThreads, size_t(1), ...)` at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:276`.
- Each iteration uses the loop index as the range index and result-slot index at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:278`, `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:307`, and `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:321`.
- TNS is accumulated with `resultsPerThreadTNS[threadCount] += double(endpointSlack)` at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:321`.
- Final TNS is accumulated serially in slot order at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:336`.
- WNS is not the same issue because it is merged by minimum comparison at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:343`.

### MT Reachability

The dispatch site is `tbb::parallel_for` at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:276`. Work scheduling is TBB-managed and may be dynamic/work-stealing, but the lambda argument is a stable partition index, not a worker ID. The issue is therefore not "first idle worker wins"; it is "different `maxThreads()` values create different stable partition sets."

The caller is `fmaxLpSolver::evaluateCurrentSolutionOneFunction`, which selects the paired TNS/WNS parallel path when the objective is TNS, the function is paired, and `_maxThreads >= 2` at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2357` and `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2360`. The parallel call is at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2364`.

### Race vs Ordering

This is race-free but order/grouping-dependent. Each partition writes its own `resultsPerThreadTNS` slot at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:270` and `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:321`; the final merge is single-threaded at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:336`. Locking is not relevant. Per the MT skill's neutralizer list, "per-thread partials merged in stable key order" neutralizes worker arrival order, but it does not neutralize thread-count-dependent regrouping.

### Gate Audit

- Thread-count gate: live. `_maxThreads < 2` avoids the path at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2360`; otherwise the parallel path runs at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2364`.
- Lock neutralizer: none cited and none needed for the per-slot writes.
- Determinism option: no determinism option found for this reduction. `fmaxLpSolver` initializes `_maxThreads` from `crmResources::get().getMaxThreadCount()` at `ccd/ctsccd/fmax/fmaxLpSolver.h:91`.
- App-option query: `/remote/u/binghui/bin/icc2query -a set_host_options` and `-a num_cpu_threads` returned no row. `/remote/u/binghui/bin/icc2query -a max_cores` returned unrelated app options such as `pin_check.common.max_cores`, not this FMAX controller.

### Downstream Visibility

`storeLatestEvaluationOfPairedFunctions(resultFloatTNS, resultFloatWNS)` stores the TNS result into the paired cost functions at `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:394` and `ccd/ctsccd/fmax/fmaxTimingCostFunction.cc:180`. The caller uses this evaluation as part of incremental LP feasibility and solution selection at `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:2364`. I did not run a design, so the exact QoR branch flip is not demonstrated here, but the floating-point result itself is an observable solver input.

### Controls / Gating

- `_maxThreads` comes from `crmResources::get().getMaxThreadCount()` at `ccd/ctsccd/fmax/fmaxLpSolver.h:91`.
- `CostFunction::_maxThreads` is set from the constructor `threadCount` at `ccd/ctsccd/fmax/fmaxCostFunction.cc:29` and `ccd/ctsccd/fmax/fmaxCostFunction.cc:38`, and read through `maxThreads()` at `ccd/ctsccd/fmax/fmaxCostFunction.h:69`.
- Local docs/scripts show `set_host_options -max_cores $prs_num_cpus` and `set_host_options -max_cores 1` in `ccd/docs/propts_preroute.cfg:226`, `ccd/docs/propts_preroute.cfg:228`, `ccd/util/scripts/propts.cfg:493`, and `ccd/util/scripts/propts.cfg:495`. The implementation of `crmResources` and `set_host_options` is outside this source slice.

### Code / Regression Setting Pass

No `nwtn/unit` directory is reachable at `/remote/us01home05/carys/cts/nwtn/unit` or `/remote/us01home05/carys/nwtn/unit`. Local scripts and docs contain `set_host_options -max_cores` examples at `ccd/docs/propts_preroute.cfg:226`, `ccd/docs/propts_postroute.cfg:213`, `ccd/docs/propts.functional_preroute_ccd.cfg:229`, `ccd/docs/propts.functional_postRoute_ccd.cfg:214`, and `ccd/util/scripts/propts.cfg:493`.

### Attribution

Unavailable. This source slice is not a Perforce client, so `p4 annotate` and CL ownership were not available.

### Fix Direction

Keep the expensive slack evaluation parallel, but make the reduction grouping independent of actual worker count. Two performance-aware choices:

- Store per-endpoint slack in a vector keyed by stable endpoint order, then do one serial full-precision pass over that vector. Cost is one `O(num_endpoints)` vector and one serial add; the expensive `evaluateSlackOfPath` loop remains parallel.
- Use a fixed number of virtual reduction buckets independent of `maxThreads()`, then let TBB schedule those buckets. Cost is bounded extra scheduling and possible load-balance tuning; the final sum is stable across host core counts.

Runtime confirmation should be a thread-count A/B: run the same design with `set_host_options -max_cores 1` and `set_host_options -max_cores N`, compare TNS raw bits or `%a`/full precision, then run `N` vs `N` to separate thread-count-dependent regrouping from true same-count scheduling ND.

Preemptive note: `getTotalInitialPower()` iterates `std::map<ndmInst*, float>` and sums floats at `ccd/ctsccd/power/ccdpwProblemGenerator.h:179` and `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:180`. A tree-wide symbol search found only those two definitions and no callers, so this is not a current finding.

## Issue #2: `findDriverTerm` Returns Last Driver In Address Order

Dashboard ID: n/a
Location: `mscts/drivers/msDrivers.cc:711`

### Verdict

Real when MLPH is enabled with multiple load nets at leaf level, but I grade it Medium in the default configuration because `cts.multisource.enable_mlph_flow` defaults false. The impact when enabled is High: the returned term can seed clock/sink context and later driver/tap construction. I also corrected the call-site count: `rg` finds 13 textual occurrences including one declaration at `mscts/drivers/msDrivers.h:633` and the definition at `mscts/drivers/msDrivers.cc:702`; there are 11 executable call sites.

### Evidence

- `_loadNetSet` is declared as `std::set<ndmNet*>*` at `mscts/drivers/msDrivers.h:493` and returned by `getLoadNetSet()` at `mscts/drivers/msDrivers.h:417`.
- `addLoadNet` allocates `new std::set<ndmNet*>()` at `mscts/drivers/msDrivers.cc:10309` and inserts the net at `mscts/drivers/msDrivers.cc:10310`.
- UI parsing for `create_clock_drivers -load` calls `msOptions.addLoadNet(...)` at `mscts/msui/msuiCreateClockDrivers.cc:621`.
- In the gated branch, `findDriverTerm` iterates `loadNetSet` in default pointer order at `mscts/drivers/msDrivers.cc:713`, overwrites `l_drvTerm` each pass at `mscts/drivers/msDrivers.cc:715`, inserts each driver into blessed `termSetType` at `mscts/drivers/msDrivers.cc:720`, and returns the last assigned `l_drvTerm` at `mscts/drivers/msDrivers.cc:766`.
- `termSetType` is deterministic because it is `std::set<ndmTerm*, ndmObjPtrCmpType>` from `export/ctsTypes.h:124`; the return value is the unsafe sink.

### Downstream Visibility

Some call sites are neutralized by immediately replacing the returned pointer with `getTopLevelDrvTerm(drvTerms)`, which iterates the blessed `termSetType` at `mscts/drivers/msDrivers.cc:1002` and returns a top-hier driver or the deterministic first driver at `mscts/drivers/msDrivers.cc:1010`. For example, `msClockDrivers::checkCfg` replaces `drvTerm` with `getTopLevelDrvTerm(drvTerms)` at `mscts/drivers/msAutoTapFlow.cc:1369`.

The real downstream sinks are the call sites that use the raw return before that canonicalization:

- `implementAllHtreeSections` calls `findDriverTerm` at `mscts/drivers/msAutoTapFlow.cc:4477`, gets a clock from that term at `mscts/drivers/msAutoTapFlow.cc:4478`, and collects sink/ICG terms from that clock and driver at `mscts/drivers/msAutoTapFlow.cc:4489`. Those sinks drive section segregation at `mscts/drivers/msAutoTapFlow.cc:4497`.
- Auto-section flow calls `findDriverTerm` at `mscts/drivers/msAutoTapFlow.cc:5190`, gets the clock at `mscts/drivers/msAutoTapFlow.cc:5191`, collects sink/ICG terms at `mscts/drivers/msAutoTapFlow.cc:5207`, builds a grid from `drvOnClk` and sink data at `mscts/drivers/msAutoTapFlow.cc:6244`, and evaluates tap configuration at `mscts/drivers/msAutoTapFlow.cc:6247`.
- The similar regular multisource path calls `findDriverTerm` at `mscts/drivers/msAutoTapFlow.cc:6194`, gets the clock at `mscts/drivers/msAutoTapFlow.cc:6195`, and collects sink/ICG terms at `mscts/drivers/msAutoTapFlow.cc:6211`.

The netlist mutation comes later through insertion. The principal insertion path calls `insertInsts(...)` at `mscts/drivers/msDrivers.cc:1586`, and MV-aware paths eventually call `insertInstsMVAwareForOneHier(...)` at `mscts/drivers/msDrivers.cc:8233`. Those routines insert/connect drivers and taps, so a different source driver/clock context can produce different inserted structures.

### Controls / Gating

- C++ gate: `_appOptions.enableMLPHFlow && loadNetSet && loadNetSet->size() > 1 && leafLevel` at `mscts/drivers/msDrivers.cc:712`.
- App option: `/remote/u/binghui/bin/icc2query -a cts.multisource.enable_mlph_flow` reports `cts.multisource.enable_mlph_flow`, bool, default false, status basic, scope block, persistent true.
- Code registration agrees: `initAppOption<bool>(catMultisource, "enable_mlph_flow", ..., default false, MSUI_BASIC, design)` at `mscts/msui/msuiAppOptions.cc:3991`.
- Production default: off. Source paths read the app-option value and enable MLPH only when it is set, for example `mscts/msui/msuiSynRegClkTree.cc:1802` and `mscts/msui/msuiSynRegClkTree.cc:1810`.

### Code / Regression Setting Pass

No reachable `nwtn/unit` directory was found. Local source references the option in UI and flow code, including `mscts/msui/msuiCreateClockDrivers.cc:893`, `mscts/msui/msuiCreateClockDrivers.cc:1024`, `mscts/msui/msuiSynthesizeGlobalTree.cc:532`, `mscts/msui/msuiSynthesizeGlobalTree.cc:933`, `mscts/msui/msuiSynRegClkTree.cc:1387`, and `mscts/msui/msuiSynRegClkTree.cc:1802`. No local script/regression setter for `cts.multisource.enable_mlph_flow` was found.

### Linter / Bypass Note

The function signature has `//LINTER_BYPASS` at `mscts/drivers/msDrivers.cc:702`, but the linter suppression is line-based: it skips a matching line only if that same line contains `LINTER_BYPASS`, as shown at `linter:112` and `linter:117`. The unsafe local declaration/use `std::set<ndmNet*>* loadNetSet` is at `mscts/drivers/msDrivers.cc:711` without a bypass on that line. So the signature bypass is not proof of a deliberate waiver for the local unsafe construct; it is more likely a nearby waiver for signature/type noise.

### Attribution

Unavailable. This source slice is not a Perforce client.

### Fix Direction

Prefer selecting a deterministic driver explicitly inside `findDriverTerm`, for example the lowest `ndmObjPtrCmpType`/object-id driver among `loadNetSet`, and return that while still filling `drvTerms`. This is cheap because the multi-net set is small and the loop already visits all nets. Alternatively change `_loadNetSet` to `netSetType` or `std::set<ndmNet*, ndmObjPtrCmpType>`, but that touches the member, accessor, allocation site, and iterator declarations.

## Issue #3: `get_power_taps` Returns A Tcl Collection In Hash Order

Dashboard ID: n/a
Location: `mscts/msui/msuiGetPowerTaps.cc:66`

### Verdict

Real, scoped to user-observable Tcl collection order. The command builds a `std::vector<ndmInst*>` directly from a `dosUnorderedSet<ndmBlkInst*>` and passes it to `clct_list_to_collection` at `mscts/msui/msuiGetPowerTaps.cc:887`, then returns that collection at `mscts/msui/msuiGetPowerTaps.cc:890`. I could not inspect `clct_list_to_collection` locally because `tcl/clct.h` is outside this source slice, so the claim is scoped to "the vector order passed to the collection layer is nondeterministic; no in-tree re-sort is visible."

### Evidence

- The command is registered as `get_power_taps` at `mscts/msui/msuiGetPowerTaps.cc:172` and added to the command group at `mscts/msui/msuiGetPowerTaps.cc:914`.
- The set type is `typedef dosUnorderedSet<ndmBlkInst *> blkInstSetType` at `mscts/msui/msuiGetPowerTaps.cc:66`.
- Population paths insert into `myset` and the final path iterates `for(auto inst:myset)` at `mscts/msui/msuiGetPowerTaps.cc:879`.
- The vector is passed directly to `clct_list_to_collection(CciIterUtils::container(l_ptaps), ...)` at `mscts/msui/msuiGetPowerTaps.cc:887`.
- This file already has a stable physical-order comparator `compareByOrigin` at `mscts/msui/msuiGetPowerTaps.cc:109`, but it is not applied before the collection return.

### Downstream Visibility

The sink is a Tcl recording/collection order sink. A user script can observe it through collection iteration or position-sensitive code after `get_power_taps`. The command returns a collection object with `setResult(tclResult)` at `mscts/msui/msuiGetPowerTaps.cc:890`. No downstream in-tree C++ consumer re-sorts this result.

Related below threshold: `report_power_taps` uses the same unordered set type at `mscts/msui/msuiReportPowerTaps.cc:71`, iterates a local unordered set at `mscts/msui/msuiReportPowerTaps.cc:760` and `mscts/msui/msuiReportPowerTaps.cc:1022`, then prints rows through `userOutput::printf` at `mscts/msui/msuiReportPowerTaps.cc:553`. That is report-text order only, so I keep it Low and not counted as one of the six Medium/High findings.

### Controls / Gating

No app-option gate found. The trigger is the user command `get_power_taps` and any input/design state producing more than one tap in `myset`.

### Code / Regression Setting Pass

No reachable `nwtn/unit` directory was found. No local regression setter is relevant because this is command output order.

### Attribution

Unavailable. This source slice is not a Perforce client.

### Fix Direction

Keep `dosUnorderedSet` for membership and duplicate filtering, then materialize stable order once before `clct_list_to_collection`. Sorting `l_ptaps` by object ID through the blessed comparator or by tap origin/path is an `O(n log n)` boundary cost on a user query, not an inner-loop cost. The local precedent is `ctssch/ctsPowerDrivenGateRelocator.cc:1066`, which keeps hash lookup and sorts a vector once before order-sensitive processing at `ctssch/ctsPowerDrivenGateRelocator.cc:1070`.

## Issue #4: MV-Aware Driver Insertion Ordered By Hier Address

Dashboard ID: n/a
Location: `mscts/drivers/msDrivers.cc:8120`

### Verdict

Real when the uncommitted-hierarchy input contains two or more equal-depth hierarchy roots. The defect is the default pointer-keyed `std::map<ndmHier*, msDriverLoadInfo>`, not the missing tie-break alone. The depth sort fails to repair same-depth address order.

### Evidence

- `segrigateLoadAndBufForHier` accepts and fills `std::map<ndmHier *, msDriverLoadInfo>& inputParamMap` at `mscts/drivers/msDrivers.cc:7992` and `mscts/drivers/msDrivers.cc:7998`.
- Loads are grouped by `msgtsUtil::getUncommittedHier(...)` and inserted into `inputParamMap[hier]` at `mscts/drivers/msDrivers.cc:8010` and `mscts/drivers/msDrivers.cc:8012`.
- Buffer locations are grouped by `msgtsUtil::getUncommittedHierFromLoc(...)` and inserted into `inputParamMap[hier]` at `mscts/drivers/msDrivers.cc:8111`.
- `convertToVector` drains that map in address order at `mscts/drivers/msDrivers.cc:8121` and `mscts/drivers/msDrivers.cc:8124`.
- `compareHierDepth` compares only `getDepthFromTop()` at `mscts/drivers/msDrivers.cc:8140` and `mscts/drivers/msDrivers.cc:8141`.
- `insertInstsMVAware` reverse-iterates the vector at `mscts/drivers/msDrivers.cc:8199` and calls `insertInstsMVAwareForOneHier(...)` at `mscts/drivers/msDrivers.cc:8233`.

### Downstream Visibility

`insertInstsMVAwareForOneHier` is the concrete insertion sink. The caller passes per-hier configs, locations, names, drivers, and loads at `mscts/drivers/msDrivers.cc:8233`. The subsequent common insertion code calls `insertInsts(...)` at `mscts/drivers/msDrivers.cc:8371`, which creates and connects drivers. Therefore equal-depth hierarchy order is consumed by design mutation, not just reporting.

Equal-depth condition: `-uncommitted_hierarchy_boundary` accepts multiple hierarchy names and boundaries at `mscts/msui/msuiCreateClockDrivers.cc:692`, looks up each `ndmHier` at `mscts/msui/msuiCreateClockDrivers.cc:709`, and pushes every entry into the vector at `mscts/msui/msuiCreateClockDrivers.cc:757`. Nothing in parsing rejects sibling hiers at the same `getDepthFromTop()`. The helper also explicitly chooses deepest matching hierarchy for locations at `mscts/msgts/msgtsUtil.cc:3030`, which confirms depth is an ordering dimension, not a uniqueness guarantee.

### Controls / Gating

This path runs only when `_msgtsOptions.getUncommittedBlockInfo()` is non-empty, `isLeaf` is true, and `section` is null; otherwise `insertInstsMVAware` calls `insertInstsMVAwareForOneHier` directly at `mscts/drivers/msDrivers.cc:8185`. The feature is exposed by `-uncommitted_hierarchy_boundary` parsing in `create_clock_drivers` at `mscts/msui/msuiCreateClockDrivers.cc:692` and `set_regular_multisource_clock_tree_options` at `mscts/msui/msuiSetRegMsClockTreeOptions.cc:684`.

### Code / Regression Setting Pass

No reachable `nwtn/unit` directory was found. No local regression setter for this exact equal-depth case was found. The command option is present in source at `mscts/msui/msuiCreateClockDrivers.cc:90` and `mscts/msui/msuiSetRegMsClockTreeOptions.cc:79`.

### Attribution

Unavailable. This source slice is not a Perforce client.

### Fix Direction

Do not rely on a one-line comparator only at the local map declaration; the map type is also part of function declarations at `mscts/drivers/msDrivers.h:862` and `mscts/drivers/msDrivers.h:869`, and definitions at `mscts/drivers/msDrivers.cc:7998` and `mscts/drivers/msDrivers.cc:8121`. A comparator-based fix should use a local typedef/alias and update the signatures consistently.

The smallest behavioral repair is to make `compareHierDepth` total by adding a stable final key when depths are equal, for example object ID through the blessed comparator. Cost is one extra integer/object-handle compare per sort comparison; hierarchy counts per call should be small. A comparator alias for the map is also acceptable and has no algorithmic cost, but it is not literally a one-line local declaration change.

## Issue #5: Buffer Insertion Ordered By Power-Domain Address

Dashboard ID: n/a
Location: `mscts/msmesh/msLevelBalancer.cc:1745`

### Verdict

Real when MV-aware level balancing is enabled and a node crosses an MV boundary. The per-domain load sets are disjoint, but every domain is processed from the same caller-level `node` and `driver` at `mscts/msmesh/msLevelBalancer.cc:1791`, so domain visit order can change which domain consumes earlier unique instance names and earlier legal placement sites around the same driver.

### Evidence

- `domainToLoads` is declared as `std::map<ndmPowerDomain*, TermToUnsignedMap>` with the default comparator at `mscts/msmesh/msLevelBalancer.cc:1745`.
- It is filled from deterministic `TermToUnsignedMap` load order at `mscts/msmesh/msLevelBalancer.cc:1747`, but the outer domain keys are raw pointers at `mscts/msmesh/msLevelBalancer.cc:1758`.
- It is iterated at `mscts/msmesh/msLevelBalancer.cc:1770`.
- Each domain calls `insertBuffers(...)` at `mscts/msmesh/msLevelBalancer.cc:1791`.
- The public gate into this helper is `if (getAppOptions().enableMVAwareLevelBalancing && lbNode->isCrossingMVBoundary())` at `mscts/msmesh/msLevelBalancer.cc:1835`.
- The header already uses deterministic comparators for iterated pointer maps such as `TermToUnsignedMap` at `mscts/msmesh/msLevelBalancer.h:63`, marks a non-iterated pointer map as no-comparator-needed at `mscts/msmesh/msLevelBalancer.h:69`, and defines `pdmSetType` with `ndmObjPtrCmpType` for `ndmPowerDomain*` at `mscts/msmesh/msLevelBalancer.h:70`.

### Downstream Visibility

The call chain creates real buffers:

- `insertBuffersByPowerDomain` calls `insertBuffers` per domain at `mscts/msmesh/msLevelBalancer.cc:1791`.
- `insertBuffers` calls `insertBuffersMultiDriver` at `mscts/msmesh/msLevelBalancer.cc:1906`.
- `insertBuffersMultiDriver` calls the lower-level `insertBuffers` at `mscts/msmesh/msLevelBalancer.cc:1938`.
- The lower-level function calls `insertBuffer` in a loop at `mscts/msmesh/msLevelBalancer.cc:2146`.
- `insertBuffer` calls `getInfra()->insertBuf(...)` at `mscts/msmesh/msLevelBalancer.cc:2732`, then moves the new instance through `getInfra()->moveInst(...)` at `mscts/msmesh/msLevelBalancer.cc:2768`.
- `ctsNL::insertBuf` constructs a base name at `ctsutil/ctsNL.cc:470`, and `insertInstOnNet` calls `hier->createUniqueNamedInst(...)` at `ctsutil/ctsNL.cc:281`.

So the observable is not only instance-name suffix order. Placement can also vary because each domain's inserted buffer is placed near the current driver at `mscts/msmesh/msLevelBalancer.cc:2751` and `mscts/msmesh/msLevelBalancer.cc:2768`; if legalizer choices compete around that driver, earlier domains consume earlier sites.

### Controls / Gating

- App option: `/remote/u/binghui/bin/icc2query -a cts.multisource.enable_mv_aware_level_balancing` reports bool, default false, status hidden, scope block, persistent true.
- Registration: `initAppOption<bool>(catMultisource, "enable_mv_aware_level_balancing", ..., default false, MSUI_HIDDEN, design)` at `mscts/msui/msuiAppOptions.cc:1412`.
- C++ gate: `getAppOptions().enableMVAwareLevelBalancing && lbNode->isCrossingMVBoundary()` at `mscts/msmesh/msLevelBalancer.cc:1835`.
- Flow gate: level balancing runs only for groups with a balance-level setting at `mscts/msmesh/msLevelBalancer.cc:755`.
- Related app options: `cts.multisource.level_balance_insert_near_driver` defaults true and unlisted; `cts.multisource.subtree_preprocess_insert_leaf_level` defaults false and hidden; `cts.multisource.level_balance_multi_logical_net_buffering_in_a_hier` defaults false and unlisted.

### Code / Regression Setting Pass

No reachable `nwtn/unit` directory was found. Local source serializes `-balance_levels true` when a group has level-balancing settings at `mscts/msutil/msCstrDesign.cc:1514`, and the command option is declared at `mscts/msui/msuiSetSubtreeOptions.cc:78`. No local script/regression setter for `cts.multisource.enable_mv_aware_level_balancing` was found.

### Attribution

Unavailable. This source slice is not a Perforce client.

### Fix Direction

This one is a near one-line declaration fix because the iteration uses `auto`:

`std::map<ndmPowerDomain*, TermToUnsignedMap, ndmObjPtrCmpType> domainToLoads;`

Expected cost is negligible: same `std::map`, same asymptotic behavior, just object-id comparison instead of address comparison for the small set of power domains. Validate with an MV level-balancing testcase because placement/QoR can shift when deterministic order changes.

## Issue #6: Load Connection Ordered By Block-Net Address

Dashboard ID: n/a
Location: `mscts/drivers/msDrivers.cc:3335`

### Verdict

Real. The outer map groups loads by `ndmBlkNet*` in raw address order, and that order directly drives `connectTerms` calls. The inner vectors are safe because they are filled from `termSetType`, but the outer block-net order is not.

### Evidence

- `connectUnassignedLoads` declares `std::map<ndmBlkNet*, std::vector<ndmTerm*> > nets` at `mscts/drivers/msDrivers.cc:3335`.
- It fills each vector while walking `unassignedLoads`, a `termSetType`, at `mscts/drivers/msDrivers.cc:3336` and `mscts/drivers/msDrivers.cc:3347`.
- It iterates the default map at `mscts/drivers/msDrivers.cc:3350` and calls `connectTerms(p_driver, itr1->second, string(""))` at `mscts/drivers/msDrivers.cc:3353`.

### Downstream Visibility

`msClockDrivers::connectTerms` seeds `msDrvConnOptions` from the shared `_nameCounters[prefix]` at `mscts/drivers/msDrivers.cc:10882`, passes the options to `_msInfra->connectTerms(...)` at `mscts/drivers/msDrivers.cc:10917` or `mscts/drivers/msDrivers.cc:10920`, then stores the advanced counter back at `mscts/drivers/msDrivers.cc:10923`. The lower layer calls `ndmHierRoot::incrHierConnect` at `mscts/msutil/msInfra.cc:735` or `ndmHierRoot::hierConnect` at `mscts/msutil/msInfra.cc:742`. Therefore block-net visit order changes which load group consumes the next auto-created net/port names.

### Controls / Gating

The function is specific to MLPH unassigned-load handling per the comment at `mscts/drivers/msDrivers.cc:3324`. It is called from driver-insertion paths after assignment leaves loads unconnected; no separate app option beyond those flow gates was found.

### Code / Regression Setting Pass

No reachable `nwtn/unit` directory was found. No local regression setter was found for this exact unassigned-load path.

### Attribution

Unavailable. This source slice is not a Perforce client.

### Fix Direction

Add `ndmObjPtrCmpType` to the map key and update the explicit iterator type at `mscts/drivers/msDrivers.cc:3350`, or use `auto` for the iterator. This is not strictly "one line with no use-site change" because the explicit iterator type names the old comparator-less map. Runtime cost is negligible for the small grouped-net set.

## Exclusion Checked: `ctsroute::ctsRouter` `_nets`

Location: `ctsroute/ctsRouter.h:64`

The shape is real but not reachable in this source slice. `_nets` is `std::map<ndmNet*, ctsRtNet*>` with the default comparator at `ctsroute/ctsRouter.h:64`. It is iterated in `readGR` at `ctsroute/ctsRouter.cc:270`, `writeGR` at `ctsroute/ctsRouter.cc:290`, `setRouteMode` at `ctsroute/ctsRouter.cc:315`, `setExtractMode` at `ctsroute/ctsRouter.cc:340`, `mapAllNets` at `ctsroute/ctsRouter.cc:384`, `unmapAllNets` at `ctsroute/ctsRouter.cc:400`, and `updateAllRoutes` at `ctsroute/ctsRouter.cc:444`. `updateRoute(ctsRtNet*)` does `unmapRoute`, `routeNet`, and `mapRoute` at `ctsroute/ctsRouter.cc:415`, `ctsroute/ctsRouter.cc:416`, and `ctsroute/ctsRouter.cc:417`.

Build inclusion is real: `ctsroute/Master.make:5` lists `ctsRouterInterf.cc`, `ctsroute/Master.make:6` lists `ctsRouter.cc`, and `ctsroute/Master.make:14` exports `ctsRouterInterf.h`.

Reachability is not proven. `ctsRouterInterf` is referenced only in `ctsroute/ctsRouterInterf.cc` and `ctsroute/ctsRouterInterf.h` under `/remote/us01home05/carys`; a parent sweep for `ctsRouterInterf` and `CTSRT_CTSROUTER` found no other consumer. The interface forwards only `getNumOfNets` at `ctsroute/ctsRouterInterf.cc:90`, `updateRoute` at `ctsroute/ctsRouterInterf.cc:105`, and `updateAllRoutes` at `ctsroute/ctsRouterInterf.cc:120`. It does not forward `readGR`, `writeGR`, `mapAllNets`, or `unmapAllNets`.

Verdict: `Dead/unused` within this source slice, with an export caveat. If an out-of-tree consumer constructs `ctsRouterInterf` with `CTSRT_CTSROUTER` and calls `updateAllRoutes`, this should be promoted to High because routing is congestion-coupled. I found no such consumer in the reachable parent tree.

## Verification Notes

- Source roots used: `/remote/us01home05/carys/cts` for CTS source, `/u/ranjithp/folders/coreStory/core/nd-audit-cts` for prior notes and report output.
- Required skills followed: base `prove-nd` and `prove-nd-mt`; no sub-agents or sub-tasks were used.
- `icc2query` results recorded:
  - `cts.multisource.enable_mlph_flow`: bool, default false, basic, block, persistent.
  - `cts.multisource.enable_mv_aware_level_balancing`: bool, default false, hidden, block, persistent.
  - `cts.multisource.level_balance_insert_near_driver`: bool, default true, unlisted, block, persistent.
  - `cts.multisource.subtree_preprocess_insert_leaf_level`: bool, default false, hidden, block, persistent.
  - `cts.multisource.level_balance_multi_logical_net_buffering_in_a_hier`: bool, default false, unlisted, block, persistent.
- `nwtn/unit` was not reachable at `/remote/us01home05/carys/cts/nwtn/unit` or `/remote/us01home05/carys/nwtn/unit`, so regression setter evidence is limited to local scripts/docs and source.
- ASCII check: passed (`ASCII OK`).
- Limitation: no runtime testcase was run. For Issue #1, the proposed confirmation is thread-count A/B with raw/full-precision TNS comparison. For Issues #2, #4, #5, and #6, source-level proof establishes address-ordered inputs and design-mutation sinks, but not a concrete reproduced design diff.
