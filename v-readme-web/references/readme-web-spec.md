# Website README Spec

Use this spec when refreshing the README for a website, web app, landing page,
or product-site repo.

## Required section order

1. Website or product name
2. Logo / branding at the top
3. One short intro sentence explaining what the website does
4. Website Preview / Screenshots
5. User-facing features
6. Getting Started / Visit / Use
7. Developer Install / Local Setup

## Logo and branding rules

- Keep the existing logo, hero image, or top brand asset near the top when the
  repo already uses one.
- Preserve existing branding assets and paths when they still match the current
  product.
- Do not replace branding casually just to make the README look newer.

## Screenshot rules

- Prefer real, current screenshots of the implemented website or web app.
- Store screenshot assets in stable repo paths such as:
  - `docs/images/`
  - `docs/screenshots/`
  - `assets/readme/`
  - `assets/screenshots/`
- Embed screenshots directly in the README.
- Add short captions only.
- Prioritize the homepage, key flows, dashboard views, and major product
  states.
- Replace stale screenshots when the UI or key product flow has changed.

## Copy rules

- Keep the tone simple, clean, and user-first.
- Make the README product-page first and developer doc second.
- Prefer one short intro sentence over a long opening paragraph.
- Make feature copy benefit-focused and easy to scan.
- Keep internal architecture and low-level implementation detail out of the top
  sections.

## Verification rules

- Only include implemented pages, flows, integrations, and features.
- Verify against current code, routes, UI, and tests when available.
- Treat old README copy as secondary context, not proof.
- If support is missing or unclear, remove the claim or move it out of the main
  feature section.

## Developer section rules

- Keep developer setup at the end of the README.
- Include how to clone or download the repo.
- Include how to install dependencies.
- Include how to run locally.
- Include how to build.
- Include how to test.
- Include framework, tooling, or version notes when relevant.
- Include env vars or local setup notes when relevant.

## Validation checklist

Before finishing a README refresh, confirm:

- the section order matches this spec
- branding remains near the top
- screenshot files exist in stable repo paths
- screenshot captions are short
- feature bullets are evidence-backed
- top sections stay user-first and avoid internal architecture
- getting-started content is separate from developer setup
- developer setup matches the real scripts and tooling

## Out of scope

- Desktop-app install flow framing
- Native platform setup assumptions
- Internal architecture deep dives in the top sections
- Rebranding unrelated product assets
