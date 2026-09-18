# Test 1 — Finding-Level Crosswalk

This crosswalk reorganizes the customer-generated 22-row comparison around the question we care about for the POV: **where did the two workflows agree, where did they differ, and was the difference primarily discovery or qualification?**

The final-source-review column reflects the supplied `snps_core_nd_comparison.md`, not an independent CoreStory verdict and not yet final SME validation.

| # | Candidate | Without MCP | With MCP | Source review | Difference type | What to inspect next |
|---:|---|---|---|---|---|---|
| 1 | `ctsAutoBalancePoint.cc:656` | Promoted | Not reported | Real | Discovery miss (With MCP) | Why sink/feedback tracing did not surface it |
| 2 | `msDrivers.cc:8189` | Promoted | Promoted | Conditional real | Agreement | Severity/gating only |
| 3 | `ctoscGlobal.h:274` | Promoted | Not reported | Conditional real | Discovery miss (With MCP) | Pointer hash → FP accumulation → sink chain |
| 4 | `ctskSize.cc:1384` | Promoted | Not reported | Not ND | Qualification issue (Without MCP) | ND vs performance/name-stability taxonomy |
| 5 | `fmaxLpSolverIncremental.cc:5127` | Promoted, later corrected | Not reported | Not ND | Qualification/self-correction | Whether proof stage consistently reclassifies deterministic bugs |
| 6 | `soSolverUpdater.cc:2100` | Promoted | Not reported | Real data race | Discovery miss (With MCP) | Highest-priority miss; inspect parallel sink tracing |
| 7 | `ctoFlowClone.cc:1884` | Promoted | Not reported | Dead/stale | Qualification issue (Without MCP) | Build inclusion correctly prevented With-MCP promotion |
| 8 | `msDrivers.cc:11645` | Promoted | Not reported | Conditional real | Discovery miss (With MCP) | Address-order + early-return sink |
| 9 | `msLevelBalancer.cc:1745` | Promoted | Promoted | Conditional real | Agreement | Feature gate/default |
| 10 | `ctomtEndpointTypes.h:32` | Promoted | Not reported | Conditional real | Discovery miss (With MCP) | Endpoint priority propagation |
| 11 | `ctsIfsDataType.h:32` | Promoted | Not reported | Duplicate of #10 | Qualification/grouping issue | Upstream evidence, not separate defect |
| 12 | `ccdcgSolver.cc:501` | Promoted | Dismissed | Not ND | Qualification win (With MCP) | Fixed seed + sequential production consumption |
| 13 | `ctsICGCell.cc:514` | Promoted | Not reported | Not ND | Qualification issue (Without MCP) | Deterministic robustness/performance vs ND |
| 14 | `ctsXformProblems.cc:1130` | Promoted | Not reported | Not ND | Qualification issue (Without MCP) | Rename fragility vs run-to-run ND |
| 15 | `msInfra.cc:1255` | Promoted | Not reported | Not ND | Qualification issue (Without MCP) | Name round-trip robustness vs ND |
| 16 | `fmaxTimingCostFunction.h:277` | Promoted | Promoted | Real, bounded | Agreement | Cross-thread-count sensitivity, not same-N race |
| 17 | `ctsLazyModel.cc:4834` | Promoted, later unresolved | Not reported | Unresolved | Qualification/evidence gap | 32-vs-33-core runtime proof |
| 18 | `ctsTimingDrivenTransitionTargets.h:181` | Promoted | Not reported | Not proven ND; comparator bug | Qualification issue (Without MCP) | Need varying input / equivalent-run proof |
| 19 | `ctsUtils.cc:57` | Promoted | Not reported | Unresolved ND; real data-loss bug | Qualification/evidence gap | Prove upstream LEQ order varies |
| 20 | `msDrivers.cc:711` | Not promoted | Promoted | Conditional real | Discovery gain (With MCP) | Accessor-aware tracing; inspect why Without MCP missed it |
| 21 | `msuiGetPowerTaps.cc:66,879` | Not promoted/stable wrapper | Promoted | Not proven ND | Qualification error (With MCP) | Container taxonomy / stable ID hash |
| 22 | `msDrivers.cc:3330` | Dead/unused | Promoted | Dead/unused | Qualification error (With MCP) | Caller/reachability gate |

## Grouped view

### Found by both and supported by source review

- `msDrivers.cc:8189`
- `msLevelBalancer.cc:1745`
- `fmaxTimingCostFunction.h:277`

These are the strongest agreement cases.

### Source-supported findings found only by Without MCP

- `ctsAutoBalancePoint.cc:656`
- `ctoscGlobal.h:274`
- `soSolverUpdater.cc:2100`
- `msDrivers.cc:11645`
- `ctomtEndpointTypes.h:32`

These are the clearest With-MCP discovery misses in Test 1.

### Source-supported finding found only by With MCP

- `msDrivers.cc:711`

This is the clearest incremental discovery from the With-MCP workflow.

### Qualification behavior worth studying

**With-MCP useful qualification**
- `ccdcgSolver.cc:501` — dismissed; supplied comparison agrees it is not ND.
- `ctoFlowClone.cc:1884` — not promoted; supplied comparison later identifies the reported implementation as dead/stale.

**With-MCP qualification failures**
- `msuiGetPowerTaps.cc:66,879` — promoted using an incorrect container/hash assumption.
- `msDrivers.cc:3330` — promoted despite no current caller.

**Without-MCP qualification failures or unresolved promotion**
- Several deterministic functional/performance/robustness issues were promoted as ND.
- The later MT proof corrected some of these, demonstrating that the workflow's later proof stage materially changes the result.

## Working hypothesis for the next experiment

Test 1 makes a fixed-candidate qualification experiment more valuable.

Freeze the union of candidate findings, remove discovery as a variable, and ask the existing Synopsys proof path and a CoreStory-assisted qualification path to evaluate the same candidates. Compare:

- build inclusion;
- production reachability;
- runtime/configuration gates;
- mechanism evidence;
- propagation to an observable sink;
- deterministic neutralization;
- disposition accuracy against SME review;
- evidence quality delivered to the SME;
- investigation effort and token/tool cost.

That experiment would test the proposed CoreStory value at the qualification boundary without requiring CoreStory to outperform the existing Synopsys workflow at repository-scale ND discovery.
