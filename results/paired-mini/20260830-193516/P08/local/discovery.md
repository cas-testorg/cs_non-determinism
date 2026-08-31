## Findings
No confirmed equivalent-run application-result nondeterminism was established in the areas I inspected. I found one plausible current application-result risk in fishbone routing, plus several semantically similar parallel patterns that appear to restore determinism before commit.

- `mscts/fishbone/fbRouter.cc` / `fbLayerSelection::compare` / `fbRouter::planTopologyForAlign`  
  Classification: `plausible schedule/traversal-order-dependent result requiring additional evidence`  
  This is a first-success-wins heuristic: `exploreLayerSelection()` ranks candidate `(trunkLayer, fingerLayer)` pairs, and `planTopologyForAlign()` commits the first candidate whose `routeTrunk()` succeeds. The risk is that the ranking comparatorΓÇÖs final tie-break is not strict: it returns `>=` on `getPhysicalIdxSum()`. If two candidates tie on penalty and cost, the sorted order can depend on sort behavior rather than a stable total order. Since the router then accepts the first successful candidate, different tie ordering could select different layers and therefore different routed geometry/timing.

```191:205:mscts/fishbone/fbRouter.cc
for (const fbLayerSelection &layers: layerSelections) {
  if (routeTrunk(layers.getTrunkLayer())) {
    planBelowTrunk(&layers);
    if (_options.getPruneTrunk()) {
      pruneTrunk();
    }
    return true;
  }
  else {
    // The net is not routed, probably because the trunk is too short.
```

```2774:2793:mscts/fishbone/fbBaseRouter.cc
bool fbLayerSelection::compare(const fbLayerSelection &s1, const fbLayerSelection &s2)
{
  // First criterion: Lowest penalty.
  if (s1._penalty < s2._penalty) {
    return true;
  }
  if (s1._penalty > s2._penalty) {
    return false;
  }

  // Second criterion: Lowest cost.
  if (s1._cost < s2._cost) {
    return true;
  }
  if (s1._cost > s2._cost) {
    return false;
  }

  // Tiebreaker: Highest Layers.
  return (s1.getPhysicalIdxSum() >= s2.getPhysicalIdxSum());
}
```

  Causal chain supported so far: tie in heuristic scores -> comparator leaves relative order unstable -> first successful layer pair may change -> different committed route.  
  Missing evidence: I did not prove that equal-penalty, equal-cost, equal-`getPhysicalIdxSum()` candidates occur in production, or that tied candidates lead to materially different routed results.  
  Confidence: medium.

- `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h` / `ctomtGlsProblemGenerator::runSccIteration`  
  Classification: `schedule-dependent execution with deterministic final result`  
  This is the exemplar pattern: parallel SCC evaluation with atomic early exit. What can vary is which SCC chunks run before `globalDone` flips, how much work is performed, and the reduction tree order. The merged state is `sccEvalResult { value, localLog }`. For the inspected current callers (`evalGskewBuffering`, `evalGskewNotBuffering`, `evalGlate`), the committed boolean result is restored by `reduceOr` / `reduceAnd`, so the application-level answer looks order-independent. The part that remains order-sensitive is `localLog`, because it is concatenated in reduction order.

```289:333:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.h
stateType runSccIteration(
    execPolicy policy,
    size_t n,
    stateType init,
    bodyType body,
    reduceType reduce
    ) const
{
  // ---------- Single-thread ----------
  if (policy == execPolicy::SingleThread) {
    stateType s = init;
    for (size_t i = 0; i < n; ++i) {
      body(i, s);
      if (s.done(init)) {
        break;
      }
    }
    return s;
  }

  // ---------- Multi-thread ----------
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
```

  Downstream effect: boolean result appears deterministic; work performed, runtime, and diagnostic ordering can vary.  
  Missing evidence for elevation: a caller using a non-commutative reduction, or a `body()` with shared side effects that feed the committed result.  
  Confidence: high.

- `ccd/skewopt/soDesign.cc` / `soDesign::identifyTargetSinks`  
  Classification: `schedule-dependent execution with deterministic final result` in the broader sense of order-sensitive heuristic selection that is now explicitly normalized  
  This path computes a heuristic `slackWorst` per sink, sorts candidate sinks, applies a cutoff, and marks sinks after the cutoff as `ignored` and `fixed`. That is a true application-result selection point: it changes which sinks remain optimization targets. The current code explicitly restores determinism by tie-breaking equal slack with `soSink::getIndex()`, and the comment says this was added to fix a nondeterministic issue.  
  Variable order mechanism: equal-score ties.  
  Selected state: which sinks stay target vs. get discarded from further optimization.  
  Determinism restorer: explicit index-based tie breaker before cutoff.  
  Downstream effect: target-set selection is application-significant, but current code appears stabilized.  
  Missing evidence: whether `getIndex()` is stable across all equivalent runs/build modes.  
  Confidence: high.

- `ctssc/lazytns/ctsLazyCostGroup.cc` / `costGroup::collectTouchedSps` and `costGroup::calculateTnsDeltaForSp`  
  Classification: `schedule-dependent execution with deterministic final result`  
  The dirty-D walk is parallel and inserts touched SP ids into a `tbb::concurrent_unordered_set`, so discovery/completion order can vary. The code then drains into ordered containers and builds the job vector in ordered `equal_range` traversal, after which `lazyCost` aggregation is done in a fixed serial order. That matters because `lazyCost::_tns += d` is floating-point addition, which would otherwise be order-sensitive.  
  Variable mechanism: worker completion and insertion order into `touched`.  
  Selected/merged state: touched start-point set, then accumulated best/worst cost deltas.  
  Determinism restorer: ordered `std::set`, deterministic job vector, serial accumulation.  
  Downstream effect: runtime/work can vary, but the committed `lazyQuery` update path appears normalized.  
  Confidence: high.  
  Missing evidence: only runtime validation of the jobs themselves, not of the merge structure.

- `ccd/ctsccd/fmax/fmaxCgSolver.cc` / `fmaxCgSolver::setupClockPathsForCGMt`  
  Classification: `schedule-dependent execution with deterministic final result`  
  This code collects `allCorners`, `allDPaths`, and `allQPaths` in concurrent unordered sets from parallel endpoint traversal. It then explicitly normalizes before commit: corners are copied into a `std::set`, path tuples into a vector that is `std::sort`ed, and `md.addClockPath()` runs afterward in sorted order.  
  Variable mechanism: worker completion and concurrent-set insertion order.  
  Selected/merged state: unique clock-path tuples that populate the `fmaxCgModel`.  
  Determinism restorer: `std::set` / `std::sort` before sequential commit.  
  Downstream effect: work/runtime may vary; the committed model path set/order appears intentionally stabilized.  
  Confidence: high.  
  Missing evidence: none visible in this caller unless `md.addClockPath()` itself has hidden order sensitivity.

- `ctscstr/ctscstrDesign.cc` / `ctscstrDesign::disarmGuardOnDtor` and `noteCcdOrCusInsertedDuringGuard`  
  Classification: `diagnostic/performance-only variation`  
  This is an atomic first-claim pattern. Which caller wins `compare_exchange_strong` can vary, but the code is designed so only one caller resumes the observer and the final guard state is the same. I did not find evidence that different winners change the committed application result; the observed consequence is who performs the deopt and when.  
  Variable mechanism: CAS winner between notifier and destructor path.  
  Selected state: only the deopt actor, not the final observer state.  
  Determinism restorer: single-winner CAS and common `resumeConnDestroyObserver` path.  
  Downstream effect: debug/perf behavior, not proven functional-result variation.  
  Confidence: high.  
  Missing evidence: a path where different winners change visible flow behavior.

## Open Questions
- I could not use CoreStory here because this session does not expose a CoreStory namespace, so this report is from fresh current source inspection only.
- `mscts/fishbone/fbRouter.cc` and `mscts/fishbone/prRouter.cc` still contain comments saying multithreading gives nondeterministic results, but I did not find the scheduler/dispatcher that consumes `canMultithread()` in the visible tree. If that dispatcher lives elsewhere, it is the next place I would inspect.
- I did not find a confirmed current case where thread schedule alone changes a committed application result in the inspected parallel code; the strongest current risk is the fishbone layer-selection comparator plus first-success commit path.

## Summary
The best-supported current application-result risk is the fishbone layer-selection path in `fbRouter`, where a first-success heuristic depends on a comparator whose last tie-break is not strict. By contrast, the GLS SCC helper, `lazytns`, and `fmax` examples are all close semantic matches to the exemplar but appear to restore determinism before commit, so their remaining variability is limited to work done, diagnostics, or runtime unless some deeper job-local side effect exists outside the inspected code.

Natural next steps are a focused runtime repro for tied fishbone layer candidates, and a follow-up inspection of the external fishbone multithread dispatcher if that code is available.
