# 07. Recommendations Draft

> This section is intentionally written as a starting point in first person. It is expected to be edited into the presenter's own wording.

## Where I think we go from here

Based on what we've seen so far, I don't think another round of tuning around broad non-determinism discovery is where we're going to learn the most.

The Synopsys workflow is already highly specialized for this problem. We have now tested CoreStory alongside that process in several different ways. In the most controlled discovery run, using the actual customer scanner, exact reference material, and intended subagent behavior, we did not materially expand what the existing process discovered.

I think that is useful evidence, even though it is not the result we originally set out to prove.

Where I think this gets more interesting is what happens after a specialized defect or high-confidence candidate has been identified.

There is still a lot of engineering work between "we found a non-determinism mechanism" and "we understand this well enough to act on it." We need to know whether it matters in the production application, what configuration enables it, which callers preserve or neutralize it, what application flows it can affect, what the blast radius is, where a fix belongs, and what needs to be validated if we change it.

Some of the focused investigations gave us useful signals in that direction. They also showed that we need to be disciplined about missing evidence. If a load-bearing implementation is not available, the result should remain unresolved rather than filling the gap with inference.

So I would broaden the next test beyond producing better evidence for the SME.

I would test whether CoreStory can provide **application-aware defect intelligence** that helps move a specialized finding toward an actionable engineering decision.

For me, that means testing whether we can establish:

- production relevance;
- configuration and runtime scope;
- affected callers and application flows;
- propagation and neutralization;
- application impact;
- remediation scope;
- blast radius;
- regression and validation requirements.

A better SME evidence package should fall out of that work, but I don't think the evidence package should be the end goal. The larger value would be reducing the amount of application reconstruction required to understand the defect and move it toward resolution.

I would keep this test separate from discovery. Start with the same frozen set of validated or high-confidence candidates, let the existing Synopsys workflow establish the specialized mechanism, and then compare how far the existing workflow and a CoreStory-assisted workflow can take an engineer toward a production-ready decision.

There is also an economics question I think is worth measuring. If application context has to be reconstructed repeatedly through source searches and model reasoning, the opportunity may be larger than token savings in one analysis run. The same reconstruction can happen during qualification, SME review, impact analysis, remediation planning, and validation planning.

I don't think we should assume persistent context creates savings. We should measure it.

The measures I would care about fall into three areas.

**Technical depth:** How much production relevance, application impact, blast radius, remediation scope, and validation planning can we establish?

**Engineering efficiency:** How much source searching, tool work, context reconstruction, and investigation time does it take to get there?

**SME efficiency:** How complete is the evidence when it reaches the SME, how much follow-up context is required, and how quickly can a confident decision be made?

If reliable token or compute telemetry is available, I would include it as part of engineering efficiency rather than make it the entire economic argument.

Beyond this particular ND workflow, I think we should spend more time on use cases where application context is central to the problem from the beginning. Impact analysis, dependency tracing, modernization planning, business-rule understanding, and carrying a validated problem into remediation are examples that appear more naturally aligned with what CoreStory provides.

If this broader application-aware defect intelligence experiment does not show differentiated value either, I would preserve the evidence and move on again rather than continuing to tune the same hypothesis.

## Short version for discussion

> We have given the broad ND discovery hypothesis several serious attempts, including a final controlled run using the customer's actual workflow. We did not demonstrate incremental discovery value. I think the more interesting question now is what happens after a specialized defect is found. Can CoreStory use its understanding of the application to establish production relevance, trace the impact, define remediation scope and blast radius, and help build the validation plan? Better SME evidence should be one result of that, but not the whole value proposition. I also want to measure whether persistent application context reduces the repeated reconstruction work across that lifecycle. In parallel, I think we should evaluate use cases where application context is the core problem rather than trying to reproduce a highly specialized detector.
