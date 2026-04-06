---
name: v-readme-app
description: "Refresh an app or desktop-software README into a user-first product page by verifying current behavior from the real codebase before writing. Use when asked to rewrite an app README, verify README claims against code, preserve branding and top logo placement, update screenshots, simplify user-facing feature copy, or split normal-user install from developer setup. Trigger phrases: refresh this app README, rewrite README for the current app, verify README against the codebase, update screenshots in the README, make this README user-friendly."
---

# App README Refresh

Use this skill when the repo is an app or desktop software project and the
README should read like a product page first.

Do not use this skill for marketing websites, landing pages, or content-heavy
websites. Those should use a separate website-focused skill.

## Core rules

- Inspect the repo before drafting copy.
- Never invent features, flows, screenshots, defaults, limits, or platform
  support.
- Keep the app logo at the top of the README if the repo already uses one.
- Do not move the logo below the intro.
- Keep the main feature section user-facing, benefit-focused, and backed by
  current code.
- Move developer-only or internal details to the final setup section.
- Prefer real screenshots stored in stable repo paths such as `docs/images/`
  or `assets/readme/`.
- If real screenshots are blocked or unavailable, pause before using generated
  imagery.

## Quick start

1. Run `scripts/discover-app-readme-surface.sh /absolute/path/to/repo`.
2. Read the current `README.md`, app entrypoints, UI/settings files,
   install/build/test scripts, and branding/screenshot assets reported by the
   script.
3. Follow the required structure and rules in
   [`references/readme-app-spec.md`](references/readme-app-spec.md).

## Workflow

1. Map the product from code, not from old docs.
   - Read the current `README.md` first to understand what exists today.
   - Read the app manifests and entrypoints next.
   - Read the user-facing UI/menu/settings source files that define what the
     product actually shows and supports.
   - Read install, build, run, and test scripts before describing setup.
2. Identify branding and screenshot assets.
   - Find the logo or icon already used in the README.
   - Preserve existing branding paths when they are still valid.
   - Find stable screenshot directories and decide whether current images are
     still accurate.
3. Verify only implemented user-facing features.
   - Include features only when current source or tests support them.
   - Rewrite technical behavior into plain language.
   - Remove roadmap items, internal architecture, and stale caveats from the
     top sections.
4. Build the README in product-page order.
   - App name
   - Logo at the top
   - One short intro sentence
   - App preview / screenshots
   - User-facing features
   - Install / getting started
   - Developer install / local setup
5. Validate before finishing.
   - Confirm logo stays at the top.
   - Confirm screenshot paths are stable and embedded directly.
   - Confirm feature bullets are evidence-backed.
   - Confirm install steps match actual scripts and requirements.
   - Confirm developer setup includes clone/download, dependencies, run/build,
     test, and OS/tooling notes when relevant.

## Evidence standard

- `Confirmed from code`: direct support from source, scripts, config, or tests.
- `Strongly inferred`: okay only for connective wording, not for new features.
- `Not found in repository`: remove it from the README or explicitly mark it as
  unavailable if context requires mentioning it.

## Output expectations

When later invoked on a target repo, the work should:

- update `README.md`
- keep copy concise and polished
- preserve the project's existing branding assets
- refresh screenshot files only when needed
- make the README easy for a new user to understand before installation

## Good trigger examples

- `refresh this app README`
- `rewrite README for the current app`
- `verify README against the codebase`
- `update screenshots in the README`
- `make this app README feel like a product page`

## Bundled resources

- `scripts/discover-app-readme-surface.sh`: read-only discovery for likely
  README inputs in app repos.
- `references/readme-app-spec.md`: required README structure, screenshot rules,
  copy rules, and verification checklist.
