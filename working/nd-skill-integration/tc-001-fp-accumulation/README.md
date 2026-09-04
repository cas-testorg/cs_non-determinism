# TC-001 — Race-Free Floating-Point Accumulation

## Status

```text
NOT RUN
```

## Objective

Evaluate the interaction between:

- the customer's `prove-nd-mt` skill,
- the existing CoreStory `code-analysis-v2.mdc` rule, and
- Cursor agent behavior

using one narrowly defined multi-threaded nondeterminism mechanism:

> race-free but order-dependent floating-point accumulation or reduction.

This is an integration/workflow test. It is **not** intended to establish defect coverage for the customer codebase.

Token metering, LiteLLM routing, JSONL analysis, and model-request accounting are explicitly **out of scope** for this test.

## Why this mechanism

The customer skill explicitly identifies non-associative floating-point reduction as an observable MT nondeterminism sink when accumulation order can vary. It also requires proving MT reachability and checking for deterministic canonicalization before classifying a candidate as Real.

This mechanism therefore exercises several important behaviors without starting with an unrestricted repository-wide ND investigation.

## Artifacts under test

### Skill

```text
references/SKILL.md
```

Expected relevant behavior includes:

- distinguish race-free ordering defects from data races;
- prove the code actually executes under multi-threading;
- identify the parallel dispatch site;
- recognize that a mutex does not make floating-point accumulation deterministic;
- inspect downstream observable consumers;
- verify whether a post-join canonicalization pass neutralizes the condition;
- verify canonicalizer coverage rather than trusting its name;
- identify missing evidence rather than guessing.

### Rule

```text
archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc
```

Expected relevant behavior includes:

- use CoreStory as the primary source of application intelligence;
- preserve the investigation objective in CoreStory queries;
- use CoreStory to narrow components/files/functions/call paths/shared state/consumers;
- inspect targeted local source after application context is established;
- distinguish observed evidence from inference;
- require a causal chain to observable impact;
- avoid manufacturing findings.

## Clean Cursor test boundary

Before running TC-001:

1. Back up or preserve the existing Cursor chat/session history.
2. Do not use an existing ND investigation chat for this test.
3. Start a fresh Cursor agent chat.
4. Confirm the customer ND skill is available.
5. Confirm the CoreStory rule is active.
6. Confirm CoreStory MCP is available.
7. Run only the exact TC-001 prompt below.
8. Do not add follow-up steering during the initial run.
9. Preserve the Cursor transcript and relevant visible tool activity.
10. Stop after the first complete run and record the results before changing anything.

The purpose of the fresh chat is to minimize carryover from prior agent conversation context and make the Cursor/CoreStory interaction easier to evaluate.

Do not delete prior chats as part of the test; preserve them as historical evidence.

## Controls

Before running, record the following in `results.md`:

```text
Date/time: Friday, September 4, 2026 9:07:50 AM
Agent/client: Cursor
Agent/client version: Version: 3.18.25
Model: gtp-5.4
CoreStory project/workspace: cts-code https://corestory.synopsys.com/chat/10
Repository/revision under investigation: NA
Existing Cursor sessions backed up/preserved: YES
TC-001 started in a fresh Cursor chat: YES
Prior TC-001 conversation context in new chat: NONE
Customer skill installed/available: YES
CoreStory rule installed/active: YES
CoreStory MCP available: YES
Other relevant rules/skills active: rules/code-analysis-v2.mdc
```

Do not change the skill or rule for this test.

Do not introduce the Workflow Dispatcher yet.

Do not provide a known defect location to the agent.

## Exact test prompt

Send the following as a single prompt without additional steering:

```text
Investigate the repository for multi-threaded nondeterminism caused by race-free but order-dependent floating-point accumulation.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start by using CoreStory to identify likely parallel execution paths, shared floating-point accumulators or reductions, and their downstream consumers.

For any candidate, do not classify it as Real until you establish:
1. the code actually executes under multi-threading,
2. accumulation order can vary,
3. the value reaches an observable consumer, and
4. no complete deterministic canonicalization occurs before that consumer.

Return only the strongest supported candidate, or state that the available evidence is insufficient.
```

## During execution

Do not correct or steer the agent during the initial run.

Capture enough evidence to reconstruct the Cursor investigation sequence, especially:

```text
User prompt sent
CoreStory queries/tool calls visible in Cursor
Local repository searches/tool calls visible in Cursor
Files/symbols inspected
Candidate identified
Parallel dispatch evidence
Shared accumulator/reduction evidence
Synchronization evidence
Downstream consumer evidence
Canonicalization/neutralization investigation
Final classification
Missing evidence stated by agent
```

If the agent encounters a tooling failure, preserve it rather than changing several variables mid-run.

## Evaluation questions

### A. Skill activation and reasoning

- Did the agent actually apply MT-specific reasoning?
- Did it distinguish a data race from race-free order dependence?
- Did it require MT reachability rather than infer concurrency from a lock?
- Did it treat locking as race protection rather than proof of determinism?
- Did it investigate canonicalization/neutralization?

### B. CoreStory rule behavior

- Was CoreStory used before broad local repository exploration?
- Were CoreStory queries phrased around the defect mechanism and application relationships rather than generic text search?
- Did CoreStory narrow the local source investigation?
- Did the agent use local source to validate rather than replace application-level intelligence?

### C. Evidence quality

For an elevated candidate, did the agent establish:

```text
parallel dispatch
    -> shared/order-sensitive floating-point operation
    -> variable accumulation order
    -> downstream consumer
    -> observable result
```

Did it look for a determinism-restoring mechanism before calling the candidate Real?

### D. Cursor interaction observations

Record, where observable:

```text
CoreStory interactions
Local repository search/read operations
Files inspected
Broad repo-wide searches
Repeated searches for information CoreStory had already supplied
Unexpected agent behavior or tool selection
```

The purpose of these observations is to understand how Cursor applies the skill and rule, not to calculate token or model-request efficiency.

## Test outcome criteria

### PASS

The combined workflow:

- uses CoreStory to narrow the investigation;
- follows the customer's MT-specific proof discipline;
- validates targeted source evidence;
- investigates neutralization/canonicalization;
- and either produces one causally supported candidate or explicitly concludes evidence is insufficient.

### PARTIAL

The workflow reaches a reasonable conclusion but materially skips either the CoreStory-first behavior or an important skill-required proof step.

### FAIL

Examples:

- CoreStory is bypassed despite being available;
- the agent labels any locked floating-point accumulation deterministic solely because a mutex exists;
- the agent claims a Real defect without proving MT reachability or observable impact;
- the agent performs a broad speculative scan and returns unsupported findings;
- the agent ignores a discovered canonicalization mechanism without evaluating it.

### INCONCLUSIVE

Use when Cursor, CoreStory MCP, repository access, or another required test dependency prevents the workflow from being meaningfully evaluated.

## Stop condition

Stop after the first complete run and record the results before changing the prompt, skill, rule, model, environment, or Cursor configuration.

Do not proceed immediately to another ND mechanism. Review TC-001 first and use its evidence to decide what TC-002 should test.
