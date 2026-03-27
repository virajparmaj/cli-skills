---
name: v-ux
description: Audit a frontend or web-app repo for user trust gaps, recovery failures, and state completeness. Use when the user asks for a UX trust audit, loading-empty-error-retry coverage, silent failures, dead-end flows, misleading demo-vs-live behavior, placeholder content, auth-payment-upload trust checks, cold-start UX, or a findings-first report with evidence, user harm, smallest fix, and test scenarios. Best fit for route-driven apps with notes docs, Supabase or serverless backends, Sonner or toast feedback, ErrorBoundary, Suspense, useIsMobile, multi-step forms, or local persistence.
---

# UX Trust Audit

Stay in audit mode. Do not edit files unless the user explicitly asks for fixes.

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
