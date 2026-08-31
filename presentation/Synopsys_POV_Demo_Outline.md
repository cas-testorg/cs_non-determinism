# Synopsys POV — Platform Demo Outline

*CoreStory Solutions Engineering · draft demo script for the Synopsys Value Sprint / POV*

Built from the platform-walkthrough segments of prior kickoff demos (Lineage, ServiceChannel, QBurst) and tuned to what Synopsys has told us in discovery. This version preserves the proven demo flow while incorporating what we learned from the nondeterminism evaluation.

---

**Their environment:** 40–50M lines of C/C++ · Fusion Compiler and other products with heavy multithreading · Perforce for version control · C++17 / C++20.

**Their two headline POV success criteria — the demo must visibly serve both:**

1. **Non-determinism investigation** — help engineers find, contextualize, and reason about potential sources of non-deterministic behavior in massively multithreaded C++.
2. **AI token-cost reduction** — evaluate whether feeding agents curated, pre-computed application context can reduce the amount of repository rediscovery and associated token cost in tools like Cursor.

Secondary threads to weave in: false-positive reduction, automated code review, periodic full-codebase scans, IDE integration, and modernization/parallelization/modularization.

**Important positioning:** CoreStory should not be framed as a replacement for a static analyzer or as a tool that has already been proven to find more nondeterminism defects than a capable coding agent. The strongest story supported by the evaluation is that CoreStory provides application-level intelligence that can change and deepen the investigation: subsystem context, execution paths, relationships, downstream significance, and mitigation/rejection reasoning.

---

## Framing before you share your screen (2 min)

Open the same way our best kickoffs did — set the arc before touching the UI:

> "Everything you're about to see is running against an ingested slice of *your* C/C++ codebase, not a toy repository. We'll start by understanding the application, then move into the engineering workflow and show how that same intelligence can help an AI coding agent investigate something particularly difficult in this environment: nondeterminism."

Then connect the demo to the POV goals without over-claiming outcomes:

> "The question we're exploring is not whether CoreStory replaces static analysis. It's whether giving an engineering agent application-level understanding can help it investigate difficult problems across a codebase of this scale without rediscovering the application from scratch every time."

Name-check that CoreStory is IDE- and tool-agnostic (VS Code, IntelliJ, Cursor, CLI) — Synopsys already lives in Cursor.

---

## The demo sequence

The sequence retains the familiar platform walkthrough used in prior demos, but the sections now form one engineering story:

**Understand the application → investigate a hard problem → bring that intelligence into the IDE → evaluate what changed → understand the impact of fixing it.**

### 1. Landing page + Intelligence Layer — "this is your code" (3–4 min)

- **Show:** The landing page with workspaces; open the Synopsys workspace. Briefly show the intelligence model and Living Intelligence / incremental updates.
- **Say:** CoreStory builds and maintains application understanding across the ingested codebase rather than relying on what can fit into an individual model context window.
- **Synopsys tie-in:** A 40–50M-line codebase changes constantly. The useful abstraction is a maintained intelligence layer over the application, not a one-time context dump into an LLM.
- **Keep brief:** Establish source → ingestion → application intelligence → continuously maintained context. Do not turn this into an architecture deep-dive unless the room asks.

### 2. Chat with your code — establish application understanding (3–4 min)

- **Show:** The in-workspace chat. Start with an architectural / execution-path question rather than asking Chat to act as a race detector. Recommended example:
  - "Where are the major multithreaded execution paths in the CCD/skew optimization subsystem, and what shared state do they interact with?"
- **Optional second question:** Ask for a high-level explanation of one of the returned subsystems or flows to show range.
- **Say:** The purpose here is to establish the application context an engineer would normally have to build before investigating a difficult concurrency issue.
- **Synopsys tie-in:** The answer should connect code-level facts to application structure and provide references back into the code. The references make the reasoning traceable.

### 3. Documents — reusable application understanding (2–3 min)

- **Show:** One or two default generated artifacts, then one custom-document example relevant to the POV, such as:
  - "Map the modules using multithreading and the shared/global state each touches."
  - "Extract the concurrency-control patterns used across this subsystem."
- **Say:** The same intelligence used for Q&A can be materialized into reusable engineering knowledge rather than rediscovered in every conversation.
- **Synopsys tie-in:** Useful for architecture comprehension, onboarding, modernization, parallelization, and modularization across a codebase too large for any individual engineer to hold in working memory.
- **Keep brief:** Documents demonstrate persistence and reuse of understanding; they are not the hero moment in this demo.

### 4. MCP in Cursor — the hero workflow (8–10 min)

- **Show:** Cursor connected to CoreStory through MCP. Use the shared-state concurrency investigation (P02-style) as the primary example.
- **Show the behavior, not just the answer:** Let the agent use CoreStory to identify relevant application context, then inspect targeted source and reason about a candidate.
- **Recommended visual flow:**

```text
Engineering question
        ↓
CoreStory application intelligence
        ↓
Relevant subsystem / execution path / relationships
        ↓
Targeted source inspection
        ↓
Candidate
        ↓
Causal reasoning + mitigation check
```

- **Say:** "The interesting part is not that CoreStory replaces the coding agent or a static analyzer. The agent is still doing source-level reasoning. CoreStory gives it application intelligence that helps determine where to investigate and how a suspicious construct fits into the larger system."
- **Synopsys tie-in:** This is where the Intelligence Layer meets the workflow Synopsys already uses. The model can reason from targeted application context instead of beginning every task by independently reconstructing the application.
- **Token-cost positioning:** Do not claim a measured token reduction unless the measurements are available and defensible. Frame token economics as an active POV measurement.

### 5. Controlled comparison — what actually changed? (4–5 min)

- **Show:** A simple comparison artifact or slide from the paired mini-benchmark.
- **State the control clearly:**

> "Same model. Same source. Same prompt. Same rule. The only difference was access to the CoreStory Intelligence Layer."

- **Use P02 as the primary example:**
  - The local-only run found a strong shared-state candidate in the solver log-sum-exp population path and correctly identified mitigations elsewhere.
  - The CoreStory-assisted run found a different config-dependent shared-state candidate involving a component explicitly documented as non-thread-safe, and added application-path context around the path.
- **Be precise about evidence:** These paired mini-benchmark outputs are discovery results, not independently validated findings. The broader evaluation used independent source-based validation separately.
- **Say:** "What we saw was not simply 'CoreStory produces more findings.' The local model was already capable at direct source inspection. What changed was the investigation: CoreStory surfaced different paths in some cases and provided more application context for understanding downstream significance and whether suspicious behavior was mitigated."
- **Primary takeaway:** CoreStory is best positioned here as an **application intelligence layer for the engineering agent**, not as another static defect detector.

### 6. Blast radius / change impact — continue the same workflow (3–4 min)

- **Show:** Take the investigation forward. Starting from a concurrency candidate or shared component, ask what else could be affected by changing it.
- **Example:** "If we change this shared component to address the concurrency problem, what other execution paths, modules, or behaviors could be affected?"
- **Say:** Once an engineer has a credible candidate, the next question is not merely "where is the bug?" but "what is the impact of fixing it?"
- **Synopsys tie-in:** This connects investigation to safe remediation, code review, and production-risk reduction. It also demonstrates where application-level relationships add value beyond the local code around the defect.

### 7. CLI / tool independence — optional (1–2 min)

- **Show:** One short CLI example using the same Intelligence Layer.
- **Say:** "Nothing about this application understanding is tied to Cursor. The same Intelligence Layer can support other MCP-capable IDEs and command-line agents."
- **Synopsys tie-in:** Reinforces that CoreStory follows the engineering workflow rather than requiring the engineering team to adopt one specific interface.

### 8. Security & deployment note — keep available, not central (1–2 min)

- **Show / say:** Reference the single-tenant organization and Azure deployment path already in motion.
- **Synopsys tie-in:** Signal that deployment and security questions are answerable, but keep the live demo focused on engineering value unless the room wants to go deeper.

---

## Close — tie back to the POV (2–3 min)

Restate what was demonstrated versus what is still being measured.

**Demonstrated in the workflow:**

- CoreStory maintains application-level understanding over the ingested codebase.
- That intelligence can be used directly through chat/documents and carried into an engineering agent through MCP.
- In the nondeterminism evaluation, CoreStory changed the investigation by surfacing different candidates in some cases and by adding application-path / downstream context.
- The same intelligence can be used to reason about the blast radius of a proposed remediation.

**Still being measured during the POV:**

- Token consumption / economics relative to the current Cursor workflow.
- Investigation effort and time-to-diagnose.
- Whether application context reduces false-positive investigation effort.
- Runtime confirmation of static nondeterminism candidates where source evidence alone is insufficient.

Recommended closing language:

> "Today we demonstrated that CoreStory can give an engineering agent application-level context for investigating nondeterminism across a very large C/C++ codebase. We also showed how that same understanding carries from exploration into the IDE and then into change-impact analysis. We're continuing to measure the economics of that workflow — particularly token consumption and investigation effort — rather than asking you to take a token-savings claim on faith."

Recommended sprint workflows:

1. Nondeterminism investigation using the application-intelligence + targeted-source workflow.
2. MCP-fed Cursor workflow measured against their current process for token consumption and engineering effort.
3. Blast-radius / code-review workflow on a real proposed change.

---

## Pain-point → demo segment cheat sheet

| Synopsys pain / goal | Demo segment to lean on |
| :---- | :---- |
| Nondeterminism investigation | §2 application understanding, §4 Cursor workflow, §5 controlled comparison |
| High AI token cost (Cursor) | §4 MCP in Cursor; position measurement as part of the POV |
| False positives / engineering effort | §4 mitigation / causal reasoning, §5 controlled comparison |
| Production-risk reduction | §6 blast radius / change impact |
| Automated code review | §6 change impact, §4 IDE integration |
| Periodic full-codebase understanding | §1 Intelligence Layer / Living Intelligence |
| Modernization / parallelization / modularization | §3 reusable docs, §6 impact analysis |
| Security / deployment approval | §8 single-tenant + Azure |

---

## Delivery reminders

- Run the whole thing **against Synopsys's own ingested code** — that is what makes the story credible.
- Avoid presenting CoreStory as a static analyzer or claiming it has already been proven to find more nondeterminism defects than the local model.
- Distinguish **grounded source mechanisms**, **plausible nondeterminism**, and **confirmed runtime nondeterminism**.
- When showing the controlled comparison, explicitly say those outputs are discovery results; do not call them independently validated findings.
- Expect detailed architecture questions (intelligence-model updates, staleness risk); have crisp answers available.
- Keep security light in the live room but clearly answerable.
- Total live-demo core remains ~30–35 min. The Cursor / engineering-agent section should receive the most time.

---

## Future slide-deck cheat sheet

When this outline stabilizes, create a compact presenter deck rather than duplicating the full script. Recommended slides:

1. **POV goals / problem statement** — scale, nondeterminism, engineering-agent context.
2. **Demo journey** — Understand → Investigate → IDE → Compare → Impact.
3. **Intelligence Layer** — maintained application understanding across the codebase.
4. **Engineering-agent workflow** — the MCP investigation flow diagram.
5. **Controlled comparison** — same model/source/prompt/rule; CoreStory access is the variable.
6. **P02 example** — local and CoreStory-assisted investigations, emphasizing different paths and contextualization rather than raw finding count.
7. **From finding to remediation** — blast radius / change-impact continuation.
8. **What we demonstrated vs. what we are measuring** — keep claims explicit and defensible.
9. **POV next steps / success metrics** — token economics, investigation effort, false-positive effort, runtime confirmation.

The deck should function as a presenter cheat sheet: minimal text on-screen, concise spoken lead-ins, key proof points, and transition lines back to the live product.