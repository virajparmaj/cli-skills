---
name: v-scaffold
description: "Bootstrap a new web or Python project using Veer's documented stack and bundled scaffold scripts. Use for new project setup, not changes to an existing application."
---

# Project Scaffolder

Bootstrap a new repo in Veer's documented conventions, one command, no assembling from memory.

## Evidence and execution

Inspect the destination before writing; preserve existing files unless overwrites were explicitly requested. Report the actual manifest and failed setup steps; do not claim dependencies or environments were installed unless verified.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

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
git init -b main
git add -- <files from the created manifest>

git commit -m "<type> : <summary 4-5 words>" \
  -m "- scaffold <web|python> project
- <convention set applied>
- <notable extra, e.g. supabase client stub>"
```

- Before any authorized commit, verify author and committer are `virajparmaj <viraj.parmaj89@gmail.com>`; preserve unrelated existing edits and omit AI attribution. Use `main` for personal projects, except an explicitly requested or contribution workflow.
- Use `chore` as the commit type for a plain scaffold (`feat` only if the scaffold ships real user behavior).
- Do not add files, dependencies, or config beyond what the scaffolder wrote. If more is needed, say so as a separate follow-up outside the two blocks.

## Edge cases

- **Target directory already has files:** the scaffolder skips existing convention files by default and reports them under `=== manifest (skipped) ===`. Surface those to the user; only pass `--force` if they explicitly want overwrites.
- **No Python 3.11 on PATH (python track):** the script writes all files but reports `venv NOT created` with the exact fix command. Relay that; do not silently proceed as if the venv exists.
- **User names a track that already exists as its own concern:** this skill only bootstraps. For git commit wording use v-git; for de-Lovable cleanup of an existing repo use v-declutter; for a Supabase migration workflow use v-supa-migrate. State the boundary instead of duplicating those jobs.
- **Nothing created (all skipped):** report the empty-created manifest honestly and report that nothing changed; use a fresh directory or `--force` only when overwrites are explicitly requested. Do not commit a no-op.

## Boundary with other skills

This skill creates a brand-new repo skeleton. It does not audit or refactor existing code (see v-vibe, v-scripts), does not write project docs (see v-notes), and does not deploy or configure Vercel beyond the SPA-rewrite skeleton (see v-vercel-doctor).

See [references/conventions.md](references/conventions.md) for the full convention list, pinned versions, and rationale this skill enforces.
