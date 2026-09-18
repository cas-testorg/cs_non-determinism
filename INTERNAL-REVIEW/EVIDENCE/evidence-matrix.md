# Evidence Matrix

## Purpose

This matrix is the shortest path from the review's conclusions to the experimental record.

It separates observation from interpretation. Where a result has an important boundary, that boundary is included in the same row rather than left for a footnote.

| Observation | Primary evidence | Observed result | Boundary / limitation | What it supports |
| --- | --- | --- | --- | --- |
| The existing Synopsys ND process is highly specialized | Customer nd-code-analyzer skill, 27-pattern reference set, scanner, prove-nd and prove-nd-mt workflows | Purpose-built mechanical discovery, project-specific semantic guidance, parallel Explore triage, observability reasoning, and dedicated proof stages | Specific to this customer workflow and source estate | Incremental CoreStory discovery value is being tested against a mature specialized baseline, not generic source search |
| Repository-scale ND analysis creates a large narrowing problem | TC-001A baseline | 4,535 mechanical hits across 817 files narrowed to 1 HIGH and 6 MEDIUM promoted findings | Exploratory run, not controlled benchmark | Candidate discovery and engineering significance are different problems |
| Application context changed early candidate dispositions | TC-001B | CoreStory-assisted analysis promoted 0 HIGH and 0 MEDIUM; ctoFlowClone was reported outside the relevant production build with an active stable-comparator implementation; another RNG candidate was reported dead/unused | Exploratory; prior artifacts available; causal contribution of MCP not isolated | Build inclusion, implementation relationships, and reachability can materially affect candidate relevance |
| Explicit application qualification gates were operationally useful | TC-001C | Evidence gate formalized build, reachability, runtime/configuration, mechanism, propagation, neutralization, and observable consequence | Child/subagent topology prevented a defensible causal comparison between rule versions | Qualification dimensions are useful investigation structure, but discovery and qualification need to be separated experimentally |
| Initial customer A/B favored the existing workflow on broad discovery | Test 1 customer comparison | Without MCP: 19 promoted, 8 source-confirmed unique. With MCP: 6 promoted, 4 source-confirmed unique. Initial source-reviewed union: 9 unique ND issues | Source-reviewed, not runtime ground truth. Runtime reproduced: 0. End-to-end arms included discovery and qualification differences | Broad discovery advantage was not demonstrated for the CoreStory-assisted workflow |
| A shorter CoreStory-assisted list was not automatically a higher-quality list | Test 1 customer comparison | Two of six With-MCP promoted rows did not survive later source review | Initial source review itself was later challenged in focused cases | Candidate count alone is not a sufficient quality measure |
| One apparent CoreStory discovery miss became an adjudication disagreement | Focused soSolverUpdater investigation | Prepopulation, partitioning, and lack of demonstrated concurrent structural mutation challenged the reported race mechanism | Narrow standard-library/runtime question remains; SME/runtime validation needed | Some apparent recall differences are actually qualification/adjudication differences |
| A CoreStory-assisted-only candidate survived deeper application tracing | Focused msDrivers findDriverTerm investigation | Raw-pointer set last-wins scalar behavior was narrowed to specific MLPH/auto-tap callers with a credible path into clock/sink selection | Trigger configuration and runtime occurrence remain to be confirmed | Application tracing can turn a broad candidate into a more specific application-relevant hypothesis |
| A CoreStory-assisted dismissal survived deeper investigation | Focused ccdcgSolver investigation | Fixed seed, immediate reseed, sequential consumption, no relevant concurrent RNG consumer | Upstream candidate/index ordering remains a residual question | Application/execution context can eliminate an apparent ND mechanism while preserving unresolved upstream questions |
| CoreStory-assisted reasoning can overreach when load-bearing evidence is absent | Focused msuiGetPowerTaps investigation | Critical dosUnorderedSet/hash and downstream conversion implementations were unavailable; promotion could not be substantiated | Missing implementation is not proof of safety | Missing load-bearing evidence must produce UNRESOLVED, not inferred REAL |
| The first Iteration 2 discovery signal was experimentally confounded | First Iteration 2 run | Apparent CoreStory-only candidates were observed | Actual customer scanner missing, Explore subagents disabled, later stages continued in same invocation | Earlier apparent discovery expansion should not be treated as clean evidence |
| The final discovery test restored the intended customer workflow | Second Iteration 2 run manifest | Exact reference artifacts verified, actual scan_nd.py used, 27 patterns loaded, 7 inherited Explore subagents completed, project 10 only, Stage 1 hard stop | Five scanner patterns reached the configured 500-hit cap | This is the strongest controlled discovery run in the package |
| CoreStory did not add differentiated broad discovery in the final controlled run | Second-run candidate set and discovery readout | 3,673 raw candidates across 588 files, 334 frozen candidates, 334 CUSTOMER-PATTERN, 0 CORESTORY-EXPANSION, 0 BOTH, 0 materially broadened paths | Result applies to the tested source and ingestion scope | Continued tuning of the same broad-discovery hypothesis has diminishing information value |
| CoreStory's available application scope constrained some analysis | Second-run manifest/readout and focused investigations | Upstream dos/ndm/nwtn comparator and wrapper implementations were not available in project 10; 25 frozen candidates were UNRESOLVED at discovery time | Broader ingestion could change what application evidence is retrievable | Do not generalize the zero-expansion result into a universal product limitation |
| The experiments expose work after specialized detection | Four focused investigations | Production relevance, configuration, caller-specific preservation, propagation, neutralization, impact, and missing evidence changed or narrowed candidate interpretation | Small focused sample, not aggregate proof | Application-aware defect intelligence is a credible next hypothesis |
| Better SME evidence is potentially valuable but is not the full proposed outcome | Focused investigations plus workflow analysis | The same application analysis can inform production relevance, impact, remediation boundary, blast radius, and validation planning | These later lifecycle benefits have not yet been measured in a controlled comparison | SME decision support should be treated as one benefit of a broader defect-to-action workflow |
| Persistent application intelligence may change workflow economics | Existing workflow structure and repeated source reconstruction observed across experiments | Discovery, qualification, focused investigation, SME review, impact analysis, and remediation can each require application context reconstruction | Reliable token/time/cost telemetry is incomplete | Token, model/tool, engineering, and SME economics are testable hypotheses, not current savings claims |

## Evidence-weighting guidance

The final controlled discovery run should carry more weight for the discovery question than the first Iteration 2 run because the known scanner and subagent deviations were corrected.

The four focused investigations should carry more weight for the four individual candidate dispositions than the original A/B summary because they were designed specifically to inspect those disagreements. They do not replace aggregate A/B evidence.

Source-reviewed findings should not be described as runtime-confirmed defects. Runtime reproduction and SME validation remain separate evidence classes.

## Current evidence-supported stopping point

The evidence supports stopping repeated tuning of the current broad-discovery hypothesis unless a material condition changes.

It does not yet support claiming that CoreStory improves the full defect lifecycle.

The next falsifiable question is whether CoreStory can take the same specialized defect and improve the path toward an actionable engineering decision through production relevance, application impact, remediation scope, blast radius, and validation planning.
