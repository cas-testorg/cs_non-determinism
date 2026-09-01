# CoreStory Agentic Bug Resolution — ND Design Reference

> **Reference summary.** Source: `cas-testorg/corestory-global-skills/skills/agentic-bug-resolution/SKILL.md` on `main` when this project structure was established. Consult the source repository for the current authoritative playbook.

## Purpose

Agentic Bug Resolution develops an evidence-based investigation and resolution plan for an application defect before attempting a fix.

## Why It Is a Candidate for ND Work

The playbook is intended for cases where application behavior is incorrect, the root cause is not yet understood, application context is required, and a localized correction may be appropriate after investigation.

That makes it a plausible downstream workflow for an ND case that the Workflow Dispatcher has classified as `APPLICATION_DEFECT` / `BUG_RESOLUTION`.

It is not yet established that the generic playbook is sufficient for Synopsys ND workflows. Existing Synopsys Cursor skills and runtime/checksum practices must be reviewed before making that design decision.

## Required Inputs

At minimum, the source playbook expects:

- Description of the observed failure or defect
- Relevant repository or application scope
- Available logs, issue details, CI evidence, or reproduction information
- CoreStory project or workspace context

## Investigation Model

The source playbook follows this general sequence:

1. Review the reported problem and available evidence.
2. Reproduce the failure when possible.
3. Use CoreStory to understand the affected application context.
4. Identify affected modules, components, code paths, and business behavior.
5. Develop and document a root-cause hypothesis.
6. Determine the smallest justified correction.
7. Define a validation plan.
8. Do not modify files until the investigation checkpoint is complete.

## Investigation Checkpoint

Before file modification, the playbook requires evidence covering:

- Proposed change
- Reproduction status
- First failing module or affected component
- Root-cause hypothesis
- CoreStory evidence
- Affected modules and code paths
- Smallest proposed correction
- Validation plan

## ND-Specific Questions to Resolve

- Where do checksum/runtime divergence artifacts enter this investigation sequence?
- Should a Synopsys ND skill run before, inside, or after the generic bug-resolution playbook?
- Does the concept of the "first failing module" map cleanly to Synopsys's first textual/runtime divergence?
- What ND-specific evidence is required before the investigation checkpoint can be satisfied?
- Should runtime validation after a correction remain external to the playbook or become an ND-specific extension?
