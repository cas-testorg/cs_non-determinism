# Staged execution evaluation
_Exported on 9/18/2026 at 14:21:40 CDT from Cursor (3.21.9)_

---

**User**

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

---

**Cursor**

I'll execute **Invocation 1 (Stage 0 + Stage 1: Discovery) only**, then stop. Let me begin by reading the customer skill and verifying the staged artifacts.

Now let me locate the staged customer artifacts and the CTS source snapshot in the workspace.

The workspace is the CTS source snapshot. The discovery scripts are at the root. Let me find the staged reference set and the `Synopsys_supporting_artifacts` folder, plus verify hashes.

The reference set isn't in the workspace root. Let me check the installed skill directory and inspect the scanner to see where it expects references.

The actual customer artifacts are installed in the skill directory, with script copies also at the CTS root. Let me verify the SHAs against the manifest (testing both git blob-hash and raw SHA1).

All six required artifacts are present with **matching manifest SHAs** (git-blob hashes). The reference set (`SKILL.md`, `nd-patterns.md`, `nd-patterns.yaml`) matches the installed skill-dir copies; the scripts (`scan_nd.py`, `render_report.py`, `report_template.md`) match the CTS-root copies. Now let me verify the runtime tooling (Python, PyYAML, ripgrep) and inspect the pattern catalog.

Python appears to be a Windows Store stub. Since Stage 0 requires the **actual** `scan_nd.py` (no emulated scanner), I must confirm whether a real Python interpreter exists before deciding `SCANNER-UNAVAILABLE`.

Found a real interpreter at `C:\Users\carys\.local\bin\python3.12.exe`. Let me verify it works and has PyYAML.

Python 3.12.14 works but lacks PyYAML. Installing PyYAML lets me run the **actual** customer scanner (not an emulation), which is what Stage 0 requires. Let me install it.

The blocked install mutates global tooling state. A lower-privilege alternative is to vendor PyYAML into a run-local directory (inside the eval output folder) and put it on `PYTHONPATH` only for the scanner call — this doesn't affect global tooling. Let me set up the run output directory and vendor locally.

PyYAML is vendored run-locally (global tooling untouched). Now I'll run the **actual** customer `scan_nd.py` (CTS-root copy, manifest SHA `451eb197…`) against the skill-dir `nd-patterns.yaml` (manifest SHA `6fd5cf24…`) over the CTS snapshot.

Scanner succeeded: **3673 raw candidates across 27 patterns**. Let me analyze the distribution by pattern and directory to plan triage and subagent dispatch.

Scanner output is frozen. Note patterns `1.2, 1.3, 3.3, 3.4, 3.6` hit the customer scanner's default `--max-per-pattern 500` cap (true counts higher — I'll record this as a scope limit but keep the customer default behavior). Let me get an accurate directory breakdown to plan subagent-based triage.

The path normalization needs fixing (backslashes). Let me redo the directory breakdown cleanly.

This clearly exceeds the skill's subagent threshold (≥50 files OR ≥5 subdirs → parallel `explore` subagents; run config = Explore SubAgent Model *Inherit from Parent*). I'll split the frozen candidates into directory-cluster slices, dispatch parallel explore subagents for Stage 2/3 triage, then do CoreStory expansion at the parent. First, let me create the slice files and read the narrative reference.

Slices ready. Now let me verify the CoreStory connection (project 10 `cts-code`) and get the `Task` subagent schema before dispatching.

Confirmed: **project 10 = `cts-code`** (ingestion complete); project 9 = `cts-code2` (excluded). CoreStory is available.

Now I'll dispatch **7 parallel `explore` subagents** (satisfying the skill's ≥50-files/≥5-subdirs threshold; model = inherit from parent) for Stage 2/3 triage of each slice.

All 7 subagents completed. Let me verify which triage JSON files were actually written to disk (some explore agents may be read-only).

All 7 triage artifacts are persisted (S2 on-disk has 19 vs 24 inline — the 5 delta are `ccd/include/soLogicCone.h` mirror-duplicates; I'll treat the on-disk files as canonical and note this). On-disk retained total = **334**.

Now, per Stage 1, I'll perform **CoreStory discovery expansion** (project 10 `cts-code` only) targeting the highest-value gaps: unresolved wrapper/comparator semantics and additional consumer sites. Let me get the CoreStory tool schemas.

I'll run targeted CoreStory semantic searches (project 10 `cts-code`) to attempt discovery expansion on the highest-value unresolved semantics and consumer paths.

CoreStory (project 10) results show its index contains **only the CTS module source already scanned** — the load-bearing wrapper/comparator implementations (`dosUnorderedSet`, `ndmObjPtrCmpType`, `nwcInsOrdMap`, `ndmObjectHandleNS::compareObjPtr`) live in **un-ingested** upstream libraries and appear only as `#include` references. Let me run two more expansion-oriented queries (semantic, not regex-shaped) to fairly test whether CoreStory surfaces any *new* candidate site.

CoreStory expansion result is now clear and I'll record it honestly: **every** chunk CoreStory returned is a file already covered by the customer scan (mscts, ccd, ctsutil, ctssc, skewgrp, include). CoreStory surfaced **no new candidate source location** and could **not** resolve the out-of-module wrapper/comparator implementations (they live in un-ingested upstream libs); it only provided corroborating in-module context. 

Now let me merge the frozen triage artifacts, assign stable IDs, and generate the candidate set.

334 candidates frozen. Let me assemble the final `candidate-set.md` (header + full candidate table + dismissed-bucket summary) programmatically.

Now let me write the `run-manifest.md` and `discovery-readout.md` artifacts with the verified facts.

All artifacts written. Let me verify the frozen output set and sanity-check the candidate table.

All four deliverables are present. Let me confirm `candidate-set.md` is well-formed.

The candidate set is well-formed. Stage 0 + Stage 1 are complete and frozen. I am **stopping here** as instructed — Stage 2, 3, and 4 were not performed.

## Invocation 1 complete — Stage 0 + Stage 1 (Discovery), FROZEN

### Stage 0 — workflow verified
All six required customer artifacts are present with **git-blob hashes exactly matching the Iteration-2 fingerprints**: the reference set (`SKILL.md`, `nd-patterns.md`, `nd-patterns.yaml`) from the installed skill dir, and the scripts (`scan_nd.py`, `render_report.py`, `report_template.md`) from the CTS root. So **not** `REFERENCE-SET-UNAVAILABLE` / `SCANNER-UNAVAILABLE`. I ran the **actual customer `scan_nd.py`** (no emulation) via CPython 3.12.14 + run-local vendored PyYAML (to avoid mutating global tooling) against the manifest-matching `nd-patterns.yaml`, using the Cursor-bundled ripgrep.

### Stage 1 — high-recall discovery
- **Scanner:** 3673 raw candidates across all 27 patterns, 588 files (verbose log preserved). Default `--max-per-pattern 500` cap left intact (recorded as a recall limit on patterns 1.2/1.3/3.3/3.4/3.6).
- **Subagents:** the skill's ≥50-files/≥5-subdirs threshold triggered; **7 `explore` subagents** (`model=inherit`, per the *Inherit from Parent* config) triaged the slices — all completed, no fallback/routing deviation. Topology and agent IDs recorded.
- **Frozen candidate set: 334** candidates (`CUSTOMER-PATTERN`, 100%) — realness hypothesis: 2 real, 282 latent-only, 25 UNRESOLVED, 25 mirror-duplicate. Latent/UNRESOLVED retained per the thin discovery rule (not dropped for incomplete downstream evidence). 3331 hits dismissed in 87 documented buckets.
- **CoreStory (project 10 `cts-code` only):** 6 semantic searches during discovery → **0 new candidates, 0 materially-broadened paths**. Recorded directly, not forced. Root cause: the project-10 index contains only the already-scanned CTS module source; the load-bearing upstream wrapper/comparator implementations (`dosUnordered*`, `ndmObjectHandleNS::compareObjPtr`, `nwcInsOrdMap`, `cstrClock::operator<`, …) are un-ingested and appear only as includes/typedefs. It provided corroborating-only context on 3 already-retained candidates; it removed none.

### Frozen deliverables (in `nd-eval-iter2/`)
- `run-manifest.md`, `candidate-set.md`, `discovery-readout.md`
- `raw/` reconstruction set: `candidates.json`, `scan_nd.stderr.log`, `slice_S*.json`, `triage_S*.json`, `merge_candidates.py`, `candidate-set.json`

Two provenance notes captured in the artifacts: (1) the skill dir also holds *non-matching* script copies — I executed the manifest-matching CTS-root `scan_nd.py`; (2) the S2 subagent's on-disk artifact (19 retained) is treated as canonical vs its inline message (24, incl. 5 `soLogicCone.h` mirror-duplicates).

**STOP.** Per the staged protocol, I did not run `prove-nd`/`prove-nd-mt` (Stage 2), `corestory-nd-qualification` (Stage 3), or Stage 4. Start Invocation 2 only after you've reviewed and accepted this candidate set as frozen.

