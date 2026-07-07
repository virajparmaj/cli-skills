# README Wiring

How to insert captured screenshots into the README without disturbing structure or branding. Run this after `capture-routes.mjs` has written the PNGs.

## What this step does and does not touch

- DOES: replace screenshot placeholders and stale image paths with the fresh files.
- DOES NOT: rewrite headings, feature copy, install instructions, or badges. For README structure use v-readme-app / v-readme-web first, then this skill to fill the gaps they leave.
- Preserve any top-of-README logo/branding block exactly where it is. Never move or replace the header logo with a route screenshot.

## Anchor patterns to look for

Replace, in this priority order:

1. **Explicit placeholder comments** the README-refresh skills leave behind. Match case-insensitively:
   - `<!-- screenshot: home -->`
   - `<!-- screenshot home -->`
   - `<!-- SCREENSHOT: /dashboard -->`
   - `<!-- TODO: add screenshot -->` (generic — fill with the `home` shot or the most representative public route).

   The token after `screenshot:` maps to a route by slug (`home` → `docs/screenshots/home.png`, `dashboard` → `docs/screenshots/dashboard.png`).

2. **Stale image references** pointing at the screenshots dir whose file was just regenerated:
   - `![...](docs/screenshots/xxx.png)`
   - `<img src="docs/screenshots/xxx.png" ...>`

   Keep existing alt text / width attributes; only the file is refreshed (path unchanged, so often no edit is needed — mark `README anchor updated: no` when the path already matched).

3. **A dedicated Screenshots section** (`## Screenshots` / `## Preview` / `## Demo`). If it exists and is empty or stale, populate it with a gallery (below). If none exists and there is no placeholder anywhere, do NOT create a section unless the user asked to — instead report the files in the manifest and note that no anchor was found (`README anchor updated: no`).

## Markdown to emit

Single hero screenshot (most common — replaces a `home` placeholder):

```markdown
![App home screen](docs/screenshots/home.png)
```

Gallery for a Screenshots section (one row per public route, alt text = a human route label):

```markdown
## Screenshots

| Home | Dashboard |
| ---- | --------- |
| ![Home](docs/screenshots/home.png) | ![Dashboard](docs/screenshots/dashboard.png) |
```

With mobile variants captured, pair them:

```markdown
| Desktop | Mobile |
| ------- | ------ |
| ![Home desktop](docs/screenshots/home.png) | ![Home mobile](docs/screenshots/home-mobile.png) |
```

## Alt text

- Derive from the route: `/` → `App home screen`; `/settings/profile` → `Settings profile screen`.
- Keep alt text meaningful (accessibility + Markdown fallback), never `screenshot` or the filename.

## Path correctness

- Always use repo-relative POSIX paths (`docs/screenshots/home.png`), never absolute machine paths.
- Confirm the file exists before writing the reference; a broken image link is worse than a missing one.

## Recording the outcome

For each route in the manifest table, set `README anchor updated`:

- `yes` — a placeholder/section was replaced or a new reference was inserted.
- `no` — file regenerated but the existing README path already pointed at it, or no anchor was found to update.
- `n/a` — route was SKIPPED (no screenshot exists).
