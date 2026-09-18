# CTS Non-Determinism Audit — Executive Brief

**Scope:** `nwtn/src/cts` snapshot at `/remote/us01home05/carys/cts` — 2,391 C++ files, 52 MB, 23 subdirectories.
**Filter:** HIGH and MEDIUM only, per request.
**Result:** **6 HIGH, 13 MEDIUM** real defects. 24 further sites are real but report/debug-only (LOW) and are listed in the full report.
**Full report:** `/u/ranjithp/folders/coreStory/snps/nd-analysis/cts-nd-report.md`

---

## The headline

CTS is **determinism-aware code that has been fixed before**, and that is exactly where the
remaining defects live. The most valuable findings are not accidental `std::set<T*>` usage —
they are **mitigations that are incomplete or inert**:

- A map is converted to a vector *"for deterministic behaviour"*, then sorted by a comparator
  that only compares hierarchy depth, so siblings keep address order.
- A helper written expressly to *"sort leq to prevent ND"* begins with an early return at its
  app option's default value, making it a no-op at all seven call sites.
- A sort-by-criticality comparator is not a strict weak ordering, so the tie-break it was meant
  to impose is unspecified (and is undefined behaviour for `std::set`).

The two genuinely new defects are in recently-touched parallel code, including the only real
data race found.

## Triage funnel

| Stage | In | Dismissed | Out |
|---|---:|---:|---:|
| Stage 1 mechanical scan (21 patterns) | — | — | 11,427 candidates |
| Stage 1 narrowing (template/key/iteration rules) | 11,427 | 9,857 | 1,570 |
| Stage 2/3 deep read (7 parallel subagents) | 1,570 | 1,370 | 200 |
| Grouped by root cause | 200 | — | **19 defects** |

## HIGH — 6

| Site | Issue | Owner (p4) |
|---|---|---|
| `ccd/skewopt/soSolverUpdater.cc:2100` | **Data race, not just ordering.** `tbb::parallel_for_each` reaches `funcsMap[scenario]` on a shared `std::map` with no mutex. Concurrent `operator[]` rebalances the red-black tree — UB. Either a scenario bucket is lost from the CG objective, or the tree corrupts and crashes on the next traversal. The correct pre-sized idiom is already 40 lines below at `:2147`. | `matteod`, CL `13914296` |
| `ctsmisc/ctsAutoBalancePoint.cc:656` | `ltermMap` is a pointer-keyed `std::map`; the `std::sort` that follows keys only on a float offset, so ties keep address order. Order matters because each launch chain reads offsets a previous one stored, and the result is committed via `setCtsDelayPoint()`. Default-on. | CL `3007535` (bulk merge — **attribution unreliable**) |
| `mscts/drivers/msDrivers.cc:8189` | The author's own fix is incomplete: `compareHierDepth` compares only `getDepthFromTop()` and `std::sort` is not stable, so sibling blocks at equal depth keep address order. That decides generated instance names and which hierarchy *adopts* an orphan load. Data-triggered, not switch-gated. | `sumanc`, CL `6890358` |
| `ctscto/ctosc/ctoscGlobal.h:274` | `sclkCornerHash` hashes a `ctoSclkBag*` address. Two of its nine containers are iterated into `margins[sink] += lmargin * weight` — a non-associative float sum whose term order *is* the hash order. That value then becomes a `std::sort` key deciding which loads sit under which inserted buffer. | `yunjianj`, CL `7023073` |
| `ccd/ctsccd/fmax/fmaxLpSolverIncremental.cc:5127` | Sorts by constraint **value**, then calls `std::unique` with **pointer** equality. The dedup can never fire for the case it was written for — in a function named `removeRedundantPathsParallel`. | `tsirogia`, CL `9748335` |
| `ctssc/ctskSize.cc:1384` | `kneeMap` keyed by lib-cell `getFullName()` in the sizing LEQ-filter inner loop; two hierarchical name builds per iteration to look up a tuple that already holds the `ndmModule*`. **Note:** the name key *was* the ND fix (CL `4151071`, *"Fixed non-deterministic behavior in ccd"*), so this is a **cost** item, not an ND regression. | `jwon`, CL `4151071` |

## MEDIUM — 13

| Site | Issue |
|---|---|
| `ctsutil/ctsUtils.cc:57` | `sortModulesByName()` — the LEQ determinism guard — early-returns at its option's default (`cts.optimize.use_module_name_to_sort_libs`, HIDDEN, `false`), so it is a no-op at all 7 call sites. Its consumer `ccdSinkSize.cc:301` funnels LEQ cells through `std::map<float, ndmModule*>`, whose `insert` **drops tied cells by input position**. |
| `ccd/ctsccd/cgbased/ccdcgSolver.cc:501` | `srand(100)` + `rand()` — the only RNG in product CTS — seeds CG candidate values from the process-global generator, and clobbers that generator for every other module. |
| `ctssch/ctsTimingDrivenTransitionTargets.h:181` | `compareTimInfo` returns `true` for both `comp(a,b)` and `comp(b,a)` on a tie (and for `comp(a,a)`) — UB as a `std::set` comparator. Ties are the *common* case: non-critical sinks all score exactly `0.0`. Drives the "N worst sinks" `max_transition` constraint write. |
| `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:277` | TNS partial sums are grouped by thread count, so the returned cost — and the WNS witness path on ties — changes with `-max_cores`. |
| `ctssc/lazytns/ctsLazyModel.cc:4834` | Lazy-TNS path-group tracing selects a **different algorithm** above 32 cores. |
| `ctscto/ctoFlowClone.cc:1884` | `restructFlow` iterates `std::set<ndmTerm*>` in address order, then clones/shields buffers and truncates at a 10% cap. |
| `mscts/drivers/msDrivers.cc:11645` | `setKeepoutMarginForLibCell` returns out of the middle of a `std::set<ndmModule*>` loop, so margins land on a run-varying subset. The `remove` counterpart can strand a hard keepout on a reference block. |
| `mscts/msmesh/msLevelBalancer.cc:1745` | MV-aware level balancing inserts buffers per power domain in `std::map<ndmPowerDomain*>` address order. Hidden option, off by default. |
| `ctscto/ctosc/ctomt/gls/ctomtEndpointTypes.h:32` | Endpoint seed priorities are numbered by `unordered_set<ndmTerm*>` iteration. |
| `ctsmisc/ctsIfsDataType.h:32` | IFS prepone endpoint set is an `unordered_set<ndmTerm*>`; hash order becomes the GLS candidate numbering. |
| `ctsmisc/ctsICGCell.cc:514` | ICG signature/BDD visitor keys two maps on `getPathName()`; 121 calls in the file, three hierarchical names in one statement. |
| `mscts/msutil/msInfra.cc:1255` | Clock-latency / ideal-network constraints stored by name and resolved via `findTerm()`; a renamed pin is silently dropped with no message. |
| `ctssc/ctsXformProblems.cc:1130` | `_instInfoMap` snapshots instance state by name, so a rename is counted as a removed cell in the user-facing CCD report. |

## Suggested order of work

1. **`soSolverUpdater.cc:2100`** — it is undefined behaviour and can corrupt state or crash, not merely reorder output. Fix is to pre-populate the map serially before the parallel loop.
2. **`ctsAutoBalancePoint.cc:656` and `msDrivers.cc:8189`** — both default-on, both reach a database write, and both are five-line comparator tie-breaks on `getIdLong()`.
3. **`ctsUtils.cc:57`** — cheapest high-leverage change in the report. Making the guard unconditional and keying it on `getIdLong()` instead of `getFullName()` is *faster* than the behaviour the option already enables, which removes the cost objection the author recorded in CL `13530532`.

## What this audit does not establish

- **Nothing was built or run.** No finding has a demonstrated run-to-run diff. Each claim is that the mechanism is present in source and that the order or value reaches an observable sink. Confirming a row needs a two-run A/B on a real design.
- **The snapshot is `cts`-only.** `nwtn/src/opt`, `util/crm.h`, `util/dos*.h`, `timerInterf`, `grArc`/`grGraph` and `xformEngine` are absent. Several latent-only verdicts would flip to real if a cross-module caller exists — **`ctsroute/ctsRouter`** is the most consequential: it has the strongest ND chain found anywhere (nets routed in address order against a shared congestion map, results written to NDM), and was classified dead only because nothing in this snapshot constructs it. Close it with `rg 'ctsRouterInterf' nwtn/src`.
- **The snapshot is stale** (tarball dated 2026-07-19). Depot attribution matched the snapshot line-for-line at 8 of 9 sites; `msDrivers.cc` has drifted ~+255 lines and was re-anchored by symbol search.
- **One ownership row is unreliable** — `ctsAutoBalancePoint.cc` annotates to a bulk branch merge whose referenced source CL is an unrelated PV crash fix.
