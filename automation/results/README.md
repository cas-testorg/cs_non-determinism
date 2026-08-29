# P01 Smoke-Test Run

Run ID: 20260828-185108
Model: gpt-5.4-high
Workspace trust: explicit --trust
Prompt transport: positional prompt after all CLI options
Discovery MCP approval: explicit --approve-mcps --force

Artifacts:
- P01.discovery.md â€” CoreStory-assisted discovery result
- P01.validation-prompt.md â€” exact independent-validation input
- P01.validation.md â€” local-source independent validation result
- mcp-before.txt â€” MCP state before discovery setup
- mcp-discovery.txt â€” MCP state after CoreStory was enabled for discovery
- mcp-validation.txt â€” MCP state after CoreStory was disabled for validation
- mcp-after.txt â€” MCP state after CoreStory was restored
- metadata.json â€” run metadata, including the pinned model, workspace trust, MCP approval/force settings, prompt transport, and absolute output path

Important: discovery explicitly approves MCP use and uses --force in the non-interactive Cursor session because --approve-mcps alone was observed to reject CoreStory MCP calls. Validation does not pass --approve-mcps or --force and runs after CoreStory has been disabled. All CLI options are placed before the positional prompt so dash-prefixed source identifiers in long validation input are not parsed as Cursor options. Review the MCP snapshots and Cursor session/transcript before treating the run as controlled evidence.
