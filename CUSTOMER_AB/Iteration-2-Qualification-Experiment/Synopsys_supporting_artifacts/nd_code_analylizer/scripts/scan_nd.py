#!/depot/Python/Python-3.12.10/bin/python3
"""
scan_nd.py - Stage 1 (mechanical scan) of the ND Code Analyzer.

Requires Python 3.7+ (for `from __future__ import annotations`).
The shebang above points at the system Python 3.12 install which has
PyYAML available; if that path doesn't exist on your system, run:

    /path/to/python3.12 scan_nd.py ...


Loads references/nd-patterns.yaml, runs each pattern's regex against the
target path using ripgrep (or mgrep for Perforce branches), and emits a
JSON list of candidate hits for the LLM to triage in Stage 2.

OUTPUT SCHEMA (candidates.json):
    [
      {
        "pattern_id": "1.1",
        "pattern_name": "Pointer-based std::sort / std::stable_sort",
        "severity_default": "HIGH",
        "category": "sorting",
        "tier": 1,
        "file": "ropt/flow/thermal/thermalViaDeletion.cc",
        "line": 384,
        "col": 5,
        "match_text": "std::sort(vias.begin(), vias.end());",
        "snippet_ctx": "  // before line\n> std::sort(...)\n  // after line"
      },
      ...
    ]

USAGE:
    scan_nd.py --path /path/to/module [options]

OPTIONS:
    --path PATH                Local directory or P4 path to scan (required)
    --patterns FILE            Path to nd-patterns.yaml (default: ../references/nd-patterns.yaml)
    --category CAT[,CAT...]    Restrict to one or more categories
                               (sorting|container|hash|random|timing|naming|
                                iteration|arithmetic|env|parallel|filesystem)
    --min-severity LEVEL       LOW|MEDIUM|HIGH (default: LOW = include all)
    --tier {1,2,all}           Restrict by tier (default: all)
    --mgrep                    Use mgrep instead of rg (for Perforce branches)
    --branch BRANCH            Branch name when using --mgrep (e.g. v, main, x)
    --out FILE                 Output JSON path (default: candidates.json in cwd)
    --max-per-pattern N        Cap matches per pattern (default: 500)
    --context N                Lines of context around each match (default: 2)
    --rg PATH                  Explicit ripgrep path (auto-detected if omitted)
    -v / --verbose             Print scan progress to stderr

EXIT CODES:
    0  success (regardless of how many findings)
    2  scanner failure (missing rg, bad YAML, unreadable path)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML not installed. Try: /depot/Python/Python-3.12.10/bin/pip install pyyaml\n"
        "Or run scan_nd.py with: /depot/Python/Python-3.12.10/bin/python3 scan_nd.py ...\n"
    )
    sys.exit(2)


SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


@dataclass
class Pattern:
    id: str
    name: str
    severity_default: str
    category: str
    tier: int
    regex: list[str]
    file_globs: list[str]
    description_md: str
    fix_template_md: str
    false_positive_hints_md: str
    example_from_plan: str = ""


@dataclass
class Candidate:
    pattern_id: str
    pattern_name: str
    severity_default: str
    category: str
    tier: int
    file: str
    line: int
    col: int
    match_text: str
    snippet_ctx: str


def find_ripgrep(explicit: str | None = None) -> str:
    """Locate the ripgrep binary, preferring an explicit path then PATH then
    the bundled Cursor / VSCode copies."""
    if explicit:
        if shutil.which(explicit):
            return explicit
        if Path(explicit).is_file() and os.access(explicit, os.X_OK):
            return explicit
        raise FileNotFoundError(f"--rg path not executable: {explicit}")

    found = shutil.which("rg")
    if found:
        return found

    candidates: list[Path] = []

    home_user = Path.home().name
    search_roots = [
        Path.home() / ".cursor" / "cursor-server" / "bin",
        Path.home() / ".vscode-server" / "bin",
    ]
    slowfs_root = Path("/slowfs")
    if slowfs_root.is_dir():
        try:
            for entry in slowfs_root.iterdir():
                potential = entry / home_user / ".cursor" / "cursor-server" / "bin"
                if potential.is_dir():
                    search_roots.append(potential)
        except OSError:
            pass

    env_path = os.environ.get("PATH", "")
    for p in env_path.split(os.pathsep):
        p_path = Path(p)
        if "cursor-server" in str(p_path) or "vscode-server" in str(p_path):
            parent = p_path
            while parent != parent.parent:
                if parent.name == "bin" and parent.parent.name == "cursor-server":
                    search_roots.append(parent)
                    break
                if parent.name == "bin" and parent.parent.name == "vscode-server":
                    search_roots.append(parent)
                    break
                parent = parent.parent

    glob_patterns = [
        "*/node_modules/@vscode/ripgrep/bin/rg",
        "*/*/node_modules/@vscode/ripgrep/bin/rg",
    ]
    for base in search_roots:
        if base.is_dir():
            for gp in glob_patterns:
                candidates.extend(base.glob(gp))

    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)

    raise FileNotFoundError(
        "ripgrep (rg) not found in PATH or bundled Cursor/VSCode locations. "
        "Install ripgrep or pass --rg /full/path/to/rg."
    )


def load_patterns(yaml_path: Path) -> list[Pattern]:
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "patterns" not in data:
        raise ValueError(f"{yaml_path} does not contain a 'patterns' key")

    out: list[Pattern] = []
    for entry in data["patterns"]:
        out.append(
            Pattern(
                id=str(entry["id"]),
                name=entry["name"],
                severity_default=entry.get("severity_default", "MEDIUM"),
                category=entry.get("category", "other"),
                tier=int(entry.get("tier", 1)),
                regex=list(entry.get("regex", [])),
                file_globs=list(entry.get("file_globs", ["*.cc", "*.cpp", "*.h", "*.hh"])),
                description_md=entry.get("description_md", ""),
                fix_template_md=entry.get("fix_template_md", ""),
                false_positive_hints_md=entry.get("false_positive_hints_md", ""),
                example_from_plan=entry.get("example_from_plan", "") or "",
            )
        )
    return out


def filter_patterns(
    patterns: list[Pattern],
    categories: set[str] | None,
    min_severity: str,
    tier: str,
) -> list[Pattern]:
    min_rank = SEVERITY_ORDER.get(min_severity.upper(), 0)
    out: list[Pattern] = []
    for p in patterns:
        if categories and p.category not in categories:
            continue
        if SEVERITY_ORDER.get(p.severity_default.upper(), 0) < min_rank:
            continue
        if tier != "all" and str(p.tier) != tier:
            continue
        out.append(p)
    return out


def make_snippet(file_path: Path, line_no: int, context: int) -> str:
    """Read ±context lines around line_no (1-based) and return a fenced
    snippet with a `>` marker on the matched line."""
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


def run_rg(
    rg: str,
    pattern: Pattern,
    path: str,
    verbose: bool,
) -> list[tuple[str, int, int, str]]:
    """Run ripgrep with --json for one pattern. Returns list of
    (file, line, col, match_text)."""
    hits: list[tuple[str, int, int, str]] = []
    for regex in pattern.regex:
        cmd = [rg, "--json", "--regexp", regex]
        for glob in pattern.file_globs:
            cmd.extend(["--glob", glob])
        cmd.append(path)

        if verbose:
            sys.stderr.write(f"  $ {' '.join(cmd)}\n")

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
        except OSError as e:
            sys.stderr.write(f"WARN: rg failed for pattern {pattern.id}: {e}\n")
            continue

        if proc.returncode not in (0, 1):
            sys.stderr.write(
                f"WARN: rg returned {proc.returncode} for pattern {pattern.id}\n"
                f"      stderr: {proc.stderr.strip()[:200]}\n"
            )
            continue

        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            if evt.get("type") != "match":
                continue
            d = evt["data"]
            file_obj = d.get("path", {})
            file_path = file_obj.get("text") or file_obj.get("bytes") or ""
            line_no = int(d.get("line_number", 0))
            submatches = d.get("submatches", [])
            match_text = (
                d.get("lines", {}).get("text", "").rstrip("\n")
                or (submatches[0]["match"]["text"] if submatches else "")
            )
            col = int(submatches[0].get("start", 0)) + 1 if submatches else 1
            hits.append((file_path, line_no, col, match_text))
    return hits


def _collapse_globs_for_mgrep(globs: list[str]) -> list[str]:
    """Workaround for mgrep server: passing many `--glob *.cc --glob *.h ...`
    flags intermittently returns rc=1 with empty stdout/stderr. Collapse
    extension-style globs of the form ``*.<ext>`` into a single
    ``*.{ext1,ext2,...}`` brace-expansion glob, which is reliable.
    Non-extension globs are passed through verbatim."""
    extensions: list[str] = []
    other: list[str] = []
    for g in globs:
        # Only collapse the simple `*.<ext>` shape.
        if g.startswith("*.") and "/" not in g and "{" not in g and "[" not in g:
            ext = g[2:]
            if ext and all(ch.isalnum() or ch in "+-_" for ch in ext):
                extensions.append(ext)
                continue
        other.append(g)
    out: list[str] = []
    if len(extensions) == 1:
        out.append(f"*.{extensions[0]}")
    elif len(extensions) > 1:
        out.append("*.{" + ",".join(extensions) + "}")
    out.extend(other)
    return out


def run_mgrep(
    pattern: Pattern,
    p4_path: str,
    branch: str | None,
    verbose: bool,
) -> list[tuple[str, int, int, str]]:
    """Run mgrep --json for one pattern across a Perforce branch."""
    mgrep = "/remote/u/binghui/bin/mgrep"
    if not Path(mgrep).is_file():
        raise FileNotFoundError(f"mgrep not found at {mgrep}")

    collapsed_globs = _collapse_globs_for_mgrep(pattern.file_globs)

    hits: list[tuple[str, int, int, str]] = []
    for regex in pattern.regex:
        cmd = [mgrep, "--json", regex]
        if branch:
            cmd.extend(["-b", branch])
        for glob in collapsed_globs:
            cmd.extend(["--glob", glob])
        if p4_path:
            cmd.extend(["-G", p4_path])

        if verbose:
            sys.stderr.write(f"  $ {' '.join(cmd)}\n")

        proc = None
        # mgrep occasionally returns rc=1 with empty output on transient
        # backend hiccups; retry up to 3 times before giving up.
        for attempt in range(3):
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, check=False
                )
            except OSError as e:
                sys.stderr.write(
                    f"WARN: mgrep failed for pattern {pattern.id}: {e}\n"
                )
                proc = None
                break
            if proc.returncode == 0 or len(proc.stdout) > 0:
                break
            if verbose:
                sys.stderr.write(
                    f"  (retry {attempt + 1}/3 for pattern {pattern.id}: "
                    f"rc={proc.returncode})\n"
                )
        if proc is None:
            continue
        if proc.returncode != 0 and not proc.stdout:
            sys.stderr.write(
                f"WARN: mgrep gave up for pattern {pattern.id} after retries "
                f"(rc={proc.returncode})\n"
            )
            continue

        for line in proc.stdout.splitlines():
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            if evt.get("type") != "match":
                continue
            d = evt["data"]
            file_obj = d.get("path", {})
            file_path = file_obj.get("text") or file_obj.get("bytes") or ""
            line_no = int(d.get("line_number", 0))
            submatches = d.get("submatches", [])
            match_text = (
                d.get("lines", {}).get("text", "").rstrip("\n")
                or (submatches[0]["match"]["text"] if submatches else "")
            )
            col = int(submatches[0].get("start", 0)) + 1 if submatches else 1
            hits.append((file_path, line_no, col, match_text))
    return hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Scan a module for non-determinism candidates."
    )
    parser.add_argument("--path", required=True, help="Local dir or P4 path to scan")
    parser.add_argument(
        "--patterns",
        default=str(Path(__file__).parent.parent / "references" / "nd-patterns.yaml"),
        help="Path to nd-patterns.yaml",
    )
    parser.add_argument("--category", default="", help="Comma-separated category filter")
    parser.add_argument("--min-severity", default="LOW", help="LOW|MEDIUM|HIGH")
    parser.add_argument("--tier", default="all", choices=["1", "2", "all"])
    parser.add_argument("--mgrep", action="store_true", help="Use mgrep instead of rg")
    parser.add_argument("--branch", default=None, help="P4 branch when using --mgrep")
    parser.add_argument("--out", default="candidates.json")
    parser.add_argument("--max-per-pattern", type=int, default=500)
    parser.add_argument("--context", type=int, default=2)
    parser.add_argument("--rg", default=None, help="Explicit ripgrep path")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    yaml_path = Path(args.patterns)
    if not yaml_path.is_file():
        sys.stderr.write(f"ERROR: pattern catalog not found: {yaml_path}\n")
        return 2

    try:
        patterns = load_patterns(yaml_path)
    except (yaml.YAMLError, ValueError) as e:
        sys.stderr.write(f"ERROR: bad pattern catalog: {e}\n")
        return 2

    categories: set[str] | None = None
    if args.category.strip():
        categories = {c.strip() for c in args.category.split(",") if c.strip()}

    selected = filter_patterns(patterns, categories, args.min_severity, args.tier)
    if not selected:
        sys.stderr.write("ERROR: no patterns match the filters\n")
        return 2

    if args.verbose:
        sys.stderr.write(
            f"Loaded {len(patterns)} patterns; {len(selected)} after filtering.\n"
        )

    rg_path: str | None = None
    if not args.mgrep:
        try:
            rg_path = find_ripgrep(args.rg)
        except FileNotFoundError as e:
            sys.stderr.write(f"ERROR: {e}\n")
            return 2
        if args.verbose:
            sys.stderr.write(f"Using ripgrep at: {rg_path}\n")

    candidates: list[Candidate] = []
    for p in selected:
        if args.verbose:
            sys.stderr.write(f"[{p.id}] {p.name}\n")

        if args.mgrep:
            raw = run_mgrep(p, args.path, args.branch, args.verbose)
        else:
            assert rg_path is not None
            raw = run_rg(rg_path, p, args.path, args.verbose)

        # Dedup per-pattern by (file, line) so multiple alternative regexes in
        # the same pattern entry don't double-count the same match site.
        seen_keys: set[tuple[str, int]] = set()
        deduped: list[tuple[str, int, int, str]] = []
        for hit in raw:
            key = (hit[0], hit[1])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(hit)
        raw = deduped

        if len(raw) > args.max_per_pattern:
            sys.stderr.write(
                f"  capping {p.id} hits at {args.max_per_pattern} (raw={len(raw)})\n"
            )
            raw = raw[: args.max_per_pattern]

        for file_path, line_no, col, match_text in raw:
            snippet = ""
            if not args.mgrep:
                try:
                    snippet = make_snippet(Path(file_path), line_no, args.context)
                except Exception:
                    snippet = ""
            candidates.append(
                Candidate(
                    pattern_id=p.id,
                    pattern_name=p.name,
                    severity_default=p.severity_default,
                    category=p.category,
                    tier=p.tier,
                    file=file_path,
                    line=line_no,
                    col=col,
                    match_text=match_text,
                    snippet_ctx=snippet,
                )
            )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            [
                {
                    "pattern_id": c.pattern_id,
                    "pattern_name": c.pattern_name,
                    "severity_default": c.severity_default,
                    "category": c.category,
                    "tier": c.tier,
                    "file": c.file,
                    "line": c.line,
                    "col": c.col,
                    "match_text": c.match_text,
                    "snippet_ctx": c.snippet_ctx,
                }
                for c in candidates
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    sys.stderr.write(
        f"Wrote {len(candidates)} candidates across {len(selected)} patterns to {out_path}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
