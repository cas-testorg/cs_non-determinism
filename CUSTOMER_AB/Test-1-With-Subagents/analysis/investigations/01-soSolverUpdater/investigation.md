# Investigation Checkpoint — Non-Determinism Candidate in Fusion Compiler CTS Skew Optimization

**Scope:** CoreStory project `10` (`cts-code`); `cts-code2`/project 9 excluded.
**Candidate:** `ccd/skewopt/soSolverUpdater.cc` ~line 2100, `tbb::parallel_for_each` with concurrent `std::map::operator[]` on shared solver maps.
**Method:** agentic-bug-resolution playbook. No source was modified. Evidence tags: **[SRC]** direct source, **[CS]** CoreStory application evidence, **[INF]** reasoned inference, **[OPEN]** unresolved.

## Problem Summary

The candidate hypothesizes that `tbb::parallel_for_each` workers concurrently perform `std::map::operator[]` on shared solver maps, and that the resulting tree insertion/rebalancing is a data race producing corrupted or run-dependent solver state (a non-determinism source).

**Verdict: The reported mechanism is not substantiated as a real race.** The reported line performs lookups on **prepopulated** keys, and the deeper, more plausible "shared solver maps" are **prepopulated single-threaded before the parallel region** and **partitioned per-scenario** across workers. One narrow, practically-benign standard-technicality remains open, plus runtime confirmation items.

## Components Involved

- `soCgSolverUpdater::addLogSumExpFuncsToSolver` — the reported `parallel_for_each` site. **[SRC]** `ccd/skewopt/soSolverUpdater.cc:2088–2113`
- `_setupScenarioInfosMap` / `_holdScenarioInfosMap` — `std::map<cstrScenario, updateInfoVecType>`, `updateInfoVecType = std::vector<updateInfo*>`. **[SRC]** `soSolverUpdater.h:152, 519–520`
- `soCgSolver::addLogSumExpFunc` / `addToLogSumExpFunc` / `initScenarioLSETable` — writers to solver-owned maps `_setupLogSumExpFuncs` / `_holdLogSumExpFuncs` (`std::map<cstrScenario, soCgEpLogSumExpFuncMapType>`). **[SRC]** `soCG.cc:1075, 1044, 1167`; `soSolverFuncs.h:139`; `soCG.h:510–511`
- Entry driver `soCgSolverUpdater::updateSolver`. **[SRC]** `soSolverUpdater.cc:875`

CoreStory characterizes the reported chunk as code that "parallel-adds per-scenario log-sum-exp timing functions from the accumulated setup and hold update infos to the solver," and `soCG.cc` as "the core multithreaded conjugate-gradient skew optimization solver." **[CS]**

## Findings Against the 10 Required Determinations

**1. Part of the production build — YES. [SRC]**
`ccd/skewopt/Master.make` `CPPFILES` lists `soCG.cc` (line 23), `soSolverUpdater.cc` (line 25), plus `soSolverPostOpt.cc`/`soDesign.cc`. The skewopt library is compiled from these.

**2. Reachable from production skew-opt paths — YES. [SRC]**
`updateSolver` is invoked from the skew-optimization driver `soDesign.cc:7269, 7460`, from `soSolverPostOpt.cc:283`, and `soCG.cc:2846`. `updateSolver → updateSolverUseSetClockArrival (soSolverUpdater.cc:908/1470) → addLogSumExpFuncsToSolver (1492)`.

**3. Conditions that execute the parallel path. [SRC]/[INF]**
`addLogSumExpFuncsToSolver` runs inside `updateSolverUseSetClockArrival`, which `updateSolver` calls only when `_useUpdateArrival && !_config.ioOnly()` (soSolverUpdater.cc:907). Worker count = number of setup/hold scenarios; effective parallelism requires a multi-scenario (multi-corner/mode) design **[INF]**. Setup and hold loops run **sequentially** (two separate `parallel_for_each`, 2100 and 2107).

**4. State shared between workers. [SRC]**
- `_setupScenarioInfosMap`/`_holdScenarioInfosMap` — read via `operator[]` (2101/2108); each worker reads a **distinct** value.
- `solver` (`soCgSolver*`) — written via `addLogSumExpFunc → _setupLogSumExpFuncs[scenario]` and `funcs[ep]=newFunc` (soCG.cc:1084–1099).
- `_updater->getInfoOrder()` — read-only during `reorderSlackFuncs` (soSolverUpdater.cc:5247). **[INF]**

**5. Whether concurrent map insertion/mutation can actually occur — NO (structural mutation does not). [SRC]**
- *Reported line (2101/2108):* keys are prepopulated immediately before the loop from the map's own keys (2093–2099: `for (auto& it : _setupScenarioInfosMap) setupScenarios.emplace_back(it.first);`). `operator[]` on an existing key performs no insertion/rebalancing.
- *Deeper solver maps:* each worker's infos all carry `_scenario == sc` (constructed with that scenario at soSolverUpdater.cc:637, 654/662), so worker `sc` touches only the **distinct** inner map `_setupLogSumExpFuncs[sc]`. Different workers never mutate the same inner map.

**6. Mechanism that prevents the race — prepopulation + partitioning. [SRC]**
At the top of `updateSolver`, single-threaded, before any parallel work:

```887:892:ccd/skewopt/soSolverUpdater.cc
  // Make sure all scenarios have a map entry in solver before starting
  for (auto& it : _setupScenarioInfosMap) {
    solver->initScenarioLSETable(it.first, true);
  }
  for (auto& it : _holdScenarioInfosMap) {
    solver->initScenarioLSETable(it.first, false);
  }
```

`initScenarioLSETable` creates the outer entry (`funcsMap[scenario]`), so during the parallel region `_setupLogSumExpFuncs[scenario]` is a **lookup on an existing key**, not an insertion:

```1167:1172:ccd/skewopt/soCG.cc
soCgSolver::initScenarioLSETable(cstrScenario scenario, bool setup)
{
  soCgEpLogSumExpFuncsMapType& funcsMap = setup ? _setupLogSumExpFuncs : _holdLogSumExpFuncs;
  soCgEpLogSumExpFuncMapType& funcs = funcsMap[scenario];
  return funcs.size();
}
```

So there are two independent protections: (a) reported-level keys prepopulated from the map itself; (b) solver-level outer keys prepopulated via `initScenarioLSETable` and inner maps partitioned one-per-scenario per worker. `std::map` nodes are reference-stable under lookups, so per-scenario references stay valid while other workers operate.

**7. How written values are consumed downstream. [SRC]/[INF]**
Values land in `_setupLogSumExpFuncs[scenario][ep]` (cloned `soCgEpLogSumExpFunc`, soCG.cc:1090–1099). They are consumed **after** `updateSolver` returns — the `parallel_for_each` join is a happens-before barrier — by the CG cost/gradient machinery (`getSetupLogSumExpFuncs()` at soSolverUpdater.cc:2154; job builders at soCG.cc:3161+, 3204+, 3451+) and `addStartPointLogSumExpFunc`. Production and consumption are separated by a synchronization barrier. **[INF]**

**8. Credible path from the suspected race to observable behavior — NOT established. [INF]**
Because no shared map is structurally mutated concurrently and consumers run after a join barrier, there is no substantiated path from the reported mechanism to run-dependent solver state.

**9. Blast radius if it were real. [INF]**
Hypothetically severe (corrupted per-scenario LSE tables would perturb CG timing objectives/gradients → run-dependent skew-optimization QoR across multi-corner CTS). But conditioned on a defect that current evidence does not support.

**10. Unresolved evidence requiring SME/runtime validation. [OPEN]**
- **Standard technicality:** per `[container.requirements.dataraces]`, `std::map::operator[]` is excluded from the functions treated as `const` for associative containers, so concurrent `operator[]` even on existing keys is not *standard-guaranteed* thread-safe. On libstdc++/libc++ it is lookup-only (no write) in practice, but this rests on implementation behavior, not a guarantee. Confirm the STL/toolchain used for production builds.
- Confirm production defaults for `_useUpdateArrival` / `ioOnly` and typical scenario/thread counts (whether the parallel region meaningfully engages).
- Confirm no *other* concurrent writer touches `_setupLogSumExpFuncs`/`_holdLogSumExpFuncs` during this window (searches show none within the region, but runtime confirmation is stronger).
- A ThreadSanitizer run over a multi-scenario CUS design would empirically settle all of the above.

## CoreStory Evidence

- `list_projects` confirmed project `10 = cts-code` (and `9 = cts-code2`, excluded). **[CS]**
- `semantic_search` corroborated the code semantics: the reported chunk "parallel-adds per-scenario log-sum-exp timing functions ... to the solver," and `soCG.cc` is "the core multithreaded conjugate-gradient skew optimization solver." No CoreStory business rule was found asserting a known non-determinism defect at this site. **[CS]**

## Impact Analysis

Under the observed design (single-threaded prepopulation + per-scenario partitioning + post-join consumption), the reported `operator[]` race is prevented. If the standard-technicality concern were realized on some toolchain, the blast radius would be skew-opt QoR non-determinism across multi-corner CTS; current evidence does not indicate this occurs.

## Suggested Next Steps

Per playbook guardrails, **no code change is recommended at this checkpoint.** This candidate should be classified **not a confirmed defect (false positive as reported)**, pending the runtime confirmations in item 10. If the team wants belt-and-suspenders hardening for the standard technicality, that is an optional, separate discussion — not justified as a defect fix by current evidence.

## Validation Plan

1. **TSan run:** build skewopt with `-fsanitize=thread`, run a multi-corner/multi-mode CUS testcase through `updateSolver`; expect no reports on `_setupLogSumExpFuncs`/`_holdLogSumExpFuncs` or `_setup/_holdScenarioInfosMap`.
2. **Determinism harness:** run the same design N times, checksum the post-`updateSolver` LSE tables (a `printChecksum()` already exists at soSolverUpdater.cc:913); expect identical checksums.
3. **Config confirmation:** verify `_useUpdateArrival`/`ioOnly` production defaults and scenario counts to ensure the parallel path is actually exercised in step 1–2.
4. **Toolchain confirmation:** record the STL implementation used in production to close the `operator[]` standard-technicality item.

---
**Distinct evidence classes:** Build inclusion, reachability, prepopulation, partitioning, and the reported-line lookup behavior are **[SRC]** (direct code). Application/semantic framing is **[CS]**. Trigger conditions, distinct-scenario ownership, and consumption ordering are **[INF]**. The standard-`operator[]` guarantee, production config/thread counts, and empirical race-freedom are **[OPEN]** and require SME/runtime validation.

I stopped at the investigation checkpoint and made no source modifications.
