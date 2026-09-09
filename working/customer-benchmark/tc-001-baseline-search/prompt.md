# TC-001 Execution Prompt

Replace only `<CTS_SCOPE>` with the exact agreed CTS source path/module. Use the resulting prompt unchanged for the matching CoreStory discovery arm.

```text
/nd-code-analyzer scan <CTS_SCOPE> for non-determinism, only HIGH and MEDIUM issues, and generate a shareable markdown report
```

## Prompt rationale

This intentionally follows the customer's documented `nd-code-analyzer` example-prompt style rather than introducing a CoreStory-specific detection prompt.

It is deliberately broad across nondeterminism mechanisms. Do not narrow the prompt to known TSan/Coverity defect classes, specific files, race conditions, pointer defects, sorting/container patterns, or any held-out ground-truth locations.

The same resolved prompt must be used for the baseline and CoreStory discovery runs.
