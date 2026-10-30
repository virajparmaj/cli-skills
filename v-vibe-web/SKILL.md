---
name: v-vibe-web
description: "Review-only post-vibe audit for websites, landing pages, marketing sites, content/docs sites, and web portals. Audits Generative Engine Optimization (GEO) & AI Search discovery (getting recommended by ChatGPT, Perplexity, Claude), Speedmaxxing performance & Core Web Vitals (20-point checklist: WebP/AVIF, lazy loading, font preloading, code splitting, debouncing), Design Slop indicators (tags/badge spam, italicized words, instrument serif + negative kerning, over-detailed UI, dividers, multiple color opacities, containers with borders, superfluous diagrams, code breadcrumbs, section numbering), Codebase Slop indicators (implicit coupling, layer-first folders, duplication, representable illegal states, god files, shotgun surgery, layering violations, pass-through wrappers, errors/validation not at the boundary), and pre-launch web essentials (OG tags, custom 404/500, legal terms, bot protection). Trigger on audit website, audit landing page, v-vibe-web, v-vibe-website, GEO audit, speedmaxxing audit, SEO for AI, design slop, website slop."
---

# Post-Vibe Website & Marketing Site Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Use this skill when auditing a website, landing page, marketing site, content/docs portal, or static/SSR web frontend. Stay in review mode unless the user explicitly requests implementation.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found in repository`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Bound the review.** Cover the requested scope and verify plausible findings. Stop once that scope is covered and required checks pass; expand or repeat only for changed code, failed checks, or unresolved evidence. State coverage gaps; do not chase speculative cases to fill a report.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_web_vibe.py" --repo "<repo>"
   ```
2. Read the domain references before evaluating:
   - [references/geo-ai-search-checklist.md](references/geo-ai-search-checklist.md) for ChatGPT/Perplexity search optimization
   - [references/speedmaxxing-web-performance.md](references/speedmaxxing-web-performance.md) for 20-point speed optimization
   - [references/web-prelaunch-checklist.md](references/web-prelaunch-checklist.md) for launch-blocking checks
   - [references/design-and-codebase-slop.md](references/design-and-codebase-slop.md) for detecting AI UI and code slop patterns

## Workflow

### 1. Absorb Context & Stack
- Read `README.md`, `package.json`, site configuration (`next.config.*`, `astro.config.*`, `vite.config.*`), and public assets.
- Identify the rendering model: Static SSG, SSR, Edge, or Client SPA. (Note: Client-only SPAs without SSR fail many AI bot discovery checks).

### 2. Audit GEO & AI Search Discovery
- **AI Crawler Directives**: Inspect `public/robots.txt` for disallow rules on `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`.
- **Exact-Question H2s**: Verify that H2 headings mirror real conversational queries and that the first 1-2 sentences immediately answer them.
- **One-Line Category Definition**: Confirm the hero or meta description includes: `"[Product] is a [category] that helps [audience] do [action]"`.
- **Structured Data**: Verify JSON-LD schemas (`Organization`, `SoftwareApplication`, `FAQPage`, `Product`).
- **Comparison & Alternatives**: Look for dedicated `*-vs-*` or `/alternatives/` comparison pages.
- **Freshness Signals**: Verify presence of explicit `dateModified` / `<time>` tags.

### 3. Audit Speedmaxxing & Core Web Vitals
- **Image Optimization**: Check for raw PNGs/JPEGs > 150KB, missing WebP/AVIF conversions, and missing `loading="lazy"` on below-the-fold assets.
- **Font Strategy**: Check for blocking external font imports, missing `font-display: swap`, and verify if primary font is preloaded.
- **Bundle & Code Splitting**: Check for monolithic page bundles, heavy unused UI packages (`lodash`, `moment`, `recharts`), and un-chunked modals.
- **Input Debouncing**: Verify debouncing on search/filter inputs (250-300ms) to avoid request thrashing.
- **Streaming & Skeletons**: Check if dynamic data or AI endpoints stream via SSE and render layout-stable skeletons.

### 4. Audit Design Slop (The 10 AI UI Smells)
- **Tags & Badge Spam**: Flag gratuitous `<Badge>` and pill tags on cards ("NEW", "FEATURE", "AI-POWERED", "BETA").
- **Italicized Words**: Flag arbitrary italicization in headings and marketing copy to fake editorial flair (*effortlessly*, *seamlessly*, *intelligently*).
- **Instrument Serif + Negative Kerning**: Identify trendy font pairings using serif headers with `tracking-tighter` or `tracking-[-0.05em]`.
- **Over the Top Detailed UI**: Identify gratuitous telemetry counters, fake activity monitors, and micro-charts on simple landing pages.
- **Dividers Everywhere**: Flag excessive `<Separator />`, `divide-y`, and hairline rules separating content blocks.
- **Multiple Color Shades and Opacities**: Audit chaotic opacity layering (`bg-opacity-50`, `text-white/70`, `text-muted-foreground/60`) creating muddy contrast.
- **Containers with Borders (Box-in-a-Box)**: Flag deeply nested bordered cards where every text block is wrapped in `border border-border rounded-lg bg-card p-4`.
- **Diagrams (The More Detailed, the Worse)**: Scrutinize superfluous Mermaid, SVG, or ASCII diagrams that add clutter without functional meaning.
- **Code Breadcrumbs**: Check for fake terminal prompts or deeply nested decorative breadcrumbs cluttering the viewport.
- **Section Numbering**: Flag robotic numbered headers ("01 / Features", "02 / Architecture", "Step 01 - Getting Started").

### 5. Audit Website Codebase Slop (The 9 Core Antipatterns)
- **Implicit Coupling**: Check for hidden state dependencies, unversioned localStorage, and implicit execution order.
- **Layer-First Folders**: Check if project is organized by `components/`, `services/`, `utils/` instead of feature/domain slices.
- **Duplication**: Identify copy-pasted UI sections, query helpers, and formatters.
- **Representable Illegal States**: Identify unconstrained boolean state types allowing conflicting loading/error/data states.
- **God Files**: Identify massive marketing or page components (> 300 LOC).
- **Shotgun Surgery**: Check if changing a single marketing theme or pricing tier requires editing 10+ files.
- **Layering Violations**: Check if landing page components query databases directly.
- **Pass-Through Wrappers**: Identify empty 1-line wrapper functions adding zero logic.
- **Errors / Validation Not at Boundary**: Check if form input validation is executed deep in handlers instead of at form boundary.

### 6. Audit Web Pre-Launch Essentials
- **Meta & Social**: Verify complete Open Graph (`og:image` 1200x630, `og:title`) and Twitter card tags.
- **Error Handlers**: Confirm existence of branded custom `404` and `500` error pages.
- **Legal Compliance**: Confirm linked Privacy Policy and Terms of Service.
- **Form Protection & Recovery**: Ensure forms have server validation, bot defenses (Turnstile/honeypot), and keep entered values on validation failure.

## Output Contract

Produce the audit report in this exact structure:

```markdown
# Website & Marketing Site Audit Report: [Site Name]

**Scanned Path**: `<path>`
**Framework & Rendering**: `Next.js / Astro / Vite SPA / Remix / HTML`
**Overall Launch Verdict**: `SHIP` | `FIX BEFORE TRAFFIC` | `NO-SHIP`

## 1. Executive Summary
- 3-5 sentence synthesis of site quality, AI search discoverability, speed bottlenecks, and conversion risks.

## 2. GEO (Generative Engine Optimization) Assessment
- **AI Crawler Access**: `Unblocked` | `Blocked (Specify bots)`
- **Schema.org JSON-LD**: `Implemented (Types)` | `Missing`
- **Definition & Q&A Structure**: `Pass` | `Needs optimization`
- **Comparison & Authority Footprint**: `Found` | `Missing`

## 3. Findings by Severity (P0, P1, P2, P3)

### [P0/P1/P2/P3-CODE] Title
- **Severity**: P0 (Launch blocker) | P1 (High risk / traffic loss) | P2 (Medium) | P3 (Polish)
- **Status**: Verified | Unverified Concern
- **File**: `path/to/file:line`
- **What**: Exact evidence found in code.
- **Why it matters**: Direct impact on search ranking, user conversion, or performance.
- **Smallest fix**: Targeted, minimal change (code snippet).
- **Verification**: How to verify the fix works.

## 4. Speedmaxxing Scorecard (20-Point Checklist)
| Check | Status | Notes |
|-------|--------|-------|
| Mobile Lighthouse / Baseline | `PASS / FAIL / UNVERIFIED` | ... |
| WebP / AVIF Images | `PASS / FAIL` | ... |
| Lazy-loading below fold | `PASS / FAIL` | ... |
| Font Preload & Display Swap | `PASS / FAIL` | ... |
| Code Splitting & Dynamic Imports | `PASS / FAIL` | ... |
| Debounced Search Inputs | `PASS / FAIL` | ... |
| Custom 404 & 500 Pages | `PASS / FAIL` | ... |
| ... | ... | ... |

## 5. Prioritized Cleanup Backlog
- **Quick Wins (< 30 mins)**: No structural risk.
- **Targeted Refactors (1-3 hours)**: Bounded scope.
- **Strategic Additions (Half-day)**: Comparison pages, Schema markup, SSR migration.

## 6. What's Already Good
- Highlight well-implemented architectural or design patterns that should be preserved.
```
