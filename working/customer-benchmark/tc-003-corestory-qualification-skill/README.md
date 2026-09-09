# TC-003 — CoreStory Qualification Skill Check

## Purpose

Run one focused follow-up test to determine whether an explicit `corestory-qualify` skill provides a cleaner and more repeatable integration pattern than relying on the CoreStory governing rule alone.

This is a **Plan B workflow test**, not a replacement for the Synopsys-controlled A/B plan in TC-002 and not a source of authoritative benchmark economics.

The test should answer one practical question:

> With the customer's normal broad nondeterminism prompt, will the agent discover and use a reusable CoreStory qualification skill to improve application-context qualification of candidates?

## Why this test exists

The existing Synopsys skills already contain strong defect-specific expertise:

- `nd-code-analyzer` identifies and triages nondeterminism candidates.
- `prove-nd` proves or dismisses source-level nondeterminism suspects.
- `prove-nd-mt` extends proof for multi-threaded nondeterminism.

The experimental CoreStory skill should **not** duplicate that expertise. Its role is limited to application-context qualification:

```text
Synopsys analysis skill
    -> identifies candidate mechanism

corestory-qualify
    -> build inclusion
    -> production reachability
    -> runtime/configuration gates
    -> cross-component relationships
    -> downstream propagation
    -> neutralizers
    -> observable application consequence

Synopsys prove skill / targeted source inspection
    -> final defect verdict and severity
```

## Test configuration

Use the same CTS source scope and the same broad customer-style prompt used in the recent runs.

```text
CoreStory MCP=Enabled
CoreStory governing rule=Disabled
CoreStory qualification skill=Enabled
Synopsys skills=Enabled and unmodified
Ground truth=Hidden during discovery/qualification
Source scope=Same CTS source used in prior tests
Model=Explicitly selected and recorded
```

The key change for this test is replacing the CoreStory v3 governing rule with the `corestory-qualify` skill.

Do **not** enable `code-analysis-v3.mdc` at the same time. The purpose is to see whether the skill can carry the qualification workflow on its own.

## Skill under test

Install or expose:

```text
working/nd-skill-integration/skills/corestory-qualify/SKILL.md
```

Keep the existing Synopsys skills available and unmodified.

## Prompt

Use the normal broad prompt without adding CoreStory-specific instructions:

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

If the local CTS path differs, change only the path.

Do not mention:

- CoreStory
- the qualification skill
- known defect locations
- prior findings
- TSan
- Coverity
- specific files or defect classes

This is deliberate. The test is meant to determine whether the workflow can use the available skill without requiring a more prescriptive user prompt.

## Preflight

Before starting:

- Confirm CoreStory MCP is connected and the intended CTS project/workspace is visible.
- Confirm `corestory-qualify` is installed/discoverable by the selected client.
- Confirm the existing Synopsys ND skills are available.
- Disable the CoreStory v2/v3 governing rules for this run.
- Keep held-out TSan/Coverity reference defects unavailable.
- Record the explicitly selected model.
- Record whether the client allows or spawns subagents and any model-routing behavior observed.
- Avoid intentionally supplying prior ND reports or candidate lists to the session.

If the CoreStory skill is not discoverable, stop and record `SKILL_DISCOVERY_FAILED` rather than manually adding CoreStory qualification instructions to the prompt.

## What to observe

During the run, capture whether the workflow naturally invokes or follows the CoreStory qualification skill.

Look specifically for:

- Whether `corestory-qualify` is read or invoked without being named in the user prompt
- Whether CoreStory MCP calls occur after candidate discovery rather than as broad undirected repository exploration
- Build inclusion checks
- Production reachability checks
- Runtime/configuration gate checks
- Downstream propagation analysis
- Neutralizer/canonicalization checks
- Observable-consequence reasoning
- Whether local source inspection is still used for the defect mechanism
- Whether the originating Synopsys skill retains final realness/severity responsibility
- Final HIGH/MEDIUM findings
- Rejected/downgraded candidates and reasons
- Number of CoreStory calls
- Local Grep/Glob/Read or equivalent operations
- Parent/child/subagent behavior
- Wall-clock runtime
- Model/usage telemetry available from the client
- Human intervention required

## Desired behavior

A good result should resemble:

```text
candidate identified by nd-code-analyzer
    -> corestory-qualify invoked
    -> build inclusion established
    -> production reachability established
    -> runtime/configuration gates checked
    -> downstream propagation traced
    -> neutralizers checked
    -> observable consequence established or rejected
    -> prove-nd / prove-nd-mt or targeted source completes defect proof
    -> final severity assigned by defect-analysis workflow
```

CoreStory should not become the source of truth for the local C++ mechanism, and the CoreStory skill should not independently label a candidate `REAL` merely because application relationships exist.

## Pass / fail interpretation

### Strong positive

Record `SKILL_INTEGRATION=PASS` when:

- The broad prompt remains unchanged.
- The agent discovers/uses `corestory-qualify` without explicit prompting.
- CoreStory usage is focused on application-context qualification.
- Qualification follows the intended build/reachability/gating/propagation/neutralizer/observability flow.
- Existing Synopsys skills continue to own defect-specific reasoning and final severity.

### Partial positive

Record `SKILL_INTEGRATION=PARTIAL` when:

- The skill is discovered, but only some qualification gates are applied; or
- CoreStory is used appropriately but the handoff back to the Synopsys proof workflow is inconsistent; or
- Client orchestration/subagents make attribution difficult but the intended workflow is visible.

### Negative

Record one or more of:

```text
SKILL_DISCOVERY_FAILED
SKILL_NOT_USED
CORESTORY_USED_TOO_BROADLY
DEFECT_RESPONSIBILITY_BLURRED
QUALIFICATION_INCOMPLETE
MODEL_ORCHESTRATION_UNCONTROLLED
RUN_CONTAMINATED
```

A negative result is still useful. It means the governing rule may be the better integration mechanism, or the originating Synopsys skill may need an explicit handoff point to `corestory-qualify`.

## Comparison target

Do not treat this as a clean quantitative A/B against TC-001C because the local harness has already shown model, subagent, and prior-artifact variance.

Use the prior v3 run only as a qualitative reference:

- Did the skill produce a more explicit candidate -> qualification -> proof handoff?
- Was CoreStory usage narrower and more purposeful?
- Did the agent avoid treating CoreStory as a general-purpose first step?
- Did the workflow remain usable with the customer's broad prompt?

If the answer is yes, retain `corestory-qualify` as the Plan B integration option for the customer-controlled TC-002 evaluation.

## Output to retain

Save:

```text
results/
├── final-report.md
├── transcript-or-session-export.*
└── notes.md
```

In `notes.md`, record at minimum:

```text
SKILL_INTEGRATION=
CORESTORY_SKILL_DISCOVERED=
CORESTORY_SKILL_USED=
CORESTORY_MCP_CALLS=
FINAL_HIGH=
FINAL_MEDIUM=
SUBAGENTS_OBSERVED=
SELECTED_MODEL=
RECORDED_MODEL=
RUNTIME=
HUMAN_INTERVENTION=
CONTAMINATION_NOTES=
```

## Decision after this run

If the qualification skill works naturally with the broad prompt, keep it as the preferred Plan B for Synopsys:

```text
Primary approach:
Synopsys skills + CoreStory MCP + v3 governing rule

Plan B:
Synopsys skills + CoreStory MCP + corestory-qualify skill
```

Do not combine the v3 rule and qualification skill in the primary comparison unless a later test explicitly evaluates that combined design.
