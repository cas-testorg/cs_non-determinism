# Run Manifest — Iteration 2, Invocation 1 (Stage 0 + Stage 1: Discovery)

**Run timestamp:** 2026-09-18 (local, UTC-5), started ~13:37.
**Invocation scope:** Stage 0 (verify workflow) + Stage 1 (high-recall discovery) ONLY.
Stage 2 (`prove-nd`/`prove-nd-mt`), Stage 3 (`corestory-nd-qualification`), and Stage 4 were **not** run.

## Source snapshot

- **Path:** `C:\Users\carys\cts` (customer CTS source snapshot selected for this evaluation).
- **VCS:** not a git working tree (`git rev-parse` → exit 128); no commit id available. Snapshot identified by path + source file mtimes (source dirs last modified 2026-08-24) + scanner artifact hashes below.
- **Top-level source dirs scanned:** ccd, cts, ctscstr, ctscto, ctsinterf, ctsmisc, ctsroute, ctsrpt, ctssc, ctssch, ctssplit, ctsui, ctsutil, export, icg, include, ips, irs, mscts, rlx, skewgrp (scan path = repo root `.`).
- **Scan file globs (from YAML patterns):** `*.cc, *.cpp, *.C, *.cxx, *.h, *.hh, *.hpp`.

## Stage 0 — Customer workflow verification

### Required artifacts — installed paths + hashes (git blob SHA-1)

The Iteration-2 staged fingerprint hashes are **git blob** hashes. All six required artifacts are present and **match** the manifest fingerprints. The reference set matches the installed skill-dir copies; the scripts match the CTS-root copies.

| Artifact | Installed path used | git-blob SHA | Manifest SHA | Match |
|---|---|---|---|---|
| SKILL.md | `C:\Users\carys\.cursor\skills\nd-code-analyzer\SKILL.md` | `203f912941c041c2e5007441035159e87c8266f5` | `203f9129…` | ✅ |
| references/nd-patterns.md | `…\skills\nd-code-analyzer\references\nd-patterns.md` | `fe5620e8dce3d2b5ce8279cc4f7d7a9ce4e46f1d` | `fe5620e8…` | ✅ |
| references/nd-patterns.yaml (**scanner source of truth**) | `…\skills\nd-code-analyzer\references\nd-patterns.yaml` | `6fd5cf240db010f0dca14afc0ff390456b41aa23` | `6fd5cf24…` | ✅ |
| scripts/scan_nd.py (**scanner used**) | `C:\Users\carys\cts\scan_nd.py` (CTS-root copy) | `451eb197897b7df4357e546b02399195f5cdd1ef` | `451eb197…` | ✅ |
| scripts/render_report.py | `C:\Users\carys\cts\render_report.py` (CTS-root copy) | `9de0df590e93dc49deba84d92a98fb6c129e39dc` | `9de0df59…` | ✅ |
| scripts/report_template.md | `C:\Users\carys\cts\report_template.md` (CTS-root copy) | `a9a40af890538e8e0eb1100f49af9ac6da32c6e6` | `a9a40af8…` | ✅ |

**Result:** neither `REFERENCE-SET-UNAVAILABLE` nor `SCANNER-UNAVAILABLE`. Measured discovery proceeded.

**Note (script duplication):** the installed skill-dir also carries *different* script copies (`scripts\scan_nd.py` git `65a41f656bac1412ae25937898e47bcc2cc43b55`, `render_report.py` git `d749525e…`, `report_template.md` git `a729d5e0…`) that do **not** match the Iteration-2 fingerprints. The manifest-matching CTS-root `scan_nd.py` was the one executed, driven by the manifest-matching skill-dir `nd-patterns.yaml`. `render_report.py`/`report_template.md` were **not** executed (Stage 1 stops before report rendering).

### Confirmation the process consumed the customer pattern/reference material

- `scan_nd.py` loaded `references/nd-patterns.yaml` and reported **"Loaded 27 patterns"** → **"Wrote 3673 candidates across 27 patterns"**. The 27-pattern catalog is the customer catalog (patterns 1.1–4.6). Verbose scanner log preserved at `raw/scan_nd.stderr.log`.
- Stage 2/3 triage subagents were pointed at the customer `references/nd-patterns.md` (narrative) and the SKILL.md Stage 2/Stage 3 / pattern-specific-narrowing / false-positive-case-study sections as the triage authority.

### Additional customer artifacts required by the skill but UNAVAILABLE

- `references/fix-recipes.md`, `references/id-system.md`, `assets/example_report.md` — **absent** from the installed skill. Not load-bearing for Stage 1 discovery (used for Version A/B/C fix authoring and Stage 5 report rendering, which are out of scope here).
- `nwtn-src-cpp-code-navigation` skill (`clangd_query.py`) — unavailable on this Windows host. The skill mandates clangd navigation **only for modules under `nwtn/src`**; this snapshot is CTS (not `nwtn/src`), so the mandatory-clangd rule does not strictly apply. Triage used text-based type resolution and marked candidates `UNRESOLVED` where a declared type/comparator/wrapper could not be resolved from available source (no inference).
- `p4-code-ownership` (Stage 4b), `mgrep`/`mgrep-agent`, `icc2query` — not used: this is a **local** snapshot (rg backend, not a P4 branch), and ownership/app-option enrichment is not part of Stage 1.

### Runtime tooling actually used

- **Python:** `C:\Users\carys\.local\bin\python3.12.exe` (CPython 3.12.14, uv-managed). The Windows Store `python`/`python3` shims are non-functional stubs.
- **PyYAML:** not present in the base interpreter. Installed **run-local** via `pip install --target nd-eval-iter2\.vendor pyyaml` (PyYAML 6.0.3) and placed on `PYTHONPATH` only for the scanner invocation — chosen over a global install to avoid mutating host tooling state.
- **ripgrep:** Cursor-bundled `rg.exe` 15.1.0-cursor5 (auto-detected by `scan_nd.py`).

### Scanner invocation (exact)

```
PYTHONPATH=<repo>\nd-eval-iter2\.vendor \
C:\Users\carys\.local\bin\python3.12.exe C:\Users\carys\cts\scan_nd.py \
  --path "." \
  --patterns "C:\Users\carys\.cursor\skills\nd-code-analyzer\references\nd-patterns.yaml" \
  --tier all \
  --out ".\nd-eval-iter2\raw\candidates.json" -v
```

- Exit code 0. **3673 raw candidates across 27 patterns**, 588 distinct files.
- **Scope limit — max-per-pattern cap:** the customer default `--max-per-pattern 500` was preserved. Patterns **1.2, 1.3, 3.3, 3.4, 3.6** each hit the 500 cap, so their true raw counts are higher than reported. This is the customer scanner's default behavior; it was not overridden (to preserve provenance fidelity). Recorded here as a known recall limit.

## Model / thinking / subagent configuration (as observed)

- **Parent model:** Claude Opus 4.8 (as reported by the running environment).
- **Thinking effort:** set per the Iteration-2 run configuration; not independently observable/queryable from within the agent, so recorded as configured-not-agent-observable.
- **Explore SubAgent Model:** **Inherit from Parent** (per run configuration). The 7 Stage-2/3 triage subagents were launched with `model="inherit"`; no model-routing deviation, fallback, or subagent failure was observed.

## CoreStory configuration

- **Scope:** project **ID 10 (`cts-code`)** ONLY. Confirmed via `list_projects` (id 10 = `cts-code`, ingestion completed). Project **9 (`cts-code2`)** was **not** used for any evidence.
- CoreStory participated during discovery via 6 `semantic_search` calls (project 10). See `discovery-readout.md` for questions, results, and expansion outcome.

## Frozen Stage 0+1 outputs

- `run-manifest.md` (this file)
- `candidate-set.md` (+ machine-readable `raw/candidate-set.json`)
- `discovery-readout.md`
- Raw reconstruction artifacts under `raw/`: `candidates.json` (scanner output), `scan_nd.stderr.log`, `slice_S*.json` (per-cluster scanner slices), `triage_S*.json` (per-subagent Stage-2/3 dispositions), `merge_candidates.py` (deterministic merge script), `candidate-set.json`.
