# De-Lovable Removal Playbook

Exact recipes for each trace type. Run `scripts/find-lovable-traces.sh <repo>`
first; every edit below maps to a section of that output. Apply edits, then
run the build. Do not claim success until the build passes.

---

## 1. `vite.config.*` — tagger plugin

Lovable injects a dev-only component tagger. Remove both the import and the
plugin entry, and simplify the plugin array back to a plain list.

Before (typical):

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { componentTagger } from "lovable-tagger";

export default defineConfig(({ mode }) => ({
  server: { host: "::", port: 8080 },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
}));
```

After:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  server: { host: "::", port: 8080 },
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
});
```

Notes:

- Delete the `import { componentTagger } from "lovable-tagger";` line.
- Remove the `mode === "development" && componentTagger()` entry.
- If the array no longer needs `.filter(Boolean)`, drop it.
- If `mode` is now unused, collapse `defineConfig(({ mode }) => (...))` back to
  `defineConfig({ ... })`. If `mode` is still used elsewhere, keep the callback.

---

## 2. `package.json` — dependency

- Delete the `"lovable-tagger": "..."` line from `dependencies` or
  `devDependencies` (Lovable usually puts it in `devDependencies`).
- Delete any `"gpt-engineer"` entry if present.
- Do NOT hand-edit the lockfile. Regenerate it after the edit (see section 7).

---

## 3. `index.html` — meta tags

Lovable stamps SEO/OpenGraph tags that point at its own domain. Rewrite them to
real project values rather than deleting them — an app with no `<title>` or
description is worse than one with Lovable's.

Before (typical):

```html
<title>Lovable App</title>
<meta name="description" content="Lovable Generated Project" />
<meta name="author" content="Lovable" />
<meta property="og:title" content="Lovable App" />
<meta property="og:description" content="Lovable Generated Project" />
<meta property="og:image" content="https://lovable.dev/opengraph-image-p98pqg.png" />
<meta name="twitter:site" content="@Lovable" />
<meta name="twitter:image" content="https://lovable.dev/opengraph-image-p98pqg.png" />
```

After (use the real project name/description from code, `notes/`, or `CLAUDE.md`):

```html
<title>{Real Project Name}</title>
<meta name="description" content="{One accurate sentence about the app}" />
<meta name="author" content="{Owner or team}" />
<meta property="og:title" content="{Real Project Name}" />
<meta property="og:description" content="{One accurate sentence about the app}" />
<!-- og:image and twitter:image: point at a real asset in public/ or remove if none exists yet -->
<meta name="twitter:card" content="summary_large_image" />
```

Notes:

- Also remove any `<script src="https://cdn.gpteng.co/gptengineer.js">` or
  similar gpt-engineer script tags from the `<body>`.
- If the project has no OG image yet, remove the `og:image` / `twitter:image`
  lines rather than leaving a broken Lovable URL. Do not fabricate an image
  path that does not exist.

---

## 4. `README.md` — rewrite (the big one)

Lovable ships a fixed boilerplate README. Replace the whole file with an
accurate, product-page-style README. Derive everything from the real repo:
project name, purpose, stack, and scripts.

### README template

```markdown
# {Real Project Name}

{One-sentence description of what the app actually does, from the code/notes.}

<!-- Keep an existing logo/screenshot at the top if the repo already has one. -->
<!-- Preserve existing screenshot placeholders/paths; do not invent captures. -->

## Features

- {Feature grounded in real code}
- {Feature grounded in real code}
- {Feature grounded in real code}

## Tech stack

- {e.g. React 18 + Vite + TypeScript}
- {e.g. Tailwind CSS + shadcn/ui}
- {e.g. Supabase / FastAPI — only if actually used}

## Getting started

\`\`\`sh
{install command matching the lockfile — npm install / bun install / pnpm install}
{dev command from package.json — e.g. npm run dev}
\`\`\`

## Build

\`\`\`sh
{build command from package.json — e.g. npm run build}
\`\`\`
```

### README rewrite rules

- Delete every Lovable heading: `# Welcome to your Lovable project`,
  `## Project info`, `## How can I edit this code?`, the "Use Lovable" /
  "Use GitHub Codespaces" / "Edit a file directly in GitHub" blocks, and the
  `**URL**: https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID` line.
- Delete the Lovable deploy/custom-domain sections
  (`docs.lovable.dev/features/custom-domain`, "Simply open Lovable ... Publish").
- Do not fabricate features. Only list what the code, `notes/`, or `CLAUDE.md`
  supports. If unsure, keep the feature list short and accurate.
- If the repo already uses a logo or screenshot at the top of the README, keep
  it at the top. Preserve existing screenshot directory paths
  (`docs/screenshots/`, `docs/images/`, etc.); do not invent new captures.
- Match install/build/dev commands to the actual `package.json` scripts and the
  lockfile's package manager.

For a fuller product-page rewrite with real screenshot capture, hand off to
`v-readme-app` / `v-readme-web`. This skill only de-Lovables the README.

---

## 5. Never-imported generated components (`orphan?:` rows)

The script's `orphan?:` list is a **heuristic**, not a verdict. A file is listed
when its module stem never appears as an import specifier anywhere in `src/`
(plus root build/test configs). Before deleting any file:

- Confirm it is not loaded via a dynamic import: `import(...)`, `React.lazy(...)`.
- Confirm it is not pulled in via a glob or barrel re-export
  (`export * from "./x"`, `import.meta.glob`).
- Confirm it is not referenced from a config, test setup, or HTML entry outside
  `src/` (some are; the script already folds in `vite.config.*`,
  `vitest.config.*`, and `index.html`).

Only delete files you have confirmed are truly unreferenced. shadcn/ui
components under `src/components/ui/` are frequently unused after generation and
are usually safe to delete once confirmed — but mark any you are unsure about as
`keep` in the removal table and say why. When in doubt, keep it.

---

## 6. Placeholder / generated assets

- `public/placeholder.svg`, `public/placeholder.png`, `src/assets/placeholder.*`
  — delete if unreferenced.
- The default Lovable `favicon.ico` / `public/opengraph-image-*.png` — delete or
  replace with a real asset; do not leave links to Lovable's CDN image.
- Confirm each asset is not referenced in `index.html` or `src/` before
  deleting (same discipline as orphan components).

---

## 7. Regenerate lockfile + build

Pick the command matching the lockfile the script reported:

| Lockfile           | Reinstall (relock)  | Build            |
| ------------------ | ------------------- | ---------------- |
| `package-lock.json`| `npm install`       | `npm run build`  |
| `bun.lockb`/`bun.lock` | `bun install`   | `bun run build`  |
| `pnpm-lock.yaml`   | `pnpm install`      | `pnpm run build` |
| `yarn.lock`        | `yarn install`      | `yarn build`     |

- Run the reinstall only if a dependency was removed from `package.json`, so the
  lockfile drops `lovable-tagger`.
- Run the build last. Read the emitted chunk sizes. Vite warns above 500 kB by
  default; flag any chunk over 500 kB in the build verdict.
- If the build fails, report the exact first error and stop. Do not claim
  success, and do not silently leave a half-cleaned repo without saying so.

---

## No-traces path

If `scripts/find-lovable-traces.sh` reports no Lovable traces (no
`lovable-tagger`, no `lovable.dev`/`gpt-engineer` URLs, no Lovable meta tags, no
boilerplate README headings):

- Do not manufacture a removal table.
- State plainly: "No Lovable traces found — nothing to strip."
- Still run the build if the user wants a verification pass, and report the
  build verdict.
- If only the README boilerplate remains (traces already stripped from config
  and HTML), rewrite just the README and say so.
