# Synopsys + CoreStory Non-Determinism Evaluation
## Technical Progress, Preliminary Findings & Controlled Validation

**Status:** Evaluation in progress  
**Primary use case:** AI-assisted non-determinism investigation in Fusion Compiler CTS

---

## Executive Summary

The goal of this evaluation is to determine whether CoreStory application intelligence can improve Synopsys's existing AI-assisted non-determinism workflow.

Synopsys already has significant expertise in this area, including custom non-determinism analysis skills, static and runtime analysis tools, and established engineering processes for investigating difficult concurrency and non-deterministic behavior.

The objective is therefore **not to replace the existing Synopsys workflow**.

Instead, the evaluation is testing whether CoreStory can complement that workflow by providing broader application context that helps determine whether a suspected issue is relevant to the built application, reachable in production, capable of propagating downstream, and ultimately capable of affecting observable behavior.

Our work to date has progressed through several stages:

1. Understand the existing Synopsys workflow and success criteria.
2. Establish the behavior of the existing AI-assisted analysis.
3. Introduce CoreStory application context.
4. Refine the division of responsibility between defect analysis and application-context qualification.
5. Design and execute a controlled A/B evaluation with Synopsys.
6. Use the A/B results to iteratively optimize the integrated workflow.

The preliminary work has produced useful technical findings, but we are intentionally **not treating exploratory results as final quantitative benchmarks**.

The authoritative measurement will come from the controlled A/B evaluation being executed in the Synopsys environment.

---

# Phase 1 — Understand the Existing Workflow

## Objective

Understand how Synopsys currently identifies, investigates, and validates non-deterministic behavior, and determine where CoreStory could add value without replacing existing engineering expertise.

## What We Learned

Synopsys already has a sophisticated non-determinism workflow that combines multiple sources of evidence, including:

- Static and runtime analysis.
- TSan and Coverity findings.
- Runtime/checksum-based investigation.
- AI-assisted source analysis.
- Custom Synopsys non-determinism skills.
- Engineering and SME validation.

This changed the initial framing of the evaluation.

The primary opportunity is not simply to introduce another mechanism for identifying suspicious C++ patterns.

The more interesting problem is determining which candidates are relevant to the actual application and deserve engineering attention.

## Resulting Hypothesis

> **Synopsys's existing expertise can identify potential non-determinism mechanisms. CoreStory can complement that expertise with application context that helps determine whether those candidates actually matter.**

---

# Phase 2 — Establish the Initial Baseline

## Objective

Understand how the existing AI-assisted workflow behaves against the CTS codebase without CoreStory application intelligence.

## What We Learned

Repository-scale non-determinism analysis can generate a significant number of potential candidates.

The challenge is progressively reducing those candidates to findings that have sufficient evidence to justify engineering investigation.

This reinforced an important distinction:

> **Finding a suspicious code pattern is not equivalent to proving an application defect.**

A candidate may appear significant when viewed locally but become less relevant after considering how the surrounding application is built and executed.

The exploratory baseline also demonstrated that the execution environment itself can influence repository-scale AI analysis. Agent orchestration, model behavior, available workflow assets, and previous analysis state all need to be considered when comparing results.

## Resulting Focus

The evaluation therefore began to shift from:

> *Can the AI find suspicious non-deterministic patterns?*

toward:

> **Can the workflow efficiently determine which suspicious patterns represent meaningful defects in the actual application?**

This distinction became increasingly important as the evaluation progressed.

---

# Phase 3 — Add CoreStory Application Context

## Objective

Determine whether adding application-level context changes how suspected non-determinism findings are evaluated.

## What We Learned

The strongest directional signal from the exploratory work came from **candidate qualification**.

CoreStory-assisted investigations introduced additional application-level questions such as:

1. Is the code included in the relevant production build?
2. Is the suspected path reachable from production behavior?
3. Are the required runtime or configuration conditions active?
4. Is there sufficient evidence for the suspected defect mechanism?
5. Can the suspected mechanism propagate into downstream application state?
6. Is the behavior subsequently normalized or otherwise made deterministic?
7. Can the behavior ultimately affect an observable application result?

These questions can materially change the interpretation of a candidate.

## Representative Example

During exploratory testing, a candidate initially appeared significant based on suspicious ordering behavior in the local source.

Application-level investigation subsequently established that the suspected implementation was not part of the relevant production build path.

The active implementation followed a different path that provided deterministic behavior.

The important result was therefore not that CoreStory found an additional suspicious pattern.

It was that **application context changed whether an existing candidate should continue through the defect-investigation process.**

A similar pattern was observed with another candidate where suspicious behavior was present in source, but deeper investigation established that the relevant execution path was not active.

These examples reinforced the importance of distinguishing between:

- Code that contains a potentially non-deterministic construct.
- Code that can actually participate in production behavior.
- Behavior that can propagate far enough to create an observable defect.

## Preliminary Finding

> **CoreStory's strongest contribution may be improving qualification of suspected defects rather than simply increasing the number of candidates found.**

This became the central hypothesis for the next phase of the evaluation.

---

# Phase 4 — Refine the Integrated Workflow

## Objective

Determine how CoreStory and Synopsys's existing non-determinism expertise should divide responsibilities.

## What We Learned

The exploratory testing suggested a useful separation of responsibilities.

### Synopsys Defect Analysis

The existing Synopsys workflow remains responsible for:

- Identifying non-determinism patterns.
- Establishing the local defect mechanism.
- Applying concurrency and non-determinism expertise.
- Performing runtime validation where appropriate.
- Determining final defect classification and severity.

### CoreStory Application Qualification

CoreStory can provide supporting application intelligence around:

- Build inclusion.
- Production reachability.
- Runtime and configuration applicability.
- Cross-component relationships.
- Downstream propagation.
- Deterministic neutralization.
- Observable application impact.

Conceptually:

    Candidate Discovery
            |
            v
    Defect-Specific Analysis
            |
            v
    Application Qualification
            |
            v
    Defect Proof / Validation
            |
            v
    Engineering Finding

This division allows each part of the workflow to focus on the type of reasoning it is best positioned to provide.

> **Synopsys skills identify and investigate the non-determinism mechanism. CoreStory provides application context needed to determine whether that mechanism is built, reachable, active, propagated, neutralized, and observable.**

## Experimental Learning

The exploratory work also identified several variables that can affect repository-scale agentic analysis, including:

- Model selection and routing.
- Agent and subagent orchestration.
- Available workflow assets.
- Execution strategy.
- Previous analysis artifacts.
- Telemetry visibility and attribution.

Because those variables could influence quantitative results, we chose not to treat the exploratory runs as an authoritative benchmark.

Instead, those runs were used to improve the experimental design.

---

# Why We Are Not Presenting Final Efficiency Percentages Yet

The exploratory runs produced useful technical evidence, but they also exposed variables that could materially influence quantitative comparisons.

For example, differences in agent orchestration, model routing, available workflow assets, prior analysis artifacts, and telemetry visibility can affect runtime, token consumption, and defect outcomes.

As a result, percentages derived from those runs could create the appearance of precision without providing a defensible causal comparison.

We are therefore treating those results as **directional evidence**, not final benchmark results.

The customer-controlled A/B test was designed specifically to remove as much of that ambiguity as possible.

> **The goal is not to produce the most favorable number. The goal is to produce a result that Synopsys can trust and reproduce.**

This is particularly important for the metrics that matter most to the evaluation:

- Defect detection and validation.
- False-positive reduction.
- Investigation effort.
- Runtime.
- Compute/token consumption.
- SME review effort.

Those measurements become substantially more meaningful when the workflow and environment are controlled.

---

# Phase 5 — Customer-Controlled A/B Validation

## Objective

Measure the incremental value of CoreStory while minimizing differences between the two workflows.

Synopsys is executing the comparison in its own controlled environment.

## Test A — Existing Synopsys Workflow

    CTS Source
        |
        v
    Existing Synopsys Skills
        |
        v
    Existing AI-Assisted Workflow
        |
        v
    Results

## Test B — Existing Workflow + CoreStory

    Same CTS Source
        |
        v
    Same Synopsys Skills
        |
        v
    Same AI-Assisted Workflow
        +
    CoreStory Application Intelligence
        |
        v
    Results

The intent is to keep the source, task, workflow, skills, model, and execution environment as consistent as possible.

The primary experimental variable is the addition of CoreStory application intelligence.

## Measurements

The controlled evaluation is intended to examine:

- Known-defect reproduction.
- Quality of additional findings.
- False-positive burden.
- Investigation time and effort.
- Coverage and completeness.
- SME validation effort.
- Compute/token usage where it can be reliably measured.

The goal is to evaluate not simply whether the two workflows produce different results, but **why** those results differ.

For example:

- Did CoreStory eliminate candidates because they were not built?
- Did application context establish that a path was unreachable?
- Did a downstream deterministic operation neutralize the suspected behavior?
- Did CoreStory expose additional relationships needed to validate a candidate?
- Did the integrated workflow require more or less investigation effort?
- Did it reduce the amount of source exploration required to reach a conclusion?

This will allow the team to evaluate both the quantitative and qualitative impact of the integration.

## Current Status

The Synopsys team has accepted the A/B methodology and is executing the evaluation.

CoreStory identified an MCP authentication constraint caused by the customer network environment, validated an alternate authentication approach, and provided the workaround to Synopsys.

We are currently awaiting validation of that configuration and completion of the controlled comparison.

## Results

**Pending customer-controlled A/B evaluation.**

We are intentionally holding final quantitative improvement claims until this evaluation is complete.

Once results are available, this section will capture the comparison across the agreed measurement categories.

---

# Phase 6 — Optimize From the Evidence

The initial A/B comparison should be treated as a **measurement point**, not necessarily the final form of the integrated workflow.

Once the results are available, CoreStory and Synopsys will review them together.

The next action will depend on what the evidence shows.

    Customer A/B Results
            |
            v
    Identify Where Value Is Gained or Lost
            |
            v
    Refine Integrated Workflow
            |
            v
    Skills / Qualification / Rules / Routing / Orchestration
            |
            v
    Re-evaluate
            |
            v
    Production-Ready Workflow

## If the Initial Results Meet the Success Criteria

The focus can move toward:

- Operationalizing the integrated workflow.
- Improving repeatability.
- Determining where it fits into the existing engineering lifecycle.
- Expanding the approach to additional non-determinism investigations.
- Evaluating applicability to adjacent engineering use cases.

## If the Results Show Value but Fall Short of the Desired Targets

The next step is not simply to repeat the same test.

Instead, the team can determine where the workflow is leaving value on the table.

Potential areas of refinement include:

- When CoreStory application context is introduced.
- How candidates are handed between analysis stages.
- How qualification is performed.
- How Synopsys skills and CoreStory responsibilities are coordinated.
- Rules governing when additional application context is required.
- Workflow routing and orchestration.
- Prompt and task decomposition.

This provides a structured way to iterate from evidence rather than optimizing toward a predetermined result.

> **The objective is not simply to prove that CoreStory can participate in the existing process. The objective is to determine the most effective way to combine Synopsys's existing non-determinism expertise with CoreStory's application intelligence.**

---

# Potential Follow-Up — Isolate Qualification Value

If the initial A/B results indicate that candidate discovery introduces too much variability, a follow-up evaluation can isolate the qualification stage.

Rather than allowing both workflows to independently discover candidates, the team can establish a fixed candidate set and evaluate how each workflow qualifies the same evidence.

    Discovery
        |
        v
    Fixed Candidate Set
        |
        +----------------------+
        |                      |
        v                      v
    Qualification A        Qualification B
    Synopsys Workflow      Same Workflow
    Without CoreStory      + CoreStory
        |                      |
        +----------+-----------+
                   |
                   v
            Compare Outcomes

This would allow the team to measure CoreStory's contribution specifically in areas such as:

- Build inclusion.
- Production reachability.
- Runtime/configuration applicability.
- Cross-component relationships.
- Downstream propagation.
- Deterministic neutralization.
- Observable impact.

It would also reduce the influence of differences in candidate discovery and allow the evaluation to focus specifically on the area where the exploratory work has shown the strongest directional signal.

---

# What We Can Claim Today

Based on the exploratory work, we can reasonably say that:

- The workflow has been exercised end to end.
- Repository-scale analysis produces a significant candidate-filtering problem.
- Application context can materially change how suspected non-determinism findings are qualified.
- Build inclusion, reachability, runtime applicability, propagation, deterministic neutralization, and observable impact are important qualification signals.
- CoreStory-assisted analysis demonstrated examples where application context changed whether an initially significant candidate survived deeper investigation.
- The exploratory work directly informed the design of the customer-controlled A/B evaluation.
- Synopsys has accepted that evaluation methodology and is executing it in its controlled environment.

The strongest preliminary finding remains:

> **The harder problem is not simply generating suspects. It is determining which suspects actually matter in the built application.**

---

# What We Are Not Claiming Yet

Until the controlled A/B evaluation is complete, we are not claiming:

- A precise token-reduction percentage.
- A precise runtime-improvement percentage.
- A controlled defect-recall advantage.
- A final false-positive-reduction percentage.
- A controlled improvement attributable to any individual rule or workflow change.
- That the current integration represents the fully optimized Synopsys + CoreStory workflow.

Those claims should be evaluated against the customer-controlled results.

---

# Current Position

## What We Have Learned

The exploratory work has demonstrated that application context can materially affect how non-determinism candidates are qualified.

It has also helped establish a clearer division between defect-specific analysis and application-level qualification.

The work has moved the evaluation from a broad question of whether CoreStory can assist non-determinism analysis toward a more specific and testable hypothesis:

> **Can application intelligence improve the quality and efficiency of determining which suspected non-determinism defects actually matter in the production application?**

## What We Are Validating Now

Whether that application intelligence produces measurable incremental value when added to Synopsys's existing workflow under controlled conditions.

## What Comes Next

1. Complete the customer-controlled A/B evaluation.
2. Review the results jointly with the Synopsys team.
3. Compare the outcomes against the agreed success criteria.
4. Identify where CoreStory added value and where additional refinement is needed.
5. Iteratively tune the integrated workflow.
6. Re-evaluate where appropriate.
7. Determine the path toward a repeatable production workflow.

---

# Key Takeaway

The evaluation has progressed from exploratory testing to a customer-controlled validation of a specific technical hypothesis.

The preliminary work indicates that CoreStory's most promising role is not simply finding more suspicious code.

It is providing the broader application intelligence needed to answer a more valuable question:

> **Does this suspected defect actually matter in the application that is built and run?**

The controlled A/B evaluation will provide the quantitative evidence needed to measure that contribution.

From there, CoreStory and Synopsys can use the results to iteratively develop the most effective combined workflow.
