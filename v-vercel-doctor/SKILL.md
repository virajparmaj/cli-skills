---
name: v-vercel-doctor
description: "Diagnose why a Vite/React app works locally but breaks on Vercel by finding the exact divergence. Use for React 18 + Vite + TS + Tailwind + shadcn frontends on Vercel, optionally with Supabase or a FastAPI backend on Render. Runs scripts/vercel-divergence.sh to gather evidence for the four recurring culprits: env-var mismatch (code VITE_*/process.env keys vs .env* vs `vercel env ls`), vercel.json config (missing SPA rewrite, headers, function settings), chunks over 500kB from the build, and hardcoded localhost/backend URLs plus CORS origins that only work locally. Produces a severity-ranked divergence table (P0-P2) with symptom, evidence file:line, local vs Vercel value, and smallest fix, then a fenced bash block of fix commands. Trigger phrases: works locally but not on vercel, vercel deploy is broken, why is the deployed site failing, 404 on refresh on vercel, check env vars against vercel, CORS error only in production. For frontend perf use v-frontend; for launch readiness use v-production."
---

# Vercel Divergence Doctor

Diagnose why a Vite/React app works on `localhost` but breaks on Vercel, and hand back the exact fix commands.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes — the deliverable is a divergence table plus a copy-paste fix block, not code changes.

This skill is a **diagnostic**: it does not audit for quality (use `v-frontend` for perf, `v-production` for launch readiness). It only explains local-vs-Vercel divergence and how to close it.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Exhaust the search.** For discovery, keep going until two consecutive passes surface nothing new; do not stop at the first plausible batch. Never silently cap coverage — state what you skipped and why.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

## The four recurring culprits

Almost every "works locally, breaks on Vercel" case is one of these. The script gathers evidence for all four in one pass:

1. **Env-var mismatch** — a key the code reads (`import.meta.env.VITE_*` or `process.env.*`) is set locally in `.env` but absent from Vercel Production, so it resolves to `undefined` in the deployed bundle.
2. **vercel.json config** — a Vite SPA with client-side routing needs a catch-all rewrite; without it, deep links and refresh 404. Missing headers, function config, or wrong `outputDirectory` also diverge.
3. **Chunks over 500kB** — an oversized bundle that Vite warns about locally can time out, blank-screen, or trip Vercel limits in production.
4. **Hardcoded URLs / CORS** — a `localhost:8000` base URL or a CORS allow-list that omits the Vercel prod and preview domains works locally but is blocked in the browser after deploy.

## Quick flow

1. Run the evidence gatherer first so the diagnosis rests on deterministic facts, not guesses:
   ```
   scripts/vercel-divergence.sh <repo-path> [--build] [--chunk-kb 500]
   ```
   - `--build` runs the production build and extracts every emitted chunk over the threshold (slow, but the only way to measure culprit #3). Without it the script reports chunks from any prior `dist/` build.
   - `--chunk-kb N` overrides the 500kB threshold.
   - The script is read-only against source; it only writes to a build output dir when `--build` runs the project's own build.
2. Read the repo's own context before judging, in this order (skip missing files):
   - `CLAUDE.md`
   - `README.md`
   - `notes/10_deployment.md`
   - `notes/06_api_contracts.md`
   - `notes/11_known_issues.md`
   - `.env.example` (never read secret values out of `.env` into the report)
3. Map every piece of script evidence to one of the four culprits. Load [Divergence Playbook](references/divergence-playbook.md) for what each script section means, how to grade severity, and the exact fix snippets.
4. Produce the output using the contract below. Every row must trace to a `file:line` from the script or a config file — nothing speculative in the table.

## Output contract (strict)

Emit exactly two things, in this order:

**A. Divergence table** — one Markdown table, most severe first, columns exactly:

| Severity | Symptom | Evidence (file:line) | Local value | Vercel value | Smallest fix |
| --- | --- | --- | --- | --- | --- |

- Severity is `P0` (site broken / blank / core flow dead in prod), `P1` (a feature silently fails or a route 404s), or `P2` (works but fragile: oversized chunk, wildcard CORS, unpinned config).
- Label each row `Confirmed from code` or `Strongly inferred` in the Symptom cell.
- "Vercel value" is the actual value if `vercel env ls` ran, otherwise the strongly-inferred value (e.g. `undefined — key absent from Production`).
- If a culprit is clean, do not invent a row — instead list it under a short "Clean" line beneath the table (e.g. "Clean: SPA rewrite present; no chunks over 500kB").

**B. Fix commands** — a single fenced ```bash``` block with the exact, ordered commands to close every P0/P1 row: `vercel env add KEY production`, the `manualChunks` snippet for `vite.config.ts`, the `vercel.json` rewrite/header block, the CORS origin edit. Real values only; do not print secret values — use `vercel env add KEY production` (which prompts) rather than echoing the secret. Put nothing outside the table and this block except the one "Clean:" line.

## Edge cases

- **Not a Vite/Vercel repo** (no `package.json`, no `vercel.json`, no `vite.config.*`): say so and stop — this skill only diagnoses Vite/React → Vercel divergence.
- **No divergence found**: return the table header, a single row-less "Clean:" line covering all four culprits, and skip the fix block. Do not manufacture findings.
- **Vercel CLI not authed / project not linked**: the script prints a notice instead of the env list. Report env findings as `Strongly inferred` (code keys missing from local `.env*`), and put `vercel link` as the first fix command so a re-run can confirm against Production.
- **Build not run** (`--build` omitted): report chunk sizes only if a prior `dist/` exists; otherwise flag chunk analysis as "not measured — re-run with --build" rather than guessing.

See [references/divergence-playbook.md](references/divergence-playbook.md) for the per-culprit evidence guide, severity rubric, and ready-to-paste fix snippets.
