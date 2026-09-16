# TC-002 — Synopsys-Controlled A/B Evaluation

## Status

**Customer-controlled A/B executed. Results are undergoing Synopsys internal/SME review.**

Detailed finding counts, cost/token observations, and outcome conclusions are intentionally not included in this package yet. They will be incorporated only after the reviewed underlying evidence is available.

## Purpose

Establish a customer-owned comparison of the existing Synopsys non-determinism workflow and the same workflow augmented with CoreStory application intelligence.

The purpose is not to replace Synopsys skills or defect-analysis methods. The comparison is intended to measure the incremental contribution of CoreStory while preserving the existing workflow.

## Core Comparison

### Arm A — Existing Synopsys Workflow

```text
Same CTS source
    -> Synopsys ND skills
    -> existing AI-assisted workflow
    -> findings / evidence

CoreStory MCP: Disabled
CoreStory governing rule: Disabled
```

### Arm B — Existing Workflow + CoreStory

```text
Same CTS source
    -> same Synopsys ND skills
    -> same AI-assisted workflow
       + CoreStory application intelligence
       + v3 qualification rule
    -> findings / evidence

CoreStory MCP: Enabled
CoreStory governing rule: Enabled
```

The intended experimental variable is the addition of **CoreStory MCP + the v3 governing qualification rule**.

## Controls

The test design calls for the two arms to preserve, as closely as practical:

- the same CTS source/revision;
- the same analysis prompt;
- the same Synopsys skill package;
- the same model/model configuration;
- the same execution workflow;
- clean analysis state;
- held-out TSan/Coverity ground truth;
- comparable telemetry and measurement.

Actual execution behavior and model/subagent topology must also be reviewed before quantitative differences are attributed to CoreStory.

## Qualification Model

The CoreStory arm is intended to add application-context evidence around:

```text
candidate
  -> build inclusion
  -> production reachability
  -> runtime/configuration gate
  -> defect mechanism
  -> propagation
  -> deterministic neutralizer / canonicalization
  -> observable consequence
  -> final proof / SME validation
```

Synopsys skills remain responsible for ND-specific mechanism analysis; CoreStory is intended to complement that analysis with application context.

## Measurements

The A/B evaluation is intended to compare:

- known-defect reproduction;
- quality/depth of additional findings;
- false-positive and reviewer burden;
- candidate disposition and supporting evidence;
- investigation effort and time;
- local repository search/read activity where available;
- CoreStory application-context retrieval;
- runtime and compute/token usage where attribution is reliable;
- SME effort required to validate results.

## Ground Truth

Known TSan/Coverity reference findings are held out during the measured discovery/qualification runs and are intended to be applied after both arms are preserved.

This prevents known defect locations from steering candidate discovery or qualification.

## SME Review

The customer review is an essential part of TC-002. Differences between Arm A and Arm B should be evaluated finding-by-finding, particularly when:

- only one arm reports a candidate;
- both arms report the candidate but classify it differently;
- CoreStory changes the disposition based on build/reachability/neutralization evidence;
- an arm appears to miss a known defect;
- the two arms reach similar conclusions through materially different investigation paths.

For each difference, the useful question is not simply **which arm produced the finding**, but:

> **Which evidence chain is technically correct, and why?**

See `METHODOLOGY/SME-review-guide.md` for the recommended review framework.

## Current Result Boundary

At this stage, this package does not claim a TC-002 winner or a quantitative improvement.

The A/B execution has produced preliminary observations, but the Synopsys team is reviewing the findings internally and with SME expertise. The reviewed evidence is needed before drawing conclusions about accuracy, missed findings, false positives, token/compute economics, or overall workflow improvement.

Once that evidence is available, this test case can be extended with:

```text
results/
  finding-comparison.md
  sme-validation.md
  execution-comparison.md
  conclusions.md
```

## Relationship to the Exploratory Tests

TC-002 is the culmination of the earlier exploratory work:

- **TC-001A** established the baseline candidate-filtering problem.
- **TC-001B** showed that application context can change candidate disposition.
- **TC-001C** refined those lessons into an evidence-gated qualification model.
- **TC-002** places that model into a customer-controlled comparison with SME validation.

The exploratory tests should therefore be read as inputs to the TC-002 methodology, not substitutes for its results.

## Next Step

After Synopsys completes its review and the underlying A/B artifacts are available, CoreStory and Synopsys can jointly map the results across:

```text
candidate
  -> discovery path
  -> qualification evidence
  -> CoreStory usage, if applicable
  -> execution/model topology
  -> final SME determination
```

That analysis will identify both where CoreStory added value and where the integrated workflow should be refined for the next iteration.
