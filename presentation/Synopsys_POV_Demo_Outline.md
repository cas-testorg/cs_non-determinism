# Synopsys POV — Platform Demo Outline

*CoreStory Solutions Engineering · draft demo script for the Synopsys Value Sprint / POV*

Built from the platform-walkthrough segments of prior kickoff demos (Lineage, ServiceChannel, QBurst) and tuned to what Synopsys has told us in discovery.

---

**Their environment:** 40–50M lines of C/C++ · Fusion Compiler and other products with heavy multithreading · Perforce for version control · C++17 / C++20.

**Their two headline POV success criteria — the demo must visibly serve both:**

1. **Non-determinism detection** — find and reason about sources of non-deterministic behavior in massively multithreaded C++.  
2. **AI token-cost reduction** — cut the token burn (and false positives) they're seeing from tools like Cursor by feeding agents curated, pre-computed context instead of re-reading the codebase.

Secondary threads to weave in: automated code review, periodic full-codebase scans, IDE integration, and modernization/parallelization/modularization.

---

## Framing before you share your screen (2–3 min)

Open the same way our best kickoffs did — set the arc before touching the UI:

> "Everything you're about to see is running against an ingested slice of *your* C/C++ codebase, not a toy repo. We'll move through how the intelligence layer understands the code, how your team asks questions of it, and — the part most relevant to your success criteria — how that same intelligence feeds your IDE and agents so you spend fewer tokens and chase fewer false positives, and how it helps you reason about non-determinism."

State explicitly that this maps to the two success criteria you aligned on. Name-check that CoreStory is IDE- and tool-agnostic (VS Code, IntelliJ, Cursor, CLI) — Synopsys already lives in Cursor.

---

## The demo sequence

This is the proven order from prior demos, re-pointed at Synopsys pain. Each segment lists **what to show**, **the talk track**, and **the Synopsys tie-in**.

### 1\. Landing page & workspaces — "this is your code" (2 min)

- **Show:** The landing page with workspaces; explain a workspace ≈ a repository, and multiple repos can be combined. Open the Synopsys workspace.  
- **Say:** Point out this is their ingested codebase, queryable across projects.  
- **Synopsys tie-in:** Acknowledge scale up front — 40–50M LOC — and that CoreStory is built to hold that much context. Note Perforce works as the source; confirm the ingested scope for the POV.

### 2\. Intelligence store & Living Intelligence — "it stays current" (4 min)

- **Show:** The intelligence model over the ingested code; then Living Intelligence — incremental updates when code changes, no full re-run.  
- **Say:** The platform maintains an always-current understanding; changes trigger incremental updates rather than reprocessing everything.  
- **Synopsys tie-in:** A 40–50M-line codebase changes constantly. Incremental updates \= the intelligence keeps pace with active development, and periodic full-codebase scans stay affordable. (Expect Kai Wang–style questions on update mechanism and the risk of operating on a stale model — the ServiceChannel team probed exactly this, so be ready with the architecture answer.)

### 3\. Chat with your code — lead with a non-determinism question (5–6 min)

- **Show:** The in-workspace chat. Ask a real question against their code. This is where you hit success criterion \#1 head-on. Examples:  
  - "Where in this module could multithreaded execution produce non-deterministic results?"  
  - "What shared state is accessed without synchronization in ?"  
  - A non-technical framing too (like the feature-flag / "how taxes work" questions in prior demos) to show range: "Give me a high-level explanation of how works."  
- **Say:** Short answer \+ background notes \+ **references back into the code**. The references are the point — every claim is traceable.  
- **Synopsys tie-in:** This is the non-determinism story made concrete. Emphasize the answer is grounded in *their* code with citations, which is how you cut false positives.

### 4\. Documents — comprehension & extraction at scale (5 min)

- **Show:** The Documents section and its default artifacts — executive overview, technical user stories with business rules, class diagrams, UML, sequence diagrams. Show export (mermaid/UML). Then create a **custom document** targeted at their world, e.g.:  
  - "Map the modules using multithreading and the shared/global state each touches."  
  - "Extract the concurrency-control patterns used across ."  
- **Say:** Default docs give instant high-level understanding; custom docs extract exactly the business/technical rules you care about from a large codebase.  
- **Synopsys tie-in:** Feeds modernization, parallelization, and modularization — the forward-looking use cases. Custom-doc extraction across 40–50M LOC is comprehension no one on the team can do by hand.

### 5\. Deep analysis — blast radius & gap analysis (5 min)

- **Show:** Generate a **blast radius** report for a proposed change (prior demos used "add Google SSO" — pick a Synopsys-relevant change, e.g., altering a shared scheduling/threading utility) and a **gap analysis**.  
- **Say:** Before you touch code, see everything a change would ripple into; surface gaps between code and its documented behavior.  
- **Synopsys tie-in:** Directly reduces production risk and powers automated code review. Be ready for "how is this different from GitHub Copilot's output?" — ServiceChannel's Adam Wendt asked exactly that. Answer: CoreStory supplies whole-codebase, referenced context, not a local guess.

### 6\. MCP in the IDE — the hero moment for token savings (6–7 min)

- **Show:** Connect the MCP token (show how easy the settings are), then use CoreStory's MCP inside **VS Code and/or Cursor**. Ask the agent a question that would normally make it crawl the repo, and show it pulling curated context from CoreStory instead. Show the **CLI/terminal** path too for flexibility (Augment, etc.).  
- **Say:** The agent gets pre-computed, precise context instead of re-reading millions of lines — fewer tokens, fewer false positives, better answers.  
- **Synopsys tie-in:** This is success criterion \#2 made visible. If possible, contrast a "cold" agent query vs. an MCP-fed one to make the token delta tangible. This is the single most important segment for Synopsys — give it room.

### 7\. Security & deployment note — for Raymond Lee / Fadi Maamari (2–3 min)

- **Show / say:** The MCP token creation for their **single-tenant** org; reference the Azure deployment path already in motion.  
- **Synopsys tie-in:** Pre-empt the security/deployment blockers that gate the MSA. Keep it brief in the live demo but signal you have answers and can go deep offline with Raymond.

---

## Close — tie back to the POV (3 min)

- Restate the two success criteria and point to the exact moments in the demo that served each (chat/analysis for non-determinism; MCP-in-IDE for token savings).  
- Confirm the 1–3 workflows to run in the sprint. Recommended for Synopsys: **(a) non-determinism investigation via chat \+ custom analysis, (b) MCP-fed IDE workflow measured against their current Cursor token spend, (c) blast-radius/code-review on a real change.**  
- Set baseline metrics to beat: current token spend per task, current time-to-diagnose a non-determinism issue, current false-positive rate.  
- Confirm cadence (two \~1-hour working sessions/week, lean team of 5–7), tooling, primary point of contact, and the closing value report.

---

## Pain-point → feature cheat sheet

| Synopsys pain / goal | Demo segment to lean on |
| :---- | :---- |
| Non-determinism detection | §3 chat (targeted questions), §4 custom docs, §5 analysis |
| High AI token cost (Cursor) | §6 MCP in IDE (hero) |
| False positives / engineering effort | §3 referenced answers, §6 curated context |
| Production-risk reduction | §5 blast radius \+ gap analysis |
| Automated code review | §5 analysis, §6 IDE integration |
| Periodic full-codebase scans | §2 Living Intelligence |
| Modernization / parallelization / modularization | §4 custom docs, §5 analysis |
| Security / deployment approval | §7 single-tenant \+ Azure |

---

## Delivery reminders (from prior kickoffs)

- Run the whole thing **against Synopsys's own ingested code** — that's what made the Lineage and ServiceChannel demos land.  
- Expect detailed architecture questions (intelligence-model updates, staleness risk) — the technical R\&D directors will probe. Have crisp answers.  
- Keep security light in the live room but clearly answerable; take the deep security review offline with Raymond Lee.  
- Total live-demo core is \~30–35 min; expand or trim §4/§5 depending on time and audience seniority.

