---
name: v-vibe
description: "Review-only post-vibe-code architecture and maintainability audit for Vite/React/TypeScript apps with Tailwind/shadcn and optional Supabase, FastAPI, or Vercel backends. First read repo context files (CLAUDE.md, notes/*, README.md, PRODUCTION_READY.md) and do not repeat known issues unless there is a delta. Map stack/auth/data/tooling, inspect architecture debt, codebase slop indicators (implicit coupling, layer-first folders, duplication, representable illegal states, god files, shotgun surgery, layering violations, pass-through wrappers, errors/validation not at the boundary), design slop indicators (tags/badge spam, italicized words, instrument serif + negative kerning, over-detailed UI, dividers, multiple color opacities, containers with borders, superfluous diagrams, code breadcrumbs, section numbering), dead code/deps, demo-vs-prod splits, state/type drift, config/doc drift, bundle health, and tests. Output verified findings with file refs, severity, smallest fix, missing tests, cleanup backlog, reusable rules, and what's good. Trigger on audit repo, post-vibe review, maintainability audit, architecture debt, codebase slop, design slop."
---

# Post-Vibe-Code Architecture Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Use this skill when the task is to inspect a repo, not to fix it. Stay in review mode unless the user explicitly asks for implementation.

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

## Quick Start

- Run `python3 "<skill-path>/scripts/repo_audit_inventory.py" --repo "<repo>"` first.
- If the repo is a Vite/React app, read [references/workspace-patterns.md](references/workspace-patterns.md) before writing findings.
- **Specialized Product Audits**: If auditing a specific product type, use the targeted `v-vibe-*` audit:
  - `v-vibe-web`: Websites, marketing/landing pages, GEO (AI search discovery), 20-point speedmaxxing.
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
   - Treat these files as the source of truth for deliberate tradeoffs, resolved issues, and known gaps.
   - Do not rereport tracked issues unless the issue worsened or produced a new symptom. Report the delta only.
   - If the repo lacks `notes/` or other context files, say so; that is itself a maintainability finding.

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

   - Oversized files and god modules:
     - Flag files above roughly 300 LOC.
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
   - Flag bundles or chunks above about 500 KB.
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
