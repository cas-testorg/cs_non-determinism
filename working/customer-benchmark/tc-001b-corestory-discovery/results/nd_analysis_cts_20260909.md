# Non-Determinism Analysis — CTS Module

**Module:** `C:\Users\carys\cts`  
**Scan date:** 2026-09-09  
**Analyzer:** nd-code-analyzer v1.4.0 (Stage 1–5; `scan_nd.py` / `render_report.py` absent from skill tree — ripgrep + CoreStory + source triage)  
**Severity floor:** HIGH and MEDIUM only (real findings)  
**Patterns evaluated:** 27 (`references/nd-patterns.yaml`)  
**CoreStory:** project `cts-code` (id 10), conversation 85  

---

## 1. Executive summary

| Severity | Real findings |
|----------|---------------|
| **HIGH** | **0** |
| **MEDIUM** | **0** |
| **LOW** | *(omitted per request)* |

**Verdict:** After mechanical scan and deep triage, **no production-reachable equivalent-run HIGH or MEDIUM ND defects** were confirmed. An earlier draft report (`nd_report_high_medium.md` from earlier today) promoted four sites that **do not survive** caller / build / observability checks; those are documented below as dismissals.

**Overall posture:** CTS QoR paths heavily use stable pointer identity (`ndmObjPtrCmpType`, `termSetType`, `ndmPtrMap` / `dosSet`) and explicit canonicalization helpers (e.g. `fillTermToTermBagMapInVec` annotated for Coverity `POINTER_NONDETERMINISM`). Remaining Stage-1 hits are overwhelmingly membership-only containers, value-type sorts, test/debug RNG, dead code, or config/platform sensitivity.

---

## 2. Critical background — ID / comparator discipline

| Mechanism | Typical use in CTS |
|-----------|--------------------|
| `ndmObjectHandleNS::compareObjPtr` / `ndmObjPtrCmpType` | `std::set` / `std::map` on `ndm*` |
| `TYPEDEF_CONTAINER_1(... ndmObjPtrCmpType)` → `termSetType` | CTO / CTS typedef layer |
| `ndmPtrMap` / `ndmPtrSet` / `dosSet` | Deterministic project containers |
| `ctsTermId` / `getIdLong()` | O(1) stable numeric keys |

Prefer stable ID comparators; canonicalize once at the boundary where order becomes observable.

---

## 3. Top summary table

| # | Issue | Real? | Notes |
|---|-------|-------|-------|
| — | *(none)* | — | No HIGH/MEDIUM real findings after Stage 3b |

---

## 4. HIGH severity findings

*None.*

---

## 5. MEDIUM severity findings

*None.*

---

## 6. Downstream proof

Not applicable — no promoted real findings. Downstream proof was applied to reject candidates (see §8–§9).

---

## 7. Performance-aware fix direction

Not applicable for promoted defects. Hygiene notes (not elevated):

- Prefer seeding clustering RNG from a design/input checksum if policy requires input-derived seeds (`msClustering::_rand`).
- Prefer `ctsscUtil::getMaxThreadCount()` over raw `hardware_concurrency()` for grain sizing consistency across hosts (`ctoGrpLatCalc`).

---

## 8. Non-real classifications (deep-read)

| Site | Prior draft label | Corrected verdict | Evidence |
|------|-------------------|-------------------|----------|
| `fmaxLpSolver::selectActiveVariableSubset` + `std::random_device` (`fmaxLpSolver.cc:3892`) | HIGH real | **dead/unused** | Only caller is **commented out** at `fmaxLpSolver.cc:146–147`; no other references |
| `ctoFlowClone.cc` `std::set<ndmTerm*>` in `restructFlow` | HIGH real | **dead/unused** | `ctoFlowClone.cc` **not** in `ctscto/Master.make` |
| Production `ctoRestruct.cc` `restructFlow(termSetType…)` | — | **safe-adopter** | `termSetType` = `std::set<ndmTerm*, ndmObjPtrCmpType>`; called from `ctscto.cc:845–850` when `isUsePreOptReStructuringForLatency()` |
| `TimingCostFunction` parallel TNS fold | MEDIUM real | **config sensitivity** | Fixed `calculateRanges` + thread-index fold; equivalent-run stable for fixed thread count |
| `ctoGrpLatCalc::calcGrpLatencyBatch` `hardware_concurrency` | MEDIUM real | **false-positive** (result ND) | Disjoint `grpLat[i]` writes; grain ≠ arithmetic result |
| `msClustering` / tap `kMeansPPSeeding` | CoreStory HIGH candidate | **not equivalent-run ND** | Default `boost::mt19937` is fixed-seed; fresh objects → same sequence across equivalent runs |
| `runSccIteration` `parallel_reduce` + `globalDone` | MT candidate | **neutralized** for bool QoR | Associative OR/AND; early-exit does not change final boolean |
| `unordered_set` → `deriveOffsetLimits` / `backPropagateCUSLimit` | Pattern 1.3 | **membership-only** | Only `find`, no order-sensitive iteration |

---

## 9. Dismissed buckets (Stage-1 mechanical noise)

| Pattern | Bucket | Approx. count | Rationale |
|---------|--------|---------------|-----------|
| 1.2 | Pointer set with stable comparator / `termSetType` | 40+ | Safe adopters |
| 1.2 | Membership / visited-only pointer sets | 60+ | No order-sensitive consumer |
| 1.3 | Pointer `unordered_*` membership-only | 40+ | `find`/`insert` only |
| 1.1 | Value-type / custom-`operator<` sorts | 50+ | Not address sort |
| 3.3 | Range-for on non-unordered containers | many | Pattern 3.3 type-resolution drop |
| 3.7 | `ndmPtrMap` / Coverity canonicalize helpers | 20+ | Fix idiom, not defect |
| 1.5 / 2.1 | Test/debug `srand(time)` / UI random tests | 5+ | Out of production QoR |
| 4.x | Lazy mutable caches / concurrent check-then-act | 4 | Latent / MT-unreachable per prior MT notes |
| 4.3 / 4.5 / 4.6 | Catalog seeds | 0 | No Stage-1 hits |

---

## 10. CL-mined semantic checklist coverage

| Checklist item | CTS result |
|----------------|------------|
| Post-collection canonicalization (3.6) | Not promoted; lazy TNS uses explicit sort after concurrent collection (`ctsLazyCostGroup.cc`) |
| Project wrapper containers (3.7) | Safe adopters (`ndmPtrMap`, `termSetType`, `fillTermToTermBagMapInVec`) |
| Graph / geometry traversal | No incomplete tie-break promoted |
| Stale cached state | `_termValidSclkCache` etc. remain **latent-only** (see MT notes) |
| Delay-sharing / scene reuse | Not promoted |
| Concurrency / write-lock discipline | `ctoGrpLatCalc` suspend path reviewed; grain dismissed |
| Deterministic control-path normalization | Not promoted |
| Checksum observability | `soCgSolverUpdater::updateSolver` → `printChecksum` after ordered scenario maps (`std::map`) |

---

## 11. Generic fix patterns (excerpt)

**Pointer containers:** Prefer `ndmPtrMap` / `std::set<T*, ndmObjPtrCmpType>` over raw `std::set<T*>`.

**Unordered iteration:** If order matters, copy keys → sort with stable comparator → consume.

**Parallel FP:** Per-thread locals + deterministic merge (only needed if thread count can vary and bit-exact TNS is required).

**Randomness:** Never `std::random_device` on live QoR paths; use fixed or app-option seed. Prefer input-derived seeds for clustering.

---

## 12. Coding guidelines

**DO**

- Use `ndmObjPtrCmpType` / `compareObjPtr` for pointer-keyed ordered containers on QoR paths.
- Canonicalize once before first order-sensitive consumer.
- Align MT grain with `getMaxThreadCount()` for cross-host consistency.
- Keep Coverity-style helpers such as `fillTermToTermBagMapInVec` when iterating former pointer maps.

**DON'T**

- Reintroduce `std::set<T*>` without comparator on mutating loops (the orphan `ctoFlowClone.cc` pattern).
- Leave entropy-seeded sampling wired into live LP paths.
- Treat membership-only `unordered_*` as ND without an order-sensitive sink.

---

## 13. Module-specific summary

The CTS tree is **generally ND-aware** on production paths. The most important correction from this pass is that previously reported “HIGH” sites were either **not linked** (`ctoFlowClone.cc`), **not called** (`selectActiveVariableSubset`), or **not equivalent-run nondeterministic** (parallel TNS fold; HW-concurrency grain). MSCTS tap clustering uses a default-seeded Mersenne engine that is **repeatable across equivalent runs** but not input-hashed — a determinism *hygiene* note, not a HIGH defect under the Stage 3b equivalent-run bar.

---

## 14. Verification notes

| Item | Detail |
|------|--------|
| **Search backend** | ripgrep (Cursor-bundled) against `nd-patterns.yaml` patterns; manual narrowing for 1.3 / 3.3 / 3.6 / 3.7 |
| **Source root** | Local `c:\Users\carys\cts` |
| **Application intelligence** | CoreStory `cts-code` project_id=10, conversation 85 |
| **Navigation** | Text search + targeted reads; `clangd_query.py` N/A (not under `nwtn/src`) |
| **Build evidence** | `ctscto/Master.make` CPPFILES inspected for `ctoRestruct.cc` vs absence of `ctoFlowClone.cc` |
| **App options / icc2query** | Not run |
| **Perforce ownership** | Skipped — no depot mapping in local client |
| **Prior artifacts** | Reused `cts_nd_details.md`, `nd_mt_candidates_discovery.md` for MT latent classifications; **supersedes** earlier draft promotions in `nd_report_high_medium.md` |
| **Scope limits** | Severity floor HIGH/MEDIUM; test dirs deprioritized; `scan_nd.py` missing so candidate counts are approximate |
| **Artifacts** | `nd_cts_findings.json` (this pass); this report |

---

## Correction notice (supersedes earlier draft)

The file previously written as a HIGH/MEDIUM report promoting H1–H2 / M1–M2 is **incorrect**. Use this document (and `nd_cts_findings.json`) as the shareable result of the nd-code-analyzer pass.

| Draft claim | Status |
|-------------|--------|
| H1 fmax UNIFORM `random_device` | Dead code — do not fix as live ND |
| H2 `ctoFlowClone` pointer sets | Not in build — do not treat as production |
| M1 parallel TNS | Config sensitivity only |
| M2 HW concurrency grain | No result ND |

---

*Generated by nd-code-analyzer workflow (manual Stage 5). Share this markdown or `nd_cts_findings.json` as needed. Re-run with depot access for Perforce ownership if findings are later promoted.*
