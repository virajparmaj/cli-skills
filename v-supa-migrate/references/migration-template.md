# Migration Template & RLS Patterns

Exact SQL blocks for drafting a Supabase migration in Veer's convention. Copy the block that matches the requested change, substitute real names from the inventory, and keep the `-- ROLLBACK` block at the bottom.

## Header comment

Start every migration with a one-line intent comment describing *why*, not just *what*:

```sql
-- Add saved_reports table: lets a user persist generated reports, owner-scoped.
```

## New table (full pattern)

Enable RLS, add owner-scoped policies, index the foreign key, and — only if the
table has `updated_at` — attach the shared trigger.

```sql
CREATE TABLE IF NOT EXISTS public.saved_reports (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  title text NOT NULL CHECK (char_length(title) BETWEEN 1 AND 200),
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_saved_reports_user ON public.saved_reports(user_id);

-- RLS
ALTER TABLE public.saved_reports ENABLE ROW LEVEL SECURITY;

-- Owners read their own rows
CREATE POLICY "saved_reports_select_own"
  ON public.saved_reports FOR SELECT
  USING (auth.uid() = user_id);

-- Owners create rows for themselves only
CREATE POLICY "saved_reports_insert"
  ON public.saved_reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Owners update their own rows
CREATE POLICY "saved_reports_update_own"
  ON public.saved_reports FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Owners delete their own rows
CREATE POLICY "saved_reports_delete_own"
  ON public.saved_reports FOR DELETE
  USING (auth.uid() = user_id);
```

### Public-read variant

When rows are meant to be world-readable (comments, public posts), replace the
select policy with:

```sql
CREATE POLICY "saved_reports_read"
  ON public.saved_reports FOR SELECT
  USING (true);
```

## updated_at trigger

Only include when the table has an `updated_at` column.

If `scripts/next-migration.sh` reports the function already exists, **omit** the
`CREATE OR REPLACE FUNCTION` block and add only the `CREATE TRIGGER`. On a first
migration (no history) include the function definition too:

```sql
-- Shared updated_at maintainer (include only if not already defined in history)
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER update_saved_reports_updated_at
  BEFORE UPDATE ON public.saved_reports
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
```

`SET search_path = public` on a `SECURITY DEFINER` function is not optional —
without it the function is flagged by Supabase's linter and is a privilege-
escalation risk. Always keep it.

## Add column(s) to an existing table

Default to nullable or provide a `DEFAULT` so the change is safe on populated
tables. Use `IF NOT EXISTS` for re-run safety.

```sql
ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS plan text NOT NULL DEFAULT 'free';
```

A bare `ADD COLUMN plan text NOT NULL` with no default on a populated table
fails — that is destructive; supply a default or split into add-then-backfill.

## Add index

```sql
CREATE INDEX IF NOT EXISTS idx_profiles_plan ON public.profiles(plan);

-- Unique / partial index (matches upskin-survey idempotency pattern)
CREATE UNIQUE INDEX IF NOT EXISTS idx_survey_responses_request_id
  ON public.survey_responses (request_id)
  WHERE request_id IS NOT NULL;
```

## Policy-only migration

When adding a policy to an existing table, reference the real table and follow
the `"<table>_<action>"` / `"<table>_<action>_own"` naming. `types action` for a
policy-only migration is `no change`.

```sql
CREATE POLICY "packs_update_own"
  ON public.packs FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

## Rollback block (always last)

Every migration ends with a commented reversal, most-recent-first, so the
reverse steps are documented even if never auto-run:

```sql
-- ROLLBACK
-- DROP TRIGGER IF EXISTS update_saved_reports_updated_at ON public.saved_reports;
-- DROP POLICY IF EXISTS "saved_reports_delete_own" ON public.saved_reports;
-- DROP POLICY IF EXISTS "saved_reports_update_own" ON public.saved_reports;
-- DROP POLICY IF EXISTS "saved_reports_insert" ON public.saved_reports;
-- DROP POLICY IF EXISTS "saved_reports_select_own" ON public.saved_reports;
-- DROP INDEX IF EXISTS public.idx_saved_reports_user;
-- DROP TABLE IF EXISTS public.saved_reports;
```

For an add-column migration:

```sql
-- ROLLBACK
-- ALTER TABLE public.profiles DROP COLUMN IF EXISTS plan;
```

## Convention checklist (verify before emitting)

- [ ] Filename matches the style + next value from the script.
- [ ] Every new table has `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.
- [ ] Every new table has at least one policy (or an explicit "intentionally locked" note).
- [ ] Owner writes use `auth.uid() = user_id` (or the real owner column).
- [ ] `IF NOT EXISTS` on create/add for re-run safety.
- [ ] Trigger function included only when needed and not already defined.
- [ ] `-- ROLLBACK` block present and reverses every statement above it.
- [ ] Destructive statements flagged in the summary.
