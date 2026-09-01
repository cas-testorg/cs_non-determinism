# Non-Determinism Workflow — Conceptual Architecture

> **Status:** Draft / theoretical. Subject to validation against Synopsys workflow artifacts, known defects, runtime evidence, and existing Cursor skills.

This document captures a high-level proposed workflow for non-determinism (ND) investigation and resolution. The intent is to integrate with the customer's existing runtime-driven diagnosis process rather than replace it.

## Presentation View

```mermaid
flowchart LR
    A[ND Unit of Work] --> B[Normalize Evidence]
    B --> C[Workflow Dispatcher]

    C --> D{Sufficient evidence?}
    D -- No --> E[INCONCLUSIVE]
    E --> F[HUMAN_TRIAGE_REQUIRED]
    F --> G[Request Missing Evidence]
    G --> B

    D -- Yes --> H{Application defect?}
    H -- Yes --> I[APPLICATION_DEFECT]
    I --> J[BUG_RESOLUTION]
    J --> K[Agentic Bug Resolution]

    H -- No --> L{Route by work type}
    L --> M[FEATURE_GAP_ANALYSIS]
    L --> N[CODEBASE_ASSESSMENT]
    L --> O[AUTOMATION_CONFIGURATION]
    L --> F

    K --> P[CoreStory-Assisted Investigation]
    P --> Q[Synopsys SME Validation]
    Q --> R{Confirmed ND defect?}

    R -- No --> S[Record Rejected Finding / False Positive]
    R -- Yes --> T[Resolution / Fix]
    T --> U[Runtime Validation]
    U --> V{Determinism restored?}
    V -- No --> P
    V -- Yes --> W[Successful Check-In]

    S --> X[Capture Metrics]
    W --> X
```

## Detailed Workflow View

```mermaid
flowchart TD

    A[ND Unit of Work] --> B[Collect / Normalize Evidence]

    B --> B1[Possible Inputs]
    B1 --> B2[Known Runtime Divergence]
    B1 --> B3[Checksum / Runtime Logs]
    B1 --> B4[TSan Finding]
    B1 --> B5[Coverity Finding]
    B1 --> B6[Cursor / AI Scan Finding]
    B1 --> B7[Customer / Test Report]

    B --> C[Workflow Dispatcher]

    C --> D{Is there sufficient evidence<br/>to classify the work?}

    D -- No --> E[INCONCLUSIVE]
    E --> F[HUMAN_TRIAGE_REQUIRED]
    F --> G[Request Missing Evidence]
    G --> B

    D -- Yes --> H{Does evidence indicate<br/>an application defect?}

    H -- Yes --> I[APPLICATION_DEFECT]
    I --> J[BUG_RESOLUTION]
    J --> K[Agentic Bug Resolution Playbook]

    H -- No --> L{What type of work<br/>does the evidence support?}

    L --> M[Expected Behavior / New Capability]
    M --> N[FEATURE_GAP_ANALYSIS]

    L --> O[Broader Code Understanding Needed]
    O --> P[CODEBASE_ASSESSMENT]

    L --> Q[Tooling / Workflow Configuration]
    Q --> R[AUTOMATION_CONFIGURATION]

    L --> S[Cannot Confidently Classify]
    S --> F

    K --> T[CoreStory-Assisted Investigation]

    T --> T1[Understand Affected Application Context]
    T --> T2[Trace Components / Execution Paths]
    T --> T3[Correlate Runtime Evidence to Source]
    T --> T4[Develop Root-Cause Hypothesis]
    T --> T5[Assess Scope / Impact]
    T --> T6[Define Smallest Justified Correction]
    T --> T7[Define Validation Plan]

    T --> U{Investigation checkpoint<br/>satisfied?}

    U -- No --> V[Gather More Evidence]
    V --> T

    U -- Yes --> W[Synopsys SME Validation]

    W --> X{Confirmed ND defect?}

    X -- No --> Y[Record False Positive /<br/>Rejected Hypothesis]
    Y --> Z[Capture Result + Metrics]

    X -- Yes --> AA[Resolution / Fix]
    AA --> AB[Runtime Reproduction & Validation]

    AB --> AC{Deterministic behavior<br/>restored?}

    AC -- No --> T
    AC -- Yes --> AD[Successful Check-In]
    AD --> Z

    Z --> AE[Measure POV Outcomes]
    AE --> AE1[Known Defect Reproduced]
    AE --> AE2[Net-New Defect]
    AE --> AE3[False-Positive Rate]
    AE --> AE4[Engineer / SME Effort]
    AE --> AE5[Cursor Token Usage]
    AE --> AE6[Time to Successful Check-In]
```

## Proposed Control Flow

1. **Evidence intake** — create an ND unit of work from runtime divergence, checksum logs, TSan, Coverity, Cursor/AI scans, or another observed failure.
2. **Workflow dispatch** — classify the work before performing a full investigation.
3. **Playbook routing** — route a supported application defect to `BUG_RESOLUTION` and the Agentic Bug Resolution playbook; route other work according to the dispatcher taxonomy.
4. **CoreStory-assisted investigation** — use application intelligence to understand affected components, execution paths, relationships, likely impact, and relevant source before proposing a correction.
5. **Human validation** — retain Synopsys SME validation as the authority for whether the suspected ND condition is a real defect.
6. **Runtime validation** — verify that any correction restores deterministic behavior using the appropriate reproducible runtime test.
7. **Measurement** — capture result quality, false positives, engineer/SME effort, token usage, and time to successful check-in.

## Open Design Questions

The following are intentionally unresolved until customer artifacts are available:

- Whether Synopsys's existing ND Cursor skills should be invoked inside Agentic Bug Resolution or require a separate ND-specific playbook.
- The exact normalized schema for an ND unit of work.
- How checksum/runtime evidence should be parsed, summarized, and passed between workflow stages.
- Whether TSan, Coverity, runtime divergence, and proactive AI scans require separate execution variants.
- What evidence threshold is required to classify a finding as `APPLICATION_DEFECT` rather than `INCONCLUSIVE`.
- Which validation gates can eventually be automated and which must remain human-controlled.

## Initial Validation Strategy

Start with one known, previously diagnosed ND defect in the scoped CTS/presynthesis codebase:

1. Obtain the original runtime/checksum evidence and known root cause.
2. Recreate the customer's current workflow and baseline effort.
3. Submit the case as an ND unit of work.
4. Run it through the dispatcher and selected playbook.
5. Validate the investigation with the appropriate Synopsys SME.
6. Compare the result and effort against the established baseline.
7. Generalize the workflow only after the known-defect path is understood.
