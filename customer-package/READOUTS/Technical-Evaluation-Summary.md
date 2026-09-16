# Synopsys + CoreStory Non-Determinism Evaluation
## Technical Evaluation Summary

**Primary use case:** AI-assisted non-determinism investigation in Fusion Compiler CTS  
**Current status:** Exploratory evaluation complete; customer-controlled A/B executed and undergoing Synopsys SME/internal review

---

## Executive Summary

This evaluation is testing whether CoreStory application intelligence can improve Synopsys's existing AI-assisted non-determinism workflow.

Synopsys already has established non-determinism expertise, custom analysis skills, static/runtime analysis methods, and engineering validation. CoreStory is therefore being evaluated as a **complement to that workflow**, not a replacement for it.

The evaluation has progressively narrowed to a specific technical hypothesis:

> **Can application intelligence improve the ability to determine which suspected non-determinism mechanisms actually matter in the application that is built and run?**

The strongest signal from the exploratory work was not an increase in the number of suspects. It was that application context materially changed how several suspects were qualified.

The work progressed through four main test stages:

| Test | Purpose | Primary learning |
|---|---|---|
| **TC-001A** | Baseline discovery without CoreStory | Repository-scale discovery creates a substantial candidate-filtering problem |
| **TC-001B** | Same broad task with CoreStory | Build, reachability, implementation, and observability evidence can change candidate disposition |
| **TC-001C** | Refine the CoreStory qualification rule | Qualification should follow a systematic evidence-gated sequence |
| **TC-002** | Synopsys-controlled A/B | Customer-owned measurement and SME validation of the integrated workflow |

TC-002 has been executed and is currently undergoing Synopsys internal/SME review. Detailed A/B outcome claims are intentionally deferred until that review and the underlying evidence are available.

---

## What the Exploratory Work Showed

### TC-001A — Baseline Discovery

The baseline exploratory run used the Synopsys non-determinism workflow without CoreStory application intelligence.

The mechanical discovery stage generated **4,535 hits across 817 files** before narrowing to **1 HIGH and 6 MEDIUM** promoted findings.

The important observation was the scale of the funnel. Broad source-pattern discovery can generate thousands of candidates; engineering value depends on determining which candidates have enough evidence to warrant promotion.

This reinforced a central distinction:

> **A suspicious source-code pattern is a candidate for investigation, not proof of a production defect.**

### TC-001B — CoreStory-Assisted Qualification

The matching exploratory CoreStory run retained the same broad user task while adding CoreStory application intelligence and a governing qualification rule.

After deeper qualification, the report promoted **0 HIGH and 0 MEDIUM** findings.

This should not be read as "CoreStory found zero defects" or as proof that the seven baseline findings were false positives. The useful result was the **reason particular candidates changed disposition**.

#### Representative example — `ctoFlowClone.cc`

The baseline identified a credible local mechanism in `ctoFlowClone.cc`: default pointer ordering in `std::set<ndmTerm*>` fed order-sensitive mutation and an early-break path.

The CoreStory-assisted investigation then expanded the question beyond the local source construct and reported that:

1. `ctoFlowClone.cc` was not included in the relevant production build definition.
2. The investigated production path used `ctoRestruct.cc`.
3. The production implementation used `termSetType`.
4. `termSetType` used `ndmObjPtrCmpType`, providing deterministic pointer ordering.

Conceptually:

```text
Suspicious local mechanism
    ctoFlowClone.cc
    std::set<ndmTerm*>
            |
            X  not in relevant production build

Investigated production path
    ctscto.cc
        -> ctoRestruct.cc
        -> termSetType
        -> ndmObjPtrCmpType
        -> deterministic ordering
```

The local mechanism remained technically interesting; the **application-level relevance changed**.

Another candidate contained `std::random_device`, which would be significant on a live QoR path. The deeper investigation reported that its only identified caller was commented out and no other live references were found.

These dispositions remain subject to Synopsys SME validation.

### TC-001C — Qualification Rule Refinement

TC-001C used the exploratory evidence to make the application-qualification criteria explicit:

```text
candidate
  -> build inclusion
  -> production reachability
  -> runtime/configuration gate
  -> defect mechanism
  -> propagation
  -> deterministic neutralizer / canonicalization check
  -> observable consequence
  -> REAL only if supported
```

The run generated approximately **15,000 mechanical candidates before narrowing** and showed stronger qualification-oriented behavior in child investigations, including checks for deterministic comparators, order-sensitive consumers, neutralizers, and downstream observability.

However, autonomous child/subagent execution changed the execution topology. The final finding differences therefore cannot be attributed solely to the v3 rule.

TC-001C is best understood as a **workflow/rule validation experiment**, not a controlled v2-vs-v3 benchmark.

---

## Resulting Integrated Workflow

The exploratory work suggests a complementary division of responsibility:

```text
Synopsys ND skills
    identify + investigate the ND mechanism
                |
                v
CoreStory application intelligence
    qualify build / reachability / runtime / propagation / neutralization / observability
                |
                v
Defect proof + Synopsys SME validation
                |
                v
Engineering finding
```

Synopsys remains responsible for non-determinism expertise and final engineering judgment. CoreStory's proposed role is to provide broader application context that helps determine whether a credible mechanism matters in production.

---

## Why the Exploratory Tests Are Not the Final Benchmark

The exploratory runs exposed several variables that can influence repository-scale agentic analysis:

- autonomous child/subagent orchestration;
- uncertain model attribution/routing;
- missing expected workflow helper scripts;
- prior analysis artifacts in some runs;
- differences in execution strategy and telemetry visibility.

Those limitations do not erase source-level or application-level evidence associated with individual findings. They do prevent a defensible causal claim about aggregate token reduction, runtime improvement, recall, or false-positive percentage.

The exploratory tests were therefore used to **improve the experimental design** rather than to produce final performance claims.

---

## TC-002 — Customer-Controlled A/B

Synopsys executed the controlled comparison in its environment.

### Arm A

Existing Synopsys workflow with CoreStory disabled.

### Arm B

The same intended source, task, Synopsys skills, and workflow with CoreStory application intelligence and the v3 qualification rule enabled.

The evaluation is intended to examine:

- known-defect reproduction;
- additional credible findings;
- finding quality and false-positive burden;
- investigation/SME effort;
- runtime and compute/token economics where attribution is reliable;
- why findings differ between the two arms.

### Current status

**The A/B execution is complete and Synopsys is reviewing the findings internally and with SME expertise.**

This package intentionally does not publish preliminary finding counts or economics from that run before the reviewed evidence is available.

The most valuable next artifact will be a finding-level comparison that maps each difference between the arms to its evidence and SME determination.

---

## What We Can Say Today

The evidence currently supports saying that:

- the workflow has been exercised against CTS at repository scale;
- broad ND analysis creates a significant candidate-filtering problem;
- application context can materially change how suspected findings are qualified;
- build inclusion, reachability, runtime applicability, propagation, neutralization, and observable impact are meaningful qualification dimensions;
- concrete exploratory examples exist where application context changed whether a candidate survived deeper investigation;
- the exploratory work directly informed a more rigorous customer-controlled A/B methodology.

The strongest preliminary technical observation remains:

> **The harder problem is not simply generating suspects. It is determining which suspects actually matter in the built application.**

---

## What We Are Not Claiming Yet

Until the TC-002 evidence and SME review are complete, this evaluation does not establish:

- a precise token or compute reduction;
- a precise runtime improvement;
- a controlled recall advantage;
- a final false-positive-reduction percentage;
- that every exploratory CoreStory disposition is correct;
- a controlled performance improvement attributable solely to v3;
- that the current workflow is the final optimized Synopsys + CoreStory integration.

---

## Next Step — Optimize From the Evidence

TC-002 should be treated as a measurement point rather than the end of the workflow design.

Once the reviewed A/B evidence is available, the most useful analysis is finding-by-finding:

```text
A/B candidate
    -> how it was discovered
    -> ND mechanism evidence
    -> application qualification evidence
    -> CoreStory calls/context, if applicable
    -> model/subagent execution topology
    -> Synopsys SME determination
```

That comparison will show whether differences came from candidate discovery, application qualification, execution/orchestration behavior, or the underlying defect reasoning.

If discovery variability makes the end-to-end comparison difficult to interpret, a follow-up can isolate the strongest exploratory value signal by using a **fixed candidate set** and comparing qualification of the same suspects with and without CoreStory.

The objective is to use the evidence to iteratively determine the most effective combination of Synopsys's existing non-determinism expertise and CoreStory application intelligence.
