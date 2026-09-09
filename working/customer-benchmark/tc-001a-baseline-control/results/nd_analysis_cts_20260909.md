# ND Code Analysis Report — `cts`

**Module:** `C:\Users\carys\cts`  
**Generated:** 2026-09-09  
**Scanner:** ripgrep Stage-1 (HIGH/MEDIUM patterns; `scan_nd.py` not installed in skill tree)  
**Branch / depot:** local workspace (no Perforce client on PATH)  
**Severity floor:** MEDIUM (LOW omitted)  
**Patterns evaluated:** 22 of 27 catalog entries (skipped LOW defaults 1.10, 3.4, 4.6)

---

## 1. Executive summary

| Metric | Value |
|---|---|
| Raw Stage-1 candidates | 4535 hits / 817 files |
| Real HIGH findings | **1** |
| Real MEDIUM findings | **6** |
| Real LOW findings | 0 (filtered) |
| Dismissed buckets | 23 (see §11) |

**By category (real findings only):**

| Category | HIGH | MEDIUM |
|---|---|---|
| container | 1 | 0 |
| sorting | 0 | 6 |

**Top hot files (real findings):**

1. `ctscto/ctoFlowClone.cc` — HIGH mutating pointer-set iteration  
2. `mscts/mstap/msTapSubtreeSyn.cc` — MEDIUM distance-tie sorts (×2)  
3. `ctscto/ctosc/ctomt/ctomtReloc.cc` — MEDIUM min/max delay ties (×2)  
4. `ctscto/ctosc/ctoscLoadPartition.cc` — MEDIUM SP sink tie  
5. `ctscto/ctoUtil.cc` — MEDIUM SP-filter min-delay index  

**Verdict:** CTS is mostly ND-hardened (many `ndmObjPtrCmpType` adopters; MT paths largely latent/idempotent). One **HIGH** pre-opt restructuring path still iterates address-ordered driver sets into mutating clone/shield. Remaining **MEDIUM** issues are equal-key / equal-delay tie-breaks that reach tap placement or relocation QoR.

---

## 2. Critical background — ID system reminder

Pointer addresses are not stable across runs (ASLR, allocator). Prefer:

| Approach | Cost | When |
|---|---|---|
| `getId()` / `getIdLong()` | O(1) | Unique within type/context |
| `ndmObjPtrCmpType` / `ndmObjectHandleNS::compareObjPtr` | O(1)–cheap | Gold-standard pointer ordering |
| `dosContainer::keyCompare` / `ndmPtrMap` | project default | Sets/maps of ndm objects |
| Sort-before-iterate snapshot | O(N log N) once | Keep unordered for lookup; canonicalize at sink |

Do **not** blindly replace hot `unordered_*` with `std::map` — prefer stable iteration at the consumer boundary.

---

## 3. Top summary table

| # | Severity | Realness | Issue | Controls (short) | Summary |
|---|---|---|---|---|---|
| 1 | HIGH | real | `ctoFlowClone.cc:1884` pointer `std::set` iteration | CTO `restructFlow` pre-opt | Address order drives clone/shield + early-break quota |
| 2 | MEDIUM | real | `msTapSubtreeSyn.cc:285` distance-only sort | MSCTS odd-fanout 2→1 | Equal-distance ties pick 1/4 repeater anchor |
| 3 | MEDIUM | real | `msTapSubtreeSyn.cc:805` distance-only sort | MSCTS recursive cluster | Equal-coord ties split cluster membership |
| 4 | MEDIUM | real | `ctoscLoadPartition.cc:136` min_element | MTCTO load partition | Equal-delay SP sink index incomplete tie-break |
| 5 | MEDIUM | real | `ctomtReloc.cc:868` max_element | MTCTO Gskew reloc | Tied max delay → first arc-order load |
| 6 | MEDIUM | real | `ctomtReloc.cc:882` min_element | MTCTO Gskew reloc | Tied min delay → first arc-order load |
| 7 | MEDIUM | real | `ctoUtil.cc:4384` min_element | CTO SP-filter reloc | Tied min delay gates gain acceptance |

---

## 4. HIGH findings

### H1 — Address-ordered driver sets drive mutating pre-opt restructuring

| Field | Value |
|---|---|
| Pattern | **1.2** — `std::set` / `std::map` with pointer key, default comparator |
| File | `ctscto/ctoFlowClone.cc:1884` |
| Severity | HIGH (default HIGH) |
| Realness | real |

**Description.** `ctoFlow::restructFlow()` builds `std::set<ndmTerm*>` / `lpCandidates` with default address ordering, then iterates both to call `cloneBufferInverter` / `bufShieldBufferInverter`. Accepted transforms mutate netlist/timing for later drivers. The non-LP loop early-exits after ~10% of `maxClockTree`, so visit order also selects which drivers are attempted.

**Current shape:**

```cpp
std::set<ndmTerm*> candidates;
std::set<ndmTerm*> lpCandidates;
// ... collect drivers ...
for (auto it = lpCandidates.begin(); it != lpCandidates.end(); ++it) {
  if (cloneBufferInverter(*it)) { ... }
  else if (bufShieldBufferInverter(*it)) { ... }
}
for (auto it = candidates.begin(); it != candidates.end(); ++it) {
  // ...
  if (countCands > (int)(10 * maxClockTree / 100)) break;
}
```

**Version A (Simple):**

```cpp
std::set<ndmTerm*, ndmObjPtrCmpType> candidates;
std::set<ndmTerm*, ndmObjPtrCmpType> lpCandidates;
```

**Version B (Robust):** populate `std::vector<ndmTerm*>`, `sort`+`unique` with `ndmObjPtrCmpType`, then iterate.

**Rationale.** Version A matches existing CTO convention and preserves set semantics.

**Code ownership (Perforce).** Depot not resolved — local tree, `p4` unavailable. Function header author: Moez Cherif (June 2015).

---

## 5. MEDIUM findings

### M1 — Distance-only sort ties pick 1/4 repeater anchor

| Field | Value |
|---|---|
| Pattern | **1.1** (tie-break gap on distance key) |
| File | `mscts/mstap/msTapSubtreeSyn.cc:285` |
| Realness | real |

`std::sort(termDistances)` uses distance-only `node::operator<`. Odd-fanout path takes the first sorted load as `load1` for `instantiateRepeater`.

**Fix A:**

```cpp
std::sort(termDistances.begin(), termDistances.end(),
  [](const node& a, const node& b) {
    if (a.getDist() != b.getDist()) return a.getDist() > b.getDist();
    return a.getObj()->getId() < b.getObj()->getId();
  });
```

**Perf:** O(1) tie-break; no extra container.

---

### M2 — Distance-only sort ties split recursive clusters

| Field | Value |
|---|---|
| Pattern | **1.1** |
| File | `mscts/mstap/msTapSubtreeSyn.cc:805` |
| Realness | real |

Same comparator; first `size1` entries → `loadTerms1`, rest → `loadTerms2`, then recursive `doClustering`. Equal X/Y ties change cluster membership.

**Fix:** same id tie-break as M1 (or fix `node::operator<` once for both call sites).

---

### M3 — SP sink `min_element` incomplete tie-break

| Field | Value |
|---|---|
| Pattern | **1.9** |
| File | `ctscto/ctosc/ctoscLoadPartition.cc:136` |
| Realness | real |

Lambda compares early/late delays but returns `false` on full ties → first equal sink in `_sinks` wins. `_spSinkPos` gates binary partition inclusion.

**Fix A:** final `return ndmObjPtrCmpType{}(s1, s2);` in the comparator.

---

### M4 / M5 — Gskew relocation min/max delay ties

| Field | Value |
|---|---|
| Pattern | **1.9** |
| Files | `ctscto/ctosc/ctomt/ctomtReloc.cc:868` (max), `:882` (min) |
| Realness | real |

Default float `max_element` / `min_element`; tied extrema pick first index → `groupedLoads[i]` for critical-path direction candidates.

**Fix A:** single-pass index scan with `(delay, termId)` lexicographic compare.

---

### M6 — SP-filter min-delay index gates gain

| Field | Value |
|---|---|
| Pattern | **1.9** |
| File | `ctscto/ctoUtil.cc:4384` |
| Realness | real |

Two-arg `min_element` on `loadPathDelayVec`; tied minima pick first load used in gain filtering for `newDrvTermLocVec`.

**Fix A:** single-pass min with deterministic tie-break against the parallel load identity/geometry.

---

## 6. Downstream proof (Stage 3b)

| # | Suspect | Caller path | Observable sink | Neutralizer? |
|---|---|---|---|---|
| H1 | `std::set<ndmTerm*>` address order | `ctoFlow::restructFlow` | `cloneBufferInverter` / `bufShieldBufferInverter` + 10% early break | None before mutation |
| M1 | distance-only sort | `do2To1Clustering` | `instantiateRepeater(driver, load1, …)` | None |
| M2 | distance-only sort | `doClustering` | recursive `loadTerms1/2` split | None |
| M3 | incomplete min_element | load-partition init | `_spSinkPos` → binary partitions | None on full ties |
| M4/M5 | float extrema | `addCriticalPathCandidates` | relocation candidate locs | None on ties |
| M6 | float min_element | `calculateNewDrvTermLocationForSpFilter` | gainVec zeroing / loc vec | None on ties |

**App options / regression setters:** not resolved (`icc2query`, `nwtn/unit` absent in this client).

---

## 7. Performance-aware fix direction (Stage 3c)

| # | Recommended fix | Complexity change | Notes |
|---|---|---|---|
| H1 | `ndmObjPtrCmpType` on set | same O(N log N) | Prefer over vector+sort unless profiling says otherwise |
| M1–M2 | id tie-break in comparator | O(1)/cmp | Prefer fixing `node::operator<` once |
| M3 | cmp tie-break | O(1)/cmp | Keep min_element |
| M4–M6 | linear scan + id | O(N) once | Do **not** add full sorts on these hot paths |

---

## 8. Non-real classifications (deep-read)

| Class | Examples | Evidence |
|---|---|---|
| latent-only | GLS `parallel_reduce` bool fold; DRC/phase concurrent maps | Prior MT C2–C4/C6/C8/C9; associative or accessor-serialized |
| dead/unused (MT) | `_termValidSclkCache` lazy `dosMap` | Prior C1 — no shared worker caller |
| false-positive | `hardware_concurrency` grain in `ctoGrpLatCalc` | Prior C5 — index-disjoint writes |
| neutralized | concurrent_vector → `std::set` median | Prior C7 |
| safe-adopter | widespread `ndmObjPtrCmpType` / `ndmPtrMap` | Container pack samples |
| test/debug only | `srand(time)` in skewgrp DisjointSet mains; fmax directory_iterator under env file-flow | Unreachable from production QoR |

---

## 9. Generic fix patterns (excerpt)

1. **Pointer set/map:** `std::set<T*, ndmObjPtrCmpType>` or `ndmPtrMap` / `ndmPtrSet`.  
2. **Sort / min / max with value key:** compare primary metric, then stable object id.  
3. **Unordered membership:** keep hash map for lookup; materialize + sort only before order-sensitive mutation/output.  
4. **RNG:** fixed or design-derived seed if ever on production path (none promoted here).  
5. **MT:** prefer disjoint keys + post-join canonicalize; do not “fix” with `std::map` on hot concurrent paths.

---

## 10. Coding guidelines

**DO**

- Use `ndmObjPtrCmpType` / object ids for any pointer ordering that reaches QoR.  
- Canonicalize at the smallest observable boundary.  
- Record tie-breaks explicitly when primary keys can collide (distance, delay, slack).

**DON'T**

- Iterate default `std::set<T*>` / `unordered_*<T*>` into mutating transforms.  
- Rely on “first of ties” from `min_element` / `max_element` / unstable sort.  
- Treat `getenv` / env file-replay paths as ND defects (intentional control surface).  
- Blindly swap hot hash maps for ordered maps.

---

## 11. Module-specific summary

Local CTS (~2391 C++ files under `ccd/`, `ctscto/`, `mscts/`, `ctsmisc/`, …) already adopts deterministic pointer comparators in many places. Stage-1 produced **4535** HIGH/MEDIUM-default hits; after narrowing and observability proof, **7** real defects remain. The standout **HIGH** is CTO pre-opt restructuring order. **MEDIUM** issues cluster on MSCTS tap synthesis and MTCTO/CTO relocation/partition tie-breaks. Random, filesystem, parallel-reduce, and most concurrency-shape hits were dismissed as test-only, fixed-seed, latent, or unreachable — consistent with the prior MT prove-nd pass on this tree.

---

## 12. Dismissed buckets (Stage-1 / triage filters)

| Pattern | Bucket | Count |
|---|---|---|
| 1.1 | Value-type / pair-key sorts | 178 |
| 1.1 | Existing ID/name comparators | 24 |
| 1.1 | Tests / debug / stable pair seconds | 30 |
| 1.2 | Membership-only pointer sets | 58 |
| 1.2 | Explicit stable comparator | 42 |
| 1.2 | Stage-1 overmatch narrowed away | 2555 |
| 1.3 | Membership / lookup-only unordered | 72 |
| 1.3 | Integer/string keys | 18 |
| 1.4 | Lookup-only / TLS pointer hashes | 16 |
| 1.5 | Test / fixed-seed rand | 34 |
| 1.6 | time-seed test mains only | 2 |
| 1.7 | Name keys lookup-only | 75 |
| 1.9 | Value/debug extrema | 11 |
| 1.11 | unique after stable sort / no-op | 17 |
| 1.12 | Env debug / test readdir | 8 |
| 3.1 | Bool parallel_reduce latent | 2 |
| 3.2 | Concurrent MT latent/idempotent | 80 |
| 3.5 | Grain-only HW concurrency | 3 |
| 3.7 | Wrapper safe / membership | 120 |
| 4.1 | Lazy cache MT-unreachable | 2 |
| 4.2 | ST first-touch only | 38 |
| 4.4 | concurrent_hash_map latent | 36 |
| semantic | CL checklist considered, no extra promote | 9 |

---

## 13. CL-mined semantic checklist coverage

| Checklist item | Result |
|---|---|
| 3.6 post-collection without sort | Sampled; no additional REAL HIGH/MEDIUM beyond listed sorting/partition sites |
| 3.7 project wrappers | Mostly safe-adopter / membership; no promote |
| Graph/geometry traversal | No incomplete tie-break beyond M1–M2 |
| Stale cached state | `_termValidSclkCache` → dead/unused for MT |
| Delay-sharing / scene reuse | Not promoted (no proved unstable reuse sink in scope) |
| Concurrency / write-lock | Prior C2–C9 latent/neutralized |
| Deterministic NdFix options | App-option DB unavailable; not promoted |
| Checksum observability | Not promoted (investigation-only) |

---

## 14. Verification notes

**Tools used**

- Pattern catalog: `~/.cursor/skills/nd-code-analyzer/references/nd-patterns.yaml`  
- Stage-1: Cursor-bundled `rg` (PCRE2) via PowerShell (skill `scripts/scan_nd.py` / `render_report.py` **not present** in this install)  
- Artifacts:  
  - `C:\Users\carys\.cursor\plans\nd_cts_candidates.json`  
  - `C:\Users\carys\.cursor\plans\nd_cts_narrowed_packs.json`  
  - `C:\Users\carys\.cursor\plans\nd_cts_findings.json`  
  - This report  
- Parallel triage: three `generalPurpose` subagents (sorting / containers / random+MT)  
- Cross-check: prior MT report `cs_non-determinism/.../tc-006-customer-workflow/results/cts_nd_details.md`

**Limits**

- No `clangd_query.py` / `nwtn-src-cpp-code-navigation` (not an `nwtn/src` sparse client)  
- No `p4 annotate` / ownership (no depot mapping)  
- No `icc2query` app-option defaults  
- Pattern 3.3 / 3.6 not exhaustively Stage-1-emitted (noisy); covered via semantic checklist + related packs  
- LOW-severity patterns excluded by request  
- Container/unordered packs sampled on hot production dirs rather than every declaration site  

**Share path:** `C:\Users\carys\.cursor\plans\nd_analysis_cts_20260909.md`

---

*End of report — HIGH/MEDIUM only.*
