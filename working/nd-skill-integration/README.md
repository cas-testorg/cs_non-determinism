# ND Skill + CoreStory Rule Integration Tests

This working area contains repeatable tests for evaluating the customer's nondeterminism methodology together with the CoreStory code-analysis rule.

The completed work is **workflow validation**, not the customer ground-truth benchmark.

## Inputs under test

### Customer workflow

The customer clarified that CTS analysis begins with broad ND pattern discovery and then verifies reported candidates with `prove-nd-mt` through an isolated agent workflow.

Customer material preserved under `working/nd-skill-integration/skills/` includes:

```text
nd-code-analyzer/SKILL.md
prove-nd/SKILL.md
non-determinism/SKILL.md        # prove-nd-mt
references/nd-patterns.yaml
references/nd-patterns.md
```

The ND pattern catalog provides the customer defect hypotheses. `nd-code-analyzer` applies discovery/triage logic. The base `prove-nd` skill performs proof/dismissal work, while `prove-nd-mt` adds concurrency-specific reachability, race-vs-ordering, gate, reset, and canonicalization reasoning.

The customer's production workflow also uses a Linux `create-cli-agent` process built around `cursor-agent` to launch verification in a clean context with a specified model.

### CoreStory rule

`archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc`

The rule directs the agent to use CoreStory application intelligence to trace application relationships, inspect targeted source, establish causal evidence, investigate controls/neutralizers, and avoid elevating unsupported candidates.

CoreStory is additive to the customer ND methodology. It does not replace the customer's pattern knowledge.

## Completed test sequence

```text
TC-001  Race-free floating-point accumulation / reduction      PASS
TC-002  Worker-state carryover / boundary reset                PASS
TC-003  Commit-order dependence / first-writer-wins            PASS
TC-004  Gate-inactive / determinism-control propagation        PASS
TC-005  Concurrent container / iteration-order dependence      PASS
TC-006  Customer pattern discovery + isolated verification     PASS
```

## What the tests established

### TC-001 through TC-005 — mechanism-specific verification

These tests exercised five different MT nondeterminism mechanisms with the customer `prove-nd-mt` reasoning and CoreStory-assisted application analysis.

Across all five tests, the workflow consistently required:

- actual MT reachability,
- a concrete source of run-to-run variability,
- downstream observable impact,
- control/gate analysis,
- neutralizer/canonicalization/reset analysis,
- explicit missing evidence rather than speculative elevation.

No test manufactured a Real finding when the evidence did not close the causal chain.

TC-003 and TC-004 showed particularly strong CoreStory narrowing, with concrete cross-file causal/control paths followed by targeted local validation. TC-005 required a late broad-search fallback after CoreStory could not close an end-to-end order-sensitive path.

### TC-006 — customer-pattern discovery + clean verification

TC-006 expanded beyond preselected mechanisms and used the customer's ND Pattern Catalog as the discovery knowledge base.

The test was executed as a **controlled workflow emulation** because the exact Linux `create-cli-agent` / `cursor-agent` infrastructure and requested model combination were not reproduced.

#### Discovery

A fresh Cursor conversation used the customer ND catalog plus CoreStory application intelligence to discover and triage CTS MT/concurrency candidates.

The original scanner implementation was unavailable, so the mechanical stage was emulated from the catalog patterns using local search. This was recorded as a workflow-fidelity deviation.

Discovery produced **10 candidates** with a structured handoff artifact containing pattern mechanism, location, MT evidence, shared state, downstream evidence, controls/neutralizers, missing evidence, and CoreStory relationships for verification.

#### Isolated verification

A second clean Cursor conversation received only the discovery artifact and used `prove-nd`, `prove-nd-mt`, the CoreStory rule, and targeted local source validation.

Final classification:

```text
Real:            0
Neutralized:     1
Latent-only:     6
False positive:  1
Dead/unused:     2
```

Examples of qualification included:

- suspicious lazy mutable state dismissed as MT-unreachable when worker reachability could not be established,
- actual MT paths retained as Latent-only when concurrent behavior was race-free/idempotent or lacked divergent observable consequence,
- concurrent insertion order classified Neutralized when a downstream deterministic set/canonicalization discarded that order,
- schedule-only `hardware_concurrency` behavior classified False positive when indexed outputs were independent.

TC-006 therefore demonstrated the complete logical workflow:

```text
customer ND pattern knowledge
    -> broad discovery
    -> CoreStory-assisted application qualification
    -> concrete candidate artifact
    -> isolated prove-nd / prove-nd-mt verification
    -> evidence-backed classifications
```

## Current conclusion

The workflow-validation stage is complete for the current scope.

The evidence supports the following bounded conclusion:

> The customer ND pattern catalog can drive broad candidate discovery, CoreStory can add application-level context during candidate qualification, and an isolated `prove-nd-mt` verifier can reduce those candidates into evidence-backed classifications without promoting unsupported findings to Real.

This conclusion is about **workflow compatibility and evidence discipline**. It is not a claim of defect recall, precision, or coverage against customer ground truth.

## Relationship to customer benchmark

The next phase is the customer ground-truth comparison using the Coverity findings Scott is expected to provide, including:

- `POINTER_NONDETERMINISM`
- `UNINIT`
- `UNINIT_CTOR`

Those findings should remain controlled/hidden from the initial discovery run and then be used to evaluate:

- recall against known findings,
- false-positive behavior,
- candidate qualification quality,
- additional supported findings not present in the supplied ground truth.

The customer has also clarified that their methodology is primarily static code scanning followed by analysis of whether a reported issue represents real ND risk. Runtime reproduction is often difficult and is not required for every finding.

## Stop condition

**Do not create additional synthetic ND tests at this time.**

TC-001 through TC-005 provide mechanism-specific verification evidence and TC-006 provides broad discovery-to-verification workflow evidence. Additional synthetic testing is unlikely to add enough value before the customer benchmark.

Resume test design when the Coverity findings are available or if customer feedback identifies a specific untested workflow gap.

## Per-test evidence

Each test directory contains its procedure and results. TC-006 additionally preserves separate discovery and verification artifacts/transcripts so the clean-context boundary can be reviewed.

Token metering is outside the scope of these completed workflow-validation tests.