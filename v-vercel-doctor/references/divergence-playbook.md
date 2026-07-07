# Vercel Divergence Playbook

Read this after running `scripts/vercel-divergence.sh`. It maps every script section to one of the four culprits, tells you how to grade severity, and gives ready-to-paste fixes. Stay in review mode: the deliverable is the divergence table and the fix block, not edited files.

## How to read the script output

The script prints `=== section ===` blocks. Map them to culprits:

| Script section | Culprit | What a problem looks like |
| --- | --- | --- |
| `env keys in code but NOT in any local .env*` | #1 env | `MISSING_LOCALLY: KEY` lines — key is read in code but declared nowhere; almost certainly missing on Vercel too |
| `code-referenced keys NOT found in Vercel Production` | #1 env | `MISSING_ON_VERCEL: KEY` lines — confirmed absent from Production (only prints when `vercel env ls` succeeds) |
| `env keys in .env.example but NOT in .env / .env.local` | #1 env | `EXAMPLE_ONLY: KEY` — documented but unset; may be set locally via shell but forgotten on Vercel |
| `vercel.json` + `SPA_REWRITE` | #2 config | `SPA_REWRITE: MISSING` on a react-router app; wrong `outputDirectory`; missing security/cache headers |
| `oversized chunks (> N KB)` | #3 chunks | `BIG_CHUNK: NNNN KB path` lines |
| `API base URLs referenced in code` | #4 url/cors | `localhost:`/`127.0.0.1` in frontend files; a remote host hardcoded instead of read from env |
| `CORS configuration` + `wildcard vs explicit` | #4 url/cors | allow-list that omits the Vercel domains; `WILDCARD_CORS` combined with `allow_credentials=True` |

A `file:line` from the script is your evidence. Every table row must cite one.

## Severity rubric (P0–P2)

- **P0** — the deployed site is broken for the primary flow: blank page, build fails on Vercel, the app's only backend call is blocked (missing `VITE_API_URL`, CORS rejects the prod origin), or the app crashes on load.
- **P1** — a feature or route silently fails while the rest works: a secondary env key missing, deep-link/refresh 404 from a missing SPA rewrite, one API call blocked by CORS but others fine.
- **P2** — works today but fragile: a chunk over 500kB (slow/at-risk, not yet broken), wildcard CORS, `outputDirectory`/framework left to inference, headers not set.

Confidence label per row:
- `Confirmed from code` — proven by a `file:line` plus (for env) a successful `vercel env ls`, or a config value that is unambiguous.
- `Strongly inferred` — proven from code but the Vercel side could not be read (CLI not authed), or the failure depends on runtime routing you cannot execute here.

## Culprit #1 — Env-var mismatch

**Why it breaks:** Vite inlines `import.meta.env.VITE_*` at build time. If the key is not present in Vercel's Production environment when the build runs, it inlines `undefined`. `process.env.*` in serverless functions reads at runtime and is `undefined` if not set in Vercel. `.env` is gitignored, so what works on the laptop never reaches Vercel unless added explicitly.

**Confirm it:**
- `MISSING_ON_VERCEL: KEY` from the script is a confirmed gap.
- If the CLI was not authed, treat `MISSING_LOCALLY` keys as `Strongly inferred` — the developer must confirm against the Vercel dashboard → Settings → Environment Variables.
- Only `VITE_`-prefixed vars are exposed to the client bundle. A client file reading a non-`VITE_` key is a separate bug worth flagging.

**Fix snippet (never echo secret values — `vercel env add` prompts securely):**
```bash
# add each missing key to Production (and Preview/Development if the app needs it)
vercel env add VITE_API_URL production
vercel env add VITE_API_URL preview
# then trigger a fresh build so Vite re-inlines the values
vercel --prod
```

## Culprit #2 — vercel.json config

**Why it breaks:** A Vite build is a static SPA. Client-side routes (`/dashboard`, `/report/123`) do not exist as files, so a hard refresh or deep link asks Vercel for a path with no file → 404. A catch-all rewrite to `/` (or `/index.html`) lets the SPA router take over.

**Confirm it:** `SPA_REWRITE: MISSING` plus a react-router/TanStack-router dependency in the code grep. Also check `outputDirectory` — Vite emits to `dist`, and if `vercel.json` or the dashboard points elsewhere the deploy serves nothing.

**Fix snippet (`vercel.json` at repo root):**
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    }
  ]
}
```
If the output dir is not `dist`, add `"outputDirectory": "dist"` and confirm the Vite `build.outDir`.

## Culprit #3 — Chunks over 500kB

**Why it matters:** Vite warns at 500kB. A single giant `index-*.js` blocks first paint, can blank-screen on slow mobile, and inflates the deploy. It rarely fails the build outright but is a real production divergence from a fast local dev server.

**Confirm it:** `BIG_CHUNK: NNNN KB path` from a `--build` run (or a prior `dist/`). If `--build` was not run and no `dist/` exists, report chunk analysis as "not measured — re-run with --build" rather than guessing.

**Fix snippet (`vite.config.ts` — split heavy vendors so they cache independently):**
```ts
// vite.config.ts
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          charts: ["recharts"],
          ui: ["@radix-ui/react-dialog", "@radix-ui/react-dropdown-menu"],
        },
      },
    },
  },
});
```
Also prefer route-level `React.lazy()` + `Suspense` for heavy pages, and dynamic `import()` for large libs used on one screen. Tune the `manualChunks` groups to the repo's actual big dependencies from the grep.

## Culprit #4 — Hardcoded URLs & CORS

**Why it breaks:** A base URL of `http://localhost:8000` works in dev but points at nothing from a deployed browser. And a FastAPI/serverless CORS allow-list that lists only `localhost` origins rejects requests from the Vercel prod domain and every `*.vercel.app` preview URL, surfacing as a CORS error in the console and a failed fetch.

**Confirm it:**
- Frontend `localhost:`/`127.0.0.1` in a base-URL assignment (not a comment) is `Confirmed from code`.
- The API base URL should come from `import.meta.env.VITE_API_URL` with the hardcoded value only as a fallback — verify which wins.
- On the backend, check that `allow_origins` includes the production Vercel domain. Preview deployments use rotating `*.vercel.app` subdomains, so a static list misses them — a regex or explicit preview handling is needed.
- `WILDCARD_CORS` (`allow_origins=["*"]`) with `allow_credentials=True` is invalid: browsers reject `*` when credentials are sent. Flag as P0/P1 if the app sends cookies or auth headers.

**Fix snippet (FastAPI):**
```python
# backend: read allowed origins from env, include prod + preview
import os, re
from fastapi.middleware.cors import CORSMiddleware

allowed = [o for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed or ["http://localhost:8080"],
    allow_origin_regex=r"https://.*\.vercel\.app",  # matches preview deploys
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Then set `ALLOWED_ORIGINS` on the backend host (e.g. Render) to the production Vercel URL, and set `VITE_API_URL` on Vercel to the backend URL so the frontend stops falling back to `localhost`.

## Assembling the report

1. One divergence table, rows sorted P0 → P2. Columns exactly: `Severity | Symptom | Evidence (file:line) | Local value | Vercel value | Smallest fix`.
2. Put the confidence label (`Confirmed from code` / `Strongly inferred`) inside the Symptom cell.
3. For any culprit with no problem, add one line under the table: `Clean: <culprit> — <why>` (e.g. `Clean: vercel.json — SPA rewrite present`).
4. One fenced `bash` block with the exact fix commands for every P0/P1 row, in dependency order (link/env first, then rebuild). Secrets are added via `vercel env add` prompts, never echoed.
5. If the CLI was not authed, make `vercel link` the first command so a re-run confirms env findings against Production.
6. Nothing outside the table, the `Clean:` lines, and the fix block.
