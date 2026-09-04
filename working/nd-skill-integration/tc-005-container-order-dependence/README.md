# TC-005 — Concurrent Container Insertion / Iteration-Order Dependence

## Purpose

Evaluate whether the `prove-nd-mt` skill and CoreStory code-analysis rule can identify and validate multi-threaded nondeterminism caused by concurrent insertion or completion order being preserved in a container and later influencing observable application behavior.

This test intentionally follows TC-003 and TC-004, where CoreStory successfully narrowed the investigation to concrete cross-file paths before local validation. TC-005 asks whether that narrowing holds for a data-flow shape that can be deceptively simple in source but difficult to prove application-wide:

```text
parallel producers
    -> shared container / result collection
    -> insertion / completion order
    -> later iteration / selection / commit
    -> observable result
```

The key distinction is between:

- a container whose order can vary but is later sorted/canonicalized or used only for membership, and
- a container whose variable insertion/iteration order survives into a decision, committed design state, ID assignment, reporting, or other observable output.

## Preconditions

Use the same controlled setup as prior tests.

```text
Agent/client: Cursor
Customer skill: prove-nd-mt
CoreStory rule: code-analysis-v2.mdc
CoreStory MCP: available
Repository under investigation: CTS source corresponding to the CoreStory project
```

Before running:

1. Purge/clear the prior Cursor chat context as practical.
2. Start a fresh Cursor chat.
3. Confirm the customer ND skill is available.
4. Confirm the CoreStory rule is active.
5. Confirm CoreStory MCP is available.
6. Do not modify the skill or rule.
7. Do not provide a known defect location.
8. Run the prompt once without steering.

## Exact prompt

```text
Investigate the repository for multi-threaded nondeterminism caused by concurrent container insertion or iteration-order dependence.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory. Before broad local repository searching, identify the strongest application-level path you can support that includes:
1. a parallel dispatch or concurrent producer set,
2. multiple workers that can append, insert, enqueue, register, or otherwise contribute results to a shared or merged container,
3. a container ordering that can depend on worker completion, arrival, insertion, or commit order across equivalent runs,
4. a later consumer that iterates or selects from that container in its preserved order, and
5. an observable application result that can depend on that order.

For any candidate, do not classify it as Real until you establish:
1. the producers actually execute concurrently,
2. insertion/merge/arrival order can vary across equivalent runs,
3. the relevant container preserves or exposes that variable order,
4. the downstream consumer is order-sensitive rather than membership-only or commutative, and
5. no complete deterministic sort, stable key ordering, canonicalization, set conversion, re-selection, or post-join recomputation neutralizes the order before the observable consumer.

Use local source inspection to validate the strongest CoreStory-supplied path. Avoid broad product-wide grep unless CoreStory cannot establish a candidate path; if you must broaden the search, make that explicit.

Do not treat an unordered container or concurrent append as sufficient evidence by itself. Prove the complete path from parallel production through preserved order to the observable consumer.

Return only the strongest supported candidate, or state that the available evidence is insufficient.
```

## What to capture

Preserve the Cursor export/transcript and record:

- whether `prove-nd-mt` was loaded,
- CoreStory queries/tool calls,
- the first CoreStory-supplied candidate path,
- parallel dispatch / producer set,
- shared or merged container,
- how insertion/arrival/merge order could vary,
- container type and ordering semantics,
- downstream iteration/selection/commit consumer,
- any sort/canonicalization/stable-key neutralizer,
- targeted local source reads/greps,
- whether broad product-wide discovery was required,
- final classification and missing evidence.

Do not use token metering or token-efficiency metrics for this test.

## Special CoreStory narrowing question

TC-005 should explicitly answer:

> Did CoreStory identify enough of the producer → container → consumer → canonicalizer relationship that Cursor could validate a concrete path without first performing a broad product-wide search for `push_back`, `insert`, `emplace`, queues, vectors, maps, and related container operations?

This is the main integration question for TC-005.

## Pass criteria

Classify the workflow test as **PASS** if:

- CoreStory is used before broad local repository discovery,
- the query preserves the concurrent-container/order mechanism,
- CoreStory identifies at least one concrete producer/container/consumer relationship worth validating,
- Cursor verifies actual concurrency and the container's order semantics,
- Cursor checks whether the downstream use is genuinely order-sensitive,
- Cursor audits sort/canonicalization/reselection neutralizers,
- local source work is primarily validation of CoreStory-supplied paths, or the agent explicitly explains why broader discovery became necessary,
- the agent returns a supported Real candidate or explicitly states that evidence is insufficient.

## Partial criteria

Classify **PARTIAL** if the overall conclusion is reasonable but the agent skips an important proof obligation, such as:

- failing to establish actual concurrent production,
- assuming `unordered_*` automatically means run-to-run observable ND,
- failing to inspect downstream order sensitivity,
- failing to inspect sorting/canonicalization,
- or relying on broad local discovery before meaningful CoreStory narrowing.

## Fail criteria

Classify **FAIL** if the agent:

- bypasses CoreStory despite the rule,
- labels a container as nondeterministic solely because it is unordered or concurrently written,
- promotes a candidate without proving an order-sensitive observable consumer,
- ignores a complete deterministic sort/reselection step,
- or produces a speculative product-wide list without a causal path.

## Stop condition

Stop after the first complete run and review the artifacts before creating TC-006.
