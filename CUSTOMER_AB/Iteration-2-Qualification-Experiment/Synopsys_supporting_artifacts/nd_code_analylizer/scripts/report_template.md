# Non-Determinism Analysis Report — {{module_slug}}

**Generated:** {{generated_at}}
**Module / Path:** `{{module_path}}`
**Search backend:** {{search_backend}}{{branch_suffix}}
**Patterns evaluated:** {{patterns_evaluated}}
**Files scanned (with hits):** {{files_with_hits}}
**Total findings:** {{total_findings}}

---

## Executive Summary

### Severity counts

| Severity | Count |
|---|---:|
| HIGH | {{count_high}} |
| MEDIUM | {{count_medium}} |
| LOW | {{count_low}} |
| INFO (file already adopts hySet/hyMap) | {{count_info}} |
| **Total** | **{{total_findings}}** |

### Findings by category

{{category_breakdown_table}}

### Top 5 hot files

{{top_files_table}}

---

## Critical Background: ID System

> See `references/id-system.md` for the full reference. Summary below.

```
+-------------------------+--------+--------------------------------------------------+
| Property                | Value  | Implication                                      |
+-------------------------+--------+--------------------------------------------------+
| getId() / getIdLong()   | O(1)   | Cheap - inline arithmetic only                   |
| getObjectType()         | O(1)   | Cheap - single lookup                            |
| getContextElement()     | O(1)   | Cheap - pointer retrieval                        |
| getFullName()           | O(d)   | EXPENSIVE - O(hierarchy depth) + string alloc    |
| getPathName()           | O(d)   | EXPENSIVE - O(hierarchy depth) + string alloc    |
+-------------------------+--------+--------------------------------------------------+
```

The gold-standard tools are:

- `ndmObjectHandleNS::compareObjPtr` — stable comparator for pointer keys.
- `dosContainer::keyHash` — context-chain-aware stable hasher.
- `ndmPtrMap<K,V>` — pointer-keyed map that uses the comparator above.
- `hySet<T, Cmp>` / `hyMap<K, V, Cmp>` (`util/export/hySet.h`,
  `util/export/hyMap.h`) — project-preferred deterministic AVL+linked-list
  container that **preserves insertion order** for iteration and is ~16%
  faster than `std::set::find()` on string keys. Use when iteration order
  must equal insertion order; use `compareObjPtr` instead when you need
  ID-stable ordering across runs with non-deterministic insertion sequence.

---

## Findings

{{findings_high_section}}

{{findings_medium_section}}

{{findings_low_section}}

{{findings_info_section}}

---

## Generic Fix Patterns

> See `references/fix-recipes.md` for the full set. Excerpts most relevant
> to this module:

{{fix_recipes_excerpt}}

---

## Coding Guidelines

### DO

1. Use `ndmPtrMap<K,V>` for pointer-keyed maps of ndm objects.
2. Use `std::map<T*, V, ndmObjectHandleNS::compareObjPtr>` for non-ndmPtr
   pointer-keyed maps.
3. Use `hySet<T*, hySetPtrCmp<T>>` / `hyMap<K*, V, hySetPtrCmp<K>>` when
   iteration must follow insertion order (the most common ND-prone case).
4. Use `std::mt19937` with a seed derived from input data.
5. Compare by `getIdLong()` + `getObjectType()` (both O(1)).
6. Hash by `getIdLong()` + `getObjectType()` via `boost::hash_combine`.
7. Sort `unordered_*` contents into a `std::vector` before iterating when
   order matters.

### DON'T

1. Use `std::set<T*>` / `std::map<T*, V>` with the default comparator.
2. Use `std::unordered_*<T*>` with default hash and expect stable iteration.
3. Use `std::random_shuffle` (deprecated).
4. Use `rand()` / `srand()` directly.
5. Use `getFullName()` / `getPathName()` for comparison (O(d) + alloc).
6. Assume IDs are globally unique — they can collide across types/contexts.

---

## Module-Specific Summary

{{module_specific_summary}}

---

## Methodology

This report was produced by the `nd-code-analyzer` skill in three stages:

1. **Mechanical scan (`scan_nd.py`):** loads
   `references/nd-patterns.yaml` and runs each pattern's regex over the
   target path using ripgrep (or mgrep for Perforce branches).
2. **LLM triage:** for each candidate, the LLM reads ±10 lines of
   surrounding context, confirms it's a real positive (filtering against
   `false_positive_hints_md`), and assigns a severity tailored to the call
   site.
3. **Tier 2 deep-read:** for parallel / FP-reduction / unordered-iteration
   patterns, the LLM follows data-flow to confirm the result actually
   affects output.
4. **Render:** this report is generated from a template.

To re-run with different filters:

```bash
~/.claude/skills/nd-code-analyzer/scripts/scan_nd.py \
    --path {{module_path}} \
    --min-severity HIGH \
    --tier 1 \
    --out candidates.json
```

To extend with a new ND pattern: add an entry to
`~/.claude/skills/nd-code-analyzer/references/nd-patterns.yaml` and the
narrative mirror in `nd-patterns.md`. No code changes required.
