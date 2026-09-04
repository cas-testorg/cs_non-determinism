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
TC-002  Worker-state carryover / boundary reset                NOT RUN
TC-003  TBD after TC-002 review
```

Only broaden the test suite after reviewing the prior test's transcript and evidence.

### TC-001 result

TC-001 validated the combined workflow on race-free, order-dependent floating-point accumulation. Cursor used CoreStory early, narrowed several candidate surfaces, performed targeted local validation, investigated MT reachability and neutralization, and correctly declined to elevate an unsupported candidate. The workflow test was classified **PASS**.

TC-001 also showed that substantial local mechanical search may still occur after CoreStory discovery. TC-002 therefore adds an explicit narrowing question: can CoreStory establish worker lifecycle, reuse, mutable state, reset boundaries, and downstream relationships well enough to reduce the breadth of subsequent local proof work?

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

## Current test

Proceed with `tc-002-worker-state-carryover/`.
