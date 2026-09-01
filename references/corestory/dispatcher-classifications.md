# CoreStory Workflow Dispatcher — Classification Reference

> **Reference snapshot.** Source: `cas-testorg/corestory-global-skills/skills/workflow-dispatcher/classifications.md` on `main` when this project structure was established. Consult the source repository for the current authoritative definition.

## Incident Disposition

Choose exactly one when applicable:

- `APPLICATION_DEFECT` — existing application behavior is incorrect or does not match expected behavior.
- `INVALID_AUTOMATED_CHANGE` — an automated change, dependency update, generated modification, or similar action is inappropriate or incompatible.
- `EXPECTED_BEHAVIOR` — the application is operating as currently designed, but the desired outcome may require different or additional functionality.
- `INCONCLUSIVE` — available evidence is insufficient or contradictory.

Incident disposition is optional when the request does not describe an incident, failure, or observed application behavior.

## Next-Work Classification

Choose exactly one:

- `BUG_RESOLUTION` — investigate and resolve a localized application defect.
- `FEATURE_GAP_ANALYSIS` — evaluate a requested new capability against the existing application.
- `CODEBASE_ASSESSMENT` — establish a broad understanding of an unfamiliar or insufficiently understood application.
- `CODE_MODERNIZATION` — assess or plan a broader framework, platform, dependency, or architectural modernization.
- `AUTOMATION_CONFIGURATION` — correct or improve CI/CD, dependency automation, tooling, or workflow configuration.
- `HUMAN_TRIAGE_REQUIRED` — no existing workflow can be selected confidently with the available evidence.

## Execution Variant

Current variants:

- `STANDARD`
- `VIBE_MODERNIZATION`

Execution variants refine how a workflow is performed and do not replace the primary next-work classification.

## Confidence

- `HIGH` — evidence clearly supports the selected workflow and there are no significant competing classifications.
- `MEDIUM` — selected workflow is the best fit, but important context or evidence remains incomplete.
- `LOW` — multiple workflows remain plausible or available evidence is insufficient.

A `LOW` confidence recommendation should normally route to `HUMAN_TRIAGE_REQUIRED`.

## ND Design Relevance

The initial ND architecture primarily depends on:

- `APPLICATION_DEFECT` -> `BUG_RESOLUTION` for a sufficiently evidenced localized defect.
- `INCONCLUSIVE` -> `HUMAN_TRIAGE_REQUIRED` when runtime or other evidence is insufficient or contradictory.

Other classifications remain available when the evidence indicates the work is not a localized defect.
