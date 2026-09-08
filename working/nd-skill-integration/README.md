# ND Skill + CoreStory Rule Integration Tests

This working area contains small, repeatable tests for evaluating the customer's nondeterminism workflow together with the existing CoreStory code-analysis rule.

The immediate goal is **workflow validation**, not yet the customer ground-truth benchmark.

## Inputs under test

### Customer workflow

The customer has now clarified that CTS analysis starts with a broad `nd-code-analyzer` scan for possible nondeterminism patterns, with emphasis on multi-threaded code, and then verifies reported candidates with `prove-nd-mt` using a secondary CLI agent.

`references/SKILL.md` contains the `prove-nd-mt` multi-threaded verification skill currently available in this repository. The customer also identified a separate base `prove-nd` skill and an `nd-code-analyzer` discovery skill as dependencies of the production workflow. Their actual contents must be available before TC-006 can be treated as a faithful workflow reproduction.

### CoreStory rule

`archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc`

The rule is always applied and directs the agent to use CoreStory as the primary source of application intelligence, narrow the investigation using application relationships, inspect targeted source for mechanism validation, establish causal evidence, and avoid elevating unsupported candidates.

## Test philosophy

TC-001 through TC-005 isolated individual MT nondeterminism mechanisms. They primarily validated the `prove-nd-mt` verification discipline together with CoreStory-assisted narrowing.

TC-006 changes the test boundary. It evaluates the customer-described end-to-end CTS workflow:

```text
broad ND pattern discovery
    -> candidate generation
    -> prove-nd-mt verification
    -> final findings
```

We want to observe whether:

1. The customer's discovery skill supplies broad ND candidate generation without us preselecting a mechanism.
2. The customer verification skill preserves the intended ND-specific proof discipline.
3. The CoreStory rule causes application intelligence to contribute during discovery and/or verification.
4. CoreStory helps narrow cross-file/cross-component investigation and reduce rediscovery between phases.
5. Findings remain evidence-backed rather than speculative.

Do not modify the customer skills or CoreStory rule merely to make an individual test pass. Preserve failures and unexpected behavior as evidence first.

## Controlled test sequence

```text
TC-001  Race-free floating-point accumulation / reduction      PASS
TC-002  Worker-state carryover / boundary reset                PASS
TC-003  Commit-order dependence / first-writer-wins            PASS
TC-004  Gate-inactive / determinism-control propagation        PASS
TC-005  Concurrent container / iteration-order dependence      PASS
TC-006  Customer CTS discovery + verification workflow         NOT RUN
```

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

Across TC-001 through TC-005, the combined workflow consistently preserved the customer's verification discipline: multi-threaded reachability, mechanism-specific variability, downstream observable impact, and neutralizers were investigated before any Real classification. No test manufactured a Real finding when the evidence was incomplete.

The CoreStory narrowing result improved over the sequence. TC-001 and TC-002 still involved substantial local mechanical search after CoreStory discovery. TC-003 and TC-004 showed the strongest narrowing, with CoreStory supplying concrete cross-file causal/control paths and local work becoming primarily validation. TC-005 retained that pattern for most of the investigation, with one late broad-search fallback after CoreStory could not close an end-to-end order-sensitive path.

The customer has since clarified that these mechanism-specific tests exercise only part of the intended CTS workflow. The next meaningful test is therefore not another synthetic ND mechanism. TC-006 evaluates the actual discovery -> verification orchestration described by the customer.

## Relationship to customer benchmark

TC-006 is still workflow validation. It should not be interpreted as Coverity recall/precision benchmarking.

The planned ground-truth comparison remains dependent on the Coverity findings Scott said he would provide, including the initial categories discussed with the customer: `POINTER_NONDETERMINISM`, `UNINIT`, and `UNINIT_CTOR`.

The customer also clarified that their ND methodology is primarily static code scanning followed by analysis of whether a reported issue represents real ND risk. Runtime reproduction is often difficult and is not required as the basis for every finding.

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
7. Record whether the customer workflow's required proof steps were followed.
8. Classify the test itself as PASS, PARTIAL, FAIL, or INCONCLUSIVE.
9. Do not interpret a workflow test as proof of customer-wide defect coverage.

## Current test

Proceed with `tc-006-customer-workflow/` only after checking its pre-run dependency gate. In particular, do not silently substitute for a missing `nd-code-analyzer` skill and then describe the run as reproduction of the customer workflow.
