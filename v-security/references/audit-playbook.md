# Audit Playbook

## Contents

- Phase 0: Load existing context
- Phase 1: Map the attack surface
- Phase 2: Inspect for concrete issues
- Phase 3: Structure findings
- Phase 4: Output
- Constraints

## Phase 0: Load Existing Context

Before inspecting code, read any project-level documentation that captures prior decisions, known gaps, and architecture choices.

Priority files:

- `CLAUDE.md`
- `README.md`
- `.env.example`
- `notes/04_auth_and_roles.md`
- `notes/03_architecture.md`
- `notes/11_known_issues.md`
- `notes/10_deployment.md`
- `notes/06_api_contracts.md`
- `notes/13_prompt_context.md`

If any of these exist, ingest them before Phase 1. Reference specific lines when they confirm or contradict a finding.

## Phase 1: Map the Attack Surface

Systematically locate and catalog these surfaces from the actual codebase:

| Surface | Where to look |
| --- | --- |
| Env vars and secrets | `.env*`, `.env.example`, `VITE_*` usage in `src/`, `import.meta.env.*`, `process.env.*` in `api/` or `backend/` |
| Client/server boundary | `api/`, `backend/`, `supabase/functions/` |
| Public endpoints | every exported handler in `api/`, every FastAPI route, any `supabase.functions.invoke()` call |
| Supabase RLS policies | `supabase/migrations/*.sql`, every `CREATE POLICY`, every `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` |
| Storage buckets and upload paths | Supabase storage policies, `supabase.storage.from()` call sites, and file input handlers |
| Auth flow | auth providers, `supabase.auth.*`, JWT handling, session storage choices |
| Route protection | route guards, protected-route wrappers, and which routes are guarded versus exposed |
| Third-party integrations | payment processors, proxied external APIs, webhook receivers |
| Headers and CSP | `vercel.json` headers, FastAPI middleware, `helmet`, manual header config |
| Request validators | Zod schemas, Pydantic models, `validation.ts`, or equivalent validation layers |
| Deployment manifests | `vercel.json`, `render.yaml`, `Dockerfile`, `fly.toml` |
| Test coverage | `src/test/`, `__tests__/`, `*.test.ts`, `*.spec.ts`, or backend test folders |

Return a compact surface map before moving to findings.

## Phase 2: Inspect for Concrete Issues

Only report issues tied to real files, config, or code paths. Do not pad with generic advice.

### Secrets and Credential Exposure

- Service-role keys, API keys, or privileged tokens in `VITE_*`, committed `.env` files, or source code
- Demo-mode credentials shipped via `VITE_*`
- Backend-only keys reachable from browser paths
- Secrets accidentally committed because `.gitignore` misses `.env`, `.env.local`, or credential files

### Auth and Authorization Gaps

- Client-side role or permission checks with no corresponding server-side enforcement
- Route protection applied inconsistently
- Session tokens in `localStorage` without compensating CSP tightness
- Missing session-expiry validation on page load
- PKCE flow correctness for Supabase Auth
- Missing admin or moderation controls in apps with user-generated content

### RLS and Database Layer

- Tables with RLS enabled but overly permissive policies
- Tables referenced in code but missing from migrations
- Cross-user exposure in `SELECT` policies
- Weak storage bucket policies
- Missing `UPDATE` or `DELETE` policies

### Input Validation and Injection

- XSS via `dangerouslySetInnerHTML`, unsanitized markdown, `innerHTML`, `eval()`, or `new Function()`
- Missing or client-only sanitization
- File upload validation done client-side only
- Raw SQL with user input
- URL validation gaps such as `javascript:` or open redirects
- Missing request payload size limits on public POST endpoints

### API Hardening

- Missing rate limiting on public endpoints
- In-memory rate limiting on Vercel serverless
- Missing webhook signature verification
- Missing request timeout enforcement on upstream API calls
- CORS misconfiguration
- Missing `Content-Type` enforcement on POST endpoints
- Health or status endpoints leaking server fingerprints

### Abuse Resistance

- Public form endpoints without CAPTCHA or honeypot
- Trust in client-supplied pricing, quantities, IDs, ownership claims, or status flags
- Missing idempotency on write paths
- Unauthenticated endpoints that write to the database without abuse controls
- Upload paths with no quota or ownership checks

### Headers, CORS, and Transport Security

- Missing `vercel.json` headers block
- Missing `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, or `X-Frame-Options`
- `script-src 'unsafe-inline'` that is undocumented or broader than needed
- `script-src 'unsafe-eval'` without a strong justification
- `connect-src https:` wildcards that allow exfiltration to any HTTPS endpoint
- FastAPI backends with no security header middleware
- Missing `Referrer-Policy` or `Permissions-Policy`

### Sensitive Data Leakage

- PII or sensitive domain data in `localStorage`
- Error handling, toasts, or console logs that expose internal state
- Analytics or logging that captures PII
- Sensitive data in unguarded `raw` payload columns

### ML and Backend-Specific Checks

- Fallback scoring or inference logic that diverges from the production model
- Model artifacts loaded without integrity verification
- External API dependencies without timeout, retry bounds, or failure isolation
- User-supplied paths used for file I/O without safe boundary checks

## Phase 3: Structure Findings

### Separate Verified from Unverified

For each finding, clearly mark:

- `VERIFIED`: visible vulnerable code or config with a concrete exploit path
- `UNVERIFIED`: likely vulnerable, but it depends on runtime behavior, dashboard settings, or env configuration you cannot inspect

### Finding Format

Use this format for every finding:

```text
[P0|P1|P2|P3] - <short title>
Status: VERIFIED | UNVERIFIED
File(s): path:line
Category: <Phase 2 category>
Issue: <what is wrong, with code evidence>
Abuse scenario: <who exploits it, how, and what they gain>
Fix: <smallest viable change>
Regression test: <test to prevent recurrence>
```

### Severity Scale

- `P0`: immediate blocker; actively exploitable, with current data exposure or privilege escalation
- `P1`: high; exploitable with moderate effort or missing a critical safeguard
- `P2`: medium; defense-in-depth gap or issue exploitable only under narrower conditions
- `P3`: low; hardening opportunity, theoretical risk, or documented trade-off

## Phase 4: Output

Return these sections in order:

### Section A: Attack Surface Map

Use the compact table from Phase 1.

### Section B: Findings

Group findings by severity first, then by category within each severity.

### Section C: Missing Security Tests

For each finding with no direct test coverage, return:

- `<finding title> -> what the test should assert -> suggested test file location`

### Section D: Hardening Roadmap

Order items by impact times ease of fix. For each item, include:

- what to do
- estimated scope
- whether it blocks production readiness

### Section E: Reusable Security Patterns

Extract 3 to 5 patterns that generalize across this stack. For each pattern, include:

- what to check
- where to look
- what good looks like
- what bad looks like

## Constraints

- Stay in audit and review mode unless the user explicitly asks for edits.
- Do not pad the report with generic OWASP advice.
- Every finding must reference a real file or config path.
- If an exploit path depends on a piece you cannot verify, state what is known and what is unknown.
- If a gap is already documented in `notes/` or `CLAUDE.md` as a known issue or accepted trade-off, reference that documentation and de-escalate it accordingly.
- Prioritize issues exploitable by an unauthenticated external attacker over internal-only or local-only risks.
- Remember the stack-specific rules from [`workspace-patterns.md`](workspace-patterns.md), especially the false-positive exceptions around Supabase anon keys and documented Vite CSP trade-offs.
