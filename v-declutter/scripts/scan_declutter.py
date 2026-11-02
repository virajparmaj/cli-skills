#!/usr/bin/env python3
"""
scan_declutter.py - Deterministic codebase declutter and structure audit scanner.

Scans a repository to identify:
1. Single-child and redundant directory nesting (e.g., deep nesting with 1 child).
2. Stuttering naming patterns (e.g., Foo/FooBar.tsx, components/Button/Button.tsx).
3. Historical patch sprawl, dated files, and fragmented seed files.
4. Pass-through wrapper layers (minimal files forwarding directly to a child).
5. Duplicate file names across directories (repetitive utils/constants).
6. Potential orphan / unreferenced source files.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", "out", ".next", ".nuxt",
    ".turbo", ".cache", ".venv", "venv", "env", "__pycache__",
    ".pytest_cache", "coverage", ".idea", ".vscode", "target", "vendor",
    ".system_generated", "brain"
}

IGNORE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".lock"
}

ENTRYPOINT_NAMES = {
    "index", "main", "app", "root", "entry", "vite.config", "next.config",
    "tailwind.config", "setup", "conftest", "__init__", "skill", "readme",
    "claude", "gemini", "license", "package", "tsconfig"
}

PATCH_DATE_REGEX = re.compile(
    r"(?:^|[._\-/])(patch|temp|bak|backup|old|copy|draft|legacy|_v\d+|\bv\d+\b|\d{4}[-_]\d{2}[-_]\d{2}|seed[_\-]?\d+)(?:[._\-/]|$)",
    re.IGNORECASE
)

WRAPPER_JSX_REGEX = re.compile(
    r"return\s*\(?\s*<([A-Z][A-Za-z0-9]+)\s*(?:\{\.\.\.props\})?\s*\/>\s*\)?",
    re.MULTILINE
)


def is_ignored(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS or part.startswith("."):
            if part not in {".", "./"}:
                return True
    return False


def collect_files_and_dirs(repo_root: Path):
    all_files = []
    all_dirs = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        current_dir = Path(root)
        if is_ignored(current_dir.relative_to(repo_root)):
            continue

        rel_dir = current_dir.relative_to(repo_root)
        if rel_dir != Path("."):
            all_dirs.append(rel_dir)

        for f in files:
            file_path = current_dir / f
            rel_file = file_path.relative_to(repo_root)
            if not is_ignored(rel_file) and file_path.suffix not in IGNORE_EXTS:
                all_files.append(rel_file)

    return all_dirs, all_files


def audit_single_child_dirs(repo_root: Path, all_dirs):
    findings = []
    for d in all_dirs:
        abs_d = repo_root / d
        try:
            entries = [
                e for e in abs_d.iterdir()
                if e.name not in IGNORE_DIRS and not e.name.startswith(".")
            ]
            if len(entries) == 1:
                child = entries[0]
                findings.append({
                    "dir": str(d),
                    "child": str(child.relative_to(repo_root)),
                    "is_dir": child.is_dir()
                })
        except (PermissionError, FileNotFoundError):
            continue
    return findings


def audit_stuttering_paths(all_files):
    findings = []
    for f in all_files:
        parent_name = f.parent.name
        stem = f.stem
        if not parent_name or parent_name in {".", "src", "app", "lib", "components"}:
            continue

        # e.g., components/companies/CompaniesList.tsx or Button/Button.tsx
        p_lower = parent_name.lower().rstrip("s")
        s_lower = stem.lower()
        if p_lower and (s_lower == p_lower or s_lower.startswith(p_lower) or p_lower in s_lower):
            findings.append({
                "file": str(f),
                "parent_dir": parent_name,
                "stem": stem
            })
    return findings


def audit_patch_sprawl(all_files):
    findings = []
    for f in all_files:
        filename = f.name
        match = PATCH_DATE_REGEX.search(filename)
        if match:
            # Skip legitimate migration files if expected (e.g., supabase/migrations/2024...)
            is_supabase_migration = "migrations" in f.parts and "supabase" in f.parts
            findings.append({
                "file": str(f),
                "matched_pattern": match.group(0),
                "is_migration": is_supabase_migration
            })
    return findings


def audit_pass_through_wrappers(repo_root: Path, all_files):
    findings = []
    code_exts = {".tsx", ".jsx", ".ts", ".js", ".py"}
    for f in all_files:
        if f.suffix not in code_exts:
            continue

        abs_path = repo_root / f
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as fp:
                lines = fp.readlines()
        except Exception:
            continue

        if 0 < len(lines) <= 35:
            content = "".join(lines)
            # Detect JSX/TSX pass-through wrappers
            if f.suffix in {".tsx", ".jsx"}:
                match = WRAPPER_JSX_REGEX.search(content)
                if match:
                    findings.append({
                        "file": str(f),
                        "lines": len(lines),
                        "wrapped_component": match.group(1),
                        "reason": f"Minimal component wrapper around <{match.group(1)} />"
                    })
    return findings


def audit_duplicate_filenames(all_files):
    by_name = defaultdict(list)
    for f in all_files:
        if f.stem.lower() not in ENTRYPOINT_NAMES and len(f.stem) > 2:
            by_name[f.name].append(str(f))

    duplicates = {
        name: paths for name, paths in by_name.items()
        if len(paths) > 1
    }
    return duplicates


def audit_potential_orphans(repo_root: Path, all_files):
    source_files = [
        f for f in all_files
        if f.suffix in {".ts", ".tsx", ".js", ".jsx", ".py"}
        and f.stem.lower() not in ENTRYPOINT_NAMES
    ]

    # Pre-read source files content for reference checks
    corpus = []
    for f in all_files:
        if f.suffix in {".ts", ".tsx", ".js", ".jsx", ".py", ".json", ".html", ".md"}:
            try:
                with open(repo_root / f, "r", encoding="utf-8", errors="ignore") as fp:
                    corpus.append((str(f), fp.read()))
            except Exception:
                continue

    orphans = []
    for s in source_files:
        stem = s.stem
        # Check if stem is mentioned in any other file
        s_str = str(s)
        ref_count = 0
        for path_str, content in corpus:
            if path_str == s_str:
                continue
            if stem in content:
                ref_count += 1
                break

        if ref_count == 0:
            orphans.append(str(s))

    return orphans


def main():
    parser = argparse.ArgumentParser(description="Audit codebase structure and declutter opportunities.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    if not repo_root.is_dir():
        sys.stderr.write(f"Error: {repo_root} is not a valid directory\n")
        sys.exit(1)

    all_dirs, all_files = collect_files_and_dirs(repo_root)

    single_child = audit_single_child_dirs(repo_root, all_dirs)
    stuttering = audit_stuttering_paths(all_files)
    patch_sprawl = audit_patch_sprawl(all_files)
    wrappers = audit_pass_through_wrappers(repo_root, all_files)
    duplicates = audit_duplicate_filenames(all_files)
    orphans = audit_potential_orphans(repo_root, all_files)

    data = {
        "repo": str(repo_root),
        "total_files_scanned": len(all_files),
        "total_dirs_scanned": len(all_dirs),
        "single_child_dirs": single_child,
        "stuttering_paths": stuttering,
        "patch_and_dated_files": patch_sprawl,
        "pass_through_wrappers": wrappers,
        "duplicate_filenames": duplicates,
        "potential_orphans": orphans,
    }

    if args.json:
        print(json.dumps(data, indent=2))
        return

    print("=" * 65)
    print(f"DECLUTTER & STRUCTURE AUDIT: {repo_root.name}")
    print(f"Scanned: {len(all_files)} files across {len(all_dirs)} directories")
    print("=" * 65)

    print("\n## 1. Single-Child & Redundant Directory Nesting")
    if single_child:
        for item in single_child:
            kind = "DIR" if item["is_dir"] else "FILE"
            print(f"  - [{kind}] {item['dir']} -> {item['child']}")
    else:
        print("  (none found)")

    print("\n## 2. Naming Redundancy & Stuttering Paths")
    if stuttering:
        for item in stuttering[:30]:
            print(f"  - {item['file']} (folder '{item['parent_dir']}' repeated in '{item['stem']}')")
        if len(stuttering) > 30:
            print(f"  ... and {len(stuttering) - 30} more")
    else:
        print("  (none found)")

    print("\n## 3. Historical Patch Sprawl & Dated Files")
    if patch_sprawl:
        for item in patch_sprawl:
            tag = "[MIGRATION]" if item["is_migration"] else "[SPRAWL CANDIDATE]"
            print(f"  - {tag} {item['file']} (pattern: '{item['matched_pattern']}')")
    else:
        print("  (none found)")

    print("\n## 4. Potential Pass-Through Wrapper Layers")
    if wrappers:
        for item in wrappers:
            print(f"  - {item['file']} ({item['lines']} lines): wraps <{item['wrapped_component']} />")
    else:
        print("  (none found)")

    print("\n## 5. Duplicate Utility / Model Filenames Across Domains")
    if duplicates:
        for name, paths in list(duplicates.items())[:20]:
            print(f"  - {name} ({len(paths)} occurrences):")
            for p in paths:
                print(f"      * {p}")
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more duplicate sets")
    else:
        print("  (none found)")

    print("\n## 6. Potential Orphan / Unreferenced Source Files")
    if orphans:
        for item in orphans[:25]:
            print(f"  - {item}")
        if len(orphans) > 25:
            print(f"  ... and {len(orphans) - 25} more")
    else:
        print("  (none found)")

    print("\n" + "=" * 65)
    print("Summary:")
    print(f"  Single-child directory nestings : {len(single_child)}")
    print(f"  Stuttering naming paths         : {len(stuttering)}")
    print(f"  Patch / dated files             : {len(patch_sprawl)}")
    print(f"  Pass-through wrapper files      : {len(wrappers)}")
    print(f"  Duplicate filename clusters     : {len(duplicates)}")
    print(f"  Potential orphan source files   : {len(orphans)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
