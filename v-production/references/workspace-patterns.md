# Workspace Calibration

Use this reference when auditing Vite + React + Tailwind projects with Vercel, Supabase, or FastAPI backends. Treat these as prioritization hints, not assumptions.

## Common stack and repo shape

- Most repos use React 18 plus Vite plus TypeScript plus Tailwind plus shadcn.
- Deployment usually falls into one of four real patterns: static SPA, SPA plus Supabase, SPA plus Vercel serverless, or SPA plus Python FastAPI on a hosted platform. Hybrids exist.
- Mature repos tend to include `CLAUDE.md` and a numbered `notes/00_` to `notes/13_` set. Read those before inventing findings.

## Repeated risk patterns

### Environment handling and secrets

- Secret hygiene is inconsistent. Common patterns include:
  - Committed `.env` files with hardcoded service URLs or credentials
  - Missing `.env.example` files
  - Inconsistent use of `.env.example` across projects
- `VITE_` prefix boundary mistakes are high-value checks because Vite exposes those vars to the client bundle.

### Demo versus production confusion

- Some projects use `VITE_DEMO_MODE` and can fail silently when switching to production without required keys or services.
- Fallback scoring logic or demo paths can diverge from the live backend.
- Several projects use `localStorage` as a production database substitute.

### Auth enforcement is uneven

- Mature projects may have Supabase Auth with PKCE, named storage key, full sign-out cleanup, and RLS on every table.
- Others have real admin auth but customer auth is still a stub, or `ProtectedRoute` is not the real gate.
- Some expose scoring or data APIs with no auth while handling sensitive data.
- Some repos have auth-flavored types and components without runtime enforcement.

### Vercel config maturity correlates with deployment risk

- Some repos are missing `vercel.json` entirely.
- Strong examples include HSTS, CSP, CORP, COEP, COOP, and immutable asset caching.
- Weaker examples still allow `unsafe-inline` and `unsafe-eval`.

### ML backend pattern has recurring gaps

- The common shape is FastAPI plus `joblib` plus `scikit-learn` or `xgboost`, with model artifacts committed under `backend/artifacts/`.
- Common gaps include missing backend deploy manifests, missing health checks, missing model versioning, and missing auth on scoring endpoints.

### Test coverage is sparse

- Most projects have little or no automated test coverage.
- Integration tests against real backends are generally absent.

### Scaffold remnants are meaningful, not cosmetic

- Generated directories, dual lockfiles, generated integration folders, and installed-but-unused libraries appear across multiple repos.
- Treat these as signals of deployment drift, dependency ambiguity, or incomplete hardening.

### Lint and build failures may have been normalized

- Some repos ship with lint failures or very large bundles.
- Chunk warnings over 500 KB should be treated as a deployment-readiness signal.

### Server-side trust of client data is a real failure mode

- Order paths or mutation endpoints that trust client-supplied values instead of enforcing server-side values from authoritative data.
- Missing schema validation at the API boundary is common.

### Rate limiting is often best-effort only

- In-memory rate limiting exists in some serverless paths and can reset on cold start.
- KV-backed rate limiting is stronger, but still needs a behavior story for outage and fallback modes.

## Additional production checks

- Rollback strategy: verify the project has a documented or automated rollback plan for failed deployments.
- Database backup and recovery: verify backup schedules, retention policies, and tested recovery procedures.
- CDN and edge caching: verify cache headers, invalidation strategy, and stale-content risk for static assets.
- Monitoring and alerting: verify health check frequency, alert thresholds, error rate monitoring, and on-call escalation paths.

## Audit posture

- Assume the repo may have thoughtful notes even when code quality is mixed.
- Favor findings tied to launch safety over generic cleanup advice.
- When a documented tradeoff is intentional, downgrade it unless the implementation evidence shows the risk is now worse than the docs claim.
