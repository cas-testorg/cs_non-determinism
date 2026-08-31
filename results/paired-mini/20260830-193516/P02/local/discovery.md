## Findings

- High: `ccd/skewopt` has a real unsynchronized shared-state defect in solver log-sum-exp population. `soCgSolverUpdater::updateSolverUseTracing()` fans out per-scenario work with TBB, and each worker mutates the same `soCgSolver` through `addToLogSumExpFunc()`. The target storage is plain `std::map`-backed solver state, with no lock, no atomics, and no concurrent container. On the first multi-scenario population of a solver instance, workers can concurrently create scenario entries in the same top-level map; there is also a second parallel population path in `addLogSumExpFuncsToSolver()`. Causal chain: scenario-parallel worker fan-out -> shared solver maps -> unsynchronized `std::map` insert/update -> corrupted or incomplete path-function tables -> unstable skew-opt cost/gradient state, wrong QoR, or crash. I would elevate this to an established shared-state concurrency defect. Schedule-dependent manifestation is established because worker interleaving can change whether the map population succeeds, corrupts, or drops data. Confidence: high.

```925:949:ccd/skewopt/soSolverUpdater.cc
unsigned int
soCgSolverUpdater::updateSolverUseTracing(soCgSolver* solver)
{
  soMonitor mon("traceCtsPathTracer");

  // ...

  std::atomic<unsigned int> numPathsAdded(0);
  tbb::parallel_for((size_t)0, scenarios.size(), [&](size_t i) {
    if (useParallelSubgraphInit) {
      numPathsAdded += updateSolverMoreMt(solver, scenarios[i].first, scenarios[i].second);
    } else {
      numPathsAdded += updateSolver(solver, scenarios[i].first, scenarios[i].second, true);
    }
  });

  if (_verbose > 0) {
    userOutput::printf("Updating solver added %u paths\n", numPathsAdded.load());
  }
  return numPathsAdded;
}
```

```1043:1068:ccd/skewopt/soCG.cc
void
soCgSolver::addToLogSumExpFunc(ndmTerm* ep, unsigned int index1, unsigned int index2, float a1, float a2, float slack,
                               bool isIO, bool target, unsigned pgId, cstrScenario scenario, bool setup, bool enableByDefault)
{
  // ...

  soCgEpLogSumExpFuncsMapType& funcsMap = setup ? _setupLogSumExpFuncs : _holdLogSumExpFuncs;

  soCgEpLogSumExpFuncMapType& funcs = funcsMap[scenario];

  soCgEpLogSumExpFuncMapType::iterator it = funcs.find(ep);

  soCgEpLogSumExpFunc* func = NULL;
  if (it == funcs.end()) {
    func = new soCgEpLogSumExpFunc(ep, -a1, -a2);
    func->addPathSlackFunc(index1, index2, -slack, isIO, target, pgId, enableByDefault);
    funcs[ep] = func;
  } else {
    func = it->second;
    func->addPathSlackFunc(index1, index2, -slack, isIO, target, pgId, enableByDefault);
    dvuAssertRelease(func->_a1 == -a1);
    dvuAssertRelease(func->_a2 == -a2);
  }
}
```

```2090:2113:ccd/skewopt/soSolverUpdater.cc
void
soCgSolverUpdater::addLogSumExpFuncsToSolver(soCgSolver* solver)
{
  // TODO: we should be able to handle setup and hold scenarios in parallel,
  // but this causes a peak memory increase, e.g. see FC-FE/dcp426.
  std::vector<cstrScenario> setupScenarios, holdScenarios;

  // ...

  tbb::parallel_for_each(setupScenarios, [&](cstrScenario& sc) {
      updateInfoVecType& infos = _setupScenarioInfosMap[sc];
      for (unsigned int i = 0; i < infos.size(); ++i) {
        infos[i]->addLogSumExpFuncsToSolver(solver);
      }
    }
  );
  tbb::parallel_for_each(holdScenarios, [&](cstrScenario& sc) {
      updateInfoVecType& infos = _holdScenarioInfosMap[sc];
      for (unsigned int i = 0; i < infos.size(); ++i) {
        infos[i]->addLogSumExpFuncsToSolver(solver);
      }
    }
  );
}
```

- Medium: `ctscto/ctoFlowMgr` contains the same lazy mutable cache pattern as your exemplar, but on the path I inspected it is intentionally pre-populated before later parallel evaluation. The accessor mutates `_upTermsMapOfGrpTerm` from a `const` API with a check-then-populate sequence and no synchronization, so the mechanism is unsafe if a cache miss happens in parallel. However, `ctomtGlsProblemGenerator::findNextProblem()` explicitly pre-warms the cache because the authors already recognized that concurrent lazy population could race or crash. I would classify this as an effectively protected pattern on the inspected GLS path, with residual risk if some other parallel caller reaches a miss after cache clear or bypasses the pre-warm discipline. Nondeterminism is not established on the current path. Confidence: medium.

```5473:5495:ctscto/ctoFlowMgr.cc
const termToConstTermSetMap&
ctoFlowMgr::getUpTermsForGrpTermsOfSclk(const ctsSclk& sclk) const
{
  if(_upTermsMapOfGrpTerm.find(sclk)!=_upTermsMapOfGrpTerm.end()){
    return _upTermsMapOfGrpTerm.at(sclk);
  }
  const auto* termClockGroupMap = getTermClockGroupMapForSclk(sclk);

  _upTermsMapOfGrpTerm[sclk] = {};
  if(!termClockGroupMap){
    return _upTermsMapOfGrpTerm.at(sclk);
  }

  ctsPathAnalyzer pathAnal(*_ctscto->getCtsInfra(), sclk.getClock());
  for (const auto& termGrp : *termClockGroupMap) {
    ndmTerm* term = termGrp.first;
    constTermVecType upTerms = pathAnal.getTermsBetween(term, nullptr);
    auto& cache = _upTermsMapOfGrpTerm[sclk][term];
    for (const ndmTerm* upTerm : upTerms) {
      cache.insert(upTerm);
    }
  }
  return _upTermsMapOfGrpTerm.at(sclk);
}
```

```255:266:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
    //to get clock grouplatency efficiently, need to cache the upstream for the grpTerms
    //it is down lazilly and its update may get triggered if being called in multi-thread
    //the cache is based on non-thread-safe dosMap and may cause race condition or crash
    //to avoid race condition, pre-cache this upstream for grpTerms
    if(isBufferingStage() && useCachedGrpUpTerms) {
      for(const ctoSclkBag* cbag : p->sclkbagsOnTerm()) {
        const ctsSclk& sclk = cbag->getSclk();
        (void)flowMgr->getUpTermsForGrpTermsOfSclk(sclk);
        tmctomtGlsGeneratorDetail.print(" getUpTermsForGrpTermsOfSclk for sclk %s\n",
                                          sclk.getName().c_str());
      }
    }
```

## Not Elevated

- `ctssc/lazytns` has a documented non-thread-safe cache merge in `populateMtJob::updateCache()`, but the callers use it only in single-threaded post-processing after TBB batches. I did not find overlap evidence there.
- `ctsinterf/ctsCstrInterf.cc` uses `tbb::spin_mutex` around its shared routing-rule/repeater caches, including a second guarded insert step that explicitly tolerates duplicate work instead of concurrent corruption.
- `mscts/mssc/msscGlobal.cc` copies values out of `msuiAppOptions` because the source object is not thread-safe, then treats the copied options as read-only. That is a protection pattern, not a defect.
- I did not find an established `THREAD LEAK`. Searches for `std::thread`, `join`, and `detach` turned up essentially no user-managed thread lifecycles; most parallelism is TBB or `ctsMtMgr::runTask()`, which executes queued work before returning.
- I also did not find an established `UNLOCK OF AN UNLOCKED MUTEX`. The manual `lock()`/`unlock()` sites I checked, including `mscts/fishbone/fbBaseRouter.cc` and `mscts/msutil/msSecondaryCost.cc`, had straight-line acquisition/release with no proven early-return or ownership-loss path between them.

## Limits

CoreStory MCP was not available in this session, so this was a fresh source-only investigation. I did not use prior analysis artifacts.

The next validation IΓÇÖd run is ThreadSanitizer on a multi-scenario `ccd/skewopt` useful-skew workload, plus lightweight instrumentation on `ctoFlowMgr::getUpTermsForGrpTermsOfSclk()` to confirm whether any parallel cache miss still occurs outside the GLS pre-warm path.
