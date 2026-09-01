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
