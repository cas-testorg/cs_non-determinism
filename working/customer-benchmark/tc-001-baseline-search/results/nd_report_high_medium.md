# Non-Determinism Analysis — CTS Module

**Module:** `C:\Users\carys\cts`  
**Scan date:** 2026-09-09  
**Analyzer:** nd-code-analyzer v1.4.0 (manual Stage 1–5; `scan_nd.py` / `render_report.py` not present in skill tree)  
**Severity floor:** HIGH and MEDIUM (real findings only)  
**Patterns evaluated:** 27 (catalog `references/nd-patterns.yaml`)

---

## 1. Executive summary

| Severity | Real findings |
|----------|---------------|
| **HIGH** | 2 |
| **MEDIUM** | 2 |
| **LOW** | *(omitted per request)* |

| Category | HIGH | MEDIUM |
|----------|------|--------|
| random | 1 | 0 |
| container / sorting | 1 | 0 |
| parallel / arithmetic | 0 | 2 |

**Top hot files (confirmed real issues):**

1. `ccd/ctsccd/fmax/fmaxLpSolver.cc` — unseeded RNG in LP variable subset selection  
2. `ctscto/ctoFlowClone.cc` — pointer-keyed `std::set` drives CTO restructuring order  
3. `ccd/ctsccd/fmax/include/fmaxTimingCostFunction.h` — parallel TNS fold (thread-count sensitive)  
4. `ctscto/ctoGrpLatCalc.cc` — `hardware_concurrency()` grain sizing vs configured thread budget

**Overall posture:** CTS core code largely uses project-stable containers (`ndmPtrMap`, `ndmObjPtrCmpType`, `dosSet`) on QoR paths. The highest-risk confirmed defects cluster in **CCD fmax LP** (random subset + parallel cost fold) and **CTO pre-opt restructuring** (address-ordered driver sets). Many Stage-1 hits (pointer `std::set` used only for membership / visited tracking, value-type sorts, `ndmPtrMap` adopters) were triaged out.

---

## 2. Critical background — ID / comparator discipline

When keys are NDM object pointers, **address order is not logical order**. Stable choices already used in this tree:

| Mechanism | Typical use |
|-----------|-------------|
| `ndmObjectHandleNS::compareObjPtr` | `std::set` / `std::map` on `ndm*` |
| `ndmObjPtrCmpType` | CTS wrapper comparator |
| `ndmPtrMap` / `ndmPtrSet` / `dosSet` | Deterministic project containers |
| `ctsTermId` / `getIdLong()` | O(1) stable numeric keys |

**Cost rule of thumb:** prefer stable ID comparators over sorting hot `unordered_*` containers on every iteration; canonicalize once at the boundary where order becomes observable (report emission, tie-break, commit order).

---

## 3. Top summary table

| # | Issue | Real? | Triggering controls | Summary |
|---|-------|-------|---------------------|---------|
| H1 | `fmaxLpSolver` UNIFORM subset RNG | **real** | `selectActiveVariableSubset(..., UNIFORM, ...)` | `std::random_device` seeds `std::mt19937`; variable subset differs run-to-run → LP dimension / solution path changes |
| H2 | `ctoFlow::restructFlow` pointer sets | **real** | Pre-opt restructuring (`restructFlow()`) | `std::set<ndmTerm*>` default comparator; iteration order selects clone/shield sequence; mutating passes change design for later drivers |
| M1 | Fmax parallel TNS fold | **real** | Fmax LP evaluate, `_maxThreads > 1`, TNS objective | Per-thread `double` TNS sums folded in thread-index order; FP association varies with thread count |
| M2 | `calcGrpLatencyBatch` grain from HW concurrency | **real** | `isUseClockGroupLatencyMT` / `_useCgLatMT`, MT branch after write-lock suspend | `_step` derived from `std::thread::hardware_concurrency()` instead of `getMaxThreadCount()`; schedule/grain differs from rest of CTS MT |

---

## 4. HIGH severity findings

### H1 — Unseeded RNG in fmax LP variable subset (`UNIFORM`)

| Field | Detail |
|-------|--------|
| **Pattern** | 2.1 — random without fixed seed |
| **File:line** | `ccd/ctsccd/fmax/fmaxLpSolver.cc` ~3892–3903 |
| **Tier** | 1 |

**Current code (excerpt):**

```cpp
std::random_device rd;
std::mt19937 generator(rd());
std::uniform_int_distribution<> uniform(1, cumulativeOccurences.back());
// ...
size_t count = size_t(uniform(generator));
size_t resultIndex = findWithBinarySearch(count, cumulativeOccurences);
result.insert(occurenceVector[resultIndex].second);
```

**Why it is real:** `selectActiveVariableSubset` builds the active LP variable set. Under `subsetType == UNIFORM`, sampling is driven by non-deterministic `random_device` entropy. Different subsets change which constraints/variables participate in the reduced LP → different optimizer path and QoR.

**Downstream observability:** `result` is consumed by fmax LP setup (variable activation / reduced model). This is on the optimization hot path, not debug-only.

**Controls / gating:** Requires `coveragePercentage ∈ (0,1)` and `VariableSubsetType::UNIFORM`. Other subset modes (`MOST_FREQUENT`, `LEAST_FREQUENT`, `BEST_POWER`) sort deterministically and are not affected.

**Performance note:** Fix with a deterministic seed (app option or design checksum hash) preserves sampling intent without changing asymptotic cost.

#### Fix suggestions

**Version A (simple):** Fixed seed for repeatability:

```cpp
std::mt19937 generator(0xC71C0000u); // or hash from design/checksum
```

**Version B (robust):** Seed from stable design id + user-visible app option default:

```cpp
const uint32_t seed = ctsAppOptions::get_fmax_uniform_subset_seed(); // default non-zero constant
std::mt19937 generator(seed);
```

**Version C (maximum safety):** Deterministic stratified selection without RNG (walk cumulative distribution with fixed stride from sorted `occurenceVector`).

**Rationale:** Version B matches Fusion “app option as control surface” convention and allows regression override.

**Code ownership (Perforce):** Not resolved — local workspace without depot mapping / `p4` client. Re-run Stage 4b with `p4-code-ownership` when depot path is known.

---

### H2 — Pointer-keyed `std::set<ndmTerm*>` in CTO restructuring

| Field | Detail |
|-------|--------|
| **Pattern** | 1.2 — `std::set<T*>` with default `std::less<T*>` |
| **File:line** | `ctscto/ctoFlowClone.cc` 1884–1885, 1993–2025 |
| **Tier** | 1 |

**Current code (excerpt):**

```cpp
std::set<ndmTerm*> candidates;
std::set<ndmTerm*> lpCandidates;
// ... populate from driver scan ...
for (std::set<ndmTerm*>::iterator it = lpCandidates.begin(); it != lpCandidates.end(); ++it) {
  // cloneBufferInverter / bufShieldBufferInverter — mutates design
}
for (std::set<ndmTerm*>::iterator it = candidates.begin(); it != candidates.end(); ++it) {
  // further restructuring attempts
}
```

**Why it is real:** Set iteration order follows pointer addresses (ASLR / allocator layout). Each iteration performs **mutating** transforms (`cloneBufferInverter`, `bufShieldBufferInverter`). Earlier transforms change netlist/timing state seen by later drivers → path-dependent restructuring outcome.

**Downstream observability:** Pre-opt restructuring changes buffer/inverter placement and shielding → CTO QoR and downstream route/CTS state.

**Controls / gating:** `ctoFlow::restructFlow()` pre-opt restructuring path; `_preOptRestructMode` set true in this function.

**Performance note:** Replacing with `ndmObjPtrCmpType` or collecting into `vector` + sort by `ctsTermId` adds O(N log N) once per pass — acceptable outside inner loops.

#### Fix suggestions

**Version A:**

```cpp
std::set<ndmTerm*, ndmObjPtrCmpType> candidates;
std::set<ndmTerm*, ndmObjPtrCmpType> lpCandidates;
```

**Version B:** Deterministic vector + explicit sort for logging stability:

```cpp
std::vector<ndmTerm*> lpCandidates;
// ... insert with dedup via std::set<ndmTerm*, ndmObjPtrCmpType> or sort+unique ...
std::sort(lpCandidates.begin(), lpCandidates.end(), ndmObjPtrCmpType{});
```

**Version C:** Sort by `(getIdLong(), getObjectType(), compareObjPtr)` for cross-type safety.

**Rationale:** Version A is minimal and matches project convention (`ctoFlow.cc` already uses `ndmObjPtrCmpType` elsewhere).

**Code ownership (Perforce):** Not resolved (local tree).

---

## 5. MEDIUM severity findings

### M1 — Parallel TNS accumulation in `TimingCostFunction::evaluate`

| Field | Detail |
|-------|--------|
| **Pattern** | 3.1 / 3.5 — parallel FP reduction; thread-count-dependent partition |
| **File:line** | `ccd/ctsccd/fmax/include/fmaxTimingCostFunction.h` ~270–337 |
| **Tier** | 2 |

**Mechanism:** `tbb::parallel_for` over thread indices fills `resultsPerThreadTNS[threadCount]`; serial fold:

```cpp
for (size_t threadIndex = 0; threadIndex < numberOfThreads; ++threadIndex) {
  resultTNS += resultsPerThreadTNS[threadIndex];
}
```

**Why it is real:** Floating-point addition is not associative. Different `_maxThreads` / partition boundaries change the sum at observability precision → TNS cost value can differ across machines or thread settings even with identical logical work.

**Downstream observability:** `resultTNS` feeds LP cost evaluation and stopping criteria in fmax optimization.

**Controls / gating:** `_maxThreads` from `crmResources::getMaxThreadCount()` in `fmaxLpSolver.h`; active when parallel evaluate path runs with TNS objective.

**Performance note:** Deterministic Kahan/compensated sequential fold after per-thread sums preserves parallelism without changing O(paths) structure. Full serial fold is correct but slower — prefer compensated merge.

#### Fix suggestions

**Version A:** Compensated sequential merge of per-thread partial sums.

**Version B:** Fixed minimum thread count for cost evaluation (document as app option; trades perf for repeatability).

**Version C:** Use integer / fixed-point micro-unit accumulation if QoR tolerance allows.

**Code ownership (Perforce):** Not resolved (local tree).

---

### M2 — `hardware_concurrency()` for MT grain in group-latency batch

| Field | Detail |
|-------|--------|
| **Pattern** | 3.5 — thread-count / partition sizing dependency |
| **File:line** | `ctscto/ctoGrpLatCalc.cc` 80–88 |
| **Tier** | 2 |

**Current code (excerpt):**

```cpp
size_t numT = std::thread::hardware_concurrency();
_step = jobSize / numT + 1;
tbb::parallel_for(tbb::blocked_range<size_t>(0, idx.size(), _step), [&](auto r) {
  for (auto i = r.begin(); i != r.end(); ++i) { calcGrp(idx[i]); }
});
```

**Why it is real:** Grain size depends on **hardware-reported** concurrency, while most CTS MT uses `ctsscUtil::getMaxThreadCount()` / `crmResources::getMaxThreadCount()`. Different hosts → different TBB chunk schedules. Per-index `grpLat[i]` writes are disjoint, so this is primarily **schedule / timing / floating tie-break exposure**, not arbitrary memory corruption.

**Downstream observability:** Group latency vector → CTO cost / clock-group latency decisions (`ctoFlow`, `ctoFlowMgr`).

**Controls / gating:** `_useCgLatMT` / `isUseClockGroupLatencyMT()`; requires successful write-lock suspend (else ST fallback).

**Performance note:** Aligning `numT` with `getMaxThreadCount()` is zero-cost and improves cross-machine consistency.

#### Fix suggestions

**Version A:**

```cpp
size_t numT = std::max(size_t(1), size_t(ctsscUtil::getMaxThreadCount()));
```

**Version B:** Reuse `ctsMtTaskRunner` blocked-range helper (already caps with CRM max ∧ TBB max concurrency).

**Code ownership (Perforce):** Not resolved (local tree).

---

## 6. Downstream proof (condensed)

| ID | Suspect source | Caller → consumer chain | Observable sink |
|----|----------------|-------------------------|-----------------|
| H1 | `uniform(generator)` sampling | `selectActiveVariableSubset` → LP model build → fmax solve | Active variable set / LP solution / QoR |
| H2 | `std::set<ndmTerm*>` iteration | `restructFlow` → `cloneBufferInverter` / `bufShieldBufferInverter` | Netlist mutations, CTO QoR |
| M1 | Parallel per-thread TNS sum | `TimingCostFunction::evaluate` → fmax cost loop | Scalar TNS cost, optimizer decisions |
| M2 | `_step` from HW concurrency | `calcGrpLatencyBatch` → `calcGrp` → `grpLat[]` → flow cost | Group latency metrics |

**Neutralizers checked:** Membership-only pointer sets (`visitedTerms`, `processedDrvSet`), `ndmPtrMap`/`dosSet` adopters, post-loop `std::sort` on value types, TBB aggregate-then-sort idioms in lazy TNS — dismissed (see §9).

---

## 7. Performance-aware fix direction

| ID | Lookup impact | Allocation / sort risk | Recommendation |
|----|---------------|------------------------|----------------|
| H1 | None | None | Deterministic seed or stratified pick — no hot-loop cost |
| H2 | None | One-time set/map per restructuring pass | `ndmObjPtrCmpType` — negligible vs timing queries in same function |
| M1 | None | Small per-thread buffers already allocated | Compensated merge — O(threads) extra |
| M2 | None | None | Use configured thread cap — aligns with existing MT infra |

---

## 8. Non-real classifications (representative)

| Bucket | Example sites | Verdict |
|--------|---------------|---------|
| Membership-only pointer set | `ctoArea.cc` `processedDrvSet`, `ctoscLevelFlow` `seedMap`, most `visitedTerms` | **false-positive** for order ND (only `find`/`insert`) |
| Safe adopter | Widespread `ndmPtrMap`, `ndmObjPtrCmpType`, `dosSet<ndmInst*>` | **safe-adopter** |
| Value-type sort | `ctsSchCts.cc` `nodeAndToggleRate` (`operator<` on toggle rate) | **false-positive** |
| Test / debug RNG | `ctsui/*RandomTest*`, `skewgrp/ctsSkewgroup.cc` test harness `srand(time)` | **dead/debug** (not production flow) |
| MT lazy cache (unproved MT reachability) | `ctsInfra::_termValidSclkCache`, `_collectSclkCache` | **latent-only / MT-unreachable** on current call graph (see `cts_nd_details.md`) |
| Concurrent map check-then-act | `processSccBagIntoCache` | **latent-only** (disjoint bag keys; assemble re-canonicalizes) |

---

## 9. Dismissed buckets (Stage-1 mechanical noise)

| Pattern | Bucket | Count (approx.) | Rationale |
|---------|--------|-----------------|-----------|
| 1.2 | Pointer `std::set` / `std::map` with explicit stable comparator | 40+ | `ndmObjPtrCmpType`, `compareObjPtr`, `comparePtr` |
| 1.2 | Pointer set membership / visited only | 60+ | No order-sensitive consumer |
| 1.3 | Integer-keyed `unordered_*` | 30+ | Not pointer-key iteration ND |
| 1.1 | Two-arg sort on value / custom `operator<` | 50+ | Not address sort |
| 3.3 | Range-for on `vector` in files declaring `unordered_*` | — | Type resolution drops hit (Pattern 3.3 narrowing) |
| 3.7 | `ndmPtrMap` / `ndmPtrSet` iteration | 20+ | Wrapper provides stable order |
| 4.x | No hits for 4.3 / 4.5 / 4.6 in CTS | 0 | — |

---

## 10. CL-mined semantic checklist coverage

| Checklist item | CTS result |
|----------------|------------|
| Post-collection canonicalization (3.6) | No promoted finding; lazy TNS uses explicit sort comments (`ctsLazyCostGroup.cc:932`) |
| Project wrapper containers (3.7) | Dismissed — widespread safe `ndmPtrMap` usage |
| Graph / geometry traversal | No incomplete canonicalization promoted |
| Stale cached state | `_termValidSclkCache` logged as latent-only (invalidation path not fully audited) |
| Delay-sharing / scene reuse | Not promoted without downstream proof in this pass |
| Concurrency / write-lock discipline | `ctoGrpLatCalc` suspend pattern reviewed; M2 grain sizing only |
| Deterministic control-path normalization | Not promoted |
| Checksum observability | Not promoted |

---

## 11. Generic fix patterns (excerpt)

**Pointer containers:** Prefer `ndmPtrMap` / `std::set<T*, ndmObjPtrCmpType>` over raw `std::set<T*>`.

**Unordered iteration:** If iteration order matters, copy keys to `vector`, sort with stable comparator, then consume.

**Parallel FP:** Per-thread locals + deterministic merge (compensated sum or integer micro-units).

**Randomness:** Never `std::random_device` on QoR paths; use fixed or app-option seed.

---

## 12. Coding guidelines

**DO**

- Use `ndmObjectHandleNS::compareObjPtr` / `ndmObjPtrCmpType` for all pointer-keyed ordered containers on QoR paths.
- Canonicalize once before first order-sensitive consumer (commit, tie-break, report).
- Align MT grain sizing with `getMaxThreadCount()` across a flow.
- Seed RNG from app options with documented defaults for repeatability.

**DON'T**

- Iterate `std::set<T*>` / `std::unordered_*<T*>` (default hash) when loop body mutates shared design state.
- Use `std::random_device` for production optimization sampling.
- Assume parallel `double` accumulation is associative across thread counts.

---

## 13. Module-specific summary

The CTS tree is **mixed but generally aware** of ND pitfalls: CTO and CCD code frequently uses stable comparators and project pointer maps. The remaining **HIGH** surface is narrow but impactful — **fmax LP** still uses entropy-seeded sampling for uniform variable subsets, and **CTO restructuring** still walks address-ordered driver sets while applying mutating transforms. **MEDIUM** issues are primarily **parallel numeric and scheduling consistency** (fmax TNS fold; group-latency MT grain). MSCTS (`mscts/`) contains additional pointer `unordered_*` declarations; most triaged usages are membership-only or reporting — not promoted without per-site downstream proof in this pass.

---

## 14. Verification notes

| Item | Detail |
|------|--------|
| **Search backend** | ripgrep against `nd-patterns.yaml` (27 patterns); manual Stage 2–3 triage |
| **Source root** | Local workspace `c:\Users\carys\cts` (no `.synmake` / `DEVROOTS`) |
| **Navigation** | Text search + targeted file reads; `clangd_query.py` / `nwtn-src-cpp-code-navigation` not available (not under `nwtn/src`) |
| **App options** | `icc2query` not run |
| **Perforce ownership** | Skipped — no depot mapping in local client |
| **Prior work reused** | `cts_nd_details.md`, `nd_mt_candidates_discovery.md` for MT/static overlap on lazy caches |
| **Scope limits** | Test directories deprioritized; LOW severity omitted; `scan_nd.py` absent — candidate counts are approximate from ripgrep |

---

*Generated by nd-code-analyzer workflow. Re-run with depot access for Perforce ownership blocks and app-option defaults.*
