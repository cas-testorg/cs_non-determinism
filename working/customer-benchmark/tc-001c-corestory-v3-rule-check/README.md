# TC-001C — CoreStory v3 Rule Check

## Purpose

Run a quick follow-up to TC-001B to see whether the revised CoreStory governing rule changes investigation behavior in a useful way.

This is **not** a new benchmark arm and should not be used for final A/B economics. It is a controlled comfort check of **v2 versus v3 rule behavior** before the customer readout.

## Experimental change

The intended difference from TC-001B is only:

```text
TC-001B rule=code-analysis-v2.mdc
TC-001C rule=code-analysis-v3.mdc
```

Everything else should remain as close to TC-001B as possible.

## Test arm

```text
CoreStory MCP=Enabled
CoreStory governing rule=Enabled
CoreStory governing rule file=code-analysis-v3.mdc
Explore Subagent Model=Disabled
Ground truth=Hidden
```

Keep the same installed Synopsys skills and the same CTS source state.

## Source scope

```text
CTS_SCOPE=C:\Users\carys\cts
CODE_COMMIT_OR_VIEW=NA
```

## Model controls

Use the same visible model configuration used for TC-001B.

```text
UI_SELECTED_MODEL=Claude Opus 4.8
CURSOR_USAGE_RECORDED_MODEL=
VERIFIED_EXECUTION_MODEL=
```

Do not intentionally select Auto and do not change model settings during the run.

Cursor telemetry in TC-001B showed autonomous routing/orchestration variance, so model-specific token economics are not the purpose of this check.

## Important environment rule

Do **not** delete, move, hide, or otherwise clean up prior local ND artifacts solely for TC-001C.

TC-001B had access to prior analysis artifacts. Keeping the environment otherwise unchanged allows this test to answer a narrow question:

> Does `code-analysis-v3.mdc` itself cause the agent to avoid reusing prior analysis and apply the stricter qualification workflow?

The v3 rule's investigation-isolation requirement should control that behavior. If the agent still reuses prior reports or candidate artifacts, record that as a rule-compliance failure.

Held-out TSan/Coverity ground truth must remain unavailable exactly as before.

## Prompt

Use `prompt.md` exactly as written.

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

Do not add any mention of v3, qualification, prior findings, CoreStory, known files, TSan, or Coverity to the prompt.

## Before submitting

Confirm:

1. CoreStory MCP is connected.
2. `code-analysis-v3.mdc` is active and v2 is not the governing rule for this run.
3. CTS source/workspace is unchanged from TC-001B.
4. Installed Synopsys skills are unchanged.
5. Explore Subagent Model remains disabled.
6. The same visible model selection is used.
7. Request Traces remain enabled at `Trace` if available.
8. Held-out TSan/Coverity ground truth is absent.

## Execution

Submit the prompt once and do not steer the agent.

If Cursor creates child sessions, allow them to complete and preserve them.

If the agent encounters prior ND artifacts, do not intervene. Record whether v3 causes it to ignore them or whether it consumes them despite the isolation rule.

If CoreStory MCP fails, preserve the failure instead of restarting the run.

## What to observe

This test is primarily qualitative. Capture:

- whether prior reports/candidate artifacts are reused,
- whether build inclusion is checked before promotion,
- whether production reachability is checked,
- whether runtime/configuration gates are considered,
- whether neutralizers/canonicalization are checked,
- whether downstream observability is established,
- which CoreStory queries/calls are used,
- local Grep/Glob/Read activity,
- final HIGH/MEDIUM count,
- non-real classifications,
- parent/child session behavior,
- wall-clock runtime,
- Cursor usage/model telemetry where available,
- any human intervention.

## Desired v3 behavior

A successful v3 behavior check does **not** require finding more defects.

The desired signal is that the agent follows a more disciplined sequence:

```text
candidate
  -> build inclusion
  -> production reachability
  -> runtime/configuration gate
  -> defect mechanism
  -> propagation
  -> neutralizer/canonicalization check
  -> observable consequence
  -> REAL only if supported
```

CoreStory should primarily provide application context; targeted source inspection should establish the local code mechanism.

Candidates lacking sufficient evidence should be classified as non-real or unresolved rather than promoted.

## Comparison with TC-001B

After the run, compare TC-001C to TC-001B on these questions:

1. Did v3 prevent reuse of prior analysis artifacts?
2. Was qualification more systematic and explicit?
3. Did CoreStory retrieval become more targeted around build/reachability/downstream context?
4. Did the agent avoid broad claims based only on pattern matches?
5. Did the final dispositions become easier to defend?

## Interpretation

TC-001C is a **rule-behavior validation**, not a customer benchmark.

If v3 produces cleaner evidence discipline, that is useful support for the meeting statement that the local testing directly informed a tighter CoreStory qualification rule.

If it does not, preserve that result as evidence that the rule needs further refinement rather than modifying the test mid-run.
