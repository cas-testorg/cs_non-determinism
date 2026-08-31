Using CoreStory first, I narrowed the investigation to the lazy-TNS / skew-opt paths in `ctssc/lazytns`, plus the state-heavy candidates it highlighted in `ccd/skewopt`, `ctscto/ctosc/ctomt/gls`, `ccd/ctsccd/fmax`, and the sentinel exemplar area in `mscts/msutil`. After targeted source inspection, I found one elevated candidate and downgraded the rest to intentionally guarded or effectively mitigated patterns.

## Findings
`ctssc/lazytns/skewSlackCalculator.cc`, symbol `skewSlackCalculator::adjustTimingSlackBySkewImp` is the only current candidate I would elevate.

The state in question is the incoming `slack` value plus the launch/capture clocks `qClk` and `dClk`. Their validity is supposed to be established by `checkInputs(...)`, which rejects uninitialized slack, invalid clocks, non-propagated clocks, and in2out paths. But both overloads ignore that rejection and continue anyway:

```56:76:ctssc/lazytns/skewSlackCalculator.cc
float
skewSlackCalculator::adjustTimingSlackBySkewImp(float slack, const grNode& qNode, const grNode& dNode, const cstrClock& qClk, const cstrClock& dClk, const cstrScenario& scen, bool isSetup, ctsscGlobal* g, ctsClockArrivalMap* cache, int debug)
{
  if (not checkInputs(slack, qNode, dNode, qClk, dClk, debug)) { nwmathFloat::getUninitValue();}

  skewSlackCalculator ssc(qNode, dNode, qClk, dClk, scen, isSetup, g->getTimerInterf(), g->_ctsInfra, cache, debug);
  float skewSlack = ssc.calculateSkewSlack(slack);

  return skewSlack;
}

std::pair<float, float>
skewSlackCalculator::adjustTimingSlackBySkewImp(float slack, const grNode& qNode, const grNode& dNode, const cstrClock& qClk, const cstrClock& dClk, const cstrScenario& scen, bool isSetup, timerInterf* timer, ctsInfra* infra, ctsClockArrivalMap* cache, int debug)
{
  if (not checkInputs(slack, qNode, dNode, qClk, dClk, debug)) { nwmathFloat::getUninitValue();}
```

That failed guard is then followed by a consumer that assumes the value is valid:

```309:338:ctssc/lazytns/skewSlackCalculator.cc
float
skewSlackCalculator::calculateSkewSlack(float slack)
{
  dvuAssertRelease(nwmathFloat::isInit(slack));
  dvuAssertRelease(_qNode.isValid() && _dNode.isValid());

  float lArrival = reuseOrGetClockArrival(_qNode, _lck, _scenario, _isSetup, false/*isD*/, _timer, _infra, _cache, _debug);
  float cArrival = reuseOrGetClockArrival(_dNode, _cck, _scenario, _isSetup, true/*isD*/, _timer, _infra, _cache, _debug);

  if (nwmathFloat::isUninit(lArrival) || nwmathFloat::isUninit(cArrival)) {
    // ...
    return nwmathFloat::getUninitValue();
  }

  _skew = calculateSkew(lArrival, cArrival, _isSetup);
  float skewSlack = calculateSkewSlack(slack, _skew);
```

CoreStory identified `ctssc/lazytns` as a main consumer side for skew-adjusted slack, and that matches the local call paths. One realistic caller is the MT lazy-path updater, which checks only clock validity, not propagation, before handing the values to `adjustTimingSlackBySkew(...)`:

```329:343:ctssc/lazytns/ctsLazyModelMtUtil.cc
void
traceLazyPathMtJob::adjustTimingSlackBySkew(ctsPathTracer::fullPath* pp, grNode qNode, grNode dNode)
{
  if (_model->isSkewOptMode() == false) { return; }

  grNode dckNode;
  if (skewSlackCalculator::getCkNodeFromDNode(dckNode, dNode, _model->getGlobal()->_ctsInfra->getTimer()) == false) {
    userOutput::printf("CTO_SOLVER: cannot get ck node from d node %d: %s\n", int(dNode.getId()), dNode.getTermName().c_str());
    pp->_slack = nwmathFloat::getUninitValue();
  } else {
    dvuAssertRelease(pp->_qClock.isValid() && pp->_dClock.isValid());
    pp->_slack = skewSlackCalculator::adjustTimingSlackBySkew(pp->_slack, qNode, dckNode,
                  pp->_qClock, pp->_dClock, _scenario, _isSetup, _model->getMode(), _model->getGlobal(),
```

Assessment:
- Initialization / validity path: external timing/path-trace population -> `checkInputs(...)`.
- Consumer: `calculateSkewSlack(slack)` and the clock-arrival queries beneath it.
- Guard or mitigation: present, but broken in this symbol because it does not return.
- What local source establishes: a rejected validity state is still consumed. That is a real control-flow defect.
- Downstream impact: lazy-TNS / skew-opt path scoring can proceed with timing context the function has already declared invalid; in debug builds this can trip the `isInit(slack)` assertion, and in non-asserting builds it can produce misleading ΓÇ£computed vs. skippedΓÇ¥ behavior for skew-adjusted slack.
- Undefined behavior: not established as a raw C++ indeterminate-memory read. This is invalid sentinel/optional-state consumption, not proven UB from stack garbage.
- Nondeterminism: not established.
- Confidence: medium-high.
- Missing evidence: a concrete runtime case showing `pp->_slack` uninitialized or `pp->_qClock` / `pp->_dClock` valid-but-unpropagated at this caller, to confirm how often the bad branch is hit in production flows.

## Downgraded / Mitigated Patterns
`msDRClimits` in `mscts/msutil/msUtil.cc` matches your exemplar and looks intentionally safe. The constructor seeds sentinel values, and the visible consumers gate on `nwmathFloat::isInit(...)` before comparison:

```4753:4790:mscts/msutil/msUtil.cc
msDRClimits::msDRClimits()
  : _maxFO(-1), _maxELCP(0), _worstTranTerm(0)
{
  _maxLen = _maxCellEm = _maxStageDelay = nwmathFloat::getUninitValue();
  //reserving space for 32 corners for now.
  _maxCap.assign(32, nwmathFloat::getUninitValue());
  _maxTran.assign(32, nwmathFloat::getUninitValue());
}

bool
msDRClimits::isLenOk(float len) const
{
  if (nwmathFloat::isInit(_maxLen) && (len > _maxLen)) {
    return false;
  }
  return true;
}
```

`ccd/ctsccd/fmax/fmaxProblemSeed.h` looked suspicious at first because `_implementationResolution` starts as a sentinel, but the only current consumer I found, `snapBudgetCost(...)`, explicitly initializes it on first use before reading it back. I would classify that as intentional optional-state handling, not an invalid read.

`ctssc/lazytns/ctsLazyModel.cc` has an explicitly deferred-init `nodeData` struct with raw `slack` / `hslack` members, but the same function fills every element in a `parallel_for` before the consumer loop reads them. That is a suspicious-looking pattern, but the local control flow currently mitigates it.

CoreStory also pointed me at `ccd/skewopt/soSolverChecker.cc` and `ctscto/ctosc/ctomt/gls/ctomtGlsProblemGenerator.cc`. After inspection, I would not elevate either:
- `soSolverChecker` initializes `launchIndex` / `captureIndex` to sentinels, but `soCgEpLogSumExpFunc::getWorstSlack(...)` writes them whenever it returns an initialized worst slack, and the checker only dereferences `_solver->_terms[launchIndex]` on that initialized-slack path.
- `ctomtGlsProblemGenerator` uses map membership as the validity flag for `sharedSccCtx`; `assembleSccContextFromCache(...)` only consumes entries after the `glateTarget.find(...)` check, and the producer inserts `rootLateEarly` before `glateTarget`.

## Open Questions
The main remaining gap is runtime confirmation for the `skewSlackCalculator` issue: whether the MT lazy-path updater actually sends uninitialized slack or valid-but-unpropagated clocks into `adjustTimingSlackBySkew(...)` in real flows. A focused assertion/logging run around that caller would answer that quickly.

If you want, I can next do a narrower pass just on `ctssc/lazytns` and map every call path into `adjustTimingSlackBySkew(...)`, separating the callers that fully prevalidate inputs from the ones that rely on the broken internal guard.
