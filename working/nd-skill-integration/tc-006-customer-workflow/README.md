# TC-006 — Customer ND Pattern Catalog + CoreStory Discovery/Verification

## Purpose

Evaluate whether the customer's nondeterminism knowledge can be combined with CoreStory application intelligence to discover and verify multi-threaded ND candidates in CTS, without requiring an exact reproduction of the customer's Linux scanner/orchestration/report-generation infrastructure.

TC-001 through TC-005 started from a preselected ND mechanism and primarily exercised `prove-nd-mt` verification. TC-006 starts from the customer's own ND pattern catalog and asks the agent to discover candidates before verifying them.

The test is therefore:

```text
customer ND pattern catalog
    -> CoreStory-assisted semantic discovery / triage
    -> candidate artifact
    -> clean verifier context
    -> prove-nd + prove-nd-mt + CoreStory
    -> verified findings
```

This is a **controlled workflow emulation**, not an exact reproduction of the customer's Linux tooling. It is also not yet the Coverity ground-truth benchmark.

## Customer knowledge available

The customer-supplied material preserved under `working/nd-skill-integration/skills/` now includes:

```text
nd-code-analyzer/SKILL.md
prove-nd/SKILL.md
non-determinism/SKILL.md        # prove-nd-mt
references/nd-patterns.yaml     # scanner source of truth
references/nd-patterns.md       # narrative/LLM mirror
```

`nd-patterns.md` states that the YAML is the source of truth for the scanner and the Markdown mirror is intended for LLM triage to understand pattern intent, severity, and fixes.

The catalog distinguishes:

- **Tier 1** patterns: regex-detectable, where the match itself is expected to be a relatively high-quality candidate.
- **Tier 2** patterns: regex is only a seed; surrounding code and application semantics must be analyzed before classifying the candidate.

For this test, the catalog is the customer knowledge basis. We are not attempting to recreate report-generation plumbing or every helper script.

## MT-focused catalog scope

The customer specifically asked for a scan of multi-threaded code. TC-006 therefore prioritizes the catalog patterns that require MT/concurrency reasoning rather than running an unrestricted test of every general ND category.

### Parallel / Tier-2 patterns

The catalog includes:

- **3.1 — Parallel floating-point reduction**
- **3.2 — Multi-threaded shared container writes**
- **3.5 — Thread-count dependency in algorithm sizing**
- **3.6 — Post-collection use without canonical ordering** when the collection source is parallel/unstable
- **3.7 — Project wrapper containers with order-sensitive use** when insertion/consumption is affected by MT execution

### Concurrency / MT-ND patterns

The catalog also includes six explicitly MT-oriented Tier-2 classes:

- **4.1 — Lazy dirty-bit recompute inside a const getter**
- **4.2 — First-touch materialization / inconsistent lazy-cache lock**
- **4.3 — Mutable non-atomic counter RMW on a const path**
- **4.4 — `concurrent_hash_map` accessor check-then-act**
- **4.5 — Condition-variable lost-wakeup shape**
- **4.6 — Address-keyed lock striping anti-pattern**

These are static source patterns. A pattern match is not automatically a Real ND finding. Reachability, MT execution, downstream observability, controls, and neutralizers must still be established using the customer proof methodology.

## Experimental question

The primary question is:

> Given the customer's ND pattern knowledge, can CoreStory application intelligence help the agent move from broad static pattern candidates to application-specific, evidence-backed ND candidates and then support isolated `prove-nd-mt` verification?

We are deliberately separating **customer ND knowledge** from **customer implementation plumbing**.

The test does not require:

- the original `scan_nd.py` implementation,
- report-generation scripts,
- the Linux-only `create-cli-agent` wrapper,
- `cursor-agent`, or
- exact customer model availability.

Those differences must be recorded as workflow deviations, but they do not prevent evaluation of the CoreStory integration hypothesis.

## CoreStory role

CoreStory does **not** replace the customer pattern catalog.

The catalog supplies the defect hypotheses and triage questions. CoreStory should be used where application intelligence can answer questions such as:

- Where does this construct participate in actual parallel execution?
- What dispatch/thread-pool/TBB path reaches it?
- Is the state shared, worker-local, object-local, or effectively thread-confined?
- What callers and downstream consumers observe the value/order/state?
- Does a candidate reach QoR, design mutation, output, ranking, selection, or another observable result?
- Are there stable sorts, canonicalizers, resets, gates, locks, atomics, post-join recomputations, or other neutralizers?
- Are there sibling implementations that establish the intended locking/canonicalization discipline?
- Does a configuration/control actually propagate to the execution path?

Local source inspection remains the mechanism-validation step.

## Required inputs / pre-run gate

Record before execution:

```text
CTS source path known:                                YES 
CTS source revision known:                            NO
CoreStory project corresponding to CTS source known:  YES
nd-code-analyzer skill available:                     YES
prove-nd skill available:                             YES
prove-nd-mt skill available:                          YES
references/nd-patterns.md available:                  YES
references/nd-patterns.yaml available:                YES
CoreStory rule installed/active:                      YES
CoreStory MCP available:                              YES
requested discovery model available:                  NO
requested verification model available:               NO
create-cli-agent available:                           NO
```

Missing exact models or `create-cli-agent` does not block this test. Missing the customer pattern catalog, proof skills, CTS source, or CoreStory access does.

## Execution controls

1. Preserve prior Cursor sessions/artifacts.
2. Do not expose TC-001 through TC-005 candidate locations/findings.
3. Do not provide Coverity findings or hidden ground truth.
4. Do not preselect a single candidate or source file.
5. Use the customer pattern catalog as the discovery basis.
6. Keep the CoreStory code-analysis rule active.
7. Preserve all candidate classifications, including dismissed and unresolved candidates.
8. Do not promote a pattern match to Real without semantic proof.
9. Record model/tool/orchestration deviations.
10. Token metering is out of scope.

# TC-006A — Pattern-guided discovery

## Goal

Discover plausible MT ND candidates in CTS using the customer's pattern catalog as the defect knowledge base and CoreStory as application intelligence.

This phase intentionally does **not** require the original scanner implementation. The objective is not to compare regex engines. It is to determine whether the same customer-defined ND hypotheses can drive useful CoreStory-assisted semantic discovery.

## Discovery prompt

Replace `<CTS_PATH>` with the actual CTS source path. Adjust only the skill paths if required by the local test environment.

```text
Investigate the CTS module located at <CTS_PATH> for possible multi-threaded nondeterminism issues.

Use the customer nd-code-analyzer skill and the customer ND Pattern Catalog in references/nd-patterns.md and references/nd-patterns.yaml as the discovery methodology.

Focus on the catalog's multi-threaded and concurrency-relevant Tier-2 patterns, including parallel floating-point reduction, shared-container writes, thread-count-dependent behavior, unstable post-collection ordering, MT-sensitive wrapper-container use, lazy mutable state in const getters, first-touch materialization or inconsistent lazy-cache locking, mutable non-atomic counters on const paths, concurrent-container compound operations, condition-variable lost-wakeup shapes, and address-keyed lock striping.

Follow the CoreStory code-analysis rule. Use CoreStory application intelligence to identify likely execution paths, parallel dispatch, shared state, callers, downstream consumers, controls, sibling implementations, and possible neutralizers. Use targeted local source inspection to validate the actual code mechanism.

A pattern match is only a candidate. Do not classify candidates as Real during this discovery phase unless the discovery skill itself requires a preliminary classification. Preserve missing evidence and neutralizers.

Produce a concise candidate artifact for a separate clean verification step. For each candidate include:
- pattern/catalog ID and mechanism,
- file/function/symbol,
- why it matched the customer pattern,
- evidence of possible MT reachability,
- shared or mutable state involved,
- known downstream consumer/observable effect, if established,
- known control/neutralizer, if established,
- missing evidence,
- CoreStory relationships that should be validated by the verifier.

Do not perform the final prove-nd-mt verification yet.
```

## Discovery behavior to observe

Capture:

- which catalog patterns the agent actually considered,
- which patterns generated concrete candidates,
- whether CoreStory was used to identify candidate locations or primarily to qualify candidates found locally,
- CoreStory queries/interactions,
- broad local pattern searches,
- targeted local source reads,
- candidate count before semantic triage when observable,
- candidate count handed to verification,
- candidates dismissed during discovery and why,
- whether the agent uses the catalog's Tier-1/Tier-2 distinction correctly,
- whether syntax-only candidates are kept separate from semantically supported candidates.

## TC-006A success criteria

TC-006A is successful when:

- the customer catalog materially drives discovery,
- multiple relevant MT/concurrency pattern classes are considered rather than a single mechanism being preselected,
- CoreStory contributes application context to candidate discovery or qualification,
- local source inspection validates constructs rather than replacing semantic reasoning with grep alone,
- obvious neutralizers/non-MT paths are recognized,
- unsupported candidates are not silently elevated, and
- a concrete candidate artifact suitable for clean verification is produced.

# TC-006B — Clean verification

## Goal

Verify the TC-006A candidate artifact using the customer's proof methodology in a context isolated from the discovery conversation.

The customer's production workflow uses `create-cli-agent` with GPT-5.5-xtra-high. If that infrastructure is unavailable, emulate its most important experimental property: **a clean verifier context**.

## Clean-context handoff

1. Preserve the exact TC-006A candidate artifact.
2. Start a new clean Cursor conversation.
3. Provide the verifier only:
   - the candidate artifact,
   - access to CTS source,
   - `prove-nd`,
   - `prove-nd-mt`,
   - the CoreStory rule/MCP.
4. Do not provide the TC-006A conversation transcript.
5. Do not add prior synthetic-test findings or hidden ground truth.
6. Record the actual verification model.

## Verification prompt

```text
Verify whether the reported multi-threaded nondeterminism candidates in the supplied discovery artifact are real.

Use the customer base prove-nd skill and the prove-nd-mt extension. Follow the CoreStory code-analysis rule throughout verification.

For each candidate, establish or explicitly fail to establish:
1. actual MT reachability and the parallel dispatch/worker path,
2. the precise race or race-free ordering mechanism,
3. the shared/mutable state and relevant access path,
4. how equivalent runs can vary,
5. the downstream C++ consumer and observable consequence,
6. applicable gates, locks, resets, canonicalizers, stable ordering, or other neutralizers, and
7. the final customer classification with missing evidence stated explicitly.

Use CoreStory to resolve application relationships and targeted local source inspection to validate the code mechanism. Do not call a candidate Real from the pattern match alone.

Return the strongest supported findings and preserve dismissed, neutralized, latent, dead/unreachable, false-positive, and unresolved classifications where applicable.
```

## Verification behavior to observe

Capture:

- MT reachability proof,
- race vs race-free ordering reasoning,
- accessor/reset/gate/canonicalizer sweeps required by `prove-nd-mt`,
- downstream observable sink proof,
- CoreStory relationships used,
- targeted local validation,
- how much discovery context the verifier must rediscover,
- final classifications,
- missing evidence,
- unsupported findings avoided.

# Combined evaluation

## Primary questions

1. Can the customer's pattern catalog serve as the ND knowledge layer without requiring us to reproduce the original scanner implementation?
2. Does CoreStory help transform broad pattern hypotheses into application-specific candidate paths?
3. Which catalog classes benefit most from application intelligence versus mechanical source search?
4. Does CoreStory help establish MT reachability, downstream observability, sibling locking patterns, controls, or neutralizers that are difficult to infer from a local pattern match?
5. Is the TC-006A artifact sufficient for a clean verifier, or does TC-006B repeat substantial discovery?
6. Does `prove-nd-mt` preserve its proof discipline when candidates originate from broad catalog-guided discovery?
7. Are any differences likely caused by model/orchestration substitutions rather than CoreStory integration?

## PASS

Classify TC-006 **PASS** when:

- the customer pattern catalog drives meaningful MT/concurrency discovery,
- CoreStory contributes useful application intelligence during discovery and/or verification,
- discovery produces a concrete clean-handoff artifact,
- verification is context-isolated,
- `prove-nd` / `prove-nd-mt` proof discipline is preserved,
- downstream consequence and neutralizers are investigated before Real classification,
- unsupported candidates are not promoted to Real, and
- workflow/model deviations are recorded.

A Real ND finding is not required for workflow PASS.

## PARTIAL

Examples:

- the catalog drives discovery but CoreStory contributes little,
- CoreStory is useful but only after substantial broad local discovery,
- clean verification requires major rediscovery,
- important proof steps are skipped,
- model/tool substitutions materially limit interpretation while still producing useful evidence.

## FAIL

Examples:

- the customer pattern catalog is effectively ignored,
- suspicious syntax is promoted to Real without semantic proof,
- CoreStory is available but the rule is ignored,
- verification relies on hidden discovery context rather than the handoff artifact,
- substitutions are hidden and the run is represented as exact customer-workflow reproduction.

## INCONCLUSIVE

Use when missing CTS source, pattern references, proof skills, CoreStory connectivity, or severe tooling limitations prevent meaningful discovery/verification.

# Relationship to customer benchmark

TC-006 tests workflow compatibility and the usefulness of CoreStory when applying the customer's ND knowledge. It does not establish recall/precision against Coverity.

When the Coverity findings for `POINTER_NONDETERMINISM`, `UNINIT`, and `UNINIT_CTOR` become available, use them as ground truth in a separate benchmark phase rather than exposing them during TC-006.

# Stop condition

Run TC-006A once. Review and preserve its candidate artifact before starting TC-006B. Run TC-006B once in a clean context. Review the combined evidence before adding further synthetic tests.
