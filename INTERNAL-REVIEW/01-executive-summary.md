# 01. Executive Summary

## What we evaluated

The evaluation tested whether CoreStory application intelligence could add differentiated value to an existing Synopsys AI-assisted non-determinism workflow operating on Fusion Compiler CTS C/C++ source.

This is an unusually specialized baseline. The existing workflow includes a purpose-built scanner, a 27-pattern non-determinism catalog, project-specific examples and false-positive guidance, semantic triage, downstream-observability reasoning, parallel Explore subagents, and dedicated proof workflows.

The evaluation therefore did not compare CoreStory with generic source search or a generic coding assistant. It tested incremental value against an already-specialized workflow.

## What we tried

The work progressed through several increasingly controlled stages:

1. Baseline repository-scale ND discovery without CoreStory.
2. CoreStory-assisted exploratory analysis and qualification.
3. A refined CoreStory qualification rule with explicit evidence gates.
4. A customer-controlled end-to-end A/B comparison.
5. Independent focused investigations of important A/B disagreements.
6. A discovery-specific CoreStory integration intended to expand, but never filter, the customer candidate set.
7. A final controlled discovery run using the customer's actual scanner, exact reference artifacts, and intended subagent topology.

When experimental weaknesses were found, they were corrected and the experiment was repeated rather than using the earlier result as proof.

## What the evidence says about broad discovery

The final controlled discovery run is the cleanest evidence.

- Actual customer scan_nd.py executed.
- Exact customer skill/reference fingerprints verified.
- 27 customer ND patterns loaded.
- 3,673 raw candidates produced across 588 files.
- The customer workflow's parallelization threshold triggered.
- Seven Explore subagents ran with the configured inherited model.
- 334 candidates were frozen after customer-workflow triage.
- All 334 originated from the customer pattern/reference workflow.
- CoreStory added **0** candidates.
- CoreStory materially broadened **0** discovery paths.
- Six targeted CoreStory semantic searches produced corroborating context, but no new useful discovery location.

The final run also exposed an application-scope limitation. Several unresolved comparator, wrapper, and container implementations reside in upstream libraries that were not ingested into the CoreStory project used by the test. The result should therefore be read as evidence for the tested application scope, not as a universal statement about CoreStory.

## What the A/B taught us

Customer A/B Test 1 initially favored the existing workflow on discovery coverage against the customer's source-reviewed union. The existing workflow promoted 19 findings and the CoreStory-assisted workflow promoted 6. The initial comparison identified 9 source-confirmed unique ND issues, with 8 found by the existing workflow and 4 by the CoreStory-assisted workflow.

Four independent disagreement investigations showed why raw counts were not enough:

- One apparent CoreStory miss, soSolverUpdater.cc:2100, became an adjudication disagreement because the focused investigation did not substantiate the reported race mechanism.
- One CoreStory-assisted-only candidate, msDrivers.cc:711, survived focused source qualification as latent ND with specific unneutralized callers.
- One CoreStory-assisted dismissal, fixed-seed RNG in ccdcgSolver.cc, was supported by the focused investigation.
- One CoreStory-assisted promotion, msuiGetPowerTaps, was not substantiated because the load-bearing container semantics were unavailable and had been inferred too aggressively.

This does not prove aggregate qualification improvement. It does show that application-level evidence can materially change candidate disposition and that missing load-bearing evidence must be represented as unresolved rather than filled in by inference.

## Current interpretation

The evidence does not currently demonstrate differentiated value from adding CoreStory to broad ND candidate discovery in this configuration.

The next question should be broader than whether CoreStory can produce a better evidence packet for an SME:

> **Can CoreStory take a specialized defect identified by the existing Synopsys workflow and accelerate the path from candidate to actionable engineering decision by establishing production relevance, application impact, remediation scope, and validation requirements?**

This is the **application-aware defect intelligence** hypothesis.

Potential CoreStory value would span a larger part of the defect lifecycle:

**specialized discovery → mechanism proof → production relevance → application impact → SME decision → remediation scope → blast radius → validation plan**

Synopsys already appears strong on specialized discovery and mechanism analysis. The potential differentiation grows as the workflow requires broader application understanding.

SME decision support remains important, but it becomes one outcome of the process rather than the endpoint.

## Economics hypothesis

A separate economics hypothesis also remains open:

> Can persistent application intelligence reduce repeated application reconstruction across the defect lifecycle?

The opportunity is not limited to token reduction during discovery. Application relationships may otherwise be reconstructed repeatedly during qualification, SME review, impact analysis, remediation planning, and validation planning.

This should be measured, not assumed.

## Suggested direction

Preserve the discovery evidence as a completed experimental result. Avoid another tuning cycle around broad discovery unless the experimental conditions materially change.

Use a frozen set of validated or high-confidence candidates to test how far the existing workflow and a CoreStory-assisted workflow can take an engineer toward a production-ready decision.

Measure at least three dimensions separately:

1. **Technical depth:** production relevance, configuration scope, affected callers and flows, propagation, neutralization, application impact, remediation boundary, blast radius, and validation requirements.
2. **Engineering efficiency:** source searches, tool work, files/context inspected, unresolved dependencies, elapsed investigation effort, and reliable token/compute measures where available.
3. **SME efficiency:** evidence completeness, requests for additional context, time-to-decision, and agreement/disagreement/insufficient-evidence outcomes.

In parallel, evaluate use cases where persistent application context is central to the problem from the beginning, such as impact analysis, cross-module dependency understanding, modernization planning, business-rule analysis, and carrying a validated engineering problem into remediation.
