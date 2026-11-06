#!/usr/bin/env python3
"""Validate the skill collection and optionally run its isolated regression suites."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.S)
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata"}


def files_under(root):
    """Prune generated trees before descending; do not follow directory symlinks."""
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith("."))
        for name in sorted(files):
            yield Path(base) / name


def prose(text):
    """Ignore fenced and inline examples when checking navigational links."""
    marker = None
    length = 0
    for line in text.splitlines():
        fence = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?(`{3,}|~{3,})(.*)$", line)
        if fence:
            token, rest = fence.groups()
            if marker is None:
                marker, length = token[0], len(token)
            elif token[0] == marker and len(token) >= length and not rest.strip():
                marker = None
            continue
        if marker is None:
            yield re.sub(r"(`+).*?\1", "", line)


def check_links(path):
    errors = []
    for line in prose(path.read_text(encoding="utf-8")):
        for match in re.finditer(r"\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", line):
            target = match[1].strip("<>")
            try:
                parts = urlsplit(target)
            except ValueError as exc:
                errors.append(f"{path}: invalid linked resource {target}: {exc}")
                continue
            if parts.scheme or parts.netloc or not parts.path:
                continue
            local = unquote(parts.path)
            if any(token in local for token in ("{", "}", "<", ">", "*")):
                continue
            if not (path.parent / local).exists():
                errors.append(f"{path}: missing linked resource {target}")
    return errors


def validate_catalog(root):
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Install requirements-dev.txt in a virtual environment.") from exc
    errors, records, names, docs = [], [], {}, set()
    files = list(files_under(root))
    for path in (p for p in files if p.name == "SKILL.md"):
        record = {"path": str(path.relative_to(root)), "name": None}
        records.append(record)
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append(f"{path}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match[1])
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{path}: frontmatter must be a mapping")
            continue
        extra = set(metadata) - ALLOWED_FIELDS
        if extra:
            errors.append(f"{path}: unsupported frontmatter fields {sorted(map(str, extra))}")
        name, description = metadata.get("name"), metadata.get("description")
        if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
            errors.append(f"{path}: invalid or empty skill name")
        else:
            record["name"] = name
            if name != path.parent.name:
                errors.append(f"{path}: declared name {name!r} differs from directory")
            if name in names:
                errors.append(f"{path}: duplicate skill name {name!r}, also at {names[name]}")
            names[name] = path
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{path}: description must contain 1–1024 characters")
        elif "<" in description or ">" in description:
            errors.append(f"{path}: description contains angle brackets")
        if not text[match.end():].strip():
            errors.append(f"{path}: skill instructions are empty")
        if any(re.fullmatch(r"\s*\[TODO:[^\n]*\]\s*", line) for line in prose(text[match.end():])):
            errors.append(f"{path}: unfinished scaffold placeholder")
        docs.add(path)
        docs.update((path.parent / "references").rglob("*.md"))
        ui_path = path.parent / "agents" / "openai.yaml"
        if ui_path.exists():
            try:
                ui = yaml.safe_load(ui_path.read_text(encoding="utf-8"))
                if not isinstance(ui, dict):
                    raise ValueError("metadata must be a mapping")
                interface = ui.get("interface", {})
                if not isinstance(interface, dict):
                    raise ValueError("interface must be a mapping")
                prompt = interface.get("default_prompt")
                if prompt is not None and (not isinstance(prompt, str) or f"${name}" not in prompt):
                    raise ValueError("default_prompt must reference this skill's $name")
                short = interface.get("short_description")
                if short is not None and (not isinstance(short, str) or not 25 <= len(short) <= 64):
                    raise ValueError("short_description must contain 25–64 characters")
                for key in ("icon_small", "icon_large"):
                    if key in interface:
                        icon = interface[key]
                        if not isinstance(icon, str) or not (path.parent / icon).is_file():
                            raise ValueError(f"{key} must reference an existing local file")
                policy = ui.get("policy", {})
                if not isinstance(policy, dict):
                    raise ValueError("policy must be a mapping")
                if "allow_implicit_invocation" in policy and not isinstance(policy["allow_implicit_invocation"], bool):
                    raise ValueError("allow_implicit_invocation must be a boolean")
            except (yaml.YAMLError, ValueError) as exc:
                errors.append(f"{ui_path}: {exc}")
    if not records:
        errors.append(f"{root}: no skills found")
    for doc in sorted(docs):
        errors.extend(check_links(doc))
    return records, files, errors


def syntax_check(path):
    try:
        if path.suffix == ".py":
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        else:
            binary = "bash" if path.suffix == ".sh" else "node"
            if not shutil.which(binary):
                return f"{path}: {binary} unavailable; syntax check unverified"
            result = subprocess.run([binary, "-n" if binary == "bash" else "--check", str(path)],
                                    capture_output=True, text=True, timeout=30)
            if result.returncode:
                return f"{path}: {result.stderr.strip() or result.stdout.strip()}"
    except (OSError, UnicodeError, SyntaxError, subprocess.TimeoutExpired) as exc:
        return f"{path}: {exc}"
    return None


TEST_PROGRAM = '''
import io, json, sys, unittest
suite = unittest.TestLoader().discover(sys.argv[1], top_level_dir=sys.argv[1])
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
print("__SKILL_TEST_RESULT__" + json.dumps({
    "run": result.testsRun, "skipped": len(result.skipped),
    "success": result.wasSuccessful(), "output": stream.getvalue()}))
sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
'''


def run_tests(root, skill_records, skill_python):
    folders = [root / "tests"] + [root / r["path"] for r in skill_records]
    folders = [p if p.name == "tests" else p.parent / "tests" for p in folders]
    results, errors = [], []
    for folder in sorted(set(folders)):
        if not folder.is_dir() or not any(folder.glob("test*.py")):
            continue
        interpreter = sys.executable if folder == root / "tests" else skill_python
        try:
            process = subprocess.run([interpreter, "-c", TEST_PROGRAM, str(folder)],
                                     capture_output=True, text=True, timeout=60, cwd=root)
            marker = process.stdout.rfind("__SKILL_TEST_RESULT__")
            if marker < 0:
                raise ValueError(process.stderr.strip() or process.stdout.strip() or "no test result")
            result = json.loads(process.stdout[marker + len("__SKILL_TEST_RESULT__"):])
            result["folder"] = str(folder.relative_to(root))
            results.append(result)
            if process.returncode or not result["run"]:
                errors.append(f"{folder}: failed, skipped, or empty regression suite\n{result['output']}")
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            errors.append(f"{folder}: {exc}")
    return results, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--tests", action="store_true", help="Run repository and skill regression suites")
    parser.add_argument("--skill-test-python", default=sys.executable,
                        help="Interpreter for skill suites (e.g. an existing pandas/sklearn environment)")
    parser.add_argument("--jobs", type=int, default=4, help="Concurrent syntax checks (1–8, default: 4)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    started = time.perf_counter()
    try:
        root = args.repo.expanduser().resolve(strict=True)
        records, files, errors = validate_catalog(root)
        scripts = [p for p in files if p.suffix in {".py", ".sh", ".mjs"}]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            errors.extend(error for error in pool.map(syntax_check, scripts) if error)
        tests = []
        if args.tests:
            tests, test_errors = run_tests(root, records, args.skill_test_python)
            errors.extend(test_errors)
        report = {"skills": len(records), "syntax_checks": len(scripts), "catalog": records,
                  "test_suites": tests, "errors": errors,
                  "elapsed_seconds": round(time.perf_counter() - started, 3)}
        if args.report:
            args.report.expanduser().write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            count = sum(s["run"] for s in tests)
            skips = sum(s["skipped"] for s in tests)
            print(f"Checked {len(records)} skills, {len(scripts)} scripts; "
                  f"{count} tests ({skips} skipped); {len(errors)} errors; "
                  f"{report['elapsed_seconds']:.3f}s")
            for error in errors:
                print(error, file=sys.stderr)
        return 1 if errors else 0
    except (OSError, UnicodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
