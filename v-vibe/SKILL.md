---
name: v-vibe
description: "Review-only post-vibe-code architecture and maintainability audit for Vite/React/TypeScript apps with Tailwind/shadcn and optional Supabase, FastAPI, or Vercel backends. First read repo context files (CLAUDE.md, notes/*, README.md, PRODUCTION_READY.md) and do not repeat known issues unless there is a delta. Map stack/auth/data/tooling, inspect architecture debt, dead code/deps, demo-vs-prod splits, state/type drift, config/doc drift, bundle health, and tests. Output verified findings with file refs, severity, smallest fix, missing tests, cleanup backlog, reusable rules, and what's good. Trigger on audit repo, post-vibe review, maintainability audit, architecture debt."
---

# Post-Vibe-Code Architecture Audit

Use this skill when the task is to inspect a repo, not to fix it. Stay in review mode unless the user explicitly asks for implementation.

## Quick Start

- Run `python3 "<skill-path>/scripts/repo_audit_inventory.py" --repo "<repo>"` first.
- If the repo is a Vite/React app, read [references/workspace-patterns.md](references/workspace-patterns.md) before writing findings.
- Build a short mental model of the app before judging quality.

## Workflow

1. Absorb repo context before code.
   - Read, in order, if present:
     1. `CLAUDE.md`
     2. `notes/13_prompt_context.md`
     3. `notes/03_architecture.md`
     4. `notes/04_auth_and_roles.md`
     5. `notes/11_known_issues.md`
     6. `notes/10_deployment.md`
     7. `notes/05_database_schema.md`
     8. `README.md`
     9. `PRODUCTION_READY.md`
   - Treat these files as the source of truth for deliberate tradeoffs, resolved issues, and known gaps.
   - Do not rereport tracked issues unless the issue worsened or produced a new symptom. Report the delta only.
   - If the repo lacks `notes/` or other context files, say so; that is itself a maintainability finding.

2. Map the repo.
   - Read `package.json`, `tsconfig.json`, `tsconfig.app.json`, `vite.config.*`, `tailwind.config.*`, `vercel.json`, `.env.example` or `.env`, ESLint config, `supabase/`, `api/` or `backend/`, and `.github/workflows/` when present.
   - Produce a compact summary of:
     - what the app does
     - deployment target
     - data layer
     - auth model
     - build and test toolchain

3. Inspect architecture and maintainability debt.
   - Oversized files and god modules:
     - Flag files above roughly 300 LOC.
     - Include the actual line count and the responsibilities that are tangled.
   - Dead code and unused dependencies:
     - Check installed-but-unused packages, unused imports, orphan files, unused service functions, Lovable traces, and placeholder tests.
     - Explicitly check for commonly unused packages such as `@tanstack/react-query`, `recharts`, `sonner`, `framer-motion`, `next-themes`, `zod`, and `lovable-tagger`.
   - Dual demo vs production paths:
     - Check `VITE_DEMO_MODE`, `isDemoMode()`, localStorage fallbacks, and whether demo behavior diverges from real contracts.
   - Folder boundaries and responsibility leaks:
     - pages doing business logic or API work
     - components importing backend clients directly
     - inline types instead of shared `types/`
     - validation scattered instead of centralized
   - Duplication:
     - repeated query helpers
     - repeated transformations
     - frontend and backend validation drift
   - Import hygiene:
     - circular or barrel problems
     - multiple lockfiles
   - State management:
     - server data cached in global state without clear need
     - context or store god objects
     - duplicated source of truth
     - React Query installed globally but unused
   - Type safety:
     - `strict: false`
     - `any`-heavy flows
     - frontend types pretending to be backend contracts
     - enum or status vocabulary drift
     - unchecked JSON from localStorage or APIs
   - Config and documentation drift:
     - stale README or template residue
     - missing `.env.example`
     - misleading notes
     - missing CSP or HSTS when the app handles user data

4. Assess build and bundle health.
   - Flag bundles or chunks above about 500 KB.
   - Check whether heavy libraries are lazy-loaded.
   - Inspect `manualChunks`, `size-limit`, and whether `dist/` is committed.

5. Write findings in a strict audit format.
   - For each finding, include:
     - `[CATEGORY-CODE] Short title`
     - `Severity: Critical | High | Medium | Low`
     - `Status: Verified | Unverified Concern`
     - `Files: path:line`
     - `What`
     - `Why it matters`
     - `Smallest fix` as the minimum viable refactor, not a rewrite
     - `Missing tests`
   - Finish with:
     - prioritized cleanup backlog:
       - quick wins: under 30 minutes, no structural risk
       - targeted refactors: 1 to 3 hours, bounded scope
       - structural refactors: half-day or more, needs design choices
     - repeated patterns that should become reusable rules
     - what is already good and should be preserved
   - If you find a major auth or security gap, add a one-line handoff item at the end instead of a deep dive here.

## Guardrails

- Stay repo-specific. Do not give generic best-practice advice.
- Cite files or concrete patterns for every finding.
- Mark uncertainty clearly as `Verified` or `Unverified Concern`.
- Respect the repo's actual architecture; do not invent missing systems.
- Do not edit files unless the user explicitly switches from audit to implementation.

## Bundled Resources

### `scripts/repo_audit_inventory.py`

Use for deterministic discovery of:

- context files and missing context
- repo map files and backend markers
- lockfiles
- oversized source files
- placeholder test files
- common dependency and demo-mode signals

### `references/workspace-patterns.md`

Read when the repo is a Vite/React app or when you want:

- common recurring debt patterns
- stack-specific audit heuristics
- FastAPI or Supabase add-on checks
- cross-project comparison prompts
