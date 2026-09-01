# Non-Determinism Workflow Design

This repository is a working design space for a non-determinism (ND) investigation and resolution workflow that combines runtime evidence, engineering triage, CoreStory application context, and existing developer tooling.

## Current Direction

The project is intentionally moving away from a static prompt-comparison experiment and toward an evidence-driven workflow that integrates with the customer's existing ND diagnosis process.

The proposed high-level flow is:

```text
Runtime / Detection Evidence
        |
        v
Normalize ND Unit of Work
        |
        v
Workflow Dispatcher
        |
        +-- insufficient evidence --> Human Triage
        |
        +-- application defect ----> Bug Resolution
        |                                  |
        |                                  v
        |                         CoreStory-Assisted Investigation
        |                                  |
        |                                  v
        |                         SME Validation
        |                                  |
        |                                  v
        |                         Runtime Validation / Check-In
        |
        +-- other classifications --> appropriate workflow
```

CoreStory is not assumed to be the primary detector of nondeterminism. Its proposed role is to provide application context, help classify and route work, and support evidence-based investigation within the customer's existing process.

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── README.md
│   ├── architecture/
│   │   ├── nd-workflow-concept.md
│   │   └── nd-workflow-presentation.mmd
│   └── discovery/
│       └── customer-workflow-inputs.md
├── references/
│   └── corestory/
│       ├── agentic-bug-resolution.md
│       └── dispatcher-classifications.md
└── archive/
    └── legacy-static-evaluation/
```

## Working Principles

- Ground the workflow in real runtime evidence and known defects before generalizing it.
- Route work before performing a full downstream investigation.
- Preserve human and runtime validation as explicit decision gates.
- Separate customer-shareable workflow documentation from internal reference material.
- Treat earlier static-analysis experiments as historical evidence, not as the current architecture.
- Avoid claims about defect detection, token savings, or productivity until they are supported by measured results.

## Current Priorities

1. Obtain one known, previously diagnosed ND defect and the runtime/checksum evidence used to localize it.
2. Review the customer's existing ND Cursor skills and workflow artifacts.
3. Reconstruct the current detection-to-check-in workflow for that defect.
4. Determine where the Workflow Dispatcher and existing CoreStory playbooks fit.
5. Decide whether ND requires a dedicated playbook or an extension of an existing bug-resolution workflow.
6. Establish a validation and measurement model before broadening the workflow.

## Archived Work

The original static-analysis and prompt-comparison experiment is preserved under `archive/legacy-static-evaluation/`. It is retained for historical reference and should not be treated as the current recommended ND workflow.
