# TC-002 — Worker-State Carryover / Boundary Reset

## Status

```text
NOT RUN
```

## Objective

Evaluate the interaction between:

- the customer's `prove-nd-mt` skill, and
- the existing CoreStory `code-analysis-v2.mdc` rule

using one narrowly defined multi-threaded nondeterminism mechanism:

> worker-state carryover across reused worker objects when work-item assignment can vary and per-worker mutable state is not fully reset at the work-item boundary.

This is an integration/workflow test. It is **not** intended to establish defect coverage for the customer codebase.

## Why this mechanism

The customer skill contains explicit reasoning for worker-object state carryover and boundary-reset defects. It requires more than finding a mutable member: the investigation must establish worker reuse, variable work-item-to-worker binding, retained state, incomplete reset behavior, and observable downstream impact.

This mechanism also exercises a different CoreStory value proposition than TC-001. Instead of primarily locating a numerical reduction, CoreStory should help establish cross-file lifecycle and relationship context such as:

- worker/thread-pool creation and reuse;
- work-item dispatch and assignment behavior;
- entry-side and exit-side lifecycle methods;
- mutable worker-owned state and its accessors;
- reset/clear/flush methods and their call sites;
- downstream consumers of retained state.

A specific goal of TC-002 is to observe whether CoreStory can narrow this lifecycle investigation before Cursor performs broad product-wide mechanical searches.

## Artifacts under test

### Skill

```text
references/SKILL.md
```

Expected relevant behavior includes:

- prove that the worker object is reused across work items;
- prove that work-item-to-worker assignment can vary across equivalent runs;
- inspect both the entry and exit sides of the work-item boundary;
- distinguish a true state reset from methods that merely flush, publish, or partially clear state;
- search accessors and aliases, not only private member names;
- verify reset polarity and coverage;
- identify whether prior-work state can reach a later work item's result;
- avoid classifying the candidate as Real when reachability or reset evidence is missing.

### Rule

```text
archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc
```

Expected relevant behavior includes:

- use CoreStory as the primary source of application intelligence;
- preserve the worker-carryover investigation objective in CoreStory queries;
- use CoreStory to narrow worker classes, lifecycle methods, call paths, mutable state, accessors, and downstream consumers;
- inspect targeted local source after application context is established;
- distinguish direct evidence from inference;
- require a causal chain to observable impact;
- avoid manufacturing findings.

## Controls

Before running, record the following in `results.md`:

```text
Date/time: Friday, September 4, 2026 10:28:04 AM
Agent/client: Cursor
Agent/client version: Version: 3.18.25
Model: gtp-5.4
CoreStory project/workspace: cts-code https://corestory.synopsys.com/chat/10
Repository/revision under investigation: NA
Existing Cursor sessions backed up/preserved: YES
TC-002 started in a fresh Cursor chat: YES
Prior TC-002 conversation context in new chat: NONE - Backed up then deleted data from previous test
Customer skill installed/available: YES
CoreStory rule installed/active: YES
CoreStory MCP available: YES
Other relevant rules/skills active: NONE
```

Do not change the skill or rule for this test.

Do not introduce the Workflow Dispatcher.

Do not provide a known defect location to the agent.

Start a fresh Cursor conversation.

## Exact test prompt

Send the following as a single prompt without additional steering:

```text
Investigate the repository for multi-threaded nondeterminism caused by worker-state carryover across reused worker objects.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory to identify long-lived worker objects, thread-server or worker-pool reuse, work-item assignment behavior, mutable per-worker state, lifecycle entry/exit methods, accessors, and downstream consumers.

For any candidate, do not classify it as Real until you establish:
1. the worker object is reused across multiple work items,
2. work-item-to-worker binding can vary across equivalent runs,
3. a relevant member can retain state from a prior work item,
4. neither the entry side nor exit side unconditionally restores that state before it is consumed, and
5. the carried value can affect an observable application result.

Inspect both sides of the work-item boundary. Do not assume that a method named reset, clear, flush, or similar fully neutralizes the state; verify what it actually changes and whether all relevant members/accessors are covered.

Return only the strongest supported candidate, or state that the available evidence is insufficient.
```

## During execution

Do not correct or steer the agent during the initial run.

Capture enough evidence to reconstruct the investigation sequence, especially:

```text
CoreStory queries/tool calls
Local repository searches/tool calls
Worker class/object identified
Worker creation/reuse evidence
Parallel dispatch / worker assignment evidence
Mutable per-worker member(s)
Accessor/alias usage
Entry-side reset/initialization evidence
Exit-side reset/cleanup evidence
Reset/clear/flush implementation semantics
Downstream consumer evidence
Final classification
Missing evidence stated by agent
```

If the agent encounters a tooling failure, preserve it rather than changing several variables mid-run.

## Evaluation questions

### A. Skill activation and reasoning

- Did the agent apply the worker-carryover-specific proof discipline?
- Did it prove worker reuse rather than merely find a worker-like class name?
- Did it establish that work-item-to-worker assignment can vary?
- Did it inspect both entry-side and exit-side boundary behavior?
- Did it verify reset semantics instead of trusting method names?
- Did it sweep relevant accessors/aliases where necessary?
- Did it require downstream observable impact?
- Did it state missing evidence instead of guessing?

### B. CoreStory rule behavior

- Was CoreStory used before broad local repository exploration?
- Did CoreStory identify useful worker lifecycle relationships, mutable state, accessors, or downstream consumers?
- Did CoreStory narrow the local source investigation to a smaller set of files/classes/functions?
- Was local source then used to validate the mechanism rather than replace application-level intelligence?

### C. CoreStory narrowing test

Record whether Cursor needed to begin with broad product-wide searches for generic worker/reset/member patterns.

The preferred behavior is:

```text
CoreStory application/lifecycle context
    -> candidate worker class / lifecycle path
    -> targeted member/accessor/reset validation
    -> targeted downstream consumer validation
```

Less desirable behavior is:

```text
broad repository grep for worker/reset/clear/flush/state patterns
    -> large candidate set
    -> CoreStory used only after local discovery
```

Do not mark the test failed solely because a mechanical sweep is required by the skill. The question is whether CoreStory materially narrows **where** that proof work must be performed.

### D. Causal evidence quality

For an elevated candidate, did the agent establish:

```text
reused worker object
    -> variable work-item-to-worker assignment
    -> retained mutable state from prior work item
    -> incomplete entry/exit boundary reset
    -> later work item consumes carried state
    -> observable application result can vary
```

A candidate that lacks any required link should not be classified as Real.

## Cursor interaction observations

Record, where observable:

```text
Number of CoreStory interactions
Number of local repository searches/reads
Number of files inspected
Any broad repo-wide searches
Any repeated searches for information CoreStory had already supplied
Whether CoreStory materially narrowed lifecycle/accessor/reset proof work
```

This test is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope.

## Test outcome criteria

### PASS

The combined workflow:

- uses CoreStory to establish and narrow worker lifecycle context;
- follows the customer's worker-carryover proof discipline;
- validates worker reuse and variable assignment;
- inspects both entry and exit boundary behavior;
- verifies reset semantics and relevant accessors;
- establishes downstream impact before elevation;
- and either produces one causally supported candidate or explicitly concludes evidence is insufficient.

### PARTIAL

The workflow reaches a reasonable conclusion but materially skips either CoreStory-first behavior or an important skill-required proof step, such as entry/exit boundary inspection or reset/accessor verification.

### FAIL

Examples:

- CoreStory is bypassed despite being available;
- a worker-like class is treated as reused without proof;
- a candidate is classified Real without showing variable work-item assignment;
- a method named `reset`, `clear`, or `flush` is assumed to neutralize state without inspection;
- only one side of the work-item boundary is inspected when the other side is relevant;
- downstream observable impact is not established;
- the agent performs a broad speculative scan and returns unsupported findings.

### INCONCLUSIVE

Use when infrastructure/tooling prevents the workflow from being meaningfully evaluated.

## Stop condition

Stop after the first complete run and record the results before changing the prompt, skill, rule, model, or environment.

Do not proceed immediately to another ND mechanism. Review TC-002 first and use its evidence to decide what TC-003 should test.
