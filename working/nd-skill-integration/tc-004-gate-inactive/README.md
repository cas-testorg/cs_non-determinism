# TC-004 — Gate-Inactive / Determinism-Control Propagation

## Objective

Evaluate whether the customer `prove-nd-mt` skill and the CoreStory code-analysis rule work together to prove or dismiss nondeterminism caused by an ineffective determinism/threading gate.

This test focuses on a control that appears intended to serialize, stabilize, disable, or otherwise alter multi-threaded behavior, but may be ineffective because it is not propagated to the real execution path, defaults off, is compiled out, is bypassed, is checked too late, or otherwise does not govern the mutation it is meant to control.

The specific CoreStory hypothesis is stronger than in prior tests: CoreStory should trace the control across files from definition/configuration through propagation and call sites to the actual parallel execution path before broad local repository discovery is needed.

## Mechanism under test

`prove-nd-mt` identifies inactive-gate patterns including:

- false/default-disabled thread-count or determinism gates,
- commented or compiled-out locks,
- no-op/default arguments that do not reach the relevant code,
- distinct locks or controls with misleadingly similar names,
- a lock/gate released before the mutation,
- broken double-checked locking,
- a determinism option that does not propagate to the execution path it is expected to govern.

For this test, prefer configuration or runtime controls that are intended to influence parallel execution or deterministic behavior and can be traced end-to-end.

## Controls

Record before running:

```text
Date/time:
Agent/client:
Agent/client version:
Model:
CoreStory project/workspace:
Repository/revision under investigation:
Existing Cursor sessions backed up/preserved:
TC-004 started in a fresh Cursor chat:
Prior TC-004 conversation context in new chat:
Customer skill installed/available: YES/NO
CoreStory rule installed/active: YES/NO
CoreStory MCP available: YES/NO
Other relevant rules/skills active:
```

Do not modify the customer skill or CoreStory rule for this test.

Do not provide a known defect location or known gate name to the agent.

Do not introduce Workflow Dispatcher or unrelated rules.

## Exact prompt

Use the following as the single initial Cursor prompt:

```text
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
```

## Execution procedure

1. Preserve or back up prior Cursor chat history as needed.
2. Purge prior test/chat context where practical and restart Cursor if that is part of the test hygiene.
3. Start a fresh Agent chat.
4. Confirm the customer ND skill is available.
5. Confirm the CoreStory rule is active.
6. Confirm CoreStory MCP is available.
7. Submit the exact prompt above once.
8. Do not provide follow-up steering during the first complete run.
9. Preserve the final response and Cursor transcript/JSONL artifacts.
10. Record CoreStory interactions separately from local source operations.
11. Stop after the first complete result and review before defining TC-005.

## Evidence to capture

Capture observable Cursor behavior only:

```text
CoreStory project selected:
CoreStory conversation/query sequence:
First control/gate candidate identified:
Control definition/configuration site:
Default value or activation condition:
Propagation path:
Parallel execution/mutation site:
Downstream consumer:
Local files inspected:
Local grep/search operations:
Broad product-wide searches:
Any CoreStory refinement after first candidate:
Final classification:
Missing evidence:
```

## CoreStory narrowing question

This test explicitly asks:

> Can CoreStory trace a control from definition/configuration through propagation to the actual parallel execution site well enough that Cursor's local work is primarily validation rather than discovery?

Record whether:

```text
CoreStory identified the control before broad grep: YES/PARTIAL/NO
CoreStory identified default/configuration behavior: YES/PARTIAL/NO
CoreStory traced propagation/call path: YES/PARTIAL/NO
CoreStory identified the governed parallel operation: YES/PARTIAL/NO
CoreStory identified a downstream consumer: YES/PARTIAL/NO
Local work remained targeted to that path: YES/PARTIAL/NO
Broad product-wide search was required: YES/NO
```

## PASS criteria

Classify TC-004 as **PASS** when the combined workflow does the following:

- uses CoreStory before broad local exploration,
- identifies a concrete control/gate candidate and attempts to trace its propagation,
- distinguishes apparent intent from actual control scope,
- verifies the real parallel execution path and gate effectiveness with targeted source,
- checks default/activation behavior and whether the control reaches the relevant mutation/order-sensitive operation,
- investigates downstream observable impact and any later neutralizer,
- does not elevate a candidate merely because a determinism-like option or lock exists,
- returns a supported Real candidate or explicitly states that evidence is insufficient.

A Real finding is not required for PASS.

## PARTIAL criteria

Use **PARTIAL** when the reasoning is generally sound but the agent skips an important proof obligation, uses substantial broad discovery before CoreStory establishes a path, or relies on the name/intent of a control without fully validating propagation/scope.

## FAIL criteria

Use **FAIL** when the agent:

- bypasses CoreStory despite availability,
- claims a gate is active/inactive from its name alone,
- fails to prove MT reachability,
- fails to trace the control to the actual ordering-sensitive operation,
- treats a configured lock/flag as proof of determinism without checking scope,
- elevates a Real finding without an observable consequence,
- ignores a complete downstream deterministic neutralizer.

## INCONCLUSIVE criteria

Use **INCONCLUSIVE** when tooling, repository access, CoreStory availability, or environment failure prevents meaningful evaluation.

## Stop condition

Stop after the first complete run. Review the transcript, tool path, proof discipline, and narrowing behavior before defining TC-005.
