# Multi-threaded nondeterminism analysis
_Exported on 9/4/2026 at 09:40:03 CDT from Cursor (3.18.25)_

---

**User**

Investigate the repository for multi-threaded nondeterminism caused by race-free but order-dependent floating-point accumulation.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start by using CoreStory to identify likely parallel execution paths, shared floating-point accumulators or reductions, and their downstream consumers.

For any candidate, do not classify it as Real until you establish:
1. the code actually executes under multi-threading,
2. accumulation order can vary,
3. the value reaches an observable consumer, and
4. no complete deterministic canonicalization occurs before that consumer.

Return only the strongest supported candidate, or state that the available evidence is insufficient.

---

**Cursor**

I'll follow the prove-nd-mt skill and CoreStory analysis workflow: read the skill first, then query CoreStory for parallel paths and order-dependent floating-point reductions.

Next I'll load the base prove-nd skill and CoreStory schemas, then list projects and query for parallel floating-point reductions.

Using the newer `cts-code` project (id 10). I'll open a CoreStory conversation and run targeted semantic searches for parallel FP reductions.

Strong leads in the fmax CG solver and TimingCostFunction. I'll query CoreStory for causal context and inspect the first search results.

CoreStory points at partitioned reductions; I'll verify whether merge order actually varies run-to-run (mutex/work-stealing) or only with thread count, and inspect the source.

`std::atomic<float>` accumulators in `ctoscGlobal` match the locked/atomic order-dependent pattern. Inspecting how they're updated and consumed.

The atomic floats sit in a `purecov` deadcode region — I'll verify MT reachability and keep hunting for live locked/atomic FP sums.

Harness updates look concurrent from `ctomt*` workers. Verifying MT dispatch, the option gate, and whether the printed sum is a live consumer.

`tbb::parallel_reduce` can vary join order run-to-run. Inspecting what that GLS reducer accumulates.

**Verdict: available evidence is insufficient** to classify any site as Real for race-free, order-dependent floating-point accumulation under multi-threading.

### What CoreStory + source showed
Live solver/QoR paths (`fmaxcgSolverImpl::calculateTns*` / `TimingCostFunction::evaluateTnsAndWnsParallel` / similar) use **per-job or per-range partials**, then **merge in fixed job/thread-index order after the join**. For fixed thread count and fixed partitioning, that association order does **not** vary across equivalent runs, so it fails criterion (2).

### Closest non-elevated surface
`ctoscGlobal` harness `std::atomic<float>` totals (`_total_path_over_margin`, etc.) **would** be Locked-but-order-dependent if concurrent workers hit them, but:
- `enable_pre_opt_harness` defaults to **false**
- members sit in a `purecov` deadcode region
- the sink is diagnostic `printHarnessSummary`, not a default-on QoR/solver path

So criteria (1) and (3) are not established for live production.

### Missing evidence for a Real finding
A default-on (or proven-on) path where concurrent workers do shared `float`/`double` `+=` under mutex/atomic, the sum reaches an observable production consumer, and no index-ordered recompute covers all contributors—plus a 1-vs-N or N-vs-N bit-level confirmation.

