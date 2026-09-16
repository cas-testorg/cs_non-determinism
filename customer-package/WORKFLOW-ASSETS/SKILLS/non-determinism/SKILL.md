# Multi-Threaded Non-Determinism — Evaluation Snapshot

**Owner:** Synopsys  
**Source skill name:** `prove-nd-mt` / multi-threaded non-determinism extension  
**Source blob:** `95204ad9767a0e155a4aad45a883f05d1af6e7b0`

> This customer-package copy preserves the operative multi-threaded ND instructions relevant to the evaluation. Internal absolute paths, supporting references, and extended worked precedents are not reproduced.

## Objective

Extend `prove-nd` for multi-threaded nondeterminism suspects including races, locks, atomics, parallel reductions, thread pools, worker-object state carryover, and commit-order dependence.

All base `prove-nd` rules apply, including the no-subagent rule and the requirement for downstream observability.

## Core Distinction

The workflow distinguishes three materially different outcomes:

| Outcome | What varies | Does locking resolve it? |
|---|---|---|
| Data race | Undefined behavior / invalid concurrent access | Often |
| Race-free but order-dependent | Observable result varies with execution order | **No** |
| Benign | Nothing observable | N/A |

A lock can establish race freedom. **A lock does not by itself establish deterministic ordering or deterministic results.**

## Hard Rules

- Prove that the code actually executes under multi-threading; do not infer concurrency from the presence of a lock.
- Prove relevant runtime/thread gates are live.
- Resolve accessors/callers rather than relying only on private member-name searches.
- Inspect both entry and exit sides of reused-worker boundaries for reset behavior.
- Atomic integer accumulation is deterministic with respect to arrival order; floating-point accumulation is not generally associative.
- Prefer thread-count A/B testing over TSan when validating an ordering claim; TSan answers a race question, which is different.

## MT-Specific Observable Sinks

Examples include:

- non-associative floating-point reduction;
- first-writer / first-finder wins;
- shared min/max ratcheting with run-dependent operands;
- order-sensitive concurrent container insertion/iteration;
- ID/handle/index allocation order;
- shared budget or early-exit exhaustion;
- worker-state carryover;
- commit-order dependence.

## MT-Specific Neutralizers

Potential neutralizers must be verified rather than assumed. Examples include:

- canonicalization after the parallel join;
- per-thread partials merged in stable-key order;
- order-independent integer/bitwise/set operations;
- idempotent writes of identical values;
- membership-only/lookup-only use;
- unconditional per-work-item assignment before read;
- deterministic re-sort at the observable boundary.

A canonicalizer must cover every contributor. Partial canonicalization can leave a real ND path.

## Gate Audit

Before accepting a lock, guard, or determinism option as protection, investigate whether it is actually active. Relevant failure modes include:

- thread-count gate permanently false;
- commented-out or compiled-out lock;
- no-op default argument;
- distinct locks that appear equivalent by name;
- lock released before the mutation it is intended to protect;
- broken double-checked locking;
- determinism option that does not reach the relevant code path.

## Worker-State Boundary Review

For reused worker objects, inspect both:

```text
Entry side: start / begin / init / reset / new-work hooks
Exit side: cleanup / end / finish / post-commit hooks
```

Do not infer carryover from the absence of an exit-side clear if an entry-side reset establishes deterministic state.

## MT Classification Refinements

The extension adds useful refinements such as:

- **Locked-but-order-dependent** — race-free but result can vary.
- **Gate-inactive** — protection exists syntactically but is inactive.
- **Worker-carryover** — pooled worker state crosses work-item boundaries.
- **Commit-order** — shared result depends on completion order.
- **Canonicalized-after-join** — transient variation removed before observation.
- **Partially-canonicalized** — neutralizer exists but does not cover all contributors.
- **Race-but-idempotent** — concurrent writes cannot change the observable value.
- **MT-unreachable** — code does not execute concurrently in the relevant path.

Use **Unresolved** when path/reachability evidence is insufficient rather than guessing.

## Runtime Validation

Match validation to the claim:

- ordering claim -> controlled thread-count/repeatability comparison;
- race claim -> TSan or targeted invariant instrumentation;
- carryover claim -> log worker/work-item/state boundary behavior;
- precision-sensitive result -> compare raw/full-precision values rather than rounded reports.

## Orchestration Note

This extension inherits the base `prove-nd` instruction to **not use sub-tasks or sub-agents**. This differs from the repository-scale `nd-code-analyzer` discovery stage, which explicitly permits parallel exploration at defined candidate/module-size thresholds.
