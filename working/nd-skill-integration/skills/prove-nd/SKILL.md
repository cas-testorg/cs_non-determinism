---
name: prove-nd
description: Use when user asks to prove ND or deep dive ND or analyzing non-determinism dashboard suspects, checking whether an ND row is real, false positive, latent-only, dead, unused, or gated, or writing a detailed report with C++ downstream usage, app-option controls, and nwtn/unit regression setter evidence.
---

# Prove ND Details

## Overview

Use this skill to turn ND dashboard suspects into a proof report. The goal is
not to restate the scanner result; the goal is to prove whether downstream C++
code can observe nondeterministic behavior, or explain why the row is not a
real issue.

## Hard Rules

- Do not use sub-tasks or sub-agents for this task.
- Preserve dashboard/source order in the summary table and issue sections.
- Ignore pure `getenv` issues for ND by definition is for runs with same ENV settings. Mark them as Ignored.
- Do not call a row real unless a downstream C++ consumer can observe it.
- Do not rely on `purecov` or Coverity annotations/directives as proof that
  code is dead, unreachable, safe, or compiled out. Treat them as analysis
  hints only unless they are part of an actual compile-time control such as
  `#if`, `#ifdef`, a build macro, or generated-source exclusion.
- Prefer reference-client source for files outside local `DEVROOTS`.
- Use ASCII-only Markdown for the report; verify with `check-ascii` when
  available.

## Workflow

1. **Bootstrap workspace context.**
   Run `viewtool info` from the workspace root, read `.synmake`, and record
   the view root, reference root, reference view, and `DEVROOTS`. If the
   suspect module is outside `DEVROOTS`, read source from the reference root
   or remote index.

2. **Parse the dashboard.**
   Read the HTML and, when available, the dashboard data JSON or generated
   module report. Create an ordered issue list with dashboard ID, source
   file:line, pattern, title, owner/CL metadata, and the scanner summary.

3. **For each issue, prove or dismiss.**
   - Read the suspect source around the flagged line.
   - Resolve the real C++ type of the iterated/indexed/sorted object.
   - Use `clangd_query.py` for semantic definitions/references when
     available; use `mgrep-agent` for cross-module callers, Tcl setters,
     unit regressions, and broad symbol searches.
   - Trace upstream reachability from user command, flow entry point, or C++
     caller to the suspect code.
   - Trace downstream consumers to a concrete observable sink: database
     mutation, `set*`/`remove*`/`reorder*`, algorithmic tie-break, report or
     Tcl recording order, message order, persisted output, QoR choice, or
     non-associative floating reduction.
   - Look for neutralizers: deterministic sort, stable comparator, lookup-only
     use, membership-only use, set union, vector iteration, allocator indexing,
     inactive `#if 0`, mirror headers, or debug-only paths.
   - When checking dead/unused claims, use compile-time controls, build
     inclusion, call graph reachability, and feature gates. Do not dismiss
     based only on `purecov` comments or Coverity suppression annotations.

4. **Classify realness.**
   Use one of these labels:
   - `Real`: downstream C++ can observe the nondeterministic order/value.
   - `Latent-only`: the suspect exists, but current consumers are lookup-only,
     membership-only, or otherwise order-insensitive.
   - `False positive`: the scanner matched the wrong type or construct.
   - `Safe adopter`: code already uses a deterministic comparator/container.
   - `Mirror duplicate`: include/export/module mirror of another row.
   - `Neutralized`: nondeterminism is canonicalized before consumption.
   - `Dead/unused`: inactive preprocessor block, no reachable caller, or not
     compiled.
   - `Unresolved`: evidence is insufficient; state exactly what is missing.

5. **Trace controls and setters.**
   For each real or potentially real issue:
   - Identify user commands, flow modes, C++ guards, and data conditions.
   - Query app-option metadata with `/remote/u/binghui/bin/icc2query -a`.
     Record defaults and whether the option is hidden, unlisted, or basic when
     visible.
   - Search C++ source for forced app-option values or code-level setters.
   - Search `nwtn/unit` regressions for Tcl setters and command flags.
   - Distinguish "test exercises this path" from "production code forces this
     value".

6. **Add attribution and fix direction.**
   Use dashboard owner/CL metadata when available. For high-confidence fixes
   or when ownership matters, resolve Perforce attribution with annotate and
   describe. Fix directions should be specific to the proven sink, not generic
   "sort it" advice.

7. **Make fixes performance-aware.**
   Fusion Compiler code is algorithm-heavy and data-structure-heavy; many ND
   suspects sit in paths executed millions or billions of times. Do not
   recommend a deterministic fix that blindly replaces hash containers with
   ordered maps, adds per-iteration sorting, or copies large containers in
   inner loops without discussing cost. Prefer fixes that preserve existing
   asymptotic behavior: sort once at the boundary where order becomes
   observable, keep fast membership structures and add a separate stable key
   vector for iteration, cache deterministic order when inputs are unchanged,
   or use existing stable IDs/comparators only where iteration/output requires
   them. Call out expected cost, data size, hot-loop risk, and whether
   performance validation is needed.

## Report Format

Write the report as `<module>_nd_details.md` in the workspace root unless the
user requests another path.

Use this structure:

```markdown
# <Module> Non-Determinism Details

Source dashboard: `<dashboard path>`

Analysis context:

- `viewtool info` summary: view, reference view, reference root.
- `.synmake` / `DEVROOTS` summary and source root used.
- Tools used: `mgrep-agent`, `clangd_query.py`, `icc2query`, direct source
  reads.
- Scope notes: ignored `getenv`, sparse-client limitations, failed navigation
  attempts if any.

## Summary Table

| Issue | Real? | Triggering controls / app options | Short summary |
|---|---|---|---|
| #1 `<dashboard-id>` | Real/Latent-only/... | Commands, flow gates, app options and defaults, data conditions | One-sentence conclusion |

## Issue #N: <specific title>

Dashboard ID: `<id>`
Location: `<source path>:<line>`

### Verdict

State realness in one paragraph. Say "real" only if the downstream proof is
complete.

### Evidence

Show concise source excerpts or prose evidence for the suspect construct and
its immediate use.

### Downstream Visibility

Trace the C++ caller/callee path to the observable sink. Name the exact
mutation/output/tie-break/reduction that observes nondeterminism.

### Controls / Gating

List commands, flows, app options with defaults, C++ guards, and data
conditions required to trigger or avoid the issue.

### Code / Regression Setting Pass

Summarize source and `nwtn/unit` searches for relevant option setters and
command flags.

### Attribution

Owner/CL or Perforce attribution. If unavailable, state what remains to be
resolved.

### Fix Direction

Give a sink-specific fix: stable comparator, sort key, preserved source order,
vector snapshot, deterministic reduction, or option/control-specific follow-up.
Include performance notes: whether the code is on a hot path, whether the fix
adds sorting/copying/allocation, how to keep lookup fast, and what benchmark or
flow should validate runtime/QoR impact.

## Verification Notes

- Commands/tools used.
- Source roots used.
- ASCII check result.
- Any limitations or unresolved evidence.
```

## Common Mistakes

- Marking pointer-keyed declarations real without proving iteration reaches a
  sink.
- Treating `operator[]` as map insertion without resolving whether the object
  is a vector, allocator, array, map, or unordered map.
- Missing app options that default off and make the issue test-only unless
  enabled.
- Reporting tests that set an option without noting that production defaults
  keep it disabled.
- Losing dashboard order while regrouping by severity.
- Omitting false positives from the summary table; the table must let the user
  see every dashboard row.
- Treating `purecov` or Coverity annotations as if they were compile-time
  guards. They are not reachability proof unless backed by real preprocessor or
  build controls.
- Suggesting `std::map` or `sort every time` as a default fix in hot code.
  FC inner loops can run billions of operations; preserve hash lookup and move
  canonicalization to the smallest observable boundary when possible.
