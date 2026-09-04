# ND Skill + CoreStory Rule Integration Tests

This working area contains small, repeatable tests for evaluating the customer's nondeterminism skill together with the existing CoreStory code-analysis rule.

The immediate goal is **workflow validation**, not broad defect discovery and not yet a customer benchmark.

## Inputs under test

### Customer skill

`references/SKILL.md`

Current skill metadata identifies it as `prove-nd-mt`, a multi-threaded extension of the customer's base `prove-nd` workflow. It adds concurrency-specific reasoning for data races, race-free order dependence, worker-state carryover, commit-order effects, parallel reductions, gate audits, canonicalization, and related mechanisms.

Important dependency: the skill states that it extends a separate base `prove-nd` skill. That base skill is not assumed to be available unless separately provided.

### CoreStory rule

`archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc`

The rule is always applied and directs the agent to use CoreStory as the primary source of application intelligence, narrow the investigation using application relationships, inspect targeted source for mechanism validation, establish causal evidence, and avoid elevating unsupported candidates.

## Test philosophy

Each test should isolate one nondeterminism mechanism and answer a small number of questions.

We want to observe whether:

1. The customer skill supplies the intended ND-specific reasoning discipline.
2. The CoreStory rule causes application intelligence to be used before broad local repository exploration.
3. CoreStory helps narrow cross-file/cross-component investigation work.
4. Required source validation from the customer skill is preserved.
5. Findings remain evidence-backed rather than speculative.

Do not modify the customer skill or CoreStory rule merely to make an individual test pass. Preserve failures and unexpected behavior as evidence first.

## Controlled test sequence

```text
TC-001  Race-free floating-point accumulation / reduction      PASS
TC-002  Worker-state carryover / boundary reset                PASS
TC-003  Commit-order dependence / first-writer-wins            PASS
TC-004  Gate-inactive / determinism-control propagation        PASS
TC-005  Concurrent container / iteration-order dependence      PASS
```

The five-test set is sufficient to pause automatic expansion and review the pattern with the internal team before defining TC-006.

### TC-001 result

TC-001 validated the combined workflow on race-free, order-dependent floating-point accumulation. Cursor used CoreStory early, narrowed several candidate surfaces, performed targeted local validation, investigated MT reachability and neutralization, and correctly declined to elevate an unsupported candidate. The workflow test was classified **PASS**.

TC-001 also showed that substantial local mechanical search may still occur after CoreStory discovery.

### TC-002 result

TC-002 validated the worker-state carryover / boundary-reset proof discipline. Cursor used CoreStory first, established real worker reuse and dynamic assignment in `ctsMtMgr`, verified that a concrete `fmaxcgSolverImpl` per-thread gradient near-candidate is neutralized after merge, distinguished stack-local/job-local state from pooled-worker state, and declined to manufacture a Real finding when no stale-state-to-observable-result chain could be proven. The workflow test was classified **PASS**.

TC-002 also confirmed the narrowing concern from TC-001: CoreStory generated useful candidate areas, but Cursor still performed substantial broad local lifecycle/reset/per-thread searches.

### TC-003 result

TC-003 validated commit-order / first-writer-wins reasoning and produced the clearest CoreStory narrowing result so far. CoreStory identified a concrete `ctomtGlsParallelBufPlans` / `driverInfo::_winner` relationship path spanning parallel plan evaluation, selection, and downstream handling. Cursor then used targeted local source inspection to prove that the candidate was neutralized: `_winner` is updated post-join, `selectBestPerDriver` performs deterministic arbitration first, and no completion-order reshuffling was established.

The workflow test was classified **PASS**. Unlike TC-001 and TC-002, no broad product-wide local discovery search was observed; local work was predominantly validation of CoreStory-supplied paths.

### TC-004 result

TC-004 validated gate/control propagation reasoning. CoreStory helped surface and narrow a concrete path around `cts.optimize.delay_insertion_enable_mt`, while Cursor verified that the explicit option defaults false but revision-based enablement makes the MT accessor true under the default enhancement revision. The agent traced that control through the live GRE delay-insertion path into multi-threaded execution, then correctly stopped short of a Real ND classification because variable observable behavior was not established and the post-join commit appeared stable.

The workflow test was classified **PASS**. TC-004 reinforces the narrowing improvement from TC-003: CoreStory helped reduce a potentially broad search for flags, locks, and thread gates into targeted validation of a concrete control-to-execution path.

### TC-005 result

TC-005 validated concurrent-container / iteration-order reasoning. CoreStory identified several concrete producer/container candidates, including parallel violated-path collection, concurrent-vector insertion, and MT path aggregation. Cursor verified the downstream behavior of the strongest candidates and found deterministic neutralizers: sort/unique, conversion to ordered sets, or stable job-index aggregation before an order-sensitive observable consumer.

The workflow test was classified **PASS**. CoreStory remained the primary discovery mechanism and most local work was targeted validation. After repeated CoreStory refinement could not establish a complete Real path, Cursor did perform a late broader repository search for `tbb::concurrent_vector` / `concurrent_vector` patterns. This is a small narrowing regression compared with TC-003 and TC-004, but it was an explicit fallback rather than a bypass of the CoreStory-first workflow.

## Cross-test observation

Across all five tests, the combined workflow consistently preserved the customer's proof discipline: multi-threaded reachability, mechanism-specific variability, downstream observable impact, and neutralizers were investigated before any Real classification. No test manufactured a Real finding when the evidence was incomplete.

The CoreStory narrowing result improved over the sequence. TC-001 and TC-002 still involved substantial local mechanical search after CoreStory discovery. TC-003 and TC-004 showed the strongest narrowing, with CoreStory supplying concrete cross-file causal/control paths and local work becoming primarily validation. TC-005 retained that pattern for most of the investigation, with one late broad-search fallback after CoreStory could not close an end-to-end order-sensitive path.

## Per-test structure

Each test directory should contain:

```text
README.md       exact procedure, prompt, controls, and pass criteria
results.md      observed behavior and conclusions
```

Optional evidence can be added later when useful, but avoid committing credentials, customer secrets, or unnecessary customer source.

## Execution discipline

For each test:

1. Record the environment/model and relevant rule/skill state.
2. Start a fresh agent conversation where practical.
3. Use the exact prompt committed in the test case.
4. Do not add steering prompts during the run unless the test explicitly calls for them.
5. Preserve the model response and relevant tool behavior.
6. Record CoreStory interactions separately from local repository operations when possible.
7. Record whether the skill's required proof steps were followed.
8. Classify the test itself as PASS, PARTIAL, FAIL, or INCONCLUSIVE.
9. Do not interpret a workflow test as proof of customer-wide defect coverage.

## Current status

Pause automatic test-suite expansion after TC-005. Review the five-test pattern with the internal team and use feedback, customer priorities, or a clearly identified coverage gap to decide whether TC-006 is warranted before the next customer meeting.
