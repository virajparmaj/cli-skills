# Post-Launch 10-Point Playbook & Reference Guide

Use these examples only for selected, authorized checkpoints. Analytics, promotion, and badges are optional. Check live responses and external account status separately; static artifacts do not prove submission or indexing. Preserve deliberate noindex, crawler restrictions, consent, and canonical choices. Apply the entrypoint’s scoring/deferral policy.

---

## 1. Remove the `noindex` Tags

### Why It Matters
Staging environments, beta branches, and development scaffolds routinely add `noindex` directives to keep search crawlers out before release. If left in production, your website is completely invisible to Google, Bing, and AI search engines (Perplexity, ChatGPT).

### Verification
Check:
- `<meta name="robots" content="noindex, nofollow">` in `<head>`.
- HTTP Response Header: `X-Robots-Tag: noindex`.
- Conditional staging logic in your build or hosting provider.

### Fix / Implementation
Replace hardcoded `noindex` with dynamic environment guards, or ensure production builds emit `index, follow`:

```html
<!-- Production: index, follow -->
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
```

In Next.js App Router (`app/layout.tsx`):
```typescript
import type { Metadata } from 'next';

export const metadata: Metadata = {
  robots: {
    index: process.env.VERCEL_ENV === 'production',
    follow: process.env.VERCEL_ENV === 'production',
    googleBot: {
      index: process.env.VERCEL_ENV === 'production',
      follow: process.env.VERCEL_ENV === 'production',
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};
```

---

## 2. Set Up Google Search Console (GSC)

### Why It Matters
GSC is Google's primary interface to report indexing status, crawl errors, security warnings, search ranking queries, and Core Web Vitals performance.

### Verification Methods
1. **DNS TXT Record (Recommended - Covers entire domain + subdomains):**
   - Add TXT record to your DNS provider (Cloudflare, Namecheap, Route53):
     `google-site-verification=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
2. **HTML Meta Tag:**
   ```html
   <meta name="google-site-verification" content="YOUR_GSC_VERIFICATION_TOKEN" />
   ```
3. **HTML File Upload:**
   - Place `google[token].html` in `public/`.

### Post-Verification Steps
- Go to [Google Search Console](https://search.google.com/search-console).
- Add Property (`https://yourdomain.com`).
- Navigate to **Sitemaps** -> Submit `https://yourdomain.com/sitemap.xml`.
- Test your homepage using **URL Inspection** -> Request Indexing.

---

## 3. Set Up Google Analytics (GA4) / Telemetry

### Why It Matters
You need immediate visibility into launch traffic, acquisition sources (Product Hunt, Twitter/X, direct referrals), user flows, bounce rates, and conversion events.

### Example asynchronous integration (measure its actual impact)
Place GA4 or Google Tag Manager asynchronously in `<head>`:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX', {
    page_path: window.location.pathname,
    cookie_flags: 'SameSite=None;Secure'
  });
</script>
```

In Next.js (`@next/third-parties`):
```tsx
import { GoogleAnalytics } from '@next/third-parties/google';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <GoogleAnalytics gaId="G-XXXXXXXXXX" />
      </body>
    </html>
  );
}
```

*Note: For privacy-first lightweight setups, Vercel Analytics (`@vercel/analytics`), Plausible, or PostHog can be run alongside or in place of GA4.*

---

## 4. Check Your `robots.txt`

### Why It Matters
A misconfigured `robots.txt` can accidentally block search engines (`Disallow: /`) or hide critical CSS/JS stylesheets and media assets needed to render and index pages.

### Canonical `robots.txt` Template (`public/robots.txt`):
```txt
# Allow major search and AI crawlers
User-agent: *
Allow: /

# Reduce crawling of non-public routes; protect data with authentication
Disallow: /api/
Disallow: /admin/
Disallow: /dashboard/
Disallow: /private/

# Explicitly link XML Sitemap
Sitemap: https://yourdomain.com/sitemap.xml
```

---

## 5. Redirect `www` to `non-www` (or Vice-Versa)

### Why It Matters
Choose the intended canonical host and check live redirects and canonical signals. Both hosts returning 200 is a candidate for review, not proof of a ranking penalty. Preserve paths and query strings and avoid redirect loops.

### Hosting-Specific Configurations

#### Vercel (`vercel.json`):
```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "www.yourdomain.com"
        }
      ],
      "destination": "https://yourdomain.com/:path*",
      "permanent": true
    }
  ]
}
```

#### Netlify (`public/_redirects`):
```text
https://www.yourdomain.com/* https://yourdomain.com/:splat 301!
http://yourdomain.com/* https://yourdomain.com/:splat 301!
```

#### Next.js (`next.config.mjs`):
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.yourdomain.com' }],
        destination: 'https://yourdomain.com/:path*',
        permanent: true,
      },
    ];
  },
};
export default nextConfig;
```

#### Cloudflare:
Create a single **Redirect Rule**:
- Expression: `(http.host eq "www.yourdomain.com")`
- Type: Dynamic 301 Redirect
- Expression: `concat("https://yourdomain.com", http.request.uri.path)`

---

## 6. Submit Your Sitemap (`sitemap.xml`)

### Why It Matters
An XML sitemap lists every canonical page, its last modified date (`<lastmod>`), and update frequency so crawlers index deep pages efficiently.

### Static Sitemap Example (`public/sitemap.xml`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://yourdomain.com/</loc>
    <lastmod>2026-11-04</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://yourdomain.com/features</loc>
    <lastmod>2026-11-04</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://yourdomain.com/pricing</loc>
    <lastmod>2026-11-04</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

### Next.js App Router Dynamic Sitemap (`app/sitemap.ts`):
```typescript
import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://yourdomain.com';
  return [
    {
      url: baseUrl,
      // Set lastModified only from the page’s actual meaningful content update.
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/pricing`,
      // Set lastModified only from the page’s actual meaningful content update.
      changeFrequency: 'weekly',
      priority: 0.8,
    },
  ];
}
```

---

## 7. Give Every Page Its Own Title and Meta Description

### Target Guidelines
- **`<title>`**: 50–60 characters. Format: `Primary Keyword or Value Prop | Brand Name`.
- **`<meta name="description">`**: 120–155 characters. Clear value proposition with actionable hook.
- **Open Graph / Twitter**: Unique title, description, and preview image (`og:image`).

### Template (`index.html` or Head component):
```html
<head>
  <!-- Primary Meta Tags -->
  <title>Have A Enike Day — Handcrafted Digital Products & Notes</title>
  <meta name="title" content="Have A Enike Day — Handcrafted Digital Products & Notes" />
  <meta name="description" content="Discover minimal, high-craft software tools, experimental web apps, and design engineering notes by Enike." />
  <link rel="canonical" href="https://haveaenikeday.com/" />

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://haveaenikeday.com/" />
  <meta property="og:title" content="Have A Enike Day — Handcrafted Digital Products & Notes" />
  <meta property="og:description" content="Discover minimal, high-craft software tools, experimental web apps, and design engineering notes by Enike." />
  <meta property="og:image" content="https://haveaenikeday.com/og-image.webp" />

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image" />
  <meta property="twitter:url" content="https://haveaenikeday.com/" />
  <meta property="twitter:title" content="Have A Enike Day — Handcrafted Digital Products & Notes" />
  <meta property="twitter:description" content="Discover minimal, high-craft software tools, experimental web apps, and design engineering notes by Enike." />
  <meta property="twitter:image" content="https://haveaenikeday.com/og-image.webp" />
</head>
```

---

## 8. Submit to Bing Webmaster Tools & IndexNow

### Why It Matters
Bing powers Microsoft Copilot, Yahoo, DuckDuckGo, and several AI search engines. Furthermore, Bing's **IndexNow** protocol pushes newly published or updated URLs directly to Bing and Yandex within minutes instead of waiting weeks for a passive crawl.

### Steps
1. **Google Search Console One-Click Import (Fastest):**
   - Log into [Bing Webmaster Tools](https://www.bing.com/webmasters).
   - Select **Import from Google Search Console**. All verified properties and sitemaps sync automatically.
2. **HTML Verification Tag:**
   ```html
   <meta name="msvalidate.01" content="YOUR_BING_VERIFICATION_KEY" />
   ```
3. **IndexNow API Setup:**
   - Generate an IndexNow key (e.g. `c4ca4238a0b923820dcc509a6f75849b`).
   - Place `public/c4ca4238a0b923820dcc509a6f75849b.txt` containing the key string.
   - Ping the IndexNow endpoint on deployment:
     ```bash
     curl "https://api.indexnow.org/indexnow?url=https://yourdomain.com/&key=c4ca4238a0b923820dcc509a6f75849b"
     ```

---

## 9. Launch Your Website on Product Hunt

### Preparation Checklist (Pre-Launch Night)
- **Tagline**: Under 60 characters. Crisp, punchy, benefit-driven (e.g., *"The all-in-one minimal toolkit for developers"*).
- **Thumbnail**: 240x240 px (GIF or high-contrast PNG).
- **Gallery**: At least 3 to 5 images (1270x760 px, 16:9 ratio). Showcase the UI, core benefit, and workflow.
- **Demo Video (Optional but recommended)**: 60-90 second YouTube loom/video showing real product usage.
- **Maker Comment**:
  - Story: Why did you build this?
  - Problem solved & who it's for.
  - Tech stack & key features.
  - Ask: *"Would love feedback on [specific feature]!"*
  - Special offer / community discount code.
- **Timing**: Schedule for **12:01 AM PT** on launch day to maximize full 24-hour voting cycle.

---

## 10. Add a Score / Trust Badge

### Why It Matters
Social proof (Product Hunt "Featured", Trustpilot, GitHub Stars, measured performance results or verified certifications) elevates conversion rate and visitor trust.

### High-Performance Badge Integration (Zero Layout Shift)
Ensure all badge images have explicit `width`, `height`, and `loading="lazy"` attributes so they don't trigger Cumulative Layout Shift (CLS) or block Largest Contentful Paint (LCP).

#### Product Hunt Upvote Badge:
```html
<a
  href="https://www.producthunt.com/posts/YOUR_SLUG?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-YOUR_SLUG"
  target="_blank"
  rel="noopener noreferrer"
  class="inline-block transition-transform hover:scale-105"
>
  <img
    src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=YOUR_POST_ID&theme=light"
    alt="Product Hunt Featured Badge"
    width="250"
    height="54"
    loading="lazy"
    decoding="async"
    style="width: 250px; height: 54px;"
  />
</a>
```

#### GitHub Stars Badge:
```html
<a href="https://github.com/yourusername/yourrepo" target="_blank" rel="noopener noreferrer">
  <img
    src="https://img.shields.io/github/stars/yourusername/yourrepo?style=social"
    alt="GitHub Stars"
    width="100"
    height="20"
    loading="lazy"
    decoding="async"
  />
</a>
```

#### Verified claims

Use factual claims supported by the product’s real certification or measured service commitment. Do not copy encryption, compliance, uptime, review, or award claims from an example.

## Generated metadata and crawler-specific checks

Next.js supports metadata generators under `app/` as well as `src/app/`; source detection does not verify deployed output. Check [robots file conventions](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots) and [sitemap conventions](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap).

Evaluate the specific crawler’s group, wildcard fallback, and Allow/Disallow precedence before changing crawl policy. Blocking a training crawler does not itself block Googlebot. The helper evaluates the root path only; inspect deeper routes and live responses separately using [Google’s robots specification](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec).
