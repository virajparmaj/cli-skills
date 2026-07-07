---
name: v-supa-migrate
description: "Draft the next timestamped Supabase migration file with matching RLS policy stubs, an optional updated_at trigger, a commented rollback section, and a typed-client sync flag, from a plain-English schema change. Use for React + Vite + Supabase repos that keep SQL migrations in supabase/migrations/ under git with a typed client in src/. Given a described change ('add a saved_reports table', 'add plan column to profiles'), it reads migration history via scripts/next-migration.sh to derive the current table inventory and next filename, then writes one migration and a strict summary. Trigger phrases: draft a supabase migration for, add a table migration, new migration file, schema change for supabase, generate migration with RLS. For serving-side or ML backends use v-ml; for RLS/auth security review use v-auth or v-security."
---

# Supabase Migration Draft

Generate one correctly named Supabase migration file — DDL + RLS stubs + optional trigger + rollback — plus a strict summary, from a plain-English schema change.

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

## Quick flow

1. Run `scripts/next-migration.sh <repo-path>` FIRST to gather deterministic facts:
   - the migrations directory and existing history
   - the naming style in use (UTC timestamp `20260228000000_` vs sequential `001_`)
   - the exact **next filename** to use
   - a rough current **table inventory** (from `CREATE TABLE` across history)
   - whether `public.update_updated_at_column()` already exists (reuse vs recreate)
   - the typed-client types file to keep in sync (e.g. `src/integrations/supabase/types.ts` or `src/lib/supabase.ts`)
2. Parse the requested change into one of: **new table**, **add column(s)**, **add index**, **alter/backfill**, or **new policy**. Match against the table inventory so you reference real tables and do not recreate existing ones.
3. Draft the migration body following [references/migration-template.md](references/migration-template.md). Reuse Veer's conventions exactly:
   - owner-scoped RLS: `auth.uid() = user_id` for insert/update/delete, public or owner select as appropriate
   - policy naming `"<table>_<action>"` and `"<table>_<action>_own"`
   - `updated_at` trigger via the shared `SECURITY DEFINER` + `SET search_path = public` function (only when the table has an `updated_at` column)
   - every migration ends with a `-- ROLLBACK` comment block documenting reversal
4. Write the file to the migrations directory using the exact filename from step 1. Write only this one file.
5. Decide the **types action** (regenerate / no change) and flag any **destructive** statement.
6. Emit the strict summary below.

## Output contract (strict)

After writing the migration file, output exactly two things and nothing else:

1. The full migration SQL in one fenced ```sql code block (the same content written to disk).
2. One fenced summary block in this exact shape:

```text
filename       : <migrations dir>/<exact filename>
tables touched : <comma-separated real table names>
RLS policies   : <count> added (<policy names, or "none — RLS unchanged">)
trigger        : <"updated_at trigger added" | "none">
types action   : <"regenerate — <types file path>" | "no change">
destructive    : <"⚠ <statement>" per line, or "none">
```

- `tables touched` must be real names verified against the inventory, never invented.
- Any `DROP`, `ALTER ... DROP`, `TRUNCATE`, `ALTER COLUMN ... NOT NULL` on an existing populated column, or type-narrowing change is **destructive** — list each with a one-line warning describing the data risk.
- `types action` is `regenerate` whenever a table or column changed shape; `no change` only for policy/index/comment-only migrations.
- Do not add prose, checklists, or next-step advice outside these two blocks.

## Idempotency and safety defaults

- Prefer `IF NOT EXISTS` on `CREATE TABLE`, `CREATE INDEX`, and `ADD COLUMN` so re-runs are safe.
- New columns on existing tables default to nullable (or supply a `DEFAULT`); never add a bare `NOT NULL` column to a populated table without a backfill + separate `SET NOT NULL` — flag it destructive if requested.
- Enable RLS on every new table. A new table with no policies is a silent lockout — always add at least a select policy or explicitly note "intentionally locked, no policies".

## No migrations directory / first migration

- If the script reports no `supabase/migrations/`, create the file at `supabase/migrations/` with a UTC-timestamp name and say so in the summary's `filename` line.
- If there is no history, this is the first migration: include the shared `update_updated_at_column()` function definition (not just the trigger) when an `updated_at` column is used.
- If no typed-client file is found, set `types action` to `no change` and note "no typed client detected" — do not invent a path.

## Boundary

This skill only drafts and writes the migration file. It does not run `supabase db push`, does not audit existing RLS correctness (use v-auth or v-security for that), and does not review serving/ML backends (use v-ml).

See [references/migration-template.md](references/migration-template.md) for the exact SQL block templates and RLS patterns, and [references/type-sync.md](references/type-sync.md) for the typed-client regeneration steps.
