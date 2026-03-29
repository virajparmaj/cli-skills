from __future__ import annotations

from pathlib import Path


FALLBACK_CODE_ROOT = Path("/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon")


def _is_code_root(candidate: Path) -> bool:
    return (
        (candidate / "src").is_dir()
        and (candidate / "scripts").is_dir()
        and (candidate / "config").is_dir()
    )


def _first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def resolve_datathon_paths(start: Path | None = None) -> dict[str, Path]:
    anchor = (start or Path.cwd()).resolve()

    code_root: Path | None = None
    for candidate in [anchor, *anchor.parents]:
        if _is_code_root(candidate):
            code_root = candidate
            break
        if candidate.name == "1" and _is_code_root(candidate.parent):
            code_root = candidate.parent
            break

    if code_root is None:
        code_root = FALLBACK_CODE_ROOT if _is_code_root(FALLBACK_CODE_ROOT) else anchor

    bundle_candidates: list[Path] = []
    for candidate in [anchor, *anchor.parents]:
        if (candidate / "data" / "raw").is_dir() and (candidate / "notes").is_dir():
            bundle_candidates.append(candidate)
            break

    legacy_bundle = code_root / "1"
    if (legacy_bundle / "data" / "raw").is_dir() and (legacy_bundle / "notes").is_dir():
        bundle_candidates.append(legacy_bundle)
    if (code_root / "data" / "raw").is_dir() and (code_root / "notes").is_dir():
        bundle_candidates.append(code_root)

    bundle_root = bundle_candidates[0] if bundle_candidates else code_root

    return {
        "code_root": code_root,
        "bundle_root": bundle_root,
        "raw_dir": _first_existing([
            code_root / "data" / "raw",
            bundle_root / "data" / "raw",
        ]),
        "template_path": _first_existing([
            code_root / "data" / "template_forecast_v00.csv",
            bundle_root / "data" / "template_forecast_v00.csv",
        ]),
        "notes_root": _first_existing([
            bundle_root / "notes",
            code_root / "notes",
        ]),
        "reports_dir": code_root / "outputs" / "reports",
        "forecasts_dir": code_root / "outputs" / "forecasts",
        "notebooks_dir": code_root / "notebooks",
        "legacy_notebooks_dir": _first_existing([
            bundle_root / "notebooks",
            code_root / "notebooks",
        ]),
    }
