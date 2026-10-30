---
name: v-frontend
description: >-
  Audit Vite + React + TypeScript + Tailwind frontends for bundle splitting,
  lazy routes, rerender risks, data-fetching inefficiencies, oversized public
  assets, font loading, test gaps, design slop (badge spam, italicized buzzwords,
  instrument serif + negative kerning, excessive dividers, nested bordered boxes),
  codebase slop (god files, layer-first folders, duplication, illegal states), and
  Vercel delivery configuration. Use when a user asks for a findings-only frontend
  performance review, startup/render/network hotspot analysis, route-by-route
  lazy-loading audit, bundle or chunk review, Supabase query efficiency check,
  frontend design slop, or Vercel caching/header audit. Typical triggers: "audit
  this app for performance", "why is initial load slow", "review bundle splitting",
  "check lazy loading and query waterfalls", "find Vercel delivery gaps",
  "do a post-build perf audit", "frontend design slop".
---

# Vite React Performance Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Use this skill for evidence-backed, findings-first audits. Stay in audit mode:
do not edit files while using this skill.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Bound the review.** Cover the requested scope and verify plausible findings. Stop once that scope is covered and required checks pass; expand or repeat only for changed code, failed checks, or unresolved evidence. State coverage gaps; do not chase speculative cases to fill a report.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

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
