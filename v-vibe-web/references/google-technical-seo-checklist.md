# Technical SEO review checkpoints

Apply these to public pages intended for search. The entrypoint’s evidence, scoring, and deferral rules apply; absence of a preferred pattern is not automatically a defect. Verify current search behavior against official sources rather than fixed character counts or ranking promises.

## Rendering and indexing

1. **Content rendering:** Inspect initial HTML and rendered output. Google can execute JavaScript; an app shell alone does not prove indexing failure. Prefer server/pre-rendering when measured crawlability or performance needs justify it. [Google JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
2. **Sitemap:** Check canonical, indexable URLs and valid sitemap/index output. A sitemap helps discovery; its absence is not proof of failed indexing. Use real modification dates.
3. **Search Console:** Distinguish URL-prefix and domain verification and external account state. Do not infer failure from absent source tags; submissions require authorization.
4. **robots.txt:** Evaluate relevant crawler groups and paths, including assets needed to render. Crawl restrictions do not secure private pages or reliably remove URLs from search. [Google robots.txt guidance](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
5. **noindex:** Confirm unintended production directives on pages meant to be indexed. Preserve intentional noindex on staging, private/error routes, and other excluded content.
6. **Redirects:** Follow actual HTTP/HTTPS, host, slash, and moved-URL behavior; find loops and avoid unnecessary chains. Preserve paths and query parameters.
7. **Internal links:** Verify actual destinations and status codes. A fragment link may be a valid in-page anchor; inspect its target before calling it broken.
8. **Canonicalization:** Check consistent canonical signals and intended duplicate handling; avoid calling ordinary URL variants an automatic penalty.

## Page meaning and presentation

9. **Titles and descriptions:** Verify useful, route-specific rendered metadata. Length ranges are editorial guidance; assess the page and likely snippet rather than enforcing a universal cutoff.
10. **Headings:** Check clear page topic and logical heading hierarchy. Do not turn a preferred single-H1 convention into a ranking requirement without evidence.
11. **Structured data:** Use only types that match visible content and current supported search features. Valid JSON-LD does not guarantee a rich result. [Google structured data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
12. **Breadcrumbs:** Assess usefulness for the actual content hierarchy; a small flat site may not need them.
13. **Discovery:** Find important public pages with no useful internal path; depth targets depend on the information architecture.
14. **Image alternatives:** Provide meaningful alternatives for informative/functional images. Decorative images may use empty alt; do not require keyword text on every image.
15. **Image delivery:** Check actual dimensions, transfer sizes, responsive formats, and visual fidelity; avoid converting every asset or imposing a universal 150 KB limit.
16. **Layout stability:** Measure CLS where possible; inspect reserved dimensions/aspect ratio and font metrics as causes. Source patterns alone do not prove a metric passes.
17. **Loading:** Measure LCP and relevant mobile conditions; use the performance rubric for image priority, fonts, bundles, and delivery. Keep project-specific stretch targets separate from baseline guidance.

## Content and authority

18. **Useful content:** Identify inaccurate, duplicated, empty, or misleading copy. A disliked phrase or AI origin alone does not establish a search penalty.
19. **Accountability:** Check truthful authorship and relevant expertise for content that needs it. Do not invent credentials or require an author biography on every product page.
20. **External references:** Assess actual references and search/account evidence when available. Outreach, directory submissions, promotion, and link acquisition are separate authorized work; do not promise rankings.

## Reporting

Record the URL or source location, checked artifact/response, applicability, and result. Separate code evidence from production responses and Search Console data. Do not promise indexing, rich results, traffic, or a particular rank. Use **UNVERIFIED** when access or representative runtime evidence is missing.
