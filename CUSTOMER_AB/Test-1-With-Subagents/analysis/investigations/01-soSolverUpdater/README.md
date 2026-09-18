# Investigation 01 — soSolverUpdater shared-map race

**Candidate:** `ccd/skewopt/soSolverUpdater.cc:2100`

**Test 1 pattern:** Found by Without MCP; not reported by With MCP.

## Objective

Investigate the reported shared-map data-race mechanism independently, then determine why the With-MCP workflow did not surface it.

Treat the reported defect as a hypothesis, not a confirmed finding.

## Starting hypothesis

A `tbb::parallel_for_each` execution may perform concurrent `std::map::operator[]` operations against shared solver maps. If multiple workers can mutate the same map concurrently, insertion/rebalancing may constitute a data race and may produce corrupted or run-dependent solver state.

## Independent investigation

Use Agentic Bug Resolution. Determine build inclusion, production reachability, parallel activation conditions, shared state, synchronization/prepopulation/thread-local protections, downstream consumers, observable behavior, blast radius, and remaining validation needs.

Do not use the Test 1 comparison's final disposition as evidence. Do not modify source.

Save the completed result in `investigation.md` before beginning the trace map.

## Trace-map question

After the investigation is frozen, compare it with both raw Test 1 arms and determine where the With-MCP path diverged: candidate discovery, parallel-pattern recognition, shared-state tracing, sink tracing, reachability, qualification, or orchestration.
