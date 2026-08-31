**Verdict:** No confirmed unmitigated pointer-dependent nondeterminism with a complete causal chain to observable CTS results. The strongest validated case matches the exemplar pattern and restores determinism via ID sort. Remaining leads are mitigated, handle/ID-ordered, membership-only, or missing evidence.

Note: the exemplar symbol in source is `msIncrMerger::mergeNodes` (not `mergeDriverNodes`).

---

### 1. Mitigated exemplar — `msIncrMerger::mergeNodes`

| Field | Evidence |
| --- | --- |
| File / symbol | `mscts/msmesh/msIncrMerger.cc` / `msIncrMerger::mergeNodes` |
| Pointer-dependent construct | `std::set<msTreeNode*>` with default pointer ordering (`mergedNodeSet`, `outputNodeSet`) — intentional for ptr-matching |
| Address variation | Heap allocation addresses of `msTreeNode` objects can differ across equivalent runs |
| Order-sensitive consumer | Iteration of `outputNodeSet` feeds next merge iteration and final `outputNodes` |
| Mitigation | `std::sort(..., msTreeNodeCompare())` before next iteration and on final output; `msTreeNodeCompare` orders by `getID()` |
| Classification | **Address-dependent construct with effective determinism restoration** |
| Equivalent-run ND established? | **No** (normalized before downstream use) |
| Confidence | High |

```239:294:mscts/msmesh/msIncrMerger.cc
  // Dont use TreeNodeSet for mergedNodeSet & outputNodeSet. 
  // It must use ptr-compare as it is used for ptr-matching operation.
  std::set<msTreeNode *> mergedNodeSet; 
  std::set<msTreeNode *> outputNodeSet;
  // ...
      // Copy to vector and sort by node ID to avoid Coverity POINTER_NONDETERMINISM warning
      // ...
      std::sort(nextInputNodes.begin(), nextInputNodes.end(), msTreeNodeCompare());
  // ...
  // Sort output by node ID for determinism, since outputNodeSet uses pointer ordering
  std::sort(outputNodes.begin(), outputNodes.end(), msTreeNodeCompare());
```

```8026:8035:mscts/mscore/msTreeNode.cc
msTreeNodeCompare::operator() (msTreeNode *n1, msTreeNode *n2) const
{
  // ...
  return n1->getID() < n2->getID();  
}
```

---

### 2. Same-class mitigations elsewhere (not defects)

These are semantically equivalent to the exemplar: address/iteration sensitivity was recognized and normalized.

| Location | Mechanism |
| --- | --- |
| `ctscto/ctoFlowMgr.cc` / `fillTermToTermBagMapInVec` | Map → vector, then sort by `termBagComparator` |
| `ctscto/ctosc/ctoscGlobal.cc` | Size sort with `getId()` tie-break |
| `ctscto/ctosc/ctoscPreRouteAreaFlow.cc` | Deduplicate via `constTermSetType` (`ndmObjPtrCmpType`) |
| `ctssc/lazytns/ctsLazyCostSp.h` / `costSpCompare` | Order by `costSp::getId()`, not raw pointer |
| `ctscto/ctosc/ctomt/ctomtClone.h` | `std::map` + `ndmObjPtrCmpType` instead of unordered iteration |
| `ctssch/ctsSchCtoOverlapClock.cc` / `collectAndSortDrivers` | Sort drivers by `getId()` before compare/checksum |

---

### 3. Plausible / insufficient (not elevated)

**`ndmObjPtrCmpType` / `compareObjPtr`** — Alias in `ctsTypes.h`; used widely. In-repo comments treat it as *not* raw pointer ordering (`ctomtMpwProblemGenerator.cc`). Definition is outside this repo → cannot prove address dependence.

**`compareNdmPointer` / `termPToIntType`** (`ctsICGEstimators.h`, `ctsTypes.h`) — Explicit ND warning; `return p1 < p2`. Header prefers unordered map. No complete unmitigated consumer chain established; `ndmPointer::operator<` not in-repo.

**Default `std::set<T*>` membership uses** (e.g. `msSplit::runSizeDRC`, `msgtsClustering` dual/single sets) — Lookup/`find` only; processing order comes from other structures. No order-sensitive consumer shown.

**`msSplit::splitLatchForDRC` first-enable selection** — Order-sensitive (`break` on first enable), but iterates `LoadGroupSet` ordered by `msLoadGroupCompare` → `ndmObjectHandle` comparison, not raw address.

---

### Causal-chain summary

| Candidate | Address variation → pointer order → order-sensitive op → observable result |
| --- | --- |
| `mergeNodes` | Yes → Yes → Yes, but **cut by ID sort** before observable merge/output |
| Widespread `TreeNodeSet` | Uses **ID** comparator — not address-dependent |
| Confirmed unmitigated ND | **None** |

**What varies across equivalent runs (when claiming ND):** only the mitigated `mergeNodes` path has a fully evidenced address → order → consumer chain, and that variability is removed before output.

**Next validation (if needed):** inspect external `ndmObjectHandleNS::compareObjPtr` and `ndmPointer::operator<` definitions; Coverity/runtime replay on paths still using `compareNdmPointer` ordered maps with `useNonNdMapType=false`.
