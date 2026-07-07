---
name: v-triage
description: "Diagnose a pasted error and apply the smallest fix, returning a strict four-section block (DIAGNOSIS, ROOT CAUSE, SMALLEST FIX, VERIFY). Use whenever the user pastes a raw stack trace, build error, traceback, or compiler/runtime error, or says fix this, check what's wrong with this error, diagnose this traceback, why is this failing. Covers Veer's stack: React 18 + Vite + TS strict + Tailwind/shadcn, Supabase, Vercel, FastAPI/Python on Render. Runs scripts/locate-error.sh to pull file:line frames, module tokens, and error codes from the text, map them to real repo files (dropping node_modules/dist noise), and print surrounding code plus git-blame recency for the top frame. Classifies into families: TS build, Vite/Rollup, React runtime, Vercel deploy, FastAPI/Python traceback, Supabase. Hard rule: never ask clarifying questions when a stack trace or file:line frame is present. Triggers: error TS####, Traceback (most recent call last), Uncaught TypeError, Failed to resolve import, PGRST codes, RLS violations."
---

# Error Triage & Smallest-Fix

Paste any raw error; get a diagnosis, the smallest fix (applied), and one verify command.

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

## The one hard rule

If the message contains a stack trace, build error, or any `file:line` frame, **do not ask clarifying questions.** Diagnose and fix. The trace already has what you need. Ask exactly one question only when there is no frame, no error code, and no recognizable signature — then stop.

## Quick flow

1. Run the locator on the pasted error text against the current repo — this gathers deterministic facts first:
   ```
   pbpaste | scripts/locate-error.sh <repo-path>
   # or if the text is in a file:
   scripts/locate-error.sh <repo-path> error.txt
   ```
   It prints the likely family, error codes/signatures, module tokens, raw frames, frames resolved to real repo files (build/dep noise dropped), and per top frame: ±15 lines of marked context plus git-blame recency.
2. Confirm the error family from the printed code — do not trust the heuristic guess blindly. Match it in [error-families.md](references/error-families.md).
3. Establish the root cause at the top resolved frame. Label it `Confirmed from code` (the context shows the defect) or `Strongly inferred` (signature + context make it near-certain, one hop away). Use fresh git recency as a regression tiebreaker.
4. Apply the smallest fix that resolves *this* error — no refactors, no renames, no unrequested error handling, no fixing adjacent bugs.
5. Emit the strict four-section contract below and nothing before it.

Follow [triage-protocol.md](references/triage-protocol.md) for the full step-by-step, the evidence-label rules, and the verify-command-per-family table.

## Output contract (strict)

Return exactly these four sections, in this order, nothing before them:

```
DIAGNOSIS: <one sentence — what is failing and at what layer>
ROOT CAUSE: <file:line> — <Confirmed from code | Strongly inferred> — <the cause in one line>
SMALLEST FIX: <the edit you applied, in one or two lines; the diff is applied>
VERIFY: <exactly one command to confirm the fix>
```

Rules:

- **DIAGNOSIS** — one sentence, plain terms, no jargon dump.
- **ROOT CAUSE** — must carry a `file:line` (or a `file` plus a named one-hop file when strongly inferred) and an evidence label. No label = not shippable.
- **SMALLEST FIX** — actually apply the edit with the editor, then describe it. If you truly cannot edit, say so and give the exact patch.
- **VERIFY** — one command, chosen for the family (see the table in the protocol), not a checklist.
- After the four sections you may add at most one line flagging a separate latent bug you noticed. Do not fix it in this pass. Nothing else follows.

## Recurring families

`typescript-build` · `vite-rollup-build` · `react-runtime` · `vercel-deploy` · `python-fastapi-traceback` · `supabase`. Signatures, usual root causes, and smallest-fix patterns for each are in [error-families.md](references/error-families.md).

## Edge cases

- **No frame resolved to the repo** (top frame is in `node_modules/`, `site-packages/`, `dist/`, or another repo): still emit the four sections; ROOT CAUSE cites the signature + context labeled `Strongly inferred` and names the likely repo-side trigger; never invent a `file:line` you did not see.
- **No frame, no code, no signature at all**: ask exactly one targeted question ("which command produced this?" / "paste the full traceback"), then stop. Never open a multi-question interrogation.
- **Empty or non-error paste**: say there is no error to triage and ask what to run.

## Boundaries with other skills

- Deep serving/inference correctness review → **v-ml** (this skill fixes the immediate error only).
- Loading/empty/error-state UX gaps → **v-ux**.
- Secrets, RLS hardening, API abuse resistance → **v-security**.
- Commit message for the fix once verified → **v-git**.

See [references/triage-protocol.md](references/triage-protocol.md) for the full diagnostic protocol and evidence-labeling rules.
