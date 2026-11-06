# Vibe Coder Performance & Core Web Vitals Audit Rubric

Apply the entrypoint’s scope, evidence, frequency x impact scoring, threshold (5), and deferral policy. These checks and severity examples guide inspection; they do not prove a bug or require a new feature. Mark inapplicable checks N/A and unavailable evidence UNVERIFIED. Below-threshold issues do not block completion; review-only requests remain read-only.

Every vibe coder's performance prompt:
> *"My website feels slow. Audit the actual application and find what's making it slow."*
>
> **Core Web Vitals Targets:**
> - **LCP (Largest Contentful Paint)**: 2.5 seconds or less.
> - **INP (Interaction to Next Paint)**: under 200 milliseconds.
> - **CLS (Cumulative Layout Shift)**: under 0.1.
>
> **Golden Principle:**
> Fix the biggest real bottlenecks first. Don't optimise random code just to make a report look better. A fast website is not just about a green Lighthouse score. People should actually feel the difference.

---

## The 20-Point Performance Checklist

### 1. Measure Current Performance Before Making Changes
- **Action**: Never guess what is slow. Establish an objective baseline first.
- **How to test**:
  - Run Lighthouse with mobile throttling (Moto G4 / budget Android profile on simulated 4G).
  - Capture real network transfer size, total JavaScript execution time, and TTFB (Time To First Byte).
  - Log baseline scores for LCP, INP, and CLS before editing any code.
- **Trap**: Testing exclusively on a M-series MacBook over gigabit fiber masks 95% of real user performance issues.

---

### 2. Check Largest Contentful Paint (LCP <= 2.5s)
- **Action**: Identify the single largest visual element above the viewport fold (hero image, heading text, or video poster).
- **Checks**:
  - Is the LCP element render-blocked by external CSS, heavy JS hydration, or font downloads?
  - For image LCP: Is the image preloaded via `<link rel="preload">`? Does it have `fetchpriority="high"`?
  - For SSR/Next.js: Use `<Image priority>` to prevent delayed discovery.
- **Trap**: Wrapping the LCP hero element inside a client-side lazy-rendered component (`React.lazy` or unmemoized query fetch) guarantees high LCP.

---

### 3. Check Interaction to Next Paint (INP < 200ms)
- **Action**: Measure the latency of all user interactions (clicks, taps, typing, accordion opens).
- **Checks**:
  - Are event handlers doing heavy computations synchronously on the main thread?
  - Yield to main thread via `setTimeout(..., 0)`, `requestAnimationFrame()`, or `scheduler.yield()` for complex operations.
  - Break up long tasks (> 50ms) using web workers or microtasks.
  - Audit third-party widgets (chat bubbles, heatmaps) that hijack main thread click listeners.

---

### 4. Check Cumulative Layout Shift (CLS < 0.1)
- **Action**: Prevent content from jumping as assets load asynchronously.
- **Checks**:
  - Ensure every image, iframe, and video element declares explicit `width` and `height` attributes or CSS `aspect-ratio`.
  - Reserve space for dynamic content, cookie banners, and ads using min-height skeletons.
  - Avoid injecting dynamic notification bars at the top of the page after initial paint.

---

### 5. Find Oversized Images & Serve Modern Formats
- **Action**: Eliminate multi-megabyte uncompressed PNGs and JPEGs.
- **Checks**:
  - Flag any static asset in `public/` or bundle > 200KB.
  - Convert all photos to **AVIF** (superior compression) with **WebP** fallback.
  - Resize images to their rendered container dimensions. Serving a 3840x2160 (4K) hero image that displays in a 1200px container wastes 80%+ of bandwidth.

---

### 6. Add Width and Height to Images to Prevent Shifts
- **Action**: Eliminate visual jumping during page loading.
- **Code Fix**:
  ```tsx
  // BAD: Layout jumps when image finishes loading
  <img src="/hero.png" alt="Product banner" />

  // GOOD: Browser reserves aspect ratio box before image downloads
  <img src="/hero.webp" width={1200} height={630} alt="Product banner" className="w-full h-auto" />
  ```

---

### 7. Lazy-Load Below-the-Fold Images
- **Action**: Defer off-screen assets until the user scrolls near them.
- **Code Fix**:
  ```tsx
  // For images, iframes, and embeds below the fold
  <img src="/testimonial-avatar.webp" loading="lazy" decoding="async" width={80} height={80} alt="User" />
  ```
- **Tools**: Native `loading="lazy"` or IntersectionObserver.

---

### 8. Don't Lazy-Load the Main Hero Image Unnecessarily
- **Action**: CRITICAL ANTI-PATTERN! Never put `loading="lazy"` on above-the-fold or hero images.
- **Why**: `loading="lazy"` forces the browser to wait until layout computation completes before starting image download, adding 500ms to 2,000ms to LCP.
- **Code Fix**:
  ```tsx
  // BAD (destroys LCP):
  <img src="/hero.png" loading="lazy" alt="Hero" />

  // GOOD:
  <img src="/hero.webp" fetchpriority="high" decoding="sync" width={1200} height={600} alt="Hero" />
  ```

---

### 9. Find Unused JavaScript & Large Dependencies
- **Action**: Prune boilerplate and AI-installed package bloat.
- **Top offenders in vibe-coded apps**:
  - `moment` (~300KB) -> Replace with native `Intl.DateTimeFormat` or modular `date-fns`.
  - `lodash` (~70KB) -> Replace with native ES6+ methods (`Array.map`, `filter`, `find`, `Object.assign`, `structuredClone`).
  - `recharts` / `chart.js` (~500KB) -> Ensure code splitting so it is only loaded on analytics routes.
  - `framer-motion` -> Use CSS animations/transitions for simple fades and slide-ins.

---

### 10. Split Large Bundles Where It Makes Sense
- **Action**: Ensure users only download the code needed for the route they are viewing.
- **Checks**:
  - Multipage routes must use dynamic imports (`React.lazy()`, `next/dynamic()`).
  - Modals, complex drawer components, and heavy sheet editors should be loaded on demand when the user triggers them.
  - In Vite: Configure `manualChunks` to split large vendor dependencies (`react`, UI primitives, charting) into stable, long-cached chunks.

---

### 11. Remove Unnecessary Client-Side Rendering
- **Action**: Avoid shipping blank HTML shells that force users to wait for JS bundles to download and parse before seeing text.
- **Checks**:
  - In Next.js: Check for gratuitous `'use client'` at the top of static landing pages or documentation. Push `'use client'` down to leaf interactive buttons.
  - In Vite/SPA: Pre-render static landing copy or ensure meaningful, styled skeleton markup is embedded in `index.html`.

---

### 12. Check for Avoidable Component Re-Renders
- **Action**: Prevent typing lag, scroll stutter, and main-thread thrashing.
- **Checks**:
  - **Context Provider Thrashing**: Never pass inline object literals like `value={{ user, token, refresh }}` into React Context providers without `useMemo`. Every parent render forces all consumers down the tree to re-render.
  - **Inline Allocations**: Avoid unmemoized `.filter()` or `.sort()` operations inside JSX `.map()` calls in hot paths.
  - **Zustand**: Use selector subscriptions (`useStore(state => state.foo)`) or `useShallow` rather than `const state = useStore()`.

---

### 13. Review API Calls & Eliminate Unnecessary Requests
- **Action**: Stop hammering the server on every keystroke or page focus.
- **Checks**:
  - Search / filter inputs: Always debounce by 250ms-300ms.
  - Duplicate fetches: Implement a caching / stale-while-revalidate client layer (TanStack Query, SWR, or RTK Query).
  - Unneeded polling: Clear intervals on unmount; avoid polling when tab is in background (`document.visibilityState === 'hidden'`).

---

### 14. Find Slow Database Queries
- **Action**: Database latency directly inflates server response times (TTFB).
- **Checks**:
  - Unbounded queries: Flag any `SELECT *` without an explicit `LIMIT` or pagination.
  - Missing Indexes: Verify that every column filtered in `WHERE`, ordered in `ORDER BY`, or joined in `JOIN` has an index.
  - N+1 Query Patterns: Identify queries inside loops; batch with `IN (...)` or JOINs.
  - Pagination: Use cursor-based / keyset pagination rather than large `OFFSET` values.

---

### 15. Fix Request Waterfalls Where Possible
- **Action**: Parallelize independent network roundtrips.
- **Checks**:
  - Avoid sequential `await fetchA(); await fetchB(); await fetchC();` inside `useEffect` or server loaders.
  - Use `Promise.all([fetchA(), fetchB(), fetchC()])`.
  - For client SPAs: Start fetching data as early as possible (e.g. in route loaders) rather than waiting for components to mount and render child trees.

---

### 16. Review Caching & Static Asset Delivery
- **Action**: Leverage edge CDNs and HTTP cache headers.
- **Checks**:
  - Hashed assets (JS, CSS with content hashes in Vite/Next.js):
    `Cache-Control: public, max-age=31536000, immutable`
  - Semi-dynamic / API endpoints:
    `Cache-Control: public, s-maxage=60, stale-while-revalidate=300`
  - Verify static assets are served via an edge CDN (Vercel Edge, Cloudflare, AWS CloudFront).

---

### 17. Check Font Loading & Layout Shifts
- **Action**: Eliminate FOIT (Flash of Invisible Text) and layout jitter caused by font swaps.
- **Checks**:
  - Never load fonts via CSS `@import url(...)` (blocks stylesheet parsing).
  - Always append `&display=swap` to Google Fonts URLs.
  - Preload the primary `.woff2` font for above-the-fold content:
    ```html
    <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
    ```
  - Limit font families to maximum 1-2 families, and load only essential weights (e.g. 400, 600).

---

### 18. Reduce Unnecessary Third-Party Scripts
- **Action**: Third-party scripts are the #1 destroyer of mobile INP and battery life.
- **Checks**:
  - Inventory all external scripts (Google Tag Manager, Meta Pixel, Hotjar, Intercom, FullStory, TikTok).
  - Ensure all tags have `async` or `defer`.
  - Defer non-critical tracking until after the initial interaction using `requestIdleCallback()` or Partytown.
  - Prune obsolete or duplicate trackers from marketing experiments.

---

### 19. Test Important Pages on Mobile & Slower Connections
- **Action**: Validate performance under realistic user conditions.
- **Checks**:
  - Test on a mid-tier mobile device or Chrome DevTools throttled to **Fast 4G** or **Slow 4G** with 4x CPU slowdown.
  - Verify layout stability, smooth scrolling (60fps), and touch responsiveness.
  - Ensure data tables and charts degrade gracefully on small screens without locking the UI.

---

### 20. Make Sure Performance Fixes Don't Break Existing Features
- **Action**: Zero regressions rule. A fast app that is broken is worthless.
- **Checks**:
  - Run the automated test suite (`npm test`, `vitest`, `pytest`) before and after optimizations.
  - Run the production build (`npm run build`) to ensure bundle splitting didn't break chunk resolution.
  - Manually test critical user flows (sign in, checkout, data submission, form validation) to confirm behavior is 100% intact.
