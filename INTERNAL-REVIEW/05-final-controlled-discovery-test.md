# 05. Final Controlled Discovery Test

## Purpose

This test was designed as one final discovery-focused attempt after the customer A/B and earlier integration work.

The objective was deliberately favorable to discovery expansion:

> Preserve every candidate the customer workflow would retain. Allow CoreStory to expand the search surface, but do not allow CoreStory qualification evidence to eliminate customer candidates during discovery.

## Controls

The final run corrected the known problems from the first Iteration 2 attempt.

All six required staged artifacts matched the expected Git blob fingerprints. The actual customer scan_nd.py was executed. No ad hoc scanner was substituted. The scanner loaded all 27 customer patterns.

The customer skill's threshold for parallel Explore triage was triggered by 588 candidate files across 21 top-level source directories. Seven Explore subagents ran with model set to inherit. No fallback or model-routing deviation was observed.

CoreStory was constrained to project 10, cts-code. Project 9, cts-code2, was excluded.

The run performed Stage 0 verification and Stage 1 discovery only. It stopped after the candidate set and discovery readout were frozen.

## Results

The actual customer scanner produced:

- **3,673 raw candidates**
- **27 patterns**
- **588 files**

Five high-volume patterns reached the customer scanner's default 500-hit per-pattern cap. The default was preserved to maintain workflow fidelity and is documented as a recall limit.

After customer-workflow triage:

- **334 total frozen candidates**
- **334 CUSTOMER-PATTERN**
- **0 CORESTORY-EXPANSION**
- **0 BOTH**
- **0 materially broadened CoreStory discovery paths**

Discovery-time hypotheses were 2 real, 282 latent-only, 25 UNRESOLVED, and 25 mirror-duplicate. These are not final defect dispositions.

## CoreStory activity

Six targeted CoreStory semantic searches attempted to resolve project wrapper semantics, comparator ordering, order-sensitive consumers, insertion-order behavior, design/database mutations driven by suspicious iteration, and first-match selection over unordered/hash containers.

The result was direct:

> CoreStory produced corroborating context on already-retained candidates, but no new candidate source location and no materially broadened discovery path.

No customer candidate was removed by CoreStory.

## Application-scope limitation

The project 10 CoreStory index contained the CTS module source already scanned by the customer workflow.

Several load-bearing semantics needed to resolve remaining uncertainty live in upstream libraries that were not part of the ingested project, including implementations related to dosUnordered types, NDM pointer comparison, nwcInsOrdMap, and other comparator/wrapper behavior.

CoreStory could surface references to those types but could not inspect implementations that were not present.

The test therefore shows no differentiated discovery expansion for the application scope provided. It does not establish what would happen if the broader upstream implementation estate were ingested.

## Why this run carries more weight

The first Iteration 2 attempt lacked the actual customer scanner and did not run Explore subagents because the Cursor setting had been left disabled. It also continued into later proof and qualification.

Those issues were corrected before the final run.

Once the customer workflow was restored, all 334 retained candidates originated from the customer discovery process.

## Discovery conclusion

For the tested configuration, differentiated CoreStory value in broad ND candidate discovery was **not demonstrated**.

This provides a reasonable stopping point for repeated discovery tuning unless a material experimental condition changes.
