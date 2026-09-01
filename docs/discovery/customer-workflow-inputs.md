# Customer Workflow Inputs

> **Status:** Working discovery document. Capture customer-provided evidence here before converting assumptions into workflow design decisions.

## Purpose

The first ND workflow should be grounded in one real, previously diagnosed defect and the customer's actual engineering process. This document tracks the inputs needed to reconstruct that workflow and establish a credible baseline.

## P0 — Required to Design the First Workflow

### Known Defect / Test Case

- [ ] One known ND defect in the scoped CTS/presynthesis codebase
- [ ] Original observed symptom
- [ ] Source revision / configuration used for the failing case
- [ ] Confirmed root cause
- [ ] Final correction, if available

### Existing ND Workflow

- [ ] Walk through the known defect from detection to successful check-in
- [ ] Identify major decision and triage points
- [ ] Identify where engineers enter the workflow
- [ ] Identify where SMEs enter the workflow
- [ ] Identify what determines routing to a team or subsystem

### Existing Cursor Skills

- [ ] Obtain Synopsys ND-related Cursor skills/workflows
- [ ] Document when each skill is invoked
- [ ] Document required inputs and generated outputs
- [ ] Classify each as static scan, runtime diagnosis, pre-check, triage, or other

### Runtime Evidence

- [ ] Obtain checksum/runtime artifacts from the known defect
- [ ] Document artifact format and approximate size
- [ ] Document how the first divergence is identified
- [ ] Capture relevant metadata such as revision, configuration, thread count, seed, and platform where applicable

## P1 — Required to Prove / Measure Success

### Baseline Metrics

- [ ] Engineer time from detection to successful check-in
- [ ] SME validation / triage time
- [ ] Cursor token information where available
- [ ] Number of AI iterations / false leads where available

### Existing Tool Baseline

- [ ] What TSan found for the known case
- [ ] What Coverity found for the known case
- [ ] What current Cursor skills / internal tooling found
- [ ] Whether the defect was missed, partially localized, or correctly identified by each baseline tool

### Validation Criteria

- [ ] Define a confirmed ND defect
- [ ] Define a false positive
- [ ] Clarify latent/theoretical race versus observed runtime manifestation
- [ ] Define net-new finding for POV measurement

### Validation Ownership

- [ ] Identify the SME / owner responsible for validating each relevant defect class

## P1 — Environment and Test Boundaries

- [ ] Confirm exact CTS/presynthesis scope
- [ ] Confirm explicit out-of-scope components, including timing-engine boundary
- [ ] Establish revision/build-controlled baseline
- [ ] Confirm CoreStory MCP is operational from the same Cursor environment used for testing
- [ ] Determine whether the known defect can be reproduced in the POV environment or whether prior runtime evidence will be supplied
- [ ] Identify owners for ingestion, runtime execution, Cursor configuration, and SME validation

## P2 — Expansion Inputs

- [ ] How proactive/full-codebase ND scans are initiated
- [ ] TSan/Coverity/internal scan artifact formats
- [ ] Triage and prioritization process at scale
- [ ] Defect classes producing the greatest SME effort or false-positive burden
- [ ] Customer comfort boundaries for automated classification/dismissal
- [ ] Mandatory human approval points
- [ ] Check-in / pre-submit integration points

## First Working Session Target

The minimum useful package for the first workflow-design session is:

1. A known ND defect and confirmed root cause.
2. Runtime/checksum evidence used to diagnose it.
3. Existing Cursor skills/workflows used for ND investigation or pre-checking.
4. A walkthrough of detection -> diagnosis -> validation -> fix/check-in.

Baseline metrics are important for POV measurement but should not block initial workflow design if they require additional time to collect.
