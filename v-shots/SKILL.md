---
name: v-shots
description: "Auto-capture route screenshots from a running Vite/React app and wire them into the README, closing the manual screenshot step that v-readme-app and v-readme-web always leave dangling. Discovers routes deterministically with scripts/list-routes.mjs (parses React Router config and App.tsx route elements), starts the dev server, captures each public route with Playwright at 1280x800 (plus 375x812 mobile on request) into docs/screenshots/<route-slug>.png, then patches README placeholders or stale image paths and emits a strict manifest table. Routes behind auth are listed SKIPPED with a reason, never faked. Use when asked to capture screenshots for the readme, fill in the readme screenshots, screenshot the routes, screenshot every page, refresh docs/screenshots, or wire captured images into the README. Trigger phrases: capture screenshots for the readme, fill in the readme screenshots, screenshot the routes, update docs/screenshots, add screenshots to README."
---

# README Screenshot Generator

Capture a fresh screenshot for every public route of a Vite/React app and wire the files into the README with a strict manifest.

This is a **generator** that writes files: it saves PNGs under `docs/screenshots/` and edits the README. It does not restructure README prose — for that, run v-readme-app (apps) or v-readme-web (websites) first, then run this skill to fill the screenshot placeholders they leave behind.

## Quick flow

Scripts run first to produce deterministic facts; model judgment (route classification, README wiring) comes after.

1. Discover routes: `node scripts/list-routes.mjs <repo-path>` — parses `App.tsx` / router config into a JSON route list on stdout. Read the JSON; do not guess routes from memory.
2. Classify each route from the JSON before capturing:
   - `public` — capture it.
   - `auth` / `protected` — mark SKIPPED (reason: requires login), never fake a placeholder image.
   - `dynamic` (has `:param`) — capture only if the script resolved a concrete sample path, else SKIPPED (reason: needs a real param).
3. Confirm the dev command and port. Check `package.json` scripts (`dev`), `vite.config.*` for `server.port`, and any existing `.claude/launch.json`. Start the dev server (use the preview/launch tooling or `npm run dev`) and wait until it serves.
4. Capture: `node scripts/capture-routes.mjs <repo-path> --base-url http://localhost:<port> --routes <routes.json>` (add `--mobile` for 375x812 variants when the user asks). It writes `docs/screenshots/<route-slug>.png`, waits for network idle per route, and prints one line per capture.
5. Wire the README: replace the user's screenshot-placeholder comments (e.g. `<!-- screenshot: home -->`) or stale image paths with the fresh files. Preserve any top-of-README logo/branding placement. See [references/readme-wiring.md](references/readme-wiring.md) for the exact anchor patterns and Markdown to emit.
6. Emit the manifest table (see Output contract). Stop the dev server when done.

## Output contract (strict)

After capturing, output exactly two things and nothing else:

1. One fenced `markdown` block containing the manifest table with these columns and rows sorted by route path:

   | route | file | size | viewport | README anchor updated |
   | ----- | ---- | ---- | -------- | --------------------- |

   - `route` — the URL path (e.g. `/`, `/dashboard`).
   - `file` — repo-relative path (e.g. `docs/screenshots/home.png`) or `SKIPPED`.
   - `size` — human-readable file size (e.g. `184 KB`) or `—` for skipped.
   - `viewport` — `1280x800`, `375x812`, or `1280x800 + 375x812`.
   - `README anchor updated` — `yes`, `no`, or `n/a` (skipped).

2. One short SKIPPED list below the table: each skipped route on its own `- ` line with the exact reason (`requires login`, `needs a real param`, `dev server never served this path`). If nothing was skipped, write `- none`.

Do not narrate the capture loop or add prose outside these two blocks.

## Slug naming rules

- `/` → `home`.
- Strip the leading slash, replace remaining `/` and `:` with `-`, lowercase (e.g. `/settings/profile` → `settings-profile`).
- Mobile variants append `-mobile` before the extension (e.g. `home-mobile.png`).
- Never overwrite a screenshot for a different route; if two routes collide on a slug, suffix the second with `-2` and note it.

## No routes / not a Vite-React app

- If `list-routes.mjs` finds no routes (no router, single-page `main.tsx` mount, or a non-React repo), do not invent any. Report: no routable views found, capture the single mounted view at `/` as `home.png` if a dev server serves it, else emit an empty manifest table and state that this repo has no discoverable routes.
- If there is no `dev` script or the server never binds a port, stop and report the blocker instead of producing fake images.

## Scope boundary

- This skill fills screenshots and wires them in. It does not rewrite README structure, feature copy, or branding — use v-readme-app / v-readme-web for that.
- It does not test route behavior or accessibility — use the v-test-* skills.
- It captures only what a real running app renders; it never fabricates a screenshot for a route it could not load.

See [references/capture-playbook.md](references/capture-playbook.md) for viewport standards, wait strategy, dev-server handling, and dynamic-route resolution.
