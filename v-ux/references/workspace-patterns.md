# Workspace Patterns

Use this reference for route-driven React + Vite + TypeScript apps with optional Supabase, FastAPI, or Vercel backends.

The patterns below are common cues that should bias your search order and risk model. Treat them as hypotheses to verify in the target repo, never as automatic findings.

## Common Repo Shape

- React 18 plus Vite plus TypeScript apps
- Route definitions in `src/App.tsx`, `src/pages/*`, or `src/views/*`
- `notes/` docs that often contain architecture, auth, deployment, and known-issues context worth reading before source files
- Tailwind plus shadcn-ui plus Lucide
- `components/ui/sonner.tsx` or a `Sonner` toaster wrapper
- `hooks/use-mobile.tsx` with `useIsMobile()`
- Optional `supabase/`, `api/`, or `backend/` directories
- `vercel.json` as the most common deployment clue
- `vitest.config.ts` present more often than meaningful test coverage

## High-Value Search Anchors

Start with these anchors before deep file-by-file reading:

- Routes and guards: `App.tsx`, router config, `ProtectedRoute`, `RequireAuth`, admin wrappers, layouts
- State completeness: `Loader2`, `Suspense`, `lazy`, skeletons, empty-state copy, retry buttons
- Feedback: `Sonner`, `toast`, `role="alert"`, inline error copy, button loading states
- Trust boundaries: `VITE_DEMO_MODE`, `Connected`, `localStorage`, fake API keys, placeholder links, `TOKEN_REFRESHED`
- Backend clues: `supabase`, `service_role`, `RLS`, `vercel.json`, `Render`, `backend/`, `api/`
- Form resilience: `react-hook-form`, `zod`, autosave hooks, multi-step forms, draft persistence
- Accessibility-mobile: `useIsMobile`, sidebar breakpoints, modal components, icon-only buttons

## Repeated Risk Patterns

### Demo And Live Mode Confusion

Watch for:

- Client-side role toggles or demo users presented as real auth
- `VITE_DEMO_MODE` fallbacks that are easy to miss in the UI
- Fake "Connected" badges or settings panels that imply backend connectivity
- Simulated delays that mimic production behavior without disclosure

### State Coverage Is Often Uneven

Common symptom:

- `Loader2`, `Sonner`, `Suspense`, and shadcn alert primitives exist, but only some routes or flows actually use them

### ErrorBoundary And Recovery Coverage Varies By Repo

Do not assume an app-level boundary exists just because one project has it. Check `App.tsx` and key route wrappers for actual `ErrorBoundary` usage.

### Form Validation And Persistence Are Inconsistent

Watch for mixed patterns inside a single repo:

- Centralized validation in one flow but ad hoc validation elsewhere
- Multi-step flows with no autosave
- Inline field errors in some forms and silent submission failures in others

### Cold-Start Backends Need Explicit UX

Projects using serverless or hosted backends where users may wait 10 to 60 seconds. Audit whether the UI explains the wait, times out safely, and offers retry.

### Security Headers And Deployment Clues Can Surface Trust Problems

Check `vercel.json`, deployment notes, and entry HTML for user-visible trust issues such as unsafe CSP exceptions, mismatched domains, stale OG metadata, or broken production asset references.

### Supabase Trust Checks Matter

When a repo uses Supabase, bias toward:

- RLS coverage in `supabase/migrations/`
- Client exposure of keys in `.env`
- Route guards that only hide UI instead of enforcing access
- Session-expiry and token-refresh handling

### Optimistic UI Needs Rollback Proof

If a repo uses optimistic updates, confirm the rollback path is real and user-visible when writes fail. If a repo does not use optimistic updates, do not invent the issue.

### Placeholder Content Ships More Often Than Expected

Explicitly look for:

- `#` hrefs
- fake metrics
- masked phone numbers
- placeholder images
- incomplete social links
- mock API keys displayed in settings

This is a trust issue, not just polish.

### Generator Residue Is A Real Signal

Search for:

- leftover generator readmes
- unused shadcn components
- generic TODO comments
- default favicons or OG tags

Treat these as evidence of incomplete product hardening, then connect them back to user-facing harm before filing a finding.

### Progressive Disclosure And Information Hierarchy

Watch for:

- Overwhelming first-time users with advanced settings or complex dashboards
- Missing contextual help or tooltips on domain-specific terminology
- Dense forms that could benefit from progressive disclosure or step-by-step flows

### Onboarding And First-Run Experience

Check for:

- Missing empty states with actionable guidance on first use
- No onboarding flow for new users in complex applications
- Features that assume prior context without providing it

### Consent And Privacy UX

Check for:

- Missing or non-compliant cookie consent banners when tracking is present
- No clear path for users to request data deletion or export
- Privacy policy links that are broken or missing from signup and settings flows

## Output Biases

- Findings should be rooted in real files and current code, not inferred from workspace reputation alone
- Mention missing tests explicitly because test config is often present without matching coverage
- Separate product-trust failures from architecture opinions
- When a repo has strong notes coverage, use those docs to avoid duplicate or already-known findings
