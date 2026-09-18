# 02. Synopsys Current Non-Determinism Process

## Why the baseline matters

The existing Synopsys workflow is not a generic LLM prompt over a repository. It is a specialized ND analysis process with domain-specific knowledge encoded into skills, references, scripts, examples, and proof stages.

That makes the evaluation a test of incremental value against a mature workflow.

## Discovery authority

The customer nd-code-analyzer skill is the primary broad-discovery workflow. Its staged artifacts include SKILL.md, nd-patterns.md, nd-patterns.yaml, scan_nd.py, render_report.py, and report_template.md.

The YAML is the scanner source of truth. The final controlled run verified the expected Git blob fingerprints before measured discovery.

The scanner loaded **27 pattern families**. They cover pointer ordering, pointer-keyed maps and sets, unordered containers, pointer hashing, RNG behavior, time/PID seeding, naming and ordering patterns, pointer arithmetic, parallel floating-point reduction, thread-count dependence, project wrapper containers, and multithreaded patterns such as lazy cache behavior, concurrent map check-then-act, lost wakeups, and address-keyed lock striping.

## Discovery and triage flow

The process is:

**27-pattern mechanical scan → candidate population → pattern-specific narrowing → semantic review and false-positive guidance → parallel Explore triage when threshold is met → downstream observability reasoning → retained candidate set**

The skill explicitly states that a regex hit is not a real ND defect. It distinguishes real findings from latent-only behavior, false positives, dead or unused paths, safe adopters, mirror duplicates, and neutralized behavior.

The workflow also contains project-specific semantic guidance. Project wrapper containers such as dosUnorderedMap, dosUnorderedSet, dosHash, nwcInsOrdMap, and related pointer types are called out for semantic inspection rather than classification by container name alone.

## Subagent behavior

The discovery skill permits and expects parallel Explore subagents when the candidate population is sufficiently large. The configured threshold is reached at 50 or more candidate files or 5 or more subdirectories.

The final controlled run had 588 candidate files across 21 top-level source directories. Seven Explore subagents were dispatched and completed.

This matters because earlier experiments that did not preserve this topology were not faithful reproductions of the customer discovery process.

## Mechanism proof

After discovery, the customer has dedicated prove-nd and prove-nd-mt workflows for deeper proof.

These stages are different from broad discovery. Their role is to establish the exact ND mechanism, required varying input or state, source evidence, and reasons a candidate should be proved, rejected, or left unresolved.

Unlike broad discovery, these proof workflows explicitly prohibit subagents.

## Downstream observability

The discovery skill already performs more than local pattern matching. Its semantic review includes downstream observability concepts such as source mechanism, caller and callee behavior, observable sink, neutralizers, controls and gating, application options, regression setters, and reference-client behavior where available.

This is important to the CoreStory positioning. CoreStory should not be described as introducing the concept of observability or qualification for the first time. Synopsys already has substantial capability here.

The potential differentiation is narrower: persistent application intelligence may make application-wide evidence easier to establish, especially build reality, broader reachability, cross-module relationships, caller-by-caller preservation or neutralization, configuration context, blast radius, and evidence that is expensive to reconstruct repeatedly.

## SME role

Automated analysis is not the final authority. Findings ultimately require engineering judgment, and some mechanisms require runtime evidence.

A mechanical candidate is not the same thing as a source-substantiated mechanism. A source-substantiated mechanism is not automatically an application-relevant issue. An application-relevant issue is not automatically a runtime-reproduced defect or SME-validated engineering finding.

## Economic characteristic of the process

The process can involve thousands of mechanical candidates, multiple rounds of narrowing, parallel model work, repeated source inspection, mechanism proof, and SME review.

That creates a separate economics question. Even if CoreStory does not improve initial discovery, persistent application context may have value if it reduces repeated reconstruction of application relationships or reduces the amount of evidence an SME must reconstruct manually.

No cost-saving claim is made yet. This is a measurement target for the next stage.
