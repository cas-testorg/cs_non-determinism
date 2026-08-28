# CoreStory Nondeterminism Evaluation

This repository contains the input artifacts for an automated comparison of two C/C++ nondeterminism investigation strategies.

The repository intentionally contains **test inputs and execution guidance only**. Validation results, prior investigation findings, and expected answers should not be added here, because they could contaminate subsequent automated runs.

## Evaluation Objective

The evaluation compares two investigation strategies against the same overall objective: identify and correctly reason about sources of nondeterminism and related correctness risks in a C/C++ application.

This is **not** intended to isolate CoreStory as the only experimental variable. Test Case 2 intentionally changes the investigation strategy by introducing CoreStory application intelligence, a revised analysis rule, and revised mechanism-oriented prompts.

Results should therefore be compared based on the **quality and validity of the resulting findings**, not simply raw finding counts or one-to-one prompt correspondence.

## Test Case 1 — Baseline

Test Case 1 represents the original investigation workflow.

- Use the original 14 nondeterminism prompts.
- Analyze the local repository without CoreStory application intelligence.
- Do not apply the Test Case 2 analysis rule.

Artifacts are stored under:

```text
test-case-1-baseline/
└── prompts/
    ├── 01-uninitialized-variables.md
    ├── ...
    └── 14-third-party-library-nondeterminism.md
```

## Test Case 2 — CoreStory-Assisted

Test Case 2 represents the revised investigation workflow.

- Use CoreStory as application intelligence.
- Apply the v2 C/C++ nondeterminism, concurrency, and undefined-behavior analysis rule.
- Use the 10 revised mechanism-oriented prompts.
- Require evidence-backed causal reasoning rather than elevating suspicious constructs by pattern alone.
- Treat each concrete exemplar as an example of the mechanism, not as a known defect or expected finding.

The 10 Test Case 2 mechanisms are:

1. Uninitialized and indeterminate state
2. Shared-state concurrency and non-thread-safe access
3. Object lifetime and use-after-free
4. Pointer-dependent ordering
5. Unstable iteration and traversal
6. Floating-point, FMA, and numerical order sensitivity
7. Runtime-derived variability
8. Schedule-dependent and heuristic result selection
9. Platform, compiler, and build variability
10. External-library and dependency variability

Requested Coverity and ThreadSanitizer defect classes are mapped directly into the applicable mechanism prompts rather than implemented as a second prompt suite. In particular:

- Coverity `UNINIT` and `UNINIT_CTOR` are handled by P01.
- ThreadSanitizer `DATA RACE`, `THREAD LEAK`, and `UNLOCK OF AN UNLOCKED MUTEX` are handled by P02.
- ThreadSanitizer `HEAP USE AFTER FREE` is handled by P03.
- Coverity `POINTER_NONDETERMINISM` is handled by P04.

The defect-class names are investigation patterns, not expected findings. A candidate must still establish the source mechanism, active defect condition where applicable, and any nondeterministic manifestation independently.

Artifacts are stored under:

```text
test-case-2-corestory/
├── rules/
│   └── code-analysis-v2.mdc
└── prompts/
    ├── 01-uninitialized-indeterminate-state.md
    ├── 02-shared-state-concurrency.md
    ├── 03-object-lifetime-use-after-free.md
    ├── 04-pointer-dependent-ordering.md
    ├── 05-unstable-iteration-traversal.md
    ├── 06-floating-point-fma-numerical-order.md
    ├── 07-runtime-derived-variability.md
    ├── 08-schedule-dependent-heuristic-results.md
    ├── 09-platform-compiler-build-variability.md
    └── 10-external-library-dependency-variability.md
```

## Operational Inputs

The analysis should depend only on inputs that are explicitly applied during execution:

1. `test-case-2-corestory/rules/code-analysis-v2.mdc`
2. the applicable prompt under `test-case-2-corestory/prompts/`
3. current CoreStory application intelligence
4. targeted source inspection

Documentation under `docs/` is for automation authors and reviewers. It must not be treated as an implicit model-context dependency unless the automation explicitly chooses to read it.

`docs/defect-class-mapping.md` documents how the requested Coverity and ThreadSanitizer classes map into the 10-prompt mechanism model.

## Comparison Model

The two test cases intentionally contain different numbers and organizations of prompts and do not require one-to-one prompt correspondence.

Test Case 1 is organized primarily around the original customer-derived technology or symptom categories. Test Case 2 reorganizes the investigation around causal mechanisms. Coverage should therefore be compared by mechanism and validated finding quality rather than prompt number.

The comparison should evaluate the resulting candidate findings using a common validation and scoring process. At minimum, the comparison should distinguish:

- source-grounded findings from unsupported candidates;
- nondeterminism from other correctness risks;
- undefined behavior from nondeterministic manifestation;
- schedule- or order-sensitive execution from a schedule-dependent application result;
- mitigated or correctly guarded patterns from active risks;
- findings that require runtime or additional external evidence.

Raw candidate count alone is not a measure of investigation quality.

## Repository Structure

```text
.
├── README.md
├── test-case-1-baseline/
│   └── prompts/
│       └── 14 baseline prompts
├── test-case-2-corestory/
│   ├── rules/
│   │   └── code-analysis-v2.mdc
│   └── prompts/
│       └── 10 mechanism-oriented prompts
└── docs/
    ├── automation-guidance.md
    └── defect-class-mapping.md
```

## Experimental Integrity

Automated runs should preserve separation between the two test cases.

In particular:

- Do not expose Test Case 1 findings to Test Case 2.
- Do not expose Test Case 2 findings to Test Case 1.
- Do not use prior nondeterminism analysis documents, previous investigation results, validation reports, or expected answers as discovery input.
- Concrete exemplars in Test Case 2 are pattern-teaching inputs only and must not be treated as known defects or expected findings.
- Search for semantically equivalent mechanisms across the application rather than merely rediscovering the exemplar location.
- Keep the application source revision constant when comparing runs.
- Record the rule and prompt versions used for each run.
- Preserve raw model/tool output so results can be independently validated later.

Additional execution details can be maintained in `docs/automation-guidance.md`.

## Status

The clean input package now contains the complete 14-prompt baseline set, the v2 CoreStory-assisted analysis rule, the complete 10-prompt mechanism-oriented Test Case 2 set, and explicit Coverity/ThreadSanitizer defect-class coverage.
