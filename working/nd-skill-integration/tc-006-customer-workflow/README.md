# TC-006 — Customer CTS ND Discovery + Verification Workflow

## Purpose

Evaluate the customer-described CTS nondeterminism workflow end to end rather than testing another preselected ND mechanism.

The customer described the workflow as a single top-level request that:

1. uses `nd-code-analyzer` to scan CTS for possible nondeterminism patterns, with emphasis on multi-threaded code, and
2. verifies reported candidates with `prove-nd-mt` using a secondary CLI agent.

TC-001 through TC-005 primarily exercised the verification/proof side of this workflow using mechanism-specific prompts. TC-006 shifts the test boundary to broad discovery -> candidate generation -> verification -> final findings.

This remains workflow validation. It is not yet the Coverity ground-truth benchmark because the customer Coverity findings have not yet been provided.

## Customer-provided workflow

Representative customer prompt:

```text
using /u/ranjithp/.claude/skills/nd-code-analyzer/SKILL.md, find out possible non determinism issues from CTS module located here : <path>

Specifically do a scan for finding out ND issues from multi-threaded code.

Verify if the reported issues are real with /prove-nd-mt using a /create-cli-agent with GPT-5.5-xtra-high
```

Customer model guidance:

- discovery: Opus 4.8 xhigh or Opus 5 high
- verification: GPT-5.5-xtra-high via `/create-cli-agent`

Record any model/tooling deviation in the results. A deviation does not automatically fail the workflow test, but it means the run must not be represented as an exact reproduction of the customer's production workflow.

## Required inputs / pre-run gate

Before running TC-006, record whether each input is actually available:

```text
CTS source path/revision known:                         YES / NO
CoreStory project corresponding to CTS source known:   YES / NO
nd-code-analyzer skill available:                      YES / NO
prove-nd-mt skill available:                           YES / NO
base prove-nd skill available:                         YES / NO
/create-cli-agent available:                           YES / NO
requested discovery model available:                   YES / NO
GPT-5.5-xtra-high verification model available:        YES / NO
CoreStory rule installed/active:                       YES / NO
CoreStory MCP available:                               YES / NO
```

### Stop condition before execution

Do not silently substitute for a missing customer skill.

If `nd-code-analyzer` is not available, **do not run TC-006 as if it reproduced the customer workflow**. Record the missing dependency and obtain the skill first.

If the base `prove-nd` skill is unavailable, record that explicitly because `prove-nd-mt` identifies it as a dependency.

If `/create-cli-agent` or the requested models are unavailable, the test may proceed only as a documented workflow approximation after the missing dependency/model is recorded.

## CoreStory integration under test

Keep the existing CoreStory code-analysis rule active.

The key question is not whether CoreStory replaces `nd-code-analyzer` or `prove-nd-mt`. It is whether application intelligence can support the customer's existing discovery-and-verification workflow by providing application relationships, execution context, call/data paths, shared-state relationships, downstream consumers, and neutralizers while preserving the customer's ND methodology.

Do not modify the customer skills merely to make CoreStory appear more useful.

## Execution controls

1. Preserve prior Cursor sessions/artifacts.
2. Start a fresh Cursor chat.
3. Record Cursor version and selected model.
4. Confirm the customer skills actually available in that environment.
5. Confirm the CoreStory rule and MCP are active.
6. Use the customer prompt shape without adding mechanism-specific hints or known candidate locations.
7. Do not provide prior TC-001 through TC-005 candidate locations/findings to the agent.
8. Do not provide Coverity findings or other hidden ground truth during this workflow-validation run.
9. Do not steer after the initial prompt unless a tooling failure requires recovery; record any intervention.
10. Preserve the complete Cursor transcript and final response.

## Prompt

Replace only `<CTS_PATH>` with the actual CTS source path.

```text
Using /u/ranjithp/.claude/skills/nd-code-analyzer/SKILL.md, find possible nondeterminism issues from the CTS module located here: <CTS_PATH>

Specifically, scan for nondeterminism issues in multi-threaded code.

Verify whether the reported issues are real with /prove-nd-mt using a /create-cli-agent with GPT-5.5-xtra-high.

Follow the CoreStory code-analysis rule throughout the investigation.
```

The final sentence is the deliberate experimental addition. The remainder preserves the customer-provided prompt shape.

## What to capture

### Discovery phase

Record:

- whether `nd-code-analyzer` activated/read successfully
- ND pattern categories it searched
- CoreStory interactions during candidate discovery
- local repository searches during discovery
- number/list of candidates produced for verification
- files/symbols associated with each candidate
- whether discovery was broad mechanical scanning, CoreStory-assisted narrowing, or both

### Discovery -> verification handoff

For every candidate sent to verification, capture:

```text
Candidate ID/name:
Mechanism/category:
File/symbol/location:
Evidence passed from discovery:
Question/instruction passed to verifier:
Verifier model/agent actually used:
```

Determine whether the handoff preserves the evidence needed by `prove-nd-mt` or causes the verifier to rediscover substantial application context.

### Verification phase

For each candidate, record:

- MT reachability evidence
- source of run-to-run variability
- race vs race-free ordering distinction where relevant
- shared state / worker state / ordering mechanism
- downstream consumer / observable consequence
- neutralizers/canonicalization/reset/gates investigated
- final classification
- missing evidence
- CoreStory interactions
- local source validation

### Final response

Capture:

- candidates reported as Real
- candidates dismissed/neutralized
- unresolved candidates
- evidence quality
- whether unsupported candidates were elevated

## Primary evaluation questions

1. Does the customer's `nd-code-analyzer` successfully drive broad MT ND discovery without us preselecting a mechanism?
2. Does CoreStory participate early enough to provide application-level context or narrow candidate investigation?
3. Does discovery hand candidates to `prove-nd-mt` with useful evidence, or does verification have to rediscover the same context?
4. Does `prove-nd-mt` preserve its proof discipline when invoked by the customer's actual orchestration rather than by our mechanism-specific prompts?
5. Are candidates traced through a plausible causal chain to downstream behavior rather than reported from suspicious syntax alone?
6. Are neutralized, unreachable, or unsupported candidates rejected appropriately?
7. Where does broad local mechanical searching still occur, and why?

## Pass criteria

Classify TC-006 **PASS** when the available customer workflow can be executed meaningfully and:

- `nd-code-analyzer` performs candidate discovery rather than relying on a preselected mechanism from us,
- the CoreStory rule is followed and application intelligence contributes to discovery and/or verification,
- candidate handoff into `prove-nd-mt` is observable,
- verification preserves the customer's MT proof discipline,
- downstream consequence and neutralizers are investigated before Real classification,
- unsupported findings are not promoted to Real, and
- any broad local search or workflow/model deviation is recorded rather than hidden.

A Real ND finding is **not required** for workflow PASS.

## Partial / fail / inconclusive guidance

### PARTIAL

Examples:

- customer discovery runs, but CoreStory is mostly bypassed,
- verification occurs but does not preserve important `prove-nd-mt` proof steps,
- orchestration works only after substantial manual intervention,
- model/tool substitutions materially change the workflow but still permit useful evaluation.

### FAIL

Examples:

- CoreStory rule is ignored despite being available,
- suspicious code patterns are promoted to Real without verification,
- `prove-nd-mt` is nominally invoked but its required causal/neutralizer analysis is not performed,
- known missing dependencies are silently replaced and the result is presented as the customer workflow.

### INCONCLUSIVE

Use when tooling or missing customer dependencies prevent meaningful execution, especially if `nd-code-analyzer` itself is unavailable.

## Relationship to the customer benchmarks

TC-006 validates reproduction of the customer's CTS workflow. It does **not** establish defect recall or precision against Coverity.

When Scott provides the Coverity findings for `POINTER_NONDETERMINISM`, `UNINIT`, and `UNINIT_CTOR`, use those as ground truth in a separate benchmark phase rather than contaminating this workflow-validation run.

## Stop condition

Run TC-006 once, preserve the evidence, and review it before defining any additional synthetic test.
