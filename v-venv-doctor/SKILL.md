---
name: v-venv-doctor
description: "Diagnose per-project Python environments on Apple Silicon and emit an ordered fix list: arm64 vs Rosetta, missing libomp for xgboost, accidental global-venv usage, and pin drift against the project's ML stack. Use when a Python/ML project won't set up cleanly on a MacBook M1/M2, xgboost or scipy misbehave, or you suspect the wrong interpreter is active. Key capabilities: detect project-local venv vs the global ~/.venvs/global interpreter, report interpreter architecture and Python version, diff installed packages against requirements.txt and the pinned stack (numpy 2.1.2, pandas 2.2.3, scikit-learn 1.5.2, xgboost 2.1.0, statsmodels 0.14.4), run xgboost/libomp and core-stack import smoke tests, and produce one status table plus exactly one bash block of ordered fix commands. Trigger phrases: fix my venv, run the env doctor, xgboost won't import on my mac, library not loaded libomp, check this project's python environment, why is numpy building from source, am I on the right python."
---

# venv Doctor (Apple Silicon)

Diagnose a project's Python environment on an M-series Mac and hand back an ordered set of fix commands.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Exhaust the search.** For discovery, keep going until two consecutive passes surface nothing new; do not stop at the first plausible batch. Never silently cap coverage — state what you skipped and why.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

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
