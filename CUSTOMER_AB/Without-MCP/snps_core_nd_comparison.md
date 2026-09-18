# CTS ND Result Comparison: snps vs core

## Scope

Compared result sets:

- `/u/ranjithp/folders/coreStory/snps/nd-analysis/cts-nd-report.md`
- `/u/ranjithp/folders/coreStory/snps/nd-analysis/cts_mt_nd_details.md`
- `/u/ranjithp/folders/coreStory/core/nd-audit-cts/ND_AUDIT_REPORT.md`
- `/u/ranjithp/folders/coreStory/core/nd-audit-cts/cts_nd_details.md`

Source authority:

- `/remote/us01home05/carys/cts`
- `/remote/swefs/PE/products/dgplt/main/clientstore/dgplt_main/nwtn/src` for
  out-of-snapshot utility definitions

Method:

1. Normalize findings by source site and root cause, not by report ID.
2. Require a varying input, a live path, and an observable sink for an ND verdict.
3. Keep deterministic functional bugs, performance issues, and rename fragility separate
   from ND.
4. Treat every report as a hypothesis and re-read source for the union of promoted rows.

Nothing was built or run. "Confirmed" below means source-confirmed, not runtime-reproduced.

## Executive Result

| Result | Count | Meaning |
|---|---:|---|
| Unique promoted rows across both runs | 22 | 19 from `snps`, 6 from `core`, with 3 exact overlaps |
| Source-confirmed current ND defects | 9 | Live varying input reaches a product or user-visible sink |
| Duplicate of another real root cause | 1 | IFS prepone set is the upstream half of endpoint candidate-order ND |
| Not a current ND defect | 10 | Deterministic functional/performance issue, false mechanism, or dead code |
| Unresolved ND status | 2 | A real non-ND concern exists, but the varying-input/equivalence proof is incomplete |
| Runtime-reproduced | 0 | Neither run executed an A/B testcase |

Source-confirmed current ND coverage:

| Run | Confirmed unique issues found | Recall against the 9-issue union | Promoted rows surviving as unique ND |
|---|---:|---:|---:|
| `snps` | 8 | 89% | 8 of 19 |
| `core` | 4 | 44% | 4 of 6 |

`snps` had much better recall, including the only proven data race. `core` produced a
shorter list, but two of its six promoted rows fail source validation.

## Exact Agreements

Both runs independently promoted these same root causes, and source confirms all three.

| Location | `snps` | `core` | Final assessment | Notes |
|---|---|---|---|---|
| `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:8189` | HIGH real | MEDIUM real | Conditional real ND | A raw-pointer hierarchy map is drained, then sorted only by depth. Equal-depth hierarchy order remains address-derived and reaches insertion/orphan-load assignment. |
| `/remote/us01home05/carys/cts/mscts/msmesh/msLevelBalancer.cc:1745` | MEDIUM real | MEDIUM real | Conditional real ND | A raw-pointer power-domain map controls per-domain buffer insertion. Requires MV-aware level balancing, which defaults off. |
| `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | MEDIUM real | MEDIUM real | Real cross-configuration ND | TNS partial-sum grouping depends on thread count. Fixed-N runs are stable; changing `-max_cores` can change low bits. |

Severity difference on the hierarchy row is judgment, not a technical disagreement.
`snps` emphasizes the downstream DB mutation; `core` grades default reachability more
conservatively.

## Direct Disagreements Resolved

| Location | `snps` result | `core` result | Source-based resolution | Why |
|---|---|---|---|---|
| `/remote/us01home05/carys/cts/ccd/ctsccd/cgbased/ccdcgSolver.cc:501` | Real | Dismissed | Not ND; `core` is correct | `srand(100)` is immediately followed by a sequential `rand()` loop. It is the only production CTS consumer. The stream is fixed. A local RNG is cleaner, but no varying input was shown. |
| `/remote/us01home05/carys/cts/mscts/msui/msuiGetPowerTaps.cc:66,879` | Wrapper bucket dismissed | Real | Not proven ND; `snps` is correct on the mechanism | `dosUnorderedSet` uses `dosContainer::keyHash`, which hashes stable object ID/type/context, not addresses. The utility header explicitly documents deterministic order for deterministic insert/delete sequences. `core` used the wrong container taxonomy. |
| `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:3330` | Dead/unused | Real | Dead/unused; `snps` is correct | `connectUnassignedLoads` has only a declaration and definition in the CTS tree. The address-ordered map would be dangerous if called, but there is no current caller. |
| `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | Initially real; MT proof changed it to non-ND | Not promoted | Not ND; deterministic functional bug | `std::unique` uses pointer equality after a value sort, so intended deduplication fails. Static partitions and value sorting do not show a schedule-dependent survivor. |

One explicit non-real agreement is also sound: both runs classify
`/remote/us01home05/carys/cts/ctsroute/ctsRouter.cc` as dead/unreachable in this source
slice. Its route-order mechanism would be serious if an external caller is added.

## Full 22-Row Crosswalk

Legend:

- `Real`: source proves current ND or a data race.
- `Conditional real`: source proves the mechanism under a specific feature/data gate.
- `Not ND`: another issue may exist, but not non-determinism.
- `Dead`: no compiled/reachable path today.
- `Duplicate`: same root cause as another row.
- `Unresolved`: source proof is incomplete.

| # | Location / root cause | `snps` | `core` | Final verdict | Independent assessment |
|---:|---|---|---|---|---|
| 1 | `/remote/us01home05/carys/cts/ctsmisc/ctsAutoBalancePoint.cc:656` | Real | Not reported | Real | Pointer-map order survives a partial float sort; later launch chains read state written by earlier ones; results reach `setCtsDelayPoint()`. Default-on debug setting. |
| 2 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:8189` | Real | Real | Conditional real | Equal-depth hierarchy order remains address-derived and controls insertion and orphan-load adoption. |
| 3 | `/remote/us01home05/carys/cts/ctscto/ctosc/ctoscGlobal.h:274` | Real | Not reported | Conditional real | `sclkCornerHash` hashes `ctoSclkBag*`; unordered iteration feeds non-associative float sums and then sink sorting/load grouping. |
| 4 | `/remote/us01home05/carys/cts/ctssc/ctskSize.cc:1384` | Real | Not reported | Not ND | The report itself proves name ordering is stable. This is a hot-path performance issue and name-stability concern, not run-to-run ND. |
| 5 | `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | Real, later corrected for MT | Not reported | Not ND | Equal-valued pointer-distinct constraints are not removed. This is deterministic deduplication failure. |
| 6 | `/remote/us01home05/carys/cts/ccd/skewopt/soSolverUpdater.cc:2100` | Real | Not reported | Real data race | TBB workers call `std::map::operator[]` on shared solver maps without a gate or lock. Concurrent tree insertion is undefined behavior. |
| 7 | `/remote/us01home05/carys/cts/ctscto/ctoFlowClone.cc:1884` | Real | Not reported | Dead/stale | `/remote/us01home05/carys/cts/ctscto/Master.make` builds `ctoRestruct.cc`, not `ctoFlowClone.cc`. The live replacement uses `termSetType`, the stable comparator type. |
| 8 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:11645` | Real | Not reported | Conditional real | A raw-pointer module set is traversed until an invalid bbox/ref design causes `return`; which prefix gets keepout changes with address order. |
| 9 | `/remote/us01home05/carys/cts/mscts/msmesh/msLevelBalancer.cc:1745` | Real | Real | Conditional real | Raw-pointer power-domain order reaches buffer creation. Hidden MV-aware option defaults off. |
| 10 | `/remote/us01home05/carys/cts/ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32` | Real | Not reported | Conditional real | A default pointer-hashed endpoint set is iterated to assign `dNum`; that priority becomes the ordered candidate queue consumed by optimization. |
| 11 | `/remote/us01home05/carys/cts/ctsmisc/ctsIfsDataType.h:32` | Real | Not reported | Duplicate of #10 | This unordered prepone set is copied into the endpoint set used by #10. It is useful upstream evidence, but not a second independent defect. |
| 12 | `/remote/us01home05/carys/cts/ccd/ctsccd/cgbased/ccdcgSolver.cc:501` | Real | Dismissed | Not ND | Constant seed, sequential consumption, and no second production CTS consumer. Process-global RNG use is hygiene debt, not a proven ND sink. |
| 13 | `/remote/us01home05/carys/cts/ctsmisc/ctsICGCell.cc:514` | Real | Not reported | Not ND | Ordered string maps are lookup-only and reproducible. Real concerns are repeated name construction, accidental `operator[]` insertion, and unguarded debug output. |
| 14 | `/remote/us01home05/carys/cts/ctssc/ctsXformProblems.cc:1130` | Real | Not reported | Not ND | Pre/post full-name comparison can mislabel a rename as remove/add, but the ordered string containers are deterministic. Rename occurrence was not proven either. |
| 15 | `/remote/us01home05/carys/cts/mscts/msutil/msInfra.cc:1255` | Real | Not reported | Not ND | Name round-tripping can silently lose a constraint after a rename, but the maps and lookup sequence are deterministic. This is robustness, not ND. |
| 16 | `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | Real | Real | Real, bounded | Thread-count-dependent floating-point grouping changes cross-machine/core-count reproducibility; no same-N scheduling race was found. |
| 17 | `/remote/us01home05/carys/cts/ctssc/lazytns/ctsLazyModel.cc:4834` | Real, later unresolved | Not reported | Unresolved | The code selects different serial/parallel algorithms above 32 threads. Equivalence was not proved, and no runtime diff exists. |
| 18 | `/remote/us01home05/carys/cts/ctssch/ctsTimingDrivenTransitionTargets.h:181` | Real | Not reported | Not proven ND; real comparator bug | Comparator returns true on ties and violates strict weak ordering. The top-N sink is real, but insertion is deterministic today; the original report admits fixed-binary run-to-run variance was not proved. |
| 19 | `/remote/us01home05/carys/cts/ctsutil/ctsUtils.cc:57` | Real | Not reported | Unresolved ND; real data-loss bug | The sort guard is off by default and `std::map<float,...>` drops tied cells. The report explicitly did not prove that the upstream LEQ vector varies run to run. |
| 20 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:711` | Not promoted | Real | Conditional real | In MLPH with multiple load nets, a raw-pointer set chooses the last driver. Live call sites use that raw return to choose clock/sink context. |
| 21 | `/remote/us01home05/carys/cts/mscts/msui/msuiGetPowerTaps.cc:66,879` | Stable wrapper bucket, not promoted | Real | Not proven ND | `dosContainer::keyHash` is ID/type based. No separate varying insertion source was shown. The returned collection is not explicitly sorted, but the reported address-hash cause is false. |
| 22 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:3330` | Dead/unused | Real | Dead/unused | Dangerous code shape, but no caller exists in CTS. Do not count it as a current defect. |

## What Is Actually Real

The 9 unique source-confirmed issues are:

| Priority | Issue | Type | Default exposure | Why owners should care |
|---:|---|---|---|---|
| 1 | `/remote/us01home05/carys/cts/ccd/skewopt/soSolverUpdater.cc:2100` | Data race | No local MT gate | Concurrent `std::map` insertion can corrupt solver state or crash. |
| 2 | `/remote/us01home05/carys/cts/ctsmisc/ctsAutoBalancePoint.cc:656` | Address-order algorithm | Default-on debug setting | Order feeds cross-term state and persisted CTS delay points. |
| 3 | `/remote/us01home05/carys/cts/ctscto/ctosc/ctoscGlobal.h:274` | Pointer-hash plus FP reduction | Flow/data gated | Float value becomes a sort key for buffering groups. |
| 4 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:711` | Last-writer/last-element selection | MLPH option defaults off | Different source driver can change the clock/sink context and tree structure. |
| 5 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:8189` | Address-order hierarchy traversal | MLPH/data gated | Changes hierarchy insertion order and orphan-load adoption. |
| 6 | `/remote/us01home05/carys/cts/mscts/msmesh/msLevelBalancer.cc:1745` | Address-order domain traversal | Hidden option defaults off | Changes per-domain insertion and shared resource/name consumption. |
| 7 | `/remote/us01home05/carys/cts/mscts/drivers/msDrivers.cc:11645` | Address-order early return | Keepout option gated | Applies/removes keepout on a varying subset when one ref view is invalid. |
| 8 | `/remote/us01home05/carys/cts/ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32` | Pointer-hash priority numbering | Endpoint flow gated | Changes seed order in an optimization that mutates design state. |
| 9 | `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | Thread-count FP grouping | More than one thread | Changes TNS low bits across `-max_cores`; not a same-N race. |

The first issue is the clearest immediate fix. It is the only proven data race and has the
strongest failure mode.

## Real Bugs That Are Not Proven ND

These should not be lost just because their ND classification was wrong:

| Location | Actual concern |
|---|---|
| `/remote/us01home05/carys/cts/ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | Pointer equality prevents intended value deduplication. |
| `/remote/us01home05/carys/cts/ctssch/ctsTimingDrivenTransitionTargets.h:181` | Invalid `std::set` comparator violates strict weak ordering and can mishandle ties. |
| `/remote/us01home05/carys/cts/ctsutil/ctsUtils.cc:57` and `/remote/us01home05/carys/cts/ccd/ctsccd/ccdSinkSize.cc:301` | Default-off canonicalizer plus float-key map silently drops tied lib cells; varying upstream order remains unproved. |
| `/remote/us01home05/carys/cts/ctsmisc/ctsICGCell.cc:514` | Repeated hierarchical name construction, default insertion on lookup, and unguarded debug output. |
| `/remote/us01home05/carys/cts/ctssc/ctsXformProblems.cc:1130` | A rename can be misreported as remove/add if such a rename occurs in the snapshot/check window. |
| `/remote/us01home05/carys/cts/mscts/msutil/msInfra.cc:1255` | A name change can silently drop preserved latency/ideal-network state. |

## Why One Run Found What The Other Missed

| Difference | Effect on `snps` | Effect on `core` |
|---|---|---|
| Broad sink tracing | Found the solver race, auto-balance feedback, hash-to-float reduction, keepout early return, and endpoint priority chain | Missed all five despite claiming broad skew/hash coverage |
| Accessor-aware tracing | Missed `findDriverTerm` because the raw-pointer set is obtained through `getLoadNetSet()` | Manual mutator-focused review found the live raw return and call sites |
| Container taxonomy | Correctly recognized `dosContainer::keyHash` as stable | Incorrectly modeled `dosUnorderedSet` as address-hashed, creating `get_power_taps` |
| Build/call reachability | Incorrectly promoted unbuilt `ctoFlowClone.cc`, but correctly rejected caller-free `connectUnassignedLoads` | Correctly avoided `ctoFlowClone.cc`, but promoted caller-free `connectUnassignedLoads` |
| Issue taxonomy | Mixed ND with performance, rename fragility, and deterministic functional bugs | Used a narrower ND filter, improving precision |
| Deep MT re-proof | Corrected the fmax `std::unique` row and downgraded Lazy-TNS to unresolved | Correctly proved the thread-count TNS mechanism, but did not expose an equivalent correction pass for its two false rows |

The differences are not caused by different source trees: both reports used the same
`/remote/us01home05/carys/cts` snapshot. They come from triage decisions, source-type
resolution, and reachability checks.

## Quality Assessment

| Quality dimension | `snps` | `core` | Assessment |
|---|---|---|---|
| Recall of current source-confirmed ND | High: 8/9 | Moderate: 4/9 | `snps` is better for discovery. |
| Precision of promoted list | Low: 8 unique ND out of 19 promoted | Moderate: 4 of 6 | `core` is shorter, but 2 of 6 still fail validation. |
| Highest-value discovery | Excellent | Weak | `snps` found the unguarded shared-map race; `core` missed it. |
| Container/type resolution | Strong overall | One major taxonomy error | `core` did not read `dosUnorderedSet`/`keyHash` before calling it address-dependent. |
| Build and caller reachability | Mixed | Mixed | Each run promoted one dead row. |
| Self-consistency | Weak in the large report; improved by MT proof | Better presentation, but overstates completeness | `snps` labels several rows real while their own sections explicitly say "no non-determinism." |
| Gate/default analysis | Strong | Strong on promoted live rows | Both usually identify feature defaults and data gates. |
| Runtime confidence | None | None | No finding was reproduced on a design. |

Overall:

- Use `snps` as the better discovery run. It found 8 of the 9 current source-confirmed
  issues and the most serious defect.
- Use neither promoted count as a defect count without reclassification.
- `core` is more concise, but its quality claim that all six were proved is not supported:
  one uses a stable ID hash and one has no caller.
- The best combined result is the 9-row source-confirmed table above, plus the separate
  non-ND bug table.

## Runtime Confirmation Needed

| Issue family | Minimum confirmation |
|---|---|
| `soSolverUpdater` shared map | TSAN or targeted concurrent-map assertion on a multi-scenario skewopt case |
| Pointer/address-order rows | Same binary and design, repeated N-vs-N runs with allocator perturbation; diff stable object IDs at the first order-sensitive sink |
| Fmax TNS | `-max_cores 1` vs N, then N vs N; compare raw/hex TNS, not rounded text |
| Lazy-TNS algorithm switch | 32 vs 33 cores, then repeated 33-core runs; diff traced path/endpoint sets and raw TNS |
| `sortModulesByName` | Assert/log the incoming LEQ stable IDs across repeated runs and create equal arc-delay ties |

Until those experiments run, the report supports source-level prioritization, not a claim
that a user-visible run-to-run delta has already been reproduced.
