# Defect-Class Mapping

This document maps the requested Coverity and ThreadSanitizer defect classes to the mechanism-oriented Test Case 2 prompts.

It is **explanatory documentation for the automation and evaluation workflow**. The analysis must not depend on this document being automatically loaded by Cursor or the model. Operational guidance required during execution is contained directly in the v2 rule and the applicable prompt.

## Mapping

| Tool | Defect class | Primary Test Case 2 prompt | Investigation focus |
|---|---|---|---|
| Coverity | `UNINIT` | P01 — Uninitialized and Indeterminate State | Read or use before valid initialization on a reachable control path |
| Coverity | `UNINIT_CTOR` | P01 — Uninitialized and Indeterminate State | Object member not validly initialized before use |
| Coverity | `POINTER_NONDETERMINISM` | P04 — Pointer-Dependent Ordering | Address-dependent ordering/hash/traversal reaching order-sensitive behavior |
| ThreadSanitizer | `DATA RACE` | P02 — Shared-State Concurrency and Non-Thread-Safe Access | Conflicting concurrent access without sufficient synchronization |
| ThreadSanitizer | `HEAP USE AFTER FREE` | P03 — Object Lifetime and Use-After-Free | Destruction/invalidation followed by a reachable stale heap access |
| ThreadSanitizer | `THREAD LEAK` | P02 — Shared-State Concurrency and Non-Thread-Safe Access | Thread/task created without a valid join, detach, shutdown, or lifecycle-completion path |
| ThreadSanitizer | `UNLOCK OF AN UNLOCKED MUTEX` | P02 — Shared-State Concurrency and Non-Thread-Safe Access | Unlock without a valid matching acquisition/ownership path |

## Interpretation Rule

The tool names above are **investigation patterns, not expected findings**.

For each candidate, the evaluation should distinguish this progression:

**tool-pattern match**  
→ **source-grounded mechanism**  
→ **active defect, if established**  
→ **nondeterministic manifestation, if separately established**

A source construct that resembles a Coverity or ThreadSanitizer class is not sufficient by itself to classify the application as defective.

Examples:

- Parallel access is not a `DATA RACE` unless conflicting operations can actually overlap without sufficient synchronization.
- A raw pointer is not `HEAP USE AFTER FREE` unless destruction/invalidation and a reachable stale access are established.
- A thread creation site is not a `THREAD LEAK` unless the lifecycle lacks an effective join, detach, shutdown, or equivalent completion path.
- An unlock call is not `UNLOCK OF AN UNLOCKED MUTEX` unless the acquisition/ownership path is invalid or absent on a reachable path.
- A pointer-keyed container is not `POINTER_NONDETERMINISM` unless address-dependent ordering reaches behavior that remains order-sensitive after any sorting, canonicalization, or other determinism-restoring mechanism.
- An uninitialized-looking sentinel is not `UNINIT` or `UNINIT_CTOR` when application invariants and guards prevent invalid consumption.

## Operational Source of Truth

During Test Case 2 execution:

1. Apply `test-case-2-corestory/rules/code-analysis-v2.mdc`.
2. Run the applicable mechanism-oriented prompt under `test-case-2-corestory/prompts/`.
3. Use CoreStory application intelligence and targeted source inspection as directed by the rule and prompt.
4. Do not require this mapping document to be read into model context.

This document exists so automation authors and reviewers can see how the requested tool-specific defect classes are covered by the 10-prompt mechanism model without creating a second, tool-specific prompt suite.
