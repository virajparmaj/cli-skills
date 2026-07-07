---
name: v-venv-doctor
description: "Diagnose per-project Python environments on Apple Silicon and emit an ordered fix list: arm64 vs Rosetta, missing libomp for xgboost, accidental global-venv usage, and pin drift against the project's ML stack. Use when a Python/ML project won't set up cleanly on a MacBook M1/M2, xgboost or scipy misbehave, or you suspect the wrong interpreter is active. Key capabilities: detect project-local venv vs the global ~/.venvs/global interpreter, report interpreter architecture and Python version, diff installed packages against requirements.txt and the pinned stack (numpy 2.1.2, pandas 2.2.3, scikit-learn 1.5.2, xgboost 2.1.0, statsmodels 0.14.4), run xgboost/libomp and core-stack import smoke tests, and produce one status table plus exactly one bash block of ordered fix commands. Trigger phrases: fix my venv, run the env doctor, xgboost won't import on my mac, library not loaded libomp, check this project's python environment, why is numpy building from source, am I on the right python."
---

# venv Doctor (Apple Silicon)

Diagnose a project's Python environment on an M-series Mac and hand back an ordered set of fix commands.

## Quick flow

1. Read repo context if present: `CLAUDE.md`, `requirements.txt`, `pyproject.toml`, `README.md`.
2. Run `scripts/venv-doctor.sh <repo>` to gather facts: venv presence and whether the active env is the global one, interpreter arch/version, pip drift vs `requirements.txt` and the pinned stack, xgboost/libomp status, and a core-stack import smoke test.
3. Load [references/venv-playbook.md](references/venv-playbook.md) for the failure-mode table and the strict output contract.
4. Turn the facts into the status table + ordered fix block.

## Output contract (strict)

- First a status table: `check | result | pass/fail`.
- Then exactly one fenced `bash` code block of ordered fix commands (most fundamental first: create/activate venv → `brew install libomp` → reinstall pinned stack), and nothing after it.
- Include only commands that address a real FAIL/WARN from the table.
- If everything passes, say "environment healthy" and emit no bash block.

## What it checks (Apple Silicon focus)

- Per-project venv present and active vs the global `~/.venvs/global` interpreter (Veer's rule).
- arm64 native vs x86_64 under Rosetta; Python 3.11.x.
- `libomp` present for xgboost (the classic macOS import failure).
- Packages installed from arm64 wheels, not compiled from sdist.
- Version drift against `requirements.txt` and the pinned ML stack.

## Scope boundary

- General dependency/dead-code audits → `v-scripts`.
- CI/deployment environment issues → `v-production`.
- This skill is local Python environment setup on macOS only.

See [references/venv-playbook.md](references/venv-playbook.md) for the failure-mode table, pinned stack, and output contract.
