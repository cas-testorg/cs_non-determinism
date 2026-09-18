# Investigation 03 — ccdcgSolver fixed-seed RNG

**Candidate:** `ccd/ctsccd/cgbased/ccdcgSolver.cc:501`

**Test 1 pattern:** Without MCP promoted; With MCP dismissed.

## Objective

Investigate whether the RNG usage creates production non-determinism and identify the evidence that should distinguish a suspicious RNG construct from an actual ND mechanism.

Treat both the promotion and dismissal as hypotheses.

## Starting hypothesis

Use of process-global `srand()` / `rand()` is suspicious, but a fixed seed followed by deterministic sequential consumption may be reproducible unless another production consumer, concurrency, call ordering, or varying input changes the stream.

## Independent investigation

Use Agentic Bug Resolution to establish build/reachability, seed behavior, all relevant production consumers, execution ordering/concurrency, whether the RNG state can vary across equivalent runs, downstream use of generated values, observable impact, and evidence gaps.

Do not use the Test 1 comparison's final disposition as evidence. Do not modify source.

Save the completed result in `investigation.md` before beginning the trace map.

## Trace-map question

After the investigation is frozen, identify what evidence allowed or should have allowed the candidate to be rejected or promoted, and whether that evidence came from application qualification rather than ND discovery.
