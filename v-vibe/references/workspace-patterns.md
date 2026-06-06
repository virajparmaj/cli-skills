# Workspace Patterns

Use this reference when auditing Vite/React/TypeScript apps with Tailwind/shadcn and optional Supabase, FastAPI, or Vercel backends.

## Repo Family Shape

- Common stack: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui.
- Common frontend layout: `src/pages` or `src/views`, `src/components`, `src/hooks`, `src/lib`, `src/services` or `src/store`, `src/types`.
- Common backend variants:
  - `supabase/` plus direct client access
  - `api/` Vercel functions
  - `backend/` FastAPI scoring services
- Common context files:
  - `notes/00-14*.md`
  - `CLAUDE.md`
  - `PRODUCTION_READY.md`
- Some repos are richly documented; some have sparse notes. Missing context is itself signal.

## Recurring Cleanup Issues

- Installed-but-unused dependencies recur often. Check these first:
  - `@tanstack/react-query`
  - `recharts`
  - `sonner`
  - `framer-motion`
  - `next-themes`
  - `zod`
- `strict: false` in TypeScript config is common.
- shadcn/ui lint failures recur in `command.tsx` and `textarea.tsx`.
- Multiple lockfiles appear in the same repo (`package-lock.json` plus `bun.lockb` or `bun.lock`).
- Scaffold residue appears via template tagger packages, template README text, and generated directories.
- Placeholder tests like `src/test/example.test.ts` create false coverage signals.

## Recurring Architecture Debt

- God files are common. Look for files above 300 LOC with tangled responsibilities.
- Dual demo and production code paths recur in projects with `VITE_DEMO_MODE` or localStorage fallbacks.
  - Look for localStorage fallbacks that quietly diverge from backend or API contracts.
- Data-authority drift is a repeating problem:
  - server trusting client-supplied fields
  - frontend enum or status strings drifting from API contracts
  - settings or admin UI that looks real but does not persist
- React Query is sometimes globally wired but unused through `useQuery` or `useMutation`.

## Auth And Security Weak Spots

- UI-only roles or hidden navigation without backend enforcement
- scaffolded auth left disabled behind flags
- missing `ProtectedRoute` or route guards
- unauthenticated API endpoints
- permissive CORS carried from dev into prod
- missing `.env.example`
- committed `.env` or risky env handling
- client-side-only rate limiting
- missing CSP headers

## Build And Deployment Pitfalls

- Vite chunk warnings above 500 KB are common; some main bundles exceed 2 MB.
- Heavy libraries worth checking for lazy loading:
  - `recharts`
  - `framer-motion`
  - `leaflet`
  - `three`
  - `pdf-lib`
- Hosted backends may have cold-start risk and no warm-up path.
- `vercel.json` SPA rewrites can shadow API routes.

## Testing Reality

- Many repos have zero real tests or only placeholder tests.
- Missing coverage often includes auth flows, RLS, API error paths, and integration or E2E paths.

## CI/CD And Maintenance Health

- Check CI/CD pipeline configuration: missing or incomplete pipelines, no automated testing in CI, no lint checks in CI.
- Dependency freshness: check for outdated dependencies with known vulnerabilities, stale lockfiles, and packages multiple major versions behind.
- Code ownership: assess bus factor by looking at contributor patterns, undocumented complex modules, and single-author critical paths.

## Audit Add-Ons

### Cross-Project Comparison Mode

Use when the user wants this repo compared against sibling projects.

Compare against common tendencies:

- TypeScript strict mode: often off
- Test count: often zero or placeholder only
- Bundle size: often 500 KB to 1 MB or higher
- Auth implementation: often absent, mock, or partially wired
- CSP headers: often missing
- `.env.example`: often missing

### FastAPI Or ML Backend Add-On

If `backend/` or model artifacts exist, also inspect:

- committed model artifacts such as `joblib` or `pickle`
- fallback heuristics diverging from the live model contract
- health or model-card endpoints
- CORS carrying dev origins into production
- missing request auth
- cold-start risk
- input validation on `/score` or `/predict`

### Supabase Add-On

If `supabase/` exists, also inspect:

- missing RLS on tables
- `WITH CHECK (true)` or inserts not scoped to `auth.uid()`
- migrations adding columns without safe defaults
- generated type files drifting against the latest migration

## Positive Baselines To Preserve

- Strong patterns to look for: strict TypeScript, typed Supabase client, CI plus `size-limit`, real tests, rich `notes/` and `prompt_context` docs.
- Rich `notes/` and prompt-context docs are a strength. Use them to avoid re-reporting known issues and to preserve deliberate design choices.
