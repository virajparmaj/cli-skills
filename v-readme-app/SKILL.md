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

- This skill is repo-agnostic. Treat the app under work as the `target repo`,
  not as a preselected product.
- Never assume a previously edited app or reuse project-specific copy, paths,
  screenshots, commands, or feature wording unless the user explicitly asked
  for that same repo.
- Derive the app name, branding, install steps, and feature copy from the
  target repo's current code and assets each time.
- If the user names a repo or passes a repo path, that repo wins over the
  currently open file, active tab, or current workspace.
- Inspect the repo before drafting copy.
- Never invent features, flows, screenshots, defaults, limits, or platform
  support.
- Keep the app logo at the top of the README if the repo already uses one.
- Do not move the logo below the intro.
- Keep the main feature section user-facing, benefit-focused, and backed by
  current code.
- Move developer-only or internal details to the final setup section.
- Prefer real screenshots, capture them when feasible, and preserve an existing
  screenshot directory when the repo already uses one.
- If the repo does not already use a screenshot directory, store new captures
  in `docs/screenshots/`.
- Do not silently mix an old screenshot directory with a new one.
- For native macOS apps, "real screenshots" means building and launching the
  current app and capturing the real app window, not just reusing old assets.
- If fresh capture is blocked or skipped, explain why before falling back.
- If real screenshots are blocked or unavailable, reuse still-valid existing
  screenshots only as a documented fallback, not as silent success.
- If real screenshots are blocked or unavailable and generated imagery is the
  only option, pause before using it.
- Always report whether screenshots were freshly captured, reused, or pending,
  along with the attempted capture tool, command, path, and any blocker.

## Quick start

1. Identify the target repo path before drafting or capturing anything.
2. Run `scripts/detect-app-type.sh /absolute/path/to/target-repo`.
3. Run `scripts/discover-app-readme-surface.sh /absolute/path/to/target-repo`.
4. Read the current `README.md`, app entrypoints, UI/settings files,
   install/build/test scripts, and branding/screenshot assets reported by the
   scripts.
5. Follow the required structure and rules in
   [`references/readme-app-spec.md`](references/readme-app-spec.md).
6. Follow the capture workflow in
   [`references/screenshot-capture-guide.md`](references/screenshot-capture-guide.md).

## Workflow

1. Map the product from code, not from old docs.
   - Read the current `README.md` first to understand what exists today.
   - Read the app manifests and entrypoints next.
   - Read the user-facing UI/menu/settings source files that define what the
     product actually shows and supports.
   - Read install, build, run, and test scripts before describing setup.
2. Detect app type.
   - Run `scripts/detect-app-type.sh` first.
   - Note the app type, framework, dev command, dev port, and dark-mode signal.
   - Use that output to choose the capture path before drafting the README.
3. Identify branding, screenshots, and UI surfaces.
   - Find the logo or icon already used in the README.
   - Preserve existing branding paths when they are still valid.
   - Find stable screenshot directories and decide whether current images are
     still accurate.
   - Preserve an existing screenshot directory such as `docs/images/` unless
     there is a good reason to migrate.
   - If no screenshot directory is established, use `docs/screenshots/`.
   - Pick one screenshot directory for the refresh and do not silently mix
     both old and new locations.
   - Read router, route, modal, dialog, and menu surfaces so screenshot capture
     covers the real product shape.
4. Capture screenshots.
   - Follow
     [`references/screenshot-capture-guide.md`](references/screenshot-capture-guide.md).
   - Use the chosen screenshot directory consistently.
   - Capture 4-6 key views such as the main screen, settings, menus, modals,
     and dark-mode variants when supported.
   - Report each screenshot as one of: freshly captured from the current
     running app, existing screenshot reused, or pending.
   - Explain why fresh capture was blocked or skipped before falling back to
     reused screenshots or pending placeholders.
   - Handle environment blockers honestly and fall back in the documented
     order.
5. Verify only implemented user-facing features.
   - Include features only when current source or tests support them.
   - Rewrite technical behavior into plain language.
   - Remove roadmap items, internal architecture, and stale caveats from the
     top sections.
6. Build the README in product-page order.
   - App name
   - Logo at the top
   - One short intro sentence
   - App preview / screenshots with an HTML table gallery
   - User-facing features
   - Install / getting started
   - Developer install / local setup
7. Validate before finishing.
   - Confirm logo stays at the top.
   - Confirm screenshot files exist at the referenced paths.
   - Confirm the screenshot gallery uses HTML table markup.
   - Confirm screenshot image files stay under the size target.
   - Confirm the final note states which screenshots were newly captured, which
     were reused, which are pending, what tool or command was attempted for
     capture, and what blocker occurred if fresh capture failed.
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

- update the target repo's `README.md`
- keep copy concise and polished
- preserve the project's existing branding assets
- capture or refresh screenshot files when needed
- state the screenshot status used: fresh capture, reused, or pending
- document any blocked or skipped fresh-capture attempt before fallback
- include a final verification note listing newly captured screenshots, reused
  screenshots, attempted capture tool or command and path, and any blocker
- make the README easy for a new user to understand before installation
- avoid carrying over product-specific wording from a previously edited app

## Good trigger examples

- `refresh this app README`
- `rewrite README for the current app`
- `verify README against the codebase`
- `update screenshots in the README`
- `make this app README feel like a product page`

## Bundled resources

- `scripts/detect-app-type.sh`: app type detection and local-run metadata for
  screenshot planning.
- `scripts/discover-app-readme-surface.sh`: read-only discovery for likely
  README inputs in app repos.
- `references/readme-app-spec.md`: required README structure, screenshot rules,
  copy rules, and verification checklist.
- `references/screenshot-capture-guide.md`: app-type-specific capture workflow,
  fallbacks, and screenshot file conventions.
