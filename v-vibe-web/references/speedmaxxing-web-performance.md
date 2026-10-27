# Speedmaxxing Web Performance: 20-Point Guide

A 1-second delay can cost up to 20% in conversion drops. Use this checklist to audit and optimize vibe-coded websites and web applications for peak Core Web Vitals (LCP, INP, CLS).

---

## 1. Measure First: Mobile Lighthouse & PageSpeed
- Test using **mobile throttling** (Moto G4 / budget Android profile on 4G).
- Desktop scores lie; 70%+ of consumer traffic arrives on mobile devices.
- Target: LCP < 2.5s, INP < 200ms, CLS < 0.1.

## 2. Modern Image Formats (WebP / AVIF)
- Never serve raw uncompressed PNGs or JPEGs on landing pages.
- Convert all static images to **AVIF** (best compression) with **WebP** fallback.
- Tools: `@squoosh/lib`, `sharp`, `next/image`, or Cloudflare Polish.

## 3. Lazy-Load Below-the-Fold Images
- Add `loading="lazy"` to all images, iframes, and embeds below the viewport fold.
- Hero images **MUST NOT** be lazy-loaded; hero images should use `fetchpriority="high"`.

## 4. Global CDN & Edge Distribution
- Deliver HTML, images, and static assets from an edge CDN (Cloudflare, Vercel Edge Network, AWS CloudFront).
- Use proper caching headers:
  ```http
  Cache-Control: public, max-age=31536000, immutable  (for hashed assets /_next/static)
  Cache-Control: s-maxage=3600, stale-while-revalidate=86400 (for ISR pages)
  ```

## 5. Prune Unused AI-Installed Packages
- AI tools frequently install heavy libraries for single-line tasks (`lodash`, `moment`, `uuid`, `recharts`, `framer-motion`).
- Run bundle analysis: `npx vite-bundle-visualizer` or `@next/bundle-analyzer`.
- Replace `moment` with native `Intl` or `date-fns` (modular).
- Replace `lodash` with native JavaScript methods (`map`, `filter`, `find`, `structuredClone`).

## 6. JavaScript Code Splitting & Route Chunking
- Ensure landing pages do not download the entire SaaS dashboard code.
- Use dynamic imports (`React.lazy()`, `next/dynamic()`) for heavy modals, complex charts, and interactive widgets only loaded upon user interaction.

## 7. Web Font Optimization
- Limit site to **1 or at most 2 font families**.
- Use `font-display: swap` to prevent FOIT (Flash of Invisible Text).
- Preload the primary above-the-fold font file in `.woff2` format:
  ```html
  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  ```
- Avoid external `@import` in CSS files; use `<link rel="preconnect">` for third-party font CDNs.

## 8. Database Indexing on Key Columns
- Add database indexes to every column referenced in `WHERE`, `ORDER BY`, or `JOIN` clauses.
- Queries that run in 2ms on 50 test rows will time out on 500,000 production rows without an index.

## 9. Eliminate N+1 Database Queries
- Vibe-coded ORMs often run a separate query inside a loop (e.g. fetching author for each post).
- Use `JOIN`, `include` (Prisma), or batch fetching (DataLoader) to fetch in a single round-trip.

## 10. Cursor-Based Pagination
- Replace offset-based pagination (`OFFSET 10000 LIMIT 20`) with cursor/keyset pagination (`WHERE id > last_seen_id LIMIT 20`).
- Offset pagination scans and discards thousands of rows, causing memory spikes.

## 11. Cache High-Traffic API Responses
- Cache static or semi-static endpoints in Redis or via HTTP `stale-while-revalidate`.
- Avoid hitting the primary database on every marketing page hit or public feature query.

## 12. Stream AI Token Responses
- Never make users stare at a loading spinner for 12 seconds waiting for an LLM response.
- Use **Server-Sent Events (SSE)** or WebSockets to stream tokens incrementally.
- Measure and optimize **Time To First Token (TTFT)**.

## 13. Skeletons Over Blank Screens
- Show skeleton screens that match the final layout geometry instead of blank screens or full-page spinning wheels.
- Skeletons prevent layout shifts (CLS) when data arrives.

## 14. Offload Heavy Work to Background Jobs
- Web requests must respond within 200-500ms.
- Offload image resizing, PDF generation, email sending, webhooks, and AI pipelines to background worker queues (BullMQ, Celery, SQS).

## 15. Server Proximity & Regional Placement
- Deploy databases and application backends in the same cloud region.
- Inter-region network latency (e.g., US-East to EU-Central) adds 80-120ms to every database query.

## 16. Serverless Cold Start Elimination
- Keep serverless functions lean: bundle size < 10MB.
- Minimize top-level imports in Lambdas/Serverless functions; move heavy imports inside handlers if not needed for all routes.
- Consider provisioned concurrency or edge runtimes (Cloudflare Workers / Vercel Edge) for latency-critical routes.

## 17. Debounce Search & Filter Inputs
- Debounce real-time search inputs by 250-300ms.
- Un-debounced inputs trigger an API request on every keystroke, exhausting backend connections and hammering database CPU.

## 18. Audit & Defer Third-Party Tracking Scripts
- Third-party scripts (Hotjar, HubSpot, Facebook Pixel, Intercom) are the #1 cause of high INP (Interaction to Next Paint).
- Load analytics scripts with `defer` or `async`, or initialize them inside `requestIdleCallback()` after initial page interactive state.

## 19. Low-End Hardware & 4G Testing
- Test the application on an inexpensive Android phone over 4G or throttled Wi-Fi.
- High-end developer MacBooks mask heavy JavaScript execution bottlenecks.

## 20. Architectural AI Performance Diagnostic
- Ask your AI assistant with codebase context:
  *"Analyze this route for unnecessary re-renders, layout thrashing, unmemoized expensive calculations, and bloated dependencies."*
