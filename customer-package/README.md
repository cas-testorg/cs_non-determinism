# Synopsys + CoreStory Non-Determinism Evaluation — Findings Package

## Purpose

This directory contains the customer-reviewable evidence from the exploratory CoreStory non-determinism evaluation against Fusion Compiler CTS.

The package is designed to support technical and SME review. It preserves finding-specific implementation evidence where that evidence is useful for validating accuracy, while excluding identity, authentication, infrastructure, and unrelated debugging details.

## Sanitization Standard

**Preserve evidence. Preserve enough implementation context to reproduce and validate findings. Remove identity/infrastructure details and irrelevant experimental plumbing. Retain limitations.**

Accordingly, this package may retain:

- CTS file, class, and function names relevant to a finding;
- small source excerpts needed to understand the suspected mechanism;
- finding severity and experimental disposition;
- build, reachability, runtime, propagation, neutralization, and observability evidence;
- test prompts and controls needed to understand the experiment;
- experimental limitations that affect interpretation.

This package excludes or generalizes:

- usernames and user-specific local paths;
- credentials, tokens, authentication headers, and session identifiers;
- internal hostnames, organization identifiers, and infrastructure details that do not affect the finding;
- raw agent transcripts and request traces unless specifically needed as evidence;
- unrelated environment/debugging details;
- internal future-work experiments that were not part of the presented evaluation.

## Evidence Boundary

The exploratory CoreStory tests are **directional evidence**, not the authoritative customer A/B benchmark. They were useful for understanding candidate discovery, application-context qualification, and the controls required for a more rigorous comparison.

The customer-controlled A/B evaluation is tracked separately. Its detailed results will not be incorporated here until the customer completes internal review and provides the underlying evidence.

## Test Cases

- **TC-001A — Baseline Control:** exploratory nondeterminism analysis without CoreStory.
- **TC-001B — CoreStory-Assisted Analysis:** matching exploratory analysis with CoreStory application context; strongest signal was candidate qualification.
- **TC-001C — CoreStory v3 Rule Check:** qualitative follow-up evaluating a stricter application-qualification workflow.
- **TC-002 — Customer-Controlled A/B:** customer-owned comparison; results pending customer review.

## SME Review

Finding-specific records are intended to support SME validation. Where applicable, each record distinguishes the experiment's conclusion from the SME's eventual determination.

An experimental disposition should therefore be read as a hypothesis supported by the captured evidence, not as a replacement for product-owner or SME validation.
