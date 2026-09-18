# CTS ND — Proof & Qualification (post-freeze)

Runs **after** the discovery freeze (`candidate-set.md`). Uses `corestory-nd-qualification` skill; CoreStory project **10 (`cts-code`) only**. No prior A/B, prior AI adjudications, or held-out ground truth used. No source modified. Evidence labeled per the skill's hierarchy: **[Direct source] / [Build/config] / [CoreStory] / [Runtime] / [Inference] / [Unavailable]**.

Qualification does not alter the discovery denominator (21 frozen candidates). Candidates not individually qualified below (clusters 014–021) remain frozen and require per-site qualification; representative dispositions are given.

---

## ND-CAND-003 — Unseeded `mt19937` in k-means++ clustering
- **Location:** `mscts/mstap/msClustering.{h:284,cc:775,816}`
- **Reported mechanism:** RNG without input-derived seed (Pattern 1.5)
- **Discovery reference/example family:** 1.5 (cf. plan example `optClustering.cc`)

**MECHANISM PROOF**
- Disposition: **mechanism partially supported (deterministic-stream caveat).**
- Evidence: [Direct source] `_rand` is a default-constructed `boost::random::mt19937` (fixed seed 5489); no `.seed(...)` call found in `msClustering.cc`. Consumed at `dist(_rand)` for k-means++ weighted centroid selection.
- Unresolved: whether `_rand` is re-seeded/reset per `cluster()` invocation; tie-behavior of weighted selection.

**APPLICATION QUALIFICATION**
- Build: [Inference] `mstap` tap-synthesis is core CTS. [CoreStory] caller `msTapSynthesis.cc:1434-1687` "runs clustering."
- Reachability: [CoreStory] tap synthesis → `msClustering` centroid seeding (Q2).
- Runtime/config: clustered tap-partitioning strategy (vs one-to-one / max-tap).
- Exact varying input/state: default-seeded mt19937 is a **fixed stream**; across *equivalent* runs the draw sequence is identical **unless** stream position differs due to prior reuse or the number of `dist()` calls varies with earlier ND (e.g. cluster iteration order).
- Mechanism: RNG → centroid index/prob → cluster assignment.
- Propagation: [CoreStory] centroid selection → cluster membership → **tap-tree topology** (Q2 observability path).
- Neutralization: none found on the RNG path; k-means++ selection is order-sensitive.
- Observable consequence: tap-tree topology / buffering (QoR).
- Blast radius: multisource tap synthesis clustering only.
- Missing load-bearing evidence: [Unavailable] per-call reset of `_rand`; input-stability of weighted-selection ties.

**CORESTORY CONTRIBUTION** — Used: YES (Q2). Purpose: find RNG consumers / observability. Evidence: k-means++ seeding + `msTapSynthesis` caller. Decision affected: established topology observability. Reachable from local source alone?: PARTIALLY (local shows RNG; CoreStory cheaply tied it to topology).

**FINAL**
- Disposition: **LATENT** (mechanism real; equivalent-run manifestation depends on unproven `_rand` reuse/tie-stability).
- Confidence basis: direct source + CoreStory path; two unresolved links.
- SME/runtime validation: seed-perturbation A/B on tap topology; check `_rand` lifecycle.

---

## ND-CAND-010 — App-option-gated "may cause ND" pointer map (ICG estimators)
- **Location:** `icg/ctsICGEstimators.h:70-140` (`ctsNdmPtr2ObjectNonNdType`), constructed at `:383`.
- **Reported mechanism:** pointer-keyed ordered map, determinism decided by comparator/branch (Pattern 1.2/3.7)
- **Discovery reference/example family:** 3.7 / SKILL checklist #7 (deterministic control-path normalization)

**MECHANISM PROOF**
- Disposition: **mechanism supported, gated.**
- Evidence: [Direct source] ctor: `if(!useNonNdMapType) _ndMap = std::map<ndmPointer<const ndmType>, valueType, compareNdmPointer<...>>` (author comment "**may cause ND**") else `ndmPtrUnorderedMap` ("not cause ND"). Construction `:383` passes `useNonNdMapType = _session->getOpt().enableDeterministicEstimation()`.
- Unresolved: [Unavailable] `compareNdmPointer<>` ordering (id vs handle/address); whether `_latencyCriticality` is **iterated** vs `findAndGet`-only.

**APPLICATION QUALIFICATION**
- Build: [Inference] `icg` (integrated clock gating) estimation is in CTS.
- Reachability: `ctsDelayEstimator*` latency-criticality estimation.
- Runtime/config: **[Build/config] gated by app option `enableDeterministicEstimation()`** — when **false**, the ND-capable `std::map` branch is selected; when true, the deterministic unordered branch is used. Default value UNRESOLVED.
- Exact varying input/state: iteration order of the `std::map<ndmPointer,float,compareNdmPointer>` if `compareNdmPointer` is address/handle-ordered.
- Mechanism: ordered-map iteration → latency-criticality consumption.
- Propagation: [Unavailable] consumer of `_latencyCriticality` (lookup vs iteration) not traced.
- Neutralization: the deterministic-estimation option is itself the neutralizer when enabled.
- Observable consequence: [Inference] "criticality" → estimation/QoR (author's "not changing QoR" note implies QoR relevance).
- Blast radius: ICG latency-criticality estimation.
- Missing load-bearing evidence: `compareNdmPointer` semantics; `_latencyCriticality` consumption; `enableDeterministicEstimation` default.

**CORESTORY CONTRIBUTION** — Used: YES (Q1) to surface the class. Decision affected: candidate exists (scan missed it — smart-pointer key). Reachable from local pattern-scan alone?: **NO** (regex 1.2 requires literal `*`).

**FINAL**
- Disposition: **UNRESOLVED** (gated ND path is real by author's own annotation, but `compareNdmPointer` order + consumer iteration + option default are load-bearing and unresolved). Do **not** promote to REAL on structural pattern alone (qualification lesson #4).
- SME/runtime validation: resolve `compareNdmPointer`; confirm `enableDeterministicEstimation` default; trace `_latencyCriticality` iteration.

---

## ND-CAND-011 — Thread-count-partitioned TNS/WNS reduction (fmax timing cost)
- **Location:** `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:233-395`
- **Reported mechanism:** parallel FP reduction + thread-count dependency (Pattern 3.1/3.5)

**MECHANISM PROOF**
- Disposition: **mechanism refuted for equivalent-run ND; reclassified.**
- Evidence: [Direct source] `numberOfThreads = maxThreads()`; `maxThreads()` returns configured `_maxThreads` (`fmaxCostFunction.h:69`, set `_maxThreads=threadCount` at `.cc:38`; one caller uses 250) — **not** `hardware_concurrency`. Input is **index-partitioned** (`iteratorRanges[threadCount]`), per-thread `double` TNS accumulation, and the merge loop runs in **deterministic `threadIndex` order** with prefix offsets; WNS tie-break resolves to lowest `threadIndex`.
- Unresolved: origin of the configured `threadCount` (app option vs derived).

**APPLICATION QUALIFICATION**
- Build/Reachability: fmax LP timing cost evaluation (TNS/WNS).
- Runtime/config: parallel path taken when `maxThreads()>1`.
- Exact varying input/state: none across *equivalent* runs at fixed `_maxThreads` — partition and merge order are fixed. Float TNS **grouping** and WNS tie-breaks change only if `_maxThreads` changes.
- Neutralization: deterministic index partition + ordered merge = built-in neutralizer.
- Observable consequence: TNS/WNS values & most-violated-path — deterministic per configuration.
- Blast radius: fmax cost evaluation; sensitivity is to configured thread count only.

**CORESTORY CONTRIBUTION** — Used: YES (Q3) to surface the site. Local source alone sufficed for the disposition.

**FINAL**
- Disposition: **CONFIGURATION-SENSITIVITY** (float grouping/tie-breaks vary with configured `_maxThreads`), **NOT equivalent-run ND** (qualification lesson #1). LATENT only if `_maxThreads` is derived from machine core count.
- SME/runtime validation: confirm `threadCount` provenance.

---

## ND-CAND-008 — `directory_iterator` order into LP model flow
- **Location:** `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2176` (`runLpSequenceFromFilesICG`)

**MECHANISM PROOF**
- Disposition: **mechanism supported.**
- Evidence: [Direct source] `for(entry : std::filesystem::directory_iterator(parentFolderPath))` classifies files into `modelFilenames`/`baselineFilenames` by substring, then `executeFlowBasedOnFilesICG(modelFilenames,...)`. `modelFilenames` order = filesystem enumeration order (no sort) ⇒ varies across machines/filesystems.

**APPLICATION QUALIFICATION**
- Reachability: [Inference] `*FromFilesICG` reads `.mps` LP model files from a folder — a **file-replay / offline LP flow**, not obviously the mainline in-memory CTS flow.
- Exact varying input/state: order of `modelFilenames` passed to `executeFlowBasedOnFilesICG`.
- Propagation/Observable: [Unavailable] whether model processing order affects LP results (order-independent solves) or accumulation.
- Neutralization: none (no sort before use).
- Blast radius: file-based ICG LP replay flow.

**FINAL**
- Disposition: **LATENT / CONFIGURATION-SENSITIVITY** (cross-filesystem order ND; production reachability of the file-replay flow and order-sensitivity of the LP consumer unresolved).
- SME/runtime validation: confirm flow reachability; add `std::sort(modelFilenames)` is the trivial neutralizer if order matters.

---

## ND-CAND-005 — Pointer-hash thread-local timing caches
- **Location:** `ccd/skewopt/soLogicCone.h:375,400-402`

**MECHANISM PROOF** — Disposition: **mechanism present, neutralized-by-usage.** [Direct source] `std::hash<const void*>` over pointer keys ⇒ bucket layout varies. But containers are `tbb::enumerable_thread_specific<unordered_map>` used as **lookup caches** (hit/miss by pointer identity); cached values are identity-invariant; no order-sensitive iteration found.

**APPLICATION QUALIFICATION** — Consumption is membership/lookup-only; iteration order unobserved. Neutralization: value is order-independent.

**FINAL** — Disposition: **NEUTRALIZED / LATENT** (address hashing real but not observably consumed; 1.3/1.4 false-positive class). CoreStory: NO (local sufficed).

---

## ND-CAND-006 — `tbb::parallel_reduce` with custom state (GLS)
- **Location:** `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:312`

**MECHANISM PROOF** — Disposition: **UNRESOLVED.** [Direct source] reduce + `globalDone` early-exit; merge order work-stealing dependent. [CoreStory Q3] `processSccBagIntoCache` "deterministically assembles" per-driver context — possible neutralizer. `stateType.reduce()` associativity **[Unavailable]**.

**FINAL** — Disposition: **UNRESOLVED** (associativity + early-exit determinism unproven; CoreStory hints at deterministic downstream assembly). SME: resolve `stateType`/`reduce`.

---

## ND-CAND-007 — `hardware_concurrency` grain size (group latency)
- **Location:** `ctscto/ctoGrpLatCalc.cc:80`

**MECHANISM PROOF** — Disposition: **refuted (scheduling-only).** [Direct source + CoreStory Q3] grain `_step` feeds `tbb::parallel_for`; body writes `grpLat[i]` by independent index and selects worst (max) latency (commutative).

**FINAL** — Disposition: **NOT-ND** (grain size affects scheduling only; per-index writes + commutative reduction). Retained in record as scanned-and-cleared.

---

## ND-CAND-001 / 002 / 004 — RNG in skew-group / test / CG solver
- **001** `ctsSkewgroup.cc:152 srand(time)`: [CoreStory Q1] file = "test and analysis driver"; random `fillMap` overload only via explicit-count call. Disposition: **LATENT** (real 2.1 mechanism; production reachability of the random path unconfirmed — likely test).
- **002** `ctsDStest.cc:150 srand(time)`: file = "Disjoint Set Analysis Test Code." Disposition: **DEAD/UNUSED (test)** w.r.t. production ND.
- **004** `ccdcgSolver.cc:501 srand(100)`: fixed seed ⇒ per-call deterministic; concern is global-`rand` state coupling. Disposition: **NOT-ND locally / LATENT** for cross-module `rand()` coupling. SME: audit other `rand()` users in the CG path.

---

## ND-CAND-013 — `dosUnorderedSet<T*>` wrapper sets
**MECHANISM PROOF** — Disposition: **UNRESOLVED.** [Unavailable] `dosUnorderedSet` hash/equality is an external `dos*` library type not in the tree or project-10 index (CoreStory Q1 did not resolve it). Per lesson #4, an unordered pointer-valued wrapper does not by itself establish address hashing.
**FINAL** — **UNRESOLVED**; resolve wrapper hash + trace iteration→output for `msuiReportPowerTaps`/`ccdUtil::collectConnectedNets`.

---

## Cluster candidates 014–021 — representative dispositions (remain frozen)
- **014 (1.2 default-comparator maps, 983):** mostly resolve to typedef'd stable comparators (`compareObjPtr`) or membership-only ⇒ largely SAFE-ADOPTER/LATENT; genuine defect subset = default-`std::less<T*>` maps iterated to order-sensitive sinks. Per-site qualification required.
- **015 (1.3 default-hash unordered, 368):** includes ND-CAND-005 (neutralized). Requires 3.3 iterated+order-sensitive check per site.
- **016 (3.2 MT writes, 203):** representatives 006 (unresolved), 011 (config-sensitivity).
- **017 (3.6 post-collection, 557):** seed-only; Stage-3 narrowing mandatory.
- **018 (4.4 concurrent_hash_map, 36):** verify accessor scoping (ctomtGls "safe for distinct bags").
- **019 (1.4 pointer hashers):** realness depends on iteration of the owning unordered container.
- **020 (4.1/4.2 mutable caches):** static MT-ND; needs TSan/MT-hunt observability.
- **021 (2.2 getFullName keys, 100):** promote where name-string key feeds order-sensitive logic.

---

## Provenance Ledger (material CoreStory evidence)

| Evidence ID | Candidate | Stage | Evidence source | Question / purpose | Result | Decision affected |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | scope | disc | CoreStory `list_projects` | Confirm project 10 only | proj10 `cts-code` completed; proj9 excluded | Scope guard |
| E2 | 013,010 | disc | CoreStory `semantic_search` Q1 (proj10) | Resolve `dosUnorderedSet` hash + pointer-set iteration | Did NOT resolve external wrapper; surfaced `ctsICGEstimators` "may cause ND" map + `ctsObjId` | 013 UNRESOLVED; **010 discovered** |
| E3 | 003 | disc | CoreStory `semantic_search` Q2 (proj10) | Clustering RNG consumers / siblings | k-means++ seeding, caller `msTapSynthesis`, sibling `msgtsClustering` | 003 observability→topology; **012 path added** |
| E4 | 011,006,007,016 | disc | CoreStory `semantic_search` Q3 (proj10) | Parallel/MT reduction & thread-count consumers | `fmaxTimingCostFunction` reduction, `ctomtGls` deterministic assembly, `ctoGrpLatCalc` per-index writes | **011 discovered**; 006/007 contrary evidence |
| E5 | 011 | qual | [Direct source] `fmaxCostFunction.{h,cc}` | Thread-count provenance | `maxThreads()`=configured `_maxThreads` | 011 → CONFIGURATION-SENSITIVITY |
| E6 | 010 | qual | [Direct source] `ctsICGEstimators.h:383` | ND-branch gating | `useNonNdMapType = enableDeterministicEstimation()` | 010 gated; still UNRESOLVED links |
| E7 | 008 | qual | [Direct source] `fmaxLpSolverCompressedEndpoints.cc:2176` | directory order consumer | order → `executeFlowBasedOnFilesICG` | 008 → LATENT |

**CoreStory scope compliance:** every CoreStory call used `project_id: 10`. No `cts-code2` (project 9) or other project consulted. All calls read-only.

## Stop condition
Stopped at the qualification checkpoint. No source modified. Dispositions, unresolved load-bearing links, and recommended SME/runtime validation recorded above.
