#!/usr/bin/env python3
"""extract-equations.py — formula-to-code traceability harvester for v-phase.

Pulls every math block from phase docs / report markdown and notebook markdown
cells, numbers them, and harvests candidate math-bearing code lines from the
repo. The model uses the paired output to build a formula -> file:line trace and
flag MISMATCH / MISSING / ORPHAN defects during the pre-flight step.

Read-only. Stdlib-first: notebook parsing prefers ``nbformat`` but degrades to a
plain JSON reader when it is not installed. Targets Python 3.11.

Usage:
    scripts/extract-equations.py [repo_path] [--doc PATH ...] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Directories we never descend into when scanning a repo.
PRUNE_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".venv", "venv",
    "__pycache__", "coverage", ".pytest_cache", ".mypy_cache",
}

MD_SUFFIXES = {".md", ".markdown"}
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}

# LaTeX / math block patterns, matched against joined markdown text.
DISPLAY_MATH = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
ALIGN_ENV = re.compile(
    r"\\begin\{(align\*?|equation\*?|gather\*?|aligned)\}(.+?)\\end\{\1\}",
    re.DOTALL,
)
INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)")

# Code lines that likely implement math worth tracing.
MATH_CALL = re.compile(
    r"\b(np|numpy|scipy|stats|statsmodels|sm|pd|pandas|math|torch|tf)\."
    r"[A-Za-z_][A-Za-z0-9_.]*\s*\("
)
STAT_KEYWORD = re.compile(
    r"\b(mean|median|std|var|variance|cov|corr|sqrt|exp|log|sum|dot|norm|"
    r"softmax|sigmoid|gradient|loss|ddof|degrees_of_freedom|quantile|"
    r"percentile|z_?score|t_?stat|p_?value|r_?squared|coef|beta|sigma|mu)\b",
    re.IGNORECASE,
)
# An operator-heavy assignment is a good math candidate even without a keyword.
OPERATOR_MATH = re.compile(r"=[^=].*[-+*/^%].*\b[A-Za-z_]\w*\b")


def is_pruned(path: Path) -> bool:
    return any(part in PRUNE_DIRS for part in path.parts)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def markdown_cells_from_ipynb(path: Path) -> list[str]:
    """Return markdown-cell source strings from a notebook.

    Prefers nbformat; falls back to a tolerant JSON read so the script still
    works in a bare Python 3.11 venv without the optional dependency.
    """
    try:
        import nbformat  # type: ignore

        nb = nbformat.read(str(path), as_version=4)
        return [c.source for c in nb.cells if c.cell_type == "markdown"]
    except ImportError:
        # nbformat not installed — install hint printed once by caller.
        pass
    except Exception:
        return []

    try:
        data = json.loads(read_text(path))
    except (json.JSONDecodeError, ValueError):
        return []
    cells = data.get("cells", []) if isinstance(data, dict) else []
    out: list[str] = []
    for cell in cells:
        if isinstance(cell, dict) and cell.get("cell_type") == "markdown":
            src = cell.get("source", "")
            out.append("".join(src) if isinstance(src, list) else str(src))
    return out


def extract_equations(text: str, source: str) -> list[dict]:
    """Extract display/align/inline math blocks from a markdown string."""
    found: list[dict] = []

    def add(kind: str, body: str) -> None:
        clean = " ".join(body.strip().split())
        if clean:
            found.append({"source": source, "kind": kind, "latex": clean})

    for m in ALIGN_ENV.finditer(text):
        add(f"env:{m.group(1)}", m.group(2))
    # Remove align envs before scanning $$ so we do not double-count.
    stripped = ALIGN_ENV.sub(" ", text)
    for m in DISPLAY_MATH.finditer(stripped):
        add("display", m.group(1))
    stripped2 = DISPLAY_MATH.sub(" ", stripped)
    for m in INLINE_MATH.finditer(stripped2):
        body = m.group(1)
        # Only keep inline math that carries an operator or known symbol —
        # skips prose that merely dollar-quotes a variable name.
        if re.search(r"[-+*/=^_\\]|\\[a-zA-Z]+", body):
            add("inline", body)
    return found


def harvest_code_lines(root: Path) -> list[dict]:
    """Return candidate math-bearing code lines across the repo."""
    hits: list[dict] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or is_pruned(path):
            continue
        if path.suffix not in CODE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        text = read_text(path)
        for lineno, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith(("#", "//", "*")):
                continue
            if len(line) > 400:
                continue
            if MATH_CALL.search(line) or (
                STAT_KEYWORD.search(line) and OPERATOR_MATH.search(line)
            ):
                hits.append(
                    {"file": str(rel), "line": lineno, "code": line[:200]}
                )
    return hits


def gather_docs(root: Path, explicit: list[str]) -> list[Path]:
    """Return the doc/notebook files to mine for equations."""
    if explicit:
        docs: list[Path] = []
        for item in explicit:
            p = Path(item)
            if not p.is_absolute():
                p = (root / item).resolve()
            if p.is_file():
                docs.append(p)
            else:
                print(f"# warning: doc not found: {item}", file=sys.stderr)
        return docs

    docs = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or is_pruned(path):
            continue
        if path.suffix in MD_SUFFIXES or path.suffix == ".ipynb":
            docs.append(path)
    return docs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Harvest equations from docs/notebooks and math-bearing "
        "code lines for formula-to-code traceability."
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="repo root")
    parser.add_argument(
        "--doc",
        action="append",
        default=[],
        dest="docs",
        help="explicit doc/notebook to mine (repeatable); default = scan repo",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit JSON instead of sectioned text"
    )
    args = parser.parse_args()

    root = Path(args.repo_path).resolve()
    if not root.is_dir():
        print(f"Not a directory: {args.repo_path}", file=sys.stderr)
        return 1

    doc_paths = gather_docs(root, args.docs)

    equations: list[dict] = []
    nbformat_missing = False
    eq_index = 0
    for doc in doc_paths:
        rel = doc.relative_to(root) if root in doc.parents or doc == root else doc
        if doc.suffix == ".ipynb":
            try:
                import nbformat  # noqa: F401
            except ImportError:
                nbformat_missing = True
            for cell in markdown_cells_from_ipynb(doc):
                for eq in extract_equations(cell, str(rel)):
                    eq_index += 1
                    eq["id"] = eq_index
                    equations.append(eq)
        elif doc.suffix in MD_SUFFIXES:
            for eq in extract_equations(read_text(doc), str(rel)):
                eq_index += 1
                eq["id"] = eq_index
                equations.append(eq)

    code_hits = harvest_code_lines(root)

    if args.json:
        print(
            json.dumps(
                {"equations": equations, "code_math_lines": code_hits},
                indent=2,
            )
        )
        return 0

    if nbformat_missing:
        print("# note: nbformat not installed — using tolerant JSON fallback "
              "for .ipynb (pip install nbformat for full fidelity)")
        print()

    print("=== equations extracted ===")
    if not equations:
        print("NONE — no LaTeX/math blocks found in scanned docs/notebooks")
    else:
        for eq in equations:
            print(f"[eq {eq['id']}] ({eq['kind']}) {eq['source']}")
            print(f"    {eq['latex']}")
    print()
    print(f"equation count: {len(equations)}")
    print()

    print("=== candidate math-bearing code lines ===")
    if not code_hits:
        print("NONE — no numpy/scipy/statsmodels or operator-heavy math lines found")
    else:
        for hit in code_hits:
            print(f"{hit['file']}:{hit['line']}: {hit['code']}")
    print()
    print(f"code line count: {len(code_hits)}")
    print()
    print("=== done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
