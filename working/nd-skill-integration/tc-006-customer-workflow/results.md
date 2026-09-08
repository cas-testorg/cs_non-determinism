# TC-006 Results — Customer CTS ND Discovery + Verification Workflow

## Test status

```text
NOT RUN
```

## Environment / pre-run gate

```text
Date/time:
Agent/client:
Agent/client version:
CTS source path:
CTS source revision:
CoreStory project/workspace:

nd-code-analyzer skill available:                     YES / NO
prove-nd skill available:                            YES / NO
prove-nd-mt skill available:                         YES / NO
nd-code-analyzer scripts/references available:       YES / NO
/create-cli-agent available:                         YES / NO
cursor-agent available:                              YES / NO
CoreStory rule installed/active:                     YES / NO
CoreStory MCP available:                             YES / NO
```

## Workflow fidelity

```text
Execution mode: EXACT CUSTOMER ORCHESTRATION / CONTROLLED WORKFLOW EMULATION

Discovery model requested:
Discovery model actually used:
Verification model requested:
Verification model actually used:
Verification isolation method: create-cli-agent / new clean Cursor conversation
Known orchestration deviations:
Known model deviations:
Other environment deviations:
```

## TC-006A — Discovery

### Discovery prompt actually sent

```text
PASTE EXACT PROMPT HERE
```

### Skill activation / scanner execution

```text
nd-code-analyzer read/activated:
Mechanical scanner executed:
Pattern catalog/references available:
Parallel triage/subagents used:
Other customer skills/tools invoked:
Unexpected discovery-tool behavior:
```

### Discovery operations

```text
Mechanical scanner/search operations:
CoreStory interactions:
Targeted local reads:
Broad local searches beyond scanner:
Repeated/redundant discovery work:
```

### Candidate flow

```text
Raw scanner candidate count:
Candidate count after triage/deep read:
Candidate count handed to verification:
```

For each handed-off candidate:

```text
Candidate ID/name:
Mechanism/category:
File/symbol/location:
Discovery evidence:
MT evidence already present:
Downstream observability already present:
Controls/gates already identified:
Neutralizers already identified:
Discovery classification if any:
```

### CoreStory contribution during discovery

```text
Application relationships/context supplied:
Candidate narrowing/triage contribution:
Reachability contribution:
Downstream consumer contribution:
Control/gate contribution:
Neutralizer contribution:
Where CoreStory did not help:
```

### Discovery artifact

```text
Artifact name/path:
Was it preserved unmodified for handoff: YES / NO
If modified, why:
```

## Discovery -> verification handoff

```text
Handoff method: create-cli-agent / manual clean-context emulation
Clean verifier context confirmed: YES / NO
Prior TC-006A conversation visible to verifier: YES / NO
Prior TC-001..TC-005 findings exposed: YES / NO
Hidden ground truth exposed: YES / NO
```

For each candidate:

```text
Candidate:
Evidence/context passed:
Verification instruction passed:
Verifier model actually used:
Additional context manually added: NONE / DESCRIBE
```

## TC-006B — Verification

### Verification prompt actually sent

```text
PASTE EXACT PROMPT HERE
```

### Skill activation

```text
prove-nd read/activated:
prove-nd-mt read/activated:
CoreStory rule active:
Additional subagents spawned by verifier: YES / NO
Unexpected verification-tool behavior:
```

### Per-candidate verification

For each candidate:

```text
Candidate:
MT reachability:
Variability mechanism:
Race vs ordering assessment:
Shared/worker/order-dependent state:
Downstream consumer / consequence:
Controls / gates:
Neutralizer / reset / canonicalizer audit:
Final classification:
Missing evidence:
CoreStory interactions:
Local source validation:
Context rediscovered from discovery phase:
```

### CoreStory contribution during verification

```text
Application relationships/context supplied:
Reachability contribution:
Downstream observability contribution:
Control/gate contribution:
Neutralizer contribution:
Where CoreStory did not help:
```

### Verification artifact / final response

```text
PASTE FINAL VERIFICATION RESPONSE HERE
```

## Cross-phase assessment

```text
nd-code-analyzer workflow preserved:                 YES / PARTIAL / NO
Mechanical discovery scan preserved:                 YES / PARTIAL / NO
CoreStory coexisted with scanner workflow:            YES / PARTIAL / NO
CoreStory contributed during discovery:              YES / PARTIAL / NO
Candidate handoff was concrete/usable:                YES / PARTIAL / NO
Verifier context was isolated:                        YES / PARTIAL / NO
prove-nd proof discipline preserved:                  YES / PARTIAL / NO
prove-nd-mt proof discipline preserved:               YES / PARTIAL / NO
Downstream consequence investigated:                  YES / PARTIAL / NO
Neutralizers investigated:                            YES / PARTIAL / NO
Unsupported Real findings avoided:                    YES / PARTIAL / NO
Verification avoided major rediscovery:               YES / PARTIAL / NO
Workflow/model deviations recorded:                   YES / PARTIAL / NO
```

## Discovery -> verification duplication

```text
What context/evidence was successfully reused from the discovery artifact?

What application context had to be rediscovered by the verifier?

Were the repeated operations necessary proof validation or avoidable discovery duplication?

Did CoreStory reduce rediscovery between phases?
```

## Observable interaction summary

```text
TC-006A CoreStory interactions:
TC-006A local scanner/search/read operations:
TC-006A broad searches beyond mandated scanner:
TC-006B CoreStory interactions:
TC-006B local search/read operations:
Repeated work across phases:
Manual interventions:
Unexpected agent/tool behavior:
```

This section is intentionally limited to observable workflow behavior. Token metering is out of scope.

## Findings summary

```text
Real:
Neutralized:
Latent-only:
False positive:
Safe adopter:
Dead/unused:
Unresolved:
Other classifications:
```

## Test verdict

```text
PASS / PARTIAL / FAIL / INCONCLUSIVE
```

### Rationale

```text
RATIONALE HERE
```

## Interpretation boundary

```text
State whether this was exact customer orchestration or controlled workflow emulation.
Do not interpret TC-006 as Coverity recall/precision evidence.
Do not attribute model/orchestration differences to CoreStory without evidence.
```

## Follow-up

```text
What did TC-006 establish?
What remains unknown?
What customer input/tooling is still required?
Should the next step be workflow refinement, Coverity ground-truth benchmarking, or no additional synthetic testing?
```
