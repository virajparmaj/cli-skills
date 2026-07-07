---
name: v-delovable
description: "Strip every Lovable / gpt-engineer trace from a freshly generated repo and leave a real project behind, then verify it still builds. This skill EXECUTES the cleanup end to end for Vite + React + TypeScript + Tailwind/shadcn repos: removes lovable-tagger/componentTagger from vite.config, deletes lovable.dev and gpt-engineer URLs and script tags, replaces the Lovable meta tags in index.html, rewrites the generated boilerplate README into an accurate product-page-style README (screenshot placeholders preserved), drops the lovable-tagger dependency, removes confirmed never-imported generated components and leftover placeholder assets, then runs the build and flags any chunk over 500 kB. Use when asked to remove lovable trace, de-lovable this repo, clean up the lovable boilerplate, strip the generated branding, or de-lovable workflow. For a review-only maintainability audit that does not edit files, use v-vibe; this skill actually applies the removals."
---

# De-Lovable Executor

Strip every Lovable trace from a freshly vibe-coded repo, rewrite the README into a real one, and confirm the app still builds.

This skill EXECUTES the cleanup. It is the opposite of a review skill: after presenting the plan you apply the removals, rewrite files, and run the build. For a review-only architecture audit that only reports findings, use `v-vibe`.

## Quick flow

1. Run `scripts/find-lovable-traces.sh <repo-path>` first to enumerate every trace deterministically. Do not grep by hand; this is the source of truth for the removal table.
2. Read the current `README.md`, `index.html`, `vite.config.*`, and `package.json` so the rewrite reflects reality. If `notes/` or `CLAUDE.md` exist, read them to learn the real project name, purpose, and stack before rewriting the README.
3. Build the removal table (see Output contract) from the script output. Every row is `trace | file:line | action`, where action is `delete`, `rewrite`, or `keep`. Mark heuristic `orphan?:` files `keep` unless you have confirmed they are truly unreferenced.
4. Apply the removals following [references/removal-playbook.md](references/removal-playbook.md): edit `vite.config.*`, `index.html`, `package.json`, delete confirmed orphan files and placeholder assets, and regenerate the lockfile if `lovable-tagger` was removed.
5. Rewrite `README.md` from the boilerplate into an accurate product page following the template in [references/removal-playbook.md](references/removal-playbook.md). Preserve any existing logo at the top and keep screenshot placeholders/paths intact.
6. Run the build (`npm run build`, or the package manager the lockfile implies). Flag any emitted chunk over 500 kB. If the build fails, report the exact error and stop before claiming success.
7. Emit the final three-part output exactly as specified below.

## What counts as a trace

- `lovable-tagger` import and `componentTagger()` plugin call in `vite.config.*` (delete the import and the plugin entry).
- `lovable-tagger` in `package.json` dependencies/devDependencies (delete, then regenerate the lockfile).
- `lovable.dev`, `docs.lovable.dev`, `gpt-engineer`, `gptengineer`, `cdn.gpteng.co` URLs and script tags anywhere.
- Lovable meta tags in `index.html`: `<title>Lovable App</title>`, `name="description"` / `name="author"` set to Lovable, `og:*` and `twitter:*` tags pointing at `lovable.dev/opengraph-image-p98pqg.png` (rewrite to real values, do not just delete the SEO tags).
- Generated README boilerplate: `# Welcome to your Lovable project`, `## Project info`, `## How can I edit this code?`, "Use Lovable", "Use GitHub Codespaces", `REPLACE_WITH_PROJECT_ID` (rewrite the whole file).
- Confirmed never-imported generated components (`orphan?:` rows) and leftover placeholder assets like `public/placeholder.svg` and the default Lovable `favicon.ico`.

## Output contract (strict)

Produce exactly these three parts, in this order, and nothing else after the build verdict:

1. A removal table:

```
| Trace | File:line | Action |
| ----- | --------- | ------ |
| componentTagger plugin | vite.config.ts:15 | delete |
| lovable-tagger import | vite.config.ts:4 | delete |
| lovable-tagger dep | package.json:82 | delete + relock |
| Lovable meta tags | index.html:9-21 | rewrite |
| Lovable README boilerplate | README.md:1-73 | rewrite |
| Unused generated component | src/components/NavLink.tsx | delete |
| Default placeholder asset | public/placeholder.svg | delete |
```

2. A one-line README delta summary, e.g. `README: replaced 73 lines of Lovable boilerplate with product-page intro, feature list, and dev setup; screenshot placeholders preserved.`

3. A build verdict, one of:
   - `Build: PASS — largest chunk <name> XXX kB (under 500 kB).`
   - `Build: PASS — WARNING: chunk <name> XXX kB exceeds 500 kB.`
   - `Build: FAIL — <first error line>. No success claimed; fix before shipping.`

Do not add commentary, next-steps prose, or a recap outside these three parts.

## Guardrails

- Confirm each `orphan?:` file is genuinely unreferenced (check dynamic imports, glob imports, and barrel re-exports) before deleting. When unsure, mark it `keep` and say so — never delete a file the app might load at runtime.
- Rewrite SEO meta tags to real project values; do not leave `index.html` with no `<title>` or description.
- Never hand-edit lockfiles. Remove the dependency from `package.json`, then regenerate the lockfile with the repo's package manager.
- Do not invent product features for the README. Derive the name, purpose, and feature list from the actual code, `notes/`, or `CLAUDE.md`; keep screenshot placeholders rather than fabricating captures.
- If the repo has no Lovable traces at all, say so and skip to the build verdict instead of manufacturing a removal table. See [references/removal-playbook.md](references/removal-playbook.md) for the no-traces path.

## Boundary with adjacent skills

- `v-vibe` reviews architecture and maintainability without editing; this skill executes the Lovable cleanup. Use `v-vibe` first if the user wants findings only.
- For a full product-page README rewrite with real screenshot capture, use `v-readme-app` / `v-readme-web`. This skill only rewrites the README enough to erase Lovable boilerplate and keep placeholders honest.

See [references/removal-playbook.md](references/removal-playbook.md) for exact per-file edit recipes, the README rewrite template, the lockfile-regeneration and build commands, and the no-traces path.
