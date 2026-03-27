#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


CONTEXT_FILES = [
    "CLAUDE.md",
    "notes/13_prompt_context.md",
    "notes/03_architecture.md",
    "notes/04_auth_and_roles.md",
    "notes/11_known_issues.md",
    "notes/10_deployment.md",
    "notes/05_database_schema.md",
    "README.md",
    ".impeccable.md",
    "PRODUCTION_READY.md",
]

REPO_MAP = {
    "package_json": ["package.json"],
    "tsconfig": ["tsconfig.json", "tsconfig.app.json"],
    "vite_config": ["vite.config.ts", "vite.config.js", "vite.config.mts", "vite.config.mjs"],
    "tailwind_config": [
        "tailwind.config.ts",
        "tailwind.config.js",
        "tailwind.config.cjs",
        "tailwind.config.mjs",
    ],
    "vercel_config": ["vercel.json"],
    "env_example": [".env.example"],
    "env_files": [".env", ".env.local"],
    "eslint_config": [
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.json",
    ],
}

DIR_MARKERS = {
    "supabase": "supabase",
    "api": "api",
    "backend": "backend",
    "github_workflows": ".github/workflows",
}

LOCKFILES = ["package-lock.json", "bun.lockb", "bun.lock", "pnpm-lock.yaml", "yarn.lock"]
COMMON_DEPS = [
    "@tanstack/react-query",
    "recharts",
    "sonner",
    "framer-motion",
    "next-themes",
    "zod",
    "lovable-tagger",
]
IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    "out",
    ".vercel",
    ".turbo",
    "__pycache__",
    ".venv",
    "venv",
}
SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
DEMO_MARKERS = ("VITE_DEMO_MODE", "isDemoMode(")


def rel(repo: Path, path: Path) -> str:
    return str(path.relative_to(repo))


def existing_paths(repo: Path, candidates: list[str]) -> list[str]:
    found = []
    for candidate in candidates:
        path = repo / candidate
        if path.exists():
            found.append(candidate)
    return found


def walk_source_files(repo: Path):
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SOURCE_SUFFIXES:
            yield path


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _ in handle)


def collect_inventory(repo: Path, threshold: int, top: int) -> dict:
    notes_files = sorted(
        rel(repo, path) for path in (repo / "notes").glob("*.md")
    ) if (repo / "notes").exists() else []

    context = []
    for candidate in CONTEXT_FILES:
        path = repo / candidate
        context.append(
            {
                "path": candidate,
                "present": path.exists(),
            }
        )

    repo_map = {
        key: existing_paths(repo, candidates)
        for key, candidates in REPO_MAP.items()
    }

    markers = {
        key: (repo / value).exists()
        for key, value in DIR_MARKERS.items()
    }

    lockfiles = [name for name in LOCKFILES if (repo / name).exists()]

    oversized = []
    for path in walk_source_files(repo):
        count = line_count(path)
        if count >= threshold:
            oversized.append({"path": rel(repo, path), "lines": count})
    oversized.sort(key=lambda item: (-item["lines"], item["path"]))

    placeholder_tests = sorted(
        rel(repo, path)
        for path in repo.rglob("example.test.*")
        if path.is_file() and not any(part in IGNORE_DIRS for part in path.parts)
    )

    dep_hits = {}
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        for dep in COMMON_DEPS:
            sections = []
            if dep in deps:
                sections.append("dependencies")
            if dep in dev_deps:
                sections.append("devDependencies")
            if sections:
                dep_hits[dep] = sections

    demo_hits = []
    for path in walk_source_files(repo):
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for lineno, line in enumerate(handle, start=1):
                if any(marker in line for marker in DEMO_MARKERS):
                    demo_hits.append(
                        {
                            "path": rel(repo, path),
                            "line": lineno,
                            "text": line.strip(),
                        }
                    )
                    if len(demo_hits) >= 12:
                        break
        if len(demo_hits) >= 12:
            break

    return {
        "repo": str(repo),
        "notes_files": notes_files,
        "context_files": context,
        "repo_map": repo_map,
        "markers": markers,
        "lockfiles": lockfiles,
        "oversized_files": oversized[:top],
        "placeholder_tests": placeholder_tests,
        "common_dependencies": dep_hits,
        "demo_mode_hits": demo_hits,
    }


def print_text_report(data: dict, threshold: int) -> None:
    print(f"Repo: {data['repo']}")
    print("")

    print("Context files:")
    for item in data["context_files"]:
        status = "FOUND" if item["present"] else "MISSING"
        print(f"- {status}: {item['path']}")
    if data["notes_files"]:
        print(f"- notes/: {len(data['notes_files'])} markdown files")
    else:
        print("- notes/: missing")
    print("")

    print("Repo map:")
    for key, matches in data["repo_map"].items():
        display = ", ".join(matches) if matches else "missing"
        print(f"- {key}: {display}")
    for key, present in data["markers"].items():
        print(f"- {key}: {'present' if present else 'missing'}")
    print("")

    print("Lockfiles:")
    if data["lockfiles"]:
        for lockfile in data["lockfiles"]:
            print(f"- {lockfile}")
    else:
        print("- none found")
    print("")

    print(f"Oversized source files (>= {threshold} LOC):")
    if data["oversized_files"]:
        for item in data["oversized_files"]:
            print(f"- {item['lines']:>5}  {item['path']}")
    else:
        print("- none found")
    print("")

    print("Placeholder tests:")
    if data["placeholder_tests"]:
        for path in data["placeholder_tests"]:
            print(f"- {path}")
    else:
        print("- none found")
    print("")

    print("Common dependency signals:")
    if data["common_dependencies"]:
        for dep, sections in data["common_dependencies"].items():
            print(f"- {dep}: {', '.join(sections)}")
    else:
        print("- none of the tracked deps found in package.json")
    print("")

    print("Demo-mode signals:")
    if data["demo_mode_hits"]:
        for hit in data["demo_mode_hits"]:
            print(f"- {hit['path']}:{hit['line']}  {hit['text']}")
    else:
        print("- none found")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a high-signal inventory for repo architecture audits."
    )
    parser.add_argument("--repo", required=True, help="Path to the repository to inspect.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=300,
        help="LOC threshold for oversized files. Default: 300.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Max oversized files to report. Default: 20.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a text report.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    data = collect_inventory(repo, threshold=args.threshold, top=args.top)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_text_report(data, threshold=args.threshold)


if __name__ == "__main__":
    main()
