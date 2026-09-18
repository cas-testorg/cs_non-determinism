# Test 1 — Iteration 2 Staged Experiment

## Purpose

Test 1 showed that the current end-to-end A/B mixes at least two different questions:

1. Can the workflow discover non-determinism candidates?
2. Can the workflow determine whether a discovered candidate is relevant in the production application?

Iteration 2 separates those questions.

The experiment preserves the customer's existing high-recall discovery workflow, freezes the discovered candidate set, and then evaluates CoreStory as an application-qualification layer.

This is an experimental design, not a claim that qualification is CoreStory's final role.

---

## Hypotheses

### H1 — Discovery

The existing Synopsys ND workflow remains the primary broad candidate-discovery mechanism.

CoreStory may be used during discovery to **expand** a candidate by finding related implementations, callers, accessors, or propagation paths, but CoreStory application qualification must not eliminate a discovered candidate during this stage.

### H2 — Qualification

Given the same frozen candidate, CoreStory application context can improve qualification by supplying evidence about:

- production build inclusion;
- production reachability;
- runtime/configuration gates;
- callers and implementations;
- propagation;
- neutralization;
- observable consequences.

### H3 — SME efficiency

A structured qualification package can reduce the evidence an SME must independently reconstruct before reaching a disposition.

---

## Experimental boundary

This test deliberately separates **discovery** from **qualification**.

A candidate discovered in Stage 1 cannot disappear because build, reachability, propagation, or application significance could not yet be established.

The candidate list is frozen before qualification begins.

No qualification result may retroactively change the discovery count.

---

# Stage 0 — Freeze execution configuration

Record before execution:

- source snapshot / commit;
- CTS workspace;
- Cursor version;
- model used by discovery;
- model used by prove-ND;
- thinking effort;
- enabled rules;
- enabled skills;
- subagent policy;
- CoreStory project ID;
- CoreStory workspace name;
- MCP authentication mode;
- date/time of run.

CoreStory scope for this experiment:

- Project ID: **10**
- Workspace: **cts-code**
- Do not use **cts-code2** or another CoreStory project as evidence.

Any configuration change during execution must be recorded.

---

# Stage 1 — High-recall discovery

## Objective

Find plausible ND candidates without attempting to prove complete production significance.

## Workflow

Use the customer's existing ND discovery skill:

- `nd-code-analyzer`

Use the customer-provided discovery taxonomy and mechanism detection.

Do **not** apply the full CoreStory v3 qualification gate during candidate elimination.

## CoreStory behavior during discovery

CoreStory may be used only to **expand or enrich discovery**, for example:

- identify callers of a suspicious helper;
- resolve wrappers/accessors;
- identify implementations;
- find related production modules;
- identify potential downstream consumers;
- expose additional paths worth adding to the candidate record.

CoreStory must not remove a candidate from the discovery set because:

- build inclusion is unknown;
- reachability is unknown;
- configuration is unknown;
- propagation is unknown;
- an observable consequence is not yet established.

If CoreStory produces evidence that appears to disprove a candidate, record that evidence for Stage 2 but retain the candidate in the frozen discovery set.

## Stage 1 output

Every candidate receives a stable ID:

`ND-CAND-001`, `ND-CAND-002`, etc.

Minimum record:

- candidate ID;
- file/function/location;
- suspected mechanism;
- discovery evidence;
- severity hypothesis;
- discovery source;
- whether CoreStory was used;
- if CoreStory was used, what question it was used to answer;
- any candidates/paths added through CoreStory expansion.

---

# Stage 1 checkpoint — Freeze candidate set

Write the complete candidate set to:

`candidate-set.md`

After this checkpoint:

- candidates cannot be silently removed;
- qualification results cannot alter discovery recall;
- new candidates found during qualification must be labeled **QUALIFICATION-DISCOVERED** and reported separately.

This checkpoint is the denominator for discovery analysis.

---

# Stage 2 — Mechanism proof

Run the customer's existing proof process against the frozen candidates:

- `prove-nd`
- `prove-nd-mt` where appropriate.

This stage answers:

> Does the suspected ND mechanism hold at the source/mechanism level?

Record:

- PROVED;
- NOT PROVED;
- UNRESOLVED;
- mechanism evidence;
- unresolved evidence.

Do not yet collapse application qualification into the mechanism result.

A source-level mechanism can be real while production application impact is absent or neutralized.

---

# Stage 3 — CoreStory application qualification

## Objective

For each frozen candidate that remains relevant after mechanism proof, determine its application significance.

Use a dedicated CoreStory ND qualification workflow rather than the global v3 rule.

Qualification sequence:

1. **Build inclusion**
   - Is the source/artifact part of the relevant production build?

2. **Production reachability**
   - Is the function/code path reachable from a production entry point?

3. **Runtime/configuration gate**
   - What feature flags, modes, topology, thread count, or configuration must be active?

4. **Exact mechanism**
   - What value/order/state can vary?
   - What evidence proves that it can vary between equivalent executions?

5. **Propagation**
   - Which callers/consumers preserve the varying state?

6. **Neutralization**
   - Do sorting, stable comparators, re-derivation, canonicalization, synchronization, convergence, or other behavior remove the variation?

7. **Observable consequence**
   - Is there a credible path to topology, timing, QoR, output, persisted state, crash, race, or another externally relevant consequence?

8. **Evidence completeness**
   - Are any load-bearing implementations unavailable?

---

## Mandatory evidence gate

**Missing load-bearing evidence must never be replaced by inference.**

If a disposition depends on an implementation that is unavailable — for example a comparator, hash function, wrapper, external library behavior, collection converter, runtime configuration, or caller — classify the relevant qualification dimension as **UNRESOLVED**.

Do not promote a candidate to REAL solely from a structural pattern when a required semantic link is unavailable.

This requirement is derived directly from the Test 1 `msuiGetPowerTaps` investigation.

---

# Qualification dispositions

Use explicit dimensions rather than forcing every candidate into one binary label.

Recommended final dispositions:

- **REAL** — mechanism and production application consequence are supported.
- **LATENT** — mechanism is supported and a credible production path exists, but required runtime/configuration conditions are not yet confirmed.
- **CONFIGURATION-SENSITIVITY** — behavior differs only across a meaningful configuration boundary rather than equivalent executions.
- **BUILD-SENSITIVITY** — relevant only to particular build composition.
- **NEUTRALIZED** — mechanism exists locally but downstream behavior removes the variation.
- **DEAD/UNUSED** — not part of relevant production execution.
- **NOT-ND** — reported ND mechanism is disproved.
- **UNRESOLVED** — evidence required for a load-bearing conclusion is unavailable.
- **SME/RUNTIME-VALIDATION** — source/application evidence supports continued investigation but runtime or domain confirmation is required.

---

# Provenance ledger

Because Cursor session/MCP traces may not be available after execution, provenance must be captured in the generated artifact itself.

For every CoreStory interaction that materially affects a candidate, record:

| Evidence ID | Candidate | Stage | Evidence source | Question / purpose | Result | Decision affected |
| --- | --- | --- | --- | --- | --- | --- |
| E001 | ND-CAND-001 | Qualification | CoreStory | Find production callers | ... | Reachability |
| E002 | ND-CAND-001 | Qualification | Source | Inspect caller | ... | Propagation |

Evidence source must distinguish:

- **Direct source**
- **CoreStory**
- **Build/configuration**
- **Runtime**
- **Reasoned inference**
- **SME**
- **Unavailable**

For CoreStory evidence, record enough information to understand the purpose and returned evidence even if the underlying MCP transcript is later unavailable.

Do not claim that CoreStory caused a decision unless the ledger records a CoreStory contribution to that decision.

---

# Per-candidate qualification record

Each candidate should produce:

```text
Candidate ID:
Location:
Reported mechanism:

DISCOVERY
Discovery source:
Discovery evidence:
CoreStory used for expansion: YES/NO
Expansion contribution:

MECHANISM PROOF
Disposition:
Evidence:
Unresolved:

APPLICATION QUALIFICATION
Build:
Reachability:
Runtime/config:
Mechanism:
Propagation:
Neutralization:
Observable consequence:

CORESTORY CONTRIBUTION
CoreStory used: YES/NO
Questions/purposes:
Evidence contributed:
Decision(s) affected:
Could the disposition have been reached from local source alone?: YES/NO/UNKNOWN

FINAL
Disposition:
Confidence basis:
SME/runtime validation required:
```

---

# Stage 4 — SME review

Do not give the SME only a binary answer.

For each candidate provide:

- reported mechanism;
- proof result;
- application qualification;
- evidence chain;
- unresolved links;
- proposed disposition.

SME response:

- **AGREE**
- **DISAGREE**
- **INSUFFICIENT EVIDENCE**

Capture the reason when practical.

---

# Measures

## Discovery

Measure independently:

- number of frozen candidates;
- known/SME-confirmed defects represented in frozen set;
- candidates added through CoreStory discovery expansion;
- candidates missed by discovery but found during later qualification.

Do not count qualification dismissals as discovery misses.

## Qualification

For the frozen set:

- candidates correctly retained;
- candidates correctly dismissed;
- candidates correctly narrowed to configuration/build/latent conditions;
- candidates incorrectly promoted;
- candidates incorrectly dismissed;
- candidates correctly marked unresolved;
- SME agreement/disagreement.

## Evidence quality

Track whether each disposition establishes:

- build;
- reachability;
- runtime/config;
- exact mechanism;
- propagation;
- neutralization;
- observable consequence.

## Efficiency

Where reliable telemetry exists:

- tool calls;
- elapsed investigation time;
- token/model usage;
- number of artifacts/source locations SME had to inspect.

Do not make token/cost claims if model/subagent telemetry is incomplete.

A useful outcome metric is:

> **Time-to-SME-decision per candidate**

---

# Controls

To make the result interpretable:

1. Use the same frozen source snapshot.
2. Freeze the candidate list before qualification.
3. Record model and thinking effort.
4. Record subagent behavior by stage.
5. Do not mix CoreStory qualification into candidate elimination during discovery.
6. Do not expose held-out ground truth until all automated dispositions are frozen.
7. Keep SME adjudication separate from automated findings.
8. Preserve raw outputs unchanged.
9. Keep analysis artifacts separate from raw outputs.
10. Record unavailable evidence rather than filling gaps with assumptions.

---

# Recommended implementation change

For this iteration, replace the broad v3 ND rule with two narrower assets.

## Thin discovery rule

The rule should enforce only workflow behavior:

> Preserve plausible ND candidates during discovery. CoreStory may be used to expand discovery through callers, implementations, accessors, related modules, and propagation paths. Do not eliminate a candidate solely because application qualification has not yet been established. Record CoreStory contributions when they materially add or alter a candidate.

## CoreStory ND qualification skill

Move the substantive v3 qualification logic into a dedicated skill:

- build;
- reachability;
- runtime/config;
- mechanism;
- varying input;
- propagation;
- neutralization;
- observable consequence;
- evidence hierarchy;
- explicit unresolved state;
- provenance ledger;
- final disposition.

This allows discovery and qualification behavior to be tuned independently.

---

# Success criteria

Iteration 2 is useful even if CoreStory does not improve discovery.

The experiment succeeds if it allows us to answer, with evidence:

1. Did the discovery workflow retain the relevant candidate set?
2. Did CoreStory expand discovery in useful cases?
3. Did application qualification improve final dispositions?
4. Which CoreStory evidence materially changed decisions?
5. Did qualification reduce SME investigation effort?
6. Where did the workflow fail because evidence was unavailable or incorrectly inferred?

---

# Claim boundary

This experiment is designed to test a hypothesis generated by Test 1:

> CoreStory may provide more differentiated value as an application-qualification layer after broad ND discovery than as a replacement for the existing discovery mechanism.

The experiment must be allowed to disprove that hypothesis.
