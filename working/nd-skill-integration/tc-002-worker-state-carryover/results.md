# TC-002 Results — Worker-State Carryover / Boundary Reset

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
TC-002 started in a fresh Cursor chat:
Prior TC-002 conversation context in new chat:
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
Worker class/object:
File(s):
Symbol(s):
```

### Worker creation and reuse

```text
EVIDENCE HERE
```

### Parallel dispatch / variable worker assignment

```text
EVIDENCE HERE
```

### Mutable per-worker state

```text
EVIDENCE HERE
```

### Accessor / alias sweep

```text
EVIDENCE HERE
```

### Entry-side reset / initialization

```text
EVIDENCE HERE
```

### Exit-side reset / cleanup

```text
EVIDENCE HERE
```

### Reset / clear / flush semantics

```text
EVIDENCE HERE
```

### Downstream consumer / observable impact

```text
EVIDENCE HERE
```

### Missing evidence identified by agent

```text
EVIDENCE HERE
```

## Skill behavior assessment

```text
Worker-carryover reasoning applied:                YES / PARTIAL / NO
Worker reuse established:                          YES / PARTIAL / NO
Variable work-item assignment established:         YES / PARTIAL / NO
Entry-side boundary inspected:                     YES / PARTIAL / NO
Exit-side boundary inspected:                      YES / PARTIAL / NO
Reset semantics verified:                          YES / PARTIAL / NO
Accessors/aliases investigated where relevant:     YES / PARTIAL / NO / N/A
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
Queries preserved carryover mechanism/objective:   YES / PARTIAL / NO
Worker lifecycle relationships identified:         YES / PARTIAL / NO
Application relationships used to narrow source:   YES / PARTIAL / NO
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
Did CoreStory identify a candidate worker/lifecycle path before broad grep?  YES / PARTIAL / NO
Did CoreStory narrow member/accessor/reset validation?                       YES / PARTIAL / NO
Did Cursor still require broad product-wide lifecycle/reset searches?        YES / PARTIAL / NO
Did local proof work remain focused on CoreStory-supplied candidates?         YES / PARTIAL / NO
```

Notes:

```text
Describe specifically where CoreStory reduced or failed to reduce the breadth of local investigation.
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

This section is intentionally limited to observable Cursor behavior. Token metering, LiteLLM routing, JSONL request analysis, and token-efficiency metrics are out of scope for TC-002.

## Test verdict

```text
PASS / PARTIAL / FAIL / INCONCLUSIVE
```

### Rationale

```text
RATIONALE HERE
```

## Follow-up

Do not define TC-003 until TC-002 has been reviewed.

```text
Recommended next change or next mechanism:
Reason:
```
