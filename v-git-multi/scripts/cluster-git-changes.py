#!/usr/bin/env python3
"""Read-only Git inventory. NUL-delimited input preserves every legal filename.

Format source: https://git-scm.com/docs/git-diff
"""
import json
import os
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def classify(path):
    name = path.lower().rsplit("/", 1)[-1]
    parts = path.lower().split("/")
    if any(p in {"test", "tests", "__tests__"} for p in parts) or any(
        token in name for token in (".test.", ".spec.")
    ) or name.endswith(("_test.py", "_test.go")):
        return "test"
    if name.startswith(("tailwind.config.", "postcss.config.")) or name.endswith((".css", ".scss", ".sass", ".less")):
        return "style"
    if name in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "makefile", "dockerfile", ".gitignore"} or name.startswith(("tsconfig", "vite.config.", "vercel.", ".env", "requirements", "docker-compose", ".eslintrc", ".prettierrc")) or name.endswith((".yaml", ".yml", ".toml", ".ini", ".cfg", ".dockerfile")) or ".github" in parts:
        return "config"
    if name.endswith((".md", ".mdx", ".rst", ".txt")) or any(p in {"docs", "notes"} for p in parts) or name.startswith(("readme", "changelog", "license")):
        return "docs"
    if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".webm", ".pdf")) or any(p in {"assets", "public"} for p in parts):
        return "asset"
    if name.endswith((".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".java", ".rb", ".php")) or any(p in {"src", "backend", "app", "lib"} for p in parts):
        return "src"
    return "other"


def changed(repo, staged):
    args = ["diff", "--name-status", "-z", "-M"]
    if staged:
        args.append("--cached")
    fields = git(repo, *args).split(b"\0")
    rows, i = [], 0
    while i < len(fields) and fields[i]:
        status = fields[i].decode("ascii")
        path = os.fsdecode(fields[i + 1])
        i += 2
        old = None
        if status.startswith(("R", "C")):
            old, path = path, os.fsdecode(fields[i])
            i += 1
        rows.append({"stage": "staged" if staged else "worktree", "status": status,
                     "class": classify(path), "topdir": path.split("/")[0] if "/" in path else "(root)",
                     "path": path, "old_path": old})
    return rows


def quoted(path):
    return json.dumps(path, ensure_ascii=True)


def main():
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip())
    staged, worktree = changed(root, True), changed(root, False)
    new = [os.fsdecode(p) for p in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p]
    rows = staged + worktree + [{"stage": "new", "status": "??", "class": classify(p),
                                "topdir": p.split("/")[0] if "/" in p else "(root)",
                                "path": p, "old_path": None} for p in new]
    # symbolic-ref also works before the first commit and in linked worktrees.
    branch_result = subprocess.run(["git", "-C", str(root), "symbolic-ref", "--short", "-q", "HEAD"], capture_output=True)
    branch = os.fsdecode(branch_result.stdout).strip() or "(detached)"
    print("=== summary ===")
    print(f"repo: {root}\nbranch: {branch}\nstaged entries: {len(staged)}\nunstaged entries: {len(worktree)}\nuntracked files: {len(new)}\nrenames detected: {sum(r['old_path'] is not None for r in rows)}")
    print("\n=== file manifest ===\nSTAGE   STATUS  CLASS   TOPDIR          PATH (JSON-quoted)")
    for row in rows:
        print(f"{row['stage']:<7} {row['status']:<7} {row['class']:<7} {quoted(row['topdir']):<15} {quoted(row['path'])}")
    print("\n=== manifest json ===")
    print(json.dumps(rows, ensure_ascii=True, indent=2))
    print("\n=== rename pairs ===")
    renames = [r for r in rows if r["old_path"] is not None]
    for row in renames:
        print(f"{quoted(row['old_path'])} -> {quoted(row['path'])} ({row['status']})")
    if not renames:
        print("(none)")
    print("\n=== diffstat (tracked changes) ===")
    for options in [("--cached",), ()]:
        output = git(root, "diff", "--stat", "-M", *options).decode("utf-8", "replace").strip()
        if output:
            print(output)
    if not staged and not worktree:
        print("(no tracked changes)")
    print("\n=== untracked sizes (best effort) ===")
    for path in new:
        try:
            lines, binary = 0, False
            with (root / path).open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    if b"\0" in chunk:
                        binary = True
                        break
                    lines += chunk.count(b"\n")
            size = "binary" if binary else f"{lines} lines"
        except OSError as exc:
            size = f"unreadable ({exc.strerror})"
        print(f"{size:>10}  {quoted(path)}")
    if not new:
        print("(none)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, IndexError) as exc:
        print(f"cluster-git-changes: {exc}", file=sys.stderr)
        raise SystemExit(1)
