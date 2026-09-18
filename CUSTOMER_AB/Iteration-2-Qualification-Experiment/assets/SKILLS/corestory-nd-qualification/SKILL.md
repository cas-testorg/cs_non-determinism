# CoreStory ND Qualification

## Objective

Qualify a **frozen non-determinism candidate** in application context after discovery and mechanism proof.

This skill does not replace the customer's discovery reference set and does not measure discovery recall. It determines whether a supplied candidate is built, reachable, active, causally capable of varying, propagated, neutralized, and observable in the production application.

Use CoreStory project **10** (`cts-code`) only. Do not use `cts-code2` or another CoreStory project as evidence.

## Inputs

For each candidate require:

- stable candidate ID;
- file/function/location;
- suspected ND mechanism;
- discovery evidence;
- mechanism-proof result from `prove-nd` / `prove-nd-mt`, when available;
- relevant customer reference/example family when recorded during discovery.

Do not use prior A/B conclusions, prior AI adjudications, held-out ground truth, or previous benchmark reports to determine the answer.

## Qualification Sequence

### 1. Build inclusion

Determine whether the relevant source/artifact participates in the production build or relevant product target.

Use direct build source when available. Use CoreStory to establish application/module relationships where useful.

### 2. Production reachability

Trace from relevant production entry points/callers to the candidate.

Do not classify code as dead solely from lack of a local text match. Resolve wrappers, accessors, indirect callers, registrations, and related implementations when relevant.

### 3. Runtime/configuration gate

Identify the feature flags, modes, thread counts, topology/data conditions, defaults, compile-time controls, or other gates required for execution.

Distinguish equivalent-run ND from configuration, build, platform, or version sensitivity.

### 4. Exact ND mechanism

State exactly what can vary across equivalent executions and why.

Resolve the actual C++ type/implementation required by the claim. Pattern names are not proof.

Examples of required distinctions:

- parallel execution vs. an actual race/order-dependent result;
- pointer element type vs. address-based ordering/hashing;
- unordered container vs. actually varying iteration order;
- PRNG presence vs. varying seed/state;
- undefined behavior vs. demonstrated nondeterministic manifestation;
- local order variation vs. observable order-sensitive consumption.

### 5. Propagation

Trace the varying state/order/value through callers and consumers.

Identify which callers preserve the mechanism and which do not.

### 6. Neutralization

Explicitly search for deterministic neutralizers, including:

- stable comparators;
- sorting/canonicalization;
- deterministic re-derivation;
- synchronization;
- idempotent/order-independent operations;
- deterministic seeds;
- stable merge/reduction;
- post-join normalization;
- lookup/membership-only consumption.

A mechanism can exist locally and still be neutralized before observation.

### 7. Observable consequence

Establish a credible path to a relevant observable result such as:

- design/database mutation;
- topology;
- timing/QoR;
- algorithmic choice;
- output/report ordering;
- persisted state;
- externally visible behavior;
- crash/corruption;
- race/invalid concurrent behavior.

Bound the blast radius. Do not generalize beyond the supported consumers/configurations.

### 8. Evidence completeness

Identify every load-bearing link in the conclusion.

**Missing load-bearing evidence must never be replaced by inference.**

If the conclusion depends on an unavailable implementation, comparator, hash function, wrapper, external-library behavior, converter, caller, runtime gate, or other semantic link, classify that dimension as `UNRESOLVED`.

A suspicious structural pattern is not sufficient to promote a candidate.

## Evidence Hierarchy

Label evidence explicitly:

1. **Direct source**
2. **Build/configuration**
3. **CoreStory application evidence**
4. **Runtime**
5. **Reasoned inference**
6. **SME**
7. **Unavailable**

Inference may guide the next investigation step but cannot substitute for a load-bearing implementation.

When evidence conflicts, record the conflict.

## CoreStory Usage

Use CoreStory for application relationships that are expensive or incomplete through local search alone, especially:

- build/component relationships;
- callers/callees;
- registrations/entry points;
- wrappers/accessors;
- implementations;
- configuration relationships;
- dependencies;
- downstream consumers;
- cross-file propagation.

Use targeted source inspection for exact local C++ semantics.

Do not force CoreStory for facts better established directly from source.

## Provenance Ledger

Because client session/MCP transcripts may not be retained, the qualification artifact itself must record material CoreStory usage.

For every evidence item that affects a disposition record:

| Evidence ID | Candidate | Stage | Evidence source | Question / purpose | Result | Decision affected |
| --- | --- | --- | --- | --- | --- | --- |

For CoreStory evidence, summarize the application question and returned evidence sufficiently to understand its contribution later.

Do not claim that CoreStory caused a decision unless the ledger shows that contribution.

## Dispositions

Use the narrowest supported disposition:

- **REAL** — mechanism and production application consequence supported.
- **LATENT** — mechanism supported and credible production path exists, but required runtime/configuration trigger is unconfirmed.
- **CONFIGURATION-SENSITIVITY**
- **BUILD-SENSITIVITY**
- **NEUTRALIZED**
- **DEAD/UNUSED**
- **NOT-ND**
- **UNRESOLVED**
- **SME/RUNTIME-VALIDATION**

Do not force a binary REAL/NOT-ND answer.

## Required Candidate Output

For each candidate produce:

```text
Candidate ID:
Location:
Reported mechanism:
Discovery reference/example family:

MECHANISM PROOF
Disposition:
Evidence:
Unresolved:

APPLICATION QUALIFICATION
Build:
Reachability:
Runtime/config:
Exact varying input/state:
Mechanism:
Propagation:
Neutralization:
Observable consequence:
Blast radius:
Missing load-bearing evidence:

CORESTORY CONTRIBUTION
CoreStory used: YES/NO
Questions/purposes:
Evidence contributed:
Decision(s) affected:
Could the disposition have been reached from local source alone?: YES/NO/UNKNOWN

FINAL
Disposition:
Confidence basis:
SME/runtime validation required:
```

Append the provenance ledger.

## Acceptance Lessons from Test 1

The workflow must handle these patterns correctly without being told their prior dispositions:

1. A parallel/container operation is not a demonstrated race without conflicting concurrent behavior.
2. Caller tracing must distinguish consumers that neutralize a local mechanism from consumers that preserve it.
3. A fixed PRNG seed with deterministic consumption is not itself equivalent-run ND; investigate upstream ordering separately if needed.
4. An unordered pointer-valued wrapper does not establish pointer-address hashing. Resolve the implementation or return `UNRESOLVED`.

These are behavioral requirements, not benchmark answers.

## Stop Condition

Stop at the qualification checkpoint. Do not modify source code.

Provide the evidence-backed disposition, unresolved links, recommended runtime/SME validation, and provenance ledger.
