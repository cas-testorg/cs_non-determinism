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

## Application significance

The focused investigations show repeated cases where the important question is not merely whether a suspicious construct exists.

The disposition can depend on whether the code is in the production build, whether it is reachable, configuration and runtime gates, which callers preserve the behavior, which callers neutralize it, whether varying state propagates, whether it reaches an observable consequence, and whether load-bearing implementation evidence is missing.

msDrivers.cc:711 is a positive example. The suspicious helper becomes meaningful only for a small set of callers that preserve the scalar return behavior.

ccdcgSolver.cc shows useful elimination of a locally suspicious RNG construct when the varying-state requirement is not established.

msuiGetPowerTaps shows the required guardrail. Missing implementation evidence must produce UNRESOLVED, not an inferred mechanism.

**Interpretation:** application significance is a credible next hypothesis, but aggregate value has not yet been proven.

## Why a pivot is reasonable

The reason to pivot is not that an individual experiment failed. It is the progression of evidence:

**Broad hypothesis → exploratory baseline and CoreStory integration → qualification rule refinement → customer end-to-end A/B → independent disagreement investigations → discovery-specific integration design → first discovery attempt exposes experimental confounds → confounds corrected → final controlled discovery test → 0 CoreStory-added candidates and 0 materially broadened discovery paths.**

The discovery hypothesis has been given multiple opportunities under progressively improved controls.

Continuing to tune the same hypothesis now has diminishing information value unless the conditions materially change.

## What is not being concluded

This review does not conclude that CoreStory can never contribute to ND discovery, that the customer workflow is perfect, that all source-reviewed findings are runtime defects, that CoreStory has already proven an aggregate qualification advantage, or that application qualification will necessarily reduce cost.

It also does not treat missing upstream libraries as a universal CoreStory limitation. That was an application-scope limitation in the tested project.

## Next hypothesis: application significance

A cleaner division of labor to test is:

**Synopsys specialized ND discovery → frozen candidate → application significance (build, reachability, runtime/configuration, callers, propagation, neutralization, observable consequence, missing evidence) → SME evidence → SME decision**

The experimental question is:

> Given the same candidate, can CoreStory help resolve application significance, reduce uncertainty, and produce better evidence for SME review?

This should be tested on a frozen candidate set so discovery variability cannot change the denominator.

## Economics hypothesis

Technical efficacy and economics should be measured separately.

The theory is:

> A persistent application intelligence layer may reduce repeated context reconstruction by allowing models and engineers to retrieve targeted application relationships instead of repeatedly searching and reconstructing them from source.

Potential measures include source searches, tool calls, files/chunks inspected, elapsed investigation time, reliable token/compute measures where available, unresolved evidence requests, SME requests for additional context, time-to-SME-decision, and SME agreement/disagreement/insufficient-evidence rates.

No precise token or cost-saving claim should be made until the telemetry supports it.

## Broader fit

The same evidence suggests looking at workflows where application context is central from the beginning rather than attempting to duplicate a mature specialized detector.

Candidate areas include change impact and blast-radius analysis, cross-module dependency understanding, modernization planning, business-rule and behavior understanding, cross-system application tracing, and carrying a validated defect into impact analysis and remediation planning.

These are recommendations for where to test next, not claims established by the ND experiment.
