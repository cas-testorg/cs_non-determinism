# TC-006 — Customer CTS ND Discovery + Verification Workflow

## Purpose

Evaluate the customer-described CTS nondeterminism workflow end to end without requiring an exact reproduction of the customer's Linux orchestration infrastructure.

The customer workflow is logically:

```text
top-level request
    -> nd-code-analyzer discovery
    -> candidate/result artifact
    -> create-cli-agent
         -> clean verifier context
         -> prove-nd / prove-nd-mt
         -> specified verification model
         -> clean verification result
    -> final result
```

TC-001 through TC-005 primarily exercised the verification/proof side using preselected MT mechanisms. TC-006 shifts the test boundary to broad discovery -> isolated verification -> final findings.

This remains workflow validation. It is not yet the Coverity ground-truth benchmark because the customer Coverity findings have not yet been provided.

## Customer-provided workflow

Representative customer prompt:

```text
using /u/ranjithp/.claude/skills/nd-code-analyzer/SKILL.md, find out possible non determinism issues from CTS module located here : <path>

Specifically do a scan for finding out ND issues from multi-threaded code.

Verify if the reported issues are real with /prove-nd-mt using a /create-cli-agent with GPT-5.5-xtra-high
```

Customer model guidance:

- discovery: Opus 4.8 xhigh or Opus 5 high
- verification: GPT-5.5-xtra-high via `/create-cli-agent`

The known customer skills are preserved under:

```text
working/nd-skill-integration/skills/
├── nd-code-analyzer/
├── prove-nd/
└── non-determinism/   # prove-nd-mt
```

## Important orchestration constraint

`create-cli-agent` is a customer-specific Linux process that depends on `cursor-agent`. It accepts a prompt and model, runs the verification in a clean agent context, and writes a clean result document.

The current test environment may not reproduce that wrapper, `cursor-agent`, or the exact customer model combination.

Therefore TC-006 is defined as a **controlled workflow emulation**, not an infrastructure-equivalence test.

The experimental property that must be preserved is **verification-context isolation**. If `create-cli-agent` cannot be used, emulate it manually by starting a new clean Cursor conversation for the verification phase and passing only the candidate artifact/context that the discovery phase produced.

Record every orchestration/model substitution. Do not describe the run as an exact reproduction of the customer's production workflow unless the original wrapper and requested models are actually used.

## Customer skill behavior that must be preserved

### nd-code-analyzer

The discovery skill has its own required workflow, including:

- Stage 1 mechanical scan using its scanner/pattern catalog,
- Stage 2 LLM triage,
- Stage 3 Tier-2 deep read,
- downstream-observability proof,
- neutralizer detection,
- real/non-real classification,
- optional parallel triage when its thresholds are met.

**Do not replace or suppress the skill's mandated mechanical scan merely to force a CoreStory-first pattern.**

CoreStory should augment the customer's discovery workflow where application intelligence is useful: reachability, cross-file relationships, callers/callees, shared state, downstream consumers, controls, neutralizers, and candidate qualification.

### prove-nd / prove-nd-mt

The base `prove-nd` skill and the MT extension require proof of downstream observability before a finding is Real. `prove-nd-mt` adds MT reachability, race-vs-ordering reasoning, gate audits, reset/canonicalization checks, and MT-specific neutralizers.

The base skill explicitly prohibits sub-agents during verification. The customer's `create-cli-agent` wrapper is treated as the outer orchestration mechanism that launches a clean verifier; the verifier itself should not recursively spawn additional sub-agents.

## Required inputs / pre-run gate

Record each item before execution:

```text
CTS source path known:                                YES / NO
CTS source revision known:                            YES / NO
CoreStory project corresponding to CTS source known:  YES / NO
nd-code-analyzer skill available:                     YES / NO
prove-nd skill available:                             YES / NO
prove-nd-mt skill available:                          YES / NO
nd-code-analyzer scripts/references available:        YES / NO
/create-cli-agent available:                          YES / NO
cursor-agent available:                               YES / NO
requested discovery model available:                  YES / NO
GPT-5.5-xtra-high verification model available:       YES / NO
CoreStory rule installed/active:                      YES / NO
CoreStory MCP available:                              YES / NO
```

### Pre-run decision

If the three customer skills or required `nd-code-analyzer` scanner assets are missing, do not run TC-006 as a customer-workflow test.

If `create-cli-agent`, `cursor-agent`, or the requested models are unavailable, TC-006 may proceed as a documented workflow emulation using the two-phase procedure below.

## Two-phase execution model

### TC-006A — Discovery

Goal: reproduce the customer discovery behavior without preselecting a specific ND mechanism.

1. Preserve prior Cursor sessions/artifacts.
2. Start a fresh Cursor chat.
3. Record Cursor version and discovery model actually used.
4. Confirm `nd-code-analyzer` and its scanner assets are available.
5. Confirm the CoreStory rule and MCP are active.
6. Use the discovery prompt below.
7. Allow `nd-code-analyzer` to perform its mandated mechanical scan.
8. Do not provide TC-001 through TC-005 candidate locations/findings.
9. Do not provide Coverity findings or hidden ground truth.
10. Preserve the discovery output/candidate artifact exactly as produced.
11. Do not manually improve, curate, or reorder candidates before verification unless the customer workflow itself requires that behavior.

#### Discovery prompt

Replace only `<CTS_PATH>`.

```text
Using /u/ranjithp/.claude/skills/nd-code-analyzer/SKILL.md, find possible nondeterminism issues from the CTS module located here: <CTS_PATH>

Specifically, scan for nondeterminism issues in multi-threaded code.

Follow the CoreStory code-analysis rule while performing the customer's nd-code-analyzer workflow.

Produce the candidate/result artifact that should be handed to the verification step. Do not verify the candidates yet.
```

The explicit phase separation is an experimental adaptation needed to emulate `create-cli-agent` cleanly. It does not change the discovery objective.

### TC-006B — Verification

Goal: emulate the isolated verification that the customer's `create-cli-agent` process provides.

1. Start a **new clean Cursor conversation**.
2. Record the verification model actually used.
3. Make `prove-nd` and `prove-nd-mt` available.
4. Keep the CoreStory rule and MCP active.
5. Provide only the discovery candidate/result artifact and minimal instruction needed to verify it.
6. Do not expose the TC-006A conversation history, prior synthetic-test findings, or hidden ground truth.
7. Do not manually add mechanism-specific hints that were absent from the discovery artifact.
8. Do not spawn additional verifier sub-agents if the skill prohibits them.
9. Preserve the complete verification transcript and clean final result.

#### Verification prompt

Attach or paste the unmodified candidate/result artifact from TC-006A, then use:

```text
Verify whether the reported multi-threaded nondeterminism candidates in the supplied discovery artifact are real.

Use the base prove-nd skill and the prove-nd-mt extension. Follow the CoreStory code-analysis rule throughout verification.

Preserve the customer skills' classification and proof requirements. Do not call a candidate Real without establishing the required MT reachability, variability mechanism, downstream observable consequence, and absence of a complete neutralizer. State missing evidence explicitly.
```

If GPT-5.5-xtra-high and `create-cli-agent` are available, use the customer's original verification mechanism instead and record that no emulation was required.

## What to capture

### Discovery phase

Record:

- whether `nd-code-analyzer` activated/read successfully,
- whether its scanner/pattern catalog executed as designed,
- candidate count before and after triage,
- pattern/categories searched,
- CoreStory interactions during triage/deep-read/observability analysis,
- local mechanical scan/search operations,
- any parallel triage/subagent behavior required by the discovery skill,
- candidates and evidence emitted for verification,
- whether CoreStory contributed application context beyond the mechanical pattern scan.

### Discovery -> verification handoff

For every candidate sent to verification, capture:

```text
Candidate ID/name:
Mechanism/category:
File/symbol/location:
Evidence passed from discovery:
Controls/neutralizers already identified:
Downstream evidence already identified:
Verifier model/agent actually used:
Handoff method: create-cli-agent / manual clean-context emulation
```

Determine whether the verifier can use the discovery artifact directly or must rediscover substantial application context.

### Verification phase

For each candidate, record:

- MT reachability,
- source of run-to-run variability,
- race vs race-free ordering distinction where relevant,
- shared/worker/ordering mechanism,
- downstream consumer / observable consequence,
- controls/gates,
- neutralizers/canonicalization/reset behavior,
- final classification,
- missing evidence,
- CoreStory interactions,
- targeted local source validation,
- duplicated discovery work.

## Primary evaluation questions

1. Does `nd-code-analyzer` generate useful MT ND candidates without us preselecting a mechanism?
2. Can its mandated mechanical scan coexist with the CoreStory rule without either workflow being distorted?
3. Where does CoreStory add value after mechanical discovery: triage, reachability, relationships, downstream observability, controls, or neutralizer analysis?
4. Does the discovery artifact contain enough context for an isolated verifier to continue without redoing most discovery work?
5. Does `prove-nd` / `prove-nd-mt` preserve its proof discipline in the isolated verification phase?
6. Are Real, Neutralized, Latent-only, Dead/unused, False-positive, and Unresolved classifications supported rather than inferred from syntax alone?
7. What investigation work is repeated between discovery and verification?
8. Does any observed difference appear caused by CoreStory integration versus by orchestration/model substitution?

## Pass criteria

Classify TC-006 **PASS** when the workflow can be executed meaningfully and:

- `nd-code-analyzer` performs its intended discovery workflow,
- its mechanical scan is preserved rather than replaced by CoreStory,
- CoreStory contributes useful application intelligence during discovery and/or verification,
- discovery produces a concrete artifact/candidate set for handoff,
- verification runs in an isolated clean context,
- `prove-nd` / `prove-nd-mt` proof discipline is preserved,
- downstream consequence and neutralizers are investigated before Real classification,
- unsupported findings are not promoted to Real,
- duplicated discovery/verification work is observable and recorded,
- all model/orchestration deviations are documented.

A Real ND finding is **not required** for workflow PASS.

## Partial / fail / inconclusive guidance

### PARTIAL

Examples:

- discovery runs correctly but CoreStory contributes little,
- isolated verification works but requires substantial rediscovery,
- important `prove-nd-mt` proof steps are skipped,
- model/tool substitutions materially affect behavior while still allowing useful evaluation,
- manual emulation requires intervention beyond clean handoff.

### FAIL

Examples:

- the customer's mechanical discovery workflow is suppressed or replaced,
- suspicious code patterns are promoted to Real without proof,
- CoreStory rule is ignored despite being available,
- verification is not isolated and relies on hidden discovery conversation context,
- known substitutions are hidden and the run is presented as an exact customer-environment reproduction.

### INCONCLUSIVE

Use when missing customer skill assets, scanner dependencies, CoreStory connectivity, or other tooling prevent a meaningful discovery/verification workflow.

## Relationship to the customer benchmarks

TC-006 validates workflow compatibility and handoff behavior. It does **not** establish recall or precision against Coverity.

When Scott provides the Coverity findings for `POINTER_NONDETERMINISM`, `UNINIT`, and `UNINIT_CTOR`, use those as ground truth in a separate benchmark phase rather than contaminating this workflow-validation run.

## Stop condition

Run TC-006A and TC-006B once, preserve the evidence, and review the combined result before defining additional synthetic tests.
