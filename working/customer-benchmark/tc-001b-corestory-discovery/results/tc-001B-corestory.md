# Code analysis report generation
_Exported on 9/9/2026 at 15:04:05 CDT from Cursor (3.18.25)_

---

**User**

/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report

---

**Cursor**

I'll follow the non-determinism analyzer skill and scan `C:\Users\carys\cts` for HIGH/MEDIUM findings, then produce a shareable markdown report.

Running the mechanical scan and checking CoreStory plus the repo layout.

Scripts are missing from the skill package; I'll drive Stage 1 from `nd-patterns.yaml` with ripgrep, then triage with CoreStory.

Found existing ND scan artifacts from today — I'll inspect them and finish the HIGH/MEDIUM report from there.

Verifying the four reported findings in source and running a fresh HIGH/MEDIUM mechanical pass for anything missed.

H1 may be dead code — the only call site looks commented out. Digging into callers and hunting other HIGH/MEDIUM candidates.

Prior report's four findings don't hold after caller/build checks. Hunting real HIGH/MEDIUM issues next.

Prior report’s four “real” issues don’t survive caller/build checks. Writing the corrected HIGH/MEDIUM report (empty findings, documented dismissals) plus `findings.json`.

**Result: 0 HIGH and 0 MEDIUM confirmed equivalent-run ND defects** in `C:\Users\carys\cts`.

### Shareable report
- [`nd_analysis_cts_20260909.md`](C:\Users\carys\cts\nd_analysis_cts_20260909.md) (canonical)
- Copy: `C:\Users\carys\.cursor\plans\nd_analysis_cts_20260909.md`
- Machine-readable: [`nd_cts_findings.json`](C:\Users\carys\cts\nd_cts_findings.json)

### Why prior draft findings were dropped
| Draft claim | Why dismissed |
|---|---|
| fmax `random_device` UNIFORM | Only call site is commented out → **dead** |
| `ctoFlowClone` pointer `std::set` | Not in `ctscto/Master.make`; production uses `ctoRestruct` + `termSetType` (`ndmObjPtrCmpType`) → **dead / safe-adopter** |
| Parallel TNS fold | Thread-index merge; stable for fixed thread count → **config sensitivity** |
| `hardware_concurrency` grain | Disjoint `grpLat[i]` writes → **no result ND** |

CTS production paths look largely ND-aware (`termSetType`, `ndmPtrMap`, Coverity canonicalize helpers). Latent MT cache suspects remain in prior MT notes, not elevated without TSan/prove-nd-mt.

