# Customer A/B Results

This directory preserves customer-provided A/B evaluation artifacts and keeps the original run outputs separate from our analysis.

## Test 1 — With Subagents

The first customer A/B test allowed the repository-scale workflow to use subagents during discovery.

### Raw artifacts

- `Test-1-With-Subagents/raw/Without-MCP/` — original Synopsys workflow outputs without CoreStory MCP.
- `Test-1-With-Subagents/raw/With-MCP/` — original workflow outputs with CoreStory MCP enabled.

These files are preserved as received. They should be treated as source artifacts rather than edited analysis documents.

### Analysis

- `Test-1-With-Subagents/analysis/snps_core_nd_comparison.md` — customer-generated comparison/adjudication across both arms. It is stored under `analysis` because it evaluates both result sets and should not be interpreted as an output of the Without-MCP arm.

Additional CoreStory analysis can be added beside it without modifying the raw customer artifacts.

## Test 2 — Without Subagents

Results will be added separately once organized. Do not combine Test 1 and Test 2 artifacts because subagent/orchestration behavior is a material experimental difference.
