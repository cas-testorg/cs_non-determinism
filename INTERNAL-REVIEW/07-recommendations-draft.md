# 07. Recommendations Draft

> This section is intentionally written as a starting point in first person. It is expected to be edited into the presenter's own wording.

## Where I think we go from here

Based on what we've seen so far, I don't think another round of tuning around broad non-determinism discovery is where we're going to learn the most.

The Synopsys workflow is already highly specialized for this problem. We have now tested CoreStory alongside that process in several different ways. In the most controlled discovery run, using the actual customer scanner, exact reference material, and intended subagent behavior, we did not materially expand what the existing process discovered.

I think that is useful evidence, even though it is not the result we originally set out to prove.

I do think there is another part of the workflow worth exploring. Once a candidate has been identified, there is still significant work involved in understanding whether it matters in the application, whether it is built and reachable, what configuration enables it, which callers preserve the behavior, whether anything neutralizes it, and what evidence an SME needs to make a decision.

Some of the focused investigations gave us useful signals there. They also showed that we need to be disciplined about missing evidence. If a load-bearing implementation is not available, the result should remain unresolved rather than filling the gap with inference.

My next step would be to test whether CoreStory can help **resolve application significance, reduce uncertainty, and produce better evidence for SME review**.

I would keep that test separate from discovery. Start with the same frozen candidate set, let the existing Synopsys workflow establish the mechanism, and measure what CoreStory adds to the application-level evidence.

There is also an economics question I think is worth measuring. If application context has to be reconstructed repeatedly through source searches and model reasoning, there may be an opportunity to reduce that work by retrieving application relationships from a persistent intelligence layer instead. I don't think we should assume that creates savings. We should measure it.

The measures I would care about include the amount of source searching and tool work required, how much evidence remains unresolved, how much additional context the SME has to request, and ultimately how long it takes to reach a confident SME decision. If reliable token or compute telemetry is available, that should be included as another measure rather than treated as the only measure.

Beyond this particular ND workflow, I think we should spend more time on use cases where application context is central to the problem from the beginning. Impact analysis, dependency tracing, modernization planning, business-rule understanding, and carrying a validated problem into remediation are examples that appear more naturally aligned with what CoreStory provides.

If the application-significance experiment does not show differentiated value either, I would preserve the evidence and move on again rather than continuing to tune the same hypothesis.

## Short version for discussion

> We have given the broad ND discovery hypothesis several serious attempts, including a final controlled run using the customer's actual workflow. We did not demonstrate incremental discovery value. I think the more useful next question is whether CoreStory can help after discovery by resolving application significance, reducing uncertainty, and producing better evidence for the SME. I also want to measure whether persistent application context changes the economics of that work. In parallel, I think we should evaluate use cases where application context is the core problem rather than trying to reproduce a highly specialized detector.
