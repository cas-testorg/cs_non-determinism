# Test 1 — Focused Disagreement Investigations

## Purpose

This directory contains focused follow-up investigations for representative disagreements from **Test 1 — With Subagents**.

The goal is not to rerun the complete non-determinism scan or to produce another aggregate defect report. The goal is to understand **why the Without-MCP and With-MCP workflows reached different outcomes** and where CoreStory application intelligence helps, fails, or never gets an opportunity to participate.

Each case is investigated independently before comparing it with the original A/B artifacts.

## Investigation model

For each case, use two layers:

### 1. Independent candidate investigation

Use the existing Agentic Bug Resolution workflow to investigate the reported candidate as a hypothesis.

Establish, where evidence permits:

1. source-level mechanism;
2. build inclusion;
3. production reachability;
4. runtime/configuration activation;
5. relevant shared state, ordering, or execution behavior;
6. deterministic neutralizers;
7. downstream propagation;
8. observable impact;
9. blast radius;
10. unresolved evidence and SME validation needs.

Do **not** give the independent investigation the customer comparison's final disposition. Prior ND reports, benchmark comparison reports, previous AI conclusions, and known-defect lists are not authoritative evidence for this stage.

Do not modify source code. Stop at the investigation checkpoint.

### 2. Workflow trace map

After the independent investigation is complete and preserved, compare it with the raw Test 1 outputs.

Trace the decision path:

```text
Reported source construct
        ↓
ND mechanism hypothesis
        ↓
Required supporting evidence
        ↓
Build inclusion
        ↓
Production reachability
        ↓
Runtime/configuration activation
        ↓
Propagation
        ↓
Neutralizer?
        ↓
Observable sink
        ↓
Disposition
```

For each step, record what the Without-MCP workflow established, what the With-MCP workflow established, what the independent investigation established, and where the paths diverged.

The purpose is to classify the disagreement as precisely as possible: discovery, mechanism interpretation, source/type resolution, build/reachability qualification, propagation/sink tracing, neutralization, evidence sufficiency, or orchestration.

## Cases

| Directory | Candidate | Test 1 pattern | Primary question |
|---|---|---|---|
| `01-soSolverUpdater/` | `ccd/skewopt/soSolverUpdater.cc:2100` | Without MCP found; With MCP missed | Why did the CoreStory-assisted workflow miss a serious data-race candidate? |
| `02-msDrivers-findDriverTerm/` | `mscts/drivers/msDrivers.cc:711` | With MCP found; Without MCP missed | What tracing/context allowed the With-MCP workflow to expose this candidate? |
| `03-ccdcgSolver-rand/` | `ccd/ctsccd/cgbased/ccdcgSolver.cc:501` | Without MCP promoted; With MCP dismissed | What evidence supported rejecting the suspicious RNG construct as ND? |
| `04-msuiGetPowerTaps/` | `mscts/msui/msuiGetPowerTaps.cc:66,879` | With MCP promoted; later source review rejected mechanism | Where did qualification stop before resolving the actual container/hash semantics? |

## Files in each case

Each case contains:

- `README.md` — case objective, starting hypothesis, and execution instructions.
- `investigation.md` — placeholder for the independent Agentic Bug Resolution result.
- `trace-map.md` — placeholder for the post-investigation A/B evidence-path comparison.

Keep the independent investigation frozen before completing the trace map.

## Evidence labels

Use these labels consistently:

- **Direct source evidence** — source, build, configuration, or other authoritative repository artifact.
- **CoreStory application evidence** — relationships/context retrieved through the CoreStory Intelligence Layer.
- **Reasoned inference** — conclusion derived from evidence but not directly demonstrated.
- **Unresolved** — evidence is insufficient; requires additional source, runtime evidence, or SME judgment.

## Claim boundary

These investigations are diagnostic. They are intended to explain Test 1 workflow behavior, not to redefine the customer's ground truth.

The customer-generated comparison remains a source-review artifact, and final defect accuracy remains subject to Synopsys SME validation and, where required, runtime reproduction.
