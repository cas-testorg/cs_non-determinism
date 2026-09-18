# Workflow Trace Map — `msuiGetPowerTaps`

**Candidate:** `mscts/msui/msuiGetPowerTaps.cc:66,879-890`

**Purpose:** Compare the original Test 1 A/B reasoning with the independent
Agentic Bug Resolution investigation and identify where the workflows diverged.

## Final focused-investigation disposition

**NOT CONFIRMED / UNSUBSTANTIATED ON CURRENT EVIDENCE**

The structural pattern is real: a `dosUnorderedSet<ndmBlkInst*>` is iterated
into an unsorted vector that is passed to a Tcl collection converter.

However, the critical premise that the container hashes or orders
`ndmBlkInst*` values using raw pointer addresses was not established.

Available adjacent source evidence instead suggests that Synopsys NDM pointer
containers commonly use object identity (`ndmID` / `ndmType`) semantics.

The actual `dosUnorderedSet` hash implementation and downstream collection
conversion implementation are external to the available source and CoreStory
project, so the complete non-determinism path cannot currently be proven.

---

## Evidence-path trace

### 1. Candidate discovery

Reported construct:

`dosUnorderedSet<ndmBlkInst*>`

**Without MCP**

The candidate was considered but was not promoted as a confirmed ND finding.

**With MCP**

The candidate was promoted as a real ND finding.

**Focused ABR investigation**

Confirmed that the container and downstream iteration path exist in production
source.

**Divergence**

The workflows did not differ primarily on whether the suspicious construct
exists. They differed on how the semantics of the pointer container were
interpreted.

---

### 2. ND mechanism hypothesis

Potential mechanism:

`pointer container`
→ unstable iteration
→ result ordering changes
→ observable Tcl collection changes

**Without MCP**

Did not establish the required pointer-address ordering mechanism.

**With MCP**

Interpreted the pointer-based unordered container as being hashed by pointer
address and therefore potentially varying across executions.

**Focused ABR investigation**

Determined that pointer element type alone is insufficient evidence that
pointer address participates in hashing or ordering.

**Divergence**

**Mechanism interpretation / evidence sufficiency**

The With-MCP workflow moved from "container contains pointers" to
"container ordering depends on pointer addresses" without resolving the
underlying container implementation.

---

### 3. Container/type resolution

Required evidence:

`dosUnorderedSet<ndmBlkInst*>`
→ `dosUnorderedSet`
→ `dosContainer::keyHash`
→ actual key semantics

**Without MCP**

Did not promote the candidate based on the wrapper/container alone.

**With MCP**

The final finding depended on address-based pointer hashing.

**Focused ABR investigation**

Attempted to resolve:

- `util/dosUnorderedSet.h`
- `dosContainer::keyHash`
- `dosContainer::keyCompare`

Those implementations are not present in the CTS workspace and are not
available in CoreStory project 10.

Adjacent CTS source shows NDM pointer identity conventions based on object
ID/type:

- `keyHashWithExpireCheck` delegates to `dosContainer::keyHash`
- `compareNdmPointerIsEqual` delegates to `dosContainer::keyCompare`
- comments describe comparison using `ndmID` and `ndmType`
- stable ordered NDM pointer sets use `ndmObjPtrCmpType`

This evidence points away from raw-address semantics but does not prove the
implementation of `dosUnorderedSet`.

**Divergence**

**Source/type-resolution failure in the With-MCP qualification path**

The implementation needed to substantiate the finding was unavailable, but
the finding was promoted rather than classified as unresolved.

---

### 4. Varying input / ordering

Required question:

What can actually vary between otherwise equivalent executions?

**With MCP**

Raw pointer addresses were treated as the varying input.

**Focused ABR investigation**

Raw pointer address has not been established as an input to the hash.

If `dosContainer::keyHash` uses stable NDM object identity, the bucket layout
may be reproducible even though the container is described as "unordered."

Upstream insertion ordering may also matter, but the ordering guarantees of
the relevant NDM iterators are external and unresolved.

**Divergence**

The With-MCP workflow established a possible structural pattern but did not
establish the required source of run-to-run variation.

---

### 5. Propagation

Source path:

`myset`
→ iteration
→ `l_ptaps.push_back(...)`
→ `clct_list_to_collection(...)`
→ Tcl result

**Without MCP**

Did not establish a complete observable ND path.

**With MCP**

Treated the unsorted iteration path as propagation of the assumed unstable
container ordering.

**Focused ABR investigation**

Confirmed direct source propagation from `myset` into `l_ptaps`.

No explicit sort of `l_ptaps` occurs before `clct_list_to_collection`.

This portion of the original hypothesis is structurally supported.

**Result**

The propagation path is plausible **if** the input iteration order varies.

---

### 6. Neutralization

Required question:

Does anything downstream canonicalize the result?

**With MCP**

The candidate was promoted without establishing a downstream neutralizer.

**Focused ABR investigation**

The implementation of `clct_list_to_collection` is external to the available
workspace and CoreStory project.

It is therefore unresolved whether the converter:

- preserves input order;
- sorts by stable object identity;
- canonicalizes the collection; or
- otherwise neutralizes ordering variation.

Tcl consumers may also treat the result as set-like rather than
order-sensitive.

**Divergence**

**Incomplete neutralization analysis**

A second required link in the ND chain remained unresolved.

---

### 7. Observable consequence

For the reported defect to be real, all of the following must hold:

1. `dosUnorderedSet` iteration varies between equivalent runs.
2. The variation is caused by a genuinely unstable property such as address
   identity or unstable insertion ordering.
3. `clct_list_to_collection` preserves that varying order.
4. A downstream consumer observes order rather than set semantics.

**Focused ABR result**

None of these links is currently confirmed as a complete chain.

Even if confirmed, current evidence limits the apparent blast radius primarily
to `get_power_taps` collection/report ordering. No evidence currently shows
that this path influences CTS optimization or placement decisions.

---

## Point of workflow divergence

The primary divergence occurred at:

**Container semantics → mechanism qualification**

The With-MCP workflow correctly identified a suspicious source pattern and a
potential propagation path, but it promoted the candidate before resolving the
semantics required to establish that the container's ordering can actually vary.

The focused investigation therefore identifies the failure as:

> **Premature mechanism inference combined with insufficient evidence gating.**

It is not primarily a discovery failure.

---

## What the workflow should have done

When the decisive container implementation could not be resolved, the
qualification path should have stopped at:

**UNRESOLVED — CONTAINER SEMANTICS REQUIRED**

rather than promoting the candidate as a real ND defect.

A suitable qualification gate is:

`pointer-valued container`
→ resolve concrete container implementation
→ resolve hash/comparator
→ establish varying input
→ establish iteration variability
→ trace propagation
→ check neutralization
→ establish observable consequence
→ promote

Failure to establish any load-bearing step should produce `UNRESOLVED` rather
than `REAL`.

---

## CoreStory contribution

CoreStory project 10 contributed application framing and confirmed that
`get_power_taps` is a user-facing Tcl command returning a cell collection.

It also helped establish that the decisive DOS container and Tcl collection
implementations were not available in the indexed application source.

However, the available evidence does **not** show that CoreStory itself caused
the original incorrect pointer-address inference.

The observed error belongs to the **With-MCP workflow** unless execution
evidence establishes which component produced that inference.

---

## Remaining validation

1. Obtain `dosUnorderedSet` / `dosContainer::keyHash` implementation.
2. Determine whether NDM pointer hashing uses object ID/type or raw address.
3. Inspect `clct_list_to_collection` for sorting/canonicalization.
4. Determine ordering guarantees of relevant upstream NDM iterators.
5. Identify whether real Tcl consumers observe collection order.
6. Run a controlled repeated-execution test if source evidence remains
   inconclusive.

---

## SME question

The most useful SME question is:

> Does `dosUnorderedSet<ndmBlkInst*>` provide stable iteration behavior for
> equivalent NDM objects because hashing/equality are based on NDM object
> identity, and does `clct_list_to_collection` preserve or canonicalize the
> incoming order?

If hashing is ID/type based and stable, the original reported mechanism is
refuted at its first required ordering link.

If hashing is address based, investigation should continue through the
collection-conversion and consumer-observability links before classifying the
candidate as a defect.

---

## Test 1 classification

**With-MCP qualification error**

More specifically:

**Premature container-semantics inference / insufficient evidence gating**

The candidate was worth investigating, but the available evidence did not
justify promotion to a confirmed non-determinism finding.
