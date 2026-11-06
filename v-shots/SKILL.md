---
name: v-shots
description: "Capture real public routes of a running Vite/React app into docs/screenshots and update README image references. Use for route screenshot refreshes; use v-readme for prose and structure."
---

# README Screenshot Generator

Capture a fresh screenshot for every public route of a Vite/React app and wire the files into the README with a strict manifest.

This is a **generator** that writes files: it saves PNGs under `docs/screenshots/` and edits the README. It does not restructure README prose — for that, run v-readme first, then run this skill to fill the screenshot placeholders they leave behind.

## Evidence and execution

Treat route extraction as a candidate inventory and confirm nested paths and guard behavior from router code. Inspect each captured image before wiring it into documentation; an HTTP response or existing PNG alone does not prove the intended page rendered.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## Quick flow

The route scanner uses the target project’s TypeScript parser when available, with a regex fallback that emits only unverified `candidate` entries. Confirm the inventory against the actual router. Resolve relative child paths against their parents, inherited guards, index routes, and configured basenames before capture. Save the reviewed route list as JSON for the capture helper.

1. Discover routes: `node scripts/list-routes.mjs <repo-path>` — parses `App.tsx` / router config into a JSON route list on stdout. Read the JSON; do not guess routes from memory.
2. Classify each route from the JSON before capturing:
   - `public` — capture it.
   - `auth` / `protected` — mark SKIPPED (reason: requires login), never fake a placeholder image.
   - `dynamic` (has `:param`) — supply a verified concrete `samplePath` before capture, else SKIPPED (reason: needs a real param).
   - `candidate` — resolve the actual path, basename, and guards before explicitly reclassifying it. Static analysis cannot prove loader authentication or runtime redirects.
3. Confirm the dev command and port. Check `package.json` scripts (`dev`), `vite.config.*` for `server.port`, and any existing `.claude/launch.json`. Start the dev server (use the preview/launch tooling or `npm run dev`) and wait until it serves.
4. Capture: `node scripts/capture-routes.mjs <repo-path> --base-url http://localhost:<port> --routes <routes.json>` (add `--mobile` for 375x812 variants when the user asks). It writes `docs/screenshots/<route-slug>.png`, waits for DOM content and a visible content selector, then prints one line per capture. Set `--wait-for <selector>` or each route’s `readySelector` to identify completed page content; `body` is the fallback and does not prove data finished loading. Set `--timeout-ms <milliseconds>` when necessary.
5. Wire the README: replace the user's screenshot-placeholder comments (e.g. `<!-- screenshot: home -->`) or stale image paths with the fresh files. Preserve any top-of-README logo/branding placement. See [references/readme-wiring.md](references/readme-wiring.md) for the exact anchor patterns and Markdown to emit.
6. Emit the manifest table (see Output contract). Stop only the dev server process started for this task; preserve a server that was already running.

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

- This skill fills screenshots and wires them in. It does not rewrite README structure, feature copy, or branding — use v-readme for that.
- It does not test route behavior or accessibility — use the v-test skill.
- It captures only what a real running app renders; it never fabricates a screenshot for a route it could not load.

See [references/capture-playbook.md](references/capture-playbook.md) for viewport standards, wait strategy, dev-server handling, and dynamic-route resolution.
