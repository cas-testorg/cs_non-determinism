I did not find a confirmed functional pointer-dependent nondeterminism defect in the current snapshot. The strongest result is a diagnostic-order risk in `mscts/msmesh/msNodeMerger.cc`; the rest of the notable sites were either debug-only output ordering or explicit mitigations that scrub pointer order before it reaches an order-sensitive consumer.

- `Plausible address-dependent behavior requiring additional evidence`: `mscts/msmesh/msNodeMerger.cc`, `msNodeMerger::merge`. The code hashes `std::pair<msTreeNode*, msTreeNode*>` by raw pointer value and then iterates that `std::unordered_map` directly to emit `CTS-979`. If `msTreeNode` addresses differ across equivalent runs because of allocator/heap layout, the bucket order can change, and so can the emitted message order. The downstream consumer I could establish is the diagnostic stream only, not functional clock-tree state. Observable impact is therefore log/message ordering and possibly brittle regression baselines, not synthesis behavior itself. Confidence: medium-high.

```70:220:mscts/msmesh/msNodeMerger.cc
struct pairFuncForNode {
  template <class T1, class T2>
  std::size_t operator() (const std::pair<T1, T2> &p) const {
    auto item1 = std::hash<T1>{}(p.first);
    auto item2 = std::hash<T2>{}(p.second);
    return (item1 ^ item2);
  }
};

// ... nodeMapping is populated ...

for (auto& map : nodeMapping) {
  msTreeNode* fromNode = map.first.first;
  msTreeNode* toNode = map.first.second;
  int numMoved = map.second;
  if (fromNode && toNode && (numMoved > 0)) {
    userMessageManager::message("CTS-979", ...);
  }
}
```

- `Plausible address-dependent behavior requiring additional evidence`: `mscts/mstap/msTapMain.cc`, debug block over `_rootToSinkGroups`, whose type in `mscts/mstap/msTapSynthesis.h` is a raw `std::map<msTreeNode*, ...>` with default pointer ordering. Different `msTreeNode` allocation addresses could change map iteration order, and the debug report prints entries in that order. I did not find a functional consumer on this path; the impact appears limited to debug-output ordering. Confidence: medium.

```64:70:mscts/mstap/msTapSynthesis.h
typedef std::map<ndmTerm *, msTap *>                             TermToTapType;
typedef std::map<ndmTerm *, msTreeNode *>                        TermToNodeType;
typedef std::pair<ndmTerm *, float>                              TermFloatType;
typedef std::vector<TermFloatType>                               TermFloatVecType;
typedef std::map<ndmTerm *, float, ndmObjPtrCmpType>             TermFloatMapType;
typedef std::map<ndmBlkInst*, ndmBlkStatus, ndmObjPtrCmpType>    blkInstStatusMap;
typedef std::map<msTreeNode *, msCstrDesign::SinkGroupVecType>   NodeToSinkGroupsType;
```

```1294:1308:mscts/mstap/msTapMain.cc
if (debug) {
  NodeToSinkGroupsType::iterator it = _rootToSinkGroups.begin();
  for (; it != _rootToSinkGroups.end(); ++it) {
    const msCstrDesign::SinkGroupVecType &sinkGroups = it->second;
    cout << "Associated tap name is: " << it->first->getNodeName() << " for below sink groups:" << endl;
    for (msCstrDesign::SinkGroup *group: sinkGroups) {
      cout << "   group name is: " << group->getName() << " and its type is: " << group->typeName() << endl;
    }
  }
}
```

- `Address-dependent construct with effective determinism restoration`: `mscts/msmesh/msIncrMerger.cc`, `msIncrMerger::mergeNodes`. This is your exemplar pattern and it looks correctly mitigated. The raw `std::set<msTreeNode*>` is used for pointer identity and temporary accumulation, but before re-evaluation and before returning output, the code copies to a vector and sorts with `msTreeNodeCompare()` on stable node IDs. That breaks the causal chain before any order-sensitive downstream use. Equivalent-run nondeterminism is not established here. Confidence: high.

```239:294:mscts/msmesh/msIncrMerger.cc
// It must use ptr-compare as it is used for ptr-matching operation.
std::set<msTreeNode *> mergedNodeSet;
std::set<msTreeNode *> outputNodeSet;

// ...

if (keepMerging) {
  sortedInputNodes.clear();
  TreeNodeVec nextInputNodes;
  for (msTreeNode* node : outputNodeSet) {
    nextInputNodes.push_back(node);
  }
  std::sort(nextInputNodes.begin(), nextInputNodes.end(), msTreeNodeCompare());
  evalDriverNodes(nextInputNodes, sortedInputNodes);
}

outputNodes.insert(outputNodes.end(), outputNodeSet.begin(), outputNodeSet.end());

// Sort output by node ID for determinism, since outputNodeSet uses pointer ordering
std::sort(outputNodes.begin(), outputNodes.end(), msTreeNodeCompare());
```

- `Address-dependent construct with effective determinism restoration`: `mscts/drivers/msDrivers.cc`. `_unusedTemplateCells` is a raw pointer set, but the code materializes it into a vector and immediately sorts by `ndmInst::getId()` before removal. That is the same stable-order normalization pattern as the exemplar. Confidence: high.

- `Address-dependent construct with order-independent semantics`: `mscts/msui/msuiCreateClockDrivers.cc`. `collectPortsFromClockTree()` returns a raw `std::set<ndmPort*>`, but the main consumer just sets the same boolean attribute on each port. I did not find an order-sensitive decision or serialization step on that path, so the final application state looks order-independent. If `debugReconnection` is enabled, the print order could still vary, but that would again be a logging-only effect. Confidence: medium-high.

Open questions and assumptions:

- I could not access a visible `CoreStory` MCP namespace in this session, so this was a fresh source-only investigation rather than a CoreStory-guided one.
- I intentionally did not elevate most `ndmObjPtrCmpType` / `ndmObjectHandleNS::compareObjPtr` containers. The clearest local clue is the comment in `mscts/msui/msuiReconnectClockDrivers.cc` saying `compareObjPtr` dereferences pointees; that does not look like a raw-address ordering primitive, so current source inspection does not establish pointer-address nondeterminism for those sites.
- I also inspected transient pointer-hash tables such as `msgtsNetSolution::copyData` in `mscts/msgts/msgtsSectionTopology.cc`. Those are used for exact-key correspondence lookup during cloning, and I did not find iteration order escaping into selection, traversal, or output there.

The best next validation is to run identical workloads repeatedly with `CTS-979` enabled and with tap debug enabled, then diff only the order of emitted messages. If those reorder across runs, the most direct hardening is to collect entries into a vector and sort by stable node or instance IDs before printing.
