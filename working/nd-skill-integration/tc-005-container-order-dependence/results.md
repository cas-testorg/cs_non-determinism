# TC-005 Results — Concurrent Container Insertion / Iteration-Order Dependence

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
TC-005 started in a fresh Cursor chat:
Prior TC-005 conversation context in new chat:
Customer skill installed/available:
CoreStory rule installed/active:
CoreStory MCP available:
Other relevant rules/skills active:
```

## Prompt

Use the exact prompt from `README.md` as a single initial prompt without follow-up steering.

## Agent final response

```text
PASTE FINAL RESPONSE HERE
```

## Cursor investigation trace

### User prompt sent

```text
PASTE EXACT PROMPT ACTUALLY SENT HERE
```

### CoreStory interactions

```text
PASTE OR SUMMARIZE CORESTORY QUERIES / TOOL CALLS HERE
```

### First CoreStory-supplied candidate path

```text
Parallel dispatch / producer set:
Shared / merged container:
Insertion / arrival / merge order source:
Downstream consumer:
Canonicalizer / sort / reselection if any:
```

### Local repository validation

```text
PASTE OR SUMMARIZE TARGETED READ/GREP OPERATIONS HERE
```

### Broad local discovery searches

```text
Were broad product-wide searches used: YES / NO
If YES, when relative to CoreStory candidate selection:
Why the agent broadened:
Patterns/areas searched:
```

### Unexpected agent/tool behavior

```text
RECORD TOOL FAILURE, BYPASS, RETRY, OR OTHER OBSERVATION HERE
```

## Candidate and causal evidence

```text
Candidate:
File(s):
Symbol(s):
Container type:
```

### Parallel dispatch / concurrent producers

```text
EVIDENCE HERE
```

### Shared / merged container

```text
EVIDENCE HERE
```

### Why insertion / arrival / merge order can vary

```text
EVIDENCE HERE
```

### Container ordering semantics

```text
EVIDENCE HERE
```

### Downstream order-sensitive consumer

```text
EVIDENCE HERE
```

### Observable impact

```text
EVIDENCE HERE
```

### Sort / canonicalization / reselection audit

```text
EVIDENCE HERE
```

### Missing evidence identified by agent

```text
EVIDENCE HERE
```

## Skill behavior assessment

```text
Container-order reasoning applied:                 YES / PARTIAL / NO
Actual concurrent producers established:           YES / PARTIAL / NO
Variable insertion/merge order established:        YES / PARTIAL / NO
Container ordering semantics verified:             YES / PARTIAL / NO
Order-sensitive consumer established:              YES / PARTIAL / NO
Observable sink investigated:                      YES / PARTIAL / NO
Canonicalization/reselection investigated:         YES / PARTIAL / NO
Missing evidence stated rather than guessed:       YES / PARTIAL / NO
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES / PARTIAL / NO
Queries preserved container-order objective:       YES / PARTIAL / NO
Producer/container/consumer path identified:       YES / PARTIAL / NO
Targeted source used for validation:                YES / PARTIAL / NO
Causal evidence requirement preserved:             YES / PARTIAL / NO
Unsupported findings avoided:                      YES / PARTIAL / NO
```

## CoreStory narrowing assessment

```text
Candidate relationship path before broad grep:     YES / PARTIAL / NO
Parallel producer set identified:                  YES / PARTIAL / NO
Shared/merged container identified:                YES / PARTIAL / NO
Downstream consumer identified:                    YES / PARTIAL / NO
Canonicalizer/sort identified where relevant:      YES / PARTIAL / NO
Local proof remained targeted:                     YES / PARTIAL / NO
Broad product-wide container search required:      YES / NO
```

Notes:

```text
Describe whether CoreStory reduced the task to validation of a concrete producer -> container -> consumer path, or whether Cursor had to discover the relationship mechanically.
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

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope.

## Test verdict

```text
PASS / PARTIAL / FAIL / INCONCLUSIVE
```

### Rationale

```text
RATIONALE HERE
```

## Follow-up

Do not define TC-006 until TC-005 has been reviewed.

```text
Recommended next change or next mechanism:
Reason:
```
