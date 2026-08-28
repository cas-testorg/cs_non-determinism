# CoreStory Nondeterminism Evaluation

This repository contains the input artifacts for an automated comparison of two C/C++ nondeterminism investigation strategies.

The repository intentionally contains **test inputs and execution guidance only**. Validation results, prior investigation findings, and expected answers should not be added here, because they could contaminate subsequent automated runs.

## Evaluation Objective

The evaluation compares two investigation strategies against the same overall objective: identify and correctly reason about sources of nondeterminism and related correctness risks in a C/C++ application.

This is **not** intended to isolate CoreStory as the only experimental variable. Test Case 2 intentionally changes the investigation strategy by introducing CoreStory application intelligence, a revised analysis rule, and revised mechanism-oriented prompts.

Results should therefore be compared based on the **quality and validity of the resulting findings**, not simply raw finding counts or one-to-one prompt correspondence.

## Test Case 1 — Baseline

Test Case 1 represents the original investigation workflow.

- Use the original nondeterminism prompts.
- Analyze the local repository without CoreStory application intelligence.
- Do not apply the Test Case 2 analysis rule.

Artifacts are stored under:

```text
test-case-1-baseline/
└── prompts/
```

## Test Case 2 — CoreStory-Assisted

Test Case 2 represents the revised investigation workflow.

- Use CoreStory as application intelligence.
- Apply the v2 C/C++ nondeterminism, concurrency, and undefined-behavior analysis rule.
- Use the revised mechanism-oriented prompts.
- Require evidence-backed causal reasoning rather than elevating suspicious constructs by pattern alone.

Artifacts are stored under:

```text
test-case-2-corestory/
├── rules/
└── prompts/
```

## Comparison Model

The two test cases may contain different numbers of prompts and do not require one-to-one prompt correspondence.

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
├── test-case-2-corestory/
│   ├── rules/
│   └── prompts/
└── docs/
    └── automation-guidance.md
```

## Experimental Integrity

Automated runs should preserve separation between the two test cases.

In particular:

- Do not expose Test Case 1 findings to Test Case 2.
- Do not expose Test Case 2 findings to Test Case 1.
- Do not use prior nondeterminism analysis documents, previous investigation results, validation reports, or expected answers as discovery input.
- Keep the application source revision constant when comparing runs.
- Record the rule and prompt versions used for each run.
- Preserve raw model/tool output so results can be independently validated later.

Additional execution details will be maintained in `docs/automation-guidance.md`.

## Status

This repository is being prepared as the clean input package for automated nondeterminism evaluation. The baseline prompts, v2 rule, revised prompts, and automation guidance will be added as separate version-controlled artifacts.
