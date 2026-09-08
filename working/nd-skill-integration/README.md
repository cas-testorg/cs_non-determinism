# ND Skill + CoreStory Rule Integration Tests

This working area contains small, repeatable tests for evaluating the customer's nondeterminism workflow together with the existing CoreStory code-analysis rule.

The immediate goal is **workflow validation**, not yet the customer ground-truth benchmark.

## Inputs under test

### Customer workflow

The customer clarified that CTS analysis starts with `nd-code-analyzer` scanning for possible nondeterminism patterns, with emphasis on multi-threaded code, and then verifies reported candidates with `prove-nd-mt` through a separate CLI-agent workflow.

The known customer skills are preserved under:

```text
working/nd-skill-integration/skills/
├── nd-code-analyzer/
├── prove-nd/
└── non-determinism/   # prove-nd-mt
```

`nd-code-analyzer` includes a mandated mechanical scan/pattern catalog followed by triage, deep read, downstream-observability analysis, neutralizer detection, and real/non-real classification. The base `prove-nd` skill performs proof/dismissal work, while `prove-nd-mt` adds concurrency-specific reachability, race-vs-ordering, gate, reset, and canonicalization reasoning.

The customer also uses a custom Linux `create-cli-agent` process built around `cursor-agent`. It accepts a prompt and model, launches verification in a clean agent context, and writes a clean result document.

### CoreStory rule

`archive/legacy-static-evaluation/test-case-2-corestory/rules/code-analysis-v2.mdc`

The rule directs the agent to use CoreStory application intelligence to narrow investigation, trace relationships, inspect targeted source, establish causal evidence, and avoid elevating unsupported candidates.

For TC-006, CoreStory must **coexist with rather than replace** the discovery skill's mandated mechanical scan. Its expected contribution is application context, reachability, cross-file relationships, shared state, downstream consumers, controls, neutralizers, and candidate qualification.

## Test philosophy

TC-001 through TC-005 isolated individual MT nondeterminism mechanisms. They primarily validated the `prove-nd-mt` verification discipline together with CoreStory-assisted narrowing.

TC-006 changes the test boundary:

```text
nd-code-analyzer discovery
    -> candidate/result artifact
    -> isolated prove-nd / prove-nd-mt verification
    -> final findings
```

Because the current environment may not reproduce the customer's Linux `create-cli-agent`, `cursor-agent`, or exact models, TC-006 is defined as a **controlled workflow emulation** when necessary. The critical property to preserve is a clean verification context: discovery occurs in one conversation, then verification occurs in a separate clean conversation using only the handoff artifact.

We want to observe whether:

1. The discovery skill produces useful MT candidates without us preselecting a mechanism.
2. The verification skills preserve their intended proof discipline.
3. CoreStory can coexist with the mechanical scanner and add useful application intelligence.
4. The discovery artifact provides enough context for isolated verification without unnecessary rediscovery.
5. Findings remain evidence-backed rather than speculative.
6. Infrastructure/model substitutions are clearly separated from CoreStory effects.

Do not modify the customer skills or CoreStory rule merely to make an individual test pass.

## Controlled test sequence

```text
TC-001  Race-free floating-point accumulation / reduction      PASS
TC-002  Worker-state carryover / boundary reset                PASS
TC-003  Commit-order dependence / first-writer-wins            PASS
TC-004  Gate-inactive / determinism-control propagation        PASS
TC-005  Concurrent container / iteration-order dependence      PASS
TC-006  Customer CTS discovery + isolated verification         NOT RUN
```

## Results so far

TC-001 and TC-002 validated the customer's verification discipline but still involved substantial local mechanical searching after CoreStory discovery.

TC-003 and TC-004 showed the strongest narrowing: CoreStory supplied concrete cross-file causal/control paths and local work became primarily targeted validation.

TC-005 retained that pattern for most of the investigation, with one late broad-search fallback after CoreStory could not close an end-to-end order-sensitive path.

Across TC-001 through TC-005, the combined workflow consistently preserved MT reachability, mechanism-specific variability, downstream observable impact, and neutralizer analysis before any Real classification. No test manufactured a Real finding when evidence was incomplete.

The customer has since clarified that these mechanism-specific tests exercise only part of the intended CTS workflow. TC-006 therefore tests the actual discovery -> isolated verification shape rather than another synthetic ND mechanism.

## Relationship to customer benchmark

TC-006 is still workflow validation and should not be interpreted as Coverity recall/precision benchmarking.

The planned ground-truth comparison remains dependent on the Coverity findings Scott said he would provide, including `POINTER_NONDETERMINISM`, `UNINIT`, and `UNINIT_CTOR`.

The customer also clarified that their ND methodology is primarily static code scanning followed by analysis of whether a reported issue represents real ND risk. Runtime reproduction is often difficult and is not required for every finding.

## Per-test structure

Each test directory should contain:

```text
README.md       exact procedure, prompt, controls, and pass criteria
results.md      observed behavior and conclusions
```

## Execution discipline

1. Record environment/model/rule/skill state.
2. Preserve exact customer skill behavior rather than suppressing mandated scans or proof steps.
3. Keep CoreStory integration additive to the customer workflow.
4. Preserve model/orchestration deviations explicitly.
5. Preserve discovery and verification artifacts separately for TC-006.
6. Record CoreStory interactions separately from local repository operations when possible.
7. Classify each test as PASS, PARTIAL, FAIL, or INCONCLUSIVE.
8. Do not interpret workflow tests as proof of customer-wide defect coverage.

## Current test

Proceed with `tc-006-customer-workflow/` using its two-phase procedure. If the customer Linux orchestration cannot be reproduced, use the documented clean-context emulation rather than attempting to rebuild `create-cli-agent` as part of this test.
