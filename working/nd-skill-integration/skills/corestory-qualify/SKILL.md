---
name: corestory-qualify
description: Use CoreStory application intelligence to qualify code-analysis candidates by establishing build inclusion, production reachability, runtime/configuration gates, cross-component relationships, downstream propagation, neutralizers, and observable application impact. Use after another analysis skill has identified a candidate mechanism. Do not replace defect-specific reasoning or classify a suspicious source pattern as a real defect based on CoreStory evidence alone.
---

# CoreStory Qualification

## Purpose

This skill complements defect-specific analysis skills.

The originating skill is responsible for identifying and reasoning about the local defect mechanism. CoreStory is responsible for establishing application context needed to determine whether that mechanism matters in the built application. Targeted source inspection remains authoritative for local code behavior.

This skill is intentionally defect-agnostic. It can be used with nondeterminism, concurrency, undefined-behavior, modernization, or other code-analysis workflows when application-level qualification is needed.

## Hard Rules

- Do not treat a suspicious source pattern as a real defect by itself.
- Do not replace the originating defect-analysis skill.
- Use CoreStory for application-level relationships and context, not facts that are more directly established by reading local source.
- Targeted source inspection establishes the local code mechanism.
- Distinguish direct source evidence, build/configuration evidence, CoreStory relationship evidence, runtime/control-path evidence, and inference.
- Inference must never be presented as direct evidence.
- If required evidence is missing, return `UNRESOLVED` rather than assuming production relevance.
- Do not use prior benchmark reports, previous-run candidate files, prior conversation findings, or held-out reference defects unless they are explicitly supplied for the current phase.
- In controlled evaluations, do not use held-out TSan/Coverity locations during discovery or qualification.
- Do not assign final defect severity independently of the originating skill.

## Qualification Gate

A candidate should not be promoted as a production-relevant defect until the analysis has considered all of the following:

1. **Build inclusion** - Is the relevant file/component included in the applicable production build? Is another implementation used instead?
2. **Production reachability** - Is there a reachable caller, flow entry point, command, or execution path to the suspect code?
3. **Runtime/configuration applicability** - Are required feature flags, app options, data conditions, threading modes, platform conditions, or configuration gates active?
4. **Defect mechanism** - Has the originating skill or targeted source inspection established the actual local mechanism?
5. **Propagation** - Does the suspect value, ordering, lifetime, shared state, or control decision propagate downstream?
6. **No deterministic neutralizer** - Is the behavior not canonicalized, normalized, deterministically re-sorted, replaced by a safe implementation, or otherwise neutralized before observation?
7. **Observable consequence** - Can an application result, persisted state, QoR decision, message/output order, crash, invalid state, or other concrete behavior actually observe the defect?

## Workflow

For each candidate supplied by the originating skill:

### 1. Capture the candidate

Record:

- File and line, when known
- Function/class/component
- Suspected defect mechanism
- Originating skill
- Provisional severity, if any

Do not broaden the search to unrelated defect classes unless the originating workflow requests it.

### 2. Establish build inclusion

Use CoreStory application relationships plus available build/configuration evidence to determine:

- Whether the file/component participates in the relevant production build
- Whether the symbol belongs to a production implementation or an unused/alternate implementation
- Relevant compile-time exclusions, product variants, generated-source substitutions, or module boundaries

If build inclusion cannot be established, record the missing evidence explicitly.

### 3. Establish production reachability

Use CoreStory to identify and narrow:

- Callers and callees
- Entry points
- Execution paths
- Feature/flow dependencies
- Cross-component relationships

Then inspect targeted source where necessary to confirm the actual path.

Do not infer production reachability from symbol existence alone.

### 4. Establish runtime/configuration applicability

Identify controls required for the suspect path to execute, including where relevant:

- Feature flags
- Application options
- Execution modes
- Threading modes
- Data-dependent conditions
- Platform/compiler conditions
- Product configuration

Distinguish "the path can be enabled" from "the relevant production workflow actually enables it."

### 5. Trace downstream propagation

Use CoreStory to identify the smallest useful set of downstream relationships, then inspect the relevant source.

Look for propagation to:

- Shared mutable state
- Database or design-state mutation
- Algorithm choices or tie-breaks
- Persisted output
- Reporting/message order
- QoR-affecting decisions
- Object lifetime/ownership consumers
- Parallel merge/reduction paths
- External interfaces or dependent components

Do not retrieve broad application context that is unrelated to qualifying the candidate.

### 6. Look for neutralizers

Check for application-level or local-code behavior that prevents the suspect mechanism from becoming observable, such as:

- Deterministic comparator or stable key
- Stable sort or canonicalization
- Normalization before consumption
- Deterministic merge/reduction
- Lookup-only or membership-only consumption
- Safe project wrapper/container
- Fresh deterministic initialization
- Alternate production implementation
- Serialization/synchronization that actually neutralizes the claimed mechanism
- Post-processing that reconstructs the result deterministically

For concurrency candidates, do not treat the mere presence of a lock as proof of deterministic ordering. Defer defect-specific correctness to the originating concurrency skill.

### 7. Establish observable consequence

Identify the concrete application behavior that can observe the suspect mechanism.

A useful causal chain is:

```text
suspect mechanism
    -> reachable execution path
    -> propagated state/order/value/lifetime
    -> downstream consumer
    -> observable application consequence
```

If the chain breaks, record where and why.

### 8. Return qualification evidence

Return the qualification record to the originating analysis workflow. The originating skill remains responsible for final defect-specific verdict and severity.

## Evidence Hierarchy

Prefer evidence in this order:

1. Direct source evidence
2. Build/configuration evidence
3. CoreStory application-relationship evidence
4. Runtime/control-path evidence
5. Inference

Use CoreStory to reduce the amount of source that must be inspected, not to replace source proof of local behavior.

## Qualification Labels

Use one of the following as the CoreStory qualification outcome:

- `QUALIFIED` - application-level evidence supports continued promotion/proof by the originating skill
- `LATENT` - suspect mechanism exists but current application consumers do not make it observable
- `DEAD/UNUSED` - excluded from relevant build or no reachable production path
- `MT-UNREACHABLE` - concurrency suspect does not execute under a relevant multi-threaded path
- `GATE-INACTIVE` - required runtime/configuration control is not active in the relevant workflow
- `NEUTRALIZED` - deterministic behavior removes the suspect effect before observation
- `SAFE-ADOPTER` - implementation already uses the intended deterministic/safe project idiom
- `CONFIGURATION-SENSITIVITY` - outcome depends on configuration rather than equivalent-run nondeterminism
- `BUILD-SENSITIVITY` - conclusion differs by build/product variant and cannot be generalized
- `PLATFORM-SENSITIVITY` - conclusion depends on compiler/platform/runtime behavior
- `FALSE-POSITIVE` - originating candidate does not represent the suspected construct/mechanism
- `UNRESOLVED` - evidence is insufficient to qualify or dismiss

`QUALIFIED` does not by itself mean `REAL`. It means the application-context gate has been satisfied strongly enough for the originating skill to complete defect-specific proof.

## Output Contract

Return a concise record for each candidate:

```text
Candidate:
Originating skill:
Suspected mechanism:

Build inclusion:
Production reachability:
Runtime/configuration gates:
Application relationships:
Downstream propagation:
Neutralizers:
Observable consequence:
Missing evidence:

CoreStory qualification:
Evidence sources:
```

Where possible, include specific files, functions, components, paths, build artifacts, and CoreStory citations/tool evidence rather than generic summaries.

## Division of Responsibility

### Originating defect-analysis skill

- Identifies the defect pattern or mechanism
- Proves local source behavior
- Applies defect-specific correctness rules
- Determines whether runtime confirmation is required
- Assigns final verdict and severity
- Recommends defect-specific remediation

### CoreStory qualification skill

- Establishes application context
- Establishes build and reachability evidence
- Traces cross-component relationships
- Identifies runtime/configuration gates
- Identifies downstream application impact
- Identifies application-level neutralizers
- Returns qualification evidence to the originating workflow

The desired interaction is:

```text
Defect-analysis skill
    -> identifies candidate mechanism

CoreStory qualification
    -> determines whether the candidate matters in this application

Targeted source / defect proof
    -> proves or rejects the actual defect
```

## Controlled-Evaluation Notes

When this skill is used in an A/B or benchmark:

- Keep the user prompt, source revision, model, originating skills, and source scope fixed between comparison arms.
- Keep held-out defect locations unavailable until scoring.
- Do not reuse candidate lists or reports from prior runs unless the experiment explicitly uses a fixed-candidate design.
- Record CoreStory MCP calls separately from local repository search/read operations when telemetry permits.
- If the skill is available but never invoked, record that as a workflow/discovery result rather than manually forcing CoreStory into the run after the fact.
