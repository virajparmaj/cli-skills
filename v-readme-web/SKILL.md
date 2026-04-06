---
name: v-readme-web
description: "Refresh a website or web-app README into a user-first product page by verifying the current site from real code before writing. Use when asked to rewrite a website README, verify README claims against the current frontend, preserve branding and top logo placement, update screenshots, simplify user-facing feature copy, or split normal user overview from developer setup. Trigger phrases: refresh this website README, rewrite README for this web app, verify this README against the current frontend, update screenshots in the website README, make this README feel like a product page."
---

# Website README Refresh

Use this skill when the repo is a website, web app, landing page, or product
site and the README should read like a product page first.

Do not use this skill for desktop apps or native-software repos. Those should
use a separate app-focused skill.

## Core rules

- Inspect the repo before drafting copy.
- Never invent pages, routes, flows, screenshots, integrations, or features.
- Keep the logo or hero branding near the top if the README already uses one.
- Preserve the project's existing branding assets and paths when they are still
  current.
- Keep the main feature section focused on implemented user-facing features.
- Remove stale, internal, architectural, or overly technical detail from the
  top sections.
- Split user-facing overview and getting-started content from developer setup.
- Prefer real, current screenshots of the live UI stored in stable repo paths
  such as `docs/images/`, `docs/screenshots/`, or `assets/readme/`.
- Avoid desktop-app assumptions such as OS install flows, native menus, or
  platform-specific desktop wording.

## Quick start

1. Run `scripts/discover-web-readme-surface.sh /absolute/path/to/repo`.
2. Read the current `README.md`, frontend entrypoints, route surfaces,
   navigation/layout files, install/build/test scripts, and branding or
   screenshot assets reported by the script.
3. Follow the required structure and rules in
   [`references/readme-web-spec.md`](references/readme-web-spec.md).

## Workflow

1. Map the product from code, not from old docs.
   - Read the current `README.md` first to understand the current shape.
   - Read the frontend entrypoints, route surfaces, and navigation/layout files
     next.
   - Verify user-facing pages, flows, and features from current code and tests
     when available.
   - Read install, run, build, and test scripts before describing setup.
2. Identify branding and screenshot assets.
   - Find the logo, hero image, or brand assets already used by the project.
   - Keep existing top branding near the top when it is still valid.
   - Find stable screenshot directories and decide whether current images still
     match the implemented UI.
3. Verify only implemented user-facing features.
   - Include pages, flows, and integrations only when current source or tests
     support them.
   - Rewrite technical behavior into clear, user-first language.
   - Remove stale roadmap items, internal implementation detail, and outdated
     README claims from the top sections.
4. Build the README in product-page order.
   - Website or product name
   - Logo or branding at the top
   - One short intro sentence
   - Website preview or screenshots
   - User-facing features
   - Getting started / visit / use
   - Developer install / local setup
5. Validate before finishing.
   - Confirm top branding stays near the top.
   - Confirm screenshot paths are stable and embedded directly.
   - Confirm feature bullets are evidence-backed.
   - Confirm the README avoids desktop-app assumptions.
   - Confirm developer setup includes clone/download, dependencies, local run,
     build, test, and tooling or env notes when relevant.

## Evidence standard

- `Confirmed from code`: direct support from routes, UI, config, scripts, or
  tests.
- `Strongly inferred`: okay only for connective wording, not for new features.
- `Not found in repository`: remove it from the README or mark it unavailable
  if context requires mentioning it.

## Output expectations

When later invoked on a target repo, the work should:

- update `README.md`
- keep copy concise, polished, and user-first
- preserve the project's existing branding assets
- refresh screenshot files only when needed
- make the README easy for a new visitor or user to understand before the
  developer setup section

## Good trigger examples

- `refresh this website README`
- `rewrite README for this web app`
- `verify this README against the current frontend`
- `update screenshots in the website README`
- `make this README feel like a product page`

## Bundled resources

- `scripts/discover-web-readme-surface.sh`: read-only discovery for likely
  README inputs in website and web-app repos.
- `references/readme-web-spec.md`: required README structure, screenshot rules,
  copy rules, and verification checklist.
