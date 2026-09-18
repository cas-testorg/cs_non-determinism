# Evidence Index

This index maps the internal review to the existing source artifacts. Raw and historical artifacts are referenced rather than copied.

## Existing process and exploratory evaluation

- [Customer package technical evaluation summary](../../customer-package/READOUTS/Technical-Evaluation-Summary.md)
- [Evaluation methodology](../../customer-package/METHODOLOGY/evaluation-methodology.md)
- [Claim boundaries](../../customer-package/METHODOLOGY/claim-boundaries.md)
- [SME review guide](../../customer-package/METHODOLOGY/SME-review-guide.md)
- [TC-001A baseline](../../customer-package/TEST-CASES/TC-001A-baseline/)
- [TC-001B CoreStory](../../customer-package/TEST-CASES/TC-001B-corestory/)
- [TC-001C rule validation](../../customer-package/TEST-CASES/TC-001C-rule-validation/)
- [TC-002 controlled A/B methodology](../../customer-package/TEST-CASES/TC-002-controlled-ab/)

## Customer A/B Test 1

- [Test 1 team readout](../../CUSTOMER_AB/Test-1-With-Subagents/analysis/TEAM-READOUT.md)
- [Test 1 analysis](../../CUSTOMER_AB/Test-1-With-Subagents/analysis/test-1-analysis.md)
- [Finding crosswalk](../../CUSTOMER_AB/Test-1-With-Subagents/analysis/finding-crosswalk.md)
- [Customer comparison/adjudication artifact](../../CUSTOMER_AB/Test-1-With-Subagents/analysis/snps_core_nd_comparison.md)
- [Focused investigations](../../CUSTOMER_AB/Test-1-With-Subagents/analysis/investigations/)
- [Without-MCP raw artifacts](../../CUSTOMER_AB/Test-1-With-Subagents/raw/Without-MCP/)
- [With-MCP raw artifacts](../../CUSTOMER_AB/Test-1-With-Subagents/raw/With-MCP/)

## Iteration 2 discovery experiment

- [Test plan](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/TEST-PLAN.md)
- [Staged execution prompt](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/PROMPT.md)
- [Synopsys supporting artifacts](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/Synopsys_supporting_artifacts/)
- [Thin CoreStory discovery rule](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/assets/RULES/corestory-nd-discovery.mdc)

### Final controlled discovery run

- [Run manifest](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/results/second-run/run-manifest.md)
- [Frozen candidate set](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/results/second-run/candidate-set.md)
- [Discovery readout](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/results/second-run/discovery-readout.md)
- [Cursor execution transcript](../../CUSTOMER_AB/Iteration-2-Qualification-Experiment/results/second-run/cursor_staged_execution_evaluation.md)

## Evidence hierarchy used in this review

Where possible, interpret evidence in this order:

1. Direct source evidence.
2. Build and configuration evidence.
3. CoreStory application relationships.
4. Runtime/control evidence.
5. Reasoned inference.
6. SME determination.

Missing load-bearing evidence is not equivalent to negative evidence. When an implementation or runtime fact required by a conclusion is unavailable, the appropriate disposition is unresolved.

## Important boundaries

- The Test 1 nine-issue union is source-reviewed, not runtime ground truth.
- No Test 1 finding was runtime reproduced by this evaluation.
- The final discovery run tests project 10 application scope. Several upstream library implementations were not ingested.
- Token/runtime/cost claims remain hypotheses unless supported by reliable telemetry.
- The first Iteration 2 discovery attempt is historical evidence only because it did not preserve the actual scanner/subagent workflow.
