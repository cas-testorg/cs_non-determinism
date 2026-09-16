# Synopsys SME Review Guide

## Purpose

The exploratory findings in this package are intended to be reviewed by engineers with CTS and non-determinism expertise.

The goal is not simply to accept or reject an AI-generated label. The review should determine **which part of the evidence chain is correct, incorrect, or incomplete** so the integrated workflow can be improved.

## Recommended Review Outcome

For each finding or experimental disposition, record one of:

```text
AGREE
DISAGREE
INSUFFICIENT EVIDENCE
```

When possible, also identify the qualification stage responsible for the disagreement.

## Evidence Chain to Review

### 1. Source / Mechanism

- Is the cited source construct accurate?
- Is the proposed ND mechanism technically credible?
- Are the relevant data structures, ordering semantics, concurrency behavior, or entropy sources characterized correctly?

### 2. Build Inclusion

- Is the cited implementation included in the relevant production build?
- Is the analysis looking at the implementation that actually ships/runs?
- Are there alternate implementations or build variants that change the conclusion?

### 3. Production Reachability

- Is the function/path reachable from relevant production behavior?
- Are identified callers complete and correct?
- Is apparently dead/unused code actually invoked through mechanisms the static investigation did not identify?

### 4. Runtime / Configuration Gates

- Are required feature flags, modes, thread configurations, platform conditions, or runtime options represented correctly?
- Does the proposed disposition apply to all relevant configurations or only a subset?

### 5. Propagation

- If nondeterministic behavior occurs locally, can it influence downstream state or processing?
- Is the reported propagation path complete?
- Does the value/order/state become significant before it is normalized?

### 6. Neutralization / Canonicalization

- Is there a deterministic comparator, sort, reduction, synchronization point, canonicalization step, or other neutralizer?
- Does it occur before the behavior becomes observable?
- Does it fully neutralize the suspected mechanism or only part of it?

### 7. Observable Consequence

- Can the behavior affect an equivalent-run application/QoR result?
- Is the claimed observable boundary the right one for CTS?
- Is the issue instead configuration sensitivity, platform sensitivity, latent behavior, or another non-production-defect category?

## Suggested Finding Review Template

```markdown
### SME determination

**Finding / candidate:** <ID or source location>

**Overall:** AGREE | DISAGREE | INSUFFICIENT EVIDENCE

**Mechanism:** Correct | Incorrect | Incomplete
**Build inclusion:** Correct | Incorrect | Incomplete | N/A
**Production reachability:** Correct | Incorrect | Incomplete | N/A
**Runtime/configuration:** Correct | Incorrect | Incomplete | N/A
**Propagation:** Correct | Incorrect | Incomplete | N/A
**Neutralization:** Correct | Incorrect | Incomplete | N/A
**Observable consequence:** Correct | Incorrect | Incomplete | N/A

**Final SME disposition:**
<REAL / FALSE POSITIVE / DEAD-UNUSED / NEUTRALIZED / etc.>

**Notes / missing evidence:**
<free text>
```

## Why Stage-Level Feedback Matters

A disagreement can mean several different things:

```text
Wrong ND mechanism
        -> improve Synopsys defect analysis / skill behavior

Wrong build/reachability/propagation conclusion
        -> improve CoreStory application qualification

Correct evidence but poor coordination between stages
        -> improve workflow/routing/orchestration

Insufficient evidence presented to reviewer
        -> improve finding/report output
```

Capturing the reason is therefore more valuable than recording only whether the final label was right or wrong.

## Priority Findings

For the exploratory package, the highest-value review target is the set of findings whose disposition changed after application qualification, especially the `ctoFlowClone.cc` pointer-ordering example.

These examples directly test the evaluation's central hypothesis: whether application intelligence helps distinguish a credible local ND mechanism from a defect that actually matters in the built application.

## Relationship to TC-002

The same review approach can be applied to findings from the customer-controlled A/B. For candidates found by only one arm or classified differently between arms, preserve both evidence chains and have the SME judge the underlying technical evidence rather than selecting a preferred tool output.

This makes the SME determination usable both as accuracy evidence and as input to the next iteration of the integrated workflow.
