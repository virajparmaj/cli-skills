---
name: v-vercel-doctor
description: "Diagnose a Vite/React app that works locally but fails on Vercel by comparing environment keys, routing/build config, assets, URLs, and CORS. Review-only unless fixes are requested."
---

# Vercel Divergence Doctor

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Briefly justify both ratings from current usage and the observed consequence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Diagnose why a Vite/React app works on `localhost` but breaks on Vercel, and hand back the exact fix commands.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes — the deliverable is a divergence table plus a copy-paste fix block, not code changes.

This skill is a **diagnostic**: it does not audit for quality (use `v-frontend` for perf, `v-vibe-app` for launch readiness). It only explains local-vs-Vercel divergence and how to close it.

## Evidence and execution

Compare the deployed project and environment with the actual local configuration. Missing local declarations, a bundle warning, or a scanner hit alone does not establish a production defect; distinguish measured facts from unavailable remote evidence.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## The four recurring culprits

Almost every "works locally, breaks on Vercel" case is one of these. The script gathers evidence for all four in one pass:

1. **Env-var mismatch** — a key the code reads (`import.meta.env.VITE_*` or `process.env.*`) is set locally in `.env` but absent from Vercel Production, so it resolves to `undefined` in the deployed bundle.
2. **vercel.json config** — a Vite SPA with client-side routing needs a catch-all rewrite; without it, deep links and refresh 404. Missing headers, function config, or wrong `outputDirectory` also diverge.
3. **Bundle delivery** — measure emitted chunk sizes and inspect failed requests or runtime evidence. A Vite 500kB warning alone does not prove a timeout, blank screen, or Vercel deployment limit.
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

Emit the diagnosis table and any verified fix commands in this order; add concise deferral or verification-gap lines when needed:

**A. Divergence table** — one Markdown table, most severe first, columns exactly:

| Severity | Symptom / trigger | Evidence (file:line) | Local value | Vercel value | Frequency x impact = score (reasons) | Smallest fix |
| --- | --- | --- | --- | --- | --- | --- |

- Severity is `P0` (site broken / blank / core flow dead in prod), `P1` (a feature silently fails or a route 404s), or `P2` (works but fragile: oversized chunk, wildcard CORS, unpinned config).
- Label each row `Confirmed from code` or `Strongly inferred` in the Symptom cell.
- `vercel env ls` establishes key names and environments, not decrypted values. Report presence/absence only when that listing was verified; otherwise write `not verified`. A missing local declaration does not establish a missing Production key. Never print secret values.
- If a culprit is clean, do not invent a row — instead list it under a short "Clean" line beneath the table (e.g. "Clean: SPA rewrite present; no chunks over 500kB").

**B. Fix commands** — a single fenced ```bash``` block with the exact, ordered commands for verified in-scope rows meeting the score threshold: `vercel env add KEY production`, the `manualChunks` snippet for `vite.config.ts`, the `vercel.json` rewrite/header block, the CORS origin edit. Real values only; do not print secret values — use `vercel env add KEY production` (which prompts) rather than echoing the secret. Include concise `Deferred issues` and verification-gap lines when needed by the practical review policy. Keep code/config examples in their correct language fences rather than presenting JSON or TypeScript as executable bash.

## Edge cases

- **Not a Vite/Vercel repo** (no `package.json`, no `vercel.json`, no `vite.config.*`): say so and stop — this skill only diagnoses Vite/React → Vercel divergence.
- **No divergence found**: return the table header, a single row-less "Clean:" line covering all four culprits, and skip the fix block. Do not manufacture findings.
- **Vercel CLI not authed / project not linked**: the script prints a notice instead of the env list. Report remote configuration as unverified; local key absence is not a production finding. Suggest the appropriate read-only listing or dashboard check. Run `vercel link` only when linking the chosen project is authorized.
- **Build not run** (`--build` omitted): report chunk sizes only if a prior `dist/` exists; otherwise flag chunk analysis as "not measured — re-run with --build" rather than guessing.

See [references/divergence-playbook.md](references/divergence-playbook.md) for the per-culprit evidence guide, severity rubric, and ready-to-paste fix snippets.
