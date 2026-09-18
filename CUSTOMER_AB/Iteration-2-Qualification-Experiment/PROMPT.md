# Iteration 2 Execution Prompt

Run the staged non-determinism evaluation on the CTS workspace.

## Evaluation controls

- Use the current customer CTS source snapshot selected for this evaluation.
- CoreStory scope is **project ID 10 (`cts-code`) only**.
- Do not use `cts-code2` or any other CoreStory project as evidence.
- Preserve raw outputs.
- Do not use prior A/B reports, prior AI findings, prior benchmark conclusions, or held-out TSan/Coverity ground truth to guide discovery or qualification.
- Do not modify source code.
- Record the model, thinking effort, enabled rules/skills, subagent behavior by stage, source snapshot, and run timestamp.

## Critical reference-set requirement

For Stage 1 discovery, use the customer's installed `nd-code-analyzer` skill **with the same installed supporting reference set used by the customer process**, including its concrete examples, pattern catalogs, and supporting case/reference material.

Do not substitute the sanitized evaluation snapshot of the skill for those installed references.

Before beginning discovery, verify that the supporting references/examples expected by `nd-code-analyzer` are accessible.

If they are not accessible:

1. record `REFERENCE-SET-UNAVAILABLE`;
2. identify which expected reference/example material is unavailable, as precisely as possible;
3. stop before measured discovery;
4. do not characterize the resulting run as comparable to the customer's discovery workflow.

The reference set may guide recognition of mechanism families in the same way it does in the customer's normal process. Do not use held-out evaluation ground truth unless it is genuinely part of that normal installed reference set.

## Stage 1 — Discovery

Use the customer's installed `nd-code-analyzer` skill as-is for broad discovery.

Apply the thin `corestory-nd-discovery` rule.

Goal: maximize retention of plausible HIGH/MEDIUM ND candidates.

CoreStory may be used to **expand** discovery by resolving callers, accessors, implementations, related modules, or downstream paths. It must not eliminate a discovered candidate based on incomplete application qualification.

For every candidate record:

- stable candidate ID;
- file/function/location;
- suspected mechanism;
- concrete customer reference/example or pattern family that guided discovery, when identifiable;
- discovery evidence;
- severity hypothesis;
- whether CoreStory was used;
- CoreStory purpose and contribution;
- any path/candidate added through CoreStory expansion.

Write the complete result to `candidate-set.md`.

**STOP AND FREEZE THE CANDIDATE SET BEFORE QUALIFICATION.**

Report the Stage 1 candidate count and confirm the candidate set is frozen.

## Stage 2 — Mechanism proof

For each frozen candidate, use the customer's installed `prove-nd` workflow and `prove-nd-mt` where appropriate.

Preserve the customer's orchestration rules: repository-scale discovery may use the subagent behavior defined by `nd-code-analyzer`; `prove-nd` / `prove-nd-mt` must not use subagents.

Record for each candidate:

- PROVED / NOT PROVED / UNRESOLVED;
- direct mechanism evidence;
- missing evidence.

Do not remove candidates from `candidate-set.md`.

## Stage 3 — CoreStory application qualification

Run the `corestory-nd-qualification` skill against the frozen candidate set.

For each relevant candidate qualify:

1. production build inclusion;
2. production reachability;
3. runtime/configuration gates;
4. exact varying input/state and ND mechanism;
5. propagation through callers/consumers;
6. deterministic neutralizers;
7. observable consequence;
8. blast radius;
9. missing load-bearing evidence.

Use CoreStory for application relationships and targeted source inspection for exact C++ semantics.

**Do not infer missing load-bearing semantics.** If an implementation required by the conclusion is unavailable, mark the dimension `UNRESOLVED`.

Capture the provenance ledger required by the qualification skill so the role of CoreStory can be reconstructed even if the MCP/chat transcript is not retained.

Candidates first discovered during qualification must be labeled `QUALIFICATION-DISCOVERED` and must not alter the Stage 1 discovery denominator.

## Stage 4 — Output for SME review

Produce:

- `candidate-set.md` — frozen discovery output;
- `mechanism-proof.md` — Stage 2 results;
- `qualification-report.md` — Stage 3 results and provenance;
- `sme-review.md` — concise review sheet with AGREE / DISAGREE / INSUFFICIENT EVIDENCE fields.

Do not expose held-out ground truth until these artifacts and automated dispositions are frozen.

Finish with a short evaluation summary separating:

- discovery performance;
- mechanism-proof performance;
- application-qualification performance;
- CoreStory discovery-expansion contributions;
- CoreStory qualification contributions;
- unresolved evidence;
- recommended SME/runtime validation.

Do not collapse these stages into a single precision/recall conclusion.
