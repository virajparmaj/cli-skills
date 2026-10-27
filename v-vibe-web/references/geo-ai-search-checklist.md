# Generative Engine Optimization (GEO) & AI Search Checklist

How to get ChatGPT, Perplexity, Claude, and Gemini to discover, cite, and recommend your website.

---

## 1. Answer Real Questions Word for Word
- **Mechanism**: LLMs and search engines retrieve content by matching semantic vector embeddings of user queries to page headers.
- **Rule**: Use the exact conversational questions people ask AI as your `<h2>` headings (e.g. `## How does [Product] handle multi-currency billing?`).
- **First-Two-Sentence Mandate**: Place the direct, unambiguous answer in the first two sentences immediately below the heading. Do not start with marketing fluff or preamble. AI citation extractors prioritize the first 50-75 tokens under a matching header.

## 2. The Cleanest Definition on the Internet
- **Formula**: `"[Product] is a [category] that helps [target audience] do [primary outcome] without [primary pain point]."`
- **Placement**: Hero section, `<meta name="description">`, and `Organization` / `SoftwareApplication` JSON-LD schema.
- **Why**: AI engines quote clean, declarative one-line explanations when answering "What is X?" or "Tell me about X".

## 3. Third-Party Citations & Digital Footprint
- **Trust Hierarchy**: LLMs weigh what third parties say about you over self-promotional website copy.
- **Key Channels**:
  - Reddit (r/SaaS, r/webdev, domain-specific subreddits)
  - Quora answers
  - G2, Capterra, and Trustpilot reviews
  - Product Hunt launches and comments
  - GitHub repositories and discussions
  - Hacker News threads
- **Action**: Ensure your canonical name, category, and core differentiators are consistently discussed across these platforms.

## 4. "Best X" and Listicle Penetration
- **Mechanism**: When a user asks "What is the best tool for [job]?", LLMs synthesize consensus from curated roundup articles and ranking lists.
- **Strategy**: Identify the top 10 articles ranking on Google and Perplexity for "best [category] tools" and pitch authors/maintainers to get included with verified feature summaries.

## 5. Proprietary Data & Benchmark Assets
- **Citation Magnet**: AI engines cite sources with unique numbers, survey statistics, and benchmark data.
- **Examples**:
  - Annual industry benchmark reports (e.g., "We analyzed 500,000 API requests...")
  - Interactive ROI, latency, or pricing calculators
  - Public status or performance trackers

## 6. AI Crawler Access & Clean Crawlability
- **robots.txt Configuration**:
  Ensure you are NOT accidentally blocking AI search indexers:
  ```txt
  User-agent: GPTBot
  Allow: /

  User-agent: OAI-SearchBot
  Allow: /

  User-agent: ClaudeBot
  Allow: /

  User-agent: PerplexityBot
  Allow: /

  User-agent: Applebot-Extended
  Allow: /

  Sitemap: https://yourdomain.com/sitemap.xml
  ```
- **Rendering Architecture**: Content must be delivered via SSR (Server-Side Rendering) or SSG (Static Site Generation). Do not hide mission-critical explanations behind client-side JavaScript clicks, tabs, or infinite scrolls that headless bots fail to execute.

## 7. Structured Data (Schema.org)
- Provide rich, machine-readable JSON-LD in the `<head>`:
  - `Organization` (name, url, logo, sameAs social links)
  - `SoftwareApplication` or `Product` (operatingSystem, applicationCategory, offers)
  - `FAQPage` (questions and answers matching on-page content)
  - `Article` or `TechArticle` for documentation and blog posts

## 8. Freshness & Last-Updated Signals
- LLMs discount stale information.
- Display `<time datetime="2026-10-01">Last updated: October 1, 2026</time>`.
- Keep sitemap `<lastmod>` tags accurate and updated whenever page content changes.

## 9. Comparison & Alternative Pages
- High-intent searchers ask AI:
  - `"[Your Product] vs [Competitor]"`
  - `"[Competitor] alternatives"`
- Build dedicated comparison routes (`/vs/competitor-a`, `/alternatives/competitor-b`).
- Format with honest, feature-by-feature comparison tables and clear migration guides.

## 10. Weekly AI Search Audit Protocol
- Run recurring test prompts across ChatGPT, Perplexity, Claude, and Google AI Overviews:
  - *"What are the best tools for [use case]?"*
  - *"How does [Product] compare to [Competitor]?"*
  - *"What are the alternatives to [Competitor]?"*
- Track whether your product appears in the recommendations, what features are attributed to you, and what inaccuracies need to be corrected in public documentation.
