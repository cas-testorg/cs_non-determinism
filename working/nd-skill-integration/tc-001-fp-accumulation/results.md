# TC-001 Results — Race-Free Floating-Point Accumulation

## Test status

```text
NOT RUN
```

## Environment

```text
Date/time:
Agent/client:
Agent/client version:
Model:
CoreStory project/workspace:
Repository/revision:
Existing Cursor sessions backed up/preserved:
TC-001 started in a fresh Cursor chat:
Prior TC-001 conversation context in new chat:
Customer skill installed/available:
CoreStory rule installed/active:
CoreStory MCP available:
Other relevant rules/skills active:
```

## Prompt

Use the exact prompt from `README.md`. Do not edit the prompt here after the run; preserve the test definition separately from the observed results.

## Agent final response

```text
PASTE FINAL RESPONSE HERE
```

## Cursor investigation trace

### User prompt sent

```text
PASTE THE EXACT PROMPT ACTUALLY SENT HERE
```

### CoreStory interactions

```text
PASTE OR SUMMARIZE CORESTORY TOOL CALLS/QUERIES VISIBLE IN CURSOR HERE
```

Count where practical:

```text
CoreStory interactions:
```

### Local repository operations

```text
PASTE OR SUMMARIZE LOCAL SEARCH/READ OPERATIONS VISIBLE IN CURSOR HERE
```

Count where practical:

```text
Local repository searches/reads:
Files inspected:
Broad repo-wide searches:
```

### Unexpected agent/tool behavior

```text
RECORD ANY UNEXPECTED TOOL CHOICE, BYPASS, RETRY, FAILURE, OR OTHER OBSERVATION HERE
```

## Candidate and causal evidence

```text
Candidate:
File(s):
Symbol(s):
```

### Parallel dispatch / MT reachability

```text
EVIDENCE HERE
```

### Floating-point accumulation/reduction

```text
EVIDENCE HERE
```

### Why accumulation order can vary

```text
EVIDENCE HERE
```

### Synchronization / race-vs-ordering determination

```text
EVIDENCE HERE
```

### Downstream consumer / observable impact

```text
EVIDENCE HERE
```

### Canonicalization / neutralizer audit

```text
EVIDENCE HERE
```

### Missing evidence identified by agent

```text
EVIDENCE HERE
```

## Skill behavior assessment

```text
MT-specific reasoning applied:                     YES / PARTIAL / NO
Data race vs order dependence distinguished:       YES / PARTIAL / NO
MT reachability established:                       YES / PARTIAL / NO
Lock treated correctly:                            YES / PARTIAL / NO / N/A
Canonicalization investigated:                     YES / PARTIAL / NO
Observable sink investigated:                      YES / PARTIAL / NO
Missing evidence stated rather than guessed:       YES / PARTIAL / NO
```

Notes:

```text
NOTES HERE
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES / PARTIAL / NO
Queries preserved defect mechanism/objective:      YES / PARTIAL / NO
Application relationships used to narrow source:   YES / PARTIAL / NO
Targeted source used for validation:                YES / PARTIAL / NO
Causal evidence requirement preserved:             YES / PARTIAL / NO
Unsupported findings avoided:                      YES / PARTIAL / NO
```

Notes:

```text
NOTES HERE
```

## Cursor interaction observations

```text
CoreStory interactions:
Local repository searches/reads:
Files inspected:
Broad repo-wide searches:
Repeated/redundant searches:
Unexpected agent behavior:
```

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL analysis, request counts, and token-efficiency metrics are out of scope for TC-001.

## Test verdict

```text
PASS / PARTIAL / FAIL / INCONCLUSIVE
```

### Rationale

```text
RATIONALE HERE
```

## Follow-up

Do not define TC-002 until TC-001 has been reviewed.

```text
Recommended next change or next mechanism:
Reason:
```
