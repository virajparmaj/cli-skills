---
name: v-perf
description: "Review web performance across frameworks, including Core Web Vitals, image and font delivery, JavaScript cost, rendering, request waterfalls, queries, and caching. Use when a website feels slow or needs a performance audit; separate source risks from runtime measurements."
---

# Web Performance & Core Web Vitals Audit (v-perf)

Every vibe coder's performance prompt:
> *"My website feels slow. Audit the actual application and find what's making it slow."*

A fast website is not just about a green Lighthouse score. People should actually feel the difference.

### Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: 2.5 seconds or less.
- **INP (Interaction to Next Paint)**: under 200 milliseconds.
- **CLS (Cumulative Layout Shift)**: under 0.1.

### Golden Rule
> **Fix the biggest real bottlenecks first. Don't optimise random code just to make a report look better.**

---

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

1. Run the deterministic performance scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_perf.py" --repo "<repo>"
   ```
2. For JSON format:
   ```bash
   python3 "<skill-path>/scripts/audit_perf.py" --repo "<repo>" --json
   ```
3. Read the detailed reference rubric:
   - [`references/perf-audit-rubric.md`](references/perf-audit-rubric.md)

---

## The 20-Point Performance Checklist

1. **Measure baseline first**: Establish current metrics (Lighthouse mobile throttling, TTFB, total JS size) before touching any code.
2. **Largest Contentful Paint (LCP <= 2.5s)**: Locate the LCP element (hero image, heading text, or banner); check for render-blocking assets.
3. **Interaction to Next Paint (INP < 200ms)**: Check event listeners for long tasks (> 50ms) blocking main thread responsiveness.
4. **Cumulative Layout Shift (CLS < 0.1)**: Audit media, iframes, and dynamic containers for missing dimensions or layout shift triggers.
5. **Oversized images**: Find uncompressed PNG/JPEG files > 200KB; verify conversion to modern WebP or AVIF formats.
6. **Image dimensions**: Ensure every `<img>` declares explicit `width` and `height` to allow browser aspect ratio pre-allocation.
7. **Lazy-load below-the-fold images**: Add `loading="lazy"` and `decoding="async"` to off-screen images and iframes.
8. **Hero image priority (NEVER lazy-load hero)**: Verify the main hero / above-the-fold image does NOT have `loading="lazy"`; ensure it has `fetchpriority="high"` (or `<Image priority>` in Next.js).
9. **Unused JS & heavy dependencies**: Identify heavy libraries (`moment`, `lodash`, `recharts`, `three`, `lottie-web`) and replace with native APIs or modular alternatives.
10. **Bundle & route splitting**: Check for monolithic bundles; verify dynamic imports (`React.lazy()`, `next/dynamic()`) on heavy routes and modals.
11. **Remove unnecessary client-side rendering**: Avoid shipping empty HTML shells; push `'use client'` down to leaf nodes or use SSR/SSG for static content.
12. **Avoidable component re-renders**: Profile hot context/subscription paths before recommending memoization or narrower selectors. Inline objects and missing memoization alone are not verified bottlenecks.
13. **API call elimination**: Check for debouncing (250-300ms) on search/filter inputs; deduplicate duplicate requests with a stale-while-revalidate client layer (TanStack Query / SWR).
14. **Slow database queries**: Inspect queries for missing indexes on `WHERE`/`ORDER BY`/`JOIN`, unbounded `SELECT *`, and missing cursor-based pagination.
15. **Request waterfalls**: Find sequential `await` chains in `useEffect` or server loaders; parallelize independent operations with `Promise.all` while preserving data dependencies and failure behavior.
16. **Caching & static asset delivery**: Verify edge CDN delivery and proper `Cache-Control` headers (`immutable` for hashed assets, appropriate public cache directives only for non-sensitive, shareable responses; preserve tenant/auth boundaries for dynamic data).
17. **Font loading & FOIT**: Verify `font-display: swap` on web fonts; preload the primary above-the-fold `.woff2` font; eliminate render-blocking CSS `@import url(...)`.
18. **Reduce third-party scripts**: Audit analytics, tracking pixels, and widgets (GTM, Hotjar, Meta Pixel); ensure they load with `async`, `defer`, or `requestIdleCallback`.
19. **Mobile & throttled network testing**: Test key flows on simulated 4G / 4x CPU slowdown to simulate real-world mobile hardware.
20. **Zero-regression safety**: Verify that fixes do not break existing features; run all test suites (`npm test`, `pytest`) and production builds (`npm run build`).

---

## Output Contract

Every audit must produce the following structured report:

### 1. Executive Summary & Stack Detection
- Target repository, detected framework (Next.js, Vite/React, Astro, Remix, Vue, Svelte, static), and rendering model (SSR, SSG, SPA).
- Core Web Vitals Readiness Rating: **Pass** / **At Risk** / **Failing** / **Unverified**. State measurement source, device/network conditions, and date. Without runtime measurements, report source risks and leave metric results unverified.

### 2. Core Web Vitals Scorecard
| Metric | Target | Status | Primary Codebase Bottleneck |
| :--- | :--- | :--- | :--- |
| **LCP** | <= 2.5s | [Optimal / Warning / Critical] | File:line or root cause |
| **INP** | < 200ms | [Optimal / Warning / Critical] | File:line or root cause |
| **CLS** | < 0.1 | [Optimal / Warning / Critical] | File:line or root cause |

### 3. Highest-ROI Bottlenecks (up to five supported items)
Ranked strictly by **Frequency x Impact score**:
1. **[Bottleneck Title]** (Score: F x I = Total)
   - **Cost**: User-perceived delay, bundle weight, or layout shift impact.
   - **File & Line**: Exact citation.
   - **Smallest Viable Fix**: 1-3 lines of code.

### 4. Verified Codebase Findings
Grouped by domain (Images, Bundles, React Rendering, Network/APIs, Caching, Fonts).
Each finding must carry:
- `Evidence`: `Confirmed from code` [path:line]
- `Why it matters`: Tangible user impact
- `Smallest viable fix`: Drop-in replacement snippet

### 5. Unverified Concerns & Runtime Profiling Recommendations
Any performance risks that require production APM, real user monitoring (RUM), or throttled browser trace confirmation.

### 6. Regression Safety Checklist
- [ ] Baseline test suite passes
- [ ] Production build succeeds
- [ ] Critical user flows verified
