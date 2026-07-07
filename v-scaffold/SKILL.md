---
name: v-scaffold
description: "Scaffolds a new project in Veer's exact stack conventions with one command, choosing a web or python track. Web track: Vite + React 18 + TypeScript strict + Tailwind + shadcn/ui, types/ directory, lib/supabase.ts typed-client stub, .env.example committed, ErrorBoundary component, and vercel.json skeleton. Python track: per-project venv on Python 3.11, pyproject with Black line-length 100 + isort, his pinned ML stack (numpy 2.1.2, pandas 2.2.3, scipy 1.14.1, scikit-learn 1.5.2, xgboost 2.1.0, statsmodels 0.14.4, matplotlib 3.9.2, seaborn 0.13.2, structlog), src/ layout, and a clean starter notebook in config->data->preprocessing->modeling order with success prints. Ends with an initial commit in his format and a strict manifest of every file created, with no extra dependencies or boilerplate. Trigger phrases: scaffold a new web app, new project in my stack, set up a python project my way, bootstrap a vite shadcn repo, new repo my conventions."
---

# Project Scaffolder

Bootstrap a new repo in Veer's documented conventions, one command, no assembling from memory.

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

1. Pick the track from the request:
   - **web** — Vite + React 18 + TypeScript strict + Tailwind + shadcn/ui (add `--supabase` if it needs Supabase).
   - **python** — Python 3.11 ML/data project with venv, Black+isort, pinned ML stack.
2. Confirm the target directory and project name. Default the name to the directory basename. Ask only if the directory is ambiguous.
3. Run the deterministic scaffolder. It writes only convention files and prints a manifest:
   - Web: `scripts/scaffold-web.sh <target-dir> [project-name] [--supabase] [--force]`
   - Python: `scripts/scaffold-py.sh <target-dir> [package-name] [--no-venv] [--no-notebook] [--force]`
4. Read the script's `=== manifest (created) ===` and `=== next steps ===` sections. Do not re-invent files — the script owns the deterministic layout. If the user asked for a feature not in the convention list (extra deps, routing, auth), add it as a clearly separate follow-up step, not baked into the scaffold.
5. Finish with an initial commit in Veer's format (see Output contract). Only run install/commit commands when the user asks you to; otherwise present them as the block to run.

## What each track writes

Read [references/conventions.md](references/conventions.md) for the exact file list, pinned versions, and the reasoning behind each convention. Never pad the scaffold beyond that list.

- **Web:** `package.json`, `tsconfig.json` (strict, `@/*` alias), `vite.config.ts`, `tailwind.config.ts`, `postcss.config.js`, `components.json` (shadcn), `index.html`, `src/main.tsx`, `src/App.tsx`, `src/index.css`, `src/lib/utils.ts` (cn), `src/components/ErrorBoundary.tsx`, `src/types/index.ts`, `vercel.json`, `.gitignore`, `.env.example`, `README.md`, `src/vite-env.d.ts`. With `--supabase`: `src/lib/supabase.ts` typed client + `src/types/supabase.ts` + Supabase env vars.
- **Python:** `pyproject.toml` (Black line-length 100, isort black profile, pinned deps), `requirements.txt`, `requirements-dev.txt`, `src/<pkg>/__init__.py`, `src/<pkg>/data.py`, `tests/test_data.py`, `notebooks/01_explore.ipynb` (config->data->preprocessing->modeling with `✅` success prints), `data/.gitkeep`, `.gitignore`, `README.md`, and a `.venv/` created with Python 3.11.

## Output contract (strict)

After the scaffolder runs, produce exactly two things:

1. A **manifest** — a fenced code block listing every file created, one relative path per line, taken verbatim from the script's `=== manifest (created) ===` section (sorted). If any files were skipped because they already existed, list them under a `# skipped (already existed)` comment inside the same block.
2. A **commands** block — one fenced `bash` code block the user can run as-is: the install/setup commands from the script's `=== next steps ===`, then the initial commit in Veer's exact format:

```bash
git init
git add .

git commit -m "<type> : <summary 4-5 words>" \
  -m "- scaffold <web|python> project
- <convention set applied>
- <notable extra, e.g. supabase client stub>"
```

- Use `chore` as the commit type for a plain scaffold (`feat` only if the scaffold ships real user behavior).
- Do not add files, dependencies, or config beyond what the scaffolder wrote. If more is needed, say so as a separate follow-up outside the two blocks.

## Edge cases

- **Target directory already has files:** the scaffolder skips existing convention files by default and reports them under `=== manifest (skipped) ===`. Surface those to the user; only pass `--force` if they explicitly want overwrites.
- **No Python 3.11 on PATH (python track):** the script writes all files but reports `venv NOT created` with the exact fix command. Relay that; do not silently proceed as if the venv exists.
- **User names a track that already exists as its own concern:** this skill only bootstraps. For git commit wording use v-git; for de-Lovable cleanup of an existing repo use v-delovable; for a Supabase migration workflow use v-supa-migrate. State the boundary instead of duplicating those jobs.
- **Nothing created (all skipped):** report the empty-created manifest honestly and recommend `--force` or a fresh directory rather than committing a no-op.

## Boundary with other skills

This skill creates a brand-new repo skeleton. It does not audit or refactor existing code (see v-vibe, v-scripts), does not write project docs (see v-notes), and does not deploy or configure Vercel beyond the SPA-rewrite skeleton (see v-vercel-doctor).

See [references/conventions.md](references/conventions.md) for the full convention list, pinned versions, and rationale this skill enforces.
