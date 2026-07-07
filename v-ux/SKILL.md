---
name: v-ux
description: Audit a frontend or web-app repo for user trust gaps, recovery failures, and state completeness. Use when the user asks for a UX trust audit, loading-empty-error-retry coverage, silent failures, dead-end flows, misleading demo-vs-live behavior, placeholder content, auth-payment-upload trust checks, cold-start UX, or a findings-first report with evidence, user harm, smallest fix, and test scenarios. Best fit for route-driven apps with notes docs, Supabase or serverless backends, Sonner or toast feedback, ErrorBoundary, Suspense, useIsMobile, multi-step forms, or local persistence.
---

# UX Trust Audit

Stay in audit mode. Do not edit files unless the user explicitly asks for fixes.

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

1. Build context before auditing. Read, in order when present: `CLAUDE.md`, `README.md`, `notes/13_prompt_context.md`, `notes/03_architecture.md`, `notes/04_auth_and_roles.md`, `notes/11_known_issues.md`, `notes/09_dev_setup.md`, `notes/10_deployment.md`, `.env.example` or `.env`, `vercel.json`, `supabase/`, `api/` or `backend/`, and `package.json`.
2. Map routes, pages, layouts, guards, and high-consequence flows before inspecting components. Start from `App.tsx`, router config, auth wrappers, layouts, and server entry points.
3. Run the full rubric in [references/audit-framework.md](references/audit-framework.md). It defines the state matrix, trust-gap categories, recovery checks, feedback audit, accessibility-mobile checks, artifact residue scan, output contract, severity scale, and add-on clauses.
4. Also read [references/workspace-patterns.md](references/workspace-patterns.md). Treat those patterns as search hints and risk priors, not as findings.
5. Use fast targeted searches before deep reading. Start with route files, then search for: `ErrorBoundary`, `Loader2`, `Sonner` or `toast`, `use-mobile` or `useIsMobile`, `VITE_DEMO_MODE`, `TOKEN_REFRESHED`, `role="alert"`, `aria-live`, `role="status"`, `Suspense`, `lazy`, `react-hook-form`, `zod`, `supabase`, `vercel.json`, `Render`, `localStorage`, and `fetch(`.
6. Keep the scope tight. This audit is about user-facing trust, recovery, and state completeness, not general architecture, performance, or visual design unless the issue directly manifests as a user-facing failure.
7. Report findings first, ordered by severity. Every verified finding needs files, evidence, user harm, smallest fix, and a concrete test scenario. Separate unverified concerns from verified issues.
8. If the user later asks for fixes, use this audit as the source of truth and implement the smallest changes that close the highest-severity gaps first.

## Reference Map

- Read [references/audit-framework.md](references/audit-framework.md) for the full audit contract and report structure.
- Read [references/workspace-patterns.md](references/workspace-patterns.md) for common patterns in this stack.
