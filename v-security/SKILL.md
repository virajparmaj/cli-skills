---
name: v-security
description: >
  Focused repo-level security, secrets, input-validation, API-hardening, and abuse-resistance audits for React/Vite/TypeScript/Tailwind/shadcn + Supabase/Vercel/FastAPI projects. Use when asked to security review a repo, check secrets exposure, auth/RBAC gaps, Supabase RLS or storage policies, insecure file uploads, Vercel or FastAPI headers and CORS, missing rate limits, webhook verification, localStorage risk, or pre-launch readiness. Typical triggers: "security audit this repo", "check secrets and abuse resistance", "review Supabase RLS and Vercel headers", "do a pre-launch security pass", or "find auth and API hardening gaps."
---

# Repo Security Audit

Perform a review-only audit unless the user explicitly asks for fixes in the same turn. Ground every claim in real files, real code paths, and the repo's own documentation.

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
