# Non-Determinism Workflow — Conceptual Architecture

> **Status:** Draft / theoretical. Subject to validation against customer workflow artifacts, known defects, runtime evidence, and existing developer skills.

## Purpose

This document captures the proposed high-level architecture for integrating CoreStory into an existing non-determinism (ND) investigation workflow. CoreStory is not positioned as the primary ND detector. The proposed role is to help classify work, provide application context, support investigation, and route work into an appropriate engineering playbook.

The design intentionally preserves runtime evidence and SME validation as authoritative validation mechanisms.

## Conceptual Flow

```text
Runtime / Detection Evidence
        |
        v
Normalize ND Unit of Work
        |
        v
Workflow Dispatcher
        |
        +-- insufficient evidence --> HUMAN_TRIAGE_REQUIRED
        |
        +-- application defect ----> BUG_RESOLUTION
        |                                  |
        |                                  v
        |                         Agentic Bug Resolution
        |                                  |
        |                                  v
        |                         CoreStory Application Context
        |                                  |
        |                                  v
        |                         SME Validation
        |                                  |
        |                                  v
        |                         Runtime Validation / Check-In
        |
        +-- other classifications --> appropriate playbook
```

The editable presentation diagram is maintained separately in `nd-workflow-presentation.mmd`. Mermaid Live Editor can be used to preview and export it to SVG.

## Major Blocks

### 1. Evidence Intake

An ND unit of work may originate from runtime divergence, checksum/runtime logs, TSan, Coverity, developer-tool or AI scans, customer reports, or another observed failure.

The exact normalized evidence schema remains an open design item.

### 2. Workflow Dispatcher

The Workflow Dispatcher should perform only enough analysis to make a defensible routing decision. It should not perform the downstream ND investigation itself.

For the initial design, the most important paths are:

- `INCONCLUSIVE` -> `HUMAN_TRIAGE_REQUIRED` when evidence is insufficient or contradictory.
- `APPLICATION_DEFECT` -> `BUG_RESOLUTION` when evidence supports a localized application defect.
- Other supported classifications route to the corresponding engineering workflow.

### 3. Bug Resolution

The current candidate for confirmed or sufficiently supported application defects is the Agentic Bug Resolution playbook.

Its investigation model aligns with the proposed ND workflow because it requires reproduction where possible, application-context retrieval, affected code-path identification, a supported root-cause hypothesis, the smallest justified correction, and a validation plan before code modification.

This does **not** yet establish that Agentic Bug Resolution is sufficient for the customer's ND work. Existing customer developer skills and runtime workflow artifacts must be reviewed first.

### 4. CoreStory-Assisted Investigation

CoreStory's proposed role is application understanding and contextual investigation: affected components, execution paths, relationships, relevant source, application behavior, and potential impact.

Runtime evidence remains a separate and critical input. The intended design is to correlate runtime evidence with application context rather than replace runtime diagnosis.

### 5. Validation

Customer SME validation remains the authority for determining whether a suspected condition is a real ND defect. Runtime reproduction/checksum validation remains the authority for determining whether deterministic behavior has been restored.

### 6. Measurement

The workflow should eventually capture known-defect reproduction, net-new defects, false-positive rate, engineer and SME effort, developer-tool token usage where measurable, and time to successful check-in.

## Open Design Questions

- Should existing customer ND developer skills execute inside Agentic Bug Resolution or require a dedicated ND playbook?
- What is the normalized schema for an ND unit of work?
- How should checksum/runtime evidence be parsed and passed between stages?
- Do TSan, Coverity, runtime divergence, and proactive AI scans require separate execution variants?
- What evidence threshold is sufficient for `APPLICATION_DEFECT` rather than `INCONCLUSIVE`?
- Which validation gates can eventually be automated and which must remain human-controlled?

## Initial Validation Strategy

Start with one known, previously diagnosed ND defect in the agreed codebase scope. Reconstruct the customer's current workflow and evidence, submit the case through the proposed routing path, validate the investigation with the appropriate SME, and compare the result and effort against the existing baseline.

Generalize the workflow only after the known-defect path is understood.
