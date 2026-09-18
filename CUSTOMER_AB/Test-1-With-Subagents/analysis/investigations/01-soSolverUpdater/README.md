# Investigation 01 — soSolverUpdater shared-map race

**Candidate:** `ccd/skewopt/soSolverUpdater.cc:2100`

**Test 1 pattern:** Found by Without MCP; not reported by With MCP.

## Execution Configuration

- **Client:** Cursor
- **Model:** Claude Opus 4.8
- **Thinking effort:** High
- **CoreStory MCP:** Enabled
- **CoreStory ND rule:** Removed / disabled
- **Customer ND skills:** Removed / disabled (`nd-code-analyzer`, `non-determinism`, `prove-nd`)
- **Enabled skill:** `agentic-bug-resolution` only
- **Other skills:** None
- **Prior A/B conclusions provided to agent:** No
- **Prompt:** `prompt.md`
- **Source:** Same CTS customer A/B source snapshot

This is a focused third-view investigation, not a reproduction of the original Without-MCP or With-MCP arm.

## Objective

Investigate the reported shared-map data-race mechanism independently, then determine why the With-MCP workflow did not surface it.

Treat the reported defect as a hypothesis, not a confirmed finding.

## Starting hypothesis

A `tbb::parallel_for_each` execution may perform concurrent `std::map::operator[]` operations against shared solver maps. If multiple workers can mutate the same map concurrently, insertion/rebalancing may constitute a data race and may produce corrupted or run-dependent solver state.

## Independent investigation

Use Agentic Bug Resolution. Determine build inclusion, production reachability, parallel activation conditions, shared state, synchronization/prepopulation/thread-local protections, downstream consumers, observable behavior, blast radius, and remaining validation needs.

Do not use the Test 1 comparison's final disposition as evidence. Do not modify source.

Use the exact investigation prompt preserved in `prompt.md`.

Save the completed result in `investigation.md` before beginning the trace map.

## Trace-map question

After the investigation is frozen, compare it with both raw Test 1 arms and determine where the With-MCP path diverged: candidate discovery, parallel-pattern recognition, shared-state tracing, sink tracing, reachability, qualification, or orchestration.
