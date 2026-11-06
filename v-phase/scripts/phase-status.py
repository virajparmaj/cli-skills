#!/usr/bin/env python3
"""Gather phase evidence in one pruned walk; file presence is not completion."""
import fnmatch
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote

PRUNE = {"node_modules", ".git", "dist", "build", ".next", ".venv", "venv", "__pycache__", "coverage"}
EXT = r"(?:tsx?|jsx?|py|json|sql|md|css|sh|toml|ya?ml)"
PATH = re.compile(r"[A-Za-z0-9_./-]+\." + EXT + r"(?::\d+(?:-\d+)?)?")


def references(text):
    candidates = []
    for match in re.finditer(r"`([^`\n]+)`", text):
        token = match[1]
        if re.search(r"\." + EXT + r"(?::\d+(?:-\d+)?)?$", token):
            candidates.append((token, False))
    stripped = re.sub(r"`[^`\n]+`", " ", text)
    for match in re.finditer(r"\]\(([^)]+)\)", stripped):
        token = match[1].strip("<>").split("#", 1)[0]
        if not re.match(r"[a-z]+://", token, re.I) and re.search(r"\." + EXT + r"$", token):
            candidates.append((unquote(token), True))
    stripped = re.sub(r"\]\([^)]+\)", " ", stripped)
    candidates.extend((match[0], False) for match in PATH.finditer(stripped))
    clean = set()
    for token, relative in candidates:
        if re.match(r"[a-z]+://", token, re.I):
            continue
        token = re.sub(r":\d+(?:-\d+)?$", "", token).removeprefix("./")
        clean.add((token, relative))
    return sorted(clean)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1
    docs, by_name = [], {}
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in PRUNE)
        for name in sorted(files):
            path = Path(base) / name
            by_name.setdefault(name, []).append(path)
            lower = name.lower()
            if any(fnmatch.fnmatchcase(lower, p) for p in ("phase-*.md", "phase_*.md", "phase[0-9]*.md")):
                docs.append(path)
    print(f"=== repo root ===\n{root}\n\n=== phase docs found ===")
    if not docs:
        print("NONE — no phase-*.md contract docs found")
        return 0
    docs.sort()
    for doc in docs:
        print(doc.relative_to(root))
    print(f"\ncount: {len(docs)}\n")
    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        print(f"=== doc: {doc.relative_to(root)} ===\n--- status markers ---")
        for number, line in enumerate(lines, 1):
            if re.search(r"\b(status|state|implemented|done|completed?|shipped|in progress|todo|pending)\s*[:—-]", line, re.I):
                print(f"{number}:{line}")
        print("\n--- acceptance checkboxes ---")
        checked = unchecked = 0
        for number, line in enumerate(lines, 1):
            match = re.match(r"\s*[-*]\s+\[([ xX])\]", line)
            if match:
                checked += match[1].lower() == "x"
                unchecked += match[1] == " "
                print(f"{number}:{line}")
        print(f"checkbox tally: checked={checked} unchecked={unchecked}\n\n--- referenced file paths (existence check) ---")
        refs = references(text)
        if not refs:
            print("(none referenced)")
        for token, relative in refs:
            path = Path(token)
            choices = [doc.parent / path, root / path] if relative else [root / path, doc.parent / path]
            exact = next((p for p in choices if p.exists()), None)
            if exact is not None:
                print(f"EXISTS   {token} -> {os.path.relpath(exact, root)}")
            elif path.name in by_name:
                matches = by_name[path.name]
                labels = ", ".join(str(p.relative_to(root)) for p in matches[:5])
                print(f"BASENAME {token} -> {labels} ({len(matches)} candidate(s); verify the intended path)")
            else:
                print(f"MISSING  {token}")
        print()
    print("=== context files present ===")
    for name in ("CLAUDE.md", "README.md", "notes/00_overview.md", "notes/03_architecture.md", "notes/06_api_contracts.md", "notes/11_known_issues.md", "TASKS.md", "TODO.md"):
        if (root / name).is_file():
            print(f"PRESENT {name}")
    print("\n=== done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
