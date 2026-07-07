---
name: v-auth
description: Audit authentication, authorization boundaries, session integrity, protected routes, Supabase RLS, custom JWT or cookie auth, serverless auth gaps, and demo or dev bypasses. Use when asked to review auth, roles, login or logout flows, password reset, backend bearer-token enforcement, route protection, RLS policies, storage policies, env-var exposure, or whether frontend restrictions are actually enforced by the backend. Triggers include "audit auth", "map the real auth model", "check protected routes", "verify RLS", "is demo mode safe", "is backend actually enforcing this", and "find launch-blocking auth gaps".
---

# Auth Boundaries Audit

This skill targets React + Vite SPAs, Supabase + RLS apps, Vercel serverless functions, and FastAPI backends.

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

## Start Here

1. Identify the target repo. If the user says "this repo", use the current working directory.
2. Run `scripts/discover-auth-surface.sh /absolute/path/to/repo` first. It surfaces the repo's auth docs, backend boundaries, migrations, env examples, and likely auth-related files.
3. Read project context in this order when present:
   - `CLAUDE.md`
   - `notes/04_auth_and_roles.md`
   - `notes/03_architecture.md`
   - `notes/13_prompt_context.md`
   - `README.md`
   - `.env.example`
   - `.env.local.example`
   - `notes/10_deployment.md`
4. Treat `notes/04_auth_and_roles.md` as the auth baseline when it exists. Verify its claims against code, but do not waste time re-deriving already confirmed facts.
5. Stay read-only unless the user explicitly asks for fixes.

## Workflow

- Build a factual auth inventory and label each item as `enforced in code`, `UI-only`, `documented-but-missing`, or `partially-implemented`.
- Use `references/auth-audit-spec.md` for the full checklist, workspace-specific failure modes, output format, and optional deep-dive variants.
- Prioritize the patterns that recur in this workspace:
  - routes hidden in nav but still served by the router
  - `RoleContext`, feature flags, or local state used as if they were authorization
  - `ProtectedRoute` or guards that exist but are not wired into the real router or shell
  - Supabase RLS mismatches, path-based storage policies, and triggers trusting `raw_user_meta_data`
  - FastAPI or Vercel endpoints with no bearer-token verification
  - demo or dev auth fallbacks, localStorage session shims, and feature-flagged auth stubs
  - in-memory rate limiters in serverless code
  - mocked auth tests that cannot catch real policy regressions
  - OAuth 2.0 or OIDC flow issues: implicit flow usage, missing PKCE, insecure redirect URI validation
  - missing or weak multi-factor authentication on sensitive operations
  - account recovery flows with non-expiring or reusable reset tokens
  - API key management: missing rotation, no expiry, keys in client-accessible code

## Evidence Standards

- Separate verified findings from unverified concerns.
- Cite file paths and line numbers for every verified finding.
- Describe a concrete exploit or misuse path, not a generic risk label.
- Suggest the smallest viable fix, but do not edit code unless the user asks.

## Output

Use the six-part report in `references/auth-audit-spec.md`:

1. Auth model summary
2. Verified findings
3. Unverified concerns
4. Prioritized fix list
5. Missing tests
6. Reusable auth audit patterns

Use the optional multi-project sweep, Supabase RLS deep-dive, session lifecycle stress test, or backend-enforcement cross-check when the repo or request calls for it.
