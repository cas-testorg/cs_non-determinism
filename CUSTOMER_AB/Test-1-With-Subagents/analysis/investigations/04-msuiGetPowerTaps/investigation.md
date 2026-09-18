# Investigation Checkpoint — `get_power_taps` Non-Determinism Candidate

Following the **agentic-bug-resolution** playbook. No source was modified. CoreStory scope: **project 10 (`cts-code`) only**; project 9 (`cts-code2`) was not used. The reported defect was treated as a hypothesis.

## Problem Summary

Reported hypothesis: in `mscts/msui/msuiGetPowerTaps.cc`, a container of `ndmBlkInst*` (line 66) is iterated in an unstable order (lines 879–890); if that container hashes/orders on raw pointer addresses and the order reaches a Tcl result, `get_power_taps` output could be run-to-run non-deterministic.

The candidate mechanism **exists structurally**, but its most load-bearing premise — that the container keys on raw pointer addresses — is **not established by available evidence, and the codebase's own conventions point the other way.** Two external definitions needed to confirm or refute it are absent from both the workspace and the CoreStory index.

## Components Involved

- **Command:** `get_power_taps` (Tcl), class `msuiGetPowerTapsCmd`, namespace `msuiGetPowerTapsNS`.
- **Container (line 66):** `typedef dosUnorderedSet<ndmBlkInst *> blkInstSetType;` → the `myset` accumulator.
- **Downstream (lines 879–890):** iterate `myset` → `std::vector<ndmInst*> l_ptaps` → `clct_list_to_collection(CciIterUtils::container(l_ptaps), rHandle, theHier)` → `setResult(...)`.

## Findings Against the 13 Questions

**1. Part of the production build — YES (direct source).** `msuiGetPowerTaps.cc` is listed in `CPPFILES` of `mscts/msui/Master.make` (line 76; module `msui`, `FEATURE_AREA = nwtn.mscts`).

**2. Reachable from production execution — YES (direct source).** `msctsPackage.cc:36` → `msCtsUI().createCommandsAndVariables()` → `msctsui.cc:127` `msuiGetPowerTaps().createCommandsAndVariables(interp, cmdGroup)` → `msuiGetPowerTaps.cc:914` `addCommand(new msuiGetPowerTapsCmd(interp), cmdGroup)`. It is a registered Tcl command. CoreStory (project 10) corroborated it as a user-facing command returning a collection of **cell** objects.

**3. Exact concrete container type (direct source).** `dosUnorderedSet<ndmBlkInst *>` — a **Synopsys DOS-family container**, distinct from `std::unordered_set`. Defined in `util/dosUnorderedSet.h`.

**4. Container implementation / hash / comparator — UNRESOLVED (definition external).** `util/dosUnorderedSet.h` and the underlying `dosContainer::keyHash` / `dosContainer::keyCompare` are **not in the workspace** (no `util/`, `ndm/`, `tcl/` dirs) and **not in the CoreStory index** (`filter_chunks` returned 0 chunks for `dosUnorderedSet.h`, `dosContainer.h`, `ndmObjectHandle.h`). I did not stop at the typedef, but the implementation is not reachable from either evidence stream.

**5. What actually participates in hashing/ordering — evidence points to object ID/type, NOT raw address (reasoned inference from adjacent direct source).** In `export/ctsTypes.h`:
- `keyHashWithExpireCheck` delegates hashing to `dosContainer::keyHash()(p)` (lines 683–704).
- `compareNdmPointerIsEqual` delegates equality to `dosContainer::keyCompare()`, documented as comparing **"based on their ndmID and ndmType"** (lines 715–740).
- Ordered `std::set<ndm*>` typedefs use `ndmObjPtrCmpType = ndmObjectHandleNS::compareObjPtr` (lines 63, 124–129).

These show the codebase's canonical ndm-pointer hash/compare hooks are **object-identity based**. Per the task guardrail, I am **not** classifying this container as pointer-address-dependent merely because its element is a pointer — and the available convention evidence actively contradicts the address-dependence premise. However, the concrete `dosContainer::keyHash` body is external/unseen, so ID-based keying for `dosUnorderedSet` specifically is **strong inference, not confirmed source.**

**6. Population / insertion-order variability (direct source).** `myset` is filled from multiple traversals: region queries `ndmBlkQuery::instIter` (`processSingleShieldShape`, `processShieldShapes`), `ndmHierRoot::instIter` (`collectTaggedTapsInCurrentHierForShape`, `collectPTapsInCurrentHierForNets`), `ndmHier::findInstWildCard` (`collectPTapsInCurrentHier`), `getFlatNetIter` (`run`), and an `ndmObjectIdSet` (`findTapCellInfo`). Whether these upstream iterators are ID-ordered is **external/unresolved**. Note: for a genuinely unordered container, insertion order matters for iteration order only if the hash preserves it — which returns to Q4/Q5.

**7. What controls iteration order — the `dosUnorderedSet` bucket layout (hash + bucket count).** If the hash is object-ID based and IDs are stable across equivalent runs, iteration order is **deterministic** despite being "unordered." If it were address-based, order could vary. This is the pivotal unresolved link (Q4).

**8. Trace into downstream (direct source).** `myset` order → `l_ptaps` push order (lines 880–882) → `clct_list_to_collection` (line 888) → `setResult`. There is **no sort of `l_ptaps`** before conversion (contrast: `taplist.sort(compareByOrigin)` at line 410 and `compareShapes` sorts exist only on intermediate geometric lists, not the final result vector).

**9. Downstream neutralizer — UNRESOLVED (definition external).** Whether `clct_list_to_collection` (`tcl/clct.h`) sorts/canonicalizes (e.g., by object ID) or preserves input order is **not determinable**: the file is absent from workspace and index. Synopsys "collection" semantics are also set-like, so a downstream Tcl consumer that compares as a set or sorts by name would neutralize any ordering variation — but that depends on the (external) consumer.

**10. Credible path to observable ND — NOT ESTABLISHED.** A real defect requires **all three** links to hold: (a) `dosUnorderedSet` hashes by address so `myset` iteration varies run-to-run; (b) `clct_list_to_collection` preserves that order; (c) the downstream Tcl consumer observes collection order without sorting/set-normalizing. Link (a) — the core premise — has adjacent source evidence **against** it; (b) and (c) are unverified. No single link is currently confirmed.

**11. Runtime/config conditions required.** Would require: address-dependent hashing to be real; a design with ≥2 qualifying power-tap cells; and a consumer/flow that prints the collection in raw internal order. `-verbose`/`-dangling` are hidden options and not required.

**12. Blast radius if real.** Limited to `get_power_taps` output ordering (a reporting/query command over power-tap cells on shield shapes). No evidence it feeds optimization/placement decisions; impact would be cosmetic/diff-noise in the returned collection rather than QoR — pending confirmation of downstream consumers.

**13. Unresolved evidence (requires SME / external source / runtime).**
- Body of `dosContainer::keyHash` / `keyCompare` and `dosUnorderedSet` (`util/`) — **the decisive question.**
- Behavior of `clct_list_to_collection` (`tcl/clct.h`) — sort/canonicalize vs. preserve order.
- Ordering guarantees of the upstream ndm iterators (`ndmBlkQuery`, `ndmHierRoot::instIter`, `findInstWildCard`, `ndmObjectIdSet`).
- The actual downstream Tcl consumer/test of `get_power_taps` output (no consumer exists textually in this repo).

## Evidence Classification

- **Direct source (this workspace):** build membership; command registration/reachability; concrete type `dosUnorderedSet<ndmBlkInst*>`; absence of a final-result sort; the ndmID/type-based hash/compare conventions in `export/ctsTypes.h`.
- **CoreStory application evidence (project 10):** confirmed `get_power_taps` is a Tcl command returning a cell collection; confirmed DOS key-hook definitions and `clct_list_to_collection` are **not** in the index; confirmed sibling commands (e.g., `ctsGetClockTreePins.cc`) *do* sort deterministically before output, whereas `get_power_taps` does not sort its final vector.
- **Reasoned inference:** `dosUnorderedSet` most likely keys on ndm object ID/type (not address), making run-to-run iteration order most likely stable; full ND path is a 3-link chain, none confirmed.
- **Unresolved:** the three external definitions above (Q4, Q9) and upstream iterator ordering (Q6).

## Assessment

**Status: NOT CONFIRMED — reported defect is unsubstantiated on current evidence, and its central premise is contradicted by the codebase's ndm-pointer hashing convention.** The structural shape (an unordered container feeding an unsorted vector into a Tcl collection) is real and is a legitimate thing to validate, but "unordered container of pointers" does **not** by itself establish run-to-run non-determinism. The decisive fact — the `dosUnorderedSet` hash key — cannot be resolved without the external `util/` source and should not be assumed to be address-based (the guardrail this candidate would violate).

## Validation Plan (to close the checkpoint)

1. **Resolve the hash key (decisive).** Obtain `util/dosUnorderedSet.h` + `dosContainer::keyHash`/`keyCompare`. Confirm whether `keyHash(ndmBlkInst*)` uses the ndm object ID/type or the raw address. If ID-based → hypothesis refuted at the source of ordering.
2. **Resolve the converter.** Inspect `tcl/clct.h` `clct_list_to_collection`: does it sort/canonicalize (e.g., by object ID) or preserve input order?
3. **Runtime differential test.** Run `get_power_taps` twice on an identical, saved design/session (same binary, controlled `PYTHONHASHSEED`/ASLR where relevant) and diff the returned collection in raw internal order (avoid `sort`/set-normalization in the harness). Repeat under ASLR on/off. Stability across runs refutes; variation confirms and localizes.
4. **Instrument order (if needed).** Temporarily log `myset` iteration order and object IDs vs. addresses across runs to see which correlates with any observed order change. (Investigation-only; not a source fix.)
5. **Confirm consumer observability.** Identify the real downstream Tcl/flow consumer of `get_power_taps` and whether it observes order or treats the result as a set.
6. **SME confirmation** on DOS container determinism guarantees and any documented convention that `dosUnorderedSet` of ndm objects is deterministic by ID.

**Escalation note:** If step 1 shows ID-based hashing (expected), this is not a defect and should be closed as unsubstantiated. If it shows address-based hashing *and* steps 2–3 show order is preserved and observable, the smallest justified correction would be a deterministic sort of `l_ptaps` (e.g., by object ID) immediately before `clct_list_to_collection` at line ~884 — **not** to be implemented until the checkpoint is validated.
