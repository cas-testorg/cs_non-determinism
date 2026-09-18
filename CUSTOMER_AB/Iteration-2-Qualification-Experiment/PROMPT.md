# Iteration 2 Staged Execution Prompts

Run this evaluation as **separate invocations by stage**. Do not continue automatically from one stage to the next.

The stage boundary is part of the experiment: outputs from each stage must be written and frozen before the next stage begins.

## Common evaluation controls

Apply these controls to every stage:

- Use the current customer CTS source snapshot selected for this evaluation.
- CoreStory scope is **project ID 10 (`cts-code`) only**.
- Do not use `cts-code2` or any other CoreStory project as evidence.
- Preserve raw outputs.
- Do not use prior A/B reports, prior AI findings, prior benchmark conclusions, or held-out TSan/Coverity ground truth to guide discovery, proof, or qualification.
- Do not modify source code.
- Record model, thinking effort, enabled rules/skills, subagent behavior by stage, source snapshot, and run timestamp.
- Do not retroactively modify a frozen artifact to improve a later-stage result. Corrections must be recorded separately with their reason.

---

# Invocation 1 — Stage 0 + Stage 1: Discovery

**Run Stage 0 and Stage 1 only. Stop immediately after writing and freezing the Stage 1 artifacts. Do not run `prove-nd`, `prove-nd-mt`, `corestory-nd-qualification`, mechanism proof, or application qualification in this invocation.**

## Stage 0 — Verify exact customer discovery workflow

Use the customer-provided `nd-code-analyzer` skill and its supporting reference set and scripts from the installed customer workflow.

The staged copies for this experiment are:

### Skill and references

- `Synopsys_supporting_artifacts/nd_code_analylizer/SKILL.md`
  - SHA: `203f912941c041c2e5007441035159e87c8266f5`
- `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.md`
  - SHA: `fe5620e8dce3d2b5ce8279cc4f7d7a9ce4e46f1d`
- `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.yaml`
  - SHA: `6fd5cf240db010f0dca14afc0ff390456b41aa23`

### Discovery scripts

- `Synopsys_supporting_artifacts/nd_code_analylizer/scripts/scan_nd.py`
  - SHA: `451eb197897b7df4357e546b02399195f5cdd1ef`
- `Synopsys_supporting_artifacts/nd_code_analylizer/scripts/render_report.py`
  - SHA: `9de0df590e93dc49deba84d92a98fb6c129e39dc`
- `Synopsys_supporting_artifacts/nd_code_analylizer/scripts/report_template.md`
  - SHA: `a9a40af890538e8e0eb1100f49af9ac6da32c6e6`

The YAML is the scanner source of truth and contains the customer pattern catalog. The narrative/reference material, concrete examples, scripts, and skill instructions are part of the customer discovery method.

Before discovery:

1. verify the required artifacts are accessible to the workflow;
2. record their installed paths and identifiers/hashes in `run-manifest.md`;
3. use the actual customer `scan_nd.py` rather than recreating its scanning behavior with ad hoc regex/ripgrep logic;
4. confirm the discovery process can consume the same pattern/reference material used by the customer workflow;
5. record any additional installed customer artifact the skill requires but that is unavailable;
6. record the actual Cursor parent model, thinking effort, and Explore SubAgent Model setting.

If the required discovery reference set or `scan_nd.py` cannot be used, record `REFERENCE-SET-UNAVAILABLE` or `SCANNER-UNAVAILABLE` as applicable and stop before measured discovery. Do not silently substitute an emulated scanner.

Do not substitute generic ND knowledge, CoreStory examples, previous A/B findings, or held-out ground truth for the customer reference set.

## Stage 1 — Final high-recall discovery attempt

Use the customer's `nd-code-analyzer` workflow and its supporting references/scripts as the discovery authority.

Apply the thin `corestory-nd-discovery` rule.

**Primary objective: improve or expand candidate discovery without reducing the candidate set the customer workflow would retain.**

Preserve the customer's discovery behavior, including:

- its actual `scan_nd.py` mechanical scan;
- pattern-specific narrowing;
- semantic review;
- false-positive guidance;
- downstream-observability reasoning;
- configured subagent behavior.

### Subagent control

Cursor's **Explore SubAgent Model is configured to `Inherit from Parent`** for this run.

Do not disable subagents to simplify provenance or CoreStory scoping. Follow the `nd-code-analyzer` skill's own subagent dispatch criteria. If the skill dispatches Explore subagents, allow them to run and record the actual topology.

Every agent or subagent that uses CoreStory must use **project ID 10 (`cts-code`) only**. Do not use project 9 (`cts-code2`) or any other project.

Record:

- whether the skill's subagent threshold was triggered;
- whether subagents were actually created;
- parent model;
- subagent model actually used, if observable;
- number/purpose of subagents, if observable;
- any subagent failure, fallback, or model-routing deviation.

Do not force subagents if the skill does not call for them, and do not suppress them if it does.

### CoreStory discovery expansion

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
- scanner/script execution actually used;
- subagent/model topology actually used.

## Stage 1 decision gate

This is the final discovery-focused iteration.

After the candidate set is frozen, preserve all discovery evidence regardless of outcome. Do not tune the rule, prompt, scripts, reference set, or orchestration in response to the observed results within this run.

If CoreStory does not materially expand useful discovery or otherwise improve discovery evidence, record that result directly. Do not force a discovery-value conclusion.

### Required Stage 0 + 1 outputs

Produce and freeze:

- `run-manifest.md`
- `candidate-set.md`
- `discovery-readout.md`
- raw scanner/discovery outputs needed to reconstruct the run

**STOP HERE. End the invocation. Do not perform Stage 2 or Stage 3.**

---

# Invocation 2 — Stage 2: Mechanism proof

**Start a new invocation only after the Stage 1 candidate set has been reviewed and accepted as frozen. Run Stage 2 only. Do not run Stage 3 qualification in this invocation.**

Use the frozen `candidate-set.md` as the complete Stage 2 input. Do not rerun discovery and do not add newly discovered candidates to the Stage 1 denominator.

For each frozen candidate, use the customer's installed `prove-nd` workflow and `prove-nd-mt` where appropriate.

Preserve the customer orchestration rule that `prove-nd` / `prove-nd-mt` must not use subagents, even though Stage 1 discovery may have used Explore subagents.

Record for each candidate:

- `PROVED`, `NOT PROVED`, or `UNRESOLVED`;
- exact mechanism being tested;
- direct source/mechanism evidence;
- required varying input/state;
- missing load-bearing evidence;
- reason for the disposition.

Do not remove or rewrite candidates in `candidate-set.md`.

Write the complete result to:

- `mechanism-proof.md`

Preserve supporting raw proof outputs where useful.

**STOP HERE. End the invocation. Do not perform Stage 3.**

---

# Invocation 3 — Stage 3: CoreStory application qualification

**Start a new invocation only after Stage 2 is frozen. Run Stage 3 only.**

Run the `corestory-nd-qualification` skill against the frozen Stage 1 candidate set, using the Stage 2 mechanism proof as evidence where applicable.

CoreStory scope remains **project ID 10 (`cts-code`) only**.

Treat application qualification as a separate measurement. Do not use qualification success to alter or redefine the Stage 1 discovery result or Stage 2 mechanism-proof result.

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

**Do not infer missing load-bearing semantics.** If an implementation required by the conclusion is unavailable, mark the relevant dimension `UNRESOLVED`.

Capture the provenance ledger required by the qualification skill so CoreStory's contribution can be reconstructed even if MCP/chat transcripts are unavailable.

For each material CoreStory contribution record:

- evidence ID;
- candidate ID;
- question/purpose;
- CoreStory relationship/evidence returned;
- corroborating direct source evidence, if available;
- qualification dimension affected;
- decision/disposition affected.

Candidates first discovered during qualification must be labeled `QUALIFICATION-DISCOVERED` and must not alter the Stage 1 discovery denominator.

Write the complete result to:

- `qualification-report.md`

Preserve supporting raw qualification evidence where useful.

**STOP HERE. End the invocation before SME/ground-truth evaluation.**

---

# Invocation 4 — Stage 4: Evaluation / SME package

**Run only after Stages 1–3 and their automated dispositions are frozen.**

Do not alter the frozen Stage 1, Stage 2, or Stage 3 artifacts.

Prepare:

- `sme-review.md`
- final evaluation summary

The evaluation summary must keep separate:

- discovery performance;
- CoreStory discovery-expansion contributions;
- mechanism-proof performance;
- application-qualification performance;
- CoreStory qualification contributions;
- unresolved evidence;
- recommended SME/runtime validation.

Do not collapse the stages into a single precision/recall conclusion.

Held-out ground truth or customer/SME adjudication may be introduced only at this stage, after the automated artifacts are frozen. Clearly distinguish:

- automated finding;
- source-based adjudication;
- runtime evidence;
- SME disposition;
- held-out benchmark match/miss.

The purpose of Stage 4 is evaluation, not retroactive tuning.
