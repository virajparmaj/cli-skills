# Website & Marketing Launch Readiness Checklist: The 12 Things That Make a Vibe-Coded Site Real

Apply the entrypoint’s scope, evidence, frequency x impact scoring, threshold (5), and deferral policy. These checks and severity examples guide inspection; they do not prove a bug or require a new feature. Mark inapplicable checks N/A and unavailable evidence UNVERIFIED. Below-threshold issues do not block completion; review-only requests remain read-only.

A vibe-coded website often looks impressive on initial load with animations, dark mode, and badges, but frequently fails in production because it is missing the foundational elements of a real, functional website. Use this 12-point checklist to verify whether a site is real and production-ready or an unlaunched vibe demo.

---

## The 12 Essentials: Real Site vs. Fake Vibe Site

### 1. Custom 404 Page
- **The Gap**: Default framework 404s (e.g. Next.js black-and-white `404 | This page could not be found`, or a Vite/React blank white screen / routing crash) immediately reveal an unmaintained AI demo.
- **Verification**: Check for `not-found.tsx` / `not-found.jsx` (Next.js App Router), `pages/404.tsx` (Pages Router), `404.html` (Vite, Astro, static), or wildcard fallback route (`path="*"`) rendering a dedicated `NotFound` component.
- **Requirement**: Branded 404 page with helpful navigation: link back to Home, link to primary features/docs, and search or contact affordance.

### 2. CTA Above the Fold
- **The Gap**: Vibe coders love putting huge abstract 3D canvases, giant typography, or decorative badge spam above the fold, pushing the primary conversion action below the viewport fold or leaving it as a dead `#` link.
- **Verification**: Inspect landing and hero components (`App.tsx`, `page.tsx`, `Hero.tsx`, `Masthead.tsx`). Verify a high-contrast, actionable Call-to-Action (`<button>`, `<Button>`, `<Link>`, or `<a href="...">`) is fully visible in the initial viewport before scrolling.
- **Requirement**: Clear conversion copy ("Get Started", "Start Free Trial", "Book Demo", "Install Extension", "Buy Now") connected to a working route, modal, or signup flow.

### 3. Meta Title Per Page
- **The Gap**: Leaving default template titles (`Vite + React + TS`, `Create Next App`) or having a single static title across all routes in `index.html`.
- **Verification**: Check indexable routes for route-specific `<title>` tags, Next.js `metadata.title` / `generateMetadata`, React Helmet `<title>`, or Astro page titles.
- **Requirement**: Descriptive, unique per page, under 60 characters (`[Page Title] | [Product Name]`).

### 4. Meta Description Per Page
- **The Gap**: Omitting `<meta name="description">` entirely or copy-pasting generic template descriptions across every route.
- **Verification**: Inspect route metadata or page sources for `<meta name="description">` or `metadata.description`.
- **Requirement**: Crisp, keyword-aligned, 120–155 characters explaining the exact value proposition of each specific page for search snippets and preview cards.

### 5. Open Graph Image
- **The Gap**: When links are shared on Twitter/X, Slack, Discord, LinkedIn, or iMessage, the site generates a blank gray box or broken image thumbnail.
- **Verification**: Verify `og:image` and `twitter:image` meta tags or Next.js `opengraph-image.(png|jpg|webp)` route files. Confirm the referenced image physically exists in `public/` (or on a live CDN URL) and is sized correctly (1200x630px, under 300KB).
- **Requirement**: Branded preview image featuring product UI or typography, readable at thumbnail scale.

### 6. Favicon Set
- **The Gap**: The #1 tell of a fake vibe site is the default Vite purple lightning bolt, Next.js black triangle, or Lovable heart sitting in the browser tab.
- **Verification**: Check `public/` and root for custom favicon assets: `/favicon.ico`, `/favicon.svg` (or `favicon-32x32.png`), `/apple-touch-icon.png`, and `/site.webmanifest` (or Next.js `app/icon.png`).
- **Requirement**: Complete custom favicon suite matching product branding, with appropriate `<link rel="icon">` and `<link rel="apple-touch-icon">` tags.

### 7. robots.txt
- **The Gap**: Missing `robots.txt`, or leftover staging rules (`Disallow: /`) that silently block all search engine crawlers and AI search bots.
- **Verification**: Inspect `public/robots.txt` or `app/robots.ts`. Verify User-agent groups, ensure production assets (CSS, JS, images) are not blocked, and ensure it links to the sitemap.
- **Requirement**: Valid `robots.txt` allowing indexing of intended public routes and referencing `Sitemap: https://yourdomain.com/sitemap.xml`.

### 8. sitemap.xml
- **The Gap**: Search engines and AI discovery tools cannot discover deep pages, comparison pages, or docs without a sitemap.
- **Verification**: Check for `public/sitemap.xml`, `app/sitemap.ts`, or dynamic sitemap generation scripts.
- **Requirement**: Valid XML sitemap listing all canonical public URLs with accurate `<lastmod>` timestamps.

### 9. Alt Text on Every Image
- **The Gap**: AI generators churn out `<img>` tags with missing `alt` attributes or lazy generic values (`alt="image"`, `alt="pic"`), violating WCAG 2.1 AA accessibility guidelines and failing Google Image SEO.
- **Verification**: Scan all `<img>` and Next.js `<Image>` tags.
- **Requirement**: Meaningful, contextual `alt` descriptions for informative and functional images; explicit `alt="" aria-hidden="true"` reserved strictly for decorative icons and graphics.

### 10. Loading States
- **The Gap**: A vibe site freezes, renders a blank white area, or layout-shifts when fetching data, submitting forms, or executing async operations.
- **Verification**: Check components with async state (`fetch`, Supabase, TanStack Query, mutations). Look for skeleton loaders (`Skeleton`), spinners (`Loader2`), disabled button states during mutation, and `<Suspense>` fallbacks (or Next.js `loading.tsx`).
- **Requirement**: Visual loading feedback on all async triggers; buttons disable with spinner during submit; lists show skeletons instead of blank spaces.

### 11. Privacy Policy Page
- **The Gap**: Fake vibe sites use dead `#` links in the footer for "Privacy Policy" or omit it entirely. This blocks OAuth app approval (Google/GitHub login), Stripe onboarding, ad platform verification, and violates GDPR/CCPA.
- **Verification**: Check for a reachable `/privacy` or `/privacy-policy` route and confirm footer navigation links to it.
- **Requirement**: Functional privacy policy page detailing data collection, cookie usage, analytics providers, and contact channels.

### 12. Analytics Installed
- **The Gap**: A demo site never knows who visits or where users drop off. A real site tracks traffic, page views, and conversion funnels.
- **Verification**: Check `package.json` and client layouts for configured analytics: PostHog, Plausible, GA4 (`gtag.js` / `@next/third-parties/google`), Vercel Analytics (`@vercel/analytics`), Umami, or Cloudflare Web Analytics.
- **Requirement**: Analytics installed and loaded asynchronously (`async` / `defer`) with key conversion events tagged (CTA clicks, newsletter signups).

---

## Extended Pre-Launch & Trust Verification

### Error Pages & Broken Link Resilience
- [ ] Custom 500 Page: Static HTML fallback (`500.html` / `error.tsx`) that renders if the application runtime crashes.
- [ ] Broken Link Crawler: Run link check (`npx broken-link-checker` or internal link crawl) to eliminate dead internal and external links.

### Legal, Trust & Privacy Compliance
- [ ] Terms of Service: Disclaimers of warranty, limitation of liability, and acceptable use policy.
- [ ] Cookie Consent Banner: Required if serving EU/UK visitors (GDPR/ePrivacy) and using non-essential tracking cookies.
- [ ] Reachable Contact Channel: Verified support email, feedback modal, or contact form.

### Lead Capture & Form Protection
- [ ] Server-Side Form Validation: Validate schemas strictly on the server (e.g. Zod); never rely solely on client HTML5 `required`.
- [ ] Bot & Spam Protection: Cloudflare Turnstile, hCaptcha, or invisible honeypot field.
- [ ] Form Field Recovery: If submission fails, preserve user input so users do not have to retype.
- [ ] Submission Feedback: Clear loading spinner during submit, explicit success state ("Check your inbox!"), actionable error messages.

### Email Deliverability for Contact & Autoresponders
- [ ] SPF Record: Verified in DNS (`v=spf1 include:... ~all`).
- [ ] DKIM Signature: Verified with 2048-bit key.
- [ ] DMARC Policy: Configured (`v=DMARC1; p=quarantine; rua=mailto:...`).
- [ ] Transactional Email Test: Verified deliverability via Mail-Tester or GlockApps (target: 9+/10 score).
