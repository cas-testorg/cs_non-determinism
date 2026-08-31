## Findings
I did not establish any **confirmed** pointer-dependent nondeterministic application behavior in the inspected paths. The strongest candidates I found are one design-affecting selection path that still needs a missing precondition, and one low-impact reporting path where output order can remain unstable in a tie.

- `mscts/drivers/msAutoTapFlow.cc`, `msClockDrivers::findTemplateTerm`: **insufficient evidence**, but this is the highest-risk candidate I found.
  
  ```4398:4406:mscts/drivers/msAutoTapFlow.cc
  auto* loadNetSet = _msOptions.getLoadNetSet();
  if (loadNetSet) {
    for (ndmNet* net : *loadNetSet) {
      if (net != loadNet) {
        ndmTerm* tmplDrv = net->getFirstFlatDriver();
        if (tmplDrv)
          return tmplDrv;
      }
    }
  }
  ```

  ```1194:1216:mscts/msui/msuiSynRegClkTree.cc
  ndmNet *net = conn->getNet();
  if(net) {
    if (conn->isNetDriver()) {
      msOptions.addLoadNet(net);
      if (net == loadnet) {
        // error, loadnet should be in put net
        msSynRegArgError("Load net ", loadnet->getFullName(),  " should not be on template output pin");
      }
    } else {
      if (net == loadnet)
        found = true;
    }
  }
  ...
  if (!group->getHtreeSections().empty() && templCells.size() > 1) {
    msSynRegArgError("A template group should not have more than one template cell when section flow is enabled.");
    return false;
  }
  ```

  ```4512:4524:mscts/drivers/msAutoTapFlow.cc
  ndmTerm* templateTerm = hasTemplateFlow
                          ? findTemplateTerm(drvTerm, topBlkNet)
                          : drvTerm;

  const size_t  templateSectionIdx = hasTemplateFlow
                                     ? findTemplateSection(templateTerm, sections)
                                     : 0;

  for (auto & htreeSection : sections) {
    ++sectionIdx;
    _isTemplateSection = (sectionIdx == templateSectionIdx);
  ```
  
  - Pointer-dependent construct: raw `std::set<ndmNet*>` in `_loadNetSet`, iterated by default pointer ordering; `findTemplateTerm()` returns the first non-load net driver.
  - Source of possible address variation: `ndmNet*` allocation addresses can differ across equivalent runs.
  - Consumer: section-flow template ownership in `implementAllHtreeSections()`, via `templateSectionIdx` and `_isTemplateSection`.
  - Order sensitivity: yes, if more than one eligible non-`loadNet` entry is present, the chosen template term changes which section is treated as the template-owning section.
  - Mitigation/restoration: none in `findTemplateTerm()` itself.
  - Application path: reg-group/template setup in `msuiSynRegClkTree` populates `_loadNetSet` -> auto-tap section flow resolves `templateTerm` -> section ownership affects tap synthesis behavior.
  - Downstream impact: could change which section consumes the template and therefore alter section-local synthesis behavior.
  - Equivalent-run nondeterminism established: **no**.
  - Confidence: **medium-low**.
  - Missing evidence: I did not prove that section flow can reach this code with more than one valid alternative non-`loadNet` candidate. The nearby guard rejects multiple template cells in section flow, so a real issue would likely require a multi-output template or another source of extra nets.

- `mscts/msui/msuiReportPowerTaps.cc`, `msuiReportPowerTapsCmd::processShieldShapes`: **plausible address-dependent behavior requiring additional evidence**, but likely limited to report ordering.
  
  ```99:103:mscts/msui/msuiReportPowerTaps.cc
  bool compareByOrigin (ndmBlkInst *first, ndmBlkInst *second)
  {
    ndmCoord originF(first->getOrigin());
    ndmCoord originS(second->getOrigin());
    return (originF < originS);
  }
  ```

  ```696:712:mscts/msui/msuiReportPowerTaps.cc
  // De-duplicate by instance pointer before reporting count/output.
  {
    std::unordered_set<ndmBlkInst*> seen(taplist.begin(), taplist.end());
    taplist.assign(seen.begin(), seen.end());
  }
  unsigned cnt = taplist.size();

  if ( cnt == 0 ) {
    ...
  }

  userOutput::printf("Reporting '%d' power tap cells associated with shield shape '%s' for clock net '%s' ...\n", cnt, shape->getFullName().c_str(), blkNet->getPathName().c_str());

  taplist.sort(compareByOrigin);
  ```

  ```535:553:mscts/msui/msuiReportPowerTaps.cc
  for (std::list<ndmBlkInst*>::iterator it=taplist.begin(); it!=taplist.end(); ++it) {
    ndmBlkInst *tap = *it;
    if ( tap ) {
      ...
      if ( myset.find(tap) == myset.end() ) {
        ...
        userOutput::printf(" %s (num=%d)\t%s\t%s\t%s (%s)\t%s\t%s\t(%0.2f %0.2f)\t%0.2f\t%s\n", ...);
  ```
  
  - Pointer-dependent construct: standard `std::unordered_set<ndmBlkInst*>` dedup keyed by raw pointer hash/address.
  - Source of possible address variation: `ndmBlkInst*` addresses can vary across equivalent runs.
  - Consumer: `report_power_taps` serialization order.
  - Order sensitivity: yes, but only if `compareByOrigin()` does not fully order the elements. It compares only origin, so equal-origin taps retain the pre-sort relative order coming from the unordered set.
  - Mitigation/restoration: partial. Sorting by origin removes most variability, but there is no stable tie-breaker for equal origins.
  - Application path: candidate taps collected -> dedup through unordered set -> sorted -> printed line-by-line.
  - Downstream impact: potentially different textual report row order for taps at the same origin. I did not find evidence that design state or decisions change.
  - Equivalent-run nondeterminism established: **not generally**; only plausible for equal-origin ties.
  - Confidence: **medium**.
  - Missing evidence: a real design where multiple reported taps share the same origin and users/scripts depend on row order.

## Effective Mitigations
These are address-dependent constructs I found where the code explicitly restores deterministic downstream behavior before any visible order-sensitive consumer.

- `mscts/mscore/msCharacterizer.h`, `mscts/mscore/msCharacterizer.cc`, `msCharacterizer::processELCPLibCells`: **address-dependent construct with effective determinism restoration**.
  
  ```70:71:mscts/mscore/msCharacterizer.h
  std::map<std::string, ndmModule*> _ELCPRefMap;
  std::map<msLibCell*, ndmModule*> _ELCPLibCellMap; // This must use pointer-compare. Dont use name-compare.
  ```

  ```410:424:mscts/mscore/msCharacterizer.cc
  std::set<msLibCell*> ELCPLibCells;
  std::map<ndmModule*, msLibCell*> lcCache;

  // Sort the keys in the _ELCPLibCellMap by-name to avoid ND when iterating the keys.
  std::vector<msLibCell*> ELCPLibCellVec;
  for (std::map<msLibCell*, ndmModule*>::iterator lcIter = _ELCPLibCellMap.begin(); 
       lcIter != _ELCPLibCellMap.end(); ++lcIter) {
    msLibCell *lc = lcIter->first;
    ELCPLibCellVec.push_back(lc);    
  }
  std::sort(ELCPLibCellVec.begin(), ELCPLibCellVec.end(), msCtsNS::msLibCellCompare());

  // Iterate keys in ELCPLibCellMap using sorted-vector to avoid ND.
  ```
  
  - Pointer-dependent construct: raw-pointer-keyed `std::map<msLibCell*, ndmModule*>`.
  - Source of variation: `msLibCell*` allocation order/address.
  - Consumer: ELCP libcell processing order.
  - Order sensitivity: would be sensitive if the map were iterated directly.
  - Mitigation: keys are copied into a vector and sorted with stable semantic comparator `msLibCellCompare()` before processing.
  - Equivalent-run nondeterminism established: **no**.
  - Confidence: **high**.

- `mscts/msmesh/msIncrMerger.cc`, `msIncrMerger::mergeNodes`: **address-dependent construct with effective determinism restoration**.
  
  ```240:294:mscts/msmesh/msIncrMerger.cc
  // It must use ptr-compare as it is used for ptr-matching operation.
  std::set<msTreeNode *> mergedNodeSet; 
  std::set<msTreeNode *> outputNodeSet;
  ...
  if (keepMerging) {
    sortedInputNodes.clear();
    // Copy to vector and sort by node ID to avoid Coverity POINTER_NONDETERMINISM warning
    TreeNodeVec nextInputNodes;
    for (msTreeNode* node : outputNodeSet) {
      nextInputNodes.push_back(node);
    }
    std::sort(nextInputNodes.begin(), nextInputNodes.end(), msTreeNodeCompare());
    evalDriverNodes(nextInputNodes, sortedInputNodes);
  }
  ...
  outputNodes.insert(outputNodes.end(), outputNodeSet.begin(), outputNodeSet.end());

  // Sort output by node ID for determinism, since outputNodeSet uses pointer ordering
  std::sort(outputNodes.begin(), outputNodes.end(), msTreeNodeCompare());
  ```
  
  - Pointer-dependent construct: raw `std::set<msTreeNode*>` used for membership and temporary accumulation.
  - Source of variation: `msTreeNode*` allocation addresses.
  - Consumer: next merge-round candidate ordering and final `outputNodes`.
  - Order sensitivity: yes, absent normalization the next round and final vector would inherit pointer order.
  - Mitigation: re-materialize into vectors and sort by stable `msTreeNodeCompare()` before reuse and before final output.
  - Equivalent-run nondeterminism established: **no**.
  - Confidence: **high**.

## Open Questions
One additional pattern surfaced, but I did not elevate it:

- `include/ctsICGEstimators.h` and `icg/ctsBanalDelayEstimatorBase.h` explicitly warn that `termPToIntType` / `termPToFloatType` ΓÇ£may lead to NDΓÇ¥ and introduce `ndmPtrUnorderedMap` as the preferred alternative.

  ```50:66:include/ctsICGEstimators.h
  typedef std::map<ndmPointer<ndmTerm>, uint, compareNdmPointer<ndmTerm> >   termPToIntType; // don't use this type, this may lead to ND, please use ndmPtrUnorderedMap below

  template<typename ndmPtrType, typename valueType>
  using ndmPtrUnorderedMap = std::unordered_map<ndmPtrType*, valueType, keyHashWithExpireCheck<ndmPtrType>, compareNdmPointerIsEqual<ndmPtrType>>;

  /**
   * @class ctsNdmPtr2ObjectNonNdType
   * @brief A class template that provides a mapping from ndmType pointers to valueType objects.
   *
   * This class template allows the user to choose between using a custom std::map (may cause ND) or a custom std::unordered_map (not cause ND) for the mapping.
  ```

  I found the warning, but in the paths I inspected I did not establish the required chain from pointer-dependent ordering to an order-sensitive downstream consumer and observable application effect.

## Summary
The fresh investigation found no confirmed pointer-driven nondeterministic behavior. The clearest non-mitigated candidate is `findTemplateTerm()` choosing the first entry from a raw `std::set<ndmNet*>`, but current section-flow guards mean I could not prove multiple eligible alternatives actually reach that path. The clearest observable case is `report_power_taps`, where pointer-hash dedup is followed by only a partial ordering sort, leaving possible row-order instability for equal-origin taps. The strongest semantically equivalent mitigations elsewhere are `msCharacterizer::processELCPLibCells()` and the provided `msIncrMerger::mergeNodes()` exemplar.

Natural next steps are a targeted runtime check for section-flow `_loadNetSet` cardinality before `findTemplateTerm()`, and a quick audit for any other ΓÇ£unordered pointer dedup -> presentation sort without tie-breakerΓÇ¥ report paths.
