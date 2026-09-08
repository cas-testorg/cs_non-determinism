# ND Pattern Catalog (Narrative Mirror)

This document mirrors `nd-patterns.yaml` for human / LLM consumption. The
YAML file is the source of truth for the scanner; this file is what the
LLM reads during triage to understand intent, severity, and idiomatic fixes.

Categories are grouped by how the pattern is detected:

- **Tier 1 (regex-detectable):** the regex by itself produces a high-quality
  candidate. The LLM only needs to confirm it's not a false positive.
- **Tier 2 (LLM-reasoned):** the regex locates a candidate site, but the
  LLM must read surrounding code to decide whether the pattern is actually
  ND in this context.

Severity tiers:

| Tier | Meaning |
|---|---|
| **HIGH** | On a hot path or directly affects QoR / final result |
| **MEDIUM** | Used but not in the main loop, or has partial mitigation |
| **LOW** | Debug-only, rarely-hit, or already neutralized by surrounding code |

Always re-read [id-system.md](id-system.md) and [fix-recipes.md](fix-recipes.md)
when authoring fixes.

---

## Original 5 Categories

### 1.1 — Pointer-based `std::sort` / `std::stable_sort`

**Severity default:** HIGH · **Tier:** 1 · **Category:** sorting

`std::sort(v.begin(), v.end())` on `std::vector<T*>` uses `std::less<T*>`,
which compares raw addresses. Address layout varies per run (ASLR, allocator
state), so the sort result is non-deterministic. If the sort feeds into
`std::unique`, into iteration with side effects, or into picking a
"first-of-ties" element, the entire downstream algorithm diverges.

**Triage signals:**

- Element type is a pointer (`T*`).
- The next few statements call `std::unique`, iterate the vector, or read
  `*v.begin()` / `v.front()` / `v.back()`.

**Fix:** see Versions A/B/C in [fix-recipes.md §1](fix-recipes.md#1-pointer-keyed-stdsort).

**Plan-file example:** `ropt/flow/thermal/thermalViaDeletion.cc:384`.

---

### 1.2 — `std::set` / `std::map` with pointer key

**Severity default:** HIGH · **Tier:** 1 · **Category:** container

Default `std::less<T*>` orders entries by address. `insert`, `find`, and
iteration all become non-deterministic. Common pattern for "fixed cells",
"failed routes", "skip nets" — exactly the data the algorithm iterates.

**Triage signals:**

- The container is iterated in a loop with side effects.
- The container is used to track "first to encounter" / "last to encounter"
  state.

**Fix:** prefer `ndmPtrMap<T*, V>` (already exists in `ndmutil`) — it uses
`dosContainer::keyCompare`. Otherwise, supply
`ndmObjectHandleNS::compareObjPtr` as the third template argument.

**Plan-file example:** `bufutil/roi/router/roiRtrCtl.cc:3304` (`failedToPlace`).

---

### 1.3 — `std::unordered_set` / `std::unordered_map` with pointer key

**Severity default:** HIGH · **Tier:** 1 · **Category:** container

`std::hash<T*>` hashes the address. Bucket assignment, rehash points, and
iteration order all vary across runs. Even a "deterministic hash" patch is
not sufficient if downstream code iterates the container — bucket sizing
still changes when load factor crosses a threshold. Pair the hash fix with
a "sort before iterating" pattern when iteration matters.

**Fix:** see [fix-recipes.md §2](fix-recipes.md#2-pointer-keyed-stdunordered_-with-iteration).

---

### 1.4 — Pointer-based hash functors (`std::hash<T*>`, `hash_combine` with pointer)

**Severity default:** HIGH · **Tier:** 1 · **Category:** hash

Custom hash functors that mix a raw pointer into the hash value reproduce
the address-dependence of `std::hash<T*>`. Same logical key hashes to a
different bucket every run.

**Fix:**

- Version A: hash `getIdLong()` instead of the pointer.
- Version B: walk the context chain via `getContextElement()` and combine
  `getIdLong()` + `getObjectType()` for each link (this is what
  `dosContainer::keyHash` does).

**Plan-file example:** `ropt/util/infeasibleMgrImpl.h:91-101` (`ndmTermPairHash`).

---

### 1.5 — Random ops without a deterministic seed

**Severity default:** HIGH · **Tier:** 1 · **Category:** random

Includes:

- `std::random_shuffle` (deprecated; uses unspecified RNG).
- `rand()` / `srand()` (global, platform-dependent state).
- `std::mt19937 rng;` with no explicit seed (technically deterministic but
  almost always indicates "I forgot to seed from the input").
- `boost::random::mt19937` with no seed.

**Fix:** derive the seed from stable input characteristics (number of
elements, design hash, IDs of inputs) and pass it to `std::mt19937`. Use
`std::shuffle` instead of `std::random_shuffle`.

**Plan-file example:** `opt/optutil/optClustering.cc:288`; `rail/rr/rr.h:677`.

---

## Tier 1 Additions (#6-14)

### 2.1 — Time / PID-based RNG seeds

**Severity default:** HIGH · **Tier:** 1 · **Category:** timing

Direct ND by construction: `srand(time(NULL))`,
`std::mt19937(getpid())`, `seed(std::chrono::*::now())`. The code *intends*
to randomize per run.

**Fix:** seed from input data (hash of element IDs, design hash) or expose
the seed as an app option.

---

### 2.2 — `getFullName()` / `getPathName()` as map key or hash input

**Severity default:** MEDIUM · **Tier:** 1 · **Category:** naming

Two issues at once:

1. `getFullName()` is **O(hierarchy depth) + string allocation**, so it is
   very expensive compared to `getIdLong()` (O(1) arithmetic).
2. The string can drift (escaping, separator changes, hierarchy renames),
   making the key unstable even within one run.

**Fix:** use the pointer with a stable comparator, or cache the string once
if external API truly needs a string key.

---

### 2.3 — `std::priority_queue<T*>` without a comparator

**Severity default:** HIGH · **Tier:** 1 · **Category:** container

Default `std::less<T*>` makes pop order address-driven. Any worklist,
Dijkstra-like search, or beam search becomes ND.

**Fix:** wrap with a `pair<Cost, T*>` and supply a comparator that breaks
ties on `getIdLong()`, or supply a stable comparator directly.

---

### 2.4 — `std::min_element` / `max_element` on pointer vectors

**Severity default:** MEDIUM · **Tier:** 1 · **Category:** container

Two-argument forms use element `operator<`. With ties, the "first min"
returned depends on address ordering of equal-score elements.

**Fix:** pass a tiebreaker comparator that falls through to `getIdLong()`.

---

### 2.5 — `std::unique` after pointer sort

**Severity default:** MEDIUM · **Tier:** 1 · **Category:** sorting

`std::unique` keeps the first element of each adjacent equivalence class.
If the preceding `std::sort` was non-deterministic, dedup is too.

**Fix:** ensure the preceding sort uses a stable comparator (Issue 1.1).

---

### 2.6 — Filesystem iteration without sorting

**Severity default:** MEDIUM · **Tier:** 1 · **Category:** filesystem

`readdir`, `std::filesystem::directory_iterator`, and the Boost equivalent
all return entries in inode / B-tree order. Cross-machine and post-rename,
this is non-deterministic.

**Fix:** collect entries into a vector, `std::sort` by path, then iterate.

---

### 2.7 — Pointer arithmetic / `reinterpret_cast` to integer as key

**Severity default:** MEDIUM · **Tier:** 1 · **Category:** arithmetic

`reinterpret_cast<size_t>(ptr)` or `(size_t)(a - b)` smuggles address-based
ordering into hashes and keys. Same root cause as `std::less<T*>`, just
disguised.

**Fix:** use `obj->getIdLong()` instead.

---

### 2.8 — `boost::container::flat_map` / `flat_set` with pointer key

**Severity default:** HIGH · **Tier:** 1 · **Category:** container

Same default-comparator problem as `std::map` / `std::set`.

**Fix:** supply `ndmObjectHandleNS::compareObjPtr` as the third template arg.

---

### 2.9 — `std::weak_ptr::owner_before` / `std::owner_less<>`

**Severity default:** LOW · **Tier:** 1 · **Category:** container

Orders `weak_ptr` by control-block address. Used as a `set` comparator,
this gives the same ND as a pointer-keyed `set`.

**Fix:** supply an ID-based comparator that calls `lock()` and compares
`getIdLong()`.

---

## Tier 2 Additions (#15-21)

These need LLM reasoning — the regex flags a candidate but the LLM must
read the surrounding code to confirm.

### 3.1 — Parallel floating-point reduction

**Severity default:** HIGH · **Tier:** 2 · **Category:** parallel

Floating-point `+` is non-associative at the bit level. Any
`tbb::parallel_reduce`, `#pragma omp parallel for reduction(+:)`, or
`std::reduce` over `float`/`double` can produce a different last-bit result
each run depending on chunk sizes and merge order.

**Triage questions for the LLM:**

1. Is the reduction operand integer or floating-point? (Integers are safe.)
2. Is the result fed into an exact compare or a hash? (Yes → ND. Used only
   for an epsilon-tolerant compare → safe.)
3. Is the result printed in a log that drives downstream tooling? (Yes → ND.)

**Fix:** force a sequential reduction; or pairwise / Kahan summation; or
fix the partition strategy so each input always goes to the same thread.

---

### 3.2 — Multi-threaded shared container writes

**Severity default:** HIGH · **Tier:** 2 · **Category:** parallel

`tbb::parallel_for` body that writes into a shared `concurrent_vector` /
`std::vector` (under mutex) gives an order that depends on thread
scheduling.

**Triage questions for the LLM:**

1. Is the parallel body writing to a *shared* mutable container?
2. Is the container later iterated for a result-affecting purpose?

**Fix:** pre-size and write by index, or use per-thread buffers and merge
deterministically.

---

### 3.3 — `unordered_*` iteration feeding algorithms

**Severity default:** MEDIUM · **Tier:** 2 · **Category:** iteration

Even with a deterministic hash, bucket count / rehash / load factor varies
the iteration order. Code that iterates an `unordered_*` and feeds an
ordered downstream consumer becomes ND.

**Triage questions for the LLM:**

1. Is the iterated container `std::unordered_*` (or has a custom hash)?
2. Does the loop body do (a) `push_back` into another container, (b) call
   a side-effecting function, or (c) accumulate non-commutative state?

**Fix:** snapshot to a vector, sort by a stable key, then iterate.

---

### 3.4 — `std::map::operator[]` with side-effecting default init

**Severity default:** LOW · **Tier:** 2 · **Category:** iteration

`myMap[k].foo()` default-constructs `V` on first access. If `V` has a
non-trivial constructor and the map is pointer-keyed, the order of
constructions follows address order.

**Triage questions for the LLM:**

1. Is `V`'s default constructor non-trivial?
2. Is the map pointer-keyed?

**Fix:** also fix the comparator (Issue 1.2). Prefer `emplace` over
`operator[]` when side effects matter.

---

### 3.5 — Thread-count dependency in algorithm sizing

**Severity default:** MEDIUM · **Tier:** 2 · **Category:** parallel

`std::thread::hardware_concurrency()`, `omp_get_num_threads()`, and
`tbb::this_task_arena::max_concurrency()` return values that depend on the
machine and the surrounding scheduler. Using them to size data structures
or pick algorithm branches makes the result machine-dependent.

**Triage questions for the LLM:**

1. Does the value flow into a data-structure size, a chunk-count, or a
   conditional branch that affects output?

**Fix:** read a configured value (`appOptions::get_max_cores()`) instead.

---

### 3.6 — Post-collection use without canonical ordering

**Severity default:** MEDIUM · **Tier:** 2 · **Category:** iteration

Some ND fixes are not visible as bad container declarations. The code
collects graph nodes, rows, batches, LEQ/knee candidates, or modules from a
traversal/binning source into a vector-like container and consumes that
collection immediately. If the source enumeration is unstable, the downstream
algorithm sees a different order each run.

**Triage questions for the LLM:**

1. Is the collection populated from a traversal, graph/bin query, hash-backed
   source, or other source without a documented stable order?
2. Is there an explicit stable `sort` / canonicalization before the collection
   is consumed?
3. Does the consumer perform order-sensitive work: first-match selection,
   ranking, output/checksum emission, mutation, or non-commutative
   accumulation?

**Fix:** collect all candidates, then sort by a stable key before use. For
object pointers, prefer `ndmObjectHandleNS::compareObjPtr{}` or the local
project comparator. For scored/ranked data, include a stable tie-break key.

**Mined evidence:** CLs `7720129`, `9275937`, `11913380`, `13380520`,
`13530532`.

---

### 3.7 — Project wrapper containers with order-sensitive use

**Severity default:** MEDIUM · **Tier:** 2 · **Category:** container

Historical fixes often replaced or adjusted project-specific wrappers rather
than plain STL containers: `dosUnorderedMap`, `hyHashI`, `nwcInsOrdMap`,
`ndmPtrSet`, `ndmPtrMap`, and comparator/hash helpers such as
`dosContainer::keyCompare` / `dosContainer::keyHash`.

A wrapper name alone is not enough evidence. Some wrappers are deterministic
by construction; others preserve insertion order and are only safe when the
insertion source is stable. Treat this pattern as a wrapper-aware extension
of pointer-container and unordered-iteration analysis.

**Triage questions for the LLM:**

1. What are the wrapper semantics: unordered, sorted by comparator, or
   insertion-order preserving?
2. If insertion-order preserving, is the insertion source itself stable?
3. If keyed by pointers, does the wrapper use stable comparator/hash support
   such as `dosContainer::keyCompare`, `dosContainer::keyHash`, or
   `ndmObjectHandleNS::compareObjPtr`?
4. Is iteration or first-match behavior result-affecting?

**Fix:** use `ndmPtrMap` / `ndmPtrSet` when stable object identity order is
intended; add `dosContainer::keyCompare` / `keyHash` where the wrapper needs
explicit stable identity support; or sort/canonicalize inputs before inserting
into insertion-order containers.

**Mined evidence:** CLs `10023555`, `10347201`, `10718451`, `10862919`,
`13380520`.

---

## Concurrency / MT-ND Additions (#4.1-4.6)

These come from the multithreading ND hunt (`multithreading-nd-hunt-plan.md`)
and are anchored on **P2-002** -- the `ndmPolyRect` "const getter that secretly
writes." They are **static source patterns**; detection is static but their
*observability* requires the MT hunt / a TSan stress test, so realness still
follows the prove-nd discipline (see `mt_nd_issue_classes.md`, types N1-N6).
Category is `concurrency`; all are Tier 2 (regex is a seed, LLM must read code).

### 4.1 -- Lazy dirty-bit recompute inside a const getter (N1 / F1b)

A `mutable` cache plus a `mutable _xDirty/_xValid/_xComputed` bit, recomputed in
a `const` accessor when stale. Concurrent const readers race on the hidden
write. **Broader than first-touch**: the dirty bit is re-armed by every
`invalidate()`, so eager-materialize-at-set-time does **not** fix it.
**Fix:** eager where there is no invalidate-after-publish; otherwise adopt the
module's existing guard (`dvuAtomicBitSet` fast-path load, or a read mutex on
the recompute path), or lock-free `store(release)`/`load(acquire)` publish.
**Evidence:** ndm `ndmGeoMask`, `ndmSiteRowData`, `ndmVoltageAreaData`,
`ndmVirtualHVTree`, `ndmPhysHierData`.

### 4.2 -- First-touch materialization / inconsistent lazy-cache lock (N2 / F1a+F1f)

(a) First-touch: `const` getter builds a `mutable` member when empty
(`if (_points.size()==0) _points.push_back(...)`) -- the P2-002 anchor.
(b) **Inconsistent locking discipline** (highest value): the same lazy-cache
pattern is mutex/atomic-guarded in some classes of a family and unguarded in
others. The guarded siblings prove the hazard is real, so the unguarded ones
are defects. The `mutable ...mutex` regex is a *seed* to find the guarded
siblings; then audit the family for unguarded twins.
**Fix:** bring unguarded members up to the family's existing standard (reuse
the sibling's atomic/mutex); prefer eager materialization for pure first-touch.
**Evidence:** ndm `ndmPolyRect` (unguarded, P2-002) vs guarded
`ndmGeoMask._readMutex`, `ndmVoltageAreaData._mutex`, `ndmModuleData._atomicBits`.

### 4.3 -- mutable non-atomic counter RMW on a const path (N3 / F1c)

A `mutable` integer (depth/refcount/level) incremented on a `const` query or
notify traversal -> torn RMW under concurrency. **Fix:** `std::atomic` (or the
project wrapper), or thread-confine / guard with the object's lock.
**Evidence:** ndm `ndmTopologyData._pointsNtfyDepth`.

### 4.4 -- concurrent_hash_map accessor check-then-act (N4)

`tbb::concurrent_hash_map`/`concurrent_unordered_*` is per-op safe, but a
read-accessor-then-write-accessor compound sequence is an atomicity violation.
**Fix:** hold one write accessor across the compound op.
**Evidence:** ndm `ndmPhysicalQueryUtil` `tbbNetMap/tbbPortMap`.

### 4.5 -- Condition-variable lost-wakeup shape (N5)

`cond.wait(lock)` under an `if` instead of a `while`/predicate, or `notify`
issued outside the lock so a wakeup is lost. **Fix:** predicate-loop wait and
notify under the lock. **Evidence:** ndm `ndmCutMetal` `_emptyCond/_fullCond`.

### 4.6 -- Address-keyed lock striping anti-pattern (N6)

Selecting a lock from a pool by hashing an object address (`addr>>4 & 511`) is
an ND/perf smell and often leaves the read path unsynchronized. This is the
*replaced* first attempt in P2-002; flag recurrences. **Fix:** remove the
address-keyed pool; use eager materialization, a per-object atomic flag, or
`std::call_once`, and guard both read and write if a lock is truly needed.

---

## Adding a New Pattern

To add a new ND category, append a new entry to `nd-patterns.yaml` with a
fresh `id` and add a corresponding section here. No code changes required.

When choosing the tier:

- **Tier 1** if a regex match nearly always indicates a real ND issue.
  Acceptable false-positive rate ≤ ~25%.
- **Tier 2** if the regex match is just "vicinity" — the LLM must read code
  to decide. Acceptable false-positive rate ≤ ~75% (the LLM filters).
