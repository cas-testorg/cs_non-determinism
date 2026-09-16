# Synopsys Findings Package — Sanitization Inventory

## Purpose

This branch is being prepared as a customer-facing evidence package for the exploratory CoreStory non-determinism work. The package is intended to be pulled into the customer VDI and reviewed there.

The exploratory test cases are **directional evidence and workflow learning**, not the authoritative customer-controlled A/B benchmark. Customer A/B results are not included here until the customer provides the underlying results and SME review is complete.

## Sanitization principles

The customer package should preserve enough information to understand the test design, observed behavior, conclusions, and limitations while avoiding unnecessary environment-specific or sensitive material.

Retain:

- test purpose and experimental design;
- exact user prompt after replacing local machine paths with neutral placeholders;
- CoreStory enabled/disabled state and governing-rule version;
- high-level model configuration where relevant to limitations;
- directional finding counts where they help explain the experiment;
- qualification concepts such as build inclusion, reachability, runtime gates, propagation, neutralization, and observability;
- sanitized representative examples;
- limitations and claim boundaries.

Remove or summarize:

- raw JSONL conversation exports;
- raw Cursor/request logs and telemetry exports;
- local usernames and machine-specific paths;
- authentication material, tokens, MCP connection strings, organization/workspace identifiers, or internal infrastructure details;
- large intermediate candidate/search artifacts;
- raw source excerpts or customer code not required to explain the result;
- hidden TSan/Coverity ground-truth locations;
- internal troubleshooting material and unrelated experiments.

## Test-case inventory

| Test case | Customer-package disposition | Material to preserve | Material to exclude or reconstruct |
|---|---|---|---|
| TC-001 initial pilot | **Summarize only** | Why a clean rerun was required | Raw session data, disk/environment troubleshooting, telemetry |
| TC-001A baseline control | **Sanitize and include** | Purpose, controls, prompt, directional result, orchestration limitation | JSONL sessions, candidate JSON, narrowed packs, usage CSV, local paths, raw source details |
| TC-001B CoreStory discovery/qualification | **Sanitize and include** | Purpose, intended delta, qualification result, representative application-context examples, limitations | JSONL session, usage CSV, local paths, raw source excerpts, environment-specific telemetry |
| TC-001C v3 rule check | **Sanitize and include** | Purpose, v2→v3 change, qualification sequence, qualitative observations and limitations | JSONL sessions, raw candidate/search JSON, logs, local paths, raw source details |
| TC-002 customer-controlled A/B | **Methodology/status only for now** | Test design and statement that customer results are under SME review | Observed customer counts, cost/token figures, candidate details, or conclusions until customer delivers/approves underlying data |
| TC-003 CoreStory qualification skill | **Exclude from findings package for now** | None unless later used in Iteration 2 | Experimental skill design is future/iteration work rather than evidence from the completed exploratory package |

## Current artifact assessment

### TC-001A — Baseline control

The existing README is useful as an internal record but should not be delivered unchanged. It contains a local Windows source path, detailed Cursor telemetry uncertainty, exact session behavior, internal artifact names, and source-specific finding details. A customer-facing reconstruction should retain the run classification, the fact that the ground truth was hidden, the broad prompt, the directional finding result, and the key limitation that autonomous orchestration prevented treating the run as a final benchmark.

Recommended customer files:

```text
TEST-CASES/TC-001A-baseline/
  README.md
  prompt.md
  sanitized-results.md
```

### TC-001B — CoreStory-assisted qualification

The existing README contains the strongest exploratory evidence and should be reconstructed rather than copied verbatim. Preserve the finding that application context changed which candidates survived qualification, along with sanitized examples demonstrating build inclusion/reachability/neutralization. Preserve the explicit limitation that prior analysis artifacts were available and model/orchestration attribution was not controlled.

Recommended customer files:

```text
TEST-CASES/TC-001B-corestory/
  README.md
  prompt.md
  sanitized-results.md
```

### TC-001C — v3 governing-rule behavior

This is best presented as a qualitative workflow-refinement experiment, not a benchmark. Preserve the disciplined qualification sequence and explain that the purpose was to improve evidence requirements before promotion. Do not include the large candidate/search artifacts or raw session exports.

Recommended customer files:

```text
TEST-CASES/TC-001C-rule-validation/
  README.md
  prompt.md
  sanitized-results.md
```

## Files/directories that should not be part of the delivered package

The branch currently inherits the full development repository. The following areas are not part of the intended customer evidence package and should not be copied into the final deliverable directory:

```text
archive/
working/cursor-token-test/
working/vdi-troubleshooting/
working/nd-skill-integration/**/artifacts/*.jsonl
working/customer-benchmark/**/results/*.jsonl
working/customer-benchmark/**/results/*.csv
working/customer-benchmark/**/results/*.log
working/customer-benchmark/**/results/*candidate*.json
working/customer-benchmark/**/results/*narrowed*.json
```

This is a packaging rule, not a statement that every inherited file contains sensitive information.

## Proposed delivered directory

Rather than deleting the development repository in place, construct a self-contained customer package under:

```text
customer-package/
  README.md
  READOUTS/
    Technical-Evaluation-Summary.md
  METHODOLOGY/
    evaluation-methodology.md
    qualification-model.md
    claim-boundaries.md
  TEST-CASES/
    TC-001A-baseline/
    TC-001B-corestory/
    TC-001C-rule-validation/
    TC-002-controlled-ab/
```

Only the `customer-package/` directory should be treated as deliverable content. This allows the package to be reviewed before it is copied into the customer VDI and avoids relying on deletion-based sanitization.

## Next pass

1. Create the `customer-package/` skeleton and package README.
2. Reconstruct sanitized TC-001A, TC-001B, and TC-001C summaries from the preserved internal records.
3. Copy/adapt the current technical readout into `customer-package/READOUTS/`.
4. Add methodology and claim-boundary documents.
5. Run a final sensitive-data review over only `customer-package/` before delivery.
