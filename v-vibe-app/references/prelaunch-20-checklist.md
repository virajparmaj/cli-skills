# Pre-Launch 20: The Definitive SaaS Release Gate

Before opening your vibe-coded application to public signups or paying customers, execute and verify these 20 non-negotiable checks.

---

| # | Check | Verification Method | Pass Criteria |
|---|---|---|---|
| **1** | **Hide every API key** | Search frontend bundles and git history | Zero live secrets in client code, public repos, or `.env` in git. |
| **2** | **Rotate committed keys** | Audit provider dashboard logs | Any key ever entered into an AI chat or git commit is revoked and rotated. |
| **3** | **Rate limiting active** | Test endpoint with `wrk` or `hey` | Rapid requests trigger HTTP 429 Too Many Requests. |
| **4** | **Server-side auth checks** | Direct curl to API without session cookie | Returns 401 Unauthorized; no reliance on frontend UI route hiding. |
| **5** | **Tenant isolation / RLS** | Query user B's resource ID using user A's token | Returns 404 or 403; zero cross-tenant data leakage. |
| **6** | **Server input validation** | Post malformed JSON & boundary payloads | Schema validation rejects with clean 422/400; no unhandled exceptions. |
| **7** | **AI provider spend caps** | OpenAI / Anthropic / Gemini console | Hard monthly spend ceiling configured; alert trigger set at 50% and 80%. |
| **8** | **No stack traces in errors** | Trigger 500 error in production mode | Clean generic error response; zero file paths, code snippets, or SQL queries exposed. |
| **9** | **Error tracking active** | Trigger intentional test exception | Exception appears in Sentry/Bugsnag within 15 seconds with stack trace and context. |
| **10** | **Tested backup & restore** | Execute manual restore into staging | Full database snapshot restores cleanly; tables verified intact. |
| **11** | **Custom 404 & 500 pages** | Navigate to `/random-nonexistent-slug` | Branded page renders with home link; no default server/framework error screen. |
| **12** | **Mobile responsiveness** | Test on physical budget Android device | Navigation drawer works, text wraps cleanly, no horizontal overflow scroll. |
| **13** | **Sub-3s load speed** | Run mobile PageSpeed / Lighthouse | Core Web Vitals pass; initial dashboard loads in under 3.0s on 4G. |
| **14** | **Meta tags & OG image** | Inspect with opengraph.xyz or Twitter card validator | Rich preview renders with title, description, and branded 1200x630 card. |
| **15** | **Privacy policy & Terms** | Verify live URLs in footer | Real, updated legal documents tailored to application data collection. |
| **16** | **Analytics & funnel tracking**| Complete signup flow | Signup event, activation step, and drop-offs tracked in analytics dashboard. |
| **17** | **E2E money flows verified** | Run live transaction (with real credit card) | Signup, card charge, receipt email, and access provisioning succeed end-to-end. |
| **18** | **Email deliverability** | Test with mail-tester.com | SPF, DKIM, and DMARC pass; test emails do not land in Gmail/Outlook spam. |
| **19** | **Customer support channel** | Submit test message via contact form / chat widget | Message arrives in founders' inbox or support queue within 60 seconds. |
| **20** | **Written rollback plan** | Review release runbook | Documented 1-command rollback procedure for code deploy and database migrations. |
