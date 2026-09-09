# Non-Determinism Analysis Report — CTS (`C:\Users\carys\cts`)

| Field | Value |
|---|---|
| Module | `cts` (Clock Tree Synthesis) |
| Scan date | 2026-09-09 |
| Patterns evaluated | 24 (HIGH/MEDIUM default severity only; LOW patterns skipped) |
| Stage-1 candidates | 15,484 across 1,214 files |
| Search backend | ripgrep (local; `scan_nd.py` not present in skill install) |
| Severity floor | **HIGH + MEDIUM only** |
| Promoted real findings | **2** (1 HIGH, 1 MEDIUM) |
| CoreStory project | `cts-code` (id 10) |
| Perforce ownership | Skipped — `p4` unavailable on this host |

---

## 1. Executive summary

Mechanical scan of the CTS tree produced a large Stage-1 surface, but after type/comparator narrowing, downstream observability proof, and qualification, **only two real HIGH/MEDIUM defects** remain.

| Severity | Count |
|---|---|
| HIGH | 1 |
| MEDIUM | 1 |
| LOW (excluded by request) | — |

**By category (promoted):** container (2).

**Top hot files (promoted):**

1. `ctssch/ctsTimingDrivenTransitionTargets.h` — broken `compareTimInfo` / N-worst max-tran
2. `mscts/drivers/msDrivers.cc` — MLPH `_loadNetSet` last-driver return

Most pointer `std::set`/`unordered_*` hits are already `ndmObjPtrCmpType` safe-adopters or membership-only. Random/`srand(time)` hits are test/fixed-seed. Tier-2 vicinity patterns (3.x/4.x) were not promoted without stronger observability/MT proof.

---

## 2. Critical background — ID system reminder

Pointer addresses are **not** stable identifiers across runs (ASLR, allocator, heap layout).

| Approach | Cost | Determinism |
|---|---|---|
| Raw `T*` / `std::less<T*>` / `std::hash<T*>` | Fast | **Non-deterministic** |
| `getIdLong()` / object-handle compare | O(1) typical | Deterministic |
| `ndmObjPtrCmpType` / `ndmObjectHandleNS::compareObjPtr` | Project idiom | Deterministic |
| `ndmPtrMap` / `dosContainer::keyCompare` | Project idiom | Deterministic |
| `getFullName()` as key | O(hierarchy) + alloc | Usually stable string, but expensive |

Gold standard for CTS/NWTN-style code: stable ID or project pointer comparators — not addresses.

---

## 3. Top summary table

| ID | Issue | Realness | Controls / app options | Summary |
|---|---|---|---|---|
| ND-CTS-001 | `compareTimInfo` invalid SWO / no ID tiebreak | real | TD sink recipe; `sortByCriticality` default **true** | N-worst / critical sinks → `setMaxTransition` QoR |
| ND-CTS-002 | `std::set<ndmNet*>` last-driver under MLPH | real | `enable_mlph_flow` default **false** | Returned driver picks clock/tap topology |

---

## 4. HIGH findings

### 4.1 ND-CTS-001 — timingInfo* set comparator lacks strict-weak-order / ID tiebreak

| | |
|---|---|
| **Pattern** | 1.2 — pointer/set ordering |
| **Severity** | HIGH |
| **File** | `ctssch/ctsTimingDrivenTransitionTargets.h:181` |
| **Symbol** | `timingDrivenSinkTargetTransitionManager::compareTimInfo` / `targetNWorstSinks` |

**Current code**

```cpp
struct compareTimInfo {
  bool operator()(const timingInfo *lhs, const timingInfo *rhs) const {
    int cmpVal = nwmathFloat::compare(lhs->getScore(), rhs->getScore(), 0.0001);
    if (cmpVal <= 0) return true;
    else return false;
  }
};
typedef std::set<timingInfo*, compareTimInfo> timingInfoSet;
```

**Why this is ND / defective**

- `cmpVal <= 0` is **not** a valid strict weak ordering (equal scores: both `a<b` and `b<a` can be true).
- No identity tiebreak (`getIdLong` / `compareObjPtr`) when scores compare equal within tolerance.
- `targetNWorstSinks` walks `_sinkPinTimingInfoSet.begin()` and selects the first N sinks into `_tightTransitionSinkPinSet` (comment: “already sorted”).
- `runTDSinkTargetTransitionRecipe` then calls `setMaxTransition` — **constraint / QoR mutation**.

**Version A (Simple) — preferred**

```cpp
struct compareTimInfo {
  bool operator()(const timingInfo* a, const timingInfo* b) const {
    int c = nwmathFloat::compare(a->getScore(), b->getScore(), 0.0001);
    if (c != 0) return c < 0; // ascending score (worst first)
    ndmTerm* ta = const_cast<timingInfo*>(a)->getTerm();
    ndmTerm* tb = const_cast<timingInfo*>(b)->getTerm();
    return ndmObjectHandleNS::compareObjPtr{}(ta, tb);
  }
};
```

**Version B (Robust)** — materialize + `stable_sort` by score then ID at the N-worst boundary; keep `_termTimingInfoMap` (already `ndmObjPtrCmpType`) for membership.

**Rationale:** Version A is sufficient and cheap; fixes UB comparator and deterministic tiebreak in one place.

**Code ownership (Perforce):** not attributed — no `p4` on this host / local mirror only.

---

## 5. MEDIUM findings

### 5.1 ND-CTS-002 — Pointer-ordered `std::set<ndmNet*>` last-driver return (MLPH)

| | |
|---|---|
| **Pattern** | 1.2 — pointer set default comparator |
| **Severity** | MEDIUM (gated) |
| **File** | `mscts/drivers/msDrivers.cc:711` (alloc ~10309) |
| **Symbol** | `msClockDrivers::findDriverTerm` / `msDriversOptions::_loadNetSet` |

**Current code (mechanism)**

```cpp
// alloc ~10309
_loadNetSet = new std::set<ndmNet*>();

// findDriverTerm MLPH multi-net leaf branch
std::set<ndmNet*>* loadNetSet = _msOptions.getLoadNetSet();
if (_appOptions.enableMLPHFlow && loadNetSet && loadNetSet->size() > 1 && leafLevel) {
  for (; itrS != itrE; ++itrS) {
    l_drvTerm = (*itrS)->getFirstFlatDriver();
    if (l_drvTerm) drvTerms.insert(l_drvTerm); // termSetType is stable
  }
}
return l_drvTerm; // last address-ordered net's driver
```

**Why MEDIUM**

- Address order of nets varies across runs → last `l_drvTerm` varies when multiple nets have drivers.
- Callers (`msAutoTapFlow.cc` ~4477 with empty/dummy `drvTerms`, ~5190, ~6194) use the **return value** for `getAClockOnTerm` and tap evaluation — topology/QoR impact.
- Gated by `enable_mlph_flow` (**default false**) → severity MEDIUM rather than HIGH.

**Version A (Simple)**

```cpp
_loadNetSet = new std::set<ndmNet*, ndmObjPtrCmpType>();
// and/or:
return drvTerms.empty() ? nullptr : *drvTerms.begin();
```

**Version B (Robust)** — return hierarchy-aware deterministic picker over `drvTerms` (e.g. `getTopLevelDrvTerm`) instead of last loop overwrite.

**Code ownership (Perforce):** not attributed — no `p4` on this host.

---

## 6. Downstream proof (Stage 3b)

### ND-CTS-001

| Step | Evidence |
|---|---|
| Suspect source | `compareTimInfo` / `_sinkPinTimingInfoSet` |
| Call path | `runTDSinkTargetTransitionRecipe` → `targetNWorstSinks` / `identifyTimingCriticalSinks` |
| Observable sink | `_tightTransitionSinkPinSet` → `setMaxTransition` DRC mutation |
| Neutralizer | None before constraint apply |
| Controls | `sortByCriticality` default true |
| Build / reachability | `ctssch` production scheduling; CoreStory indexes TD sink transition recipe |

### ND-CTS-002

| Step | Evidence |
|---|---|
| Suspect source | `std::set<ndmNet*>` `_loadNetSet` |
| Call path | `findDriverTerm` MLPH branch → `msAutoTapFlow` consumers |
| Observable sink | `getAClockOnTerm` / tap configuration / sink collection |
| Neutralizer | `drvTerms` stable; **return scalar is not** |
| Controls | `enable_mlph_flow` default false |
| Build / reachability | `mscts/drivers` production multi-source CTS |

---

## 7. Performance-aware fix direction (Stage 3c)

| Finding | Fix cost | Guidance |
|---|---|---|
| ND-CTS-001 | Negligible | Fix comparator in place; avoid per-sink full resorts |
| ND-CTS-002 | Negligible | Stable comparator on small net sets; prefer return from already-stable `drvTerms` |

Do **not** blanket-replace hot `unordered_*` lookup maps with `std::map` across CTS — most Stage-1 1.3 hits are membership-only and should stay hash-based.

---

## 8. Non-real classifications (deep-read)

| Class | Examples | Verdict |
|---|---|---|
| false-positive | `ccdcgSolver` `srand(100)`; default `mt19937` in `msClustering` | Fixed/default seed → not equivalent-run ND |
| test-only / dead-unused | `skewgrp` `srand(time(NULL))`; `ctsui*RandomTest` | Not production flow |
| latent-only | Pointer `std::hash` caches in `soLogicCone`, `ctoscFilter` | Membership/lookup only |
| safe-adopter | Widespread `termSetType` / `ndmObjPtrCmpType` | Already deterministic |
| mirror-duplicate | `include/` copies of `ctosc*` / `soLogicCone` headers | Same as primary |
| report-only (LOW) | `soClockGateOpt` `fromToMap` unordered iteration | Report order; excluded by severity floor |
| neutralized | Many 1.3 sites with post-loop `sort(compareObjPtr)` | Order canonicalized before sink |

---

## 9. Generic fix patterns

1. **Pointer set/map:** `std::set<T*, ndmObjPtrCmpType>` or `ndmPtrMap` / `ndmPtrSet`.
2. **Sort / N-worst / min_element:** metric primary key, then `getIdLong` / `compareObjPtr` tiebreak; use strict `<`.
3. **Unordered iteration:** keep hash for lookup; sort keys once at mutation/report boundary.
4. **RNG:** seed from design-stable IDs or explicit app option — never `time(NULL)` on production paths (test harnesses OK).

---

## 10. Coding guidelines

**DO**

- Use `ndmObjPtrCmpType` / `compareObjPtr` for pointer-keyed ordered containers.
- Ensure set/map comparators implement a valid strict weak ordering.
- Canonicalize order before first-N selection, last-wins loops, or DRC mutation.
- Document intentional randomness in test-only files.

**DON'T**

- Use raw `std::set<T*>` / `std::map<T*,V>` when iteration or last/first selection matters.
- Write `cmp <= 0` style “comparators.”
- Treat Stage-1 regex hits as defects without iterated-type + sink proof.
- Classify fixed-seed `rand`/`mt19937` as equivalent-run ND.

---

## 11. Module-specific summary

CTS shows mature adoption of stable pointer comparators (`termSetType`, `ndmObjPtrCmpType`), which correctly dismissed the bulk of ~15k Stage-1 candidates. Residual risk concentrates in **custom comparators that omit identity tiebreaks** and **gated MLPH paths that still return address-ordered “last” objects**. Randomness in production clustering/CCD is largely fixed-seed; time-based seeds remain in DisjointSet test drivers only.

---

## 12. Dismissed buckets (Stage-1 filters)

| Pattern | Bucket | Approx count | Why dismissed |
|---|---|---|---|
| 1.1 | Numeric/ID sorts | ~401 | Not pointer vectors |
| 1.2 | Membership / safe comparator | ~2900 | `ndmObjPtrCmpType` or find-only |
| 1.3 | Lookup / post-sort | ~530 | No order-sensitive QoR sink (or LOW report-only) |
| 1.4 | Pointer hash caches | 16 | Membership-only |
| 1.5 / 2.1 | Random / time seed | 25 | Test or fixed seed |
| 2.2 | getFullName | ~100 | Tiebreak/diagnostics |
| 3.x / 4.x | Vicinity / MT seeds | ~11k | Insufficient observability/MT proof |

---

## 13. CL-mined semantic checklist coverage

| Checklist family | Result |
|---|---|
| Post-collection canonicalization (3.6) | Seed-heavy; spot checks showed many post-sorts / membership — not promoted |
| Project wrapper containers (3.7) | Many safe `ndm*` / `dos*` adopters |
| Graph/geometry traversal | Not elevated in this pass |
| Stale cached state | `_termValidSclkCache` documented thread-safe `dosMap` — not promoted |
| Delay-sharing / cross-scene | Not elevated |
| Concurrency / write-lock | 4.x seeds only; no HIGH/MEDIUM without TSan/MT proof |
| Deterministic control-path / NdFix | Not elevated |
| Checksum observability | Not elevated |

---

## 14. Verification notes

**Tools / method**

- Stage 1: PowerShell + Cursor `rg` against `nd-patterns.yaml` (HIGH/MEDIUM defaults); output `C:\Users\carys\cts\.cursor\nd-scan\candidates.json`
- Stage 2–3: Single-agent + parallel `generalPurpose` triage on random/hash/sort-set buckets; CoreStory `semantic_search` on project `cts-code` (id 10)
- Stage 4: `C:\Users\carys\cts\.cursor\nd-scan\findings.json`
- Stage 4b: **Skipped** — `p4` not installed; no depot mapping
- Stage 5: Hand-rendered report (skill `render_report.py` not present in this install)

**Scope limits**

- Severity floor HIGH/MEDIUM only (user request)
- LOW patterns (e.g. 2.9, 3.4, 4.6) not scanned
- Full deep-read of all ~11k Tier-2 vicinity hits was not performed; dismissed in aggregate after sampling + narrowing rules
- No clangd / TSan / Coverity runtime confirmation
- App-option defaults taken from local `msuiAppOptions.cc` / TD option call sites; `icc2query` not available

**Artifacts**

- Candidates: `C:\Users\carys\cts\.cursor\nd-scan\candidates.json`
- Findings: `C:\Users\carys\cts\.cursor\nd-scan\findings.json`
- This report: `C:\Users\carys\.cursor\plans\nd_analysis_cts_20260909_a7c3.md`

---

## Recommended next validation

1. Fix ND-CTS-001 comparator; re-run TD sink transition recipe twice on identical inputs; diff max-tran pin sets / QoR.
2. With `enable_mlph_flow` true and multi-net leaf loads, fix ND-CTS-002; compare returned driver IDs / tap clocks across runs.
3. Optional: ThreadSanitizer on mutable lazy caches (`msgtsCluster::_leafCount`) if MT CTS paths are in scope for a follow-up.
