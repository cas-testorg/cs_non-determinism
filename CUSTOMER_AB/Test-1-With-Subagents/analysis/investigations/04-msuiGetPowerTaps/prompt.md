Use the agentic-bug-resolution playbook to investigate a reported
non-determinism defect in Fusion Compiler CTS.

CoreStory scope constraint:

Use CoreStory project ID 10 (workspace: cts-code) for all CoreStory
application-context queries in this investigation.

Do not use cts-code2 or any other CoreStory project as evidence.

Treat the reported defect as a hypothesis, not as a confirmed finding.

Reported candidate:

File:
mscts/msui/msuiGetPowerTaps.cc

Approximate locations:
66 and 879-890

Reported mechanism:

A container holding ndmBlkInst* values may be iterated in an unstable
order. If the container's hash or ordering behavior depends on raw
pointer addresses, iteration order may vary between otherwise equivalent
executions. If that iteration order is preserved into a Tcl result or
another observable downstream collection, the output may be
non-deterministic.

Investigate this candidate independently.

Determine:

1. Whether the affected source is part of the relevant production build.
2. Whether the code is reachable from production CTS execution paths.
3. The exact concrete type of the container involved.
4. Resolve the container implementation, typedefs, aliases, hash
   function, equality/comparator behavior, and any relevant wrapper
   classes. Do not infer behavior from the container or type name.
5. Determine what values actually participate in hashing or ordering:
   raw pointer address, object ID/handle, object type, name, context,
   insertion sequence, or another property.
6. Determine how the container is populated and whether its insertion
   order can vary between otherwise equivalent executions.
7. Determine what controls its iteration order.
8. Trace the iterated values into the downstream Tcl/result collection
   or other consumer.
9. Determine whether downstream sorting, canonicalization, stable
   conversion, set semantics, or another neutralizer removes any
   ordering variation before it becomes observable.
10. Determine whether a credible path exists from varying input or
    ordering to observable CTS/Tcl behavior.
11. Identify the runtime/configuration conditions required for the
    suspected behavior.
12. Determine the likely blast radius if the defect is real.
13. Identify what evidence remains unresolved and requires SME or
    runtime validation.

Trace definitions through their implementation rather than stopping at
typedefs or wrapper APIs.

For any claim that pointer identity or pointer address affects hashing
or ordering, identify the source implementation that establishes that
behavior. Do not classify the container as pointer-address-dependent
solely because its element type is a pointer.

Likewise, a container being unordered does not by itself establish
run-to-run non-determinism. Establish what can vary between equivalent
executions and whether that variation reaches an observable consumer.

Clearly distinguish:

- direct source evidence;
- CoreStory application evidence;
- reasoned inference;
- unresolved questions.

Do not use previous generated ND reports, benchmark comparison reports,
prior AI conclusions, or known defect lists as evidence.

Do not assume the reported defect is correct.

Do not modify source code.

Stop at the investigation checkpoint and provide an evidence-based
assessment and validation plan.
