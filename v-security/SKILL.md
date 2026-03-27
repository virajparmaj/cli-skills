---
name: v-security
description: >
  Focused repo-level security, secrets, input-validation, API-hardening, and abuse-resistance audits for React/Vite/TypeScript/Tailwind/shadcn + Supabase/Vercel/FastAPI projects. Use when asked to security review a repo, check secrets exposure, auth/RBAC gaps, Supabase RLS or storage policies, insecure file uploads, Vercel or FastAPI headers and CORS, missing rate limits, webhook verification, localStorage risk, or pre-launch readiness. Typical triggers: "security audit this repo", "check secrets and abuse resistance", "review Supabase RLS and Vercel headers", "do a pre-launch security pass", or "find auth and API hardening gaps."
---

# Repo Security Audit

Perform a review-only audit unless the user explicitly asks for fixes in the same turn. Ground every claim in real files, real code paths, and the repo's own documentation.

## Workflow

1. Confirm the target repo, then read the priority docs first: `CLAUDE.md`, `README.md`, `.env.example`, and `notes/04_auth_and_roles.md`, `notes/03_architecture.md`, `notes/11_known_issues.md`, `notes/10_deployment.md`, `notes/06_api_contracts.md`, `notes/13_prompt_context.md` when present.
2. Run [`scripts/surface-map.sh`](scripts/surface-map.sh) on the repo to build a compact attack-surface map before making claims.
3. Read [`references/workspace-patterns.md`](references/workspace-patterns.md) to pick up workspace-specific false positives, recurring gaps, and de-escalation rules.
4. Use [`references/audit-playbook.md`](references/audit-playbook.md) as the authoritative audit contract:
   - map the attack surface
   - inspect only concrete issues
   - mark findings `VERIFIED` or `UNVERIFIED`
   - return the required sections in the required order
5. Apply variants from [`references/variants.md`](references/variants.md) only when the repo actually matches them:
   - Supabase-heavy repo
   - Vercel `api/` serverless repo
   - FastAPI `backend/` repo
   - pre-launch gate
6. Cite line references from both code and docs when docs confirm, limit, or acknowledge a gap. De-escalate documented trade-offs instead of re-flagging them at full severity.
7. Prioritize unauthenticated external exploit paths over internal-only or local-only issues. Do not pad with generic OWASP advice.

## Output

Return:
- Attack Surface Map
- Findings grouped by severity, then category
- Missing Security Tests
- Hardening Roadmap
- Reusable Security Patterns

Use the exact finding format, severity scale, and constraints from [`references/audit-playbook.md`](references/audit-playbook.md).
