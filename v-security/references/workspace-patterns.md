# Workspace Patterns

## Contents

- Stack constants
- Strengths to avoid false positives
- Recurring gaps to check every time
- Deployment-specific pitfalls
- Auth and RBAC weak spots
- ML and backend-specific patterns
- Documentation hints
- Preserved tuning rationale

## Stack Constants

These recurring patterns come from React + Vite + TypeScript + Tailwind + shadcn/ui projects and should tune the audit:

- Most projects use React 18 + Vite + TypeScript + Tailwind + shadcn/ui.
- Supabase is the main BaaS when a managed backend exists.
- Backend code usually lives in Vercel serverless `api/` handlers or a FastAPI `backend/` folder.
- Frontend deployment is usually Vercel, with `vercel.json` handling rewrites and headers.

## Strengths to Avoid False Positives

- `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are intentionally public. Do not flag them unless the anon key has elevated privileges or the touched tables lack effective RLS.
- Supabase storage ownership checks that use `auth.uid()::text = (storage.foldername(name))[1]` are valid path-based ownership patterns.
- `script-src 'unsafe-inline'` can be a documented Vite trade-off. Note it accurately, but do not treat it as critical by default when the repo explicitly documents it and the rest of CSP is tight.

## Recurring Gaps to Check Every Time

- Client-side role or auth checks with no server-side enforcement.
- In-memory rate limiting on Vercel serverless handlers that can be bypassed across cold starts and instances.
- Sensitive or user-impacting data in `localStorage` (health data, PII, demo orders, sessions).
- Demo credentials shipped via `VITE_*`.
- Missing CSP headers entirely.
- Overly permissive FastAPI CORS such as `allow_methods=["*"]` or `allow_headers=["*"]`.
- `WITH CHECK (true)` on Supabase `INSERT` policies — sometimes intentional and public, sometimes a gap.
- Route protection applied to some pages but not all.
- Missing rate limiting on public endpoints.
- Missing webhook signature verification.
- Any service-role key in `VITE_*` or client-reachable code.
- File upload checks done client-side only, with no server-side MIME or size re-validation.

## Deployment-Specific Pitfalls

- `VITE_*` vars are baked into the client bundle at build time.
- Non-`VITE_*` vars are only available in server contexts such as Vercel functions.
- SPA rewrite rules in `vercel.json` can accidentally swallow `/api/*` or internal paths.
- FastAPI on hosted platforms does not add security headers by default.
- Missing `Strict-Transport-Security`, `X-Content-Type-Options`, or `X-Frame-Options` often means `vercel.json` or backend middleware was never hardened.

## Auth and RBAC Weak Spots

- Social or UGC apps often lack an admin or moderation path.
- `localStorage` session persistence is an accepted trade-off in some repos, so evaluate it together with CSP tightness instead of flagging it mechanically.
- PKCE is often present, but session-expiry or refresh handling can be inconsistent.

## ML and Backend-Specific Patterns

- Client-side fallback scoring can drift from the real production model.
- External HTTP dependencies can exist without timeouts or failure isolation.
- Model or artifact loading may happen at startup without integrity verification.

## Documentation Hints

- Repos with `notes/` usually document architecture, auth, deployment, and known issues well enough to prevent duplicate findings.
- `notes/04_auth_and_roles.md`, `notes/11_known_issues.md`, and `notes/10_deployment.md` are especially important.
- `.env.example` reliably documents expected env vars and the intended client or server boundary.

## Additional Security Checks

- Supply chain security: audit `npm audit` or `pip audit` output, verify lockfile integrity, check for typosquatting risks in dependencies.
- SSRF prevention: verify server-side URL fetching validates and restricts target hosts, blocks internal network access.
- Subdomain takeover risk: check for dangling DNS records pointing at decommissioned services (Vercel, Heroku, S3, etc.).
- Security.txt and vulnerability disclosure: check for `/.well-known/security.txt` with valid contact and policy information.

## Preserved Tuning Rationale

Keep these reasons in mind so the skill preserves the original intent:

- Load docs first because repos often document accepted trade-offs and known issues in `notes/`.
- Do not flag the Supabase anon key by default because it is intentionally exposed and documented as safe when RLS is correct.
- Check for demo credentials because some projects expose demo passwords via `VITE_*` env vars.
- Check client-side role gating without backend enforcement because some projects keep role state in React context only.
- Check serverless rate limiting carefully because in-memory state on Vercel is not durable.
- Check `localStorage` sensitivity contextually because several projects intentionally persist state there, but not all data stored is equally risky.
- Judge Supabase `WITH CHECK (true)` policies contextually because public survey or form models may legitimately use them.
- Check partial route protection because inconsistent guarding creates false confidence.
- Apply FastAPI-specific CORS and header checks because permissive middleware defaults are common.
- Include ML and backend-specific checks because model drift risk and unbounded third-party HTTP calls are real.
- Separate `VERIFIED` from `UNVERIFIED` because some exploit paths depend on dashboard settings or deploy-time env values.
- De-escalate documented trade-offs when repo docs already acknowledge them.
- Call out missing security tests separately because many repos have unit tests but little direct coverage for security paths.
- Extract reusable patterns at the end so the audit can become a reusable checklist.
- Do not recommend `X-XSS-Protection` as a hardening must-have; modern best practice can be `0`.
- Check public forms for honeypots or CAPTCHA as an anti-abuse pattern.
- Check idempotency on public writes to prevent duplicate submissions.
