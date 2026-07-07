# Phase Contract Playbook

The full workflow for running one numbered phase-doc contract: verify prior
phases from code, implement the requested phase strictly from its doc, then
update the doc. This is a workflow-executor, not a review-only skill: the
pre-flight is read-only, but the implement step writes code once the pre-flight
is clean or the gaps are explicitly acknowledged.

## Step 0: Load project context

Read whatever exists, in this order, and skip missing files:

1. `CLAUDE.md`
2. `README.md`
3. `notes/00_overview.md`
4. `notes/03_architecture.md`
5. `notes/06_api_contracts.md`
6. `notes/11_known_issues.md`
7. The target phase doc the user named (`phase-NN.md`)

`notes/` and `CLAUDE.md` often record which phases really landed and what the
prior contracts promised. Trust code over prose, but use these to orient.

## Step 1: Gather deterministic phase evidence

Run the helper first so judgment rests on facts:

```
scripts/phase-status.sh <repo-path>
```

It emits, per phase doc:

- `--- status markers ---`: any `Status:` / `Implemented — <date>` / `done` lines
- `--- acceptance checkboxes ---`: every `- [ ]` / `- [x]` item plus a tally
- `--- referenced file paths (existence check) ---`: each promised path tagged
  `EXISTS`, `BASENAME` (found by filename elsewhere), or `MISSING`

Also run the formula-to-code harvester when the phase doc or a report contains
math (see [formula-trace.md](formula-trace.md)):

```
scripts/extract-equations.py <repo-path> --doc <phase-doc-or-report>
```

## Step 2: Build the pre-flight verification table

For every phase the user claims is complete (e.g. "phases 1-9 are done"), decide
whether the code backs the claim. Do not take the checkbox or status line at face
value — cross-check against the `EXISTS`/`MISSING` evidence and, where the doc
states a formula, against the formula-trace verdicts.

Output this exact table before writing any code:

```
## Pre-flight: prior phases

| phase | claimed status | evidence | verdict |
| --- | --- | --- | --- |
| phase-01 | done | src/lib/db.ts:1-40 present; 6/6 acceptance items checked | CONFIRMED |
| phase-07 | done | doc references src/api/score.ts but file MISSING | MISSING |
```

Rules for the table:

- One row per prior phase the user claims complete.
- `verdict` is `CONFIRMED` or `MISSING` only. Use `MISSING` if any promised
  module is absent, any acceptance item is factually unmet in code, or a stated
  formula is not implemented as written.
- Label each evidence cell `Confirmed from code` when it cites a real file:line,
  or `Strongly inferred` when you are reasoning from doc/notes prose without a
  code sighting. Never present inference as confirmation.
- After the table, print one line per `MISSING` phase describing the gap you are
  refusing to paper over. If everything is `CONFIRMED`, say so in one line.

## Step 3: Gap gate

- If prior phases are all `CONFIRMED`, proceed to Step 4.
- If any prior phase is `MISSING`, stop and surface it. Do not silently
  implement on top of a hole. Ask the user whether to (a) backfill the missing
  prior phase first, or (b) proceed anyway with the gap recorded. Only continue
  once they choose. Record the choice in the final summary.

## Step 4: Implement the requested phase — strictly from the doc

- Implement only what the target phase doc specifies. No scope creep beyond the
  contract, even if adjacent improvements are tempting.
- Treat each acceptance item as a concrete deliverable. Every unchecked box in
  the target phase is a thing you must make true.
- Where the doc states a formula, implement it exactly as written (correct
  `ddof`, correct population vs sample variance, correct sign and order). Use the
  formula-trace verdicts to avoid re-introducing a MISMATCH.
- Follow the repo's stack conventions (React 18 + Vite + TS strict + Tailwind +
  shadcn/ui, Supabase, FastAPI on Render; Python 3.11, Black line-length 100,
  isort, Google docstrings) and its existing patterns. Reuse before writing new.
- Add the tests the acceptance items imply. If the doc lists acceptance
  behaviors, each becomes a test case.

## Step 5: Update the phase doc

After the implementation lands and tests pass:

- Check off every acceptance item the implementation now satisfies: `- [ ]` ->
  `- [x]`. Leave genuinely unmet items unchecked and note why.
- Append a status stamp at the end of the doc using today's date:

  ```
  Status: Implemented — 2026-07-06
  ```

- Do not fabricate completion. An acceptance item stays unchecked unless the code
  and tests actually satisfy it.

## Step 6: Final one-line summary

Print a single closing line that states:

- which phase was implemented,
- which acceptance items are now checked,
- and any prior-phase gaps you refused to paper over (from Step 3), or "no prior
  gaps" if all were CONFIRMED.

## Edge cases

- **No phase docs found**: `phase-status.sh` prints `NONE`. Tell the user this
  skill expects `phase-NN.md` contract docs and ask where the contracts live.
  Do not invent a phase structure.
- **Only one phase doc, nothing prior**: skip the prior-phase table (state "no
  prior phases to verify") and go straight to implementing it from the doc.
- **Doc has no acceptance checkboxes**: treat the doc's prose requirements as the
  contract, list them explicitly as the deliverable set, and append the status
  stamp without a checkbox pass.
- **Target phase already stamped `Implemented`**: report that the doc claims
  completion, run the pre-flight to verify it against code, and ask the user
  whether they want a re-verification, a fix of any gap, or the next phase.

## Boundary with other skills

- For a full architecture/maintainability sweep, use `v-vibe`.
- For serving-side ML correctness, use `v-ml` or `v-ml-deploy`.
- For writing the commit after the phase lands, use `v-git`.
- For creating the `notes/` docs this skill reads, use `v-notes`.
  `v-phase` executes one phase contract; it does not audit the whole repo.
