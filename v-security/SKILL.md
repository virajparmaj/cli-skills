---
name: v-security
description: "Review repository security, secrets exposure, input validation, API hardening, and abuse resistance in React, Supabase, Vercel, or FastAPI projects. Use for a security audit or pre-launch security review; keep implementation within the user’s authorized scope."
---

# Repo Security Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Perform a review-only audit unless fixes are already authorized for the active task. Ground every claim in real files, real code paths, and the repo's own documentation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

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
