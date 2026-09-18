# ND Discovery Evaluation — Run Manifest

## Run identity

- **Run timestamp (start):** 2026-09-18 12:54 (UTC-5), America/Chicago
- **Evaluation type:** Final discovery-focused non-determinism (ND) evaluation on the CTS workspace. Discovery is frozen before proof/qualification.
- **Model:** Claude Opus 4.8 (Cursor agent).
- **Thinking effort:** Extended thinking enabled (high).
- **Operator harness:** Cursor IDE agent, PowerShell shell on win32 10.0.22631.

## Source snapshot under evaluation

- **Workspace path:** `c:\Users\carys\cts`
- **Snapshot selection:** Current customer CTS source snapshot selected for this evaluation (the working tree at `c:\Users\carys\cts`).
- **Version control metadata:** No git repository detected at the workspace root (`git rev-parse` exit 128); no commit SHA available. Snapshot is identified by workspace path + run timestamp.
- **Source size:** 2,391 C++ translation/header units (`*.cc,*.cpp,*.C,*.cxx,*.h,*.hh,*.hpp`) across 22 top-level module directories:
  ccd(447), cts(11), ctscstr(42), ctscto(270), ctsinterf(21), ctsmisc(41),
  ctsroute(15), ctsrpt(28), ctssc(148), ctssch(49), ctssplit(12), ctsui(52),
  ctsutil(183), export(41), icg(45), include(383), ips(11), irs(26),
  mscts(526), python(7), rlx(27), skewgrp(6).

## Enabled rules / skills / workflow authority

- **Always-applied workspace rule:** `corestory-nd-discovery.mdc` (thin CoreStory ND discovery rule) — applied as the discovery governance rule for Stage 1.
- **Discovery authority skill:** `nd-code-analyzer` (customer workflow) at `C:\Users\carys\.cursor\skills\nd-code-analyzer\`.
- **Later-stage skill (post-freeze):** `corestory-nd-qualification` at `C:\Users\carys\.cursor\skills\corestory-nd-qualification\`.
- **Not used for discovery/qualification guidance:** prior A/B reports, prior AI findings, prior benchmark conclusions, held-out TSan/Coverity ground truth. (Per controls.)

## Stage 0 — Discovery reference-set verification

The customer discovery reference set was verified by git-blob SHA-1 (`git hash-object`) against the fingerprint staged for this experiment.

| Required artifact (staged path) | Required SHA | Verified installed path | Computed SHA | Match |
| --- | --- | --- | --- | --- |
| `Synopsys_supporting_artifacts/nd_code_analylizer/SKILL.md` | `203f912941c041c2e5007441035159e87c8266f5` | `C:\Users\carys\.cursor\skills\nd-code-analyzer\SKILL.md` | `203f912941c041c2e5007441035159e87c8266f5` | ✅ |
| `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.md` | `fe5620e8dce3d2b5ce8279cc4f7d7a9ce4e46f1d` | `...\nd-code-analyzer\references\nd-patterns.md` | `fe5620e8dce3d2b5ce8279cc4f7d7a9ce4e46f1d` | ✅ |
| `Synopsys_supporting_artifacts/nd_code_analylizer/references/nd-patterns.yaml` | `6fd5cf240db010f0dca14afc0ff390456b41aa23` | `...\nd-code-analyzer\references\nd-patterns.yaml` | `6fd5cf240db010f0dca14afc0ff390456b41aa23` | ✅ |

**Result: REFERENCE-SET-VERIFIED.** All three load-bearing discovery inputs are byte-identical to the required fingerprint and are accessible to the workflow. The narrative reference (`nd-patterns.md`), the YAML scanner source-of-truth (`nd-patterns.yaml`, 27 patterns), and the SKILL method (`SKILL.md`) are consumed directly as the discovery authority.

- **Note on staged path:** The literal staged directory `Synopsys_supporting_artifacts/nd_code_analylizer/` does not exist inside the CTS workspace; the identical content is installed at the skill path above (SHA-verified). The Discovery Authority clause of `corestory-nd-discovery.mdc` names the *installed* customer references as the authority, so this is not a substitution — it is the same byte-identical material.

### Additional customer artifacts the skill references but which are UNAVAILABLE

Recorded per Stage 0 (these do not block discovery because the reference set itself is present; the YAML is the scanner source of truth and is reproduced faithfully with ripgrep):

- `scripts/scan_nd.py` — the Stage-1 mechanical scanner. **UNAVAILABLE** (no `scripts/` dir installed). **Mitigation:** Stage-1 mechanical scan reproduced by running the YAML `regex` fields directly with ripgrep 15.1.0 over the YAML `file_globs`. The YAML (SHA-verified) is the pattern source of truth, so candidate enumeration is faithful.
- `scripts/render_report.py` — report renderer. **UNAVAILABLE.** Not required for discovery freeze; discovery output is written directly as `candidate-set.md` / `discovery-readout.md`.
- `references/fix-recipes.md`, `references/id-system.md`, `assets/example_report.md` — **UNAVAILABLE.** These inform fix authoring/report styling, not candidate discovery; discovery recall is unaffected.
- `p4-code-ownership` skill — **UNAVAILABLE** (`C:\Users\carys\.cursor\skills\p4-code-ownership` absent). Ownership attribution (Stage 4b) is out of scope for this discovery-only freeze and depends on Perforce depot mapping not present in this local snapshot.
- `nwtn-src-cpp-code-navigation` skill (clangd_query.py) — **UNAVAILABLE.** This module is CTS (`c:\Users\carys\cts`), not `nwtn/src`, so the mandatory-clangd rule (scoped to `nwtn/src`) does not apply; C++ navigation for discovery uses ripgrep + targeted reads + CoreStory project 10.

## CoreStory configuration

- **Allowed project:** ID **10** (`cts-code`) only. Ingestion status: completed (100%).
- **Forbidden:** project 9 (`cts-code2`) and any other project — not used as evidence.
- **Role in discovery:** search expansion only (resolve helpers/accessors, find callers/callees, sibling paths, cross-file relationships, downstream consumers). CoreStory may not remove a customer-discovered candidate.

## Subagent / model topology (by stage)

- **Stage 0 (verification):** main agent only.
- **Stage 1 (mechanical scan):** main agent, ripgrep over YAML regexes. No subagents.
- **Stage 1 (triage + CoreStory expansion):** main agent, single-agent triage loop with targeted CoreStory (project 10) queries. Deliberate deviation from the skill's "parallel explore subagents for >=50 files / >=5 subdirs" guidance, chosen to keep the CoreStory project-10-only scope constraint and the provenance ledger centrally controlled (parallel subagents each issuing CoreStory calls would risk scope drift and fragment provenance). Recorded here and in `discovery-readout.md`. This choice does not reduce the candidate set — the full mechanical scan is retained and triaged.
- **Proof / qualification (post-freeze):** main agent with `corestory-nd-qualification`, CoreStory project 10.
