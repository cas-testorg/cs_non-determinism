# Independent Source Validation

Use the **LOCAL REPOSITORY SOURCE ONLY**.

This is a validation task, not a discovery task.

Do not use:

- CoreStory
- MCP tools
- previously generated nondeterminism analysis documents
- prior analysis artifacts
- prior investigation conclusions
- external analysis

The candidate findings supplied below came from a separate discovery session. Treat every statement in them as an untrusted claim to validate independently against the local source repository.

For each candidate finding, evaluate two questions.

## 1. Source Grounding

Determine whether the cited source location, symbol, control path, application relationship, and claimed mechanism actually exist in the local repository.

Classify source grounding as:

- **SUPPORTED** — local source directly supports the material claim.
- **PARTIALLY SUPPORTED** — part of the claim is grounded, but an important link is missing or overstated.
- **UNSUPPORTED** — local source does not support the claim.

## 2. Defect / Nondeterminism Correctness

Determine whether the grounded mechanism actually supports the defect or nondeterminism classification claimed by the discovery result.

For nondeterminism, require evidence for both:

1. what can vary across equivalent executions; and
2. how that variation can reach an observable application result.

Distinguish among:

- established defect mechanism
- established undefined behavior
- established nondeterministic manifestation
- plausible but requiring additional runtime/external evidence
- mitigated or correctly guarded behavior
- deterministic behavior
- insufficient evidence

Do not treat a suspicious construct as a defect by pattern alone.

Examples:

- Parallel execution is not a data race unless conflicting shared-state access and insufficient synchronization are established.
- A raw pointer is not a use-after-free unless destruction followed by reachable stale access is established.
- An unordered or pointer-ordered container is not equivalent-run nondeterminism unless variable ordering reaches an order-sensitive observable result.
- A sentinel value is not an uninitialized read when it is intentional state and required guards are present.
- Platform, compiler, build, version, or configuration sensitivity is not equivalent-run nondeterminism unless behavior can vary under the same execution conditions.

## Required Output

For each candidate provide:

- candidate identifier, preserving the discovery identifier when present
- grounding classification
- defect/nondeterminism classification
- independently located file and symbol
- source evidence
- causal chain supported by the source
- mitigating or determinism-restoring behavior
- FACT versus INFERENCE distinction
- alternate explanation when applicable
- missing evidence required for confirmation
- concise validator conclusion

End with an aggregate summary containing:

- total candidates validated
- source grounding counts
- established defect/UB counts
- established nondeterminism counts
- mitigated/deterministic counts
- candidates requiring additional evidence

Do not perform a new broad search for unrelated findings. Validate only the supplied candidate set.
