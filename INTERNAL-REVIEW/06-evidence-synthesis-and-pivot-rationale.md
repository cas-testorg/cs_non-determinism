# 06. Evidence Synthesis and Pivot Rationale

## Broad ND discovery

The evidence is strongest here.

The existing Synopsys process has specialized ND knowledge, a 27-pattern scanner, project-specific semantic guidance, parallel triage, and downstream-observability reasoning.

The customer A/B initially favored the existing workflow on discovery coverage against its source-reviewed union.

The final controlled discovery run then gave CoreStory an expansion-oriented role while preserving every customer candidate. With the actual customer scanner and intended subagent topology restored, CoreStory added 0 candidates and materially broadened 0 discovery paths.

**Interpretation:** differentiated value in broad discovery has not been demonstrated in the tested configuration.

## Mechanism proof

Synopsys already has dedicated prove-nd and prove-nd-mt workflows.

The focused investigations show that exact C++ semantics still require careful source reasoning. CoreStory relationship context is not a substitute for resolving a comparator, hash implementation, RNG behavior, or concurrency mechanism.

**Interpretation:** replacing the specialized mechanism-proof workflow is not the strongest differentiation hypothesis.

## What the focused investigations exposed

The investigations point to a broader problem than candidate qualification.

Once a credible mechanism exists, an engineer still needs to understand:

- whether the code is actually built and production reachable;
- which runtime or configuration conditions enable it;
- which callers preserve the behavior and which neutralize it;
- how the behavior propagates through the application;
- which application flows or outputs may be affected;
- what the blast radius is;
- where the appropriate remediation boundary is;
- what a change could affect;
- what should be validated after remediation;
- what evidence remains unavailable and requires SME or runtime confirmation.

msDrivers.cc:711 illustrates the distinction. The interesting result was not simply more citations for an SME. The suspicious helper was narrowed to a small set of callers that preserved the scalar behavior and provided a credible path into clock/sink selection and potentially topology/QoR.

ccdcgSolver.cc shows the opposite case. Application and execution context supported elimination of the reported RNG mechanism and redirected attention toward a narrower upstream ordering question.

msuiGetPowerTaps shows the required guardrail. Missing load-bearing implementation evidence must remain unresolved rather than being converted into an inferred defect.

These examples suggest that the useful boundary may be larger than "qualification."

## Next hypothesis: application-aware defect intelligence

The next hypothesis is:

> **Can CoreStory take a specialized defect identified by the existing Synopsys workflow and accelerate the path from candidate to actionable engineering decision by establishing production relevance, application impact, remediation scope, and validation requirements?**

A possible division of labor is:

**Synopsys specialized discovery → mechanism proof → CoreStory-assisted production relevance and application impact → SME decision → remediation scope and blast radius → validation plan → engineering action**

This does not make CoreStory the authority on ND mechanism semantics. It tests whether persistent application intelligence becomes more valuable as the workflow moves from a specialized defect mechanism into the surrounding application.

### Layer 1: production relevance

Determine whether the mechanism matters in the application that is actually built and run:

- build inclusion;
- production reachability;
- runtime/configuration gates;
- active implementation;
- caller-specific preservation or neutralization;
- missing load-bearing evidence.

### Layer 2: application impact

Determine what a relevant defect can affect:

- affected application flows;
- downstream modules and consumers;
- configuration scope;
- topology/QoR or other observable consequences where evidence supports them;
- related implementations;
- dependency and blast-radius relationships.

### Layer 3: resolution intelligence

Carry the validated understanding into engineering action:

- likely remediation boundary;
- dependent artifacts affected by a proposed change;
- blast radius;
- regression surfaces;
- validation requirements;
- grounded remediation plan.

SME evidence is an output across these layers, not the final value proposition.

## Why a pivot is reasonable

The reason to pivot is not that an individual experiment failed. It is the progression of evidence:

**Broad hypothesis → exploratory baseline and CoreStory integration → qualification rule refinement → customer end-to-end A/B → independent disagreement investigations → discovery-specific integration design → first discovery attempt exposes experimental confounds → confounds corrected → final controlled discovery test → 0 CoreStory-added candidates and 0 materially broadened discovery paths.**

The discovery hypothesis has been given multiple opportunities under progressively improved controls.

Continuing to tune the same hypothesis now has diminishing information value unless the conditions materially change.

The focused investigations, however, exposed work that continues after specialized discovery and mechanism proof. That creates a distinct hypothesis that can be tested without asking CoreStory to outperform a mature ND detector.

## What is not being concluded

This review does not conclude that CoreStory can never contribute to ND discovery, that the customer workflow is perfect, that all source-reviewed findings are runtime defects, that CoreStory has already proven application-aware defect intelligence, or that the proposed workflow will necessarily reduce cost.

It also does not treat missing upstream libraries as a universal CoreStory limitation. That was an application-scope limitation in the tested project.

## How to test the new hypothesis

Use a frozen set of validated or high-confidence ND candidates. Start both workflows from the same defect mechanism so discovery variability cannot change the denominator.

The comparison should ask how far each workflow can take an engineer toward a production-ready decision.

Measure:

### Technical depth

- production relevance established;
- runtime/configuration scope;
- affected callers and flows;
- propagation and neutralization;
- application impact;
- blast radius;
- remediation boundary;
- regression/validation plan;
- unresolved evidence.

### Engineering efficiency

- source searches;
- tool calls;
- files/chunks inspected;
- elapsed investigation effort;
- repeated context reconstruction;
- reliable token/compute measures where available.

### SME efficiency

- evidence completeness;
- additional evidence requested;
- time-to-SME-decision;
- agreement, disagreement, and insufficient-evidence outcomes.

The test should be able to disprove the hypothesis. If CoreStory does not improve technical depth, engineering efficiency, or SME decision support, preserve the result and move to a different use case.

## Economics hypothesis

The economics theory should also expand beyond token reduction during discovery:

> **A persistent application intelligence layer may reduce repeated application reconstruction across the defect lifecycle.**

Without persistent context, relationships may be reconstructed repeatedly during candidate qualification, SME review, impact analysis, remediation planning, and validation planning.

Potential economic value therefore includes model/tool efficiency, engineer investigation effort, SME review effort, and reuse of application understanding across repeated ND runs or related engineering work.

No precise token, time, or cost-saving claim should be made until the telemetry supports it.

## Broader fit

The same evidence suggests looking at workflows where application context is central from the beginning rather than attempting to duplicate a mature specialized detector.

Candidate areas include change impact and blast-radius analysis, cross-module dependency understanding, modernization planning, business-rule and behavior understanding, cross-system application tracing, and carrying a validated defect into impact analysis and remediation planning.

These are recommendations for where to test next, not claims established by the ND experiment.
