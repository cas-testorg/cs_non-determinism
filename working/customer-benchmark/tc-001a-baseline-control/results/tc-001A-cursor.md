# Code analysis report generation
_Exported on 9/9/2026 at 14:12:28 CDT from Cursor (3.18.25)_

---

**User**

/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report

---

**Cursor**

I'll follow the ND code analyzer skill and scan `C:\Users\carys\cts` for HIGH and MEDIUM issues, then produce a shareable markdown report.

Running Stage 1 mechanical scan with severity floor MEDIUM, then I'll triage and render the report.

Scanner scripts aren't in the skill install — I'll drive Stage 1 from the pattern YAML with ripgrep, then triage and render the report.

I'll build a Stage 1 scanner from the pattern YAML (scripts aren't installed) and scan HIGH/MEDIUM patterns across the CTS tree.

Building a PowerShell Stage 1 scanner from the YAML and running HIGH/MEDIUM pattern searches across the CTS tree.

4535 raw hits — narrowing high-volume patterns, then parallel triage of the HIGH/MEDIUM signal set.

Launching parallel triage on narrowed packs and deep-reading the highest-signal, low-count patterns myself.

Subagent type fixed — relaunching triage and deep-reading the strongest candidates.

Verifying the HIGH finding and assembling the final findings + report.

Assembling `findings.json` and rendering the HIGH/MEDIUM markdown report.

**1 HIGH + 6 MEDIUM** real ND issues in `C:\Users\carys\cts` (LOW omitted). Stage-1 found 4535 candidates; most were membership-only, safe adopters, test/debug, or latent MT.

**Shareable report:** [C:\Users\carys\.cursor\plans\nd_analysis_cts_20260909.md](file:///C:/Users/carys/.cursor/plans/nd_analysis_cts_20260909.md)  
**Structured data:** [C:\Users\carys\.cursor\plans\nd_cts_findings.json](file:///C:/Users/carys/.cursor/plans/nd_cts_findings.json)

| Sev | Location | Issue |
|---|---|---|
| HIGH | `ctscto/ctoFlowClone.cc:1884` | Address-ordered `std::set<ndmTerm*>` drives clone/shield (+ early-break quota) |
| MED | `mscts/mstap/msTapSubtreeSyn.cc:285`, `:805` | Distance-only sort ties → repeater/cluster choice |
| MED | `ctoscLoadPartition.cc:136`, `ctomtReloc.cc:868/882`, `ctoUtil.cc:4384` | Equal-delay min/max ties → partition/relocation QoR |

Perforce ownership was skipped (no `p4` client). Skill scripts (`scan_nd.py` / `render_report.py`) were missing, so Stage-1 used rg + YAML patterns and the report was rendered from `findings.json`.

