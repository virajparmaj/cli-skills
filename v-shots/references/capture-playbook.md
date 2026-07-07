# Capture Playbook

How this skill turns a running Vite/React app into a clean set of README screenshots. Follow these standards so every run is reproducible and no image is ever faked.

## 1. Route discovery (deterministic first)

Always run the script before reasoning about routes:

```bash
node scripts/list-routes.mjs <repo-path>
```

It prints a JSON array. Each entry:

```json
{ "path": "/dashboard", "kind": "public", "source": "src/App.tsx", "reason": "no auth or param signals" }
```

`kind` is one of:

- `public` — captured.
- `auth` — segment like `login`/`signup`/`auth` or a guard wrapper (`ProtectedRoute`, `RequireAuth`, `AuthGuard`). SKIPPED with reason `requires login`.
- `dynamic` — contains `:param` or `*`. SKIPPED with reason `needs a real param` unless you add a concrete `samplePath` (see below).

The parser reads both router styles:

- JSX: `<Route path="/x" element={...} />`
- Object config: `createBrowserRouter([{ path: "/x", ... }])` / route arrays.

It never executes code, so it is safe on any repo. If it returns `[]`, treat the app as single-view (capture `/` only) or non-routable — do not invent routes.

## 2. Resolving dynamic routes (optional)

For a `dynamic` route you want captured, add a `samplePath` to that entry before passing the JSON to the capture script. Pick a value that actually exists in dev (a seeded id, a demo slug). Example:

```json
{ "path": "/product/:id", "kind": "dynamic", "samplePath": "/product/demo-1", "source": "src/App.tsx" }
```

The capture script visits `samplePath` but slugs the file from the original `path` (`product-id.png`). Never use a fabricated id that renders a 404 or empty state — that is a fake screenshot. If no real sample exists, leave it SKIPPED.

## 3. Dev server

The capture script does NOT start the server; it screenshots one that is already running. Determine the command and port in this order:

1. `package.json` → `scripts.dev` (usually `vite`).
2. `vite.config.*` → `server.port` (Vite default is `5173`).
3. Existing `.claude/launch.json` if the repo already defines one.

Start it (preview/launch tooling or `npm run dev`), wait until it serves, then pass `--base-url http://localhost:<port>`. Stop the server after the manifest is emitted.

## 4. Viewport standards

- Desktop (always): **1280x800**, `deviceScaleFactor: 2` for crisp Retina-quality PNGs.
- Mobile (only when the user asks, via `--mobile`): **375x812** (iPhone-class), same scale factor.
- Full-page capture (`fullPage: true`) so long marketing pages are captured end to end, not just the fold.

## 5. Wait strategy

Per route the script:

1. `goto(url, { waitUntil: "networkidle", timeout: 30000 })` — lets Supabase/API calls and route-level code-split chunks finish.
2. `waitForTimeout(600)` — settles entrance animations and lazy images.
3. `screenshot({ fullPage: true })`.

If a route throws (timeout, crash, never served), it is reported SKIPPED with reason `dev server never served this path` — never retried into a blank image.

## 6. File naming

Slugs are derived, not free-form (mirrors SKILL.md):

| route | file |
| ----- | ---- |
| `/` | `docs/screenshots/home.png` |
| `/dashboard` | `docs/screenshots/dashboard.png` |
| `/settings/profile` | `docs/screenshots/settings-profile.png` |
| `/product/:id` | `docs/screenshots/product-id.png` |

Mobile variants append `-mobile` (`home-mobile.png`). Slug collisions get a `-2` suffix and a note in the SKIPPED list.

## 7. Command reference

```bash
# desktop only, routes from a file
node scripts/capture-routes.mjs <repo-path> \
  --base-url http://localhost:5173 \
  --routes routes.json

# pipe discovery straight into capture, desktop + mobile
node scripts/list-routes.mjs <repo-path> \
  | node scripts/capture-routes.mjs <repo-path> \
      --base-url http://localhost:5173 --routes - --mobile
```

Output lines are `CAPTURED <path> -> <file> (<size>, <viewport>)` or `SKIPPED <path> (<reason>)`. Turn these into the strict manifest table from the Output contract.

## 8. Honesty rules (non-negotiable)

- Never write a PNG for a route the app did not actually render.
- Auth routes are SKIPPED, not logged into with fake credentials, unless the user explicitly provides a login flow and asks for it.
- Dynamic routes without a real `samplePath` are SKIPPED.
- If Playwright is not installed, stop and print the install hint (`npm i -D playwright && npx playwright install chromium`) — do not silently produce nothing.
- The manifest must reflect files that exist on disk with real sizes; do not report a capture you did not verify.
