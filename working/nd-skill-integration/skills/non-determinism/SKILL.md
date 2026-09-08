---
name: prove-nd-mt
description: Use when proving or dismissing MULTI-THREADED non-determinism suspects - races, locks, atomics, parallel reductions, thread pools, worker-object state carryover, commit-order dependence - or when a prove-nd pass involves tbb::parallel_for, thread servers, per-thread caches, or a mutex-guarded accumulator. Extends the prove-nd skill with concurrency-specific sinks, neutralizers, labels, and sweep rules.
---

# Prove ND Details - Multi-Threaded Extension

## Overview

This extends `prove-nd` for concurrency. Read the base skill first:
`/u/ranjithp/.claude/skills/hubble_v0.4/ranjithp-skills/prove-nd/SKILL.md`

All base rules still apply, including: no sub-agents, preserve dashboard order, ignore pure
`getenv`, do not call a row real without a downstream C++ consumer, do not treat `purecov` or
Coverity annotations as reachability proof, ASCII-only report.

The base skill is tuned for **container-order** non-determinism: pointer-keyed maps, unordered
containers, sort instability. That taxonomy misclassifies concurrency bugs, because the
governing question is different. For container ND the question is "is the iteration order
observable". For MT ND the question is **"which of three very different things is this"**:

| Outcome | What varies | Locking fixes it? |
|---|---|---|
| Data race | undefined behaviour, torn/garbage reads, crashes | Yes |
| Race-free but order-dependent | the RESULT, run to run | **No** |
| Benign | nothing observable | n/a |

Conflating the middle row with the first is the single most common error in this area. Most of
the interesting MT ND in this codebase is the middle row: correctly locked, race-free, and
still not reproducible.

## Hard Rules (in addition to the base skill)

- **A lock proves race-freedom, never determinism.** Never cite the presence of a mutex as a
  neutralizer for an ordering question.
- **Prove the code actually runs under MT.** Name the parallel dispatch site
  (`tbb::parallel_for`, thread-pool `run()`, worker functor, per-thread server acquisition).
  Do not infer concurrency from the presence of a lock; locks are often defensive or vestigial.
- **Prove the gate is live before trusting a lock.** See "Inactive-gate checklist".
- **Sweep accessors, not member names.** See "Sweep discipline". This rule exists because
  skipping it produced two false findings in one wave.
- **Census both sides of a work-item boundary.** Entry-side and exit-side. See "Boundary reset".
- **Atomic integer accumulation is deterministic; atomic floating-point is not.** Integer add
  is exact and associative, so arrival order cannot change the sum. Float/double add is
  neither.
- Prefer a thread-count A/B (1 vs N) over TSAN as the primary runtime confirmation for an
  ordering claim. TSAN answers "is there a race", which is a different question.

## MT-Specific Observable Sinks

Add these to the base skill's sink list. Any one of them is enough to make an ordering
hazard `Real`, provided reachability under MT is proven.

- **Non-associative float reduction.** `sum += x` on `float`/`double` from N threads, in any
  order, even under a perfect mutex. Also `*=`, and any mean/variance built from them.
- **First-writer-wins / first-finder-wins.** `if (!found) { found = true; best = candidate; }`
  under concurrency: whichever thread arrives first decides, and that varies.
- **Ratcheting min/max on shared state.** `MifsUpdMin`/`MifsUpdMax` (or bare `if (x < best)`)
  applied to a member that is not reset per work item. Ties resolve to whoever got there
  first; and if the operand is itself run-dependent, the ratchet locks in a run-dependent
  bound. Note the operand-provenance test below before flagging these.
- **Container insertion order under concurrent insert.** Even a locked `std::map` gets a
  run-dependent *node order* if keys are pointers, and any later iteration inherits it.
- **ID / handle / index allocation order.** If workers allocate from a shared counter, the
  identity attached to a given object varies, and every downstream use of that identity
  inherits it.
- **Budget or early-exit exhaustion.** A shared iteration/expansion/effort budget consumed by
  N workers: whoever consumes it first survives, the rest get truncated. Work-stealing makes
  the split vary.
- **Worker-state carryover.** A long-lived worker object (thread server, maze engine,
  partition) reused across work items, where the item-to-worker binding is decided by a
  first-idle-wins pool. Any member not restored at the boundary carries a value from whichever
  item previously used that worker, which differs per run. This is race-free by construction
  and therefore invisible to race detectors.
- **Commit-order dependence.** Changes applied to shared design state in completion order,
  where a later reader sees a different prefix depending on who finished first.

## MT-Specific Neutralizers

A hazard is NOT real if one of these canonicalizes before any consumer observes it. Each must
be verified, not assumed.

- **Canonicalization pass after the parallel join.** A single-threaded pass that re-derives
  the value in a fixed (index) order. Verify three things: it is actually called (find
  production call sites), it runs after the join, and **it covers every contributor** - a
  partial canonicalizer that skips a subset leaves that subset non-deterministic, and this is
  easy to miss because the function name suggests total coverage.
- **Per-thread partials merged in stable key order.** Accumulate into a slot indexed by a
  stable key (part index, net index - never thread id), then reduce in index order.
- **Atomic integer add / bitwise or / set-union.** Order-independent by construction.
- **Idempotent write of an identical value.** Multiple threads writing the same value is
  benign; confirm the value cannot differ per thread.
- **Membership-only or lookup-only use.** The container's order never reaches a consumer.
- **Unconditional per-work-item assignment.** For a mode flag on a shared object: a write that
  executes on every path, before any read. A *conditional clear* is not sufficient.
- **Deterministic re-sort at the observable boundary.** Sorting by a stable key just before
  output, rather than relying on production order.

## Inactive-Gate Checklist

Before accepting any lock, guard, or determinism option as a neutralizer, rule out all of
these. Each has produced a real defect in this codebase.

1. **Thread-count gate that is permanently false.** `if (getNumThrd() > 1) lock();` where the
   thread count is set elsewhere such that it never exceeds 1 in the MT path. Resolve the
   actual value at the call site.
2. **Commented-out lock.** Grep the guarded region for `//` before the lock macro. Check every
   layer independently; the same critical section may be disabled at one layer and live at
   another.
3. **Compiled-out lock.** `#if 0`, an undefined build macro, a `SPOT_LOCK`-style macro that
   expands to nothing.
4. **No-op default argument.** A `lock(bool really = false)` style API where callers rely on
   the default and get no lock.
5. **Two distinct locks sharing one name.** Same member/static name in different classes or
   translation units, so call sites that look mutually exclusive are not.
6. **Lock released before the mutation it is supposed to guard.** Classic: clear a cache
   after unlocking.
7. **Broken double-checked locking.** Fast-path read outside the lock with no acquire
   semantics.
8. **Determinism option that does not reach the code.** Confirm the option's value actually
   arrives: check the enum-to-int mapping, the cascade/ladder that sets dependent bits, and
   whether the specific level the user sets has an implemented branch. An option can accept a
   value and silently ignore it.

## Sweep Discipline

The mechanical step that decides whether a finding is real or an artefact.

**Never conclude "this member has no reset" from a sweep of the member name.** A private
member appears only in its own class's header and implementation; it is manipulated elsewhere
through its accessors. Sweeping `foo_` and concluding "only assigned in constructors" is
invalid.

Required sweep set for a member `foo_` on class `C`:

```
foo_                          # declaration, in-class writes
setFoo|getFoo|resetFoo|clearFoo|addFoo|dltFoo   # every accessor, whatever the naming
C::.*Foo                      # qualified forms
```

Sweep across the whole product tree, not the owning module.

**Extension coverage.** In this codebase `apf` uses `.cxx`/`.hxx` while `nwtn` uses
`.cc`/`.h`. A glob of `*.{cc,h,hh,cpp,c}` silently misses most of `apf`. Either list all of
`{cc,h,hh,cpp,c,cxx,hxx}` or pass no glob at all.

**Alias coverage.** One option or variable often carries several names (a C++ variable, a
registered option name, and one or more aliases). Sweep all of them, and confirm the set is
complete by finding the registration site rather than guessing.

**Trap: `rg -r`.** `-r` is `--replace`, not `--recursive`. `rg -rn PATTERN path` silently
replaces every match with the literal `n` and your counts become meaningless. Recursion is the
default; never pass `-r` unless you mean replacement.

## Boundary Reset (worker-state carryover)

For a member on a reused worker object, "is it reset at the work-item boundary" requires
censusing **both** sides:

- **Exit side**: `cleanup*`, `end*`, `finish*`, `*PostCommit`, destructor-like teardown.
- **Entry side**: `start*`, `begin*`, `init*`, `reset*`, `newProblem`, `open*`.

Either one suffices. Checking only the exit side manufactures false positives - a reset can
legitimately live on entry.

Also distinguish **flush from clear**. A `flushMap()` that flushes each element without
emptying the container is not a reset. Read the implementation; do not trust the name. And
`reset*` does not reliably mean "restore to default" - verify the polarity, since a
`resetFoo()` that sets the flag TRUE exists in this codebase.

## Operand-Provenance Test

Before flagging a `MifsUpdMin`/`MifsUpdMax`/compare-and-store on shared state as a ratchet,
resolve where each operand comes from:

- All operands compile-time constants or freshly-read control values -> **not** a ratchet; the
  result is the same every run regardless of call order.
- Any operand derived from prior work items, or from a run-dependent quantity -> genuine
  ratchet.

Also check upstream: **a fresh assignment upstream neutralizes a downstream ratchet.** If some
earlier statement on every path assigns the member outright, the later update cannot
accumulate across items.

## Classification Labels for MT

Use the base skill's labels, plus these refinements. State the refinement in the verdict
paragraph and map it to a base label for the dashboard field.

| MT refinement | Meaning | Base label |
|---|---|---|
| `Locked-but-order-dependent` | correctly locked, race-free, result still varies (usually FP reduction) | `Real` |
| `Gate-inactive` | the lock/guard exists but never engages, so the race is live | `Real` |
| `Worker-carryover` | unreset state on a pooled worker, race-free but run-dependent | `Real` |
| `Commit-order` | observable depends on which thread finished first | `Real` |
| `Canonicalized-after-join` | ND exists transiently, re-derived deterministically before any consumer | `Neutralized` |
| `Partially-canonicalized` | canonicalizer exists but skips a subset; that subset stays ND | `Real` (scope it to the subset) |
| `Race-but-idempotent` | concurrent writes of a provably identical value | `Latent-only` |
| `MT-unreachable` | code never actually runs under concurrency | `Dead/unused` |

Reserve `Unresolved` for the honest case, and say exactly what is missing. For MT the usual
missing piece is **path reachability**: symbol sweeps find call sites but cannot prove that
some path reaches a read without passing a write. Say so explicitly rather than guessing.

## Runtime Confirmation for MT

Design the confirmation to match the claim.

- **Ordering claim** (result varies): thread-count A/B. Same design, same seed, `-nthreads 1`
  vs `-nthreads N`, diff the specific value. If it differs, the ordering claim is confirmed
  end to end. Then N vs N to separate ordering from thread-count-dependent algorithm changes.
- **Race claim** (UB): TSAN, or a targeted assertion on the invariant.
- **Carryover claim**: instrument the boundary to log `(worker id, item id, member value)` and
  diff the sequence across two runs.
- **Precision trap.** If the sink prints at fixed precision (`%.2f`), a real difference can be
  invisible. Compare the raw value, print with `%a`/full precision, or checksum the bits.
  Never conclude "no difference" from a rounded report.

## Report Additions

Use the base skill's report structure. Add to each issue section:

- **MT Reachability**: the named parallel dispatch site, and how work binds to workers
  (static partition, dynamic/work-stealing, first-idle-wins pool). Say which, because
  static partitioning is often deterministic while the other two are not.
- **Race vs Ordering**: state which of the three outcomes this is. If it is ordering, say
  explicitly that locking cannot fix it.
- **Gate Audit**: the inactive-gate checklist result for every lock or option cited as a
  neutralizer.

In the summary table, add a column for the MT refinement label so a reader can tell
`Locked-but-order-dependent` from `Gate-inactive` without opening the section.

## Worked Precedents

Concrete outcomes from this codebase, useful as calibration.

- **Partially-canonicalized, ruled Real.** A global float wirelength was summed across worker
  threads under a mutex. A post-join, single-threaded, index-ordered pass re-derived it - but
  only for nets satisfying an `isLocalNetExist` guard. Nets on the other branch kept their
  arrival-order sum and reached a printed total. The canonicalizer's existence looked like a
  neutralizer; its *coverage* was the defect. Lesson: always check what the canonicalizer
  skips.
- **Entry-side reset, ruled Neutralized.** A per-thread sparse demand map was only
  `flushMap()`-ed at the commit boundary, which looked like uncovered carryover. But
  `startProblem()` cleared it on entry, and all four functional readers cleared before
  reading; the only unguarded reader was a diagnostic, already removed. Lesson: census both
  sides before claiming a boundary is uncovered.
- **Two false findings from a name-only sweep.** Two mode flags were reported as having "no
  reset anywhere" on the strength of sweeping the member names. Both were in fact set on both
  polarities from ~20 and ~13 call sites in a different file, via their setters. Lesson: the
  Sweep Discipline section exists because of this.
- **Option that accepts a value and ignores it, ruled Real.** A user-visible enum accepted
  levels 4, 5 and `latest`, but the cascade's last rung was `val >= 3`, so all three delivered
  level 3 silently. No regression set any of those values. Lesson: for a determinism option,
  verify the specific level has an implemented branch, and check the regression suite for
  which values are actually exercised.

## Common Mistakes (MT-specific)

- Citing a mutex as evidence that a float accumulation is deterministic.
- Assuming a canonicalization pass covers every contributor because its name says "global".
- Concluding "no reset" from a sweep of a private member name.
- Checking only the exit side of a work-item boundary.
- Treating `flushMap()`/`flush()` as equivalent to `clear()`.
- Assuming a lock is live without auditing the thread-count gate, comment state, and build
  macros around it.
- Assuming an app option's advertised range is implemented.
- Using `rg -r` and trusting the resulting counts.
- Concluding a value is deterministic from a fixed-precision report.
- Reporting a data race and an ordering defect as the same finding; they need different fixes
  and different confirmations.
