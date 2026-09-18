# Internal Review: CoreStory + Synopsys Non-Determinism Evaluation

## Purpose

This package consolidates the evidence gathered during the CoreStory non-determinism evaluation against the Synopsys CTS workflow.

It is intentionally evidence-heavy. The goal is not to argue from opinion. The goal is to document what was tried, what changed between iterations, what the tests actually produced, what remains unresolved, and what the evidence suggests should be tested next.

The package is written for both technical and leadership review. The opening summary is intended to make the progression understandable without requiring every raw artifact. The technical sections provide enough detail to challenge the interpretation and trace important claims back to the underlying evidence.

## Central question

The evaluation began with a broad question:

> Can CoreStory add differentiated value to an existing AI-assisted non-determinism workflow?

As the evaluation progressed, that question separated into three more specific hypotheses:

1. **Discovery expansion:** Can CoreStory materially improve broad ND candidate discovery beyond the existing Synopsys workflow?
2. **Application-aware defect intelligence:** Given a specialized defect or high-confidence candidate, can CoreStory accelerate the path to an actionable engineering decision by establishing production relevance, application impact, remediation scope, and validation requirements?
3. **Economics:** Can persistent application intelligence reduce repeated context reconstruction, model/tool effort, or SME and engineering effort across that defect lifecycle?

The current evidence is strongest for the first question. In the final controlled discovery run, the actual customer scanner and reference set produced 3,673 raw candidates across 27 patterns and 588 files. The customer workflow retained 334 candidates. CoreStory added 0 candidates and materially broadened 0 discovery paths.

That result does not establish that CoreStory can never contribute to ND discovery. It does show that differentiated discovery value was not demonstrated in the tested configuration after correcting known experimental confounds.

The second hypothesis is broader than producing a better evidence packet for an SME. SME decision support is one potential benefit. The larger question is whether CoreStory can carry a specialized finding forward through production relevance, impact understanding, engineering scope, and validation planning.

The second and third hypotheses remain worth measuring.

## Package contents

- [01 Executive Summary](01-executive-summary.md)
- [02 Synopsys Current Process](02-synopsys-current-process.md)
- [03 Experimental Progression](03-experimental-progression.md)
- [04 Customer A/B Test 1](04-customer-ab-test-1.md)
- [05 Final Controlled Discovery Test](05-final-controlled-discovery-test.md)
- [06 Evidence Synthesis and Pivot Rationale](06-evidence-synthesis-and-pivot-rationale.md)
- [07 Recommendations Draft](07-recommendations-draft.md)
- [Evidence Index](EVIDENCE/evidence-index.md)

## Reading guidance

The recommendations section is deliberately written in first person and as a starting point. The factual sections should remain evidence-oriented. The recommendation language is intended to be edited into the presenter's own voice.

## Claim boundaries

This package distinguishes source review, automated disposition, runtime reproduction, SME determination, and experimental inference. It does not treat source-reviewed findings as runtime-confirmed defects. It does not claim a measured token or cost reduction where reliable telemetry is unavailable. It does not attribute an outcome specifically to CoreStory MCP unless the available evidence supports that attribution.

The application-aware defect intelligence hypothesis is a proposed next test, not a benefit established by the current ND experiments.
