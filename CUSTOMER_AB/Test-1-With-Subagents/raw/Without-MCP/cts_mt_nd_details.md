# CTS Multi-Threaded Non-Determinism Proof Details

Source dashboard: `/u/ranjithp/folders/coreStory/snps/nd-analysis/cts-nd-report.md`

Source data: `/u/ranjithp/folders/coreStory/snps/nd-analysis/findings_final.json`

## Analysis Context

- Source tree used: `/remote/us01home05/carys/cts`, a detached read-only snapshot of `nwtn/src/cts`.
- Workspace context: this is not a Perforce/viewtool client. There is no `.synmake`, no `DEVROOTS`, no `.p4config`, and `viewtool` bootstrap was intentionally skipped.
- Depot/cross-module context: local source was primary. `p4`, `/remote/u/binghui/bin/mgrep`, and `/remote/u/binghui/bin/icc2query` were used for branch-only files and app-option metadata. `util/include/crm.h` and `util/crm/crm.cc` were read from depot/cross-module output because `util/crm.h` is not in the snapshot.
- Build/runtime context: nothing was built or run. Every runtime confirmation below is an experiment design, not an executed result.
- Scope: only the MT-relevant rows named in the prompt were re-audited. Pure environment-variable variation is not counted as ND by itself; it is only recorded when it selects a different MT algorithm or path.

## Summary Table

| Issue | Location | Prior verdict | Your verdict | MT refinement | Race vs Ordering | Triggering controls / app options | Short summary |
|---|---|---|---|---|---|---|---|
| A1 | `ccd/skewopt/soSolverUpdater.cc:2100` | HIGH real | Real | Gate-inactive | Data race | More than one setup/hold scenario; raw `tbb::parallel_for_each`; no thread-count or lock gate | Confirmed. Workers structurally insert into shared solver `std::map` members through `funcsMap[scenario]`. |
| A2 | `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | HIGH real | False positive for MT ND | n/a (benign by construction) | Benign for MT; deterministic functional dedup bug remains | `_useFullyParallelLpSolver`, `_maxThreads` | Changed from real -> false positive for MT. `std::unique` is wrong because it uses pointer equality, but the source does not prove schedule-dependent survivors. |
| A3 | `ctscto/ctosc/ctoscGlobal.h:274` | HIGH real | Real | Locked-but-order-dependent | Race-free but order-dependent | `CTO_GSKEW`, `CTOSC_LOAD_PART_USE_AVG_LATE_MARGIN`, `CTOSC_LOAD_PART_USE_AVG_TARGET_LATE_MARGIN` defaults from flow state | Confirmed. Pointer hash order feeds non-associative `float` sums, then sink sorting and load partition selection. Locking would not fix this. |
| A4 | `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | MEDIUM real | Real | Locked-but-order-dependent | Race-free but order-dependent | `set_host_options -max_cores` / CRM max thread count; no local enable flag | Confirmed and broadened. Timing and sibling cost functions group floating sums by thread-count-sized ranges, then merge per-thread slots. |
| A5 | `ctssc/lazytns/ctsLazyModel.cc:4834` | MEDIUM real | Unresolved | n/a (unresolved) | Race-free algorithm selection, equivalence unresolved | `crmResources::get().getMaxThreadCount() > 32`, `ccdConfig::is_128_core()`, `ccdConfig::get_enable_runtime_improvements() > 1` | Source does not prove `doPrgTracePerScenParallel` and `doPrgTracePerScen` are equivalent; this remains a machine-dependent algorithm switch. |
| B1 | `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:312` | False positive | Neutralized | n/a (benign by construction) | Benign | `execPolicy::MultiThread`; `globalDone` atomic early-stop | Confirmed dismissal. The only first-writer effect is setting the same boolean stop flag; boolean result uses absorbing `&&`/`||`; local log order is debug-only. |
| B2 | `ctscto/ctoGrpLatCalc.cc:80` | Latent-only | False positive | n/a (benign by construction) | Benign | `_useCgLatMT`, write-lock suspend success, `std::thread::hardware_concurrency()` grainsize | Confirmed safe. Per-index output is stable; `maxLate` and `worstRatio` are local max reductions with no product witness captured. |
| B3 | `ctsutil/ctsMtTaskRunner.h:81` | Dead/unused | Dead/unused for flagged `step`; runner otherwise live | MT-unreachable | Benign | CRM max threads and TBB arena max concurrency | Confirmed. `step` is computed and clamped but never passed to `blocked_range`; callers cannot rely on it. No pooled worker state is stored. |
| B4 | `ccd/skewopt/soCG.cc` gradient functors | Dismissed | False positive | n/a (benign by construction) | Benign | Multiple `tbb::parallel_for` ranges over `_numVars` or job count | Confirmed dismissal after reading functors. Workers own output index ranges; inner job accumulation order is fixed. |
| B5 | Concurrent containers called neutralized | Neutralized | Neutralized | Canonicalized-after-join | Benign | `ccdUtil::parallel_for` and TBB concurrent containers | Confirmed. All five found containers are drained/sorted after the join and the canonicalization covers every contributor found. |
| B6 | `ctssc/ctsscUskewLimit.cc:871` | Not filed; noted no gate | Latent-only | Race-but-idempotent | Benign for product values; debug tie witnesses may vary | Unconditional `tbb::parallel_for` over `sinkTerms` | Reclassified as latent-only. Numeric constraints are reduced into stable maps/value reductions; only debug min/max term names can vary on exact ties. |
| C1 | `ctssc/lazytns/ctsLazyModel.cc:2520` | Latent-only, unresolved duplicate fact | Unresolved | n/a (unresolved) | Race-free but order-dependent if duplicate equal-key entries exist | `ccdConfig::is_ccd_enable_lazy_tns_runtime_improvement() & 0x2` | Still unresolved. `LPKEY` includes path-group id, but I did not find a uniqueness invariant for duplicate `(LPKEY, D-node)` payloads. |

## Issue A1: Shared CG Solver Log-Sum-Exp Map Insertion

Location: `ccd/skewopt/soSolverUpdater.cc:2100`

### Verdict

Confirmed `Real`, MT refinement `Gate-inactive`. This is a data race, not merely order-dependent behavior. The code directly mutates shared `soCgSolver` maps from TBB workers; a lock would be a valid race fix, but would not by itself prove deterministic insertion order for later consumers.

### Evidence

`soCgSolverUpdater::addLogSumExpFuncsToSolver()` builds scenario vectors and calls `tbb::parallel_for_each` over setup scenarios and hold scenarios. Each worker calls `updateInfo::addLogSumExpFuncsToSolver()`, which calls `solver->addLogSumExpFunc(...)`. In `soCgSolver::addLogSumExpFunc()`, `funcsMap` is a reference to `_setupLogSumExpFuncs` or `_holdLogSumExpFuncs`, and `funcsMap[scenario]` structurally inserts into a shared `std::map<cstrScenario, soCgEpLogSumExpFuncMapType>`.

The sibling code around `soSolverUpdater.cc:2147` is a correct contrast: `ccdUtil::parallel_for` writes per-index `scenarioLogSumExpStartPointFuncs[i]`, then a serial post-join loop calls `solver->updateLogSumExpStartPointFunc(...)`.

### MT Reachability

Parallel dispatch site: `tbb::parallel_for_each(setupScenarios, ...)` and `tbb::parallel_for_each(holdScenarios, ...)` in `soCgSolverUpdater::addLogSumExpFuncsToSolver()`. Work binding is TBB dynamic/work-stealing over scenario vectors.

### Race vs Ordering

Outcome: Data race. Concurrent `std::map::operator[]` insertions into the same red-black tree are undefined behavior. Locking can fix the race; deterministic merge order still needs a stable post-join merge if later iteration order matters.

### Gate Audit

1. Thread-count gate: none found around the raw `tbb::parallel_for_each`; 2. commented-out lock: no lock in the guarded region; 3. compiled-out lock: no `#if` or lock macro neutralizer; 4. no-op default argument: no lock API; 5. two locks sharing one name: no lock; 6. released before mutation: no lock; 7. double-checked locking: none; 8. determinism option reachability: no option reaches this dispatch.

### Downstream Visibility

The solver later iterates `_setupLogSumExpFuncs` and `_holdLogSumExpFuncs` in objective/gradient setup. A lost, corrupt, or misbucketed scenario changes the CG objective and can also crash on map traversal. The observable sink is the skew solution and committed clock latency/QoR, with crash as a second sink.

### Controls / Gating

Triggered when there is more than one setup or hold scenario. I found no app option, CRM thread-count check, write-lock fallback wrapper, or single-thread branch at the dispatch site.

### Code / Regression Setting Pass

Local source search covered `_setupLogSumExpFuncs`, `_holdLogSumExpFuncs`, `addLogSumExpFunc`, `parallel_for_each`, `mtSpinMutex`, and lock spellings in `ccd/skewopt`. No production setter or option neutralizer was found.

### Attribution

Prior report attribution points to CL `13914296` for the unguarded insertion refactor. I did not re-run full annotate for this proof pass; local source text matched the reported site.

### Fix Direction

Prefer the existing per-scenario-vector idiom: have each worker fill a slot keyed by scenario index, then merge into the solver serially in `getSolverScenarios()` order. A coarse mutex around `addLogSumExpFunc()` is the smallest race fix but serializes a hot solver path and still leaves insertion order dependent on arrival if pointer-like keys are ever introduced below it.

### Runtime Confirmation

Race confirmation: run a TSAN build on a multi-scenario skewopt case and stress `addLogSumExpFuncsToSolver()`. Ordering/result confirmation: A/B one thread vs N threads, then N vs N, and diff solver log-sum-exp scenario bucket counts and final clock latencies with full precision.

## Issue A2: Fmax Redundant-Path Dedup

Location: `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127`

Changed from: HIGH real -> False positive for MT ND.

### Verdict

The `std::unique` call is a real functional bug candidate, but I do not find the MT nondeterminism proof claimed by the prior audit. Verdict is `False positive` for MT ND, refinement `n/a (benign by construction)`, because the evidence shows no schedule-dependent nondeterminism is produced rather than a transient ND value being canonicalized.

### Evidence

`pathVector` is `std::vector<const I2V*>` inside `TimingRelationContainerLightVectorBased`. `ConstraintComparatorNew` compares the dereferenced `I2V` content by variable index and coefficient. The following `std::unique(pathVector.begin(), pathVector.end())` uses pointer equality, so equal-valued constraints at different addresses are not deduped.

The parallel merge uses fixed ranges by thread index. Each worker writes its own `fragmentedContainers[threadIndex]`; the merge loops `outerIndex = 0..numberOfThreads-1`; the final container is filled by deterministic `rangeStart[threadIndex]`. Then `removeRedundantPathsParallel()` sorts each endpoint vector by value before the faulty unique.

### MT Reachability

Parallel dispatch sites: the two `tbb::parallel_for(size_t(0), numberOfThreads, ...)` phases in `mergeViolatedPathsOfSolutionsParallel()`, and the later `tbb::parallel_for` in `removeRedundantPathsParallel()`. Work binding is static by computed ranges and endpoint modulo, not first-idle completion order.

### Race vs Ordering

Outcome: Benign for MT. I found no data race and no schedule-dependent survivor. The bug is that duplicates remain, not that different runs choose different duplicates.

### Gate Audit

1. Thread-count gate: live through `_maxThreads`; 2. commented-out lock: none cited; 3. compiled-out lock: none; 4. no-op default argument: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: no determinism option cited or needed for the dismissal.

### Downstream Visibility

Duplicate paths can flow into violated path evaluation and cost functions, so the functional bug may overcount work or constraints. That is deterministic for a fixed input and thread count in the source I read.

### Controls / Gating

Requires `_useFullyParallelLpSolver` and path vectors with more than one entry. `_maxThreads` comes from `crmResources::get().getMaxThreadCount()`.

### Code / Regression Setting Pass

Read `fmaxLpModel.h`, `fmaxTimingCostFunction.h`, and `fmaxLpSolverIncremental.cc`. No test or option source proving a thread-schedule permutation was found.

### Attribution

Attribution not re-resolved. Prior audit attributed this area to the incremental fmax LP implementation; local source confirms the relevant code.

### Fix Direction

Use `std::unique(pathVector.begin(), pathVector.end(), value_equal)` after the value sort, or store constraints in a value-comparator set before vectorizing. Cost is linear after an existing sort and should be negligible compared with slack evaluation.

### Runtime Confirmation

Functional confirmation: instrument `pathVector` before/after sort and unique, count equal-valued but pointer-distinct adjacent entries. MT confirmation: run 1 vs N and N vs N with full path-vector checksums per endpoint. If checksums are stable while duplicate counts remain, this is not MT ND.

## Issue A3: `sclkCornerHash` Floating Sum

Location: `ctscto/ctosc/ctoscGlobal.h:274`

### Verdict

Confirmed `Real`, refinement `Locked-but-order-dependent`. The important point is the MT distinction: this is race-free ordering nondeterminism. Locking the maps would not fix it because the result varies with the order of `float` accumulation.

### Evidence

`sclkCornerHash` hashes `ctoSclkBag*` using `std::hash<ctoSclkBag*>()`. `_sinkDelayMapBySclk` and `_sinkDelayTargetMapBySclk` are unordered maps using that hash. `getAvgWeightedLateMargin()` and `getAvgWeightedLateTargetMargin()` iterate those maps and do `margins[sink] += (lmargin * weight)` and `weights[sink] += weight`. The averages become `avgLateMargins` / `avgLateTargetMargins`, which are used as `std::sort(_sinks...)` keys. The sorted prefix is copied into a buffered load group in `findRealBoundaryByPortPunchAnalysis()`.

### MT Reachability

Parallel context: this code is in MTCTO GLS buffering (`ctomtBuffer`), with `ctomtGlsProblemGenerator` and `ctomtGlsLevelFlow` feeding MTCTO xform problems. The source read proves the function is in the MTCTO product path and also proves the hash-order issue without relying on concurrency. I did not prove a direct parallel dispatch around `ctoscLoadPartition::init()` from this snapshot, so the extra MT scheduling source remains less certain than the hash-order source. Work binding for the proven issue is unordered-map bucket order, not worker order.

### Race vs Ordering

Outcome: Race-free but order-dependent. Non-associative `float` addition changes the numeric value when term order changes. Locking cannot fix this; only a deterministic accumulation order or deterministic keying can.

### Gate Audit

1. Thread-count gate: no thread-count gate neutralizes the hash iteration; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: no option reaches this accumulation order.

### Downstream Visibility

The value is compared as a raw `float` sort key, not a rounded report field. Precision trap: confirmation must compare raw `float` bits or print with `%a` / full precision; a fixed decimal report can hide the difference. The sink is load grouping for buffer insertion.

### Controls / Gating

`ctomtBuffer` sets `useAvgLateMargin` when flow type is `CTO_GSKEW` and `CTOSC_LOAD_PART_USE_AVG_LATE_MARGIN` defaults from `isSolverAugLeafOnly()`. It sets `useAvgTargetLateMargin` when advanced skew opt is active and `CTOSC_LOAD_PART_USE_AVG_TARGET_LATE_MARGIN` defaults from `isAdvancedSkewOpt()`.

### Code / Regression Setting Pass

Read `ctoscGlobal.h`, `ctoscLoadPartition.cc`, and `ctomtBuffer.cc`. Other `sclkCornerHash` containers were checked as lookup-only or not part of this proven sum.

### Attribution

Prior report attributes `sclkCornerHash` to CL `7023073`. I did not re-run annotate; local source confirms the same functor and consumers.

### Fix Direction

Best fix: hash by stable `sclkCornerType` IDs instead of bag address, preserving `unordered_map` lookup cost. Alternative: snapshot keys and sort once before the two accumulations. The snapshot cost is `O(S log S)` for SCC count, usually small; QoR needs validation because stable order will not match the old arbitrary order.

### Runtime Confirmation

Run the same MTCTO GLS skew-opt design with 1 vs N and N vs N. Dump per-sink weighted margin raw bits before sorting `_sinks`, then dump `_sinks` order and buffered group membership. Do not rely on rounded timing reports.

## Issue A4: Fmax Timing Cost Thread-Grouped Reductions

Location: `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277`

### Verdict

Confirmed `Real`, refinement `Locked-but-order-dependent`. This is race-free but the arithmetic grouping depends on `numberOfThreads`.

### Evidence

`evaluateTnsAndWnsParallel()` asserts `numberOfThreads > 1`, splits relations with `calculateRanges(relations, numberOfThreads)`, accumulates `resultsPerThreadTNS[threadCount]`, then serially adds slots in thread-index order. The sibling methods at the previously unread sites follow the same shape: `evaluateTnsFull` around `:436`, top-300/non-top timing around `:667`, and WNS around `:1213`. The four `.cc` siblings (`fmaxBufferCountCostFunction.cc`, `fmaxPiecewiseLinearCostFunction.cc`, `fmaxSkewSumCostFunction.cc`, plus constructor/range setup in `fmaxTimingCostFunction.cc`) also use per-thread partial vectors and serial slot merges.

`calculateRanges()` uses total path count divided by `threadCount`, so changing max cores changes range boundaries and therefore floating-point grouping.

### MT Reachability

Parallel dispatch site: `tbb::parallel_for(size_t(0), numberOfThreads, size_t(1), ...)` in timing and sibling cost evaluators. Work binding is static by range index; this makes N vs N likely stable, but 1 vs N or N1 vs N2 changes arithmetic grouping.

### Race vs Ordering

Outcome: Race-free but order-dependent. There is no shared write race in the per-thread slots. Locking cannot fix the thread-count grouping; only stable partitioning or stable merge semantics can.

### Gate Audit

1. Thread-count gate: live via `_maxThreads`; depot CRM shows reset default sets max threads to 1 unless host options/EAM set more, but fmax stores `_maxThreads` from CRM; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: no determinism option reaches the reductions.

### Downstream Visibility

Returned TNS/WNS/cost values drive solver validity, ranking, and path lists. WNS witness path on exact ties is selected by thread-index merge order. Precision trap applies: compare raw returned floats/doubles, not fixed precision log lines.

### Controls / Gating

`fmaxLpSolver` initializes `_maxThreads` from `crmResources::get().getMaxThreadCount()`. Depot CRM code shows host options default `NO_LIMIT=0`, while `resetGlobalOptions()` forces `setMaxThreadCount(1)` unless EAM or host options set a larger value.

### Code / Regression Setting Pass

Read the main header sites and `.cc` sibling cost functions. No app-option setter was found to force a deterministic partition independent of max cores.

### Attribution

Attribution not re-resolved. The implementation is in the fmax LP cost-function family.

### Fix Direction

Do not force a fully sequential reduction in this hot path. Use stable chunks independent of thread count, for example fixed endpoint/path block IDs, compute block partials in parallel, then reduce blocks in block-id order. This preserves parallel evaluation and severs arithmetic from `-max_cores`.

### Runtime Confirmation

Run a fixed fmax testcase with `-max_cores 1` and `-max_cores N`, then N vs N. Dump TNS/WNS/cost as hex floats and record WNS witness IDs. A 1-vs-N difference confirms thread-count grouping; an N-vs-N difference would indicate an additional scheduling source.

## Issue A5: Lazy-TNS PRG Trace Algorithm Switch

Location: `ctssc/lazytns/ctsLazyModel.cc:4834`

### Verdict

`Unresolved`, refinement `n/a (unresolved)`. This is a thread-count-dependent algorithm switch, not a `Gate-inactive` lock/guard problem, and source alone does not prove the serial and parallel algorithms produce identical results.

### Evidence

`doPrgTrace()` chooses `doPrgTracePerScenParallel()` only when `maxThreads > 32`, there is more than one candidate, and `disableParallelPrgTrace` is false. The serial branch writes `_scenariosToPrgGraphs[st]`, runs `operatePrgGraph(pG)`, clears the ep map, then immediately calls `populatePrgPath()`, `addExtraCostEp()`, and `dumpPrgGraph()`. The parallel branch builds local graphs, sets `pG.setEnablePrgAnalysis(false)`, runs `operatePrgGraph()`, calls `populatePrgPath()` in the worker, stores `extraClocks`, then serially dumps and adds extra EPs in `mergePrgTraceResult()`.

These are similar, but not textually equivalent. I could not prove `operatePrgGraph()` and `populatePrgPath()` are side-effect equivalent in the two contexts from the CTS snapshot.

### MT Reachability

Parallel dispatch site: `ccdUtil::parallel_for(size_t(0), candidates.size(), ...)` inside `doPrgTrace()`. Work binding is by candidate index, likely static within the wrapper, with result merge in candidate order.

### Race vs Ordering

Outcome: Race-free algorithm selection, equivalence unresolved. If the algorithms differ, locking is irrelevant; this is a different-answer path, not a data race.

### Gate Audit

1. Thread-count gate: live and selects `maxThreads > 32`; 2. commented-out lock: none cited; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: write lock is suspended before the branch and resumed after, not a determinism neutralizer; 7. double-checked locking: none; 8. determinism option: no determinism option forces one algorithm for reproducibility.

### Downstream Visibility

`populatePrgPath()` updates cost endpoints; `addExtraCostEp()` changes the model; PRG dumps differ if graph content differs. This can affect lazy TNS costs and solver choices, but I did not prove a concrete divergence.

### Controls / Gating

Controls are `crmResources::get().getMaxThreadCount() > 32`, `candidates.size() > 1`, `ccdConfig::is_128_core()`, and `ccdConfig::get_enable_runtime_improvements() > 1`.

### Code / Regression Setting Pass

Read `ctsLazyModel.cc`, `ctsLazyTnsModel.h`, `ctsLazyCostGroup.cc`, and `ctsLazyCostEp.cc`. External `operatePrgGraph()` behavior was not available in the snapshot.

### Attribution

Attribution not re-resolved. The parallel path comments are dated April 2026 in local source.

### Fix Direction

Either prove equivalence with an invariant/regression, or make the algorithm choice an explicit deterministic option independent of machine core count. If parallel stays, keep result merge by candidate order and audit `populatePrgPath()` for shared model writes.

### Runtime Confirmation

Run the same testcase with `-max_cores 32` and `-max_cores 33`, then repeat 33 vs 33. Diff per-endpoint traced-path sets, extra EP IDs, and final TNS at full precision. Add temporary checksums before and after `mergePrgTraceResult()`.

## Issue B1: `runSccIteration` Atomic Early Stop

Location: `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:312`

### Verdict

Confirmed prior dismissal as `Neutralized`, refinement `n/a (benign by construction)`. No normative refinement applies because the absorbing boolean reduction produces no product nondeterminism; `Race-but-idempotent` would imply the `Latent-only` base label, which is not the verdict here.

### Evidence

`sccEvalResult` is `{ bool value; std::string localLog; }`. `done(init)` is `value != init.value`. `reduceOr` combines values with `||`; `reduceAnd` combines with `&&`; both concatenate `localLog`. In users at `evalGskewBuffering()`, `evalGskewNotBuffering()`, and `evalGlate()`, the boolean result is the only product decision. `localLog` is printed only through `tmctomtGlsGeneratorDetail`.

### MT Reachability

Parallel dispatch site: `tbb::parallel_reduce(tbb::blocked_range<size_t>(0, n), ...)` in `runSccIteration()`. Work binding is TBB dynamic/work-stealing, with possible early drops after `globalDone` becomes true.

### Race vs Ordering

Outcome: Benign. Dropped operands cannot change an OR after true or an AND after false. The log concatenation order is order-dependent but debug-only.

### Gate Audit

1. Thread-count gate: `execPolicy::MultiThread` is the gate and is live when caller selects it; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: relaxed atomic is sufficient for a performance early-stop hint because correctness follows from absorbing booleans; 8. determinism option: no option cited.

### Downstream Visibility

The product boolean is stable. Only debug trace text can vary in order or completeness.

### Controls / Gating

Controlled by the caller's `execPolicy` and SCC count.

### Code / Regression Setting Pass

Read the state, reducer, dispatch, and all local call sites returned by `rg runSccIteration`.

### Attribution

Not re-resolved; no fix recommended.

### Fix Direction

None for product determinism. If debug log reproducibility matters, collect per-SCC log slots and print in SCC index order after the join.

### Runtime Confirmation

Run MultiThread vs MultiThread with verbose detail on and off. Product booleans should match; debug log line order/count may differ after early stop.

## Issue B2: `ctoGrpLatCalc` Grainsize And Max Ratchets

Location: `ctscto/ctoGrpLatCalc.cc:80`

### Verdict

Confirmed safe; verdict `False positive`, refinement `n/a (benign by construction)`. No canonicalization pass is involved; the MT computation is fixed by construction through per-index output and order-independent local max reductions.

### Evidence

`_step = jobSize/numT + 1` is used as the TBB grainsize in `calcGrpLatencyBatch()`. The body writes `grpLat[i]` by original index. In nested per-term MT, `maxLate` and `worstRatio` are local variables in `getClockGroupLatencyPerSccPerTermMt()`, protected by a local `mtSpinMutex`, and no witness term is captured.

Operand provenance: `thisMaxLate` comes from `phase + arrival` for the current term; `ratio` comes from the current `ctoCGLat`; `late` is the current call input. No operand derives from a prior work item or unreset member. Boundary reset: the ratchet variables are locals, so entry/exit reset is automatic. Accessor sweep found `_step` as the only member involved and it is not the ratchet value.

### MT Reachability

Parallel dispatch sites: `tbb::parallel_for(tbb::blocked_range<size_t>(0, idx.size(), _step), ...)` and nested `tbb::parallel_for(tbb::blocked_range<size_t>(0, terms.size(), 1), ...)`. Work binding is TBB range scheduling; output is indexed.

### Race vs Ordering

Outcome: Benign. Max of values without witness is order-independent, and per-index output removes scheduling order.

### Gate Audit

1. Thread-count gate: `_useCgLatMT && idx.size() >= 2`, live when set; 2. commented-out lock: no commented lock in mutation region; 3. compiled-out lock: none; 4. no-op default lock: `mtSpinMutex` has explicit lock/unlock; 5. two locks: local lock object only; 6. released before mutation: unlock follows updates; 7. double-checked locking: none; 8. determinism option: no option neutralizer cited.

### Downstream Visibility

`grpLat[i]` values are deterministic for the same inputs. Debug printing order can vary but is lock-serialized text only.

### Controls / Gating

`_useCgLatMT`, `_perTermMt`, write-lock suspend success, and `std::thread::hardware_concurrency()` for `_step`.

### Code / Regression Setting Pass

Read `ctoGrpLatCalc.cc` and `ctoGrpLatCalc.h`; swept `_step`, `maxLate`, and `worstRatio` locally.

### Attribution

Not re-resolved; no product fix recommended.

### Fix Direction

No determinism fix needed. If keeping `_step`, consider basing it on CRM/TBB arena instead of raw hardware concurrency for consistency, but that is performance policy rather than ND.

### Runtime Confirmation

Run 1 vs N and N vs N, diff `grpLat` by index and raw float. Instrument `maxLate`/`worstRatio` if a tie-witness report is ever added.

## Issue B3: `ctsMtTaskRunner` Unused `step`

Location: `ctsutil/ctsMtTaskRunner.h:81`

### Verdict

Confirmed `Dead/unused` for the flagged value, refinement `MT-unreachable`. `step` never reaches `blocked_range`, so it cannot affect partitioning or determinism.

### Evidence

`doParallelFor()` computes `numT` from `min(crmResources::get().getMaxThreadCount(), tbb::this_task_arena::max_concurrency())`, computes and clamps `step`, then calls `tbb::parallel_for(tbb::blocked_range<iterator_type>(begin, end), ...)` without the grainsize argument.

Other uses of `ctsMtTaskRunner` in `ctoFlowMgr.cc`, `ctoSclkMgr.cc`, `ctomtGlsProblemGenerator.cc`, `ctoGrpLatCalc.cc`, and `msELCPUtil.cc` create a fresh runner around a container reference. The class stores no pooled worker state, so the worker-carryover pattern is absent.

### MT Reachability

Parallel dispatch sites: `doParallelFor()` and `doParallelForEach()` are live shared utilities. Work binding is TBB range scheduling or TBB `parallel_for_each`. The flagged `step` itself is not bound to workers.

### Race vs Ordering

Outcome: Benign. The unused local has no observable effect.

### Gate Audit

1. Thread-count gate: computed but discarded for grainsize; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: no; 5. two locks: each call creates an `ndmDesignWriteLock`; 6. released before mutation: write lock is suspended before parallel callback by design; 7. double-checked locking: none; 8. determinism option: no option cited.

### Downstream Visibility

No downstream value can observe `step`. Callers may observe TBB default partitioning, but not the intended custom step.

### Controls / Gating

CRM max threads, TBB arena max concurrency, and write-lock suspend fallback to serial.

### Code / Regression Setting Pass

Read `ctsMtTaskRunner.h` and swept all `ctsMtTaskRunner` uses in the snapshot.

### Attribution

Not re-resolved.

### Fix Direction

Delete `step` or pass it as `blocked_range(begin, end, step)` if callers really need coarser deterministic chunks. Passing it may affect load balance and should be benchmarked on current callers.

### Runtime Confirmation

Instrument `blocked_range::grainsize()` or callback range lengths before/after any fix. Verify caller outputs are unchanged and runtime does not regress.

## Issue B4: `soCG.cc` Gradient Functors

Location: `ccd/skewopt/soCG.cc`

### Verdict

Confirmed dismissal as `False positive`, refinement `n/a (benign by construction)`. No canonicalization pass is involved; the float accumulation sequence for each output index is fixed over job order.

### Evidence

The functors `parallelTnsGradAdd`, `parallelIOTnsGrad`, `parallelHoldTNSGrad`, `parallelWnsGradAdd`, and `parallelWnsPerPgGradAdd` all parallelize over output index ranges. Inside each output index, they loop jobs in ascending `j` order and add job contributions. Higher-level `logSumExpGradFuncTNSMt`, `logSumExpGradFuncWNSMt`, and `logSumExpGradFuncWNSPerPgMt` run jobs in parallel, then merge job results serially in vector index order or `std::map` key order.

### MT Reachability

Parallel dispatch sites: TBB loops over `logSumExpTNSJobs.size()`, `logSumExpWNSJobs.size()`, and `blocked_range<size_t>(0, _numVars)`. Work binding is range-based; each output index is written by one worker per functor invocation.

### Race vs Ordering

Outcome: Benign. No two workers accumulate into the same `grads[i]` in the same functor call, and per-index job order is fixed.

### Gate Audit

1. Thread-count gate: live through the solver MT path; 2. commented-out lock: none cited; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: none.

### Downstream Visibility

Gradients and log-sum-exp values are product-visible, but the source proves their merge order is stable for these functors.

### Controls / Gating

Solver MT gradient path and objective flags such as asymmetric IO/hold and WNS-per-PG.

### Code / Regression Setting Pass

Read declarations near the top of `soCG.cc`, the MT gradient functions, and the functor `operator()` bodies at the end of the file.

### Attribution

Not re-resolved.

### Fix Direction

No fix needed for these functors. Preserve the output-index partitioning pattern if adding new gradient kernels.

### Runtime Confirmation

Run N vs N with checksums of `grads[]` and per-job partials. A mismatch would point outside these functors, likely job construction or earlier shared state.

## Issue B5: Concurrent Containers With Canonicalization

Location: multiple sites

### Verdict

Confirmed `Neutralized`, refinement `Canonicalized-after-join`.

### Evidence

Five containers were found and checked:

| Site | Container | Canonicalizer | Coverage result |
|---|---|---|---|
| `ccd/ctsccd/fmax/fmaxCgSolver.cc:452` | `allCorners` concurrent set | Copy to `std::set<cstrCornerId>` | Covers all inserted corners before `initClockPathIfNotExist()`. |
| `ccd/ctsccd/fmax/fmaxCgSolver.cc:453` | `allDPaths` concurrent set | Helper copies to vector and `std::sort`s | Covers all D paths before `md.addClockPath()`. |
| `ccd/ctsccd/fmax/fmaxCgSolver.cc:454` | `allQPaths` concurrent set | Same helper | Covers all Q traced and lazy paths before `md.addClockPath()`. |
| `ccd/skewopt/soSolverUpdater.cc:1953` | `clustersToTrace` concurrent vector | Drained into `std::set<unsigned>` | Covers every pushed cluster before scheduling non-overlap rounds. |
| `ctssc/lazytns/ctsLazyCostGroup.cc:914` | `allDsSet` concurrent set | Copy to vector, `std::sort`; Q vectors sorted too | Covers all jumped D nodes before `_jumpDs` and job creation. |

### MT Reachability

Parallel dispatch sites are the surrounding `ccdUtil::parallel_for` or `tbb::parallel_for` loops. Work binding varies by TBB scheduling, but consumption happens only after the join through sorted/set order.

### Race vs Ordering

Outcome: Benign. The transient insertion order is not observed.

### Gate Audit

1. Thread-count gates: the sites are live MT sites; 2. commented-out lock: none used as neutralizer; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: no option controls the canonicalizers; they are unconditional before consumption.

### Downstream Visibility

Downstream consumers see sorted corners, sorted path tuples, sorted cluster IDs, or sorted D-node IDs. No partial contributor subset was found.

### Controls / Gating

Normal fmax CG, skewopt cluster update, and lazy-TNS jumped-D collection MT paths.

### Code / Regression Setting Pass

Searched for `concurrent_vector`, `concurrent_unordered`, and the deterministic-order comments. Read every listed producer and consumer boundary.

### Attribution

Not re-resolved.

### Fix Direction

No determinism fix required. Keep the canonicalization adjacent to the first consumer; moving it earlier into workers would risk partial coverage.

### Runtime Confirmation

Add checksums after each canonicalizer and compare N vs N. Also compare the raw concurrent-container iteration order to prove the checksum is independent of insertion order.

## Issue B6: Max Useful-Skew Initial Limit MT Collection

Location: `ctssc/ctsscUskewLimit.cc:871`

### Verdict

Reclassified as `Latent-only`, refinement `Race-but-idempotent`. The path is definitely MT and has no thread-count gate, but the product values are not order-dependent in the source I read.

### Evidence

The `tbb::parallel_for` over `sinkTerms` writes thread-local `clockInitUskewInfo` objects. The serial merge inserts per-term data into `std::map<tccKey, ...>`, builds median value vectors, and merges min/max values. `calculateMedianLatency()` uses `nth_element`, which selects by value, not insertion order. `minTerm`/`maxTerm` witnesses can depend on tie order, but they are only printed under `tmsgMaxUskewDebug`.

Operand provenance: min/max operands are current sink arrivals and CCD delay points read in the same work item. Boundary reset: all per-thread objects and aggregate variables are local to the clock/corner loop; no accessor-managed member ratchet was found.

### MT Reachability

Parallel dispatch site: `tbb::parallel_for(tbb::blocked_range<size_t>(0, sinkTerms.size()), ...)`. Work binding is TBB range scheduling into `mtmsThreadDataHolder` per-thread storage.

### Race vs Ordering

Outcome: Benign for product values. Debug-only tie witnesses may be race-free order-dependent; locking cannot make a tie witness deterministic unless a stable tie-break is added.

### Gate Audit

1. Thread-count gate: none at this dispatch; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: no lock neutralizer; 5. two locks: none; 6. released before mutation: no lock; 7. double-checked locking: none; 8. determinism option: no option reaches this path.

### Downstream Visibility

Product constraints use `minLatency`, `maxLatency`, `medianLatency`, and skew-group value maps. Debug output can print different min/max term names on exact ties.

### Controls / Gating

Runs when initial max useful-skew limit collection reaches this function and `sinkTerms` is non-empty.

### Code / Regression Setting Pass

Read the parallel body, merge loop, median calculator, skew-group merge, and print helpers.

### Attribution

Not re-resolved.

### Fix Direction

No QoR fix needed unless debug reproducibility is required. If it is, add a stable term-ID tie-break to the `elrfReplaceValueIf*` witness selection.

### Runtime Confirmation

Run N vs N with debug off and compare `_termClkCornerLimitMap` / `_clkCornerMinMaxLatencyMap` raw values. With debug on, create equal-latency ties and diff printed min/max term names.

## Issue C1: Lazy-TNS `LPKEY` Concurrent Drain

Location: `ctssc/lazytns/ctsLazyModel.cc:2520`

### Verdict

Still `Unresolved`, refinement `n/a (unresolved)`. `Partially-canonicalized` would assert a proven skipped subset; here the duplicate equal-key subset itself is unproven, so no normative refinement applies yet.

### Evidence

`LPKEY` is `(cstrScenario, unsigned pgId, grNodeId qid)`. The concurrent path fills `concurrentLpMap`, then creates a sorted `std::map<LPKEY, std::multimap<grNodeId, costEp*>> lpMap` by parallelizing over the outer keys. Each worker iterates `localConcurrentLpMap[*key]` and emplaces into an inner `std::multimap` keyed by D-node id.

The insertion sites show `costEp::collectLazyPathForTracing()` uses `_scen`, `_pgId`, and Q ID for `LPKEY`, then inserts `_node.getId()` and `this`. That makes differing path-group IDs separate keys. However, `costGroup::_allEps` is a multimap by D node, `addExtraEp()` can add another `costEp*` for the same node, and I did not find an invariant that forbids duplicate `(scenario, pgId, qid, D-node)` entries with different `costEp*` payloads.

### MT Reachability

Parallel dispatch sites: `costGroup::collectLazyPathForTracing(concurrentLpMap&)` parallelizes over primary EPs, and `lazyTnsModel::upfrontLazyPathTracing()` parallelizes over `keyVec` at the drain. Work binding is TBB index scheduling; inner concurrent multimap iteration order is not proven stable.

### Race vs Ordering

Outcome: Race-free but order-dependent if duplicate equal-key entries exist. Locking cannot fix equal-key insertion-order dependence; a stable secondary key is required.

### Gate Audit

1. Thread-count gate: controlled by `ccdConfig::is_ccd_enable_lazy_tns_runtime_improvement() & 0x2`; 2. commented-out lock: none; 3. compiled-out lock: none; 4. no-op default lock: none; 5. two locks: none; 6. released before mutation: none; 7. double-checked locking: none; 8. determinism option: no option proves duplicate handling.

### Downstream Visibility

`lpMap` feeds `traceLazyPaths()`, which creates one trace/update job per LPKEY and inner endpoint map. Equal D-node ordering can affect job payload ordering if duplicates are semantically distinct.

### Controls / Gating

Enabled by lazy-TNS runtime improvement bit `0x2`.

### Code / Regression Setting Pass

Read `ctsLazyModel.cc`, `ctsLazyCostEp.h/.cc`, and `ctsLazyCostGroup.cc` insertion sites. The missing evidence is a uniqueness invariant for `(LPKEY, D-node)` after `addExtraEp()` and sleep/woken EP creation.

### Attribution

Not re-resolved.

### Fix Direction

If duplicates are possible, drain the inner concurrent multimap into a vector and sort by `(D-node id, costEp id, capture clock id, path-group id)` before emplacing, or change the inner key to include the stable secondary identity. Cost is per LPKEY and should be small compared with tracing.

### Runtime Confirmation

Add a debug assertion while draining: for each LPKEY, record duplicate D-node entries and print path-group id, costEp id, and capture clock id. Run 1 vs N and N vs N. If duplicates appear, diff traced-path job payloads.

## Determinism-Option Audit

The sweep searched `NdFix`, `deterministic`, `reproducib`, `sort.*libs`, and `use_.*_to_sort`, then queried options with `icc2query`.

| Option | Metadata | Source reach | Verdict |
|---|---|---|---|
| `cts.optimize.use_module_name_to_sort_libs` | bool, default `false`, hidden, block persistent | `ctsUtils::sortModulesByName()` returns immediately when false; `sortModulesByLongKey()` and ctomt size/removal/reloc sites choose name tie-break only when true | Inert by default. This is the known determinism option whose fix does not engage unless users opt in. |
| `cts.compile.enable_deterministic_estimation` | bool, default `true`, unlisted, deprecated | Initialized true; if false, `shell.common.enable_deterministic_mode > 0` can force it true | Effective by default for the ICG estimator reference found. Not an inactive determinism fix. |
| `shell.common.enable_deterministic_mode` | enum, default `0`, basic, global | Cascades to `_enableDeterministicEstimation`, `_repeaterSelectionFix`, and `_cleanupZbufCache` only when those local booleans are false | No accepted-but-ignored CTS branch found in this pass; cascade is partial by design and not a CTS-specific inert option. |

No other CTS determinism-related app option with the same "accepted but ineffective" shape was found in this snapshot.

## Verification Notes

- Files read included the two requested prior-audit files and local CTS source around every scoped site.
- Tools used: `ReadFile`, `rg`, `p4 print`, `/remote/u/binghui/bin/mgrep`, and `/remote/u/binghui/bin/icc2query`.
- Source roots used: `/remote/us01home05/carys/cts` and branch/depot reads under `/remote/swefs/PE/products/dgplt/main/clientstore/dgplt_main/nwtn/src` / `//synopsys/nwtn/main/dev/nwtn/src`.
- Shell note: login `tcsh -l` / `csh -l` was rejected by this host shell, so commands were run with `/bin/tcsh -c` while keeping csh-compatible syntax.
- ASCII check: passed. `rg '[^\x00-\x7F]' /u/ranjithp/folders/coreStory/snps/nd-analysis/cts_mt_nd_details.md` found no matches.
- Second-round mapping check: refinement/base-label mapping was reconciled against the `prove-nd-mt` classification table; rows with no proven normative refinement now use explicit `n/a`.
- Unresolved evidence: A3 direct concurrent dispatch around `ctoscLoadPartition::init()` was not fully proven from the snapshot; A5 algorithm equivalence depends on external PRG/timer behavior; C1 needs a uniqueness invariant or runtime assertion for duplicate `(LPKEY, D-node)` entries.
