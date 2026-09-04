# Multi-threaded nondeterminism analysis
_Exported on 9/4/2026 at 14:27:51 CDT from Cursor (3.18.25)_

---

**User**

Investigate the repository for multi-threaded nondeterminism caused by concurrent container insertion or iteration-order dependence.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory. Before broad local repository searching, identify the strongest application-level path you can support that includes:
1. a parallel dispatch or concurrent producer set,
2. multiple workers that can append, insert, enqueue, register, or otherwise contribute results to a shared or merged container,
3. a container ordering that can depend on worker completion, arrival, insertion, or commit order across equivalent runs,
4. a later consumer that iterates or selects from that container in its preserved order, and
5. an observable application result that can depend on that order.

For any candidate, do not classify it as Real until you establish:
1. the producers actually execute concurrently,
2. insertion/merge/arrival order can vary across equivalent runs,
3. the relevant container preserves or exposes that variable order,
4. the downstream consumer is order-sensitive rather than membership-only or commutative, and
5. no complete deterministic sort, stable key ordering, canonicalization, set conversion, re-selection, or post-join recomputation neutralizes the order before the observable consumer.

Use local source inspection to validate the strongest CoreStory-supplied path. Avoid broad product-wide grep unless CoreStory cannot establish a candidate path; if you must broaden the search, make that explicit.

Do not treat an unordered container or concurrent append as sufficient evidence by itself. Prove the complete path from parallel production through preserved order to the observable consumer.

Return only the strongest supported candidate, or state that the available evidence is insufficient.

---

**Cursor**

I'll start with the prove-nd-mt skill and CoreStory application intelligence, then validate only the strongest concurrent insertion/order-dependence path in source.

Next I'll load the base prove-nd skill and query CoreStory for concurrent container insertion / order-dependence paths.

CoreStory ranked `fmaxLpSolverIncremental` highest but left the consumer link weak; I'll tighten that path in-module and cross-check `ctsPathTracer` before trusting either.

Both top hits look neutralized; I'll ask CoreStory for other concurrent-insert paths that keep arrival order through an order-sensitive consumer.

`soSolverUpdater` looks promising from retrieval; I'll check whether path merge is completion-order or job-index, and hunt for true shared concurrent inserts.

CoreStory found no proven Real path yet; I'll validate `fmaxTimingCostFunction` path-merge and the GLS parallel buf-plan near-misses in source.

CoreStory couldn't close a Real path; I'll spot-check the strongest near-misses in local source and do a narrow index filter for concurrent containers.

**Evidence is insufficient** to classify any concurrent container-insertion / iteration-order path as Real.

CoreStory and targeted local checks found parallel producers that append into shared or merged containers, but every complete path examined has a neutralizer or fails an order-sensitivity requirement before an observable consumer.

### Closest near-misses (why they fail)

| Path | Parallel producers | Order preserved? | Why not Real |
| --- | --- | --- | --- |
| `fmaxLpSolver::mergeViolatedPathsOfSolutionsParallel` → `removeRedundantPathsParallel` | `tbb::parallel_for` + `push_back` into per-endpoint vectors | Transiently | `std::sort` + `std::unique` with `ConstraintComparatorNew` before pruning; consumer is membership/slack-based |
| `ctsInterClockBalance` `arrivals1` | `tbb::parallel_for` into `tbb::concurrent_vector<float>` | Yes at insert | Folded into `std::set<float>` before median; membership-only |
| `soSolverUpdater` `clustersToTrace` | Parallel `push_back` into `tbb::concurrent_vector` | Yes at insert | Immediately transferred into `std::set<unsigned int> clustersNotTraced` |
| `ctsPathTracerInterf::findPathsMt` | MT jobs | No (job-index merge) | Aggregation is by job index, not completion order |

### Missing for a Real finding

A proven chain where (1) workers run concurrently, (2) insert/merge order can vary across equivalent runs, (3) that order is preserved, (4) a downstream consumer is order-sensitive (not membership-only / commutative), and (5) no sort, set conversion, stable-key merge, or post-join canonicalization removes the variance.

No such end-to-end path was established from CoreStory application intelligence plus the local validation above.

