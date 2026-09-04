# TC-004 Results — Gate-Inactive / Determinism-Control Propagation

## Test status

```text
PASS
```

## Environment

```text
Date/time: 2026-09-04, run started approximately 12:30 CDT
Agent/client: Cursor
Agent/client version: 3.18.25
Model: not recorded in exported artifact
CoreStory project/workspace: cts-code, project id 10
Repository/revision: local CTS repository; exact revision not recorded in exported artifact
Existing Cursor sessions backed up/preserved: user performed purge/restart before run
TC-004 started in a fresh Cursor chat: YES
Prior TC-004 conversation context in new chat: NO known prior context
Customer skill installed/available: YES — prove-nd-mt loaded from Cursor skills
CoreStory rule installed/active: YES by test setup
CoreStory MCP available: YES
Other relevant rules/skills active: base prove-nd availability was checked by the agent
```

## Prompt

The exact prompt from `README.md` was used as a single initial prompt without user steering.

## Agent final response

The agent concluded that the available evidence was **insufficient for Gate-inactive / Real**. It identified a strong control-path near-miss around `cts.optimize.delay_insertion_enable_mt`, proved that the explicit option can be ineffective under the default enhancement revision, traced the control into a live multi-threaded delay-insertion path, and then declined to elevate it because variable observable nondeterminism was not established and the post-join commit path appeared stable.

The final response also identified a second classic inactive-gate shape in `ctscto::areaRecoveryMultiThread`, where an `isMultiThreadEnabled()` check is commented out, but correctly did not elevate it because the surrounding feature gates default false and the ND sink remained unproven.

## Cursor investigation trace

### User prompt sent

The exact TC-004 prompt from `README.md` was used. It required CoreStory-first discovery of a control path spanning definition/default, propagation, the governed parallel operation, and downstream behavior; it also required proof that the control is actually ineffective and that observable ND survives before classifying Gate-inactive / Real.

### CoreStory interactions

The agent:

1. Loaded the `prove-nd-mt` skill and CoreStory tool schemas.
2. Queried CoreStory for inactive or bypassed determinism/threading controls.
3. Refined the initial `enable_multi_thread` propagation-gap lead.
4. Asked about stronger determinism cascades, thread-count gates, and dead/commented-out locking controls.
5. Used CoreStory to narrow toward `delay_insertion_enable_mt`, its revision-based enablement, related accessors, and the relevant multi-threaded delay-insertion path.
6. Continued to use CoreStory to test whether the control anomaly reached an order-sensitive operation or observable sink.

### First CoreStory-supplied control path

```text
Control / gate: cts.optimize.delay_insertion_enable_mt
Definition/configuration site: ctsutil/ctsAppOptions.cc and ctsui/ctsuiOptimizeAppOptions.cc
Default / activation condition: explicit bool defaults false, but delay-insertion enhancement revision defaults to 1
Propagation path: _delayInsertionEnableMt / delayInsertionEnableMt() -> ctscto::meetTargetLatency -> meetTargetLatencyMtInternal -> ctoTargetLatInserter::run
Governed parallel operation: performDelayInsertion -> dlyFlow(problemDefs).run -> _xformSuite->runAccurate
Downstream consumer: inserted buffers / latency / summary output
```

### Local repository validation

Local source inspection was used to validate:

- option registration and defaults,
- the `enabledByRevision(1) || _delayInsertionEnableMt || flag-bit` accessor behavior,
- call sites of `isCtoMultiThreadEnabled` and `delayInsertionEnableMt`,
- the live GRE delay-insertion MT path,
- `_enableMtTask` and revision-based enablement,
- the commented-out `isMultiThreadEnabled()` gate in area recovery,
- the `runAccurate` parallel region and comments about avoiding worker-thread data races,
- post-join integration/commit behavior and whether it preserved variable completion order.

### Broad local discovery searches

```text
Were broad product-wide searches used: Limited/targeted rather than primary discovery
If YES, when relative to CoreStory candidate selection: after CoreStory had already supplied control-path leads
Why the agent broadened: to prove defaults, propagation, exact gate scope, and whether a real ND sink survived
Patterns/areas searched: specific accessors, revision flags, enable_mt controls, call sites, delay-insertion paths, and related MT gates
```

### Unexpected agent/tool behavior

No blocking tool failure was observed. The notable behavior was positive: the agent did not treat the discovered option/revision mismatch as sufficient proof of ND and continued through the actual execution and sink path.

## Candidate and causal evidence

```text
Candidate: cts.optimize.delay_insertion_enable_mt control path
File(s): ctsutil/ctsAppOptions.cc; ctsui/ctsuiOptimizeAppOptions.cc; CTS CTO/delay-insertion implementation files reached by meetTargetLatency / performDelayInsertion
Symbol(s): _delayInsertionEnableMt; delayInsertionEnableMt(); _delayInsertionEnhancementRevision; meetTargetLatencyMtInternal; ctoTargetLatInserter::run; performDelayInsertion; dlyFlow::run; _xformSuite->runAccurate
```

### Control definition / intended behavior

The explicit option is registered as a delay-insertion MT control and defaults to false. The path therefore presents itself as a control over whether this work uses multi-threading.

### Default / activation condition

The agent established that `_delayInsertionEnhancementRevision` defaults to `1`, while the accessor uses a condition equivalent to:

```text
enabledByRevision(1) || _delayInsertionEnableMt || flag-bit
```

As a result, the MT accessor evaluates enabled under the default revision even when the explicit boolean option remains false.

### Propagation path

The agent traced the control through `delayInsertionEnableMt()` into `ctscto::meetTargetLatency`, then to `meetTargetLatencyMtInternal`, `ctoTargetLatInserter::run`, `performDelayInsertion`, and `dlyFlow(problemDefs).run`.

### Parallel reachability / governed operation

The path reaches `_xformSuite->runAccurate` inside an explicitly multi-threaded region. Source comments and nearby setup also indicate that some pre-work is deliberately hoisted before the worker region to avoid a data race, supporting that the MT path is real rather than hypothetical.

### Why the control is ineffective

The explicit `delay_insertion_enable_mt=false` value does not disable the path while revision 1 remains active. The agent also observed that runtime mode code can toggle the named option without changing the revision, reinforcing that the option alone does not govern the effective accessor under the default revision.

### Variable ordering / concurrency-sensitive behavior

This was **not fully established**. The agent proved MT execution, but did not prove that equivalent runs can produce different buffering/QoR outcomes because of variable worker ordering.

### Downstream consumer / observable impact

Inserted buffers, latency values, and summary output are observable application results on the path. However, the agent did not establish that their values vary because of the control anomaly.

### Neutralizer / post-condition audit

The post-join integration path appeared to commit problems in stable index order. That prevented the agent from proving that parallel completion order survives into the observable result.

### Missing evidence identified by agent

The agent explicitly called for either:

- thread-count A/B validation (`1` vs `N`) on the GRE target-latency path with default revision 1 while comparing raw post-insertion latency / buffer sets, or
- source/runtime proof of cross-problem interference inside `runAccurate` that is not neutralized by the index-ordered post-join commit.

## Skill behavior assessment

```text
Gate-audit reasoning applied:                      YES
MT reachability established:                       YES
Control intent verified from code/path:            YES
Default / activation behavior checked:             YES
Propagation to execution site checked:             YES
Exact control scope verified:                       YES
Variable ordering consequence investigated:         YES
Observable sink investigated:                       YES
Neutralizer investigated:                           YES
Missing evidence stated rather than guessed:        YES
```

Notes:

The strongest aspect of the run was the refusal to equate an ineffective gate with a proven ND defect. The agent found a real control mismatch, then continued through the MT operation, observable sink, and neutralizer before deciding that criteria 4–5 were still missing.

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:      YES
Queries preserved gate/control objective:           YES
Definition-to-execution path identified:            YES
Targeted source used for validation:                 YES
Causal evidence requirement preserved:              YES
Unsupported findings avoided:                       YES
```

Notes:

CoreStory supplied useful control-path leads and helped keep the investigation centered on option/default/propagation relationships. Local source work primarily verified the exact behavior of those supplied paths.

## CoreStory narrowing assessment

```text
Control identified before broad grep:               YES
Default/config behavior identified:                  YES
Propagation/call path identified:                    YES
Governed parallel operation identified:              YES
Downstream consumer identified:                      YES
Local proof remained targeted:                       YES
Broad product-wide discovery required:               NO
```

Notes:

TC-004 extends the narrowing improvement seen in TC-003. CoreStory helped turn what could have become a repository-wide search for flags, locks, and thread gates into validation of a concrete control-to-execution path.

## Cursor interaction observations

```text
CoreStory interactions: multiple targeted CoreStory queries/refinements before source validation
Local repository searches/reads: targeted reads/greps around the CoreStory-supplied control path and related MT gates
Files inspected: option/default files plus CTO/delay-insertion execution and integration paths
Broad repo-wide searches: no broad product-wide discovery sweep was observed as the primary strategy
Repeated/redundant searches: some iterative verification of accessors/gates, but aligned with proof requirements
Unexpected agent behavior: none materially negative
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope.

## Test verdict

```text
PASS
```

### Rationale

TC-004 passed as a workflow-integration test. The objective was not to force a Real defect; it was to test whether the combined CoreStory rule and customer skill could trace a determinism/threading control through defaults, propagation, live MT execution, and downstream behavior while preserving the proof standard for ND.

The run did that successfully. It identified and proved a real option/revision mismatch, established a live multi-threaded path, investigated downstream observability and stable post-join behavior, and stopped at insufficient evidence rather than promoting the control anomaly into a Real nondeterminism finding.

## Follow-up

```text
Recommended next mechanism: concurrent container insertion / iteration-order dependence
Reason: test whether CoreStory can identify a parallel producer -> shared container -> consumer/canonicalizer path and whether completion/insertion order survives into observable behavior.
```
