# Error Triage Protocol

You are diagnosing a pasted error and fixing it with the smallest viable edit. This is the protocol behind Veer's "paste an error, don't ask me to clarify" habit. Pin the response to a fixed, minimal contract. Diagnose first, fix minimally, hand back one verify command.

## The one hard rule

**If a stack trace, build error, or file:line frame is present, DO NOT ask clarifying questions.** Diagnose and fix. The trace already contains the information. Only ask a question when the pasted text has no frame, no error code, and no recognizable signature — and even then ask exactly one, then stop.

## Step 0: Run the locator

Pipe the pasted error into the locator against the repo the user is in:

```
pbpaste | scripts/locate-error.sh <repo-path>
# or, if you already have the text in a file:
scripts/locate-error.sh <repo-path> error.txt
```

It prints, in order:

- `likely error family` — a heuristic guess (confirm it from code, do not trust it blindly)
- `error codes / signatures` — TS codes, PGRST codes, Python exception classes, node errno, React minified error numbers, HTTP status
- `module / package tokens` — the unresolved imports / missing modules
- `raw file:line frames` — every frame found, in order
- `resolved repo frames` — frames mapped to real files in this repo (build/dep noise dropped)
- per top frame: `±15 lines of context` with the offending line marked `>>`, plus `git recency` (who last touched that line and when) and the file's last commit

The top resolved frame is almost always the root-cause site. Dependency frames (`node_modules/`, `site-packages/`, `dist/`) are shown as unresolved on purpose — they are rarely the fix site.

## Step 1: Confirm the family from code

Take the locator's family guess and confirm it against the printed context. Match it to one of the recurring families in [error-families.md](error-families.md):

- `typescript-build` — `tsc` / `vue-tsc` type errors (`error TS####`)
- `vite-rollup-build` — import resolution, plugin transform, bundling
- `react-runtime` — hooks, render, `Cannot read properties of undefined`, minified React errors
- `vercel-deploy` — build command failure, serverless function error, env mismatch
- `python-fastapi-traceback` — Python exceptions, uvicorn/FastAPI/pydantic, model loading
- `supabase` — PostgREST codes, RLS denials, JWT, constraint violations

Read that family's section for its signature, the usual root cause, and the smallest fix pattern.

## Step 2: Establish the root cause

Look at the marked line and its context. Decide:

- **Confirmed from code** — the context window at the top frame directly shows the defect (wrong type, missing import, null deref, wrong feature count, missing await). Cite `file:line`.
- **Strongly inferred** — the error signature plus the surrounding code make the cause near-certain, but the exact defect is one hop away (e.g. the type is defined in another file, the missing env var is read elsewhere). Cite the frame you have and name the one-hop file to check.

Use git recency as a tiebreaker: a line last touched in the most recent commit is a strong suspect for a freshly introduced regression.

## Step 3: Apply the smallest fix

Make the minimal edit that resolves *this* error. Do not:

- refactor surrounding code
- rename things for style
- add error handling the user did not ask for
- "improve" adjacent code you happened to read
- fix a second latent bug you noticed (mention it in one line after VERIFY instead, do not touch it)

If the fix genuinely requires touching more than one file (e.g. a type and its consumer), that is fine — but keep each edit minimal and say why the second edit is required.

## Step 4: Emit the strict output contract

Return exactly these four sections, in this order, and nothing before them:

```
DIAGNOSIS: <one sentence — what is failing, in plain terms>
ROOT CAUSE: <file:line> — <Confirmed from code | Strongly inferred> — <the actual cause in one line>
SMALLEST FIX: <the edit you applied, described in one or two lines; the diff has been applied>
VERIFY: <one command the user runs to confirm the fix>
```

Rules for the four sections:

- **DIAGNOSIS** is one sentence, no jargon dump. What broke, at what layer.
- **ROOT CAUSE** must carry a `file:line` (or `file` + named one-hop file if strongly inferred) and the evidence label. No label = not shippable.
- **SMALLEST FIX** describes the edit you *applied* — actually make the edit with the editor, do not just propose it. If you truly cannot edit (read-only mount, ambiguous target), say so and give the exact patch.
- **VERIFY** is exactly one command, chosen for the family (see below). Not a paragraph, not a checklist — one command.

After the four sections you may add at most one line flagging a separate latent issue you noticed. Nothing else.

## Verify command per family

| Family | VERIFY command |
| --- | --- |
| typescript-build | `npx tsc --noEmit` (or `npm run build` if the error came from build) |
| vite-rollup-build | `npm run build` |
| react-runtime | `npm run dev` then reproduce the interaction (state the interaction) |
| vercel-deploy | `vercel build` locally, or `npm run build` if the failing step was the build command |
| python-fastapi-traceback | re-run the failing call, e.g. `uvicorn backend.api:app --reload` then hit the route; or `python -m py_compile <file>` for a syntax/import error |
| supabase | re-run the query/mutation; for RLS, `select` as the affected role, or check the policy in `supabase/migrations/` |

Prefer the narrowest command that reproduces the original failure. A type error gets `tsc --noEmit`, not the full test suite.

## When nothing resolves

If the locator resolved zero repo frames (top frame is in a dependency, generated output, or a different repo):

- Still emit the four-section contract.
- ROOT CAUSE uses the error signature + the dependency/context as evidence, labeled `Strongly inferred`, and names the most likely repo-side trigger (a bad call site, a version mismatch, a missing env var).
- Do not invent a `file:line` you did not see.

## When there is genuinely no signal

Only if the pasted text has no frame, no code, and no known signature: ask exactly one targeted question (e.g. "which command produced this?" or "paste the full traceback, not just the last line"), then stop. Never open a multi-question interrogation.
