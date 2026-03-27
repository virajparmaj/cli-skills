#!/usr/bin/env python3
"""Map the likely ML audit surface for a Website project."""

from __future__ import annotations

import argparse
from pathlib import Path


CONTEXT_ORDER = [
    "CLAUDE.md",
    "README.md",
    "notes/13_prompt_context.md",
    "notes/03_architecture.md",
    "notes/06_api_contracts.md",
    "notes/11_known_issues.md",
    "notes/10_deployment.md",
    ".env.example",
    ".env",
]


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def existing(root: Path, ordered_paths: list[str]) -> list[Path]:
    return [root / item for item in ordered_paths if (root / item).exists()]


def glob_many(root: Path, patterns: list[str]) -> list[Path]:
    found: set[Path] = set()
    for pattern in patterns:
        found.update(root.glob(pattern))
    return sorted(p for p in found if p.exists())


def infer_topology(root: Path) -> str:
    has_backend = (root / "backend").exists() and bool(
        glob_many(root, ["backend/*.py", "backend/**/*.py"])
    )
    has_frontend_preprocessing = any(
        (root / candidate).exists()
        for candidate in [
            "src/lib/alignFeatures.ts",
            "src/contexts/DataContext.tsx",
            "src/pages/Upload.tsx",
            "src/data/demoRunSnapshot.ts",
            "scripts/build-demo-snapshot.ts",
        ]
    )
    has_frontend = (root / "src").exists()

    if not has_backend and has_frontend:
        return "frontend-only/demo"
    if has_backend and has_frontend_preprocessing:
        return "hybrid"
    if has_backend:
        return "backend-only"
    return "frontend-only/demo"


def print_section(title: str, items: list[Path], root: Path) -> None:
    print(f"\n{title}")
    if not items:
        print("- none found")
        return
    for item in items:
        print(f"- {rel(root, item)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the likely ML audit surface for a Website repo."
    )
    parser.add_argument("repo", help="Absolute or relative path to the repo root")
    args = parser.parse_args()

    root = Path(args.repo).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Path is not a directory: {root}")

    print(f"Repo: {root}")
    print(f"Topology guess: {infer_topology(root)}")

    print_section("Context files (read in this order)", existing(root, CONTEXT_ORDER), root)
    print_section(
        "Dependency manifests",
        existing(root, ["package.json", "backend/requirements.txt", "pyproject.toml"]),
        root,
    )
    print_section(
        "Model artifacts",
        glob_many(
            root,
            [
                "backend/artifacts/*.joblib",
                "backend/artifacts/*.pkl",
                "backend/artifacts/*.onnx",
                "backend/artifacts/*.pt",
                "models/*.joblib",
                "models/*.pkl",
                "models/*.onnx",
                "models/*.pt",
            ],
        ),
        root,
    )
    print_section(
        "Model metadata",
        glob_many(
            root,
            [
                "backend/artifacts/model_info*.json",
                "backend/artifacts/model_card*.json",
                "models/model_info*.json",
                "models/model_card*.json",
            ],
        ),
        root,
    )
    print_section(
        "Backend inference files",
        glob_many(root, ["backend/*.py", "backend/**/*.py"]),
        root,
    )
    print_section(
        "Frontend contract files",
        glob_many(
            root,
            [
                "src/services/api.ts",
                "src/lib/api.ts",
                "src/lib/api/**/*.ts",
                "src/types/*.ts",
                "src/types/**/*.ts",
                "src/lib/alignFeatures.ts",
            ],
        ),
        root,
    )
    print_section(
        "Fallback/demo candidates",
        glob_many(
            root,
            [
                "src/contexts/*.tsx",
                "src/data/*.ts",
                "src/pages/Upload.tsx",
                "scripts/*.ts",
            ],
        ),
        root,
    )
    print_section(
        "Notes files",
        glob_many(root, ["notes/*.md"]),
        root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
