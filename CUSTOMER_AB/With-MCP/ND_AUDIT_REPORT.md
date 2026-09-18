# Non-Determinism Audit — CTS

**Scope:** `/remote/us01home05/carys/cts`
**Reported:** HIGH and MEDIUM only, as requested
**Result:** **6 MEDIUM** from ~2,080 triaged candidates (no HIGH in the default configuration)

> **Proof pass applied.** All six findings were independently re-proved against the
> `prove-nd` / `prove-nd-mt` standard, including app-option defaults via `icc2query` and
> full downstream sink traces. That pass confirmed all six as real and re-graded severities.
> Full proof report: `/u/ranjithp/folders/coreStory/core/nd-audit-cts/cts_nd_details.md`

---

## Bottom line

This codebase is in good shape on determinism. It has a build-time determinism linter, a
set of blessed pointer comparators, and a visible history of deliberate ND fixes — several
carry dated author comments and references to Coverity's `POINTER_NONDETERMINISM` check.
Most of what a mechanical scan flags here is already correct by construction.

Six defects survived verification. Every one shares a single shape:

> **A `std::map` or `std::set` keyed on a raw pointer with the *default* comparator, whose
> iteration order reaches something that mutates the design.**

Five of the six are fixed by adding the project's existing `ndmObjPtrCmpType` comparator to
a container declaration. One (F5) is a true one-liner; the others also need the function
signature or spelled-out iterator types updated to match the new map type.

Severities are graded **in the default configuration**. The two most damaging findings sit
behind app options that default to off (`cts.multisource.enable_mlph_flow` and
`cts.multisource.enable_mv_aware_level_balancing`), which is what keeps this list at MEDIUM.
Turn MLPH on and F6 is a HIGH.

---

## Findings

| ID | Sev | Location | What goes wrong | Fix |
|---|---|---|---|---|
| **F6** | MEDIUM by default · **HIGH when enabled** | `mscts/drivers/msDrivers.cc:711-722` | `findDriverTerm` returns the driver of the **last** net in heap-address order; seeds a different clock/sink context run to run. Gated by `cts.multisource.enable_mlph_flow`, **default false** | Add comparator, or select lowest id instead of last-wins |
| **F1** | MEDIUM | `ccd/ctsccd/fmax/fmaxTimingCostFunction.h:270-337` | Parallel TNS sum is partitioned by thread count; float addition is non-associative, so TNS changes with thread count | Fixed-size partition independent of `maxThreads()` |
| **F2** | MEDIUM | `mscts/msui/msuiGetPowerTaps.cc:66,879-890` | `get_power_taps` returns a Tcl collection ordered by hash of pointer addresses; user scripts see different order | Sort before building the collection |
| **F4** | MEDIUM | `mscts/drivers/msDrivers.cc:8120-8132` | `std::map<ndmHier*,…>` drained into MV-aware driver insertion; equal-depth hiers insert in address order | Add comparator to the map |
| **F5** | MEDIUM | `mscts/msmesh/msLevelBalancer.cc:1745,1770` | `std::map<ndmPowerDomain*,…>` iterated into buffer creation | Add comparator to the map |
| **F7** | MEDIUM | `mscts/drivers/msDrivers.cc:3335,3350` | `std::map<ndmBlkNet*,…>` iterated into `connectTerms`; nets/ports created and named in address order | Add comparator to the map |

---

## F6 — MEDIUM by default, HIGH when MLPH enabled — Primary driver selected by pointer address

**`mscts/drivers/msDrivers.cc:711-722`** · declaration at **`msDrivers.h:493`**

```cpp
std::set<ndmNet*>* _loadNetSet;        // msDrivers.h:493 — default std::less, address order

std::set<ndmNet*>* loadNetSet = _msOptions.getLoadNetSet();               // :711
if (_appOptions.enableMLPHFlow && loadNetSet && loadNetSet->size() > 1 && leafLevel) {
  for (itrS = loadNetSet->begin(); itrS != itrE; itrS++) {
    l_drvTerm = (*itrS)->getFirstFlatDriver();   // :716 — overwritten every pass
    if (l_drvTerm) { drvTerms.insert(l_drvTerm); }  // :720 — blessed set, harmless
  }
}
return l_drvTerm;                                 // :766 — the LAST net wins
```

`l_drvTerm` is reassigned on each pass, so the returned driver is whichever net sorts last
by raw heap address. The set it accumulates into (`drvTerms`) is a blessed `termSetType`
and is fine. The **return value** is the problem, and the return value is what callers use.

**Why this is the highest-impact one.** The returned term seeds clock/sink context and
later driver and tap construction. A different source driver yields a *structurally
different clock tree*, not a reordering of the same tree.

**Narrowed by the proof pass — this matters for the fix.** There are **11 executable call
sites** (not 13; that count included the declaration at `msDrivers.h:633` and the
definition at `:702`). Most are **already neutralized**: they immediately replace the
returned pointer with `getTopLevelDrvTerm(drvTerms)`, which iterates the blessed
`termSetType` and returns a top-hier driver or the deterministic first driver
(`msDrivers.cc:1002-1010`) — for example `checkCfg` at `msAutoTapFlow.cc:1369`.

The real sinks are the three call sites that consume the **raw** return before that
canonicalization: `msAutoTapFlow.cc:4477` (`implementAllHtreeSections`), `:5190`
(auto-section flow), and `:6194` (regular multisource). Each derives a clock from the
returned term and collects sink/ICG terms from it, which then drives section segregation
and tap configuration. Netlist mutation follows via `insertInsts` (`msDrivers.cc:1586`)
and `insertInstsMVAwareForOneHier` (`:8233`).

**Severity.** `cts.multisource.enable_mlph_flow` is bool, **default false**, basic,
block-scoped (confirmed by `icc2query`, and by the registration at
`mscts/msui/msuiAppOptions.cc:3991`). No local script or regression sets it. So this is
MEDIUM in the default configuration and HIGH wherever MLPH is turned on. The guard
`loadNetSet->size() > 1` is exactly the condition that makes order matter.

**Correction on the linter bypass.** The signature at `:702` carries `//LINTER_BYPASS`, and
I originally read that as a deliberate waiver of this defect. It is not. The linter
suppresses **per line** (`linter:112`, `:117`), and the unsafe declaration is at `:711`,
which carries no bypass. The signature-line bypass almost certainly covers signature/type
noise instead. So this construct was never waived — the linter simply has no rule that
catches it, since `_loadNetSet` is reached through an accessor rather than declared inline.

**Fix** — either:
```cpp
std::set<ndmNet*, ndmObjPtrCmpType>* _loadNetSet;   // msDrivers.h:493
```
or keep the set and pick deterministically (lowest object id among discovered drivers)
rather than last-wins. **Cost:** negligible — small sets, comparator swap is free.

---

## F1 — MEDIUM — TNS depends on thread count

**`ccd/ctsccd/fmax/fmaxTimingCostFunction.h`**

```cpp
size_t numberOfThreads = size_t(this->maxThreads());            // :233
newRanges = calculateRanges(relations, numberOfThreads);        // :246
size_t averagePathCount = std::ceil(double(allPathsCount)/double(threadCount));  // :126

std::vector<double> resultsPerThreadTNS(numberOfThreads, 0);    // :270
for (size_t threadIndex = 0; threadIndex < numberOfThreads; ++threadIndex) {
  resultTNS += resultsPerThreadTNS[threadIndex];                // :336-337
}
```

Work is split into exactly `numberOfThreads` chunks, each accumulating a partial sum, and
the partials are then added together. Floating-point addition is not associative, so
changing the thread count regroups the additions and yields a slightly different TNS.

The per-run order is stable — this is **not** a same-machine flake. It breaks
*reproducibility across machines or `maxThreads` settings*, which matters for QoR
comparison and regression baselines.

**Fix:** partition into a fixed number of chunks independent of `maxThreads()`, so the
summation tree is identical regardless of how many threads execute it.

---

## F2 — MEDIUM — `get_power_taps` returns results in hash order

**`mscts/msui/msuiGetPowerTaps.cc`**

```cpp
typedef dosUnorderedSet<ndmBlkInst *> blkInstSetType;   // :66 — hashed on pointer address

std::vector<ndmInst*> l_ptaps;
for (auto inst : myset) {                               // :879 — hash order
  l_ptaps.push_back(inst->getInst());
}
Tcl_Obj *tclResult = clct_list_to_collection(CciIterUtils::container(l_ptaps), ...);
setResult(tclResult);                                   // :890 — returned to the user
```

This is a **user-facing Tcl command**. The returned collection's order varies between runs,
so any script doing `lindex`, `foreach` with early exit, or writing the list to a file sees
run-to-run differences.

**Fix:** sort `l_ptaps` with `ndmObjPtrCmpType` (or by name) before building the collection.
Keep the hash set for lookup; materialize a stable order once at the boundary.

*Related, below threshold:* `mscts/msui/msuiReportPowerTaps.cc:760-771,1022-1035` has the
same pattern but only affects report text, so it is LOW and not counted here.

---

## F4 — MEDIUM — MV-aware driver insertion ordered by address

**`mscts/drivers/msDrivers.cc:8120-8132`**

```cpp
msClockDrivers::convertToVector(
  const std::map<ndmHier*, msDriverLoadInfo>& inputParamMap,   // default std::less
  std::vector<std::pair<ndmHier*, msDriverLoadInfo>>& infoInVector)
{
  for (auto& itr : inputParamMap) {                     // address-order walk
    infoInVector.push_back(std::pair<...>(itr.first, itr.second));
  }
  std::sort(infoInVector.begin(), infoInVector.end(), compareHierDepth);   // depth only
}
```

`compareHierDepth` (`:8136-8142`) compares `getDepthFromTop()` and nothing else, so hiers at
equal depth keep the address order they came out of the map with.
`insertInstsMVAware` (`:8193-8233`) then applies driver insertion per entry in that order.

**Gating (from the proof pass):** requires `_msgtsOptions.getUncommittedBlockInfo()`
non-empty, `isLeaf` true, and no section at `:8185`. It needs **equal-depth sibling
uncommitted hierarchies** to exist — if every hier has a unique depth, the depth sort fully
canonicalizes and there is no defect. Such siblings are accepted by
`-uncommitted_hierarchy_boundary` parsing (`mscts/msui/msuiCreateClockDrivers.cc:692`).

**Fix:** add `ndmObjPtrCmpType` to the map, or give `compareHierDepth` a final key:
`return elem1.first->getId() < elem2.first->getId();` Note this is *not* a single-line
change — the `convertToVector` signature and any spelled-out iterator types over the same
map must be updated to match, or it will not compile.

---

## F5 — MEDIUM — Buffer insertion ordered by power-domain address

**`mscts/msmesh/msLevelBalancer.cc:1745`** · iterated at **`:1770`**

```cpp
std::map<ndmPowerDomain*, TermToUnsignedMap> domainToLoads;   // :1745 — default std::less

for (const auto& domainPair : domainToLoads) {                // :1770 — address order
  ...
  insertBuffers(node, driver, domainLoadVsBufferCount, clock,
                lbNode->getLBTree(), domainBufferCount, targetVA, checkOnly);  // :1791
}
```

`insertBuffers` creates real buffer instances (`:1868` → `insertBuffersMultiDriver` `:1906`,
recursing at `:1927`). Visit order changes the generated instance-name sequence and the
placement sites consumed near the shared driver. The domains' load sets are disjoint, but
the physical resources they compete for are not.

**This one is clearly an oversight, and its own header says so.** `msLevelBalancer.h:60-70`
declares every iterated pointer-keyed map with a deterministic comparator and annotates the
single exception:

```cpp
typedef std::map<ndmTerm*, unsigned, ndmObjPtrCmpType>  TermToUnsignedMap;   // :63
typedef std::map<ndmNet*, msLBTreeNode*> NetToLBNodeMap; // :69 (No need of comparator as we're not iterating)
typedef std::set<ndmPowerDomain*, ndmObjPtrCmpType>     pdmSetType;          // :70
```

Line 69 states the rule — comparator when you iterate — and it does not apply here because
this map *is* iterated. Line 70 proves `ndmObjPtrCmpType` accepts `ndmPowerDomain*`.

**Fix (one line, no change at the use site):**
```cpp
std::map<ndmPowerDomain*, TermToUnsignedMap, ndmObjPtrCmpType> domainToLoads;
```

**Reachability:** gated by `cts.multisource.enable_mv_aware_level_balancing` — bool,
**default false**, *hidden*, block-scoped (confirmed by `icc2query`) — plus
`lbNode->isCrossingMVBoundary()` at `:1835`. That containment is why this is MEDIUM rather
than HIGH. The function is dated Aug 2025 (`:1727`), postdating the convention it misses.

---

## F7 — MEDIUM — Load connection ordered by block-net address

**`mscts/drivers/msDrivers.cc:3335`** · iterated at **`:3350`**

```cpp
std::map<ndmBlkNet*, std::vector<ndmTerm*>> nets;     // :3335 — default std::less
...
nets[l_blkNet].push_back(*itrS);                      // :3347
...
for (itr1 = nets.begin(); itr1 != itr2; itr1++) {
  connectTerms(p_driver, itr1->second, string(""));   // :3353 — mutates connectivity
}
```

The inner vectors are safe — they are built while walking `unassignedLoads`, a blessed
`termSetType`. The outer key order is raw address order, so hierarchical nets and ports are
created and named in a sequence that varies run to run.

**Fix:** `std::map<ndmBlkNet*, std::vector<ndmTerm*>, ndmObjPtrCmpType> nets;` — plus the
spelled-out iterator type at `:3350`, which names the map type explicitly and must be
updated in step. The proven sink is that `connectTerms` consumes **shared net/port
counters**, so the auto-generated names depend on call order.

---

## One methodology note worth carrying forward

A large share of the initial candidates — 23 promoted findings across two triage passes,
including 16 marked HIGH — rested on this argument:

> *"The comparator sorts by distance/delay/area and has no `getId()` tie-break, and the
> sorted order drives a first-accept or top-N decision."*

**That argument is wrong on its own, and all 23 were rejected.**

`std::sort` is **unstable**, but unstable is not the same as **non-deterministic**.
Introsort produces the identical permutation on every run given the same input sequence and
comparator. A missing tie-break therefore creates no run-to-run variation by itself. It is a
genuine robustness concern — results can shift across a compiler or STL upgrade — but that
is build-to-build fragility, not the run-to-run ND this audit targets.

The correct test has two parts, and the first is the one that gets skipped:

1. **Is the input sequence non-deterministic?** It is only if it comes from a raw-pointer
   container with the default comparator, an iterated pointer-keyed hash container, thread
   completion order, or time/randomness. Vector loops, tree and graph traversals,
   value-keyed maps, and blessed-comparator containers are all deterministic.
2. **Only then:** does an order-sensitive sink consume the order?

Applying step 1 dissolved every one of those 23 findings. It also explains why F4 is real:
not because `compareHierDepth` lacks a tie-break, but because `convertToVector` drains a
pointer-keyed map whose ordering *is* the heap address. The missing tie-break merely fails
to repair the damage.

---

## What was checked and cleared

| Area | Candidates | Outcome |
|---|---|---|
| Pointer-keyed hash containers | 421 | 0 — lookup-only, or sorted before use |
| Ordered pointer containers (pattern 1.2) | 500 | 1 LOW (debug dump), below threshold |
| Pointer sorts, `ccd`/`mscts` | 237 | 1 real (F4); 10 rejected on provenance |
| Pointer sorts, `ctscto`/`cts` | 166 | 0 — all 12 claims rejected on provenance |
| Raw-pointer map/set sweep | 716 decls | 1 real (F5); 54 iterated, rest already fixed |
| Multithreading / parallel reductions | ~175 | 1 real (F1) |
| Wrappers and name-keys | 214 | 2 (F2 + one LOW) |
| Result integrators | 130 | 0 — snapshot pass-through, no local iteration |
| Skew solvers and optimizers | 100 | 0 — lookup/membership only |
| DB mutators and router | 140 | 2 real (F6, F7); router dismissed on reachability |

**Deliberately excluded**, with reasons:

- **`ctsroute::ctsRouter` `_nets`** — `std::map<ndmNet*, ctsRtNet*>` with the default
  comparator, walked by five loops including congestion-coupled routing. On shape alone this
  would be the worst defect found. It is excluded because nothing reaches it:
  `ctsRouterInterf`, the module's only entry point, appears nowhere outside its own two
  files, and four of the five loops are not even forwarded through it. If `ctsroute` is ever
  wired up, fix `ctsRouter.h:64` first — one line fixes all five loops.
- **`ctoBpScaler` `bpSinkSet`** (`ctscto/ctoBpScaler.cc:583`) — address-hashed set feeding
  constraint work, but the authors documented it at `:576-579`, explained that results land
  in an `ndmObjPtrCmpType`-ordered map, and queued a `std::set` conversion. Residual risk is
  the `getHierBpTerm` first-claim-wins path, which is safe only under an invariant asserted
  in a comment rather than enforced in code.
- **`getTotalInitialPower()`** (`ccd/ctsccd/power/ccdpwProblemGenerator.h:179-183`,
  `ccd/ctsccd/voltagedrop/ccdvdProblemGenerator.h:180-182`) — accumulates floats over a
  `std::map<ndmInst*, float>` in address order. Real ND shape, but no callers. Worth fixing
  before anyone wires it up.
- **`_refOTrans`** (`ctscto/ctoDrcFix.cc:4841`) and **`selected`**
  (`ctsutil/ctsCharacterizer.cc:810`) — genuine raw-pointer maps with `std::less`, not
  iterated today. Note the linter has no `ndmModule*` rule, so neither would be caught if
  someone adds a range-for later.

---

## The pattern to copy

The codebase already contains the right fix, with a dated comment showing it was a
deliberate ND repair:

```cpp
// ctssch/ctsPowerDrivenGateRelocator.cc:1066-1071
// Shuai: drivers must be sorted for deterministic iteration, 07/12/2023
std::vector<ndmInst *> allDrivers;
for (auto iter = _hashTblDrivers.begin(); iter != _hashTblDrivers.end(); ++iter) {
  allDrivers.push_back(iter->second);
}
std::sort(allDrivers.begin(), allDrivers.end(), ndmObjPtrCmpType());
```

Keep the hash container for `O(1)` lookup; materialize a stable order exactly once, right
before the order-sensitive loop. Use this shape for F2. For F5 the simpler fix applies —
add `ndmObjPtrCmpType` to the declaration and change nothing else. F4 and F7 need the same
comparator plus matching updates to the function signature and any spelled-out iterator
types that name the map.

---

## Suggested order of work

1. **F5** — genuinely a one-line comparator addition. Lowest risk, highest
   certainty, and its own header already proves the comparator accepts the key type.
2. **F6** — highest impact when reachable. Fix the three raw-return call sites
   (`msAutoTapFlow.cc:4477`, `:5190`, `:6194`) or the container; the other call sites are
   already canonicalized by `getTopLevelDrvTerm`. Leave the `:702` `LINTER_BYPASS` alone —
   it does not cover the unsafe line.
3. **F7, F4** — comparator plus signature and iterator-type updates; still small,
   but they touch more than one line so they need a compile check.
4. **F2** — small change at the Tcl boundary; user-visible, so worth doing deliberately.
5. **F1** — needs design thought to decouple partitioning from `maxThreads()`. Confirm with
   a thread-count A/B (1 vs N) comparing **raw or full-precision** TNS, never a rounded
   report value.

---

## Verification status

| Finding | Source-level proof | Runtime confirmation |
|---|---|---|
| F1 | Complete — dispatch, slot indexing, serial merge all traced | **Not run.** Thread-count A/B designed but not executed |
| F2, F4, F5, F6, F7 | Complete — address-ordered input and mutation sink traced | **Not run.** No reproduced design diff |

Every finding is proved at the source level: an address-ordered (or thread-count-dependent)
input, and a concrete sink that observes it. None has been demonstrated on a running design,
so each should be confirmed against a real testcase before a fix is signed off. For F1 the
confirmation is a 1-vs-N thread-count A/B on raw TNS bits.

Two dependencies sit outside this source slice and their internals could not be read:
`util/dosMap.h` / `util/dosUnorderedSet.h` (container ordering semantics) and the Tcl
`clct_list_to_collection` implementation (whether the collection layer re-sorts, which
would reduce F2).
