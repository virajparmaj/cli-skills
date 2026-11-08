---
name: v-vibe
description: "Review architecture and maintainability in Vite/React/TypeScript projects with optional Supabase or FastAPI. Use for a post-vibe code audit, coupling, duplication, state/type drift, dead code, or configuration drift; route specialized product reviews to v-vibe-*."
---

# Post-Vibe-Code Architecture Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill when the task is to inspect a repo, not to fix it. Stay in review mode unless the user explicitly asks for implementation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

- Run `python3 "<skill-path>/scripts/repo_audit_inventory.py" --repo "<repo>"` first.
- If the repo is a Vite/React app, read [references/workspace-patterns.md](references/workspace-patterns.md) before writing findings.
- **Specialized Product Audits**: If auditing a specific product type, use the targeted `v-vibe-*` audit:
  - `v-vibe-web`: Websites, marketing/landing pages, Google 20-point technical SEO & ranking, GEO (AI search discovery), 20-point speedmaxxing.
  - `v-vibe-app`: Full-stack SaaS apps, APIs, 19 distributed systems pillars, 80+ enterprise readiness, pre-launch 20.
  - `v-vibe-macos`: macOS desktop software (Swift/Tauri/Electron), App Sandbox, entitlements, PrivacyInfo.xcprivacy, atomic writes.
  - `v-vibe-ml`: AI/LLM/agent products, prompt injection, spend caps, model fallback, evals, RAG isolation.
- Build a short mental model of the app before judging quality.

## Workflow

1. Absorb repo context before code.
   - Read, in order, if present:
     1. `CLAUDE.md`
     2. `notes/13_prompt_context.md`
     3. `notes/03_architecture.md`
     4. `notes/04_auth_and_roles.md`
     5. `notes/11_known_issues.md`
     6. `notes/10_deployment.md`
     7. `notes/05_database_schema.md`
     8. `README.md`
     9. `PRODUCTION_READY.md`
   - Use these files to identify deliberate tradeoffs, resolved issues, and known gaps; verify current behavior against code and configuration.
   - Do not rereport tracked issues unless the issue worsened or produced a new symptom. Report the delta only.
   - If context files are absent, inspect source directly and state any actual coverage gap. Missing a preferred notes directory alone is not a bug.

2. Map the repo.
   - Read `package.json`, `tsconfig.json`, `tsconfig.app.json`, `vite.config.*`, `tailwind.config.*`, `vercel.json`, `.env.example` or `.env`, ESLint config, `supabase/`, `api/` or `backend/`, and `.github/workflows/` when present.
   - Produce a compact summary of:
     - what the app does
     - deployment target
     - data layer
     - auth model
     - build and test toolchain

3. Inspect architecture and maintainability debt.
   - Codebase Slop Indicators (The 9 Core Antipatterns):
     - **Implicit coupling**: Modules secretly relying on global variables, hidden side-effects, implicit execution order, or shared localStorage keys without typed contracts.
     - **Layer-first folders**: Structuring directories by technical layer (`components/`, `services/`, `controllers/`, `models/`, `hooks/`, `utils/`) rather than by domain/feature slices (`features/auth/`, `features/billing/`), breaking co-location and causing sprawling imports.
     - **Duplication**: Copy-pasting logic across files (slightly altered utility functions, repeated fetch wrappers, duplicated form handlers) because the AI lacked global codebase context across turns.
     - **Representable illegal states**: Modeling state with loose, unconstrained types allowing mutually exclusive values simultaneously (e.g. `{ isLoading: true, error: Error, data: User }` where all three can be set, instead of discriminated unions `{ status: 'loading' } | { status: 'error' } | { status: 'success' }`).
     - **God files**: Sprawling files (>300 LOC, often 1,000-2,000+ LOC) accumulating unrelated components, handlers, hooks, and helpers that the AI kept appending to.
     - **Shotgun surgery**: A single conceptual change (e.g. adding a new user role or status) requires modifying 8-15 disparate files because domain concepts are fragmented everywhere.
     - **Layering violations**: Presentation components invoking database queries or backend clients directly; backend models importing HTTP request/response DTOs.
     - **Pass-through wrappers**: Trivial one-line wrapper functions, empty abstractions, and facade services that do nothing except delegate to another function without adding behavior, validation, or transformation.
     - **Errors / validation not at the boundary**: Checking inputs deep inside nested business logic or database layers instead of parsing and validating strictly at system boundaries (API ingress, form submission, external API response) using schemas (Zod/Pydantic).

   - Design Slop Indicators (The 10 UI Smells):
     - **Tags / badge spam**: Gratuitous `<Badge>`, pill tags, and status chips plastered on every single card and heading ("NEW", "FEATURE", "AI-POWERED", "BETA", "v1.2") to simulate visual density.
     - **Italicized words**: Arbitrary italicization in headings or body copy to simulate editorial design (*effortlessly*, *seamlessly*, *intelligently*, *instantly*).
     - **Instrument serif, negative kerning**: Overused trendy AI font pairing (serif display headers with `tracking-tighter` / negative letter spacing) applied indiscriminately regardless of brand identity.
     - **Over the top detailed UI**: Excessive pseudo-complex dashboard metrics, fake activity feeds, micro-widgets, and telemetry counters on simple apps that don't need them.
     - **Dividers**: Gratuitous horizontal and vertical hairline rules (`<Separator />`, `divide-y`, `border-t`, `border-b`) cutting every minor component into disconnected compartments.
     - **Multiple color shades and opacities**: Chaotic color hierarchy with arbitrary alpha opacities (`bg-opacity-50`, `text-white/70`, `text-muted-foreground/60`, five different shades of gray/neutral in one view).
     - **Containers with borders**: "Box-in-a-box-in-a-box" card nesting, where every single paragraph, stat, or list item is wrapped in a `border border-border rounded-lg bg-card p-4`.
     - **Diagrams (the more detailed, the worse)**: Superfluous ASCII/SVG/Mermaid architecture diagrams, node graphs, or decorative flowcharts that add clutter without semantic or functional value.
     - **Code breadcrumbs**: Fake terminal prompts, decorative pseudo-code blocks, or deeply nested decorative breadcrumbs (`Dashboard > Analytics > Overview > Metric 1`) cluttering user workflow.
     - **Section numbering**: Robotic numbered sections ("01 / Features", "02 / Architecture", "03 / Pricing", "Step 01 - Onboarding") typical of generic AI template generation.
     - **The fake vibe site antipattern (12 missing essentials)**: Shiny surface aesthetics masking the absence of production foundations: (1) Custom 404 page, (2) CTA above the fold, (3) Meta title per page, (4) Meta description per page, (5) Open Graph image, (6) Favicon set, (7) robots.txt, (8) sitemap.xml, (9) Alt text on every image, (10) Loading states, (11) Privacy policy page, (12) Analytics installed. Route full website checks to `v-vibe-web`.

   - Oversized files and god modules:
     - Inspect files above roughly 300 LOC as candidates; report only demonstrated responsibility or change-coupling problems.
     - Include the actual line count and the responsibilities that are tangled.
   - Dead code and unused dependencies:
     - Check installed-but-unused packages, unused imports, orphan files, unused service functions, Lovable traces, and placeholder tests.
     - Explicitly check for commonly unused packages such as `@tanstack/react-query`, `recharts`, `sonner`, `framer-motion`, `next-themes`, `zod`, and `lovable-tagger`.
   - Dual demo vs production paths:
     - Check `VITE_DEMO_MODE`, `isDemoMode()`, localStorage fallbacks, and whether demo behavior diverges from real contracts.
   - Folder boundaries and responsibility leaks:
     - pages doing business logic or API work
     - components importing backend clients directly
     - inline types instead of shared `types/`
     - validation scattered instead of centralized
   - Duplication:
     - repeated query helpers
     - repeated transformations
     - frontend and backend validation drift
   - Import hygiene:
     - circular or barrel problems
     - multiple lockfiles
   - State management:
     - server data cached in global state without clear need
     - context or store god objects
     - duplicated source of truth
     - React Query installed globally but unused
   - Type safety:
     - `strict: false`
     - `any`-heavy flows
     - frontend types pretending to be backend contracts
     - enum or status vocabulary drift
     - unchecked JSON from localStorage or APIs
   - Config and documentation drift:
     - stale README or template residue
     - missing `.env.example`
     - misleading notes
     - missing CSP or HSTS when the app handles user data

4. Assess build and bundle health.
   - Inspect bundles or chunks above about 500 KB as candidates; report measured transfer/execution cost or a violated project budget.
   - Check whether heavy libraries are lazy-loaded.
   - Inspect `manualChunks`, `size-limit`, and whether `dist/` is committed.

5. Write findings in a strict audit format.
   - For each finding, include:
     - `[CATEGORY-CODE] Short title`
     - `Severity: Critical | High | Medium | Low`
     - `Status: Verified | Unverified Concern`
     - `Files: path:line`
     - `What`
     - `Why it matters`
     - `Smallest fix` as the minimum viable refactor, not a rewrite
     - `Missing tests`
   - Finish with:
     - prioritized cleanup backlog:
       - quick wins: under 30 minutes, no structural risk
       - targeted refactors: 1 to 3 hours, bounded scope
       - structural refactors: half-day or more, needs design choices
     - repeated patterns that should become reusable rules
     - what is already good and should be preserved
   - If you find a major auth or security gap, add a one-line handoff item at the end instead of a deep dive here.

## Guardrails

- Stay repo-specific. Do not give generic best-practice advice.
- Cite files or concrete patterns for every finding.
- Mark uncertainty clearly as `Verified` or `Unverified Concern`.
- Respect the repo's actual architecture; do not invent missing systems.
- Do not edit files unless the user explicitly switches from audit to implementation.

## Bundled Resources

### `scripts/repo_audit_inventory.py`

Use for deterministic discovery of:

- context files and missing context
- repo map files and backend markers
- lockfiles
- oversized source files
- placeholder test files
- common dependency and demo-mode signals

### `references/workspace-patterns.md`

Read when the repo is a Vite/React app or when you want:

- common recurring debt patterns
- stack-specific audit heuristics
- FastAPI or Supabase add-on checks
- cross-project comparison prompts
