---
name: v-auth
description: "Review authentication and authorization in React, Supabase, Vercel, or FastAPI projects. Use for login/session, protected-route, role, RLS, storage-policy, or backend enforcement audits; report verified boundaries and concrete exploit paths."
---

# Auth Boundaries Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


This skill targets React + Vite SPAs, Supabase + RLS apps, Vercel serverless functions, and FastAPI backends.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

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
