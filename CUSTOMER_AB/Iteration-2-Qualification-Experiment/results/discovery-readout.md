# CTS ND Discovery — Readout (Stage 1, frozen)

Run: 2026-09-18 (America/Chicago). Model: Claude Opus 4.8, extended thinking (high). Authority: `nd-code-analyzer` v1.4.0 (SHA-verified refs). Rule: `corestory-nd-discovery.mdc`. CoreStory: project 10 `cts-code` only. See `run-manifest.md`, `candidate-set.md`.

## 1. Total frozen candidates
**21** stable candidate IDs (`ND-CAND-001`…`ND-CAND-021`): 11 individual + 2 CoreStory-surfaced paths + 8 recall-preserving cluster candidates. Frozen before proof/qualification.

## 2. Candidates from customer pattern/reference discovery
**18** candidates surfaced through the customer mechanical scan / reference method:
- Individual: 001, 002, 003(also CoreStory), 004, 005, 006, 007, 008, 009, 013.
- Clusters: 014, 015, 016, 017, 018, 019, 020, 021.

Pattern coverage actually exercised (raw hits, mirror-inflated): 1.1=404, 1.2=2955, 1.3=531, 1.4=16, 1.5=34, 2.1=2, 2.2=100, 2.4=17, 2.5=17, 2.6=8, 3.1=2, 3.2=203, 3.5=3, 3.6=557, 3.7=288, 4.1=2, 4.2=40, 4.4=36. Zero-hit: 2.3, 2.7, 2.8, 2.9, 4.3, 4.5, 4.6.

## 3. Candidates added through CoreStory expansion
**3** first surfaced by CoreStory (project 10), plus **1 BOTH**:
- **ND-CAND-010** (`ctsICGEstimators.h` toggled "may cause ND" pointer map) — **the mechanical scan could not have caught it**: key is smart-pointer wrapper `ndmPointer<const ndmType>` with no literal `*`, so YAML 1.2 regex does not match. Pure CoreStory-expansion gain.
- **ND-CAND-011** (`fmaxTimingCostFunction.h` thread-count-partitioned TNS/WNS reduction) — surfaced via CoreStory Q3.
- **ND-CAND-012** (`msgtsClustering.cc` sibling clustering engine) — surfaced via CoreStory Q2 as an alternate implementation to scan.
- **ND-CAND-003** (`msClustering` unseeded RNG) — **BOTH**: decl found by customer pattern 1.5; CoreStory added the downstream-observability path (RNG → centroid selection → tap-tree topology).

## 4. Candidates where CoreStory materially broadened evidence/path
**4**: 003 (RNG→topology observable, caller `msTapSynthesis`), 010 (new candidate + "may cause ND" author intent), 011 (new candidate + partition/merge structure), 012 (new sibling path). CoreStory also supplied **contrary/neutralizer evidence** retained for qualification (not used to delete): 006 (`processSccBagIntoCache` "deterministically assembles"), 007 (`ctoGrpLatCalc` per-index independent writes + commutative max).

## 5. CoreStory calls/purposes that produced no useful expansion
- **Q1** (`dosUnorderedSet` pointer-key hash semantics + iteration consumers): did **not** resolve the external `dos*` wrapper hash implementation (not indexed in project 10). Returned CTS-side conversion helpers (`ctsObjId`) and the `ctsICGEstimators` map (useful for 010) but left **ND-CAND-013 semantics UNRESOLVED**. Net: partially useful (010) but failed its primary purpose (wrapper resolution).

Total CoreStory calls this stage: **3** (`semantic_search`, project 10) + 1 `list_projects` (scope confirmation). All read-only. No project-9 (`cts-code2`) or other-project evidence used.

## 6. Unavailable evidence or tooling
- `scan_nd.py`, `render_report.py` — **UNAVAILABLE**; Stage-1 reproduced with ripgrep over the SHA-verified YAML (source of truth). Enumeration faithful.
- `references/fix-recipes.md`, `id-system.md`, `assets/example_report.md`, `p4-code-ownership`, `nwtn-src-cpp-code-navigation` — **UNAVAILABLE** (do not affect discovery recall; ownership/fixes are post-discovery, clangd rule is `nwtn/src`-scoped and this module is CTS).
- External `dos*` / `ndm*` library internals (`dosUnorderedSet` hash, `compareNdmPointer`, `ndmPtrUnorderedMap`, `stateType.reduce`) — **UNRESOLVED** in both local tree and project-10 index; load-bearing for ND-CAND-010, 011, 013, 006.
- No git/P4 metadata at workspace root → snapshot identified by path + timestamp; no commit SHA.

## 7. Subagent / model topology actually used
- **Single-agent, no subagents**, all stages (verification, mechanical scan, triage, CoreStory expansion, freeze). Model: Claude Opus 4.8, extended thinking (high).
- **Deliberate deviation** from the SKILL's "parallel `explore` subagents for ≥50 files / ≥5 subdirs" guidance (CTS = 2,391 files / 22 dirs would normally trigger it). Rationale: keep the **CoreStory project-10-only scope constraint** and the **provenance ledger** centrally controlled — parallel subagents each issuing CoreStory calls would risk cross-project scope drift and fragment provenance. The full mechanical scan was retained and triaged, so **no candidate was dropped** by this choice; recall is preserved via enumerated cluster candidates.
- Preserved customer discovery behavior: pattern-specific narrowing (1.1 value-type dismissal, 1.2/1.3 comparator/hash + membership-only auto-dismiss, 3.3 iterated-type check), safe-adopter/mirror-duplicate/neutralized realness classes, and downstream-observability reasoning were all applied — but only to **classify**, never to remove a discovered candidate.

## 8. Method integrity notes
- Reference set SHA-verified identical to the required fingerprint (Stage 0, all 3 ✅).
- No prior A/B reports, prior AI findings, benchmark conclusions, or held-out TSan/Coverity ground truth were consulted.
- No source code modified. Raw scan outputs preserved under `nd-eval-final/raw/`.
