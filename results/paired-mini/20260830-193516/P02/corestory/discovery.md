## Findings
1. `ccd/skewopt/soDataPowerOptimizer.cc` has a config-dependent shared-state race if `CUS_DATA_POWER_POTENTIAL` is set to `timer_based_delay_potential_with_annotations`.

CoreStory surfaced the CCD/skew-opt area as one of the main parallel execution surfaces, and source inspection confirms a real conflicting-access path under that mode. `soDataPowerOptimizer::initPotentials()` builds one shared `ConeCellCost` object, then uses it from all sink workers inside `ccdUtil::parallel_for`:

```282:323:ccd/skewopt/soDataPowerOptimizer.cc
  std::unique_ptr<ConeCellCost> cellCost;
  cellCost = make_cell_cone_cost(cellCostName, nullptr, &roptInitPublic::getOptGlobal());
  if (!cellCost || !cellCost->initOK()) {
    if (debug()) {
      userOutput::printf(LOG_PREFIX "Cell cost function '%s' failed to initialize\n", cellCostName.c_str());
    }
    return;
  }

  if (debug()) {
    cpuTimer.snapshot();
    userOutput::printf(LOG_PREFIX "initPotentials: initialize potential function: elapsed %g\n", cpuTimer.getElapsed());
    cpuTimer.reset();
    userOutput::printf(LOG_PREFIX "Computing potentials with function '%s'...\n", cellCostName.c_str());
  }

  std::vector<SinkPotential> potentials(sinks.size());

  // Compute potentials in parallel
  ccdUtil::parallel_for(0, sinks.size(), [&](size_t i) {
    soSink *sink = sinks[i];
    SinkPotential &potential = potentials[i];

    // Evaluate potential for each side of sink
    ConeEvaluatorMulti evaluator(*cellCost);
    evaluator.setCombinationalCellsOnly(true);
    std::tie(std::ignore, potential.d) = evaluator.evaluate(GR_SEARCH_BACKWARD, sink->getDpins());
    std::tie(std::ignore, potential.q) = evaluator.evaluate(GR_SEARCH_FORWARD, {sink->getClockPin()});

    // Now evaluate potential for sink itself, if it's a reg
    if (ndmInst *inst = sink->getInst()) {
      potential.reg = cellCost->compute(inst);
    } else {
      potential.reg = 0;
    }
  });
```

That factory can legally produce `TimerBasedCellDelayPotentialCostWithAnnotations`:

```4255:4274:ccd/skewopt/soLogicCone.cc
ctsNS::make_cell_cone_cost(CellCostType type, scenArcIncrDelayMap *origIncrArcDelays,
    const optGlobal* opt, float threshold)
{
  switch (type) {
    case COUNT:
      return std::make_unique<CellCountCost>();
    case AREA:
      return std::make_unique<CellAreaCost>();
    case AREA_POTENTIAL:
      return std::make_unique<CellAreaPotentialCost>();
    case AREA_BASED_DELAY_POTENTIAL:
      return std::make_unique<AreaBasedCellDelayPotentialCost>();
    case AREA_ORDERING_BASED_DELAY_POTENTIAL:
      return std::make_unique<AreaOrderingBasedCellDelayPotentialCost>();
    case TIMER_BASED_DELAY_POTENTIAL:
      return std::make_unique<TimerBasedCellDelayPotentialCost>(opt, threshold);
    case TIMER_BASED_DELAY_POTENTIAL_WITH_ANNOTATIONS:
      return std::make_unique<TimerBasedCellDelayPotentialCostWithAnnotations>(opt, origIncrArcDelays);
    case ROPT_POWER_POTENTIAL:
      return std::make_unique<RoptPowerPotentialCellCost>();
```

And that implementation is explicitly marked non-thread-safe and mutates shared timing annotation state:

```3274:3315:ccd/skewopt/soLogicCone.cc
//! @function TimerBasedCellDelayPotentialCostWithAnnotations::compute
//! @brief this just wraps the non-const version. this potential function is NOT thread safe!
//! @todo this is not really a potential function and should be spin off as something else.
float
TimerBasedCellDelayPotentialCostWithAnnotations::compute(const ndmInst* inst) const
{
  return const_cast<TimerBasedCellDelayPotentialCostWithAnnotations*>(this)->compute(inst);
}

float
TimerBasedCellDelayPotentialCostWithAnnotations::compute(const ndmInst* inst)
{
  float success = 0.0;
  if (!inst) {
    return success;
  }
  ndmModule* currLc = inst->getRefModule();
  if (!currLc) {
    return success;
  }

  int fastestIndex = -1;
  ndmModule* fastestLc = getFastestLibCell(inst, fastestIndex);

  if (!fastestLc) {
    return success;
  }
  if (fastestLc == currLc) {
    return success;
  }

  std::tuple<scenArcIncrDelayMap, scenArcIncrDelayMap> origNewDelays;
  if (computeAndAnnotateIncrArcDelaysMcmm(inst, fastestLc, origNewDelays, /*annotate*/ true)) {
    success = 1.0;
  }
```

Causal chain: parallel sink workers -> shared `cellCost` object -> concurrent `compute()` / cone evaluation calls -> unsynchronized timer-annotation mutation -> corrupted or schedule-dependent potential values -> different sink ranking / optimization choices.  
Classification: established conflicting access if that mode is enabled; schedule-dependent output is plausible and likely.  
Confidence: medium-high for the code path, medium overall because the default is still `ropt_power_potential`, so I did not establish that this mode is used in normal runs.

2. `mscts/mssc/msscGlobal.cc` shows the MT latency flow knows `msuiAppOptions` is not thread-safe, but the codebase still reads the raw app-options object in MT-related code.

`msscGlobal::initOptions()` explicitly says the copied options struct exists because `msuiAppOptions` is not thread-safe:

```320:340:mscts/mssc/msscGlobal.cc
//==============================================================================
// Options Initialization Methods
// This options supposed to absorb the appOptions info and kept read-only, 
// because msuiAppOptions is not thread-safe
//==============================================================================

void msscGlobal::initOptions() 
{
  // Ensure _appOptions and _msData is available
  if (!_appOptions || !_msData) {
    dvuAssert(false);
    return;
  }

  // Initialize all configuration options here using pointer syntax
  _options->enableMultiThread = _appOptions->subtreeEnableMultiThread;
  _options->enableMultiCorner = _msData->isMultiCornerSupportEnabled();
```

But `mssckSize` still reaches back to `getMsGlobal().getAppOptions()`:

```386:404:mscts/mssc/mssckSize.cc
  int filterLeq = getMsGlobal().getAppOptions().splitLatencyKSizeFilterLeq;
  if (filterLeq <= 0) {
    filteredLeqSet = leqSet;  // No LEQ-set filtering
    if (getMsGlobal().getVerbose() >= 10) {
      userOutput::printf("[MSSC] Skip LEQ filtering with driverLibCell. KSizer runtime may not be optimal.\n");
    }
  } else {
    // Enable LEQ-set filtering
    selectLeqCells(driver, driverLibCell, leqSet, filteredLeqSet);
    if (getMsGlobal().getVerbose() >= 10) {
      userOutput::printf("[MSSC] Filtering with driverLibCell information available.\n");
    }
  }
  
  // Apply LEQ limit
  int leqLimit = getMsGlobal().getAppOptions().splitLatencyKSizeLeqLimit;
```

CoreStory identified `msSplit::runMTOptLatency()` and `msmtLatencyFlow` as the MT latency entry path, and source confirms that path constructs `msscGlobal` and then runs a ΓÇ£multi-thread based latency optimizationΓÇ¥ flow. What I could not prove from visible code is whether these particular `mssckSize` accesses happen on worker threads inside `_xformSuite->runAccurate(...)`, because the relevant lower-layer scheduling is outside the inspected implementation.  
Classification: suspicious shared-state pattern with incomplete evidence of overlap, not an established race.  
Confidence: low-medium.

3. The MSGTS singleton helpers (`msTech`, `msgtsTreeTopology`, `msgtsSCSolutions`) use unprotected global `_instance` / `refCount` lifecycles.

Representative pattern:

```434:456:mscts/mscore/msTech.cc
msTech* msTech::getOrCreate()
{
  //Replacement for msTech constructor
  //msTech::removeOrDestroy must be called in pair when msTech::getOrCreate() is called
  refCount++;
  if (exist()) {
    return _instance;
  }

  msTech* newObj = new msTech(&ctsNS::ctsSession::get()->getDesign());
  return newObj;
}

void msTech::removeOrDestroy()
{
  //Replacement for msTech destructor,
  //This function must be called when msTech::getOrCreate() is invoked
  dvuAssertRelease(refCount > 0);
  refCount--;
  if (refCount == 0 && exist()) {
    delete _instance;
    _instance = 0;
  }
}
```

The same pattern appears in `msgtsTreeTopology` and `msgtsSCSolutions`. `msgtsFlow` owns these objects in normal flow startup/shutdown, so there is a clear shared-lifecycle surface. What is missing is proof of same-process overlapping creation/destruction from parallel workers; the ΓÇ£route in parallelΓÇ¥ text in MSGTS did not, by itself, prove concurrent singleton lifecycle calls in this process.  
Classification: suspicious singleton shared-state/lifecycle pattern, not an established race or leak.  
Confidence: low.

## Not Elevated
The CTO exemplar is real as a pattern, but the current code explicitly mitigates it. `ctomtGlsProblemGenerator::findNextProblem()` pre-populates the group-upstream cache before parallel work because `ctoFlowMgr::getUpTermsForGrpTermsOfSclk()` lazily mutates a non-thread-safe `dosMap` cache:

```255:266:ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc
    //to get clock grouplatency efficiently, need to cache the upstream for the grpTerms
    //it is down lazilly and its update may get triggered if being called in multi-thread
    //the cache is based on non-thread-safe dosMap and may cause race condition or crash
    //to avoid race condition, pre-cache this upstream for grpTerms
    if(isBufferingStage() && useCachedGrpUpTerms) {
      for(const ctoSclkBag* cbag : p->sclkbagsOnTerm()) {
        const ctsSclk& sclk = cbag->getSclk();
        (void)flowMgr->getUpTermsForGrpTermsOfSclk(sclk);
```

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
```

Other shared-state patterns I checked look intentionally protected rather than defective:

- `ctssc/lazytns/ctsLazyModel.cc` repeatedly uses job-local accumulation plus main-thread merge, and its PRG trace path is explicitly documented as parallel-safe.
- `ctscstr/ctscstrDesign.cc` uses `tbb::concurrent_hash_map` for per-design observer bookkeeping.
- `mscts/msutil/msSecondaryCost.cc` and `mscts/fishbone/fbBaseRouter.cc` protect their mutable caches / process-global env-refcount with explicit mutexes.

## Lifecycle / Unlock results
I did not find a repo-local `std::thread` / `pthread_create` path that lacked a visible join, detach, shutdown, or owner cleanup path. The main in-repo worker abstraction is `ctsMtMgr`, which owns the task manager and thread objects and tears them down in its destructor. I also did not find an established unlock-without-ownership bug in the inspected mutex code; the visible manual `lock()` / `unlock()` pairs I checked were balanced.

The main remaining uncertainty is below the repository boundary: classes like `mtPool`, `nqTaskManagerHybrid`, and parts of the base `xformSuite` scheduler are not implemented in the inspected files, so I cannot prove lower-layer thread-join behavior or rule out races inside those external components.

Natural next steps are a focused ThreadSanitizer run for the CCD power-potential path with `CUS_DATA_POWER_POTENTIAL=timer_based_delay_potential_with_annotations`, and a narrower source review of the `runAccurate` worker path to see whether `mssckSize` actually dereferences `msuiAppOptions` from parallel workers.
