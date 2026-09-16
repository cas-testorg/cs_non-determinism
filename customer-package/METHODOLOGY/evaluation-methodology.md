# Evaluation Methodology

## Objective

Evaluate whether CoreStory application intelligence can improve Synopsys's existing AI-assisted non-determinism workflow without replacing Synopsys defect expertise, analysis skills, or engineering validation.

The evaluation evolved around a key distinction:

> **Finding a suspicious source pattern is not equivalent to proving an application defect.**

A useful investigation must progressively establish both the non-determinism mechanism and its relevance to the built application.

## Evaluation Model

The integrated workflow separates four related activities:

```text
Candidate Discovery
        |
        v
ND Mechanism Analysis
        |
        v
Application Qualification
        |
        v
Defect Proof / SME Validation
        |
        v
Engineering Finding
```

### 1. Candidate Discovery

Identify code constructs that may represent nondeterministic behavior: unstable ordering, concurrency hazards, entropy sources, incomplete tie-breaking, order-sensitive iteration, or related mechanisms.

A candidate is a reason to investigate. It is not yet a confirmed defect.

### 2. ND Mechanism Analysis

Establish whether the local code can exhibit the suspected nondeterministic mechanism and under what conditions. Synopsys's existing skills and engineering expertise remain central to this stage.

### 3. Application Qualification

Determine whether the mechanism matters in the application that is actually built and run. The qualification sequence used by the refined CoreStory workflow is:

```text
candidate
  -> build inclusion
  -> production reachability
  -> runtime/configuration gate
  -> defect mechanism
  -> propagation
  -> deterministic neutralizer / canonicalization check
  -> observable consequence
  -> REAL only if supported
```

CoreStory's intended contribution is application intelligence supporting these relationships and conditions; targeted source inspection remains important for establishing the local code mechanism.

### 4. Defect Proof / SME Validation

Synopsys engineering/SME review determines whether the evidence supports the final defect classification and severity. Experimental AI dispositions are hypotheses to validate, not substitutes for SME judgment.

## Evaluation Progression

The exploratory tests intentionally evolved as evidence was gathered:

```text
TC-001A — Baseline Discovery
        |
        | established candidate-filtering problem
        v
TC-001B — CoreStory-Assisted Qualification
        |
        | showed application context can change candidate disposition
        v
TC-001C — Qualification Rule Refinement
        |
        | made qualification evidence systematic
        v
TC-002 — Synopsys-Controlled A/B
        |
        | customer-owned measurement + SME validation
        v
Integrated Workflow Refinement
```

The exploratory tests were used to improve the experimental design rather than being treated as final quantitative benchmarks.

## Ground Truth

Known TSan/Coverity reference findings are held out during candidate discovery and qualification. They are intended for scoring only after comparison arms are preserved, preventing known locations from steering the investigation.

## Controlled A/B Principle

For the authoritative comparison, the goal is to hold the source, task, Synopsys skills, model, workflow, and execution environment as constant as practical.

**Arm A:** existing Synopsys workflow without CoreStory.  
**Arm B:** same workflow with CoreStory application intelligence and the governing qualification rule.

The intended experimental variable is therefore CoreStory's application-context contribution.

## Measurements

The controlled evaluation is intended to examine:

- reproduction of known defects;
- quality and credibility of additional findings;
- false-positive and SME-review burden;
- investigation time and effort;
- coverage/completeness;
- compute/token usage where attribution is reliable;
- differences in source exploration and application-context retrieval.

Finding counts alone are not sufficient. For findings that differ between arms, the evaluation should capture **why** the disposition changed.

## Evidence Standard

A promoted finding should make its evidence chain inspectable. Depending on the candidate, this may include source code, file/function names, build evidence, callers, runtime/configuration conditions, downstream relationships, neutralizers, and observable consequences.

The package intentionally preserves such implementation details when they are needed for SME validation.

## Experimental Integrity

When model attribution, orchestration, prior analysis state, required workflow assets, or telemetry cannot be controlled, the limitation is recorded rather than converted into a precise quantitative claim.

The guiding principle is:

> **Produce results that can be understood, challenged, and reproduced — not simply the most favorable number.**
