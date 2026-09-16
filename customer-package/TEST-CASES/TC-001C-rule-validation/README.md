# TC-001C — CoreStory v3 Rule Validation

## Status

**Completed qualitative rule-behavior experiment. Directionally useful; not a controlled v2-vs-v3 benchmark.**

## Purpose

TC-001C followed TC-001B to evaluate whether a revised CoreStory governing rule produced a more disciplined application-qualification workflow.

The intended change was narrow:

```text
TC-001B: code-analysis-v2.mdc
TC-001C: code-analysis-v3.mdc
```

The same broad CTS source scope, user prompt, CoreStory connection, and Synopsys non-determinism skills were intended to remain unchanged.

This test was not designed to determine whether v3 finds more defects. It was designed to evaluate **how candidates are investigated before promotion**.

## Test Configuration

- **Application:** Fusion Compiler CTS
- **CoreStory MCP:** Enabled
- **CoreStory governing rule:** `code-analysis-v3.mdc`
- **Synopsys non-determinism skills:** Enabled and unmodified
- **Ground-truth TSan/Coverity findings:** Held out
- **Severity requested:** HIGH and MEDIUM
- **User steering after submission:** None intended

User-specific local paths, session identifiers, infrastructure identifiers, and raw execution traces are excluded from this customer package.

## Prompt

The same broad prompt was used without mentioning v3, CoreStory, known findings, TSan, Coverity, or specific source files:

```text
/nd-code-analyzer scan <CTS_WORKSPACE> for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## What Changed in v3

The revised rule made the promotion criteria explicit. A suspicious source construct should not be promoted as a real application defect until the investigation establishes the relevant evidence chain:

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

The rule also tightened investigation isolation: prior reports, candidate files, benchmark outputs, and held-out defects should not become evidence unless intentionally supplied to the investigation.

## Intended Division of Responsibility

TC-001C clarified an important separation between defect expertise and application context.

### Synopsys non-determinism workflow

Responsible for identifying and investigating the **non-determinism mechanism**, including questions such as:

- Is there a race, unstable ordering, entropy source, incomplete tie-break, or other ND mechanism?
- Under what concurrency or execution conditions can it occur?
- Is the mechanism itself technically credible?

### CoreStory application intelligence

Used to qualify the candidate in the context of the application:

- Is the implementation part of the relevant build?
- Is it reachable from a production path?
- Do runtime/configuration gates activate it?
- How does the behavior propagate across components?
- Is the effect deterministically normalized before it matters?
- Does it reach an observable application/QoR boundary?

The intended relationship is therefore:

```text
Synopsys skills
    identify + investigate ND mechanism
                |
                v
CoreStory
    qualify in application context
                |
                v
Defect proof / SME validation
```

CoreStory is not treated as a replacement for Synopsys defect expertise or runtime/static-analysis methods.

## Observed Behavior

The TC-001C execution generated a large mechanical candidate set — approximately **15,000 candidates before narrowing** — and then decomposed the investigation into child analysis sessions.

The child investigations showed stronger qualification-oriented behavior than simple pattern promotion. Observed investigation themes included:

- distinguishing pointer-container patterns from existing deterministic comparator usage;
- checking whether an apparent ordering issue reached an order-sensitive consumer;
- looking for deterministic comparators and canonicalization/neutralization behavior;
- distinguishing membership-only container usage from order-sensitive iteration;
- considering build and production-path evidence before promotion;
- requiring downstream observability rather than treating a suspicious construct alone as proof of a defect.

This behavior was directionally aligned with the v3 evidence sequence.

## What the Result Supports

TC-001C supports the following qualitative observation:

> **The revised rule was better aligned with an evidence-gated qualification model in which a source-level ND mechanism is a candidate, not automatically a production defect.**

The test also reinforced the application-qualification pattern seen in TC-001B:

```text
Pattern match
    !=
Confirmed ND mechanism
    !=
Built/reachable mechanism
    !=
Observable production defect
```

Each transition requires evidence.

## Why the Final Finding Count Is Not the Main Result

The final findings changed again during TC-001C, but the execution topology also changed. Cursor created child/subagent sessions despite the visible controls, and the fallback scanning strategy differed in execution details.

Because both the governing rule and autonomous execution behavior affected the run, the resulting finding set cannot be causally attributed to v3 alone.

For that reason, this package does **not** present TC-001C as evidence that v3 increased or decreased defect count by a particular amount.

## Investigation Isolation

TC-001C intentionally left prior local artifacts in the environment so the v3 isolation requirement could be observed rather than manually enforced by cleaning the workspace.

This was a useful rule-compliance question:

> Can the governing rule prevent prior reports and candidate artifacts from becoming evidence even when they are physically available to the agent?

The broader experiment showed that agent execution and orchestration were not controlled tightly enough to turn this into a definitive rule-compliance benchmark. The lesson carried forward was that clean isolated workspaces are preferable for controlled A/B testing, while the rule should still explicitly prohibit use of prior findings and held-out ground truth.

## Experimental Limitations

### Autonomous child/subagent execution

Cursor again created child/subagent analysis sessions despite the visible control configuration. This changed the execution topology relative to earlier runs.

**Impact:** differences in final findings cannot be attributed solely to the v2-to-v3 rule change.

### Fallback discovery workflow

Expected scanner/report helper scripts were still unavailable, so the agent synthesized a repository-scanning workflow using local search tooling before deeper investigation.

The mechanical pass generated roughly 15,000 candidates before narrowing.

**Impact:** candidate volume and execution cost are properties of this exploratory execution, not a controlled measurement of the intended production workflow.

### Model/orchestration attribution

The exploratory environment did not provide sufficiently deterministic model/orchestration control for precise model-specific economics.

**Impact:** TC-001C should not be used to claim token, runtime, or cost improvement from v3.

## SME / Engineering Review

TC-001C is primarily a workflow-design artifact rather than a list of independently validated defects. The useful review questions are therefore:

- [ ] Is build inclusion required before promoting a production ND defect?
- [ ] Is production reachability required?
- [ ] Are runtime/configuration gates relevant to qualification?
- [ ] Should a deterministic neutralizer prevent promotion when it occurs before the observable sink?
- [ ] Is downstream observable behavior required before a candidate is classified as a real equivalent-run defect?
- [ ] Does the proposed division of responsibility between Synopsys ND expertise and CoreStory application context match the intended engineering workflow?
- [ ] Are any qualification stages missing or incorrectly ordered?

**SME notes:**

---

## Relationship to TC-001A and TC-001B

The three exploratory tests represent a progression in the evaluation:

```text
TC-001A
Baseline discovery
"What suspicious ND patterns survive the existing workflow?"
        |
        v
TC-001B
CoreStory-assisted qualification
"Does application context change which candidates survive?"
        |
        v
TC-001C
Qualification-rule refinement
"Can we make that application-context reasoning systematic and evidence-gated?"
```

TC-001A established the scale of the candidate-filtering problem. TC-001B provided concrete examples where build, reachability, implementation, and neutralization evidence changed candidate disposition. TC-001C turned those lessons into a more explicit qualification sequence.

## Interpretation

The most defensible conclusion from TC-001C is about **workflow design**, not defect count:

> **Synopsys skills identify and investigate the non-determinism mechanism. CoreStory supplies application context needed to determine whether that mechanism is built, reachable, active, propagated, neutralized, and observable.**

TC-001C provided directional evidence that the v3 rule better expressed that division of labor. It did not establish a controlled v2-vs-v3 performance improvement.

The experiment also made clear that future controlled testing should verify not only the prompt, model selection, and source revision, but the actual execution topology and model usage observed during the run.
