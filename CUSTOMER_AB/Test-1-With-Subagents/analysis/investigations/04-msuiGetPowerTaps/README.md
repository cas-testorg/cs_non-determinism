# Investigation 04 — msuiGetPowerTaps container semantics

**Candidate:** `mscts/msui/msuiGetPowerTaps.cc:66,879`

**Test 1 pattern:** With MCP promoted; later source review challenged the reported mechanism.

## Objective

Independently resolve the ordering/hash semantics of the container and determine why the With-MCP qualification path promoted the candidate.

Treat the reported address/hash mechanism as a hypothesis.

## Starting hypothesis

The candidate depends on whether `dosUnorderedSet<ndmBlkInst*>` iteration is driven by raw pointer addresses or by stable application identity, and whether insertion order itself can vary. The container implementation must be resolved before making an ND claim.

## Independent investigation

Use Agentic Bug Resolution to trace the container typedef and implementation, hash/comparator behavior, insertion sources/order, iteration behavior, build/reachability, downstream Tcl collection construction, observable ordering, neutralizers/canonicalization, and unresolved external definitions.

Do not infer container semantics from the type name alone. Do not use the Test 1 comparison's final disposition as evidence. Do not modify source.

Save the completed result in `investigation.md` before beginning the trace map.

## Trace-map question

After the investigation is frozen, identify where the With-MCP reasoning stopped too early: type resolution, hash semantics, insertion-order analysis, downstream observability, evidence sufficiency, or another qualification step.
