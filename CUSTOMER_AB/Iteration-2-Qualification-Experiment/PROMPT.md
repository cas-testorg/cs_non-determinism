# Iteration 2 Execution Prompt

Run one final discovery-focused non-determinism evaluation on the CTS workspace, then continue into proof and qualification only after the discovery result is frozen.

## Evaluation controls

- Use the current customer CTS source snapshot selected for this evaluation.
- CoreStory scope is **project ID 10 (`cts-code`) only**.
- Do not use `cts-code2` or any other CoreStory project as evidence.
- Preserve raw outputs.
- Do not use prior A/B reports, prior AI findings, prior benchmark conclusions, or held-out TSan/Coverity ground truth to guide discovery or qualification.
- Do not modify source code.
- Record model, thinking effort, enabled rules/skills, subagent behavior by stage, source snapshot, and run timestamp.

## Stage 0 — Verify exact customer discovery reference set

For Stage 1, use the customer-provided `nd-code-analyzer` skill and its supporting reference set from the installed customer workflow. The staged copies for this experiment are:

- `Synopsys_supporting_artifacts/nd_code_analylizer/SKILL.md`
  - SHA: `203f912941c041c2e5007441035159e87c8266f5`
- `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.md`
  - SHA: `fe5620e8dce3d2b5ce8279cc4f7d7a9ce4e46f1d`
- `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.yaml`
  - SHA: `6fd5cf240db010f0dca14afc0ff390456b41aa23`

The YAML is the scanner source of truth and contains the customer pattern catalog. The narrative/reference material and concrete examples are part of the discovery method.

Before discovery:

1. verify these artifacts are accessible to the workflow;
2. record their paths and identifiers in `run-manifest.md`;
3. confirm the discovery process can consume the same pattern/reference material used by the customer workflow;
4. record any additional installed customer artifact the skill requires but that is unavailable.

If the required discovery reference set cannot be used, record `REFERENCE-SET-UNAVAILABLE` and stop before measured discovery.

Do not substitute generic ND knowledge, CoreStory examples, previous A/B findings, or held-out ground truth for the customer reference set.

## Stage 1 — One final high-recall discovery attempt

Use the customer's `nd-code-analyzer` workflow and its supporting references as the discovery authority.

Apply the thin `corestory-nd-discovery` rule.

**Primary objective: improve or expand candidate discovery without reducing the candidate set the customer workflow would retain.**

Preserve the customer's own discovery behavior, including its pattern-specific narrowing, semantic review, false-positive guidance, downstream-observability reasoning, and configured subagent behavior.

CoreStory is allowed to participate during discovery, not only after it. Use it selectively where application relationships can broaden the search, for example:

- resolve a suspicious helper/accessor to its implementations;
- find callers/callees that expose additional candidate sites;
- identify related implementations or sibling paths;
- trace a suspect construct into related production modules;
- identify downstream consumers that suggest additional source locations to inspect;
- expose cross-file relationships that local pattern scanning may not surface.

CoreStory **must not remove** a customer-discovered candidate merely because build inclusion, reachability, configuration, propagation, neutralization, or observable consequence is incomplete. Record contrary evidence for later proof/qualification.

For every retained candidate record:

- stable candidate ID;
- file/function/location;
- suspected mechanism;
- exact customer pattern/reference/example family that guided discovery, when identifiable;
- discovery evidence;
- severity hypothesis;
- discovery origin: `CUSTOMER-PATTERN`, `CORESTORY-EXPANSION`, `BOTH`, or `OTHER`;
- whether CoreStory was used;
- CoreStory question/purpose and returned relationship/evidence;
- any additional candidate/path exposed by CoreStory.

Write the complete result to `candidate-set.md`.

Also write `discovery-readout.md` containing:

- total frozen candidates;
- candidates originating from customer pattern/reference discovery;
- candidates added through CoreStory expansion;
- candidates where CoreStory materially broadened the evidence/path;
- CoreStory calls/purposes that produced no useful expansion;
- unavailable evidence or tooling;
- subagent/model topology actually used.

**STOP AND FREEZE THE CANDIDATE SET BEFORE PROOF OR QUALIFICATION.**

Do not retroactively change Stage 1 counts.

## Stage 1 decision gate

This is the final discovery-focused iteration.

After the candidate set is frozen, preserve all discovery evidence regardless of outcome. Do not tune the rule, prompt, or reference set in response to the observed results within this run.

The later evaluation will compare the frozen discovery result against the customer process and SME/held-out evidence only after the automated artifacts are frozen.

If CoreStory does not materially expand useful discovery or otherwise improve the discovery evidence, record that result directly. Do not force a discovery-value conclusion. The preserved artifacts become the evidence package for the next hypothesis.

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

Treat this as a secondary measurement in this iteration; do not use qualification success to mask or redefine the Stage 1 discovery result.

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

Capture the provenance ledger required by the qualification skill so CoreStory's contribution can be reconstructed even if MCP/chat transcripts are unavailable.

Candidates first discovered during qualification must be labeled `QUALIFICATION-DISCOVERED` and must not alter the Stage 1 discovery denominator.

## Stage 4 — Freeze artifacts for evaluation

Produce:

- `run-manifest.md`
- `candidate-set.md`
- `discovery-readout.md`
- `mechanism-proof.md`
- `qualification-report.md`
- `sme-review.md`

Do not expose held-out ground truth until these artifacts and automated dispositions are frozen.

Finish with an evaluation summary that keeps separate:

- discovery performance;
- CoreStory discovery-expansion contributions;
- mechanism-proof performance;
- application-qualification performance;
- CoreStory qualification contributions;
- unresolved evidence;
- recommended SME/runtime validation.

Do not collapse these stages into a single precision/recall conclusion.
