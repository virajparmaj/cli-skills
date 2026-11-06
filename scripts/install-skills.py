#!/usr/bin/env python3
"""Link this checkout's skills into CLI workflows without overwriting other skills."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys
import uuid


REPO = Path(__file__).resolve().parents[1]
RETIRED = {
    "v-delovable", "v-macos", "v-ml-deploy", "v-production",
    "v-readme-app", "v-readme-web", "v-test-functional",
    "v-test-handling-fallback", "v-test-input-edge",
    "v-test-system-reliability", "v-ux", "v-structure", "v-speed",
    "v-performance", "v-go-live",
}
EXCLUDED = {".git", "node_modules", ".venv", "__pycache__"}


def discover(repo):
    """Return unique declared names, including the five nested UI skills."""
    skills = {}
    for base, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith("."))
        if "SKILL.md" not in files:
            continue
        folder = Path(base)
        content = (folder / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
        match = re.search(r"^name:\s*['\"]?([a-z0-9]+(?:-[a-z0-9]+)*)['\"]?\s*$",
                          frontmatter[1], re.M) if frontmatter else None
        if not match or len(match[1]) > 64:
            raise ValueError(f"Invalid or missing skill name: {folder / 'SKILL.md'}")
        name = match[1]
        if name != folder.name:
            raise ValueError(f"Skill name {name!r} differs from folder {folder.name!r}")
        if name in skills:
            raise ValueError(f"Duplicate skill name {name!r}: {skills[name]} and {folder}")
        skills[name] = folder.resolve()
    if not skills:
        raise ValueError(f"No skills found in {repo}")
    return dict(sorted(skills.items()))


def default_targets():
    home = Path.home()
    codex = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).expanduser()
    targets = {"codex": codex / "skills"}
    # Reuse the user's installed workflows; do not provision unrelated tools.
    for name, folder in {
        "claude": home / ".claude" / "skills",
        "gemini": home / ".gemini" / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
        "gemini-legacy": home / ".gemini" / "config" / "skills",
    }.items():
        if folder.is_dir():
            targets[name] = folder
    return targets


def link_target(path):
    raw = os.readlink(path)
    return (path.parent / raw).resolve(strict=False)


def owned_link(path, repo):
    return path.is_symlink() and link_target(path).is_relative_to(repo)


def make_plan(repo, skills, targets):
    repo = repo.resolve()
    actions = []
    for target in targets:
        if target.exists() and not target.is_dir():
            raise ValueError(f"Skill destination is not a directory: {target}")
        if target.resolve(strict=False).is_relative_to(repo):
            raise ValueError(f"Install destination must be outside the source checkout: {target}")
        for name, source in skills.items():
            dest = target / name
            action = "link"
            previous = None
            if dest.is_symlink():
                previous = os.readlink(dest)
                if link_target(dest) == source:
                    action = "unchanged"
                elif owned_link(dest, repo):
                    action = "replace"
                else:
                    action = "conflict"
            elif dest.exists():
                action = "conflict"
            actions.append({"action": action, "path": str(dest),
                            "source": str(source), "previous": previous})
        for name in sorted(RETIRED - skills.keys()):
            dest = target / name
            if owned_link(dest, repo):
                actions.append({"action": "retire", "path": str(dest),
                                "source": None, "previous": os.readlink(dest)})
    return actions


def apply_plan(actions):
    conflicts = [a["path"] for a in actions if a["action"] == "conflict"]
    if conflicts:
        raise ValueError("Preserved existing skills; resolve conflicts first: " + ", ".join(conflicts))
    for item in actions:
        action = item["action"]
        if action == "unchanged":
            continue
        dest = Path(item["path"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        if action in {"replace", "retire"}:
            if not dest.is_symlink() or os.readlink(dest) != item["previous"]:
                raise ValueError(f"Destination changed after preflight; stopped: {dest}")
        if action == "retire":
            dest.unlink()
        elif action == "replace":
            temporary = dest.with_name(f".{dest.name}.{uuid.uuid4().hex}.link")
            try:
                temporary.symlink_to(item["source"], target_is_directory=True)
                os.replace(temporary, dest)
            finally:
                if temporary.is_symlink():
                    temporary.unlink()
        else:
            # symlink_to fails if another process creates this name; no overwrite.
            dest.symlink_to(item["source"], target_is_directory=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO, help="Source checkout (default: this repo)")
    parser.add_argument("--target", type=Path, action="append",
                        help="Exact skills folder; repeat for multiple destinations")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply the plan (default: preview only)")
    mode.add_argument("--check", action="store_true", help="Exit 1 if installation needs updating")
    parser.add_argument("--json", action="store_true", help="Print the complete plan as JSON")
    parser.add_argument("--report", type=Path, help="Save plan and original link targets as JSON")
    args = parser.parse_args()
    try:
        repo = args.repo.expanduser().resolve(strict=True)
        skills = discover(repo)
        selected = args.target or list(default_targets().values())
        targets = list(dict.fromkeys(p.expanduser().resolve(strict=False) for p in selected))
        actions = make_plan(repo, skills, targets)
        report = {"repo": str(repo), "skills": len(skills),
                  "targets": [str(p) for p in targets], "applied": False, "actions": actions}
        if args.report:
            args.report.expanduser().write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.apply:
            apply_plan(actions)
            report["applied"] = True
            if args.report:
                args.report.expanduser().write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        counts = dict(Counter(a["action"] for a in actions))
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{'Installed' if args.apply else 'Checked' if args.check else 'Preview'}: "
                  f"{len(skills)} skills, {len(targets)} destinations; {counts}")
            for target in targets:
                print(f"  {target}")
            for item in actions:
                if item["action"] == "conflict":
                    print(f"  PRESERVED CONFLICT: {item['path']}")
            if not args.apply and not args.check:
                print("Run with --apply to install. Other skills and real directories are preserved.")
        needs_change = any(a["action"] != "unchanged" for a in actions)
        return 1 if (args.check and needs_change) or counts.get("conflict") else 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
