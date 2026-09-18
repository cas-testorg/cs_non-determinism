# Discovery Readout — Iteration 2, Stage 1 (FROZEN)

This is the final discovery-focused iteration. Evidence is preserved regardless of outcome; the rule/prompt/scripts/reference set/orchestration were **not** tuned in response to observed results.

## Headline counts

| Metric | Value |
|---|---|
| Raw scanner candidates (customer `scan_nd.py`, 27 patterns) | **3673** across 588 files |
| **Total FROZEN Stage-1 candidates** | **334** |
| Candidates originating from customer pattern/reference discovery (`CUSTOMER-PATTERN`) | **334 (100%)** |
| Candidates added through CoreStory expansion (`CORESTORY-EXPANSION`) | **0** |
| Candidates independently surfaced by both (`BOTH`) | 0 |
| Candidates where CoreStory materially broadened the evidence/path | **0** |
| Dismissed at Stage 2/3 (grouped regex/false-positive buckets, counts preserved) | 3331 in 87 buckets |

Reconciliation: 334 retained + 3331 dismissed = 3665; remaining ≈8 are same-site cross-pattern duplicates de-duplicated within slices (notably S7 reported 107 raw → 103 unique). All raw hits are accounted for in either `candidate-set.md` retained rows or dismissed buckets.

### Retained candidates by discovery-time realness hypothesis

Per the `corestory-nd-discovery` rule, latent-only / UNRESOLVED candidates are **retained** for later proof/qualification and are **not** removed for incomplete downstream evidence.

| Realness (hypothesis) | Count |
|---|---|
| real | 2 |
| latent-only | 282 |
| UNRESOLVED (type/comparator/wrapper unresolved from available source) | 25 |
| mirror-duplicate (header/#include mirror of another retained candidate) | 25 |

### Retained candidates by customer pattern family

| Pattern | Count | Pattern | Count |
|---|---|---|---|
| 1.1 pointer sort | 17 | 2.6 filesystem iteration | 5 |
| 1.2 pointer set/map | 32 | 3.1 parallel float reduction | 1 |
| 1.3 pointer unordered_* | 122 | 3.2 MT shared-container writes | 8 |
| 1.4 pointer hash functor | 16 | 3.3 unordered iteration | 1 |
| 1.5 random w/o det. seed | 32 | 3.4 operator[] side-effect | 6 |
| 2.1 time/pid RNG seed | 2 | 3.5 thread-count dependency | 3 |
| 2.2 name-as-key | 24 | 3.6 post-collection ordering | 44 |
| 2.5 unique after ND sort | 1 | 3.7 project wrapper containers | 13 |
| | | 4.1 lazy dirty-bit const getter | 2 |
| | | 4.4 concurrent_hash_map check-then-act | 5 |

The 2 discovery-time `real` candidates: `ctsui/ctsuiCreateClockBuffer.cc:783` and `:800` (`std::sort(refModuleVec, sortByArea)` with no id tie-break, then median pick drives buffer-module selection). All others are latent-only/UNRESOLVED/mirror pending Stage 2/3.

## Scanner / script execution actually used

- Customer `scan_nd.py` (CTS-root copy, git-blob `451eb197…`, manifest-matching) executed with CPython 3.12.14 + run-local vendored PyYAML 6.0.3, reading the manifest-matching skill-dir `nd-patterns.yaml` (git-blob `6fd5cf24…`), ripgrep backend (Cursor-bundled rg 15.1.0-cursor5). Exit 0, 3673 candidates / 27 patterns. Verbose log: `raw/scan_nd.stderr.log`.
- No emulated/ad-hoc scanner was substituted. `render_report.py` was not run (Stage 1 stops before reporting).
- Known recall limit: default `--max-per-pattern 500` capped patterns 1.2/1.3/3.3/3.4/3.6 at 500 raw hits each (true counts higher); customer default preserved.

## Subagent / model topology actually used

- The skill's Stage-2 parallelization threshold (**≥50 candidate files OR ≥5 sub-directories**) was **triggered** (588 files, 21 top-level dirs).
- Subagents **were** created: **7 `explore` subagents**, one per directory cluster, `model="inherit"` (Explore SubAgent Model = Inherit from Parent). All completed; **no** failure, fallback, or model-routing deviation.
- `prove-nd`/`prove-nd-mt` subagent restriction is **not** applicable to Stage 1 (those run in Stage 2).

| Subagent | Scope (dirs) | Raw hits | Retained | Dismissed | Agent ID |
|---|---|---|---|---|---|
| S1 | mscts | 1086 | 58 | 1028 | 99aa6fb7-fb15-45ff-8574-4d47b4f79c98 |
| S2 | ccd | 793 | 19 | 769 | 330c3bd4-179d-4bab-a7dd-75fd2707d1a8 |
| S3 | ctscto | 623 | 12 | 611 | b7930ec6-e005-4723-bd17-a3f527b86bf4 |
| S4 | ctssc, ctsmisc, ctssch, ctscstr | 428 | 14 | 414 | 1de6984d-df78-4c39-96ae-a893c5930028 |
| S5 | ctsutil, include, ctsinterf, export | 398 | 187 | 211 | 68d6961b-5ec9-4b18-a1e6-0fd5c95331f9 |
| S6 | rlx, ctsrpt, icg, ips, irs | 238 | 8 | 230 | 1db6d75d-e038-43e5-b0b5-bf5164a11cda |
| S7 | cts, ctsui, skewgrp, ctssplit, ctsroute | 107 | 36 | 67 | 28fc1ee0-cabd-45ff-8068-6cc9cb319725 |

**Data note (S2):** the S2 subagent's inline message listed 24 retained rows including 5 `ccd/include/soLogicCone.h` mirror-duplicate rows; its persisted on-disk artifact `raw/triage_S2_ccd.json` contains 19. The on-disk artifacts are treated as canonical for the frozen set (334 total). The 5 delta rows are mirror-duplicates of retained `ccd/skewopt/soLogicCone.h` sites, already represented.

## CoreStory discovery expansion — calls, purposes, and outcome

CoreStory (project 10 `cts-code`) was invoked during discovery via 6 `semantic_search` queries. **Outcome: CoreStory did not materially expand useful candidate discovery for this snapshot.** This is recorded as a direct result, not forced toward a discovery-value conclusion.

Root cause: the project-10 index contains **only the CTS module source already scanned by the customer patterns**. The load-bearing semantics needed to resolve the UNRESOLVED candidates (implementations of `dosUnorderedSet`/`dosUnorderedMap`, `ndmObjectHandleNS::compareObjPtr`/`ndmObjPtrCmpType`, `nwcInsOrdMap`, `cstrClock::operator<`, `ndmShapePtrComparator`, `ctsModuleCompare` upstream) live in **un-ingested upstream libraries** (nwtn/dos/ndm) and appear in the index only as `#include`/typedef references. Every chunk CoreStory returned was a file already inside the customer scan's coverage.

| CoreStory call | Question / purpose | Returned relationship / evidence | Useful expansion? |
|---|---|---|---|
| semantic_search #1 | Resolve `dosUnorderedSet`/`dosUnorderedMap` wrapper hash/iteration-order semantics | Only in-module *uses* + `export/ctsTypes.h` safe pointer comparator/hash functors + `msDrivers.cc setMap` (uses `ndmObjPtrCmpType`); wrapper implementation NOT in index | No — impl un-ingested; UNRESOLVED remains UNRESOLVED |
| semantic_search #2 | Resolve `ctsModuleCompare` ordering (id-stable vs address) | Surfaced in-module LEQ comparators (`ctsRefLEQ.cc`, `msLibCell.cc` context compares by ids/function-class) — corroborates that in-module comparators are id/value-based, but the specific `ctsModuleCompare` used by the S1 UNRESOLVED site was not definitively resolved | No new candidate; partial corroboration only |
| semantic_search #3 | Find consumers that iterate the endpoint delay-potential `unordered_map<ndmTerm*,float>` order-sensitively | `soPredictiveCcd.cc` consumers operate over a separately-collected `std::vector<grNode> validEps`, not by iterating the pointer-keyed map — weak evidence the map is consumed order-insensitively | No new candidate; corroborating context for later stages |
| semantic_search #4 | Resolve `nwcInsOrdMap` insertion-order semantics + polarity-solution iteration | `msgtsClustering.cc` confirms nwcInsOrdMap use ("polarity solutions indexed by topology, module ref, boolean") — corroborates the S1 retained candidate, but nwcInsOrdMap impl not in index | No — corroborates an already-retained candidate; impl UNRESOLVED |
| semantic_search #5 | Find design/DB mutations ordered by unordered/pointer-container iteration (downstream ND sink) | Returned buffer-insertion/netlist files (`ctsNL.cc`, `msDrivers.cc`, `ctsBuffer.cc`, `bgtBufferCri.cc`) already in scan scope; no new site, no proof of unordered-iteration-driven mutation surfaced | No |
| semantic_search #6 | Find first-match selection while iterating an unordered/hash container | Returned already-covered files (`msDrivers.cc setMap` — ordered/stable; `ctsCharacterizer.cc`; `ctsLazyTnsTypeDef.h` — value-keyed) | No |

**Net CoreStory contribution to discovery:** 0 new candidates, 0 materially-broadened paths. Corroborating-only context on 3 already-retained candidates (nwcInsOrdMap use; in-module id-based comparators; endpoint-map consumer shape). One incidentally-corroborated ND-aware design element: `icg/ctsICGEstimators.h` template lets callers pick a "may cause ND" std::map vs "not cause ND" unordered_map via `useNonNdMapType` (already handled in triage as a safe-adopter). No candidate was removed by CoreStory (rule-compliant).

## Unavailable evidence / tooling (discovery-limiting)

- clangd / `nwtn-src-cpp-code-navigation` unavailable → 25 candidates left `UNRESOLVED` (types/comparators/wrappers unresolved from available source; no inference).
- Upstream wrapper/comparator/library implementations not in the project-10 index and not in the local snapshot → semantics for `dosUnordered*`, `nwcInsOrdMap`, `ndmObjectHandleNS::compareObjPtr`, `cstrClock::operator<`, `ndmShapePtrComparator` cannot be confirmed at discovery time.
- `references/fix-recipes.md`, `references/id-system.md`, `assets/example_report.md` absent (not needed for discovery).
- `--max-per-pattern 500` cap on 5 high-volume patterns (recall limit; customer default retained).

## Stage 1 decision gate

Candidate set frozen at **334**. All discovery evidence preserved under `raw/`. No tuning performed in response to results. **STOP** — Stage 2 (mechanism proof) not started.
