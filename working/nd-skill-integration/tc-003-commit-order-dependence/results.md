# TC-003 Results — Commit-Order Dependence / First-Writer-Wins

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
TC-003 started in a fresh Cursor chat:
Prior TC-003 conversation context in new chat:
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
Competing producer(s):
Shared destination / commit / selection site:
Downstream consumer:
CoreStory evidence for relationship:
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
```

### Parallel dispatch / concurrent producers

```text
EVIDENCE HERE
```

### Competing valid results

```text
EVIDENCE HERE
```

### Shared destination / commit / selection point

```text
EVIDENCE HERE
```

### Why completion / commit order can vary

```text
EVIDENCE HERE
```

### Race vs race-free ordering determination

```text
EVIDENCE HERE
```

### Downstream consumer / observable impact

```text
EVIDENCE HERE
```

### Arbitration / tie-break / canonicalization audit

```text
EVIDENCE HERE
```

### Missing evidence identified by agent

```text
EVIDENCE HERE
```

## Skill behavior assessment

```text
Commit-order reasoning applied:                    YES / PARTIAL / NO
Actual concurrent producers established:           YES / PARTIAL / NO
Competing valid outcomes established:              YES / PARTIAL / NO
Variable completion/commit order established:      YES / PARTIAL / NO
Race vs ordering distinguished:                    YES / PARTIAL / NO
Shared destination/selection identified:           YES / PARTIAL / NO
Observable sink investigated:                      YES / PARTIAL / NO
Arbitration/canonicalization investigated:         YES / PARTIAL / NO
Missing evidence stated rather than guessed:       YES / PARTIAL / NO
```

Notes:

```text
NOTES HERE
```

## CoreStory rule assessment

```text
CoreStory used before broad local exploration:     YES / PARTIAL / NO
Queries preserved commit-order objective:          YES / PARTIAL / NO
Cross-file relationship path identified:           YES / PARTIAL / NO
Targeted source used for validation:                YES / PARTIAL / NO
Causal evidence requirement preserved:             YES / PARTIAL / NO
Unsupported findings avoided:                      YES / PARTIAL / NO
```

Notes:

```text
NOTES HERE
```

## CoreStory narrowing assessment

```text
Complete candidate relationship path before broad grep:       YES / PARTIAL / NO
Dispatch/producers identified by CoreStory:                    YES / PARTIAL / NO
Commit/selection site identified by CoreStory:                 YES / PARTIAL / NO
Downstream consumer identified by CoreStory:                   YES / PARTIAL / NO
Broad repository discovery before path validation:             YES / PARTIAL / NO
Broad grep used only after CoreStory evidence was insufficient:YES / PARTIAL / NO / N/A
```

Notes:

```text
Describe specifically whether local work was primarily discovery or validation.
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

Do not define TC-004 until TC-003 has been reviewed.

```text
Recommended next change or next mechanism:
Reason:
```
