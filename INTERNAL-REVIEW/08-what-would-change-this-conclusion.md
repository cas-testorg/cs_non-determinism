# What Would Change This Conclusion?

## Purpose

The current recommendation is based on the tested configuration and the evidence available today. It should be revisited if the experimental conditions materially change or if new evidence contradicts the current result.

## Reasons to revisit broad ND discovery

Broad discovery would be worth retesting if one or more of the following changes occur:

1. **Broader application ingestion.** The missing upstream dos, ndm, nwtn, comparator, container, or related implementation libraries are ingested and CoreStory can resolve semantics that were unavailable in project 10.
2. **A different source estate.** The evaluation moves beyond the CTS source surface on which the customer already has highly specialized pattern coverage.
3. **Systematic cross-module misses are identified.** SME review or runtime evidence shows that the customer discovery workflow repeatedly misses candidates that require relationships CoreStory can retrieve.
4. **Provenance shows CoreStory was materially underused.** Better instrumentation demonstrates that the measured workflow did not actually invoke the application intelligence needed to test the hypothesis.
5. **CoreStory gains a materially different discovery capability.** A product or workflow change creates a new source of candidate discovery rather than another prompt/rule tuning pass over the same information.

Without one of these changes, another broad-discovery tuning cycle would largely repeat a hypothesis already tested under progressively improved controls.

## What would support application-aware defect intelligence

The next hypothesis should earn its place through measurable results.

Evidence in its favor would include consistent improvement on the same frozen defects in one or more of these areas:

- more complete production relevance;
- better identification of configuration and runtime scope;
- more complete affected-caller and application-flow tracing;
- clearer propagation and neutralization evidence;
- better-supported application impact;
- more complete blast-radius analysis;
- more actionable remediation boundaries;
- stronger regression and validation planning;
- fewer unresolved application-context questions;
- less repeated source/context reconstruction;
- less SME follow-up required to reach a decision.

## What would cause another pivot

The application-aware defect intelligence hypothesis should not become another open-ended tuning exercise.

If a controlled comparison shows that CoreStory does not materially improve technical depth, engineering efficiency, or SME decision support, the result should be preserved and the evaluation should move to a different use case.

Likewise, if the existing Synopsys workflow already produces the same application impact, remediation scope, and validation understanding with comparable or better effort, that would weaken the differentiation hypothesis even if CoreStory can technically produce similar answers.

## Economics threshold

Token economics should not be used as a fallback argument if technical value is weak.

Economic value should be measured only after the workflow demonstrates useful technical output. Relevant evidence may include model/tool usage, source searches, files/context inspected, elapsed engineering effort, repeated reconstruction avoided, SME follow-up effort, and time-to-decision.

If reliable telemetry is unavailable, the package should continue to label the economic case as a theory rather than estimate savings.
