# 03. Experimental Progression

## Original hypothesis

The initial hypothesis was broad: CoreStory application intelligence might improve ND analysis by adding application context that is difficult for a model to reconstruct from local source inspection alone.

The evaluation evolved as evidence accumulated.

## TC-001A: baseline exploratory discovery

CoreStory was disabled. The Synopsys ND workflow operated against the CTS repository.

The mechanical discovery stage produced **4,535 hits across 817 files** before narrowing to **1 HIGH and 6 MEDIUM** promoted findings.

The primary learning was the scale of the filtering problem. A suspicious source construct is only a candidate. The engineering problem is deciding which candidates survive deeper analysis.

A representative promoted finding was ctoFlowClone.cc, where raw-pointer ordering fed order-sensitive behavior.

### Limitation

This was exploratory, not a controlled benchmark. It established a baseline workflow behavior and candidate funnel.

## TC-001B: CoreStory-assisted exploratory qualification

The broad task was repeated with CoreStory application intelligence and a qualification rule.

The final report promoted **0 HIGH and 0 MEDIUM** findings.

The useful result was not the zero count. It was why candidate dispositions changed.

For ctoFlowClone.cc, the CoreStory-assisted investigation reported that the suspicious file was not part of the relevant production build and that the active implementation used a stable comparator type.

Another candidate containing std::random_device was reported as dead or unused because its identified caller was commented out and no live reference was established.

### Learning

Build inclusion, implementation relationships, reachability, and downstream application behavior can change the relevance of a locally credible mechanism.

### Limitation

This did not prove that every dismissal was correct, and it did not isolate CoreStory as the causal variable.

## TC-001C: qualification rule refinement

The exploratory findings were converted into a more explicit evidence gate:

**candidate → build inclusion → production reachability → runtime/configuration → exact mechanism → propagation → neutralizer/canonicalization → observable consequence**

The run produced approximately **15,000 mechanical candidates before narrowing** and showed more systematic qualification behavior.

### Learning

The qualification dimensions were useful, but autonomous child/subagent execution changed the topology. This prevented a defensible causal comparison between rule versions.

## Customer-controlled A/B: Test 1

The customer executed an end-to-end comparison of its existing workflow and a CoreStory-assisted workflow.

At face value, the existing workflow had stronger discovery coverage against the customer's initial source-reviewed union. The important follow-up was that four independent disagreement investigations showed that some apparent discovery differences were actually qualification disagreements.

## Focused disagreement investigations

A fixed independent configuration was used: Cursor, Claude Opus 4.8 with High thinking, CoreStory MCP against project 10, no CoreStory ND rule, no customer ND discovery/proof skills, and only the agentic bug-resolution workflow.

The previous A/B conclusions were withheld from the focused investigation.

| Candidate | A/B appearance | Focused result |
| --- | --- | --- |
| soSolverUpdater.cc:2100 | Existing workflow only | Reported race not substantiated; residual runtime/library question |
| msDrivers.cc:711 | CoreStory-assisted only | Source-substantiated latent ND in specific callers |
| ccdcgSolver.cc:501 | Existing workflow promoted, CoreStory-assisted dismissed | Dismissal supported for fixed-seed RNG mechanism |
| msuiGetPowerTaps.cc | CoreStory-assisted promoted | Promotion not substantiated because load-bearing container semantics were unavailable |

### Learning

Raw promoted-finding counts were not enough to explain the differences. Application tracing could improve or weaken a candidate. Missing evidence could also lead the CoreStory-assisted workflow to overreach.

## Iteration 2, first discovery-focused attempt

The workflow was redesigned to separate discovery from qualification.

The design principle was: **Discovery may expand but must not filter. Qualification may narrow based on evidence.**

The first run showed apparent CoreStory discovery expansion, but it had important experimental problems. The actual customer scan_nd.py was unavailable and its behavior was recreated. Explore subagents were not used because the Cursor Explore SubAgent Model setting had been left disabled. The same invocation also continued into later proof and qualification.

The apparent discovery gains therefore could not be treated as clean evidence.

## Iteration 2, final controlled discovery run

The experimental problems were corrected:

- actual customer scanner obtained and fingerprinted;
- exact reference set verified;
- Explore SubAgent Model set to Inherit from Parent;
- customer subagent dispatch behavior preserved;
- CoreStory constrained to project 10;
- thin discovery rule used;
- discovery and qualification separated into independent invocations;
- run stopped after the Stage 1 candidate set was frozen.

The result was **3,673 raw scanner candidates, 27 customer patterns, 588 files, 7 Explore subagents, 334 frozen customer-workflow candidates, 0 CoreStory-added candidates, and 0 materially broadened discovery paths.**

## Why the progression matters

The final result was not selected because it supported a preferred conclusion. Earlier apparent CoreStory gains were discarded as proof when experimental deficiencies were identified. Those deficiencies were corrected and the experiment was repeated.

The cleaner experiment produced a weaker discovery result for CoreStory.

That is why the final controlled run should carry more weight than the first Iteration 2 attempt.
