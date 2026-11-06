---
name: v-frontend
description: "Review Vite, React, TypeScript, and Tailwind frontend performance: bundles, routes, rendering, data fetching, assets, fonts, and Vercel delivery. Use for a focused frontend audit; use v-perf for performance reviews across other web stacks."
---

# Vite React Performance Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill for evidence-backed, findings-first audits. A review request stays read-only; apply fixes only when the active task authorizes them.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Workflow

1. Start with repo context, not fixes.
   - Run `scripts/probe_repo.sh <repo-root>` first.
   - Read any `CLAUDE.md`, `notes/*known*`, `notes/*perf*`,
     `notes/03_architecture.md`, `notes/13_prompt_context.md`, and bundle
     budget files before drawing conclusions.
2. Map the runtime architecture from repo evidence.
   - Confirm app type, route and lazy-loading shape, state and data patterns,
     bundle strategy, and deployment target from `package.json`,
     `vite.config.*`, `src/App.*` or router entry, `src/contexts`,
     `src/store`, `src/providers`, `src/lib`, `src/services`, `public/`,
     `index.html`, global CSS, and `vercel.json`.
3. Follow the full rubric in
   [`references/audit-rubric.md`](references/audit-rubric.md).
   - Every confirmed issue needs exact file evidence, cost, expected impact,
     and the smallest viable fix.
   - Separate `Verified Findings` from `Unverified Concerns`.
4. Also read [`references/workspace-patterns.md`](references/workspace-patterns.md) to calibrate against common patterns in this stack.
5. End with the required output sections from the rubric:
   `Verified Findings`, `Unverified Concerns`, `Top 5 Highest-ROI
   Optimizations`, `Likely Startup / Render / Network Hotspots`, and
   `Reusable Patterns for a Frontend Perf Skill`. Include fewer than five optimizations when the evidence supports fewer; never invent findings to fill a quota.

## Scope Rules

- Prefer direct file evidence over theory.
- Do not re-report documented issues without checking whether they are still
  present.
- If the user scopes the audit to one area, keep the same findings-first style
  but narrow the checklist accordingly.
- If the user later wants fixes, finish the audit first and switch to
  implementation only on explicit request.
