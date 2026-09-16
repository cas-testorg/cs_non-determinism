# Claim Boundaries

## Purpose

This document distinguishes conclusions supported by the exploratory evaluation from questions that require the customer-controlled A/B results and Synopsys SME validation.

## What the Exploratory Work Supports

### The workflow has been exercised against CTS at repository scale

The evaluation executed the Synopsys non-determinism workflow against the CTS source both without and with CoreStory application intelligence.

### Candidate filtering is a material part of the problem

The baseline exploratory run generated 4,535 Stage-1 hits across 817 files before narrowing to seven promoted HIGH/MEDIUM findings. A later exploratory execution generated approximately 15,000 mechanical candidates before narrowing.

These counts are properties of the exploratory executions, not estimates of the number of actual CTS defects. They demonstrate the difference between broad candidate generation and engineering-grade qualification.

### Application context can materially change candidate disposition

The CoreStory-assisted exploratory work produced concrete examples where candidates changed disposition after build, caller/reachability, implementation, neutralization, or observability evidence was considered.

For example, a locally suspicious pointer-ordered implementation in `ctoFlowClone.cc` was subsequently reported as absent from the relevant production build, while the investigated production implementation used a deterministic comparator. Another candidate containing `std::random_device` was reported to have no live caller.

These experimental dispositions are preserved for Synopsys SME validation.

### Qualification requires more than identifying an ND mechanism

The exploratory work supports using evidence such as:

- build inclusion;
- production reachability;
- runtime/configuration applicability;
- defect-mechanism evidence;
- downstream propagation;
- deterministic neutralization/canonicalization;
- observable application impact.

### The exploratory work improved the evaluation methodology

TC-001A established the candidate-filtering problem. TC-001B exposed the value of application-context qualification. TC-001C translated those lessons into a more explicit evidence-gated qualification rule. Those lessons informed the customer-controlled TC-002 design.

## What the Exploratory Work Does Not Establish

The exploratory tests do **not** establish:

- a precise CoreStory token-reduction percentage;
- a precise runtime or cost improvement;
- a controlled recall advantage;
- a final false-positive-reduction percentage;
- that seven baseline findings were all false positives;
- that zero findings in TC-001B means CTS contains no relevant non-determinism defects;
- a causal performance improvement attributable solely to v3 versus v2;
- that the current workflow is the fully optimized Synopsys + CoreStory integration.

## Why Those Claims Are Deferred

The exploratory environment exposed variables including autonomous child/subagent execution, uncertain model attribution, missing expected workflow helper scripts, prior analysis artifacts, and differences in execution strategy.

Those factors do not erase finding-specific evidence, but they prevent precise causal attribution of aggregate counts, runtime, tokens, or economics.

## Customer-Controlled A/B

TC-002 was designed to provide a more authoritative comparison by keeping the two arms as consistent as possible and adding CoreStory as the intended experimental variable.

The customer-controlled A/B has been executed and is currently undergoing Synopsys internal/SME review. Detailed quantitative results and conclusions are intentionally excluded from this package until the reviewed underlying evidence is available.

## SME Validation Boundary

Throughout this package, terms such as **experimental disposition**, **reported qualification**, or **CoreStory-assisted conclusion** distinguish AI-assisted analysis from Synopsys's final engineering judgment.

The SME review should be treated as the authority for whether the evidence supports the proposed classification.

## Current Technical Hypothesis

The evaluation currently supports testing this hypothesis under controlled conditions:

> **CoreStory application intelligence can complement Synopsys's existing non-determinism expertise by improving the ability to determine whether suspected mechanisms are built, reachable, active, propagated, neutralized, and observable in the production application.**

TC-002 and subsequent SME validation determine how strongly that hypothesis is supported and where the integrated workflow should be refined.
