# Audit Framework

Use this reference when the skill triggers. It is the full operating contract for the audit.

## Role And Scope

- Act as a senior product engineer with a security-conscious UX mindset.
- Stay in audit mode. Do not edit files unless the user explicitly asks for fixes.
- Do not drift into general architecture review, dependency critique, or visual design critique unless the issue directly manifests as a user-facing trust or recovery problem.

## Setup: Build Context Before Auditing

Read these in order when they exist:

1. `CLAUDE.md`
2. `README.md`
3. `notes/13_prompt_context.md`
4. `notes/03_architecture.md`
5. `notes/04_auth_and_roles.md`
6. `notes/11_known_issues.md`
7. `notes/09_dev_setup.md`
8. `notes/10_deployment.md`
9. `.env.example` or `.env` to check for committed secrets
10. `vercel.json`, `supabase/`, `api/` or `backend/`
11. `package.json`

Before auditing components, build a mental model of:

- The deployment target
- The auth model
- The real backend path versus demo-only behavior
- Which flows are high consequence
- Which context files already document known issues

## Map User Flows First

Map routes from `App.tsx` or the router config, then classify flows as:

- High-consequence: auth, payment or checkout, donation, data upload or submission, destructive actions, admin operations, ML or AI result display, privacy-sensitive screens
- Standard: browse, search, filter, navigate, settings, profile
- Entry or exit: onboarding, signup, login, logout, password reset, 404, error-boundary fallback

Also identify stack specifics that change the audit surface:

- Auth provider: Supabase Auth, NextAuth, custom auth, no auth, or demo-only roles
- State management: Zustand, Context, React Query, localStorage, IndexedDB
- Backend type: Supabase, FastAPI on Render, Vercel Functions, none, or client-only
- Form library: react-hook-form plus Zod, custom validation, or none
- Feedback layer: Sonner, custom toasts, inline alerts, or silence
- ErrorBoundary presence and placement

## Audit Categories

### A. State Completeness

Produce a coverage matrix for every page and interactive component:

| Page or Component | Loading | Empty | Error | Retry | Offline or Timeout | Success Feedback |
|---|---|---|---|---|---|---|

Look specifically for:

- Missing loading states: no `Loader2`, spinner, skeleton, or `Suspense` fallback during async work
- Missing empty states: list or dashboard renders blank instead of saying what happened
- Missing error states: `fetch`, Supabase, or form failures with no user-facing feedback
- Silent failures: caught errors that only `console.error`, swallow the failure, or leave the UI unchanged; explicitly check every Supabase call, every `fetch`, and every form submission handler you touch
- No retry path: error messages with no button, link, or instruction
- Stuck states: loading UI that never resolves on timeout or network failure

### B. Trust Gaps

Inspect for situations where users would lose confidence:

- Demo-live confusion: demo toggles, mock fallbacks, fake connected badges, fake API keys, simulated delays, or any state that feels production-real without disclosure
- Placeholder content shipped as real: fake images, `#` links, masked phone numbers, lorem ipsum, hardcoded social proof, or fake metrics
- Auth trust: client-only guards, role toggles without backend enforcement, login without recovery, password reset gaps, weak session handling, insecure token storage
- Payment or donation trust: unclear amounts, weak confirmation, missing receipts, missing interruption handling, or no safe way to resume after an interrupted attempt
- ML or AI output trust: no confidence or disclaimer, fallback scores not distinguished from live predictions, opaque inputs, no explanation of what drove the result, stale model metadata
- Upload trust: no progress, no size-type validation, unclear success-failure feedback, no cancel path, or no clear post-upload success state
- Data persistence trust: local-only storage without disclosure, no export or backup affordance
- Cold-start backend trust: Render or similar cold starts handled with blank screens, hanging spinners, or no retry guidance
- Env or secret exposure: committed secrets, client-exposed keys that should be server-only, service role usage in client code

### C. Recovery Paths

Test whether users can recover from every failure mode:

- Form recovery: failed multi-step forms, refresh loss, missing draft persistence, weak autosave behavior
- Network recovery: retry path without full reload, timeout behavior, retry with backoff where appropriate
- Auth recovery: expired session mid-task, redirect and return behavior, token refresh handling
- Navigation recovery: dead-end routes, weak 404, broken links, no path home
- Destructive action recovery: confirm dialogs, clear loss messaging, undo when applicable
- ErrorBoundary recovery: fallback offers reload, go home, or report path instead of a dead end
- Optimistic UI recovery: optimistic changes roll back or reconcile clearly when the server rejects them

### D. Feedback Consistency

Audit whether the project communicates with users consistently:

- Toast audit: map which operations show success, error, or info feedback and which are silent
- Validation feedback: inline versus submit-only, user-friendly wording versus developer wording, consistency across pages
- Button-state feedback: disabled or loading states, double-submit protection, text or spinner changes
- Confirmation patterns: destructive actions confirmed consistently while lower-risk actions are not over-gated

### E. Mobile And Accessibility Trust

Audit the trust-breaking basics:

- Tap targets at or above 44 by 44 pixels
- Responsive breakage around mobile breakpoints, horizontal overflow, clipped critical text, overflowing dialogs
- Keyboard navigation, focus traps, and Escape handling
- Screen-reader basics: labels, alt text, `role="alert"`, `role="status"`, and live-region behavior

### F. Generator Artifact Residue

If the repo was scaffolded or heavily generated, look for:

- Generator readmes or leftover boilerplate
- Unused shadcn or Radix components left installed or imported
- Generic TODO comments or generator signatures
- Default favicons, OG tags, or metadata that no longer match the product

## Output Contract

### Section 1: Project Context Summary

Summarize:

- Tech stack
- Auth model
- Backend type
- Deployment target
- High-consequence flows identified
- Context files read and the most relevant knowledge extracted

### Section 2: Verified Findings

Group findings by audit category. For each finding use this structure:

`[P0-P3] Category: Short title`

- Files: path and line references
- Evidence: exact code pattern, missing handler, or state gap
- User harm: what a real user experiences
- Smallest fix: minimum change that resolves the issue
- Test scenario: the automated test that should cover the happy path and failure path

Severity scale:

- P0: user loses data, money, or access; security or privacy violation
- P1: user gets stuck with no recovery path; trust-breaking experience
- P2: confusing or inconsistent UX that degrades confidence
- P3: polish gap that is noticeable but not harmful

### Section 3: Unverified Concerns

List issues you suspect but cannot confirm from code alone, such as timing-sensitive race conditions, device-specific behavior, or third-party failures. State what needs to be tested and how.

### Section 4: Missing Test Coverage

Provide a table:

| Flow | Has Unit Test | Has Integration Test | Has E2E Test | Priority Test to Add |
|---|---|---|---|---|

### Section 5: Prioritized Fix Plan

1. P0 fixes before users touch the app
2. P1 fixes before launch or next deploy
3. P2 quick wins with the highest confidence return
4. P3 polish when time allows

### Section 6: Reusable Audit Patterns

When valuable, call out reusable patterns that could become standalone skills. Include trigger, inspection steps, and expected output format. The source prompt explicitly called out:

- State completeness matrix generator
- Toast or feedback consistency checker
- Auth trust verifier
- Form recovery path validator
- Cold-start UX evaluator
- Generator artifact detector

## Optional Add-On Clauses

### Supabase-Specific Trust Add-On

If the project uses Supabase, additionally verify:

- RLS policies exist on every table storing user data
- Service-role keys never appear in client code or client env vars
- Auth callback URLs match deployment URLs
- Email templates are customized when relevant
- Edge Functions or privileged paths re-validate JWTs before bypassing RLS

### ML Result Trust Deep Dive

If the project displays ML or AI predictions, additionally verify:

- Fallback predictions are visually distinct from live predictions
- Confidence, uncertainty, or disclaimers are shown
- Input validation blocks clearly out-of-distribution inputs
- Model version or training date is visible
- Precomputed and live computation paths do not silently diverge

### Payment Or Donation Flow Trust Add-On

If the project handles payments or donations, additionally verify:

- Amount is confirmed before gateway invocation
- Loading or processing state prevents double submission
- Success path shows confirmation and reference ID
- Failure path is clear and retry-safe
- Interrupted flows can be reconciled
- Payment endpoints are rate limited
- Sensitive PII is encrypted at rest when stored

### Strict No-Overlap Clause

Use this when the user is running parallel architecture, security, performance, or design audits:

- Out of scope: file organization, dependency choices, backend internals, deep security review, bundle profiling, visual design quality
- In scope only when the issue directly manifests as a user-facing trust problem, such as a visible fetch failure, a blank screen, or a broken recovery path

## Operating Rules

- Findings must be evidence-backed, not speculative
- Separate verified issues from hypotheses
- Keep findings user-centered rather than code-style-centered
- Do not skip test gaps for critical flows
- Do not soften high-severity trust failures into polish notes
