# ND Code Analyzer — Evaluation Snapshot

**Owner:** Synopsys  
**Source skill name:** `nd-code-analyzer`  
**Source version identified by skill:** 1.4.0  
**Source blob:** `95204ad9767a0e155a4aad45a883f05d1af6e7b0`

> This customer-package copy preserves the operative instructions relevant to the evaluation. Internal absolute tool paths, supporting references, extended pattern catalogs, ownership tooling details, and historical case-study material are not reproduced here. Those supporting references were part of the installed workflow where available.

## Objective

Find static source-code-level non-determinism candidates in C++ modules and produce a structured report with severity classification and context-specific remediation guidance.

**Real ND is not a regex hit.** A finding is real only after tracing the suspect source to downstream C++ code that can observe nondeterministic behavior: a mutating sink, tie-break decision, output/report order, message order, persisted state, QoR-affecting algorithm choice, or floating aggregation result.

If downstream proof is missing, use a non-real classification such as latent-only, false-positive, dead/unused, safe-adopter, mirror-duplicate, or neutralized.

## Workflow

```text
Stage 1 — Mechanical scan / candidate generation
        |
        v
Stage 2 — LLM triage + realness classification
        |
        v
Stage 3 — Tier-2 deep read / semantic analysis
        |
        v
Stage 3b — Downstream observability proof
        |
        v
Stage 3c — Performance-aware fix direction
        |
        v
Stage 4 — Assemble findings
        |
        v
Stage 5 — Render report
```

## Stage 2 Realness Classification

For each candidate, inspect surrounding source, resolve the actual type/construct, and classify before assigning severity.

- **real** — downstream C++ can observe nondeterministic behavior.
- **latent-only** — suspect construct exists but consumers are lookup-only, membership-only, or otherwise order-insensitive.
- **false-positive** — type resolution shows a different construct, stable comparator, inactive code, or pattern mismatch.
- **safe-adopter** — code already uses a deterministic project comparator/container idiom.
- **mirror-duplicate** — include/export/module mirror of another issue.
- **neutralized** — nondeterministic order is canonicalized before consumption.
- **dead/unused** — code is not compiled or has no reachable caller.

Severity is assigned only to real findings:

- **HIGH** — hot path or directly affects QoR/database state.
- **MEDIUM** — real but gated, uncommon, or partially mitigated.
- **LOW** — real but debug/report-only or difficult to trigger.

## Parallel Triage Rule

The source skill explicitly instructs the agent to dispatch parallel `explore` subagents when **either**:

- candidate count is at least 50 candidate files, or
- the module spans at least five subdirectories.

Each subagent triages a subdirectory or category and returns structured results for the parent agent to merge.

For smaller modules, the skill instructs a single-agent triage loop.

**Evaluation implication:** child/subagent creation during repository-scale `nd-code-analyzer` discovery is consistent with the skill design and should not by itself be treated as orchestration non-compliance.

## Deep-Read Requirements

Tier-2 candidates require data-flow reasoning beyond pattern matching. The investigation should determine whether the candidate affects output or another observable result and should drop candidates that do not survive semantic inspection.

For unordered/container-order candidates, the workflow requires resolving the actual iterated type before classification and checking whether the consumer is order-sensitive.

## Neutralizer Detection

Candidates should be dismissed or downgraded when deterministic behavior is restored before an observable consumer. Examples include:

- stable/deterministic comparator;
- deterministic sort or stable sort;
- canonicalization after collection;
- membership-only or lookup-only use;
- deterministic merge/reduction behavior;
- project-specific deterministic container idioms.

The existence of a suspicious declaration alone is insufficient.

## Semantic Review Themes

The installed skill includes broader semantic review guidance covering areas such as:

- post-collection canonicalization;
- project wrapper containers;
- graph/geometry traversal and tie-breaking;
- stale cached state;
- cross-scene/state reuse;
- concurrency and write-lock discipline;
- deterministic control-path normalization;
- checksum/ND observability;
- static multi-threaded ND source shapes.

Supporting pattern references are acknowledged but excluded from this package.

## Downstream Observability Requirement

Before promotion, trace the candidate to a concrete downstream consumer. Examples include:

- database/design mutation;
- order-sensitive algorithm choice;
- tie-break behavior;
- persistent or externally visible output;
- QoR-affecting calculation;
- non-associative floating-point aggregation.

A suspicious source pattern without an observable downstream consequence should not be promoted as a real HIGH/MEDIUM defect.

## Relationship to `prove-nd`

`nd-code-analyzer` performs broad discovery, triage, and deep-read analysis. Candidates requiring deeper proof can be evaluated under the `prove-nd` workflow.

The two skills have intentionally different orchestration rules: this repository-scale analyzer permits parallel exploration at defined thresholds, while `prove-nd` prohibits subagents during proof.
