# Typed-Client Sync

Veer's convention keeps a typed Supabase client in git, so any migration that
changes table shape must be followed by regenerating the generated types. This
file is how the skill decides the `types action` line and what command to hand
back.

## Where the types live

`scripts/next-migration.sh` reports the detected file. Common locations across
the web repos:

- `src/integrations/supabase/types.ts` — the Lovable/CLI default (upskin-survey, illini-drive-hub)
- `src/lib/supabase.ts` — hand-maintained typed client + `Database` type (back-pack)
- `src/types/supabase.ts` or `src/lib/database.types.ts` — occasional variants

If none is found, set `types action` to `no change` and note "no typed client
detected" — never invent a path.

## When to regenerate (the `types action` rule)

| Change in the migration                        | types action        |
|------------------------------------------------|---------------------|
| New table                                      | regenerate          |
| Add / drop / rename column                     | regenerate          |
| Change a column type or nullability            | regenerate          |
| New enum / composite type used by a column     | regenerate          |
| Index only                                     | no change           |
| RLS policy only                                | no change           |
| Trigger only (no column change)                | no change           |
| Comment-only                                   | no change           |

`regenerate` means the row/insert/update TypeScript shapes will drift from the
database until the file is rebuilt, so downstream `.from('table')` calls lose
type safety. `no change` means the generated types are unaffected.

## Regeneration commands

The project ref comes from `supabase/config.toml` (`project_id`), reported by the
script. Two equivalent forms depending on whether the CLI is linked:

Linked project (preferred):

```bash
supabase gen types typescript --linked > src/integrations/supabase/types.ts
```

By project ref (when not linked):

```bash
supabase gen types typescript --project-id <project_id> > src/integrations/supabase/types.ts
```

Local dev database (no remote round-trip):

```bash
supabase gen types typescript --local > src/integrations/supabase/types.ts
```

Substitute the real detected path as the redirect target. Do not run these as
part of the skill — the skill only writes the migration file and reports the
action. Regeneration is the user's next step (it needs network/CLI auth).

## Hand-maintained clients

Repos like back-pack keep the `Database` type by hand in `src/lib/supabase.ts`
rather than generating it. For those, `types action` is still `regenerate`, but
the note should say "hand-maintained — update the Database type in
src/lib/supabase.ts by hand" so it is clear no generator command applies.

## Why this matters

- Generated types are the contract between the SQL schema and every `.from()`
  query; a stale file gives false green in `tsc --strict`.
- Because migrations are tracked in git, the type file should be regenerated and
  committed in the same change as the migration so the two never diverge in
  history.
