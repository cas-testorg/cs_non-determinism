# TC-001A Execution Prompt

Use this prompt unchanged for TC-001A and for the matching CoreStory discovery run.

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## Control rule

Do not add hints from TC-001, TSan, Coverity, prior CoreStory runs, known candidate files, race conditions, pointer defects, or other held-out evidence.

The matching CoreStory arm must use this exact prompt. CoreStory behavior should be introduced by enabling MCP + the governing rule, not by changing the user prompt.
