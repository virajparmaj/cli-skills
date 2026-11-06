#!/usr/bin/env python3
"""Clear outputs from explicitly selected notebooks, replacing changed files atomically."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


def strip_outputs(path):
    path = path.resolve(strict=True)
    if path.suffix != ".ipynb" or not path.is_file():
        raise ValueError(f"not a notebook file: {path}")
    # Read and validate before opening any file for writing.
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("cells"), list):
        raise ValueError(f"notebook has no cells array: {path}")
    if any(not isinstance(cell, dict) for cell in document["cells"]):
        raise ValueError(f"notebook contains a non-object cell: {path}")
    changed = False
    for cell in document["cells"]:
        if cell.get("cell_type") == "code":
            if cell.get("outputs") != [] or cell.get("execution_count") is not None:
                changed = True
            cell["outputs"] = []
            cell["execution_count"] = None
    if not changed:
        return False
    payload = json.dumps(document, ensure_ascii=False, indent=1) + "\n"
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", type=Path, nargs="+", help="Explicit notebook paths (shell globs allowed)")
    args = parser.parse_args()
    failed = False
    for path in args.notebooks:
        try:
            print(f"{'cleared' if strip_outputs(path) else 'unchanged'}: {path}")
        except (OSError, ValueError) as exc:
            print(f"ERROR: {path}: {exc}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
