# CTS ND Discovery — Frozen Candidate Set

**Status: FROZEN** at 2026-09-18 (America/Chicago). No candidate below may be silently removed by later proof/qualification. Candidates first found after this freeze would be labeled `QUALIFICATION-DISCOVERED`.

- **Discovery authority:** customer `nd-code-analyzer` v1.4.0 workflow + SHA-verified references (`nd-patterns.yaml` = 27-pattern catalog, source of truth). See `run-manifest.md` Stage 0.
- **Governance rule:** `corestory-nd-discovery.mdc` (thin). CoreStory (project 10 `cts-code` only) used as *search expansion*; it did not remove any customer-discovered candidate.
- **Mechanical scan:** ripgrep reproduction of `scan_nd.py` over YAML regexes (script unavailable). Raw per-pattern outputs preserved in `nd-eval-final/raw/scan/`.
- **Recall-preservation note:** where a YAML pattern produced a large regex cluster, the cluster is retained as an enumerated **cluster candidate** (with representative sites + full raw file), NOT dropped. Narrowing/realness evidence is recorded for qualification, never used to delete a candidate at discovery.

## Structural facts affecting all candidates

1. **Mirror duplication.** `include/` (top-level) and per-module `*/include/` and `*/core/include/` trees are byte-mirrors of the module source headers (e.g. `ctsutil\ctsInfra.h` ≡ `include\ctsInfra.h`; `ccd\skewopt\soLogicCone.h` ≡ `ccd\include\soLogicCone.h`; `rlx\...\cnmNetwork.h` appears 4×). Raw hit counts are inflated ~2–4×; candidate counts below are mirror-deduped by (basename,line,code).
2. **House determinism idiom is pervasive.** CTS widely uses `ndmObjectHandleNS::compareObjPtr`, `dosContainer::keyCompare`, `ndmObjPtrCmpType`, `compareNdmPointer`, `ndmPtrMap`/`ndmPtrSet`, `ndmPtrUnorderedMap`. ~60% of pointer-container declarations carry an on-line stable comparator/hash. The genuine ND surface is the *residue* that lacks these, plus wrappers whose semantics are external/unresolved.

---

## A. Promoted individual candidates

### ND-CAND-001 — Time-seeded RNG in skew-group utility
- **Location:** `skewgrp/ctsSkewgroup.cc:152` (`srand(time(NULL))`), consumed at 154–155 (`rand()%cntV`).
- **Suspected mechanism:** Pattern 2.1 (time/PID RNG seed) → different sequence every run by construction.
- **Customer pattern/example family:** 2.1 "Time/PID-based RNG seeds"; sibling of plan example `opt/optClustering.cc`.
- **Discovery evidence:** `raw/scan/p2.1.txt`, `p1.5.txt`. Inside `fillMap(multimap<int,int>&,cntV,cntE)` "build random mmap".
- **Severity hypothesis:** HIGH if production; LOW if test scaffold.
- **Origin:** CUSTOMER-PATTERN.
- **CoreStory used:** YES (query Q1) — ranked `ctsSkewgroup.cc` as a disjoint-set *test/analysis driver*; contrary evidence for later qualification (path likely test harness). CoreStory did not remove the candidate.
- **Contrary evidence (for proof/qual, not removal):** the `srand(time)` overload of `fillMap` is only invoked at `ctsSkewgroup.cc:223` with explicit `cnt` args; file summary = "test and analysis driver."

### ND-CAND-002 — Time-seeded RNG in disjoint-set test
- **Location:** `skewgrp/ctsDStest.cc:150` (`srand(time(NULL))`).
- **Mechanism:** Pattern 2.1. **Origin:** CUSTOMER-PATTERN. **Severity:** LOW (file = "Disjoint Set Analysis Test Code").
- **CoreStory:** YES (Q1) confirmed test harness. Retained; not removed.

### ND-CAND-003 — Unseeded `mt19937` driving k-means++ clustering
- **Location:** decl `mscts/mstap/msClustering.h:284` (`boost::random::mt19937 _rand;`); use `mscts/mstap/msClustering.cc:775` (`dist(_rand)*N` centroid index), `:816` (`prob = dist(_rand)`).
- **Suspected mechanism:** Pattern 1.5 (RNG without deterministic input-derived seed). Default-constructed `mt19937` (fixed seed 5489) is *technically* deterministic, but the RNG is a **reused class member**: stream position depends on prior clustering calls → order/coupling sensitivity; no input-derived seeding.
- **Customer pattern/example family:** 1.5; directly analogous to plan example `opt/optutil/optClustering.cc:288`.
- **Discovery evidence:** `p1.5.txt`; source read of decl + both `dist(_rand)` sites (k-means++ weighted centroid selection).
- **Severity hypothesis:** MEDIUM–HIGH (centroid selection → cluster assignment → tap-tree topology).
- **Origin:** BOTH — customer pattern found the unseeded RNG decl; **CoreStory materially broadened the observability path**.
- **CoreStory used:** YES (Q2). Returned `msClustering.cc:696-836` ("k-means++ centroid seeding … randomized weighted center selection by nearest-center distance") and callers `msTapSynthesis.cc:1434-1687` ("runs clustering" for tap partitioning). This ties the RNG to **final tap-tree topology** — a downstream observable.
- **Contrary evidence:** default seed 5489 ⇒ deterministic stream in isolation; realness hinges on whether `_rand` state is reset per clustering and whether ties in weighted selection are input-stable (qualification).

### ND-CAND-004 — Fixed-seed global `srand` in CG solver
- **Location:** `ccd/ctsccd/cgbased/ccdcgSolver.cc:501` (`srand(100)`), `:505` (`rand()`).
- **Mechanism:** Pattern 1.5/2.1. `srand(100)` is a *fixed* seed (deterministic locally) but mutates **global** RNG state, coupling any other `rand()` consumer in the run.
- **Origin:** CUSTOMER-PATTERN. **Severity:** LOW–MEDIUM (global-state coupling).
- **CoreStory:** NO. **Contrary evidence:** fixed seed ⇒ per-call deterministic; concern is cross-module global-`rand` coupling.

### ND-CAND-005 — Pointer-address `std::hash<const void*>` in thread-local timing caches
- **Location:** `ccd/skewopt/soLogicCone.h:375,400-402` — `std::hash<const void*>{}` over `key.first`, `key.driver/inst/libCell` inside `std::unordered_map<...>` wrapped by `tbb::enumerable_thread_specific` (`tl_toNodeCache`, `tl_fromNodeCache`, `tl_deltaCapCache`).
- **Suspected mechanism:** Pattern 1.4 (pointer-based hash) / 1.3 (pointer-keyed unordered). Address hashing ⇒ bucket layout varies across runs.
- **Customer pattern/example family:** 1.4 "Pointer-based hash functors"; 1.3.
- **Discovery evidence:** `p1.4.txt`; source read of the cache key hashers.
- **Severity hypothesis:** LOW (latent-only).
- **Origin:** CUSTOMER-PATTERN.
- **CoreStory used:** NO (local source sufficed).
- **Contrary evidence:** these are **lookup-only caches** (hit/miss by pointer identity); the cached *value* is identity-invariant and the maps are not iterated for order-sensitive output ⇒ classic latent-only / likely false-positive per 1.3/1.4 hints. Retained per rule (cannot drop for incomplete observability); flagged latent.

### ND-CAND-006 — `tbb::parallel_reduce` with custom state merge (GLS problem generator)
- **Location:** `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h:312` — `tbb::parallel_reduce(blocked_range, init, body, reduce)` with early-exit `globalDone` atomic.
- **Suspected mechanism:** Pattern 3.1 (parallel reduction) — merge order is work-stealing dependent; combined with a `globalDone` short-circuit whose trip point is schedule-dependent.
- **Customer pattern/example family:** 3.1 "Parallel floating-point reduction".
- **Discovery evidence:** `p3.1.txt`; source read of the reduce lambdas.
- **Severity hypothesis:** MEDIUM–HIGH pending `stateType`/`reduce()` operand types.
- **Origin:** CUSTOMER-PATTERN.
- **CoreStory used:** YES (Q3) — returned `ctomtGlsProblemGenerator.cc:2596 processSccBagIntoCache` ("uses tbb concurrent containers … deterministically assembles a per-driver sccContext"). Neutralizer/contrary hint that final assembly may be canonicalized.
- **Contrary evidence / UNRESOLVED:** `stateType.reduce()` semantics unresolved (associativity of the merged quantity); `globalDone` early-exit may make the reduction *result* schedule-dependent even if the merge is associative.

### ND-CAND-007 — `hardware_concurrency()` grain size in group-latency parallel_for
- **Location:** `ctscto/ctoGrpLatCalc.cc:80` (`std::thread::hardware_concurrency()`), sets `_step` grain for `tbb::parallel_for` at :84.
- **Suspected mechanism:** Pattern 3.5 (thread-count dependency in sizing).
- **Customer pattern/example family:** 3.5.
- **Discovery evidence:** `p3.5.txt`; source read of the parallel_for.
- **Severity hypothesis:** LOW.
- **Origin:** CUSTOMER-PATTERN.
- **CoreStory used:** YES (Q3) — returned `ctoGrpLatCalc.cc:60-182`, confirming the body writes `grpLat[i]` **by independent index** and selects **worst (max) late latency** (commutative).
- **Contrary evidence:** grain size affects scheduling only; per-index independent writes + commutative worst-case selection ⇒ likely safe (3.5 false-positive class). Retained; flagged likely-safe.

### ND-CAND-008 — `std::filesystem::directory_iterator` without ordering (fmax LP solver)
- **Location:** `ccd/ctsccd/fmax/fmaxLpSolverCompressedEndpoints.cc:2176, 2606, 2632` (three `directory_iterator` loops).
- **Suspected mechanism:** Pattern 2.6 (filesystem iteration without sort) → inode/B-tree order, cross-machine ND.
- **Customer pattern/example family:** 2.6.
- **Discovery evidence:** `p2.6.txt`.
- **Severity hypothesis:** MEDIUM pending whether the enumerated files drive result-affecting state vs. logging.
- **Origin:** CUSTOMER-PATTERN. **CoreStory:** NO.

### ND-CAND-009 — `readdir` loops (CTS test util)
- **Location:** `ctsutil/ctsTest.cc:985, 1646` (`while((dp=readdir(dirp)))`).
- **Mechanism:** Pattern 2.6. **Origin:** CUSTOMER-PATTERN. **Severity:** LOW (test utility). **CoreStory:** NO.

### ND-CAND-010 — Developer-toggled "may cause ND" pointer map (ICG estimators)
- **Location:** `icg/ctsICGEstimators.h:70-140` — `template<...> class ctsNdmPtr2ObjectNonNdType` selecting `std::map<ndmPointer<const ndmType>, V, compareNdmPointer<...>>` (**source comment: "may cause ND"**) vs `ndmPtrUnorderedMap` ("not cause ND") via ctor flag `useNonNdMapType`.
- **Suspected mechanism:** Pattern 1.2/3.7 (pointer-keyed ordered map; comparator semantics decide determinism). Developer explicitly acknowledges an ND risk on the `std::map` branch.
- **Customer pattern/example family:** 1.2 / 3.7 (project wrapper w/ order-sensitive use).
- **Discovery evidence:** CoreStory Q1 hit → source read of the template.
- **Severity hypothesis:** MEDIUM.
- **Origin:** **CORESTORY-EXPANSION.** The mechanical scan **missed** this: the key is a smart-pointer wrapper `ndmPointer<const ndmType>` (no literal `*`), so YAML regex 1.2 (`[A-Za-z_]\w*\s*\*`) does not match. CoreStory surfaced a candidate local pattern-scan could not.
- **CoreStory used:** YES (Q1). Returned `icg/ctsICGEstimators.h` + `include/` mirror as "configurable ND vs non-ND pointer-to-object map."
- **Contrary evidence / UNRESOLVED:** `compareNdmPointer<>` semantics (id-order vs handle/address-order) are **UNRESOLVED** (external); the default value of `useNonNdMapType` at call sites is UNRESOLVED — both are load-bearing for realness.

### ND-CAND-011 — Thread-count-partitioned TNS/WNS reduction (fmax timing cost)
- **Location:** `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:272-395` — `tbb::parallel_for(0, numberOfThreads, ...)`: per-thread `resultsPerThreadTNS[t]+=double(endpointSlack)` and per-thread WNS/most-violated-path, merged over `threadIndex`.
- **Suspected mechanism:** Pattern 3.1 (parallel FP reduction) + 3.5 (thread-count dependency). TNS is a `double` sum whose *grouping* depends on `numberOfThreads`; WNS worst-path tie-break depends on which thread's fixed range holds the tying path.
- **Customer pattern/example family:** 3.1 / 3.5.
- **Discovery evidence:** CoreStory Q3 hit → source read of the full reduction/merge.
- **Severity hypothesis:** MEDIUM.
- **Origin:** **CORESTORY-EXPANSION** (surfaced by Q3; not in the local high-signal sample set).
- **CoreStory used:** YES (Q3).
- **Contrary evidence (key qualification nuance):** input is **index-partitioned** (`iteratorRanges[threadCount]`, not work-stealing) and the merge loop runs in **deterministic thread-index order** with prefix offsets ⇒ result is *deterministic for a fixed `numberOfThreads`*. The ND is **thread-count / platform sensitivity**, not equivalent-run ND — unless `numberOfThreads` derives from `hardware_concurrency`. `numberOfThreads` source UNRESOLVED.

---

## B. CoreStory-surfaced candidate PATHS (to scan/qualify)

### ND-CAND-012 — Sibling pin-clustering engine
- **Location:** `mscts/msgts/msgtsClustering.cc` (643 KB; e.g. clustering entry ~5899, sorts at 1170/1324/5539).
- **Suspected mechanism:** same clustering-order / selection family as ND-CAND-003 (distinct implementation: MSGTS flat-sink pin clustering).
- **Origin:** **CORESTORY-EXPANSION** (Q2 surfaced it as a sibling clustering implementation).
- **Discovery evidence:** CoreStory Q2 ranking; `p1.1.txt` shows its sorts are over value vectors (`l_distVec`, `cost_vec`).
- **Severity hypothesis:** UNRESOLVED — retained as a path to scan for RNG/ordering-driven cluster assignment.

### ND-CAND-013 — `dosUnorderedSet<T*>` wrapper sets (unresolved hash)
- **Locations:** `mscts/msui/msuiReportPowerTaps.cc:71`, `mscts/msui/msuiGetPowerTaps.cc:66` (`dosUnorderedSet<ndmBlkInst*>`); `cts/ctsManager.h:363` (`dosUnorderedSet<ndmTerm*> _processedDriverTermsInGbgCts`); `ccd/util/ccdUtil.h:294` (`dosUnorderedSet<ndmNet*>&`).
- **Suspected mechanism:** Pattern 3.7 (project wrapper container, pointer key). If `dosUnorderedSet` hashes by address ⇒ 1.3-class ND on iteration.
- **Customer pattern/example family:** 3.7.
- **Discovery evidence:** `p3.7.txt`; wrapper definition not in tree.
- **Severity hypothesis:** MEDIUM.
- **Origin:** CUSTOMER-PATTERN.
- **CoreStory used:** YES (Q1) — did not resolve the wrapper's hash implementation (external `dos*` library not indexed under project 10); returned CTS-side conversion helpers (`ctsObjId`) instead.
- **Contrary evidence / UNRESOLVED:** `dosUnorderedSet` hash/equality semantics **UNRESOLVED** (external). Per qualification lesson #4, an unordered pointer-valued wrapper does not by itself establish address hashing.

---

## C. Retained cluster candidates (recall-preserving; full raw files retained)

Each cluster is a retained candidate space (not dropped). Representative sites given; per-site promotion happens at qualification. Counts are mirror-deduped where noted.

### ND-CAND-014 — Pointer-keyed default-comparator `std::set`/`std::map` residue
- **Pattern:** 1.2. **Raw:** 2,955 hits / 629 files (`p1.2.txt`); **no-on-line-comparator, mirror-deduped:** 983 (`p1.2_narrow_dedup.txt`).
- **Dominant key types:** `ndmTerm`(289), `ndmHier`(125), `ndmInst`(120), `ndmModule`(104), `ndmNet`(47), + CTS types (`costEp`, `msTreeNode`, `ctsTreeNode`, `fmaxVariable`, `cstrSkewGroup`, …).
- **Origin:** CUSTOMER-PATTERN. **CoreStory:** partial (Q1).
- **Narrowing evidence (for qualification, not deletion):** much of the residue resolves to typedef'd stable-comparator aliases (e.g. `cnmNdmInst2NodeMap` uses `compareObjPtr`) or membership-only use; the genuine 1.2 defect subset is default-`std::less<T*>` maps that are **iterated** into order-sensitive sinks. Auto-dismiss rule (1.2) applies to membership-only sites.

### ND-CAND-015 — Pointer-keyed default-hash `std::unordered_*` residue
- **Pattern:** 1.3. **Raw:** 531 / 188 files (`p1.3.txt`); **no-on-line-hash, mirror-deduped:** 368 (`p1.3_narrow_dedup.txt`).
- **Dominant key types:** `ndmTerm`(220), `ndmInst`(35), `ndmModule`(23), `ctsXformProblem`(16), `fmaxVariable`(14), `soIcdSink`(13), `ctoSclkBag`(5)…
- **Origin:** CUSTOMER-PATTERN. Includes ND-CAND-005 as a confirmed instance. Stage-3 3.3 narrowing (iterated + order-sensitive sink) required per site.

### ND-CAND-016 — MT shared-container writes
- **Pattern:** 3.2. **Raw:** 203 hits / 46 files (`p3.2.txt`) — `tbb::concurrent_*`, `tbb::parallel_for`, `std::async`.
- **Representatives:** `ctomtGlsProblemGenerator` concurrent SCC cache (ND-CAND-006), `fmaxTimingCostFunction` (ND-CAND-011).
- **Origin:** CUSTOMER-PATTERN. CoreStory (Q3) surfaced representatives.

### ND-CAND-017 — Post-collection use without canonical ordering
- **Pattern:** 3.6 (broad seed). **Raw:** 557 hits / 173 files (`p3.6.txt`). Stage-3 narrowing mandatory (unstable source + pre-sort-consumption + order-sensitive consumer).
- **Origin:** CUSTOMER-PATTERN.

### ND-CAND-018 — `tbb::concurrent_hash_map` check-then-act
- **Pattern:** 4.4. **Raw:** 36 hits / 21 files (`p4.4.txt`).
- **Representative:** `ctomtGlsProblemGenerator` tbb concurrent containers (Q3 note: "safe to call concurrently for distinct bags" — to verify accessor scoping).
- **Origin:** CUSTOMER-PATTERN.

### ND-CAND-019 — Pointer hash functors (beyond ND-CAND-005)
- **Pattern:** 1.4. **Raw:** 16 hits / 8 files (`p1.4.txt`).
- **Sites:** `ctscto/ctosc/ctoscGlobal.h:274` `std::hash<ctoSclkBag*>`; `ctoscFilter.h:334-335` `std::hash<const ndmInst*>`/`<const ndmModule*>`; `ctscstr/ctscstrDesign.h:92` `std::hash<const ndmDesign*>`.
- **Origin:** CUSTOMER-PATTERN. Realness depends on whether these unordered containers are iterated for output.

### ND-CAND-020 — Static MT-ND: mutable lazy caches / mutable mutex families
- **Pattern:** 4.1 / 4.2. **Raw:** 4.1 = 2 hits (`ctsutil/ctsInfra.h:838 mutable termSclksMapType _termValidSclkCache`); 4.2 = 40 hits / 26 files (`p4.2.txt`).
- **Origin:** CUSTOMER-PATTERN. Requires MT-hunt/TSan-style deep read (Stage 3b) for observability; retained as static candidates.

### ND-CAND-021 — `getFullName()/getPathName()` as map key / hash input
- **Pattern:** 2.2. **Raw:** 100 hits / 21 files (`p2.2.txt`).
- **Origin:** CUSTOMER-PATTERN. Naming-key stability + perf; promote where the name string is a live key feeding order-sensitive logic.

---

## D. Dismissed buckets (regex-level filters; recorded, not candidates)

Recorded per SKILL `dismissed_buckets`. These are regex artifacts, not retained ND candidates. (Distinct from realness classifications, which stay in the candidate space above.)

- **DB-1 — Value/scalar `std::sort` (Pattern 1.1).** 404 raw / 88 mirror-deduped 2-arg sorts (`p1.1_narrow_dedup.txt`) are overwhelmingly over **value/scalar vectors** (`pathDelays`, `slacks`, `coords`, `clockPeriodMap`, `netWireLengths`, `cornerLatencies`, `l_distVec`, `cost_vec`, …) with deterministic `operator<`. One site is explicitly commented "sort to get deterministic order" (`ctsLazyCostGroup.cc:932`). Pattern 1.1 false-positive class. Residual object-vector sorts to spot-check at qualification: `_treeNodes`, `_corners`, `_modes`, `masterClocks`, `_icgEnNodes`, `events` (folded into ND-CAND-014 if pointer-typed).
- **DB-2 — House-comparator wrapper hits (Pattern 3.7).** Majority of the 288 `p3.7.txt` hits use `ndmObjectHandleNS::compareObjPtr`, `dosContainer::keyCompare`, `ndmObjPtrCmpType`, `ndmPtrMap`/`ndmPtrSet` — safe-adopters (the fix, not the bug).
- **DB-3 — Mirror duplicates.** `include/`, `*/include/`, `*/core/include/` trees mirror module sources (2–4× inflation). Deduped for candidate counting; raw kept.
- **DB-4 — Random-test files (Pattern 1.5).** `ctsui/ctsuiscRandomTest.cc`, `ctsui/ctsuiCtoRandomTest.cc`, `ctsutil/test/ctsGfxDrawTest.cc` are randomized *test* harnesses; several already seed from IDs (`srand(drvTerm->getIdLong())`). Out-of-scope test randomness; not promoted (kept visible).
- **DB-5 — Empty patterns.** 2.3, 2.7, 2.8, 2.9, 4.3, 4.5, 4.6 produced 0 hits in CTS.

---

## Freeze summary (denominator)

- **Individual candidates:** ND-CAND-001 … 011 (11).
- **CoreStory-surfaced paths:** ND-CAND-012, 013 (2).
- **Cluster candidates:** ND-CAND-014 … 021 (8).
- **Total frozen candidate IDs:** **21.**
- **Origin split:** CUSTOMER-PATTERN = 17 (001,002,004,005,006,007,008,009,013,014,015,016,017,018,019,020,021); CORESTORY-EXPANSION = 3 (010,011,012); BOTH = 1 (003).
- **CoreStory materially broadened evidence/path:** ND-CAND-003 (RNG→topology), ND-CAND-010 (new candidate scan missed), ND-CAND-011 (new candidate), ND-CAND-012 (sibling path). = 4.
- **CoreStory calls with no useful expansion:** Q1 did not resolve `dosUnorderedSet` external hash semantics (ND-CAND-013 remains UNRESOLVED).
