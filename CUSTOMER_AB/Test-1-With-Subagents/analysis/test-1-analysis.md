# Test 1 — With Subagents: Analysis Notes

## Purpose

This file is a CoreStory-side synthesis of the customer-provided Test 1 artifacts. It does not replace or modify the raw reports, and it does not treat the customer-generated comparison as final SME validation.

The test compares two end-to-end workflows on the same CTS source snapshot:

- **Without MCP:** Synopsys ND workflow, 19 promoted HIGH/MEDIUM findings.
- **With MCP:** CoreStory-assisted workflow, 6 promoted MEDIUM findings after approximately 2,080 triaged candidates.

Because the two workflows discovered and qualified their own candidates, this test does **not** isolate CoreStory application qualification from ND discovery. Subagent behavior is also part of this test configuration.

## Customer-generated adjudication

The supplied comparison re-read source for the union of promoted findings and normalized them by source site/root cause. It reports:

| Measure | Without MCP | With MCP |
|---|---:|---:|
| Promoted rows | 19 | 6 |
| Source-confirmed unique ND issues found | 8 | 4 |
| Recall against 9-issue source-confirmed union | 89% | 44% |
| Promoted rows surviving as unique ND | 8/19 | 4/6 |

Across both arms, the comparison identifies 22 unique promoted rows, 9 source-confirmed current ND issues, 1 duplicate root cause, 10 rows that are not current ND defects, and 2 unresolved ND statuses. No finding was runtime-reproduced.

These are **source-review results from the supplied comparison**, not yet the final SME verdict.

## What Test 1 appears to show

### 1. The existing Synopsys workflow was stronger at discovery in this run

The Without-MCP arm found 8 of the 9 source-confirmed issues in the union, including the shared-map data race in `soSolverUpdater.cc:2100`. The With-MCP arm found 4 of 9.

This is the clearest result from Test 1 and should not be obscured by the smaller CoreStory finding count.

### 2. A shorter promoted list did not automatically mean better qualification

The With-MCP report claimed all six promoted findings survived its proof pass. The later comparison rejected two:

- `msuiGetPowerTaps.cc:66,879` — the reported address-hash mechanism was contradicted by the implementation of `dosContainer::keyHash`.
- `msDrivers.cc:3330` — the suspicious implementation had no current caller and was classified dead/unused.

The With-MCP arm therefore showed useful filtering, but its own proof stage was not sufficient to make every promoted result reliable.

### 3. CoreStory-associated reasoning was useful on at least one direct disagreement

For `ccdcgSolver.cc:501`, the Without-MCP report promoted the global `rand()` usage as ND. The With-MCP path dismissed it. The supplied comparison supports the dismissal because `srand(100)` is followed by sequential consumption and no varying production input was established.

This is a useful example of candidate qualification preventing a suspicious construct from becoming an ND finding.

### 4. Build/reachability qualification was mixed in both arms

The comparison found complementary mistakes:

- Without MCP promoted `ctoFlowClone.cc:1884`, but the file is not in the relevant production build and the live replacement uses a stable comparator type.
- With MCP promoted `connectUnassignedLoads` in `msDrivers.cc:3330`, but no current caller was found.

This supports application qualification as a valuable stage, but Test 1 does not show that either end-to-end workflow applied it consistently.

### 5. The two workflows had different discovery strengths

The supplied comparison attributes several Without-MCP-only discoveries to broad sink tracing, including the solver race, auto-balance feedback, pointer-hash/FP reduction, keepout early-return behavior, and endpoint priority chain.

The With-MCP workflow uniquely surfaced `findDriverTerm` in `msDrivers.cc:711`, where an accessor exposes a raw-pointer set and the last iterated driver can become the returned value. The comparison classifies this as a conditional real ND issue.

This suggests the workflows were not merely producing different precision/recall from the same candidate pool; they were traversing the problem differently.

## Current interpretation

Test 1 supports the following cautious interpretation:

> In the subagent-enabled end-to-end test, the existing Synopsys workflow demonstrated better discovery recall. The CoreStory-assisted workflow produced a smaller result set and showed useful qualification behavior on some candidates, but it also missed source-confirmed findings and promoted two candidates that did not survive the later source review.

That makes it premature to claim that CoreStory improves the complete ND discovery workflow.

At the same time, the disagreements strengthen the case for separately testing **application qualification** on a fixed candidate set. The current end-to-end design mixes discovery quality, ND mechanism reasoning, application context, proof behavior, and orchestration.

## Questions to carry into SME review

1. Does the SME agree with the nine source-confirmed ND issues in the supplied comparison?
2. Does the SME agree that the two CoreStory-promoted rows rejected by the comparison are not current ND defects?
3. Does the SME agree with the CoreStory-side dismissal of the fixed-seed `rand()` candidate?
4. Which Without-MCP-only findings represent true discovery misses versus candidates CoreStory encountered but filtered?
5. At what workflow stage did subagents execute, and which models handled discovery versus proof?
6. Did model/subagent routing differ between the two arms enough to confound attribution?
7. For a future fixed-candidate test, what evidence does the SME actually need to make a disposition quickly?

## Claim boundary

Do not use Test 1 alone to claim:

- that CoreStory improves ND discovery;
- that the smaller With-MCP list is inherently higher quality;
- that any source-confirmed issue has been runtime reproduced;
- that the 9-issue union is ground truth;
- that observed differences are attributable only to MCP/CoreStory.

Test 1 is useful evidence about workflow behavior. Final defect accuracy still requires SME validation and, for runtime claims, targeted reproduction.
