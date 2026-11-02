# Google Technical SEO & Search Console Readiness Checklist: The 20-Point Vibe Coder's Guide

When vibe-coding a website or web app, default frameworks, SPA scaffolds, and AI-generated copy frequently leave critical technical SEO gaps that prevent Googlebot from indexing or ranking pages.

Before launching or wondering why your site has 0 Google impressions, run through this definitive 20-point checklist.

---

## 1. Switch to Server-Side Rendering (SSR / SSG)
- **The Problem**: Pure client-side single-page applications (vanilla Vite + React, Create React App) serve an empty `<div id="root"></div>`. Googlebot has a Web Rendering Service (WRS), but it defers JavaScript execution to a second wave of indexing that can take days or weeks, or times out on heavy client bundles.
- **The Solution**: Use a framework with pre-rendering: **Next.js** (App Router with SSR/SSG), **Astro** (zero-JS SSG by default), **Remix**, or **Nuxt**.
- **Verification**: Run `curl -s https://yourdomain.com | grep "<h1"` in your terminal. If the H1 and body copy are not in the raw HTML payload, search crawlers cannot index your content immediately.

## 2. Create an XML Sitemap (`sitemap.xml`)
- **The Problem**: Without a clean XML sitemap, search engines must discover pages exclusively through link crawling, leaving deep pages unindexed.
- **The Solution**: Generate a dynamic or build-time `sitemap.xml` listing all canonical, public, 200-OK pages with `<lastmod>` timestamps:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
      <loc>https://yourdomain.com/</loc>
      <lastmod>2026-10-30</lastmod>
      <changefreq>weekly</changefreq>
      <priority>1.0</priority>
    </url>
  </urlset>
  ```
- **Tools**: `next-sitemap` for Next.js, `@astrojs/sitemap` for Astro.

## 3. Submit in Google Search Console (GSC)
- **The Action**:
  1. Add domain property in Google Search Console via DNS TXT record or HTML tag.
  2. Navigate to **Sitemaps** in GSC sidebar and submit `https://yourdomain.com/sitemap.xml`.
  3. Use the **URL Inspection** tool on your homepage and primary landing pages to request manual indexing.

## 4. Let Googlebot in Through `robots.txt`
- **The Danger**: Template starter kits often ship with `Disallow: /` to prevent indexing during development. If deployed to production, Googlebot drops the entire domain.
- **Production Standard**:
  ```txt
  User-agent: *
  Allow: /
  Disallow: /api/
  Disallow: /admin/
  Disallow: /dashboard/

  Sitemap: https://yourdomain.com/sitemap.xml
  ```
- **Crucial Rule**: Never block CSS or JS asset directories (`/_next/static/`, `/assets/`). Googlebot needs CSS and JS to compute mobile-friendliness and Core Web Vitals.

## 5. Strip Out Every `noindex` Tag
- **The Danger**: AI scaffolding often leaves `<meta name="robots" content="noindex, nofollow">` or HTTP headers `X-Robots-Tag: noindex` in page layouts from staging templates.
- **Inspection**: Search codebase for `noindex` (`rg -i "noindex"`). Verify public production routes return `<meta name="robots" content="index, follow">`.

## 6. Collapse Redirect Chains
- **The Problem**: Redirect hops (`http://example.com` -> `https://example.com` -> `https://www.example.com` -> `https://www.example.com/`) burn Googlebot's crawl budget and dilute link equity (PageRank).
- **The Fix**: Configure your edge/CDN (Vercel, Cloudflare, Nginx) to collapse all variants directly to the canonical host in a **single 301 Permanent Redirect**:
  - `http://` -> `https://` (1 hop)
  - `non-www` -> `www` (or vice-versa, unified in the same rule)
  - Trailing slash standardized across all routes.

## 7. Fix Every Broken Link (Internal 404s)
- **The Problem**: Dead internal links (`href="#"`, broken relative paths, outdated slugs) waste crawl budget and create dead ends for user signals.
- **The Fix**: Run a local broken link crawler:
  ```bash
  npx broken-link-checker https://yourdomain.com -ro --filter-level 3
  ```
  Ensure all internal links return HTTP 200 OK.

## 8. Set Canonical URLs (`rel="canonical"`)
- **The Problem**: URL parameters (`?ref=producthunt`, `?utm_source=twitter`), trailing slash differences, or HTTP/HTTPS variants create duplicate content penalties.
- **The Fix**: Every indexable page must output a self-referential canonical tag in `<head>`:
  ```html
  <link rel="canonical" href="https://yourdomain.com/pricing" />
  ```
  In Next.js Metadata API:
  ```typescript
  export const metadata = {
    alternates: {
      canonical: 'https://yourdomain.com/pricing',
    },
  };
  ```

## 9. Unique Title and Meta Description per Page
- **The Problem**: AI scaffolds reuse the same generic title ("My App - Fast and Easy") and meta description across all routes. Google suppresses duplicate snippets.
- **The Standard**:
  - `<title>`: Under 60 characters. Format: `Primary Keyword or Page Name | Brand Name`
  - `<meta name="description">`: 120–155 characters. Crisp, compelling summary including primary keyword with a clear call-to-action.

## 10. Exactly One `<h1>` per Page (Clean Hierarchy)
- **The Problem**: Vibe-coded templates often use 4-5 `<h1>` tags on a single page (every card header or section title rendered as `<h1>`), or skip from `<h1>` directly to `<h4>`.
- **The Standard**:
  - Exactly **one** semantic `<h1>` tag containing the primary topic/keyword of the page.
  - Strict logical heading ladder: `<h1>` -> `<h2>` for major sections -> `<h3>` for sub-points. Never pick heading tags based on visual font size; use CSS classes (`text-xl font-bold`) for styling.

## 11. FAQ and Article Schema Markup (JSON-LD)
- **The Benefit**: Rich snippets in Google search results (expandable FAQ accordions, author bylines, publish dates) dramatically increase click-through rate (CTR).
- **The Standard**: Embed machine-readable JSON-LD in the `<head>`:
  ```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "How does pricing work?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "We offer a flat monthly plan with a 14-day free trial."
        }
      }
    ]
  }
  </script>
  ```
  Use `Article` or `BlogPosting` schema on all content and documentation pages.

## 12. Breadcrumb Navigation & Schema
- **The Benefit**: Google displays hierarchical site navigation in search snippets (`yourdomain.com > docs > api-keys`) instead of raw URL strings.
- **The Standard**: Provide semantic `<nav aria-label="Breadcrumb">` links and `BreadcrumbList` schema:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://yourdomain.com" },
      { "@type": "ListItem", "position": 2, "name": "Docs", "item": "https://yourdomain.com/docs" }
    ]
  }
  ```

## 13. Internally Link Every Orphan Page
- **The Problem**: Orphan pages (pages with 0 incoming internal links from other pages on your site) are rarely crawled and receive zero PageRank equity.
- **The Fix**:
  - Every blog post or docs article must be linked from parent category pages or related posts.
  - Link key conversion and feature pages directly from the main navbar or footer.
  - Keep all important pages within **3 clicks** of the homepage.

## 14. Write Descriptive `alt` Text on All Images
- **The Problem**: Empty `<img src="..." alt="" />` or generic `alt="image"` misses Google Images search traffic and violates accessibility standards.
- **The Standard**: Write 4–10 word contextual descriptions:
  ```html
  <!-- BAD -->
  <img src="/dashboard.png" alt="screenshot" />

  <!-- GOOD -->
  <img src="/dashboard.png" alt="Analytics dashboard showing real-time revenue and conversion metrics" />
  ```

## 15. Compress Images to WebP / AVIF
- **The Problem**: Raw 3MB PNG screenshots destroy page speed, exhaust mobile user bandwidth, and trigger mobile ranking penalties.
- **The Fix**: Convert all assets to **WebP** or **AVIF**. Set `quality=80`. Keep all image file sizes under **150 KB**.
- **Next.js / Astro**: Use native `<Image />` components that handle on-the-fly resizing, modern format negotiation (`image/avif`), and responsive `srcset`.

## 16. Get Cumulative Layout Shift (CLS) Under 0.1
- **The Problem**: Google's Core Web Vitals penalize pages where content jumps around as images, fonts, or ads load asynchronously.
- **The Fix**:
  - Always declare explicit `width` and `height` attributes (or aspect ratios) on all `<img>`, `<video>`, and `<iframe>` elements.
  - Use `font-display: swap` and preload main fonts to prevent layout thrashing on font load.
  - Use skeleton placeholders with identical dimensions to incoming dynamic content.

## 17. Load Every Page in Under 2 Seconds (LCP < 2.0s)
- **The Problem**: 53% of mobile users abandon sites that take longer than 3 seconds to load; Google's ranking algorithms heavily favor sub-2.5s Largest Contentful Paint.
- **The Fix**:
  - Serve HTML and assets via a global edge CDN (Vercel Edge, Cloudflare).
  - Preload the above-the-fold hero image using `<link rel="preload" as="image" href="..." fetchpriority="high">`.
  - Never lazy-load the hero image (do not put `loading="lazy"` on above-the-fold assets).
  - Code-split heavy interactive libraries (charts, animations) so the critical rendering path is minimal.

## 18. Rewrite Anything That Sounds Like AI Slop
- **The Problem**: Google's Helpful Content System (HCS) demotes low-effort, repetitive AI-generated text that offers no unique value.
- **AI Slop Signatures**:
  - *"In today's fast-paced digital world..."*
  - *"Moreover, it is important to remember..."*
  - *"Delve into the multifaceted tapestry of..."*
  - *"A testament to our commitment to excellence..."*
  - *"In conclusion, when it comes to X..."*
- **The Fix**: Strip the fluff. Replace passive corporate jargon with first-hand experience, concrete step-by-step instructions, and unique insights.

## 19. Add a Real Author with a Real Bio (E-E-A-T)
- **The Google Guideline**: Google evaluates **E-E-A-T** (Experience, Expertise, Authoritativeness, and Trustworthiness). Anonymous articles generated by AI get discounted in search rankings.
- **The Standard**:
  - Add a visible author byline on every article/guide with author photo, full name, and job title.
  - Dedicated author bio page (`/authors/john-doe`) detailing practical industry experience, credentials, and links to verified social profiles (LinkedIn, X, GitHub).
  - Include `Person` schema markup linked to author profiles.

## 20. Earn Backlinks from Sites People Trust
- **The Reality**: Technical SEO gets you crawled; backlinks get you ranked. Google's foundational algorithm (PageRank) still requires third-party votes of confidence.
- **Actionable Tactical Backlink Strategies for Vibe Coders**:
  - Launch on Product Hunt, Hacker News Show HN, and Betalist.
  - Submit your tool to curated directories (There's An AI For That, Futurepedia, AlternativeTo, SaaSHub).
  - Open-source a useful library, starter kit, or CLI on GitHub and link back to your product documentation.
  - Publish original benchmark data or calculators that industry blogs and newsletters cite as authoritative sources.
