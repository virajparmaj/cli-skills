---
name: v-triage
description: "Diagnose a pasted stack trace, compiler/build error, or runtime failure and apply the smallest authorized fix. Report DIAGNOSIS, ROOT CAUSE, SMALLEST FIX, and VERIFY."
---

# Error Triage & Smallest-Fix

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Briefly justify both ratings from current usage and the observed consequence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Paste any raw error; get a diagnosis, the smallest fix (applied), and one verify command.

## Evidence and execution

Start from the supplied error and resolve its frames to current source. A frame is a starting point, not proof of the root cause; trace its callers or configuration and verify the proposed change against the original failure.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## The one hard rule

Use the supplied trace, build error, or `file:line` frame to start immediately. Apply the smallest fix when diagnosis/fixing is requested; an explicit explanation-only or review-only request stays read-only. If a necessary fact cannot be established from source or the trace, ask one targeted question while completing independent diagnosis.

## Quick flow

1. Run the locator on the pasted error text against the current repo — this gathers deterministic facts first:
   ```
   pbpaste | scripts/locate-error.sh <repo-path>
   # or if the text is in a file:
   scripts/locate-error.sh <repo-path> error.txt
   ```
   It prints the likely family, error codes/signatures, module tokens, raw frames, frames resolved to real repo files (build/dep noise dropped), and per top frame: ±15 lines of marked context plus git-blame recency.
2. Confirm the error family from the printed code — do not trust the heuristic guess blindly. Match it in [error-families.md](references/error-families.md).
3. Trace the top resolved frame and its relevant callers/configuration to establish the root cause. Label it `Confirmed from code` (the context shows the defect) or `Strongly inferred` (signature + context make it near-certain, one hop away). Use fresh git recency as a regression tiebreaker.
4. Apply the smallest fix that resolves *this* error — no refactors, no renames, no unrequested error handling, no fixing adjacent bugs.
5. Run the narrow verification that reproduces the original failure where practical, then emit the four-section contract. State an unavailable check honestly. Required repository checks still apply; summarize them within VERIFY.

Follow [triage-protocol.md](references/triage-protocol.md) for the full step-by-step, the evidence-label rules, and the verify-command-per-family table.

## Output contract (strict)

Return exactly these four sections, in this order, nothing before them:

```
DIAGNOSIS: <one sentence — what is failing and at what layer>
ROOT CAUSE: <file:line> — <Confirmed from code | Strongly inferred> — <cause and trigger; F x I = score with brief rating reasons>
SMALLEST FIX: <the edit you applied, in one or two lines; the diff is applied>
VERIFY: <exactly one command to confirm the fix>
```

Rules:

- **DIAGNOSIS** — one sentence, plain terms, no jargon dump.
- **ROOT CAUSE** — must carry a `file:line` (or a `file` plus a named one-hop file when strongly inferred) and an evidence label. No label = not shippable.
- **SMALLEST FIX** — describe the applied change, or state `review only` / `deferred below threshold` when applicable. For an authorized fix blocked by access, state the blocker and provide the exact patch.
- **VERIFY** — the narrow reproducer command and observed result, plus a concise result for required checks. Do not call `py_compile` proof that a runtime import or API request now works.
- After the four sections you may add at most one line flagging a separate latent bug you noticed. Do not fix it in this pass. Nothing else follows.

## Recurring families

`typescript-build` · `vite-rollup-build` · `react-runtime` · `vercel-deploy` · `python-fastapi-traceback` · `supabase`. Signatures, usual root causes, and smallest-fix patterns for each are in [error-families.md](references/error-families.md).

## Edge cases

- **No frame resolved to the repo** (top frame is in `node_modules/`, `site-packages/`, `dist/`, or another repo): still emit the four sections; ROOT CAUSE cites the signature + context labeled `Strongly inferred` and names the likely repo-side trigger; never invent a `file:line` you did not see.
- **No frame, no code, no signature at all**: ask exactly one targeted question ("which command produced this?" / "paste the full traceback"), then stop. Never open a multi-question interrogation.
- **Empty or non-error paste**: say there is no error to triage and ask what to run.

## Boundaries with other skills

- Deep serving/inference correctness review → **v-ml** (this skill fixes the immediate error only).
- Loading/empty/error-state UX gaps → **v-ui**.
- Secrets, RLS hardening, API abuse resistance → **v-security**.
- Commit message for the fix once verified → **v-git**.

See [references/triage-protocol.md](references/triage-protocol.md) for the full diagnostic protocol and evidence-labeling rules.
