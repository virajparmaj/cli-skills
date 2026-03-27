---
name: v-frontend
description: >-
  Audit Vite + React + TypeScript + Tailwind frontends for bundle splitting,
  lazy routes, rerender risks, data-fetching inefficiencies, oversized public
  assets, font loading, test gaps, and Vercel delivery configuration. Use when
  a user asks for a findings-only frontend performance review, startup/render/
  network hotspot analysis, route-by-route lazy-loading audit, bundle or chunk
  review, Supabase query efficiency check, or Vercel caching/header audit.
  Typical triggers: "audit this app
  for performance", "why is initial load slow", "review bundle splitting",
  "check lazy loading and query waterfalls", "find Vercel delivery gaps", or
  "do a post-build perf audit".
---

# Vite React Performance Audit

Use this skill for evidence-backed, findings-first audits. Stay in audit mode:
do not edit files while using this skill.

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
   `Reusable Patterns for a Frontend Perf Skill`.

## Scope Rules

- Prefer direct file evidence over theory.
- Do not re-report documented issues without checking whether they are still
  present.
- If the user scopes the audit to one area, keep the same findings-first style
  but narrow the checklist accordingly.
- If the user later wants fixes, finish the audit first and switch to
  implementation only on explicit request.
