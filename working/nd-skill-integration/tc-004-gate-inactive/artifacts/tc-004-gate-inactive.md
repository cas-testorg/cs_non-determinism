# Multi-threaded nondeterminism analysis
_Exported on 9/4/2026 at 12:52:58 CDT from Cursor (3.18.25)_

---

**User**

Investigate the repository for multi-threaded nondeterminism caused by an inactive, bypassed, or ineffective determinism/threading control.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory. Before broad local repository searching, identify the strongest application-level control path you can support that includes:
1. a configuration option, runtime flag, thread-count gate, lock/determinism control, or similar mechanism that appears intended to influence parallel or deterministic behavior,
2. where that control is defined and how it is configured or defaulted,
3. how the value propagates through the application to the relevant execution path,
4. the actual parallel dispatch, shared mutation, reduction, commit, or ordering-sensitive operation it is supposed to govern, and
5. the downstream observable behavior that could vary if the gate is ineffective.

For any candidate, do not classify it as Gate-inactive / Real until you establish:
1. the protected or supposedly controlled operation is actually reachable under multi-threading,
2. the control is intended to govern that operation,
3. the control is ineffective in the real path because it is default-disabled, bypassed, not propagated, checked too late, released before the mutation, compiled out, or otherwise does not actually govern the operation,
4. equivalent runs can therefore experience a variable ordering or concurrency-sensitive behavior, and
5. that behavior can reach an observable application result without a complete deterministic neutralizer afterward.

Use local source inspection to validate the strongest CoreStory-supplied control path. Avoid broad product-wide grep unless CoreStory cannot establish the control-to-execution relationship; if you must broaden the search, make that explicit.

Do not infer intent from a flag or lock name alone. Verify defaults, propagation, call sites, and the exact scope of the gate/control.

Return only the strongest supported candidate, or state that the available evidence is insufficient.

---

**Cursor**

I'll follow the prove-nd-mt skill and CoreStory workflow: read the skill, then use CoreStory to find the strongest control-to-execution path before local validation.

Next I'll pull CoreStory project context and query for inactive or bypassed threading/determinism controls.

Querying CoreStory for inactive/bypassed determinism and threading controls, and retrieving ranked chunks for the same mechanisms.

CoreStory flagged `enable_multi_thread` as a propagation-gap candidate. I'll refine that path and check stronger Gate-inactive patterns (determinism cascades, thread-count gates, dead locks).

CoreStory’s `enable_multi_thread` lead is only a propagation gap so far. I’ll pull indexed chunks for those symbols and dig into stronger lock/determinism-gate patterns.

CoreStory couldn't confirm Gate-inactive Real. Validating the strongest control path in local source next.

Found defaults and accessors. Tracing `isCtoMultiThreadEnabled` and `delayInsertionEnableMt` into the live parallel paths.

Local call sites exist for both accessors. Tracing how `_enableMultiThread` and `delayInsertionEnableMt` actually gate parallel work.

`_enableMtTask` defaults true while `enable_multi_thread` defaults false — checking whether that bypasses the intended gate.

Revision defaults to 1, which forces delay-insertion MT on. Checking the commented-out `isMultiThreadEnabled` gate and how `_enableMtTask` bypasses it.

Tracing whether the revision-forced MT path and the commented-out gate reach order-sensitive work.

Validating production reachability of the commented-out gate and whether delay-insertion MT has order-sensitive commits.

The option/revision mismatch is clear; I'm checking whether the forced MT path has order-sensitive shared mutation, not just parallel speedup.

**Verdict: evidence is insufficient for Gate-inactive / Real.**

CoreStory plus targeted local validation found a strong control-path near-miss, but not a complete causal chain to run-to-run observable nondeterminism.

### Strongest near-miss (not elevated)

**Control:** `cts.optimize.delay_insertion_enable_mt` → `_delayInsertionEnableMt` / `delayInsertionEnableMt()`

| Step | Evidence |
|------|----------|
| Definition / default | Registered in `ctsutil/ctsAppOptions.cc`; `_delayInsertionEnableMt(false)`; UI default also `false` (`ctsui/ctsuiOptimizeAppOptions.cc`) |
| Bypass | `_delayInsertionEnhancementRevision` defaults to **1**; accessor is `enabledByRevision(1) \|\| _delayInsertionEnableMt \|\| flag-bit`, so the bool is true by default and setting the option false does not disable it while revision stays 1 |
| Propagation | `ctscto::meetTargetLatency` / overload: `if (useGRE && delayInsertionEnableMt())` → `meetTargetLatencyMtInternal` → `ctoTargetLatInserter::run` |
| Parallel op | `performDelayInsertion` → `dlyFlow(problemDefs).run` → lock suspend + `_xformSuite->runAccurate` (comments explicitly mark a multi-thread region; `preRunBatches` hoists blockage-map work “to avoid data race in worker thread”) |
| Observable sink | Inserted buffers / latency / summary via `printInsertionResult` / `printSummaryTable` |

`setOptimizeModeRuntimeInMap` toggles `delay_insertion_enable_mt` without changing revision, which reinforces that the named option does not actually govern the accessor under default revision.

### Why not Gate-inactive / Real

Criteria 1–3 are supported (live GRE MT path; option intended to gate it; option ineffective under default revision). Criteria 4–5 are not: post-join commit walks problems in stable index order (`dlyFlow::runBatches` → `dlyResultIntegrator::commit`), and there is no established proof that equivalent runs change QoR/buffering because of concurrency—only that MT evaluation runs.

### Also not elevated

Commented-out `if (!isMultiThreadEnabled()) return false;` in `ctscto::areaRecoveryMultiThread` is a classic inactive-gate shape, but entry is further gated by `enable_cto_mt_area_removal` / `enable_cto_mt_area_sizing` (default **false**), and the same ND-sink gap remains.

### Missing evidence for Real

Thread-count A/B (`-nthreads 1` vs `N`) on GRE target-latency with default revision=1, comparing raw post-insertion latency / buffer set; and/or showing cross-problem interference inside `runAccurate` that is not neutralized by index-ordered commit.

