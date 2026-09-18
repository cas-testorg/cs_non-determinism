# Investigation 02 — msDrivers findDriverTerm

**Candidate:** `mscts/drivers/msDrivers.cc:711`

**Test 1 pattern:** Not promoted by Without MCP; promoted by With MCP.

## Objective

Investigate the candidate independently and determine what evidence path allowed the With-MCP workflow to surface a candidate the Without-MCP workflow did not promote.

Treat the reported defect as a hypothesis.

## Starting hypothesis

A raw-pointer-ordered load-net set may influence which driver term is returned when multiple load nets are present. If the return value is last-wins and reaches production consumers before deterministic canonicalization, address ordering may affect clock/sink context and downstream tree construction.

## Independent investigation

Use Agentic Bug Resolution to establish build/reachability, the semantics of the load-net set, loop/return behavior, callers, any canonicalization at call sites, runtime/feature gates, downstream mutation, observable impact, and unresolved evidence.

Do not use the Test 1 comparison's final disposition as evidence. Do not modify source.

Save the completed result in `investigation.md` before beginning the trace map.

## Trace-map question

After the investigation is frozen, determine whether the With-MCP advantage came from accessor-aware tracing, application relationships, manual source reasoning, candidate discovery strategy, or another factor.
