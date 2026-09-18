# Non‑Determinism Investigation — `msClockDrivers::findDriverTerm` (Fusion Compiler CTS)

**Playbook:** `agentic-bug-resolution` · **CoreStory scope:** project ID 10 (`cts-code`) only · **No source modified.** I did not use the `.cursor/nd-scan/` artifacts (prior ND reports/AI conclusions) as evidence, per constraint.

Evidence tags used below: **[SRC]** direct source, **[CS]** CoreStory app evidence, **[INF]** reasoned inference, **[?]** unresolved.

---

## Problem Summary

Reported hypothesis: a raw‑pointer set iterated in address order selects/retains a driver term by "last encountered," making the returned driver term address‑dependent. I treated this as a hypothesis and verified each link independently.

**Outcome: the reported mechanism is real in source, but only partially. The defect is confined to the *scalar return value* of `findDriverTerm`, not to the accumulated `drvTerms` output. Most callers neutralize it; a specific set of auto‑tap / multisource synthesis callers do not.**

---

## The candidate code [SRC]

The reported branch (`msDrivers.cc` 711–723), active when `enableMLPHFlow && loadNetSet->size() > 1 && leafLevel`:

```711:723:mscts/drivers/msDrivers.cc
  std::set<ndmNet*>* loadNetSet = _msOptions.getLoadNetSet();
  if(_appOptions.enableMLPHFlow && loadNetSet && loadNetSet->size() > 1 && leafLevel) {
    std::set<ndmNet*>::iterator itrS = loadNetSet->begin(), itrE = loadNetSet->end();
    for(; itrS != itrE; itrS++) {
      l_drvTerm = (*itrS)->getFirstFlatDriver();
      if ( l_drvTerm) {
        if (true) {//isOnClockNetwork(l_drvTerm, /*isDriver*/ true) )
          drvTerms.insert(l_drvTerm);
        }
      }
    }
  } ...
  return l_drvTerm;
```

There is **no `break`**, and `l_drvTerm` is overwritten every iteration → the returned scalar is `getFirstFlatDriver()` of the **last net in iteration order** (last‑wins).

---

## Findings against the 11 required questions

**1. Part of the production build?** **Yes [SRC].** `mscts/drivers/Master.make` lists `msDrivers.cc` and `msAutoTapFlow.cc` under `CPPFILES` in module `drivers`, `FEATURE_AREA = nwtn.mscts`. Not a test target.

**2. Reachable from production CTS paths?** **Yes [SRC][CS].** `findDriverTerm` has real production callers (below). CoreStory describes `msDrivers.cc` as *"multi‑source clock tree driver management logic … for clock‑driver insertion within the Synopsys CTS flow,"* and the chunk containing `findDriverTerm` as *"identifies and collects valid clock‑driver terminals … across MLPH/non‑MLPH flows."* **[CS]**

**3. Concrete container & what determines iteration order?** **`std::set<ndmNet*>` with the default `std::less<ndmNet*>` comparator → ordered by raw pointer address [SRC].**
- `getLoadNetSet()` returns `std::set<ndmNet*>*` (`msDrivers.h:417`).
- Allocated as `_loadNetSet = new std::set<ndmNet*>()` (`msDrivers.cc:10309`) — **no custom comparator**.
- Notably, a stable alternative exists and is unused here: `ctsTypes.h:127` defines `netSetType = std::set<ndmNet*, ndmObjPtrCmpType>`, where `ndmObjPtrCmpType = ndmObjectHandleNS::compareObjPtr` (a handle/ID‑based stable comparator). So iteration order of `_loadNetSet` is **address‑dependent** → run‑to‑run variable under ASLR/allocator differences. **[SRC]/[INF]**

**4. Population & can multiple candidates occur?** **Yes [SRC].** `msDriversOptions::addLoadNet()` (`msDrivers.cc:10306`) inserts one net per call. Callers:
- `msuiCreateClockDrivers.cc:621` — the `-load` handler loops over all objects and calls `addLoadNet` per net (`no_nets++`), so a multi‑net `-load` yields `size() > 1`.
- `msuiSynRegClkTree.cc:1197, 1247` — regular clock‑tree synthesis adds load nets.
So >1 candidate net is achievable in production.

**5. Does selection depend on iteration order?** **Yes, for the return value only (last‑wins) [SRC].** The `drvTerms` *out‑set* receives **all** non‑null drivers, so its **content is order‑independent**; and `drvTerms` is `termSetType = std::set<ndmTerm*, ndmObjPtrCmpType>` (stable order) [SRC, `ctsTypes.h:124`]. The address dependence is isolated to the scalar `return l_drvTerm` = last net's driver.

**6. Any neutralizer (sort/canonicalization/stable comparator/filter)?** **Partial [SRC]:**
- `drvTerms` uses a **stable comparator** → the set path is deterministic.
- The main driver‑insertion callers **discard the return and re‑derive** the driver from `drvTerms` via `getTopLevelDrvTerm(drvTerms)` (`msDrivers.cc:995`), which returns the first `drvTerms` element whose root hier == top hier, else `*drvTerms.begin()`. Since `drvTerms` is stably ordered and content‑deterministic, this is **deterministic** → the return‑value nondeterminism is **neutralized** in those callers (1262, 1498) and in 262 (return discarded) and 780 (null‑check only).
- **No neutralizer** exists in the auto‑tap/multisource callers that consume the raw return (see Q7/Q8).
- The non‑MLPH `else` branch (746–764) uses a real `break;` (first‑wins on DB term‑iterator order); the MLPH `else if` branch (724–745) has its `//break;` commented, another last‑wins accumulate — same class but outside the reported 711–722 lines.

**7. Callers consuming the returned value [SRC]:**

| Caller | leaf? | Uses return? | Deterministic? |
|---|---|---|---|
| `msDrivers.cc:262` `updateDesignType` | true | discarded; iterates `drvTerms` | Yes (stable set) |
| `msDrivers.cc:780` `checkTemplateCellLevels` | true | null‑check only | Yes |
| `msDrivers.cc:1262` / `:1498` | var | overwritten by `getTopLevelDrvTerm(drvTerms)` | Yes (neutralized) |
| `msDrivers.cc:3400` | **false** | direct | reported branch not taken |
| **`msAutoTapFlow.cc:4477`** | **true** | **direct → `getAClockOnTerm(drvTerm)` + `collectClockTreeSinkAndIcgTerms`**; passes a `dummy` out‑set | **No** |
| **`msAutoTapFlow.cc:5190`** | **true** | **direct → `getAClockOnTerm` → `drvOnClk` → sink/ICG collection** | **No** |
| **`msAutoTapFlow.cc:6194`** | **true** | **same pattern as 5190** | **No** |
| `msAutoTapFlow.cc:1565` etc. | var | `checkCfg(cfg, drvTerm,…)` then later `getTopLevelDrvTerm` | Weak/partial [?] |

**8. Can it propagate into observable CTS behavior?** **Yes, via the auto‑tap/multisource sinks [SRC][INF].** At `msAutoTapFlow.cc:4477/5190/6194`, the raw return feeds `_ctsInfra->getAClockOnTerm(drvTerm)` (clock selection) and `ctsSession::get()->collectClockTreeSinkAndIcgTerms(clock, drvTerm, …)` (sink/ICG set that seeds tap‑section segregation and tree topology). If the last‑visited net's driver differs across runs, the selected clock and collected sink set can differ → different tap synthesis topology/QoR. `getAClockOnTerm` returns "a/fastest clock on term" (`ctsInfraApiNwtn.cc:4146`), so a different driver term **can** map to a different clock. **[SRC]**

**9. Runtime/config conditions required [SRC][INF]:**
- `enable_mlph_flow` = true (`msuiAppOptions.cc:3990`; default **false**, MSUI_BASIC user option) → MLPH (multi‑level physical hierarchy) / auto‑tap or multisource synthesis flow.
- `_loadNetSet->size() > 1` (multiple candidate load nets).
- `leafLevel == true` (the three strong sinks pass `true`).
- **[?]** The candidate nets' `getFirstFlatDriver()` results must differ **and** map to different clocks (or different sink collections). If all candidate drivers sit on one clock net, `getAClockOnTerm` collapses the difference and there is no observable effect.

**10. Likely blast radius (if real) [INF]:** Bounded to MLPH auto‑tap / regular‑multisource clock‑tree **synthesis topology** — clock chosen for a tap driver, the sink/ICG set fed to section segregation, and downstream tap placement/buffering. That can perturb CTS results, timing/skew, and QoR run‑to‑run. It does **not** appear to corrupt correctness of the `drvTerms`‑based main insertion path (neutralized). Severity is "reproducibility/QoR variance," not functional miscompile. **[INF]**

**11. Unresolved (needs SME/runtime) [?]:**
- Whether production MLPH/auto‑tap runs actually populate `_loadNetSet` with ≥2 nets whose drivers differ and belong to different clocks (the trigger for observable divergence).
- `getFirstFlatDriver()` is an `ndm` DB accessor not in this repo; I assume it is deterministic *per net* (nondeterminism is *which* net is last, not the per‑net lookup). Needs confirmation. **[INF]/[?]**
- Whether `getAClockOnTerm`'s "fastest clock" tie‑breaking is itself order‑stable for a fixed term.
- Behavior of the weaker `msAutoTapFlow.cc:1565` path (via `checkCfg`) before the later `getTopLevelDrvTerm` reassignment.

---

## Distinguished conclusions

- **Direct source evidence:** container is `std::set<ndmNet*>` default comparator (address order); return is last‑wins; `drvTerms` is stably ordered and its content is order‑independent; main callers neutralize via `getTopLevelDrvTerm`; three `msAutoTapFlow.cc` callers consume the raw return for clock/sink selection; file is in the production build.
- **CoreStory evidence:** confirms this code is the production multi‑source clock‑tree driver‑management/insertion logic spanning MLPH and non‑MLPH flows.
- **Reasoned inference:** address ordering ⇒ run‑to‑run variance under ASLR/allocator; divergent return can change clock/sink selection and thus tap topology/QoR.
- **Unresolved:** whether production inputs meet all trigger conditions simultaneously (multi‑net, distinct drivers, distinct clocks).

**Assessment:** The reported hypothesis is **substantiated at the source level but narrower than stated** — the ordering risk is real only through the scalar return consumed by the auto‑tap/multisource sinks; the `drvTerms` output path is already deterministic. Classification: a genuine latent non‑determinism defect **pending runtime confirmation** of trigger conditions.

---

## Validation Plan (no code changes yet)

1. **Confirm trigger reachability:** instrument/observe (or ask SME) whether real MLPH auto‑tap / `synthesize_regular_multisource_clock_trees` runs reach `msAutoTapFlow.cc:4477/5190/6194` with `_loadNetSet.size() > 1`.
2. **Prove order dependence deterministically:** in a debug run, log, in the 711–723 loop, each `(*itrS)` net id and `getFirstFlatDriver()` id, plus the final returned `l_drvTerm` and the `getAClockOnTerm` result. Independently, iterate `_loadNetSet` in a **stable** order (e.g., by object id) and compare the selected driver/clock. Divergence ⇒ confirmed.
3. **A/B determinism harness:** run identical design twice under address‑space randomization (or an allocator that shuffles) and diff selected clock, `sinkTerms`/`icgTerms`, and resulting tap topology. Stable `drvTerms` path should not differ; the auto‑tap path is the one to watch.
4. **Confirm clock‑collapse question:** check whether candidate load nets in target testcases map to distinct clocks; if always the same clock, observable impact is nil despite the code smell.
5. **Scope the fix (only after confirmation):** the minimal, behavior‑preserving direction is to make the *return selection* deterministic (e.g., derive the return from the already‑stable `drvTerms`, mirroring `getTopLevelDrvTerm`, or back `_loadNetSet` with the existing stable `netSetType`/`ndmObjPtrCmpType`). Defer until steps 1–4 validate the defect and an SME confirms intended selection semantics.

Stopping at the investigation checkpoint as instructed — no code modified.
