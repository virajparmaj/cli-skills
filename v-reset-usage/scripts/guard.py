#!/usr/bin/env python3
"""Read-only Git eligibility checks; these checks do not establish semantic safety."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".c", ".h", ".cc", ".cpp", ".hpp"}
PROTECTED_PARTS = {
    ".git", ".github", "test", "tests", "__tests__", "spec", "specs", "fixtures",
    "mocks", "scripts", "tools", "tooling", "ci", "build", "dist", "vendor",
    "node_modules", "app", "pages", "routes", "api", "endpoints", "functions",
    "auth", "authentication", "authorization", "security", "crypto", "credentials",
    "db", "database", "migrations", "migration", "supabase", "alembic", "prisma",
    "schema", "schemas", "data", "datasets", "models", "model", "ml", "training",
    "inference", "finance", "financial", "risk", "metrics", "backtest", "signals",
}
PROTECTED_STEMS = {
    "main", "index", "app", "application", "server", "client", "bootstrap", "entry",
    "entrypoint", "router", "routes", "middleware", "setup", "manage", "conftest",
    "config", "settings", "manifest", "requirements", "lock", "package",
}
SENSITIVE_NAME = re.compile(
    r"auth|security|password|credential|session|migration|schema|database|"
    r"predict|training|inference|backtest|sharpe|drawdown|calibration|provenance|"
    r"finance|financial|risk|metric|model|dataset|signal|leakage"
)
PENDING = ("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG",
           "rebase-apply", "rebase-merge", "sequencer")


class GuardError(Exception):
    pass


def git(repo, *args, allow_failure=False):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    result = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
         "-c", "core.filemode=true", *args],
        cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
    )
    if result.returncode and not allow_failure:
        raise GuardError("Git inspection failed: " + result.stderr.decode(errors="replace").strip())
    return result


def decoded(result):
    return result.stdout.decode("utf-8", errors="surrogateescape").strip()


def inside(path, directory):
    return path == directory or directory in path.parents


def state(repo):
    root = Path(decoded(git(repo, "rev-parse", "--show-toplevel"))).resolve()
    common = Path(decoded(git(root, "rev-parse", "--git-common-dir")))
    common = (root / common).resolve() if not common.is_absolute() else common.resolve()
    gitdir = Path(decoded(git(root, "rev-parse", "--absolute-git-dir"))).resolve()
    head = decoded(git(root, "rev-parse", "--verify", "HEAD", allow_failure=True))
    branch = decoded(git(root, "symbolic-ref", "--quiet", "--short", "HEAD", allow_failure=True))
    issues = []
    if not head:
        issues.append("No committed HEAD exists")
    if not branch:
        issues.append("Detached HEAD is audit-only")
    for name in PENDING:
        path = Path(decoded(git(root, "rev-parse", "--git-path", name)))
        if not path.is_absolute():
            path = root / path
        if path.exists():
            issues.append("Pending Git operation: " + name)
    metadata_dirs = {common, gitdir}
    if any(any(directory.glob("*.lock")) or any((directory / "refs").rglob("*.lock"))
           for directory in metadata_dirs):
        issues.append("Git lock indicator exists")
    index = git(root, "ls-files", "-v", "-z").stdout.split(b"\0")
    if any(item and (item[:1].islower() or item[:1] == b"S") for item in index):
        issues.append("Index has assume-unchanged or skip-worktree entries")
    return {"version": 1, "root": str(root), "git_common_dir": str(common),
            "git_dir": str(gitdir),
            "head": head, "branch": branch, "issues": issues}


def capture(repo, output):
    info = state(repo)
    root = Path(info["root"])
    output = Path(output).resolve()
    if inside(output, root) or inside(output, Path(info["git_common_dir"])):
        raise GuardError("Checkpoint must be outside the repository and common Git directory")
    if git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
           "--ignore-submodules=none").stdout:
        info["issues"].append("Checkout contains tracked, staged, or untracked changes")
    info["eligible"] = not info["issues"]
    with output.open("x", encoding="utf-8") as stream:
        json.dump(info, stream, indent=2)
        stream.write("\n")
    return info


def allowed_path(root, relative):
    pure = PurePosixPath(relative)
    if (not relative or pure.is_absolute() or str(pure) != relative or "\\" in relative
            or any(part in {".", ".."} for part in pure.parts)):
        raise GuardError("Allowlist requires exact normalized relative paths")
    path = root.joinpath(*pure.parts)
    cursor = root
    for part in pure.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise GuardError("Symlink path is ineligible: " + relative)
    if path.suffix.lower() not in CODE_SUFFIXES:
        raise GuardError("Only supported existing source files are eligible: " + relative)
    lowered = [part.lower() for part in pure.parts]
    filename = lowered[-1]
    stem = Path(filename).stem
    tokens = set(re.split(r"[^a-z0-9]+", "/".join(lowered)))
    if (set(lowered) & PROTECTED_PARTS or tokens & PROTECTED_PARTS
            or stem in PROTECTED_STEMS or SENSITIVE_NAME.search(filename)
            or ".config." in filename or filename.endswith(".d.ts")
            or re.search(r"(^|[._-])(test|spec)([._-]|$)", filename)):
        raise GuardError("Protected path (heuristic; not exhaustive): " + relative)
    return relative


def verify(checkpoint, allow):
    checkpoint = Path(checkpoint).resolve()
    with checkpoint.open(encoding="utf-8") as stream:
        baseline = json.load(stream)
    if baseline.get("version") != 1 or baseline.get("eligible") is not True:
        raise GuardError("Baseline is not eligible")
    current = state(baseline["root"])
    if current["issues"]:
        raise GuardError("; ".join(current["issues"]))
    for key in ("root", "git_common_dir", "git_dir", "head", "branch"):
        if current[key] != baseline.get(key):
            raise GuardError("Repository identity changed: " + key)
    root = Path(current["root"])
    if inside(checkpoint, root) or inside(checkpoint, Path(current["git_common_dir"])):
        raise GuardError("Checkpoint must remain outside Git/repository directories")
    allow = {allowed_path(root, path) for path in allow}
    if git(root, "diff", "--cached", "--name-only", "-z", "--ignore-submodules=none").stdout:
        raise GuardError("Staged changes are ineligible")
    if git(root, "ls-files", "--others", "--exclude-standard", "-z").stdout:
        raise GuardError("Unexpected untracked files exist")
    raw = git(root, "diff", "--raw", "-z", "--no-renames", "--no-ext-diff",
              "--no-textconv", "--ignore-submodules=none", "HEAD", "--").stdout.split(b"\0")
    touched = []
    for offset in range(0, len(raw) - 1, 2):
        fields = raw[offset].decode().split()
        path = raw[offset + 1].decode("utf-8", errors="surrogateescape")
        if len(fields) != 5:
            raise GuardError("Unexpected Git diff structure")
        old_mode, new_mode, status = fields[0][1:], fields[1], fields[4]
        if path not in allow:
            raise GuardError("Changed path outside exact allowlist: " + path)
        allowed_path(root, path)
        if status not in {"M", "D"} or old_mode not in {"100644", "100755"}:
            raise GuardError("Only existing regular-file edits/deletions are eligible: " + path)
        if status == "M" and new_mode != old_mode:
            raise GuardError("File-mode change is ineligible: " + path)
        original = git(root, "cat-file", "blob", "HEAD:" + path).stdout
        if b"\0" in original or (status == "M" and b"\0" in (root / path).read_bytes()):
            raise GuardError("Binary source content is ineligible: " + path)
        touched.append(path)
    added = deleted = 0
    stats = git(root, "diff", "--numstat", "-z", "--no-renames", "--no-ext-diff",
                "--no-textconv", "--ignore-submodules=none", "HEAD", "--").stdout.split(b"\0")
    for entry in filter(None, stats):
        plus, minus, _ = entry.split(b"\t", 2)
        if plus == b"-" or minus == b"-":
            raise GuardError("Binary change is ineligible")
        added += int(plus)
        deleted += int(minus)
    if len(touched) > 5 or added + deleted > 100:
        raise GuardError("Invocation exceeds five files or 100 added+deleted lines")
    return {"eligible": True, "root": str(root), "files": touched,
            "added": added, "deleted": deleted,
            "limitation": "Mechanical gate only; semantic and project-policy review still required"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cap = commands.add_parser("capture")
    cap.add_argument("--repo", required=True)
    cap.add_argument("--output", required=True)
    check = commands.add_parser("verify")
    check.add_argument("--checkpoint", required=True)
    check.add_argument("--allow", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        result = (capture(args.repo, args.output) if args.command == "capture"
                  else verify(args.checkpoint, args.allow))
    except (GuardError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        result = {"eligible": False, "issues": [str(exc)], "mode": "audit-only"}
    if not result.get("eligible"):
        result["mode"] = "audit-only"
    print(json.dumps(result, indent=2))
    return 0 if result.get("eligible") else 2


if __name__ == "__main__":
    sys.exit(main())
