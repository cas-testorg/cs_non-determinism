# Code analysis report generation
_Exported on 9/9/2026 at 11:16:49 CDT from Cursor (3.18.25)_

---

**User**

/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report

---

**Cursor**

I'll read the ND code analyzer skill and scan the project for HIGH and MEDIUM non-determinism issues.


The scan scripts aren't in the skill tree, so I'll run the mechanical scan with ripgrep against the pattern catalog and build the report from that.


I'll dig into the highest-risk CTS call sites next and verify whether they have real downstream impact.


Writing the shareable markdown report from triaged findings.


Completed an **nd-code-analyzer v1.4.0** pass on `C:\Users\carys\cts` (ripgrep against the 27-pattern catalog + manual Stages 2–3 triage). `scan_nd.py` / `render_report.py` are not in the skill tree, so this was a manual workflow.

**Note:** Disk space on `C:` was exhausted during report write — a partial file may exist but could not be saved reliably. The full shareable report is below (copy to `.md` when space is available).

---

# Non-Determinism Analysis — CTS Module

**Module:** `C:\Users\carys\cts`  
**Date:** 2026-09-09  
**Severity floor:** HIGH and MEDIUM (real findings only)  
**Patterns evaluated:** 27

## Executive summary

| Severity | Real findings |
|----------|---------------|
| **HIGH** | 2 |
| **MEDIUM** | 2 |

| Category | HIGH | MEDIUM |
|----------|------|--------|
| random | 1 | 0 |
| container / sorting | 1 | 0 |
| parallel / arithmetic | 0 | 2 |

**Hot files:** `ccd/ctsccd/fmax/fmaxLpSolver.cc`, `ctscto/ctoFlowClone.cc`, `ccd/ctsccd/fmax/include/fmaxTimingCostFunction.h`, `ctscto/ctoGrpLatCalc.cc`

**Posture:** CTS mostly uses stable idioms (`ndmObjPtrCmpType`, `ndmPtrMap`, `dosSet`). Confirmed defects cluster in **CCD fmax LP** and **CTO pre-opt restructuring**. Hundreds of Stage-1 pointer-container hits were dismissed (membership-only sets, safe adopters, value-type sorts).

---

## Top summary table

| # | Issue | Real? | Triggering controls | Summary |
|---|-------|-------|---------------------|---------|
| **H1** | Fmax UNIFORM subset RNG | real | `selectActiveVariableSubset(..., UNIFORM, ...)` | `std::random_device` seeds sampling; LP variable subset varies run-to-run |
| **H2** | `restructFlow` pointer sets | real | `ctoFlow::restructFlow()` pre-opt | `std::set<ndmTerm*>` address order drives mutating clone/shield sequence |
| **M1** | Parallel TNS fold | real | Fmax TNS evaluate, threads > 1 | FP sum association depends on thread-count partition |
| **M2** | HW concurrency grain | real | `_useCgLatMT` MT batch | `_step` from `hardware_concurrency()` vs `getMaxThreadCount()` elsewhere |

---

## HIGH findings

### H1 — Unseeded RNG in fmax LP (`UNIFORM` subset)

| | |
|--|--|
| **Pattern** | 2.1 — random without fixed seed |
| **Location** | `ccd/ctsccd/fmax/fmaxLpSolver.cc` ~3892–3903 |

```cpp
std::random_device rd;
std::mt19937 generator(rd());
std::uniform_int_distribution<> uniform(1, cumulativeOccurences.back());
// ... samples into `result` (active LP variable indices)
```

**Why real:** Under `VariableSubsetType::UNIFORM`, the active LP variable set is sampled with entropy-seeded RNG. Different subsets → different reduced LP → different optimizer path and QoR.

**Gating:** `coveragePercentage ∈ (0,1)` and `subsetType == UNIFORM`. Other modes sort deterministically.

**Fix A:** Fixed seed. **Fix B:** App-option seed. **Fix C:** Deterministic stratified selection (no RNG). **Perf:** No hot-loop cost.

---

### H2 — Pointer-keyed `std::set<ndmTerm*>` in CTO restructuring

| | |
|--|--|
| **Pattern** | 1.2 — default `std::less<T*>` on pointers |
| **Location** | `ctscto/ctoFlowClone.cc` 1884–2025 |

```cpp
std::set<ndmTerm*> candidates;
std::set<ndmTerm*> lpCandidates;
for (std::set<ndmTerm*>::iterator it = lpCandidates.begin(); ...; ++it) {
  cloneBufferInverter(drvTerm);  // or bufShieldBufferInverter
}
```

**Why real:** Iteration follows pointer addresses (ASLR/allocator layout). Each iteration **mutates** the design; earlier transforms change state seen by later drivers.

**Gating:** `restructFlow()` / `_preOptRestructMode`.

**Fix:** `std::set<ndmTerm*, ndmObjPtrCmpType>` (matches convention elsewhere in `ctoFlow.cc`). **Perf:** One-time O(N log N) — negligible vs timing queries in the same function.

---

## MEDIUM findings

### M1 — Parallel TNS accumulation in `TimingCostFunction::evaluate`

| | |
|--|--|
| **Pattern** | 3.1 / 3.5 |
| **Location** | `ccd/ctsccd/fmax/include/fmaxTimingCostFunction.h` ~270–337 |

Per-thread `resultsPerThreadTNS[i]` filled in `tbb::parallel_for`, then:

```cpp
for (size_t threadIndex = 0; threadIndex < numberOfThreads; ++threadIndex)
  resultTNS += resultsPerThreadTNS[threadIndex];
```

**Why real:** FP addition is not associative; partition/thread count changes the summed TNS at observable precision → LP cost / stopping behavior can differ across hosts or thread settings.

**Fix:** Compensated merge of per-thread partials; or document fixed thread budget for cost evaluation.

---

### M2 — `hardware_concurrency()` for MT grain in group-latency batch

| | |
|--|--|
| **Pattern** | 3.5 |
| **Location** | `ctscto/ctoGrpLatCalc.cc` 80–88 |

```cpp
size_t numT = std::thread::hardware_concurrency();
_step = jobSize / numT + 1;
tbb::parallel_for(tbb::blocked_range<size_t>(0, idx.size(), _step), ...);
```

**Why real:** Grain uses **hardware-reported** concurrency while most CTS MT uses `ctsscUtil::getMaxThreadCount()`. Per-index `grpLat[i]` writes are disjoint, but schedule/grain can diverge → potential tie-break / latency path differences in downstream CTO cost.

**Fix:** `numT = ctsscUtil::getMaxThreadCount()` (align with `ctsMtTaskRunner`).

---

## Dismissed buckets (representative)

| Bucket | Verdict |
|--------|---------|
| Pointer sets with `ndmObjPtrCmpType` / `compareObjPtr` | safe-adopter |
| `visitedTerms`, `processedDrvSet`, etc. (membership only) | false-positive |
| `nodeAndToggleRate` sort in `ctssch/ctsSchCts.cc` | false-positive (value type with `operator<`) |
| `_termValidSclkCache`, `_collectSclkCache` | latent-only / MT-unreachable on current graph — see `cts_nd_details.md` |
| `processSccBagIntoCache` | latent-only (disjoint bags; assemble reorders) |
| Test RNG (`ctsui/*RandomTest*`, `skewgrp` test harness) | debug/test only |

---

## DO / DON'T

**DO:** Use `ndmObjPtrCmpType` on QoR pointer containers; canonicalize before observable sinks; align MT grain with `getMaxThreadCount()`; use app-option seeds for any intentional sampling.

**DON'T:** Iterate raw `std::set<T*>` when mutating shared design state; use `random_device` on production QoR paths; assume parallel `double` sums are associative.

---

## Verification notes

- **Method:** ripgrep + manual triage (no `scan_nd.py`)
- **Root:** local `c:\Users\carys\cts`
- **Not run:** `clangd_query.py`, `icc2query`, Perforce `p4 annotate`
- **Related prior work:** `cts_nd_details.md`, `nd_mt_candidates_discovery.md`

---

To persist this as a file once disk space is freed:

```powershell
# After freeing space on C:
Set-Content -Path "c:\Users\carys\cts\nd_report_high_medium.md" -Encoding UTF8
# paste report body, or ask me to re-write the file
```

I can re-write the markdown file when disk space is available, or drill into any single finding (downstream callers, fix patch, MT prove-nd pass).

---

**User**

Please write to file

---

**Cursor**

I'll write the full HIGH/MEDIUM ND report to a markdown file now.


Disk has space again. Writing the full report now.

Written to **`C:\Users\carys\cts\nd_report_high_medium.md`** (~18 KB): full HIGH/MEDIUM ND report with summary table, four findings, fixes, dismissed buckets, and verification notes.

