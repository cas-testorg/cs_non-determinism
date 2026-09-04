# TC-003 — Commit-Order Dependence / First-Writer-Wins

## Status

```text
NOT RUN
```

## Objective

Evaluate the interaction between the customer's `prove-nd-mt` skill and the CoreStory `code-analysis-v2.mdc` rule on a different multi-threaded nondeterminism mechanism:

> multiple concurrent producers can commit competing results to a shared destination, and the observable result depends on which valid producer commits first or last.

The primary workflow question for TC-003 is narrower than simple correctness:

> Can CoreStory identify a complete parallel producer -> competing commit -> shared destination -> downstream consumer path early enough that Cursor can perform mostly targeted source validation rather than broad repository-wide discovery searches?

This is still a workflow-integration test, not a customer-wide defect-coverage benchmark.

## Why this mechanism

TC-001 and TC-002 both passed the customer's proof discipline, but both still required meaningful local mechanical search after CoreStory discovery. Commit-order dependence should give CoreStory a stronger opportunity to contribute application-relationship intelligence because the proof naturally crosses dispatch, producer, commit, shared-state, and consumer boundaries.

The customer skill treats commit-order dependence and first-writer / first-finder behavior as real MT nondeterminism when competing valid outcomes can reach an observable result and no deterministic arbitration/canonicalization neutralizes the ordering.

## Artifacts under test

### Skill

```text
references/SKILL.md
```

Expected relevant behavior includes:

- establish actual MT reachability;
- identify multiple competing producers or workers;
- distinguish a race from race-free ordering dependence;
- prove that commit order can vary across equivalent runs;
- identify the shared destination or selection point;
- trace the selected/committed value to an observable consumer;
- inspect deterministic arbitration, stable tie-breaking, re-sort, recomputation, or other canonicalization before classifying a candidate Real;
- state missing evidence rather than guessing.

### Rule

```text
archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc
```

Expected relevant behavior includes:

- use CoreStory as the primary source of application intelligence;
- preserve the commit-order mechanism in CoreStory queries;
- identify cross-file/cross-component relationships before broad local exploration;
- use targeted source inspection to validate the mechanism;
- preserve causal evidence and avoid unsupported findings.

## Controls

Before running, record the following in `results.md`:

```text
Date/time:
Agent/client:
Agent/client version:
Model:
CoreStory project/workspace:
Repository/revision under investigation:
Existing Cursor sessions backed up/preserved: YES/NO
TC-003 started in a fresh Cursor chat: YES/NO
Prior TC-003 conversation context in new chat: NONE / describe
Customer skill installed/available: YES/NO
CoreStory rule installed/active: YES/NO
CoreStory MCP available: YES/NO
Other relevant rules/skills active:
```

Do not change the customer skill or CoreStory rule for this test.

Do not introduce the Workflow Dispatcher.

Do not provide a known defect location.

Start a fresh Cursor chat after purging prior chat/session state where practical.

## Exact test prompt

Send the following as a single prompt without additional steering:

```text
Investigate the repository for multi-threaded nondeterminism caused by commit-order dependence or first-writer/first-finder-wins behavior.

Use the prove-nd-mt skill and follow the CoreStory code-analysis rule.

Start with CoreStory. Before broad local repository searching, identify the strongest application-level path you can support that includes:
1. a parallel dispatch or concurrent producer set,
2. two or more producers that can generate competing valid results,
3. a shared destination, commit point, selection site, or winner field,
4. a commit/selection order that can vary across equivalent runs, and
5. a downstream consumer whose observable behavior can depend on which result wins.

For any candidate, do not classify it as Real until you establish:
1. the competing producers actually execute concurrently,
2. their completion or commit order can vary across equivalent runs,
3. the shared destination preserves or exposes that ordering choice,
4. the selected value reaches an observable application result, and
5. no complete deterministic arbitration, stable tie-break, canonicalization, re-sort, or post-join recomputation neutralizes the ordering before that consumer.

Use local source inspection to validate the strongest CoreStory-supplied path. Avoid broad product-wide grep unless CoreStory cannot establish a candidate path; if you must broaden the search, make that explicit.

Return only the strongest supported candidate, or state that the available evidence is insufficient.
```

## During execution

Do not correct or steer Cursor during the initial run.

Capture enough evidence to reconstruct the investigation, especially:

```text
CoreStory queries/tool calls
First candidate path supplied by CoreStory
Parallel dispatch / competing producers
Shared destination / commit / selection site
Why commit order can vary
Downstream consumer
Arbitration / tie-break / canonicalization investigation
Local source validation performed
Any broad local search performed before or after CoreStory candidate selection
Final classification
Missing evidence stated by agent
```

If tooling fails, preserve the failure rather than changing several variables during the run.

## Evaluation questions

### A. Skill activation and reasoning

- Did Cursor distinguish commit-order dependence from a data race?
- Did it prove actual concurrent producers?
- Did it establish a variable completion/commit order?
- Did it identify the shared commit/selection destination?
- Did it trace the winner/selected value to an observable consumer?
- Did it inspect deterministic arbitration or canonicalization before elevation?

### B. CoreStory rule behavior

- Was CoreStory used before broad local repository exploration?
- Did the first CoreStory phase produce a coherent producer -> commit -> consumer path rather than isolated symbols?
- Were CoreStory queries specific to commit-order/selection behavior?
- Was local source inspection primarily validating a CoreStory-supplied path?

### C. CoreStory narrowing test

This is the differentiating criterion for TC-003.

Record:

```text
Did CoreStory identify a complete candidate relationship path before broad grep?       YES / PARTIAL / NO
Did CoreStory identify the dispatch/producers?                                        YES / PARTIAL / NO
Did CoreStory identify the commit/selection site?                                     YES / PARTIAL / NO
Did CoreStory identify a downstream consumer?                                         YES / PARTIAL / NO
Did Cursor still perform broad repository discovery before validating that path?      YES / PARTIAL / NO
Was broad grep needed only after CoreStory failed to establish sufficient evidence?   YES / PARTIAL / NO / N/A
```

The desired behavior is not zero local search. The desired behavior is that local work shifts from discovering the application relationship to validating a relationship already established by CoreStory.

### D. Evidence quality

For any elevated candidate, require this causal chain:

```text
parallel dispatch
    -> competing valid producers
    -> variable completion/commit order
    -> shared destination / winner selection
    -> downstream consumer
    -> observable result
```

Then prove that deterministic arbitration/canonicalization does not neutralize it.

## Test outcome criteria

### PASS

The combined workflow:

- uses CoreStory first;
- follows the customer's commit-order proof discipline;
- validates the strongest CoreStory-supplied path in targeted source;
- investigates deterministic arbitration/canonicalization;
- and either produces one causally supported candidate or explicitly concludes evidence is insufficient.

For a strong PASS on the CoreStory narrowing dimension, CoreStory should establish most of the producer -> commit -> consumer relationship before broad local discovery.

### PARTIAL

Examples:

- the final reasoning is sound but CoreStory only provides isolated leads and Cursor must rediscover the relationship through broad grep;
- CoreStory is used early but an important proof obligation is skipped;
- the agent reaches a reasonable conclusion without fully checking arbitration/canonicalization.

### FAIL

Examples:

- CoreStory is bypassed despite being available;
- a first writer or last writer is assumed nondeterministic without proving concurrent competing producers;
- a data race is mislabeled as race-free commit-order dependence;
- a candidate is called Real without downstream observable impact;
- deterministic arbitration or canonicalization is discovered but ignored;
- unsupported speculative findings are elevated.

### INCONCLUSIVE

Use when infrastructure or tool failure prevents meaningful evaluation.

## Stop condition

Stop after the first complete run and preserve the Cursor transcript/artifacts before changing the prompt, skill, rule, model, or environment.

Do not define TC-004 until TC-003 has been reviewed.
