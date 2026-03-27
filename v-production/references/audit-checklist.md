# Production Readiness, Deployment Safety, and Observability Audit

Use this reference after `SKILL.md` triggers.

## Role and ground rules

- You are an auditor, not a fixer. Report findings with evidence. Do not apply changes.
- Separate VERIFIED findings from UNVERIFIED CONCERNS.
- If the repo contains context files such as `CLAUDE.md`, `notes/10_deployment.md`, `notes/11_known_issues.md`, `notes/03_architecture.md`, `notes/04_auth_and_roles.md`, `notes/09_dev_setup.md`, `.env.example`, or `README.md`, read them first. These encode prior decisions, accepted tradeoffs, and known gaps.
- Do not re-report a known gap as a new finding unless the severity has escalated or the documentation is stale.
- Do not fabricate infrastructure context. If the deploy story depends on CI, CDN, monitoring, or another service that is not represented in the repo, say what is missing instead of assuming.

## Step 1: Map the deployment topology

Identify the tier, then follow the matching checklist:

| Tier | Signals |
| --- | --- |
| Static SPA | No `api/`, no `backend/`, no `supabase/`, no server env vars, content in `src/data/` |
| SPA plus Supabase | `supabase/` directory, `VITE_SUPABASE_URL` in env, Supabase client in `src/lib/` or `src/integrations/` |
| SPA plus Vercel serverless | `api/` directory at project root, `vercel.json` with rewrites, server-only env vars in `.env.example` |
| SPA plus external backend | `backend/` directory, `Procfile` or `Dockerfile`, `VITE_API_URL` pointing to Render, Railway, or Heroku |
| Hybrid | Combines multiple tiers such as Supabase plus Vercel serverless |

For every tier, map:

- Package scripts: `dev`, `build`, `start`, `test`, `typecheck`, `lint`
- Runtime config: `vercel.json`, `render.yaml`, `Procfile`, `Dockerfile`, `docker-compose.yml`, `.nvmrc`
- Env handling: `.env`, `.env.local`, `.env.example`, what is committed, what is gitignored, what reference file is missing
- `VITE_` prefix boundary: verify no server secret is prefixed with `VITE_`
- API base URL handling: hardcoded URLs, env fallbacks, localhost assumptions
- Feature flags and demo-mode toggles: `VITE_DEMO_MODE`, conditional `localStorage` fallbacks, demo data paths
- Health endpoints: any `/health`, `/api/health`, readiness probes
- Logging: structured logger in `src/lib/`, API request logging in `api/_lib/`, backend logging
- CI config: `.github/workflows/`, pre-commit hooks, build gates
- Test infrastructure: runner config, test file count and location, covered flows

## Step 2: Inspect for production risks

Check these issue classes.

### Environment and secrets

- [ ] `.env` committed with real credentials such as Supabase keys, API keys, or backend URLs
- [ ] No `.env.example` documenting required variables and their purpose
- [ ] Server-only secrets using `VITE_` prefix
- [ ] Hardcoded API base URLs that differ between dev, staging, and prod. Search for `localhost`, `127.0.0.1`, `.onrender.com`, `.vercel.app`
- [ ] Environment variables referenced in code but absent from `.env.example` or deploy docs
- [ ] Vercel env vars not documented in deploy notes

### Demo and production mode boundaries

- [ ] Demo mode flag exists but switching to production without required infra such as KV, encryption keys, or DB causes silent failure instead of a loud error
- [ ] `localStorage` used as production persistence for data that should survive browser clears such as orders, user data, or analysis runs
- [ ] Fallback or demo scoring and data logic diverges from the production backend
- [ ] Feature flags reference stubs that always fail when enabled

### Deployment manifests and build

- [ ] Missing `vercel.json` for a Vercel-deployed SPA
- [ ] Missing `Procfile`, `render.yaml`, or `Dockerfile` for backend services deployed to PaaS
- [ ] Drift between `notes/10_deployment.md` or `README.md` and actual runtime config
- [ ] Dual lockfiles such as `package-lock.json` plus `bun.lockb`
- [ ] `dist/` committed to git
- [ ] Build warnings normalized: chunks over 500 KB, lint errors, typecheck failures that are not gating deployment
- [ ] Missing or incomplete CI pipeline: no lint, typecheck, or test gates before deploy
- [ ] Scaffold remnants such as `.lovable/`, unused `integrations/`, React Query installed but never called

### Auth and authorization

- [ ] Auth scaffolding exists in types or components but has no runtime enforcement
- [ ] API endpoints accept requests without authentication on routes that handle sensitive data
- [ ] Client-side role switching is treated as access control
- [ ] Sign-out flow is incomplete: tokens cleared but store state, localStorage, or draft data not cleaned up
- [ ] Session tokens in localStorage without compensating CSP strictness
- [ ] Supabase RLS is present but missing for specific tables or operations
- [ ] Admin routes are accessible without auth or with demo-mode fallback credentials in the client bundle

### Server-side trust and validation

- [ ] API trusts client-supplied price, quantity, product ID, or other business-critical values without server-side verification
- [ ] No request payload schema validation at the API boundary. Look for missing Zod, Joi, or Pydantic validation
- [ ] Backend CORS allowlist will break on Vercel preview deployments or custom domains
- [ ] Rate limiting is in-memory per serverless instance

### ML and inference backend specifics

Use when `backend/` or model artifacts exist.

- [ ] Model artifact checked into git with no versioning scheme
- [ ] Scoring endpoint is unauthenticated and publicly accessible
- [ ] No `/health` endpoint or model-load validation at startup
- [ ] No backend deploy manifest such as `Procfile` or `Dockerfile`
- [ ] Model feature schema is not validated against incoming requests
- [ ] CORS on backend is not aligned with frontend deployment domains
- [ ] No request or response logging on scoring endpoints

### Observability and incident readiness

- [ ] No structured logging, or logger exists but production gets no useful logs
- [ ] No error tracking service integration such as Sentry, Datadog, or LogRocket
- [ ] No health or readiness endpoint for the primary service
- [ ] API errors returned as raw text instead of structured JSON with stable error codes
- [ ] No audit trail for security-sensitive operations such as admin login, data export, or PII access
- [ ] No monitoring hooks on critical user flows such as auth, payment or order, data upload, or scoring
- [ ] No cache or CDN headers on static assets
- [ ] No rollback documentation or instant rollback capability documented

### Supabase-specific

Use when `supabase/` exists.

- [ ] Migrations are not sequentially numbered or use inconsistent naming
- [ ] No migration runner is configured
- [ ] RLS policies do not cover all user-writable tables
- [ ] Storage bucket policies do not scope uploads to authenticated user paths
- [ ] Service role key is present anywhere in client-accessible code
- [ ] No documented backup and recovery strategy for Supabase data and storage buckets
- [ ] Image and file cleanup is not automated on parent record deletion

## Step 3: Produce findings

For each finding, provide:

| Field | Required |
| --- | --- |
| ID | `P0`, `P1`, `P2`, or `P3` |
| Title | One-line summary |
| File evidence | Exact file path and line numbers, or explicit `file not found` |
| Production failure mode | What breaks, for whom, and how it manifests |
| Smallest viable fix | Minimum change to resolve it |
| Smoke test or monitor | The automated check that should catch regression |
| Verified vs. Unverified | `VERIFIED` if proven by file evidence, `UNVERIFIED` if inferred from absence |

Priority definitions:

- `P0` launch blocker: committed secrets, unauthenticated access to sensitive data, silent data loss, production pointing at demo or localhost, missing deploy manifest for a deployed service
- `P1` launch risk: demo and prod confusion causing wrong behavior, missing security headers, client-trusting business-critical values, no error handling on critical paths
- `P2` post-launch hardening: missing observability, no integration tests, in-memory rate limiting, scaffold remnants, lint and build warnings
- `P3` improvement: missing `.env.example`, dual lockfiles, `dist/` in git, documentation drift, dead code

## Step 4: Missing test coverage

Separately list flows that lack test coverage and should be tested before or shortly after launch:

| Flow | Why it matters | Test type needed |
| --- | --- | --- |
| Example: order creation with production KV | Can silently fail without encryption key | Integration test |

Focus on flows where failure is silent or where demo-mode masking can hide a real bug.

## Step 5: Reusable audit patterns

Identify 3 to 5 repo-independent audit patterns that could become reusable skills. For each pattern, include:

- Pattern name
- What it checks
- Trigger condition
- Inputs it needs from the repo
- Example finding it would catch

Prioritize patterns that caught real issues in the current audit, not theoretical best practices.

## Output structure

Use this order:

1. Deployment Topology
2. Findings
3. `P0` Launch Blockers
4. `P1` Launch Risks
5. `P2` Post-Launch Hardening
6. `P3` Improvements
7. Unverified Concerns
8. Missing Test Coverage
9. Reusable Audit Patterns

If a severity bucket is empty, say so briefly instead of omitting it.

## Optional add-ons

### Multi-project batch mode

For workspace-wide audits, add a cross-project summary after project-level findings:

- Which projects share the same deployment gap
- Which projects have mature `notes/` and which are undocumented
- Overall secret hygiene posture
- Rank projects by `READY`, `NEEDS WORK`, `NOT DEPLOYABLE`

### Pre-launch gate

For a repo about to ship, answer:

- Is this repo safe to deploy to production today
- If no, list the exact `P0` items that must be resolved first, in dependency order
- If yes with conditions, list what must be monitored in the first 48 hours post-launch

### ML backend hardening add-on

Use for repos with `backend/artifacts/` or similar model-serving structure:

- Is the model artifact reproducible
- Does the scoring endpoint validate feature names and types against the model schema
- Is there a model card endpoint the frontend can use to validate uploads before scoring
- What happens if the model file is corrupt or missing at startup
- Is there a shadow or canary scoring path for model updates

### Supabase migration safety add-on

Review every file in `supabase/migrations/` in order:

- Is it reversible
- Does it add RLS policies for new tables
- Does it handle existing data and backfills
- Is there a documented rollback migration

Flag any migration that is destructive without a reverse migration file.
