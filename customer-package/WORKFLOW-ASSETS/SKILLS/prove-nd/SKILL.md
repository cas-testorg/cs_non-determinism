# Prove ND — Evaluation Snapshot

**Owner:** Synopsys  
**Source skill name:** `prove-nd`  
**Source blob:** `23dd701095a49cc0f182d5d83f0e263fd2ccceb8`

> This customer-package copy preserves the operative instructions relevant to the evaluation. Internal absolute tool paths, supporting references, ownership tooling, and environment-specific navigation details are not reproduced.

## Objective

Turn ND suspects into a proof report. The goal is not to restate a scanner result; it is to prove whether downstream C++ can observe nondeterministic behavior or explain why the candidate is not a real issue.

## Hard Rules

- **Do not use sub-tasks or sub-agents for this task.**
- Preserve source/dashboard order when reviewing supplied suspects.
- Do not call a row real unless a downstream C++ consumer can observe it.
- Do not treat coverage or static-analysis annotations alone as proof that code is dead, unreachable, safe, or compiled out.
- Use actual compile-time controls, build inclusion, call-graph reachability, and feature/runtime gates for dead/unused claims.

## Proof Workflow

For each issue:

1. Read the suspect source around the flagged location.
2. Resolve the actual C++ type of the iterated/indexed/sorted object.
3. Trace upstream reachability from a relevant entry point or caller.
4. Trace downstream consumers to a concrete observable sink.
5. Look for deterministic neutralizers or reasons the candidate is non-real.
6. Classify realness.
7. Trace relevant controls/gates.
8. Record specific evidence and any missing proof.

## Realness Labels

- **Real** — downstream C++ can observe the nondeterministic order/value.
- **Latent-only** — suspect exists but current consumers are order-insensitive.
- **False positive** — scanner matched the wrong type or construct.
- **Safe adopter** — deterministic comparator/container already used.
- **Mirror duplicate** — duplicate/mirror of another row.
- **Neutralized** — nondeterminism is canonicalized before consumption.
- **Dead/unused** — inactive code, no reachable caller, or not compiled.
- **Unresolved** — evidence is insufficient; state exactly what is missing.

## Observable Sinks

Examples of acceptable downstream proof include:

- database/design mutation;
- `set*`, `remove*`, or reorder operations;
- algorithmic tie-breaks;
- report or recording order;
- message order;
- persisted output;
- QoR choice;
- non-associative floating-point reduction.

## Neutralizers

Investigations should explicitly look for mechanisms such as:

- deterministic/stable sorting;
- stable comparators;
- lookup-only or membership-only use;
- order-independent set union;
- vector/index iteration;
- inactive compile-time paths;
- deterministic canonicalization before the observable boundary.

## Controls / Gating

For real or potentially real issues, identify the commands, modes, C++ guards, app options, defaults, and data conditions needed to activate or avoid the path.

Distinguish test/regression configuration from production defaults or production-forced behavior.

## Performance-Aware Fix Direction

Do not recommend deterministic fixes that blindly replace hash containers with ordered maps, add per-iteration sorting, or copy large containers in hot loops without discussing cost.

Prefer preserving lookup complexity and canonicalizing only where ordering becomes observable, using stable keys/comparators, cached deterministic order, or boundary-level sorting where appropriate.

## Reporting Requirement

A proof report should make clear:

- verdict / realness;
- concise source evidence;
- downstream visibility;
- controls and gating;
- reachability/build evidence where relevant;
- attribution when available;
- fix direction and performance implications;
- verification limitations and unresolved evidence.

## Orchestration Note

Unlike `nd-code-analyzer`, which explicitly permits parallel exploration during large repository-scale triage, this skill explicitly prohibits sub-tasks/sub-agents during proof.

For evaluation analysis, subagent activity should therefore be attributed to the workflow stage in which it occurred rather than treated as a single global client behavior.
