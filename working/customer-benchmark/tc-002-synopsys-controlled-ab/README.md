# TC-002 — Synopsys-Controlled CoreStory A/B Evaluation

## Purpose

Establish a customer-owned, reproducible baseline for the existing Synopsys nondeterminism workflow, then measure the incremental value of adding CoreStory to that same workflow.

The intent is **not** to replace the Synopsys skills or defect-analysis process. The comparison should preserve the existing workflow and add CoreStory only as an application-context and qualification layer.

The authoritative result should come from the Synopsys-controlled environment because Synopsys can control model selection, source state, skill installation, orchestration, telemetry, and workspace isolation more tightly than the earlier local exploratory runs.

## Core comparison

The primary comparison has two arms.

### Arm A — Synopsys standalone baseline

Run the existing Synopsys nondeterminism workflow with:

```text
CoreStory MCP=Disabled
CoreStory governing rule=Disabled
Synopsys skills=Enabled and unmodified
Prompt=Fixed
Source scope=Fixed
Model=Fixed and verified
Workspace/session=Clean
Held-out ground truth=Hidden
```

This run establishes the standalone result that Synopsys trusts in its own environment.

### Arm B — Same workflow with CoreStory

Repeat the same test with:

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
CoreStory rule=code-analysis-v3.mdc
Synopsys skills=Enabled and unmodified
Prompt=Identical to Arm A
Source scope=Identical to Arm A
Model=Identical to Arm A and verified
Workspace/session=Clean
Held-out ground truth=Hidden
```

The intended experimental change is the addition of **CoreStory MCP + the governing rule**. All other controllable variables should remain the same.

## What this test is intended to prove

The test should determine whether adding CoreStory to the existing Synopsys workflow changes any of the following in a measurable and useful way:

- Candidate qualification quality
- False-positive / reviewer burden
- Recall against known defects
- Additional credible findings
- Time to result
- Token / compute cost
- Amount of local repository search and file-reading work

A particularly important question is whether CoreStory helps distinguish a suspicious source-code pattern from a defect that actually matters in the built application.

Examples of qualification evidence include:

- Production build inclusion
- Reachable callers and execution paths
- Active feature or runtime gates
- Dependencies and shared-state relationships
- Downstream consumers and observable impact
- Deterministic comparators, normalization, canonicalization, synchronization, or other neutralizers

## Test phases

### Phase 0 — Preflight

Do not begin a measured run until the environment passes preflight.

Record and verify:

- CTS source location and revision/view
- Exact Synopsys skill package/version
- Required skill scripts and dependencies are present
- Exact user prompt
- Exact model and model version
- Model is pinned or otherwise verifiably controlled; do not use ambiguous Auto routing for a measured run
- Subagent/orchestration settings are documented
- Workspace is clean and does not contain prior ND reports, candidate files, benchmark artifacts, or held-out defect locations
- Runtime/token telemetry is available and understood
- Start/end timestamps can be captured

If a required skill component is missing, stop the benchmark rather than allowing the agent to synthesize a replacement workflow.

### Phase 1 — Standalone Synopsys baseline

Run Arm A with the agreed prompt and capture all metrics and output artifacts.

Do not expose TSan, Coverity, or other held-out known-defect locations during discovery or qualification.

### Phase 2 — CoreStory implementation preflight

Before Arm B, integrate CoreStory without changing the Synopsys skills.

#### Enable CoreStory MCP

The exact client/harness-specific installation location should be confirmed during setup. At minimum:

1. Configure the CoreStory MCP endpoint in the selected agent/client.
2. Complete the required CoreStory authentication/authorization flow.
3. Confirm the client can connect successfully.
4. Confirm the intended CTS CoreStory project/workspace is visible.
5. Execute a lightweight MCP validation call, such as listing available projects or retrieving project metadata, before the measured run.
6. Record the MCP endpoint/configuration used.

Do not begin Arm B if MCP connectivity is intermittent or authentication is unresolved.

#### Install the CoreStory governing rule

The rule must be installed where the selected agent/harness will actually apply governing/project instructions. The exact location is client-specific and must be confirmed during preflight.

For the primary Arm B test, install and enable:

```text
rules/code-analysis-v3.mdc
```

Requirements:

- Confirm the rule is active before the measured run.
- Do not load v2 and v3 simultaneously.
- Record the rule filename and Git commit used.
- Do not modify the Synopsys skills to accommodate the rule.

`code-analysis-v2.mdc` is retained in this test case for reproducibility and optional follow-on comparison, but **v3 is the recommended rule for the primary CoreStory arm**.

### Phase 2A — CoreStory integration smoke test

Before the measured CoreStory run, perform a small smoke test whose only purpose is to confirm that:

1. The selected CLI can see and call CoreStory MCP.
2. The v3 governing rule is active in the session.

This is not a nondeterminism benchmark and should not perform a repository-wide ND scan.

The exact commands will depend on the CLI selected by Synopsys. The following examples are intended as starting points and should be adjusted once the execution environment is confirmed.

#### Cursor CLI example

For Cursor CLI, configure CoreStory MCP through the normal Cursor MCP configuration and install the v3 rule in the project rule location used by the CLI, for example `.cursor/rules/` when applicable.

Example validation flow:

```bash
# Confirm configured MCP servers
agent mcp list

# Confirm CoreStory tools are visible
agent mcp list-tools <corestory-server-name>

# Start from the test workspace
cd tc-002-synopsys-controlled-ab

# Run a lightweight validation prompt
agent --mode=ask "
Use CoreStory to identify the current project/workspace and return one
application-level relationship, such as a component, dependency, or call path.

Also state which project rules are governing this analysis and summarize
the CoreStory qualification criteria you are expected to apply.

Do not perform a nondeterminism scan.
"
```

#### Claude Code example

For Claude Code, configure the CoreStory MCP server using the CLI's MCP configuration mechanism. The v3 governing instructions should be installed using the project-instruction mechanism supported by Claude Code, such as a project-level `CLAUDE.md`, rather than assuming the `.mdc` file is consumed natively.

Example validation flow:

```bash
# Confirm MCP configuration
claude mcp

# Start from the test workspace
cd tc-002-synopsys-controlled-ab

# Run a lightweight validation prompt
claude -p "
Use CoreStory to identify the current project/workspace and return one
application-level relationship, such as a component, dependency, or call path.

Also summarize the CoreStory qualification criteria governing this analysis.

Do not perform a nondeterminism scan.
"
```

#### Behavioral rule probe

In addition to confirming that CoreStory tools are callable, use a small behavioral prompt to verify that the v3 rule is influencing qualification behavior:

```text
A file contains a pointer-ordered container.
Is that sufficient to classify it as a real nondeterminism defect?
Explain what additional evidence is required before promotion.
```

A v3-aligned response should not promote the pattern by itself. It should require evidence such as:

- Build inclusion
- Production reachability
- Applicable runtime/configuration controls
- The actual defect mechanism
- Propagation to downstream state or behavior
- Absence of a deterministic neutralizer
- Observable consequence

#### Smoke-test pass criteria

Record the smoke test as PASS only when both conditions are satisfied:

```text
MCP_CONNECTIVITY=PASS
- CoreStory server is visible
- CoreStory tools are visible
- At least one CoreStory tool call succeeds
- The returned result corresponds to the intended CTS project/workspace

RULE_ACTIVATION=PASS
- The agent demonstrates the expected v3 qualification behavior
- The response reflects build/reachability/neutralizer/observability criteria
- The full nondeterminism scan was not performed during the smoke test
```

If either condition fails, resolve the integration issue before beginning Arm B.

### Phase 3 — CoreStory comparison run

Run Arm B using the same source, prompt, model, skills, and measurement approach used for Arm A.

The rule should cause CoreStory to be used primarily for application-level qualification evidence while targeted source inspection establishes the local defect mechanism.

### Phase 4 — Ground-truth scoring

Only after both Arm A and Arm B are complete, compare each result against the held-out TSan/Coverity reference set.

Score at minimum:

- Known defects re-detected
- Known defects missed
- Additional credible defects
- Final promoted HIGH/MEDIUM findings
- False positives or findings rejected during engineering review
- Reasons candidates were downgraded or rejected

Where useful, record dispositions such as:

```text
REAL
LATENT
UNRESOLVED
DEAD/UNUSED
MT-UNREACHABLE
GATE-INACTIVE
NEUTRALIZED
SAFE-ADOPTER
CONFIGURATION-SENSITIVITY
BUILD-SENSITIVITY
PLATFORM-SENSITIVITY
FALSE-POSITIVE
```

## Fixed prompt

Unless Synopsys deliberately chooses a different production prompt before the test begins, use the same prompt for both arms:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

If the Synopsys-controlled environment uses a different CTS path, update only the path and preserve the analysis instruction exactly between Arm A and Arm B.

## Metrics to capture for every measured run

Record:

- Test arm
- Start time
- End time
- Wall-clock runtime
- Source revision/view
- Prompt text or prompt hash
- Model and model version
- Skill package/version
- Rule version, if any
- CoreStory MCP enabled/disabled
- Number of parent/child/subagent sessions if the agent exposes this
- Local search/tool calls
- Files read/opened, if available
- CoreStory MCP calls
- Input/cache/output/total tokens where available
- Candidate count
- Final HIGH findings
- Final MEDIUM findings
- Rejected/downgraded candidate count
- Human interventions
- Errors, retries, or environment anomalies

If model attribution, token accounting, or orchestration cannot be verified, record that limitation rather than deriving a precise economics claim from the run.

## Run-validity rules

A run should be flagged as non-authoritative for the primary A/B comparison if any of the following occurs:

- The two arms use different source revisions or materially different prompts
- The intended model cannot be verified
- Required Synopsys skill assets are missing
- The agent silently substitutes a different analysis implementation
- Prior benchmark artifacts or held-out known defects influence discovery/qualification
- CoreStory connectivity fails materially during Arm B
- Significant human intervention changes the workflow

The artifact can still be retained as diagnostic evidence, but it should not be used for precise A/B claims.

## Interpretation

The primary question is not whether the CoreStory arm simply produces a larger defect list.

The stronger question is:

> Does adding CoreStory to the existing Synopsys workflow improve the ability to determine which suspected defects actually matter in the built application, while maintaining or improving recall and reducing engineering effort or compute cost?

The desired integration model is:

```text
Synopsys skills
    -> identify and reason about nondeterminism mechanisms

CoreStory
    -> provide application context needed to qualify those mechanisms

Targeted source inspection
    -> prove or reject the local code behavior
```

## Optional follow-on: v2 versus v3

Do **not** mix rule-version testing into the primary Arm A versus Arm B comparison.

After the primary result is complete, Synopsys may optionally repeat the CoreStory arm with `code-analysis-v2.mdc` to evaluate whether the more qualification-focused v3 rule changes behavior. If this is done, preserve the same controls and treat it as a separate rule-evaluation experiment.

## Test-case layout

```text
tc-002-synopsys-controlled-ab/
├── README.md
├── rules/
│   ├── code-analysis-v2.mdc
│   └── code-analysis-v3.mdc
└── results/
    └── README.md
```

Store measured run artifacts under `results/` in clearly separated subdirectories for the standalone and CoreStory arms.

Suggested structure:

```text
results/
├── arm-a-standalone/
└── arm-b-corestory-v3/
```
