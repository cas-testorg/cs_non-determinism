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
Discovery model requested:
Discovery model actually used:
Verification model requested:
Verification model actually used:
CTS source path:
CTS source revision:
CoreStory project/workspace:

nd-code-analyzer skill available:                      YES / NO
prove-nd-mt skill available:                           YES / NO
base prove-nd skill available:                         YES / NO
/create-cli-agent available:                           YES / NO
CoreStory rule installed/active:                       YES / NO
CoreStory MCP available:                               YES / NO
Fresh Cursor chat:                                     YES / NO
Prior TC-001..TC-005 findings exposed to agent:        YES / NO
```

## Workflow deviations

```text
Record every known difference from the customer-described workflow, including model, skill path, orchestration, client, or agent substitutions.
```

## Prompt actually sent

```text
PASTE EXACT PROMPT HERE
```

## Discovery phase

### Skill activation

```text
nd-code-analyzer read/activated:
Other skills/rules activated:
```

### CoreStory interactions

```text
PASTE OR SUMMARIZE CORESTORY QUERIES / TOOL CALLS HERE
```

### Local repository discovery

```text
PASTE OR SUMMARIZE SEARCH/READ OPERATIONS HERE
```

### Candidates produced

```text
Candidate count:

1. Candidate:
   Mechanism/category:
   File/symbol/location:
   Discovery evidence:

2. Candidate:
   Mechanism/category:
   File/symbol/location:
   Discovery evidence:
```

## Discovery -> verification handoff

For each candidate:

```text
Candidate:
Evidence/context passed to verifier:
Verification instruction:
Verifier agent/model actually used:
CoreStory context passed/requeried:
Local context passed/requeried:
```

## Verification phase

For each verified candidate:

```text
Candidate:
MT reachability:
Variability mechanism:
Race vs ordering assessment:
Downstream consumer / consequence:
Neutralizer / reset / canonicalizer audit:
Final classification:
Missing evidence:
CoreStory interactions:
Local source validation:
```

## Final agent response

```text
PASTE FINAL RESPONSE HERE
```

## Workflow assessment

```text
Broad ND discovery performed by customer skill:       YES / PARTIAL / NO
CoreStory used during discovery:                      YES / PARTIAL / NO
CoreStory used during verification:                   YES / PARTIAL / NO
Candidate handoff observable:                         YES / PARTIAL / NO
Verification avoided unnecessary rediscovery:         YES / PARTIAL / NO
prove-nd-mt proof discipline preserved:               YES / PARTIAL / NO
Downstream consequence investigated:                  YES / PARTIAL / NO
Neutralizers investigated:                            YES / PARTIAL / NO
Unsupported Real findings avoided:                    YES / PARTIAL / NO
Workflow/model deviations recorded:                   YES / PARTIAL / NO
```

## CoreStory contribution

```text
What application relationships/context did CoreStory provide during discovery?

What application relationships/context did CoreStory provide during verification?

Where did the agent still require broad local mechanical searching?

Did CoreStory reduce rediscovery between the discovery and verification phases?
```

## Observable Cursor interaction summary

```text
CoreStory interactions:
Local repository searches/reads:
Broad repo-wide searches:
Repeated/redundant searches:
Secondary-agent interactions:
Unexpected agent/tool behavior:
```

This section is intentionally limited to observable workflow behavior. Token metering is out of scope.

## Test verdict

```text
PASS / PARTIAL / FAIL / INCONCLUSIVE
```

### Rationale

```text
RATIONALE HERE
```

## Follow-up

```text
What did TC-006 establish?
What remains unknown?
What customer input is still required?
Should the next step be workflow refinement, Coverity ground-truth benchmarking, or no additional synthetic testing?
```
