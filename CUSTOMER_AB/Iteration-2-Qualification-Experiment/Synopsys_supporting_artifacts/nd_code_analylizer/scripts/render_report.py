#!/depot/Python/Python-3.12.10/bin/python3
"""
render_report.py - Stage 5 (rendering) of the ND Code Analyzer.

Consumes triaged findings.json (after Stage 1 candidates + Stage 2–4 triage +
optional Stage 4b ownership) and emits markdown following report_template.md.

INPUT SCHEMA (findings.json):
    {
      "module_path": "ropt/flow/thermal",
      "module_slug": "ropt-flow-thermal",
      "search_backend": "rg" | "mgrep",
      "branch": "v" | null,
      "patterns_evaluated": 20,
      "findings": [
        {
          "pattern_id": "1.1",
          "pattern_name": "Pointer-based std::sort / std::stable_sort",
          "category": "sorting",
          "tier": 1,
          "severity": "HIGH",            # LLM-confirmed (may differ from default)
          "file": "ropt/flow/thermal/thermalViaDeletion.cc",
          "line": 384,
          "col": 5,
          "title": "Pointer-based std::sort on vias vector",
          "description_md": "...why it's ND in this site...",
          "snippet_ctx": "...code snippet from scan...",
          "fix_versions": [
            {"label": "Version A (Simple)", "code_md": "```cpp\\n...\\n```"},
            {"label": "Version B (Robust)", "code_md": "```cpp\\n...\\n```"},
            {"label": "Version C (Maximum safety)", "code_md": "```cpp\\n...\\n```"}
          ],
          "rationale_md": "Why this version recommended...",
          "false_positive_check_md": "Why this is not a false positive...",
          "ownership_md": "Optional Markdown (v1.2): populated via p4-code-ownership — depot, annotate CL, describe summary, notes."
        },
        ...
      ],
      "module_specific_summary_md": "Markdown narrative...",
      "fix_recipes_excerpt_md": "Markdown narrative..."
    }

USAGE:
    render_report.py --findings findings.json [--out report.md]
                     [--template report_template.md]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

SEVERITY_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "module"


def load_pattern_catalog(yaml_path: Path) -> dict[str, dict]:
    """Load the ND pattern catalog keyed by pattern id.

    The renderer uses this as a fallback so reports still show useful generic
    guidance when Stage 2-4 omitted site-specific fix text.
    """
    if yaml is None or not yaml_path.is_file():
        return {}
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

    patterns = {}
    for entry in data.get("patterns", []):
        pid = str(entry.get("id", "")).strip()
        if pid:
            patterns[pid] = entry
    return patterns


def make_snippet(file_path: Path, line_no: int, context: int) -> str:
    """Read ±context lines around line_no (1-based)."""
    try:
        lines = file_path.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
    except OSError:
        return ""

    lo = max(0, line_no - 1 - context)
    hi = min(len(lines), line_no + context)
    out: list[str] = []
    for i in range(lo, hi):
        marker = ">" if (i + 1) == line_no else " "
        out.append(f"{marker} {i + 1:5d} | {lines[i]}")
    return "\n".join(out)


def repo_relative_candidates(path_value: str) -> list[str]:
    """Return candidate repo-relative paths for file values from findings.json.

    Inputs may be absolute local paths, repo-relative paths, or depot-like
    paths. The last `nwtn/...` suffix is usually the usable local path.
    """
    raw = str(path_value or "").strip().replace("\\", "/")
    if not raw:
        return []

    out: list[str] = []

    def add(candidate: str) -> None:
        candidate = candidate.strip().lstrip("./")
        if candidate and candidate not in out:
            out.append(candidate)

    add(raw)

    anchored = "/" + raw.lstrip("/")
    nwtn_idx = anchored.rfind("/nwtn/")
    if nwtn_idx != -1:
        add(anchored[nwtn_idx + 1 :])

    for anchor in ("/src/", "/unit/"):
        idx = anchored.rfind(anchor)
        if idx != -1:
            add(anchored[idx + 1 :])

    return out


def resolve_source_file(
    file_value: str,
    module_path: str,
    source_root: Path,
) -> Path | None:
    """Best-effort mapping from finding file strings to a readable local file."""
    raw = str(file_value or "").strip()
    if not raw:
        return None

    direct = Path(raw)
    if direct.is_file():
        return direct

    module_rel = str(module_path or "").strip().strip("/")
    module_parent = str(Path(module_rel).parent) if module_rel else ""
    module_name = Path(module_rel).name if module_rel else ""

    rel_candidates: list[str] = []

    def add_rel(candidate: str) -> None:
        candidate = candidate.strip().strip("/")
        if candidate and candidate not in rel_candidates:
            rel_candidates.append(candidate)

    for candidate in repo_relative_candidates(raw):
        add_rel(candidate)

        if module_rel and not candidate.startswith(module_rel + "/"):
            if module_name and candidate.startswith(module_name + "/") and module_parent not in ("", "."):
                add_rel(f"{module_parent}/{candidate}")
            else:
                add_rel(f"{module_rel}/{candidate}")

    for rel in rel_candidates:
        resolved = source_root / rel
        if resolved.is_file():
            return resolved

    return None


def fallback_snippet(
    finding: dict,
    module_path: str,
    source_root: Path,
    context: int,
) -> str:
    """Return the best available code snippet for a finding."""
    snippet = str(finding.get("snippet_ctx") or "").rstrip()
    if snippet:
        return snippet

    line_no = int(finding.get("line", 0) or 0)
    match_text = str(finding.get("match_text") or "").strip()
    source_file = resolve_source_file(
        str(finding.get("file") or ""),
        module_path,
        source_root,
    )
    if source_file and line_no > 0:
        snippet = make_snippet(source_file, line_no, context)
        if snippet and (not match_text or match_text in snippet):
            return snippet

        if match_text:
            try:
                lines = source_file.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
            except OSError:
                lines = []

            for idx, line in enumerate(lines, 1):
                if match_text in line:
                    snippet = make_snippet(source_file, idx, context)
                    if snippet:
                        return snippet

    return match_text


def cleaned_fix_versions(finding: dict) -> list[dict]:
    """Normalize fix versions and drop empty entries."""
    cleaned: list[dict] = []
    for version in finding.get("fix_versions") or []:
        code_md = str(version.get("code_md") or "").rstrip()
        if not code_md:
            continue
        cleaned.append(
            {
                "label": version.get("label", "Version"),
                "code_md": code_md,
            }
        )
    return cleaned


def render_finding(
    idx: int,
    f: dict,
    pattern_catalog: dict[str, dict],
    module_path: str,
    source_root: Path,
    snippet_context: int,
) -> str:
    """Render one finding as a Markdown subsection."""
    parts: list[str] = []
    title = f.get("title") or f["pattern_name"]
    pattern_meta = pattern_catalog.get(str(f.get("pattern_id", "")).strip(), {})
    description_md = (
        str(f.get("description_md") or pattern_meta.get("description_md") or "").rstrip()
    )
    snippet_ctx = fallback_snippet(f, module_path, source_root, snippet_context)
    fix_versions = cleaned_fix_versions(f)
    fallback_fix_md = ""
    if not fix_versions:
        fallback_fix_md = str(pattern_meta.get("fix_template_md") or "").rstrip()

    parts.append(f"### Issue {f['pattern_id']}.{idx} — {title}")
    parts.append("")
    parts.append(
        f"- **File:** `{f['file']}:{f['line']}` "
        f"(col {f.get('col', 1)})"
    )
    parts.append(f"- **Pattern:** {f['pattern_id']} — {f['pattern_name']}")
    parts.append(f"- **Category:** {f['category']}")
    parts.append(f"- **Severity:** {f['severity']}  (default: {f.get('severity_default', f['severity'])})")
    parts.append(f"- **Tier:** {f.get('tier', 1)}")
    if f.get("file_adopts_hyset"):
        parts.append(
            "- **hySet adopter:** file already declares `hySet<>`/`hyMap<>` "
            "elsewhere &mdash; this site is flagged for migration audit, not "
            "as a fresh ND defect."
        )
    parts.append("")

    if description_md:
        parts.append("**Why this is non-deterministic:**")
        parts.append("")
        parts.append(description_md)
        parts.append("")

    if snippet_ctx:
        parts.append("**Current code:**")
        parts.append("")
        parts.append("```cpp")
        parts.append(snippet_ctx)
        parts.append("```")
        parts.append("")

    if fix_versions:
        parts.append("**Suggested fix:**")
        parts.append("")
        for v in fix_versions:
            label = v.get("label", "Version")
            parts.append(f"**{label}:**")
            parts.append("")
            code_md = v.get("code_md", "").rstrip()
            if not code_md.startswith("```"):
                code_md = f"```cpp\n{code_md}\n```"
            parts.append(code_md)
            parts.append("")
    elif fallback_fix_md:
        parts.append("**Suggested fix:**")
        parts.append("")
        parts.append(
            "_Site-specific fix variants were not provided; showing the generic "
            "pattern fix template instead._"
        )
        parts.append("")
        parts.append(fallback_fix_md)
        parts.append("")

    if f.get("rationale_md"):
        parts.append("**Why this fix:**")
        parts.append("")
        parts.append(f["rationale_md"].rstrip())
        parts.append("")

    if f.get("false_positive_check_md"):
        parts.append("**False-positive check:**")
        parts.append("")
        parts.append(f["false_positive_check_md"].rstrip())
        parts.append("")

    if f.get("ownership_md"):
        parts.append("**Code ownership (Perforce):**")
        parts.append("")
        parts.append(str(f["ownership_md"]).rstrip())
        parts.append("")

    parts.append("---")
    return "\n".join(parts)


def render_severity_section(
    severity: str,
    findings: list[dict],
    pattern_catalog: dict[str, dict],
    module_path: str,
    source_root: Path,
    snippet_context: int,
) -> str:
    """Build one of HIGH / MEDIUM / LOW sections."""
    sev_findings = [f for f in findings if f.get("severity", "").upper() == severity]
    if not sev_findings:
        return f"## {severity} Severity Issues\n\n_No {severity.lower()} severity findings._\n"

    out: list[str] = [f"## {severity} Severity Issues", ""]
    out.append(f"_{len(sev_findings)} finding(s)._")
    out.append("")

    grouped: dict[str, list[dict]] = defaultdict(list)
    for f in sev_findings:
        grouped[f["pattern_id"]].append(f)

    for pid in sorted(grouped.keys()):
        group = grouped[pid]
        first = group[0]
        out.append(f"### Pattern {pid} — {first['pattern_name']}  (×{len(group)})")
        out.append("")
        for i, f in enumerate(sorted(group, key=lambda x: (x["file"], x["line"])), 1):
            out.append(
                render_finding(
                    i,
                    f,
                    pattern_catalog,
                    module_path,
                    source_root,
                    snippet_context,
                )
            )
            out.append("")

    return "\n".join(out)


def render_category_table(findings: list[dict]) -> str:
    """Build the by-category breakdown table."""
    if not findings:
        return "_No findings._"

    by_cat: dict[str, Counter] = defaultdict(Counter)
    for f in findings:
        by_cat[f.get("category", "other")][f.get("severity", "LOW").upper()] += 1

    lines = [
        "| Category | HIGH | MEDIUM | LOW | INFO | Total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    cat_totals = []
    for cat, c in by_cat.items():
        total = c["HIGH"] + c["MEDIUM"] + c["LOW"] + c["INFO"]
        cat_totals.append((cat, c["HIGH"], c["MEDIUM"], c["LOW"], c["INFO"], total))
    cat_totals.sort(key=lambda x: (-x[5], x[0]))
    for cat, h, m, l, info, total in cat_totals:
        lines.append(f"| {cat} | {h} | {m} | {l} | {info} | {total} |")
    return "\n".join(lines)


def render_top_files(findings: list[dict], top_n: int = 5) -> str:
    if not findings:
        return "_No findings._"

    by_file: Counter = Counter()
    sev_by_file: dict[str, Counter] = defaultdict(Counter)
    for f in findings:
        by_file[f["file"]] += 1
        sev_by_file[f["file"]][f.get("severity", "LOW").upper()] += 1

    lines = [
        "| File | HIGH | MEDIUM | LOW | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for file, total in by_file.most_common(top_n):
        sev = sev_by_file[file]
        lines.append(
            f"| `{file}` | {sev['HIGH']} | {sev['MEDIUM']} | {sev['LOW']} | {total} |"
        )
    return "\n".join(lines)


def fill_template(template: str, mapping: dict) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Render the ND analysis report from triaged findings."
    )
    parser.add_argument("--findings", required=True, help="Path to findings.json")
    parser.add_argument("--out", default=None, help="Output report path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).parent / "report_template.md"),
        help="Path to report_template.md",
    )
    parser.add_argument(
        "--patterns",
        default=str(Path(__file__).parent.parent / "references" / "nd-patterns.yaml"),
        help="Path to nd-patterns.yaml for generic fallback fix text",
    )
    parser.add_argument(
        "--source-root",
        default=".",
        help="Repo/workspace root used to reconstruct missing snippets (default: cwd)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=2,
        help="Context lines when reconstructing missing snippets",
    )
    args = parser.parse_args(argv)

    findings_path = Path(args.findings)
    if not findings_path.is_file():
        sys.stderr.write(f"ERROR: findings file not found: {findings_path}\n")
        return 2

    template_path = Path(args.template)
    if not template_path.is_file():
        sys.stderr.write(f"ERROR: template not found: {template_path}\n")
        return 2

    data = json.loads(findings_path.read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    source_root = Path(args.source_root).resolve()
    pattern_catalog = load_pattern_catalog(Path(args.patterns))

    severity_counts = Counter(f.get("severity", "LOW").upper() for f in findings)
    files_with_hits = len({f["file"] for f in findings})

    module_path = data.get("module_path", "(unknown)")
    module_slug = data.get("module_slug") or slugify(module_path)
    branch = data.get("branch")
    branch_suffix = f" (branch: `{branch}`)" if branch else ""

    template = template_path.read_text(encoding="utf-8")

    mapping = {
        "module_slug": module_slug,
        "module_path": module_path,
        "search_backend": data.get("search_backend", "rg"),
        "branch_suffix": branch_suffix,
        "patterns_evaluated": data.get("patterns_evaluated", "N/A"),
        "files_with_hits": files_with_hits,
        "total_findings": len(findings),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "count_high": severity_counts["HIGH"],
        "count_medium": severity_counts["MEDIUM"],
        "count_low": severity_counts["LOW"],
        "count_info": severity_counts["INFO"],
        "category_breakdown_table": render_category_table(findings),
        "top_files_table": render_top_files(findings),
        "findings_high_section": render_severity_section(
            "HIGH", findings, pattern_catalog, module_path, source_root, args.context
        ),
        "findings_medium_section": render_severity_section(
            "MEDIUM", findings, pattern_catalog, module_path, source_root, args.context
        ),
        "findings_low_section": render_severity_section(
            "LOW", findings, pattern_catalog, module_path, source_root, args.context
        ),
        "findings_info_section": render_severity_section(
            "INFO", findings, pattern_catalog, module_path, source_root, args.context
        ),
        "fix_recipes_excerpt": data.get(
            "fix_recipes_excerpt_md",
            "_See `references/fix-recipes.md` for the canonical patterns._",
        ),
        "module_specific_summary": data.get(
            "module_specific_summary_md",
            "_LLM did not provide a module-specific summary._",
        ),
    }

    report = fill_template(template, mapping)

    out_path: Path
    if args.out:
        out_path = Path(args.out)
    else:
        date = datetime.date.today().strftime("%Y%m%d")
        digest = hashlib.sha1(module_path.encode()).hexdigest()[:8]
        out_path = (
            Path.home()
            / ".cursor"
            / "plans"
            / f"nd_analysis_{module_slug}_{date}_{digest}.md"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    sys.stderr.write(f"Wrote report ({len(findings)} findings) to {out_path}\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
