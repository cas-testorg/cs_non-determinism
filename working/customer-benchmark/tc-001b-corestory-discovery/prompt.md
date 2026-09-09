# TC-001B Execution Prompt

Use this prompt unchanged from TC-001A.

```text
/nd-code-analyzer scan C:\Users\carys\cts for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## Control rule

Do not mention CoreStory in the user prompt. The only intended change from TC-001A is that CoreStory MCP and the governing `code-analysis-v2.mdc` rule are enabled.

Do not add hints from TC-001, TC-001A, TSan, Coverity, prior CoreStory runs, known candidate files, race conditions, pointer defects, or other held-out evidence.
