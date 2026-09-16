# Workflow Assets Used in the Evaluation

## Purpose

This directory identifies the governing rules and Synopsys non-determinism skills used during the evaluation so that the methodology is inspectable alongside the findings.

These assets are included because agent behavior is part of the experimental configuration. They should not be interpreted as the complete or final production workflow.

## Asset Manifest

| Asset | Owner | Role in evaluation | Applicable tests |
|---|---|---|---|
| `nd-code-analyzer` | Synopsys | Repository-scale candidate discovery, triage, deep read, realness classification, observability proof, and report generation | TC-001A, TC-001B, TC-001C, TC-002 |
| `prove-nd` | Synopsys | Deep proof/dismissal of ND suspects, downstream observability, controls/gating, reachability, neutralizer analysis | As invoked by Synopsys workflow |
| `non-determinism` / `prove-nd-mt` | Synopsys | Multi-threaded ND extension for races, order dependence, reductions, worker state, gates, and MT-specific neutralizers | As invoked by Synopsys workflow |
| `code-analysis-v2.mdc` | CoreStory | Earlier CoreStory application-context instructions | TC-001B |
| `code-analysis-v3.mdc` | CoreStory | Evidence-gated application qualification and investigation isolation | TC-001C, TC-002 CoreStory arm |

## References

The Synopsys skills reference additional pattern catalogs, navigation utilities, scripts, ownership workflows, and internal supporting material. Those references were part of the installed workflow where available, but they are **not reproduced in this customer package**.

This package focuses on the governing skill/rule instructions that materially explain the evaluation methodology and agent behavior.

## Important Skill Interaction Observed During Review

Review of the actual skill instructions identified an important orchestration detail.

The `nd-code-analyzer` skill explicitly instructs the agent to dispatch parallel `explore` subagents when either:

- the candidate set spans at least 50 candidate files, or
- the module spans at least five subdirectories.

By contrast, the `prove-nd` skill explicitly states:

> Do not use sub-tasks or sub-agents for this task.

The multi-threaded extension (`prove-nd-mt`) inherits that base `prove-nd` restriction.

This means the child/subagent activity observed during repository-scale scans should **not automatically be characterized as the client ignoring a no-subagent instruction**. At the discovery/triage stage, subagent creation is consistent with the `nd-code-analyzer` skill itself. The no-subagent rule applies to the deeper `prove-nd` workflow.

For controlled comparisons, the execution record should therefore distinguish:

```text
nd-code-analyzer discovery / triage
    -> parallel subagents may be expected by skill design

prove-nd / prove-nd-mt deep proof
    -> subagents are explicitly prohibited by skill design
```

If subagents are observed during a `prove-nd` stage, that is a different and more meaningful orchestration-compliance issue.

## Version / Provenance Notes

The copies in this package are evaluation snapshots taken from the repository branch used to construct the customer findings package. Source provenance and exact source blob identifiers are recorded in the accompanying asset files where practical.

The `nd-code-analyzer` source identifies itself as version 1.4.0 and includes later change-history notes, including the static concurrency/MT-ND additions. The evaluation package preserves the operative workflow used for this assessment rather than attempting to reconcile upstream/internal version history.

## Excluded Future Work

The proposed CoreStory-specific qualification skill (`corestory-qualify`) is intentionally excluded. It was not part of the exploratory A/B configuration represented by this package and is being considered as a possible future workflow refinement.
