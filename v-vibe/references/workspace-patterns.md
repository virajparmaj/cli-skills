# Workspace Patterns

Use this reference when auditing Vite/React/TypeScript apps with Tailwind/shadcn and optional Supabase, FastAPI, or Vercel backends.

## Repo Family Shape

- Common stack: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui.
- Common frontend layout: `src/pages` or `src/views`, `src/components`, `src/hooks`, `src/lib`, `src/services` or `src/store`, `src/types`.
- Common backend variants:
  - `supabase/` plus direct client access
  - `api/` Vercel functions
  - `backend/` FastAPI scoring services
- Common context files:
  - `notes/00-14*.md`
  - `CLAUDE.md`
  - `PRODUCTION_READY.md`
- Some repos are richly documented; some have sparse notes. Missing context is itself signal.

## Recurring Cleanup Issues

- Installed-but-unused dependencies recur often. Check these first:
  - `@tanstack/react-query`
  - `recharts`
  - `sonner`
  - `framer-motion`
  - `next-themes`
  - `zod`
- `strict: false` in TypeScript config is common.
- shadcn/ui lint failures recur in `command.tsx` and `textarea.tsx`.
- Multiple lockfiles appear in the same repo (`package-lock.json` plus `bun.lockb` or `bun.lock`).
- Scaffold residue appears via template tagger packages, template README text, and generated directories.
- Placeholder tests like `src/test/example.test.ts` create false coverage signals.

## Recurring Architecture Debt

- God files are common. Look for files above 300 LOC with tangled responsibilities.
- Dual demo and production code paths recur in projects with `VITE_DEMO_MODE` or localStorage fallbacks.
  - Look for localStorage fallbacks that quietly diverge from backend or API contracts.
- Data-authority drift is a repeating problem:
  - server trusting client-supplied fields
  - frontend enum or status strings drifting from API contracts
  - settings or admin UI that looks real but does not persist
- React Query is sometimes globally wired but unused through `useQuery` or `useMutation`.

## Codebase Slop Indicators

Vibe-coding engines inevitably exhibit 9 structural code smell patterns when building applications across conversational iterations:

1. **Implicit Coupling**:
   - *Symptom*: Modules secretly depend on shared mutable global variables, hidden side-effects, implicit execution order, or unversioned localStorage keys.
   - *Why it hurts*: Refactoring one component silently breaks another in distant routes without compiler or runtime warnings.
   - *Remedy*: Expose explicit parameter contracts, pass dependencies via props/context, and enforce typed schemas for local persistence.

2. **Layer-First Folders**:
   - *Symptom*: Organizing directories strictly by technical layer (`src/components/`, `src/services/`, `src/models/`, `src/hooks/`, `src/utils/`) rather than by domain/feature (`src/features/auth/`, `src/features/billing/`).
   - *Why it hurts*: Developing a single feature requires jumping between 7 directories; deleting or refactoring an abandoned feature leaves orphan files scattered across layers.
   - *Remedy*: Adopt feature-first / vertical-slice structure where components, hooks, queries, and types for a domain live together.

3. **Duplication**:
   - *Symptom*: The same utility logic (date formatting, currency math, error parsing, API client creation) is copy-pasted across 4-6 files with slight variable name differences because the AI lacks cross-turn memory.
   - *Why it hurts*: Bug fixes applied to one instance leave the others broken, creating silent behavioural divergence.
   - *Remedy*: Extract shared domain helpers into centralized, tested utilities (`src/lib/` or feature-level utils).

4. **Representable Illegal States**:
   - *Symptom*: State modeled as independent loose booleans: `{ isLoading: boolean, isError: boolean, data?: User, error?: Error }`.
   - *Why it hurts*: The type system allows mutually exclusive states like `{ isLoading: true, error: Error, data: User }` to exist simultaneously, forcing defensive conditional checks everywhere.
   - *Remedy*: Model state as discriminated unions:
     ```typescript
     type State =
       | { status: 'idle' }
       | { status: 'loading' }
       | { status: 'success'; data: User }
       | { status: 'error'; error: Error };
     ```

5. **God Files**:
   - *Symptom*: Sprawling files (500 to 2,000+ LOC) accumulating UI markup, state machines, business validation, API calls, and inline helper types.
   - *Why it hurts*: Exceeds mental context limits, causes merge conflicts, and obscures responsibility boundaries.
   - *Remedy*: Split by responsibility: extract subcomponents, custom hooks for state logic, and pure transformation helpers.

6. **Shotgun Surgery**:
   - *Symptom*: Adding a single new status value (e.g. `'trial_expired'`) or user role requires manually editing 12 different files (enums, UI badges, route guards, DB queries, mock data).
   - *Why it hurts*: Inevitably misses one or two locations, producing runtime crashes or security bypasses.
   - *Remedy*: Centralize domain concepts in a single source of truth (Zod enum, Prisma schema) and derive downstream types and handlers.

7. **Layering Violations**:
   - *Symptom*: Presentation components importing database clients (`supabase.from('users')`, Prisma, or SQL queries) directly inside JSX render functions; backend models importing HTTP request/response DTOs.
   - *Why it hurts*: Bypasses authorization, security policies, and validation; prevents automated testing without mock databases.
   - *Remedy*: Strictly enforce boundary layers: UI -> Service/Hook -> API Client -> Backend Route -> Domain Service -> Data Layer.

8. **Pass-Through Wrappers**:
   - *Symptom*: Empty 1-line functions, classes, or services created purely because the AI follows an over-abstracted OOP reflex: `function getUser(id) { return userService.getUser(id); }` where `userService.getUser` just returns `api.get()`.
   - *Why it hurts*: Bloats codebase with boilerplate layers that add zero behavior, validation, or transformation.
   - *Remedy*: Inline pass-through wrappers unless they encapsulate genuine validation, caching, or transformation logic.

9. **Errors / Validation Not at the Boundary**:
   - *Symptom*: Checking for null, missing parameters, or invalid email formats deep inside service functions or database queries instead of at the entry boundary.
   - *Why it hurts*: Leads to defensive `if (!data) return null;` checks scattered across every function; produces unhelpful generic 500 errors instead of clean 422/400 validation responses.
   - *Remedy*: Parse and validate inputs strictly at the boundary (API route handlers via Zod/Pydantic, form submits via react-hook-form) and assume valid data internally.

## Design Slop Indicators

AI-generated interfaces (from v0, Lovable, Claude Artifacts, Bolt) exhibit recognizable visual clichés that create visual noise and telegraph amateur prompt-engineering:

1. **Tags / Badge Spam**:
   - *Symptom*: Gratuitous `<Badge>` and pill tags ("NEW", "FEATURE", "AI-POWERED", "BETA", "v1.2", "HOT") attached to every card, title, and list item.
   - *Harm*: Dilutes genuine visual priority; creates visual clutter where everything screams for attention.
   - *Fix*: Remove 80% of badges; reserve tags strictly for critical, user-actionable status indicators (e.g., "Payment Overdue").

2. **Italicized Words**:
   - *Symptom*: Arbitrary italicization in headings and marketing copy to fake editorial flair (*effortlessly*, *seamlessly*, *intelligently*, *instantly*).
   - *Harm*: Reads as generic AI copywriting filler; reduces readability in display typography.
   - *Fix*: Replace buzzword copy with concrete, plain-English verbs; remove gratuitous italic styling.

3. **Instrument Serif + Negative Kerning**:
   - *Symptom*: The ubiquitous AI aesthetic pairing: a serif display typeface (Instrument Serif, Playfair Display) forced into modern tech UIs with aggressive negative letter-spacing (`tracking-tighter`, `tracking-[-0.05em]`).
   - *Harm*: Homogenizes products into an indistinguishable template aesthetic; negative kerning creates glyph collision on mobile screens.
   - *Fix*: Match typography to actual brand identity; use clean sans-serif (Inter, Geist, SF Pro) with neutral tracking for functional interfaces.

4. **Over the Top Detailed UI**:
   - *Symptom*: Excessive dashboard widgets, fake activity graphs, telemetry gauges, and micro-metrics on simple applications that only need a basic list or form.
   - *Harm*: Cognitive overload for users; introduces massive bundle weight (recharts, canvas libraries) for zero user utility.
   - *Fix*: Design for user tasks, not visual complexity. Strip unused metrics and graphs until users explicitly demand them.

5. **Dividers Everywhere**:
   - *Symptom*: Gratuitous horizontal and vertical hairline dividers (`<Separator />`, `divide-y`, `border-t`, `border-b`) slicing every element into isolated boxes.
   - *Harm*: Visual friction. Clean layouts use whitespace (padding, margin, gap) to group content, not borders.
   - *Fix*: Remove dividers; increase vertical rhythm using Tailwind gap/space classes (`space-y-6`, `gap-8`).

6. **Multiple Color Shades and Opacities**:
   - *Symptom*: Unsystematic color layering: arbitrary alpha opacities (`bg-opacity-50`, `text-white/70`, `text-muted-foreground/60`, `bg-neutral-800/40`) resulting in 5 slightly different gray backgrounds in one view.
   - *Harm*: Degrades contrast, violates WCAG accessibility rules, and creates a muddy, unpolished visual appearance.
   - *Fix*: Stick strictly to semantic theme tokens (`bg-background`, `bg-card`, `bg-muted`, `text-foreground`, `text-muted-foreground`) without inline opacity hacks.

7. **Containers with Borders (Box-in-a-Box)**:
   - *Symptom*: Endless nested bordered cards: page in a card, containing section cards, containing item cards, containing pill cards, each with `border border-border rounded-lg p-4`.
   - *Harm*: Creates claustrophobic "bento-box syndrome" where border lines dominate the screen rather than content.
   - *Fix*: Flatten hierarchy: use plain background with subtle elevation or unbordered sections separated by whitespace.

8. **Diagrams (The More Detailed, the Worse)**:
   - *Symptom*: Superfluous architecture diagrams, Mermaid charts, node graphs, or decorative SVG flowcharts crammed into landing pages and docs.
   - *Harm*: Complex diagrams are usually unreadable on mobile, quickly drift from code reality, and serve as decorative posturing.
   - *Fix*: Delete decorative diagrams. Use concise bulleted flows or simplified high-level conceptual illustrations.

9. **Code Breadcrumbs**:
   - *Symptom*: Fake terminal mockups, syntax-highlighted code snippets, or deeply nested decorative breadcrumbs (`Dashboard > Analytics > Overview > Metric 1`) on consumer products.
   - *Harm*: Wastes vertical real estate and distracts from core user actions.
   - *Fix*: Remove fake terminal headers; keep breadcrumbs simple and functional only on deeply nested hierarchies (3+ levels).

10. **Section Numbering**:
    - *Symptom*: Robotic numbered section headers: "01 / Overview", "02 / Features", "03 / Architecture", "Step 01 - Getting Started".
    - *Harm*: Characteristic signature of generic AI template generators; rigid numbers break when sections are reordered or removed.
    - *Fix*: Use clear descriptive headings that communicate value without artificial serial numbers.

## Auth And Security Weak Spots

- UI-only roles or hidden navigation without backend enforcement
- scaffolded auth left disabled behind flags
- missing `ProtectedRoute` or route guards
- unauthenticated API endpoints
- permissive CORS carried from dev into prod
- missing `.env.example`
- committed `.env` or risky env handling
- client-side-only rate limiting
- missing CSP headers

## Build And Deployment Pitfalls

- Vite chunk warnings above 500 KB are common; some main bundles exceed 2 MB.
- Heavy libraries worth checking for lazy loading:
  - `recharts`
  - `framer-motion`
  - `leaflet`
  - `three`
  - `pdf-lib`
- Hosted backends may have cold-start risk and no warm-up path.
- `vercel.json` SPA rewrites can shadow API routes.

## Testing Reality

- Many repos have zero real tests or only placeholder tests.
- Missing coverage often includes auth flows, RLS, API error paths, and integration or E2E paths.

## CI/CD And Maintenance Health

- Check CI/CD pipeline configuration: missing or incomplete pipelines, no automated testing in CI, no lint checks in CI.
- Dependency freshness: check for outdated dependencies with known vulnerabilities, stale lockfiles, and packages multiple major versions behind.
- Code ownership: assess bus factor by looking at contributor patterns, undocumented complex modules, and single-author critical paths.

## Audit Add-Ons

### Cross-Project Comparison Mode

Use when the user wants this repo compared against sibling projects.

Compare against common tendencies:

- TypeScript strict mode: often off
- Test count: often zero or placeholder only
- Bundle size: often 500 KB to 1 MB or higher
- Auth implementation: often absent, mock, or partially wired
- CSP headers: often missing
- `.env.example`: often missing

### FastAPI Or ML Backend Add-On

If `backend/` or model artifacts exist, also inspect:

- committed model artifacts such as `joblib` or `pickle`
- fallback heuristics diverging from the live model contract
- health or model-card endpoints
- CORS carrying dev origins into production
- missing request auth
- cold-start risk
- input validation on `/score` or `/predict`

### Supabase Add-On

If `supabase/` exists, also inspect:

- missing RLS on tables
- `WITH CHECK (true)` or inserts not scoped to `auth.uid()`
- migrations adding columns without safe defaults
- generated type files drifting against the latest migration

## Positive Baselines To Preserve

- Strong patterns to look for: strict TypeScript, typed Supabase client, CI plus `size-limit`, real tests, rich `notes/` and `prompt_context` docs.
- Rich `notes/` and prompt-context docs are a strength. Use them to avoid re-reporting known issues and to preserve deliberate design choices.
