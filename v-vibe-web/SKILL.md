---
name: v-vibe-web
description: "Review websites, landing pages, and content portals for the 12 essentials of a real site, indexing, search discoverability, performance, UX recovery, and maintainability. Use for a website or marketing-site audit; use v-perf for a performance-only review."
---

# Post-Vibe Website & Marketing Site Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill when auditing a website, landing page, marketing site, content/docs portal, or static/SSR web frontend. Stay in review mode unless the user explicitly requests implementation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_web_vibe.py" --repo "<repo>"
   ```
2. Read only domain references relevant to this review:
   - [references/google-technical-seo-checklist.md](references/google-technical-seo-checklist.md) for Google technical SEO and ranking (20-point checklist)
   - [references/geo-ai-search-checklist.md](references/geo-ai-search-checklist.md) for ChatGPT/Perplexity search optimization
   - [references/speedmaxxing-web-performance.md](references/speedmaxxing-web-performance.md) for 20-point speed optimization
   - [references/web-prelaunch-checklist.md](references/web-prelaunch-checklist.md) for launch-blocking checks and the 12 essentials that make a vibe-coded site real
   - [references/design-and-codebase-slop.md](references/design-and-codebase-slop.md) for detecting AI UI and code slop patterns
   - [references/ux-trust-framework.md](references/ux-trust-framework.md) for UX trust, empty/loading/error state completeness, and user flow recovery

## Applicability

Separate public indexable content from private app routes. Source patterns cannot prove indexing, rankings, crawler access, or Core Web Vitals. Verify rendered output/live responses where available, and use current official guidance for search policy; missing preferred schemas, author pages, comparison pages, or a specific font/style is not automatically a bug.

## Workflow

1. Read project context and identify the rendering model, public routes, hosting, and existing SEO/promotion choices. Run the scanner from Quick Start to locate candidates.
2. Inspect raw and rendered HTML, status codes, canonical URLs, redirects, robots directives, and sitemap output where available. Verify current guidance in [references/google-technical-seo-checklist.md](references/google-technical-seo-checklist.md); do not infer indexing failure solely from a client-rendered shell.
3. For AI-search discovery, use [references/geo-ai-search-checklist.md](references/geo-ai-search-checklist.md). Preserve the user’s crawler policy; training access, search discovery, and referrals are separate goals.
4. For performance, use [references/speedmaxxing-web-performance.md](references/speedmaxxing-web-performance.md), with a measured baseline when runtime access exists. Source heuristics identify risks; they do not establish LCP, INP, or CLS.
5. For launches, forms, and the 12 "real site" essentials (custom 404, CTA above fold, per-page meta title/desc, OG image, favicon set, robots.txt, sitemap.xml, alt text, loading states, privacy policy, analytics), use [references/web-prelaunch-checklist.md](references/web-prelaunch-checklist.md) and [references/ux-trust-framework.md](references/ux-trust-framework.md). Trace relevant loading, empty, validation, error, and recovery states.
6. For maintainability/design concerns, use [references/design-and-codebase-slop.md](references/design-and-codebase-slop.md). Report concrete clarity, accessibility, change-cost, or behavior problems; aesthetic preferences alone are suggestions.

## Output

Keep the report proportional to scope:

1. Site, framework/rendering model, reviewed paths, deployment evidence, and coverage limits.
2. Short executive summary and `SHIP`, `FIX BEFORE TRAFFIC`, or `UNVERIFIED` verdict with its concrete basis.
3. Applicable SEO, AI-discovery, performance, UX, and 12 Real Site Essentials scorecards. Use `PASS`, `FAIL`, `N/A`, and `UNVERIFIED`; source-only absence cannot prove missing DNS/account configuration or failed production indexing.
4. Verified findings ordered by practical score, with severity, exact evidence, reachable trigger, frequency x impact = score, rating reasons, confidence, smallest fix, and verification. Keep unverified concerns separate.
5. A short action list, **Deferred issues**, and what is already good. Deduplicate tracked issues and report only meaningful changes in their evidence.

Do not fill an arbitrary number of findings. Base launch blockers on demonstrated consequences for intended public pages or user flows. Keep optional schemas, comparison content, author pages, marketing badges, and structural redesign out of required fixes unless the user’s actual requirements make them necessary.
