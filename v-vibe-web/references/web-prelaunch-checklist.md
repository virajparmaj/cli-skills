# Website & Marketing Launch Readiness Checklist

Pre-launch verification checklist for public-facing websites, marketing pages, and content sites before driving traffic or launching on Product Hunt / Hacker News.

---

## 1. Social Sharing & Metadata
- [ ] `<title>`: Descriptive, unique per page, under 60 characters (`[Page Title] | [Product Name]`).
- [ ] `<meta name="description">`: Crisp, keyword-aligned, 120-155 characters.
- [ ] Open Graph: `og:title`, `og:description`, `og:image` (1200x630px, < 300KB), `og:url`, `og:type="website"`.
- [ ] Twitter Cards: `twitter:card="summary_large_image"`, `twitter:title`, `twitter:image`, `twitter:creator`.
- [ ] Favicon Suite: `/favicon.ico`, `/favicon-32x32.png`, `/apple-touch-icon.png`, `/site.webmanifest`.
- [ ] Canonical URL: `<link rel="canonical" href="https://yourdomain.com/path">` to prevent duplicate content penalties.

## 2. Error Pages & Broken Link Resilience
- [ ] Custom 404 Page: Branded, helpful navigation links (Home, Search, Docs), friendly tone.
- [ ] Custom 500 Page: Static HTML fallback that renders even if the application runtime crashes.
- [ ] Link Crawler: Run `npx broken-link-checker` to eliminate 404s on external and internal links.

## 3. Legal, Trust & Privacy Compliance
- [ ] Privacy Policy: Explicitly details what data is collected, third-party analytics used, and cookie policies.
- [ ] Terms of Service: Disclaimers of warranty, limitation of liability, governing law, and acceptable use.
- [ ] Cookie Consent Banner: Required if serving EU/UK visitors (GDPR/ePrivacy) and using non-essential tracking cookies.
- [ ] Contact Channel: Clear, reachable support email or contact form.

## 4. Lead Capture & Form Protection
- [ ] Server-Side Form Validation: Never rely solely on client-side HTML5 `required` or JS validation.
- [ ] Bot & Spam Protection: Cloudflare Turnstile, hCaptcha, or invisible honeypot field.
- [ ] Form Field Recovery: If server validation fails, re-populate the form with the user's submitted values so they don't have to re-type everything.
- [ ] Submission Feedback: Clear loading spinner during submit, explicit success state ("Check your inbox!"), actionable error messages.

## 5. Email Deliverability for Contact / Autoresponders
- [ ] SPF Record: Verified in DNS (`v=spf1 include:... ~all`).
- [ ] DKIM Signature: Verified with 2048-bit key.
- [ ] DMARC Policy: Configured (`v=DMARC1; p=quarantine; rua=mailto:...`).
- [ ] Test transactional emails via Mail-Tester or GlockApps (target: 9+/10 score).

## 6. Analytics & Event Tracking
- [ ] Privacy-friendly or configured analytics (PostHog, Plausible, GA4).
- [ ] Conversion events tagged: CTA clicks, newsletter signups, demo requests.
- [ ] Script tag loaded asynchronously (`async` or `defer`) to prevent blocking first paint.
