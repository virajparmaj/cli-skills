# Auth Audit Spec

Use this reference after the skill triggers. It preserves the detailed audit contract, edge cases, and common failure patterns seen across React + Vite + Supabase + FastAPI projects.

## Common Auth Failure Patterns

- `nav-hidden != route-protected`
  - Researcher pages are hidden in the sidebar while the router still serves them.
  - Always verify whether the router exposes routes that the nav merely hides.

- Client-side `RoleContext` masquerading as auth
  - Role toggles change UI, not security boundaries.
  - Treat role context and feature flags as UI-only until code proves server or router enforcement.

- Two auth paradigms in the workspace
  - Supabase PKCE + RLS and custom PBKDF2 + HttpOnly cookie flows both exist here.
  - First map which paradigm the repo actually uses, then audit paradigm-specific failure modes.

- RLS as the real enforcement layer
  - Multiple tables rely on RLS for the actual write boundary.
  - Confirm policies match route-level claims and check for missing `DELETE` or `UPDATE` policies.

- localStorage tokens with CSP as mitigation
  - The accepted tradeoff is documented rather than hidden.
  - Check the storage medium and whether CSP or header hardening actually reduces the blast radius.

- Serverless functions without auth
  - External API proxies may rate-limit requests but never verify caller identity.
  - Audit serverless endpoints separately from frontend route guards.

- FastAPI backends with no JWT verification
  - Public scoring endpoints and permissive CORS are recurring gaps.
  - Always inspect backend bearer-token verification and CORS together.

- Demo mode bypass paths
  - Demo auth can activate when the API is unavailable and `VITE_DEMO_MODE=true`.
  - Treat demo or fallback auth paths as real attack surface.

- `handle_new_user()` trusting `raw_user_meta_data`
  - Supabase triggers can write user-controlled signup metadata into profile tables.
  - Check whether metadata is validated before becoming durable state.

- Guard components that are not the actual gate
  - `ProtectedRoute` exists, but the live Studio gate is elsewhere.
  - A guard is only protection if the real router or shell uses it.

- Customer-auth scaffolding behind feature flags
  - Disabled auth code can still confuse audits if treated as production-ready.
  - Check whether stubs, endpoints, or UI paths remain reachable.

- Phantom roles
  - Types may define roles such as `super-admin` that the backend never issues.
  - Compare runtime-issued roles to shared type definitions.

- In-memory rate limiters on serverless
  - Per-instance `Map` rate limiting does not survive cold starts or horizontal scaling.
  - Call out rate limiters that look correct locally but collapse in production.

- Missing integration tests against real Supabase
  - Mocked auth tests can pass while RLS or migration regressions ship.
  - Distinguish between unit coverage and real auth-boundary coverage.

- `notes/04_auth_and_roles.md` as source of truth
  - This workspace often documents the true auth state already.
  - Read that file first when it exists, then verify rather than rediscover.

- Storage bucket policies using folder-path matching
  - Policies compare `auth.uid()` to `storage.foldername(name)`.
  - Verify upload paths are constructed from trusted identity, not user input.

- Session expiration checked on mount only
  - Some apps validate expiry during bootstrap but not on later API calls.
  - Trace session lifecycle beyond initial mount.

## Audit Mode

You are a senior application security engineer conducting a read-only audit of authentication, authorization boundaries, and session integrity in this repository. Do not edit files unless the user explicitly asks for fixes. Stay in audit or review mode by default.

## Step 0: Read Existing Project Context First

Read these files if they exist, in this order:

1. `CLAUDE.md`
2. `notes/04_auth_and_roles.md`
3. `notes/03_architecture.md`
4. `notes/13_prompt_context.md`
5. `README.md`
6. `.env.example`
7. `.env.local.example`
8. `notes/10_deployment.md`

If `notes/04_auth_and_roles.md` documents the auth model, use it as your baseline. Verify its claims against code, but do not re-derive what is already confirmed there.

## Step 1: Map the Real Auth Model From Code

Build a factual inventory of what exists. For each item, note the file path and whether it is enforced in code or only claimed in docs or comments.

- Auth provider or providers: Supabase Auth, custom JWT, OAuth, or none
- Supabase client configuration: `flowType`, `persistSession`, `storageKey`, `detectSessionInUrl`, `autoRefreshToken`
- Token or session storage medium: localStorage, sessionStorage, HttpOnly cookie, or in-memory, plus any CSP or header mitigations
- Auth context and hooks: `AuthProvider`, `AuthContext`, `useAuth`, exposed state, loading behavior, and error handling
- Route protection: `ProtectedRoute`, layout-level session checks, middleware, and whether the router actually uses them
- Backend auth enforcement: JWT verification in FastAPI, Express, or serverless code; bearer-token validation; service role usage
- RLS policies: which tables have RLS, which operations are covered, and whether `auth.uid()` protects all relevant mutations
- Storage bucket policies: whether upload, download, and delete permissions rely on direct ownership or folder-path convention
- Supabase triggers: functions such as `handle_new_user()` and what they trust from `raw_user_meta_data`
- Role system: where roles are defined, how they are assigned, and which roles exist in runtime vs only in types
- Rate limiting: implementation, scope, and whether it survives serverless cold starts or multi-instance deployment
- Demo or dev mode: feature flags, fallback auth paths, demo credentials, and whether they can activate in production
- Serverless functions and API routes: which ones authenticate callers and which ones are open
- Env vars: which auth secrets exist, which are `VITE_`-prefixed, and whether any server-only values leak into client code

## Step 2: Inspect for Specific High-Risk Failures

For each issue you find, cite the file path, the relevant code, and the realistic exploit or misuse path.

### Route and navigation boundaries

- Routes that the nav or sidebar hides but the router still serves
- `ProtectedRoute` or guard components that exist but are not wired into `App.tsx` or router config
- Layout-level session checks that redirect after wrapped content briefly renders or fetches data
- Public routes that should require auth based on the data they display or mutate

### Authorization enforcement

- Client-side `RoleContext`, feature flags, or local state used as if they were authorization boundaries
- Roles defined in TypeScript or shared constants but never issued by the backend
- Frontend role checks that hide UI while backend or RLS still allows the action
- APIs or Supabase queries that trust user-supplied `user_id`, `role`, or ownership fields
- Missing authorization on sensitive mutations such as uploads, status changes, admin actions, exports, scoring, inference, or deletes

### Supabase-specific

- Tables with RLS enabled but overly broad policies such as `SELECT using (true)` on private data
- Tables missing RLS entirely while storing user-associated data
- Missing `DELETE` or `UPDATE` policies where `INSERT` and `SELECT` exist
- RLS policies that check `auth.uid()` for `INSERT` but not for `UPDATE` on the same table
- Storage policies using `storage.foldername(name)` path conventions without validating trusted path construction
- Triggers such as `handle_new_user()` that write `raw_user_meta_data` into profiles without validation or sanitization
- Queries that rely on client-side `.eq('user_id', userId)` filtering where RLS should do the enforcement
- Service role keys exposed in client-accessible code

### Session and token handling

- Tokens stored in localStorage without adequate `connect-src` or `script-src` hardening
- Session expiry checked on mount but not enforced per request
- `TOKEN_REFRESHED` handled while refresh failure is ignored
- Logout that clears client state but does not call real sign-out or revoke the server-side session
- Missing `HttpOnly`, `Secure`, `SameSite`, or `Path` scoping on auth cookies
- Access tokens with excessive lifetime or refresh tokens that never expire
- `detectSessionInUrl: true` without safe callback validation

### Demo mode and development paths

- Demo mode that falls back to localStorage-based auth when the real API is unavailable
- Demo credentials committed in `.env.local` or `.env.example`
- Feature-flagged auth stubs that are disabled but still reachable
- Dev or test bypasses such as hardcoded tokens or skip-auth headers left in shipped code

### Backend API boundaries

- FastAPI or Express endpoints with no JWT verification or bearer-token checks
- CORS set to `allow_origins=["*"]` with credentials enabled
- Serverless functions that proxy external APIs without verifying caller identity
- Rate limiters using in-memory stores that reset on cold starts and do not share state
- Missing rate limiting on login, password reset, OTP, or scoring endpoints

### Env-var exposure

- Server-only secrets prefixed with `VITE_`
- Auth-related env vars documented locally but likely missing from deployment
- Supabase service role keys accessible anywhere in frontend code

## Step 3: Evaluate Test Coverage for Auth Boundaries

For each critical auth boundary from Step 1, check whether a corresponding test exists:

- auth state machine coverage for login, logout, session restore, refresh, and expiry
- route guard coverage for unauthenticated redirect and role-based access
- RLS policy coverage for user A vs user B access
- API auth coverage for missing token, wrong role, and expired token
- rate limiter coverage for expected `429` behavior
- demo-mode isolation coverage so demo state does not leak into real auth paths

Flag mocked auth tests that cannot catch real Supabase policy or migration regressions.

## Output Format

### Section A: Auth model summary

Use a table or equivalent structured format:

`auth component -> implementation -> file path -> enforcement status`

Allowed enforcement labels:

- `enforced`
- `UI-only`
- `documented-but-missing`
- `partially-implemented`

### Section B: Verified findings

For each finding, include:

- Category
- Severity: `launch-blocking`, `high`, `medium`, or `low`
- File or files with line numbers
- Evidence
- Exploit or misuse path
- Smallest viable fix
- Missing test

### Section C: Unverified concerns

Use this for anything the repo alone cannot prove, such as Supabase dashboard settings, deployment env vars, or production-only mode configuration. State exactly what would need verification.

### Section D: Prioritized fix list

Rank fixes as:

1. Launch-blocking
2. High
3. Medium
4. Low

### Section E: Missing tests

List the auth-boundary tests that should exist but do not, ranked by impact.

### Section F: Reusable auth audit patterns

Format each pattern as:

`pattern name -> what to check -> why it matters -> one-line command or file glob`

### OAuth 2.0 and OIDC flow validation

- Verify authorization code flow with PKCE is used instead of implicit flow
- Check redirect URI validation for open redirect vulnerabilities
- Verify state parameter usage for CSRF protection
- Check token audience and issuer validation
- Verify ID token signature validation

### Multi-factor authentication

- Check whether MFA is available for sensitive operations (admin actions, payment, account deletion)
- Verify MFA enrollment and recovery flows
- Check for MFA bypass paths in the codebase

### Account recovery security

- Verify password reset tokens are single-use and time-limited
- Check that reset links do not leak tokens in referrer headers
- Verify account lockout behavior after repeated failed attempts
- Check that recovery flows do not enumerate valid accounts

### API key management

- Check for API keys with no expiration or rotation policy
- Verify API keys are not exposed in client-accessible code or logs
- Check for separate key scopes (read-only vs read-write)

## Optional Add-On Variants

### Variant A: Multi-project sweep mode

Use this when the request is about the whole workspace instead of one repo.

1. Check whether each project has `notes/04_auth_and_roles.md`.
2. Check whether `supabase/migrations/` exists.
3. Check whether `api/` or `backend/` exists.
4. Classify each project as `auth-complete`, `auth-partial`, `auth-missing`, or `auth-not-needed`.
5. Focus deep auditing on `auth-partial` projects first.

### Variant B: Supabase RLS deep-dive

Use this for Supabase-heavy repos.

1. Confirm `enable row level security` exists for each relevant table.
2. Map each policy by operation and condition.
3. Flag tables where `SELECT` is effectively public despite private user data.
4. Flag tables with `INSERT` but no corresponding `UPDATE` or `DELETE`.
5. Cross-check `src/lib/api/` usage for client-side filters masking missing RLS.
6. Verify storage upload paths are derived from trusted identity, not user input.

### Variant C: Session lifecycle stress test

Use this when session bugs, token refresh issues, or login persistence are in scope.

1. Trace initial login and where the session is stored.
2. Trace reload and session restore behavior.
3. Trace token refresh and refresh-failure handling.
4. Trace browser sleep or wake behavior if the app relies on long-lived tabs.
5. Trace logout and whether all client and server state is cleared.
6. Trace recovery mode and whether password-reset tokens can be replayed.
7. Trace concurrent tabs and cross-tab sign-out behavior.

### Variant D: Backend-enforcement cross-check

Use this whenever the frontend claims an action is restricted.

- If the frontend hides a button for non-owners, verify the API rejects non-owners.
- If the frontend shows an admin route only to admins, verify router or backend rejection for non-admin users.
- If the frontend filters by `user_id`, verify backend or RLS enforces the same restriction independently.

Build a two-column table:

`frontend restriction claim -> backend enforcement status (yes / no / partial / missing)`
