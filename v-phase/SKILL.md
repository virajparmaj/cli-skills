---
name: v-phase
description: "Verify claimed prior phase completion, implement the requested phase-NN.md contract, validate its acceptance items and formulas, then update its status. Use for phase-driven implementation or phase verification."
---

# Phase Contract Executor

Run one numbered phase-doc contract end to end: verify prior phases from code,
implement the requested phase strictly from its doc, and update the doc.

The pre-flight (Steps 1-2) is strictly read-only. Do not edit any file during
pre-flight. Only after the gap gate (Step 3) passes or the user explicitly
accepts a gap do you write implementation code.

## Evidence and execution

Verify code and required acceptance checks, not just checked boxes or existing filenames. A formula scanner proposes candidates; trace its inputs, units, and implementation before declaring a mismatch.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## Quick flow

1. Load context: read `CLAUDE.md`, `README.md`, `notes/00_overview.md`,
   `notes/03_architecture.md`, `notes/11_known_issues.md`, and the target phase
   doc the user named. Skip missing files.
2. Run `scripts/phase-status.sh <repo-path>` to gather, per phase doc, its status
   markers, acceptance checkboxes, and the existence of every file path it
   promises. Judgment comes after these facts, not before.
3. If any doc or linked report contains math the phase must implement, run
   `scripts/extract-equations.py <repo-path> --doc <phase-doc-or-report>` and
   trace each formula to its code line per
   [references/formula-trace.md](references/formula-trace.md).
4. Build the strict pre-flight table (see Output contract) for every prior phase
   the user claims complete.
5. Gap gate: if all prior phases are `CONFIRMED`, proceed. If any is `MISSING`,
   stop and ask whether to backfill first or proceed with the gap recorded.
6. Implement the requested phase strictly from its doc — no scope beyond the
   contract. Every unchecked acceptance item is a deliverable; every stated
   formula must be implemented exactly. Add the tests the acceptance items imply.
7. Update the phase doc: flip satisfied `- [ ]` items to `- [x]`, then append
   `Status: Implemented — <today's date>`. Never fabricate completion.
8. Print the one-line final summary (see Output contract).

Follow [references/phase-contract-playbook.md](references/phase-contract-playbook.md)
for the full step-by-step workflow, gap gate, and edge cases.

## Output contract (strict)

Before writing any code, output the pre-flight table exactly in this shape:

```
## Pre-flight: prior phases

| phase | claimed status | evidence | verdict |
| --- | --- | --- | --- |
| phase-01 | done | src/lib/db.ts:1-40 present; 6/6 items checked | CONFIRMED |
| phase-07 | done | doc references src/api/score.ts but file MISSING | MISSING |
```

- One row per prior phase the user claims complete. `verdict` is `CONFIRMED` or
  `MISSING` only.
- Mark each evidence cell `Confirmed from code` when it cites a real `file:line`,
  or `Strongly inferred` when reasoning from doc/notes prose. Never present
  inference as confirmation.
- Below the table, print one line per `MISSING` phase naming the gap you refuse
  to paper over; if all `CONFIRMED`, say "no prior gaps" in one line.

After implementation and doc update, print exactly one closing line stating: the
phase implemented, which acceptance items are now checked, and any prior-phase
gaps recorded (or "no prior gaps").

## Implementation rules

- Implement only what the target phase doc specifies. No scope creep.
- Match the repo's stack (React 18 + Vite + TS strict + Tailwind + shadcn/ui,
  Supabase, FastAPI on Render; Python 3.11, Black line-length 100, isort, Google
  docstrings) and reuse existing patterns before writing new code.
- Resolve every formula MISMATCH/MISSING for the phase being built so the code
  matches the doc's math exactly.
- An acceptance box stays unchecked unless code and passing tests satisfy it.

## Edge cases

- **No phase docs found**: `phase-status.sh` prints `NONE`. Tell the user this
  skill expects `phase-NN.md` contract docs and ask where the contracts live. Do
  not invent a phase structure.
- **Only one phase doc, nothing prior**: state "no prior phases to verify", skip
  the table, and implement it straight from the doc.
- **Doc has no acceptance checkboxes**: treat its prose requirements as the
  contract, list them as the deliverable set, and append the status stamp without
  a checkbox pass.
- **Target phase already stamped `Implemented`**: run the pre-flight to verify it
  against code and ask whether the user wants re-verification, a gap fix, or the
  next phase.

## Boundary with other skills

- Full architecture/maintainability sweep: use `v-vibe`.
- Serving-side ML correctness: use `v-ml`.
- Commit message after the phase lands: use `v-git`.
- Creating the `notes/` docs this skill reads: use `v-notes`.
  `v-phase` executes one phase contract; it does not audit the whole repo.

See [references/phase-contract-playbook.md](references/phase-contract-playbook.md)
for the full workflow and [references/formula-trace.md](references/formula-trace.md)
for the formula-to-code traceability pre-flight.
