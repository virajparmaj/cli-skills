---
name: v-venv-doctor
description: "Diagnose a project Python environment on Apple Silicon: interpreter selection, architecture, dependency drift, and native import failures. Use for local setup problems; honor project pins over historical defaults."
---

# venv Doctor (Apple Silicon)

Diagnose a project's Python environment on an M-series Mac and hand back an ordered set of fix commands.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Use the project lockfile, supported Python version, and dependency declarations as the authority; historical stack pins are examples only. Execute repairs when requested, preserving the existing environment until a replacement works.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `requirements.txt`, `pyproject.toml`, `README.md`.
2. Run `scripts/venv-doctor.sh <repo>` to gather facts: venv presence and whether the active env is the global one, interpreter arch/version, dependency drift vs project requirements, xgboost/libomp status, and a core-stack import smoke test.
3. Load [references/venv-playbook.md](references/venv-playbook.md) for the failure-mode table and the strict output contract.
4. Turn the facts into the status table + ordered fix block.

## Output contract (strict)

- First a status table: `check | result | pass/fail`.
- Then exactly one fenced `bash` code block of ordered fix commands (most fundamental first: create/activate venv → `brew install libomp` → reconcile project requirements), and nothing after it.
- Include only commands that address a real FAIL/WARN from the table.
- If everything passes, say "environment healthy" and emit no bash block.

## What it checks (Apple Silicon focus)

- Per-project venv present and active vs the global `~/.venvs/global` interpreter (Veer's rule).
- arm64 native vs x86_64 under Rosetta; Python version against the project's declared requirement.
- `libomp` present for xgboost (the classic macOS import failure).
- Packages installed from arm64 wheels, not compiled from sdist.
- Version drift against project requirements; historical pins apply only if the project explicitly adopts them.

## Scope boundary

- General dependency/dead-code audits → `v-scripts`.
- CI/deployment environment issues → `v-vibe-app` or `v-vercel-doctor`.
- This skill is local Python environment setup on macOS only.

See [references/venv-playbook.md](references/venv-playbook.md) for the failure-mode table and output contract.
