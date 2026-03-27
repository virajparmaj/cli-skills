# Variants

Apply these add-on clauses only when the target repo actually matches the stack or the review goal.

## Supabase-Deep Mode

Add when the repo is Supabase-heavy:

- Check every migrated table for RLS enablement and at least one relevant policy per operation.
- Check storage bucket policies for `auth.uid()` path ownership.
- Check every `supabase.rpc()` call and any `SECURITY DEFINER` function for auth validation.
- Check that no migration or function leaks `service_role` behavior into client-reachable paths.
- Check `supabase/functions/` for JWT verification on incoming requests.
- Check `.env.example` for placeholders only, not real keys.

## Vercel Serverless Hardening

Add when the repo has multiple `api/` handlers:

- Verify every handler checks HTTP method and returns `405` for unsupported methods.
- Verify `Content-Type` validation on POST handlers.
- Check that handlers do not rely on `VITE_*` vars at runtime.
- Check that production error responses do not leak stack traces or internal paths.
- Check `vercel.json` rewrites to make sure `/api/*` is excluded from SPA catch-alls.
- Check for shared mutable module state that will not survive cold starts.

## FastAPI Backend Hardening

Add when the repo has a `backend/` FastAPI service:

- Check for raw f-string SQL queries with user input.
- Verify `CORSMiddleware` uses explicit origins rather than `["*"]`.
- Check for missing security headers middleware.
- Verify file path handling uses safe resolution and traversal boundaries.
- Check for unvalidated user-supplied file paths.
- Verify external HTTP calls have timeouts and error handling.
- Check startup behavior so missing models or artifacts fail loudly instead of serving stale state.

## Pre-Launch Gate

Add when the user asks for production readiness or a launch go/no-go:

- Add a `GO/NO-GO` section after findings.
- List every `P0` and `P1` that must be resolved before launch.
- List env vars that must exist in Vercel or Render, cross-referenced against `.env.example`.
- Verify demo mode is disabled in production.
- Verify production CORS origins are not localhost.
- Verify HTTPS is enforced, including HSTS.
- Flag dependencies with known CVEs if the lockfile or audit output shows them.
