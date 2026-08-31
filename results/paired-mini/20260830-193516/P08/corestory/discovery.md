No confirmed schedule-dependent application result emerged from the new pass. CoreStory placed the highest-signal sites into four different roles in the CTS/CTO stack: GLS candidate filtering, GLS winner consolidation before commit, lazy-TNS endpoint model construction, and delay-insertion / cloning heuristics. Of those, the parallel sites I inspected either reduce through order-independent state or do a full join before selection; the heuristic sites do affect committed choices, but I did not establish equivalent-run nondeterminism from scheduling or unstable traversal.

1. `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h` / `ctomtGlsProblemGenerator::runSccIteration`

CoreStory places this in `ctomtGlsFlow::runBatches()` via `findNextProblem()`, so it is upstream candidate filtering rather than direct commit. The variable part is real: in MT mode, worker scheduling determines which SCC indices execute before `globalDone` flips, and the reducer can concatenate `localLog` in different orders. But at the inspected call sites in `ctomtGlsProblemGenerator.cc` (`evalGskewBuffering`, `evalGskewNotBuffering`, `evalGlate`), the committed decision is only the boolean `value`, reduced with `&&` or `||`; `localLog` is only printed. Classification: `schedule-dependent execution with deterministic final result`. Confidence: high. Missing evidence for escalation: a hidden side effect inside `body(...)` or a non-diagnostic consumer of `localLog`.

```310:334:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h
std::atomic<bool> globalDone{false};

return tbb::parallel_reduce(
    tbb::blocked_range<size_t>(0, n),
    init,
    [&](const tbb::blocked_range<size_t>& r, stateType localS)->stateType {
      for (size_t i = r.begin(); i != r.end(); ++i) {
        if (globalDone.load(std::memory_order_relaxed)) {
          break;
        }
        body(i, localS);
        if (localS.done(init)) {
          globalDone.store(true, std::memory_order_relaxed);
          break;
        }
      }
      return localS;
    },
    [&](const stateType& a, const stateType& b)->stateType {
      stateType merged = reduce(a, b);
      if (merged.done(init)) {
        globalDone.store(true, std::memory_order_relaxed);
      }
      return merged;
    });
```

2. `ctscto/ctosc/ctomt/gls/ctomtGlsResultIntegrator.cc` / `ctomtGlsResultIntegrator::selectBestPerDriver`

This is the strongest result-selection site I found in GLS. CoreStory ties it to the Phase-2-to-Phase-3 handoff: per-plan problems are evaluated in parallel, then `selectBestPerDriver()` groups them by driver and keeps only one survivor before the later commit path. That survivor absolutely affects downstream committed state, but the selection itself is a serial post-pass over the fully finished set, comparing `costVector`s and clearing `foundSolution` / `tryCommit` on losers. Equal-cost ties fall back to the first encountered index; from `ctomtGlsParallelBufPlans.cc`, expansion order is fixed (`planIdx`, then clone-only, then delay-engine-only), so I did not establish scheduler dependence. Classification: `schedule-dependent execution with deterministic final result`. Confidence: medium-high. Missing evidence: whether some uninspected step reorders `problems` or makes equal-cost ties scheduler-sensitive.

```600:640:ctscto/ctosc/ctomt/gls/ctomtGlsResultIntegrator.cc
void
ctomtGlsResultIntegrator::selectBestPerDriver(ctsXformProblems& problems)
{
  std::unordered_map<const ndmTerm*, std::vector<size_t>> groups;
  for (size_t i = 0; i < problems.size(); ++i) {
    auto* p = static_cast<ctomtXformProblem*>(problems[i]);
    if (p->isDriverGrouped() && !p->getSeedTerms().empty()) {
      groups[p->getSeedTerms()[0]].push_back(i);
    }
  }

  for (auto& [term, indices] : groups) {
    if (indices.size() <= 1) continue;

    size_t bestIdx = indices[0];
    bool bestFound = false;
    for (size_t idx : indices) {
      auto* p = static_cast<ctsXformProblem*>(problems[idx]);
      if (!p->getFoundSolution()) continue;
      if (!bestFound) {
        bestIdx = idx;
        bestFound = true;
        continue;
      }
      auto* best = static_cast<ctsXformProblem*>(problems[bestIdx]);
      changeState* bestBest = best->getCtsCkt().getBestState();
      changeState* curBest = p->getCtsCkt().getBestState();
      const costVector* bestCost = bestBest ? bestBest->getCost() : nullptr;
      const costVector* curCost = curBest ? curBest->getCost() : nullptr;
      if (curCost && (!bestCost || curCost->compare(bestCost) < 0)) {
        bestIdx = idx;
      }
    }
    // ...
  }
}
```

3. `ctssc/lazytns/ctsLazyModel.cc` / `collectCostGroupEndpointsMt` and `buildCostGroupEpMt`

CoreStory places these in lazy-TNS model initialization, not at a commit boundary. The parallelism is one job per scenario/path-group, but each job writes into local `std::set`s, and the merge back into `setupEps`, `holdEps`, `_outRangeEps`, `_epsInSkippedPg`, and latch-graph pin sets is done in a serial `for` loop after all jobs finish. Then `buildCostGroupEpMt()` creates jobs from the already ordered `std::set eps`, runs them in parallel, and consumes them serially. So worker completion order can change runtime, but from the inspected code it does not change endpoint membership at this stage. Classification: `schedule-dependent execution with deterministic final result`. Confidence: high. Missing evidence: I did not exhaustively trace whether later `costGroup` consumers introduce a separate order-sensitive selection.

4. `ctsutil/ctsSearchClockTreeDriver.cc` / `ctsSession::searchClockTreeDriverTermsForDelayInsertion`

This is not a parallel race, but it is a genuine traversal-order / first-success heuristic. CoreStory places it in target-latency / delay-insertion candidate generation, and `ctscto.cc` uses the resulting candidate chains exactly ΓÇ£in order, until one of the insertions is successful.ΓÇ¥ That means the chosen driver/load chain can affect committed buffer placement. Still, the inspected source shows explicit strategy control (`FIRST_DOWNSTREAM`, `LAST_DOWNSTREAM_MIN_LOAD`, `LAST_DOWNSTREAM_MIN_DRIVER`), reconvergence pruning, and ordered containers; I did not establish any equivalent-run variability in the traversal itself. Classification: `insufficient evidence`. Confidence: medium. Missing evidence: whether `ctsClockPathIterator` visitation or the underlying comparator-backed term ordering can vary across equivalent runs.

```3180:3239:ctscto/ctscto.cc
// From the requested root, get a vector of parallel delay chains
// This traverses down the tree to find drivers of bufferable nets and 
// performs port punch analysis requires further splitting into parallel chains.
// This provides an ordered list of candidate drivers (and corresponding load subsets)
// that we should try, in order, until one of the insertions is succesful.
int orderIndex = getCtsSession()->getOpt().getDebugIntSetting("cts_meet_target_latency_downstream_strategy", ctsDlyDriverSearcher::FIRST_DOWNSTREAM);
// ...
for (auto dcIter = delayChains.begin(); dcIter != delayChains.end(); ++dcIter) {
  bool anyCandSuccess = false;
  std::size_t candTry = 0;
  ctsDlyDriverSearcher::candidateDelayChainsType candidateDelayChains = *dcIter;
  for (auto candIter = candidateDelayChains.begin(); candIter != candidateDelayChains.end(); ++candIter) {
    // try candidates in order
```

5. `ctscto/ctoRestruct.cc` / `ctoRestruct::partitionLoadsForCloning`

CoreStory places this in cloning/reparent preparation, upstream of the later transform that may commit. The algorithm is explicitly heuristic: classify loads by criticality, choose a farthest load, sort by distance to that representative, form groups according to the selected partition scheme, then try partition schemes from ordered `schemeTrials` and stop at the first one that improves QoR. That definitely influences which work is performed and can influence the eventual committed transformation. But I did not find a scheduler-dependent mechanism here; the sort has an explicit tie-breaker and the scheme order is fixed. Classification: `insufficient evidence`. Confidence: medium. Missing evidence: whether equal-distance ties and multiple-improving schemes occur often enough to change equivalent runs, and whether the comparator semantics are stable across runs.

A relevant non-elevated atomic first-claim pattern does exist in `ctscstr/ctscstrDesign.cc`: `ctscstrDesign::disarmGuardOnDtor()` uses `compare_exchange_strong` so only one caller resumes the observer under a guard. I did not elevate it because this is concurrency control around observer state, not a site that selects an optimization candidate or commits QoR state.

Two stabilizing patterns showed up repeatedly and are worth noting because they reduced concern: `ctoFlowRelaxAnalyzer.cc` explicitly sorts candidate term bags ΓÇ£to avoid randomness,ΓÇ¥ and `ctomtClone.cc` changed `_mgToSgMap` to a `std::map` to avoid Coverity `POINTER_NONDETERMINISM`. Those are signs the code already has some active determinism hardening in adjacent heuristics.

If you want the next highest-value validation, IΓÇÖd do two focused checks: vary thread count around the GLS Phase-2 / `runSccIteration` path to confirm only work/log/runtime change, and add temporary logging for equal-cost ties in `selectBestPerDriver` and equal-distance ties in `partitionLoadsForCloning` to see whether the fixed heuristic order is ever deciding materially different downstream results.
