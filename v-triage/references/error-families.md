# Recurring Error Families

The families Veer's stack actually produces (React 18 + Vite + TS strict + Tailwind/shadcn, Supabase, Vercel; FastAPI on Render; Python 3.11). Each entry: how to recognize it, the usual root cause at the top frame, and the smallest fix. Confirm against the code the locator printed — these are priors, not verdicts.

---

## 1. typescript-build

**Signature:** `error TS####`, `tsc` / `vue-tsc` in the output, `is not assignable to type`, `has no exported member`, `Cannot find name`, `Object is possibly 'null'`, `Property 'x' does not exist on type`.

**Where the fix lives:** the `.ts`/`.tsx` frame the compiler names, or the type declaration one hop away (`src/types/`, an interface, a shadcn/generated type).

**Common root causes → smallest fix:**

- `TS2339 Property 'x' does not exist` — the type is missing the field, or you are reading the wrong shape. Fix: add the field to the interface in `src/types/`, or read the correct property. Do not cast to `any`.
- `TS2345 / TS2322 not assignable` — shape mismatch at a call or assignment. Fix: correct the value or widen the specific field's type; never blanket-cast.
- `TS2307 Cannot find module` / `TS2305 has no exported member` — bad import path or wrong named export. Fix: correct the path (check `@/` alias in `tsconfig.json` `paths`) or the export name.
- `TS18048 / TS2531 possibly null/undefined` — strict-null on a value that can be absent. Fix: add the guard (`if (!x) return`), optional chaining, or a nullish default — at that line only.
- `TS7006 implicitly has 'any'` — missing param type. Fix: annotate that one param.

**VERIFY:** `npx tsc --noEmit` (or `npm run build` if the error surfaced during build).

---

## 2. vite-rollup-build

**Signature:** `[plugin:vite:import-analysis]`, `Failed to resolve import`, `Rollup failed to resolve import`, `does not provide an export named`, `Pre-transform error`, `[plugin:...]`, esbuild transform errors.

**Where the fix lives:** the importing file (the `from "..."` side), the alias config, or a missing dep.

**Common root causes → smallest fix:**

- `Failed to resolve import "@/..."` — wrong path or the `@` alias not wired. Fix: correct the path; confirm `resolve.alias` in `vite.config.ts` and `paths` in `tsconfig.json` agree.
- `Failed to resolve import "<pkg>"` — package not installed. Fix: `npm i <pkg>` (check it belongs in deps vs devDeps).
- `does not provide an export named 'X'` — default-vs-named import mismatch, or an ESM/CJS interop issue. Fix: switch between `import X` and `import { X }` to match the package's actual export.
- `Pre-transform error` / syntax in transform — a real syntax error in the named file. Fix: correct the syntax at the frame.

**VERIFY:** `npm run build`.

---

## 3. react-runtime

**Signature:** `Uncaught TypeError: Cannot read properties of undefined (reading 'x')`, `x is not a function`, `Rendered more/fewer hooks than during the previous render`, `Maximum update depth exceeded`, `Minified React error #185/#310/#31`, hydration mismatch, `Cannot update a component while rendering a different component`.

**Where the fix lives:** the component/hook frame; often a render-time access of async data before it loads, or a hooks-rule violation.

**Common root causes → smallest fix:**

- `Cannot read properties of undefined` — reading into data that is still loading or null. Fix: guard with a loading/empty state or optional chaining at that access. (This is a v-ux-adjacent smell but the crash fix belongs here.)
- `Rendered more/fewer hooks` — a hook behind a condition or early return. Fix: move the hook above the conditional; hooks run unconditionally, every render.
- `Maximum update depth exceeded` — `setState` during render or an effect with a bad/missing dependency array causing a loop. Fix: correct the `useEffect` deps, or move the setState out of render.
- `Minified React error #NNN` — decode the number at react.dev/errors, then treat as the underlying error above.
- `useX must be used within a Provider` — the component is outside its context provider. Fix: wrap it, or check provider ordering in `App.tsx`.

**VERIFY:** `npm run dev` then reproduce the exact interaction (name it in the VERIFY line).

---

## 4. vercel-deploy

**Signature:** `Error: Command "npm run build" exited with 1`, `Build Failed`, `FUNCTION_INVOCATION_FAILED`, `Serverless Function has exceeded the maximum`, `EXDEV` / `ENOENT` during build, `Module not found` only on Vercel, missing `VITE_*` / env var at build.

**Where the fix lives:** the build config, env vars, or a difference between local and Vercel (case-sensitive FS, missing env, node version).

**Common root causes → smallest fix:**

- Build fails only on Vercel — usually a case-sensitive import path (macOS is case-insensitive; Vercel Linux is not). Fix: correct the import's casing to match the file on disk.
- `VITE_X is undefined` at build — env var not set in the Vercel project. Fix: add it in Vercel env settings; confirm it is `VITE_`-prefixed to be exposed to the client bundle. Never bake a secret into a `VITE_` var.
- `FUNCTION_INVOCATION_FAILED` / timeout — a serverless function threw or ran too long. Fix: read the function log, handle the error, or move heavy work off the request path.
- Chunk >500 kB warning blocking a strict build — Fix: lazy-load the heavy route/dep (`React.lazy` + `import()`), or adjust `build.chunkSizeWarningLimit` only if the size is intentional.
- Wrong node version — Fix: pin via `.nvmrc` / `engines` in `package.json`.

**VERIFY:** `vercel build` locally, or `npm run build` when the failing step is the build command.

---

## 5. python-fastapi-traceback

**Signature:** `Traceback (most recent call last)`, `File "...", line N`, `ModuleNotFoundError`, `ImportError`, `TypeError`/`ValueError`/`KeyError`/`AttributeError`, `pydantic.ValidationError`, uvicorn/FastAPI in the trace, `joblib`/`sklearn`/`xgboost` on model load.

**Where the fix lives:** the deepest *repo* frame (the last `File "..."` before it enters `site-packages/`). Library frames are context, not the fix site.

**Common root causes → smallest fix:**

- `ModuleNotFoundError: No module named 'x'` — missing dep or wrong import. Fix: add to `requirements.txt` and install into the per-project venv; or correct the import path. Check you are in the right venv (`~/.venvs/...` or per-project).
- `ValueError: X has N features, but expects M` (sklearn/xgboost) — training/serving feature skew. Fix: align the DataFrame columns/order to the model's `feature_names_in_`. This is a correctness bug — for a full serving audit use v-ml, but the immediate fix is column alignment at the predict call.
- `pydantic.ValidationError` — request body doesn't match the model. Fix: correct the client payload or the Pydantic model field; do not loosen types to silence it unless the field is genuinely optional.
- `FileNotFoundError` on a model artifact — path is CWD-relative and the process started elsewhere. Fix: resolve the path from `__file__` / `pathlib`, not a bare relative string.
- `AttributeError` on a loaded model — version drift between the pickling and loading environments. Fix: pin `scikit-learn`/`xgboost`/`joblib`/`numpy`/`pandas` to the versions that created the artifact.
- `KeyError` / `TypeError` in request handling — missing/None field used unguarded. Fix: guard or default at that line.

**VERIFY:** re-run the failing call — `uvicorn backend.api:app --reload` then hit the route; or `python -m py_compile <file>` for an import/syntax error.

---

## 6. supabase

**Signature:** `PGRST###` (PostgREST), `new row violates row-level security policy`, `JWT expired` / `JWT malformed`, `duplicate key value violates unique constraint`, `violates foreign key constraint`, `permission denied for table`, `column "x" does not exist`.

**Where the fix lives:** the query/mutation call site in `src/`, an RLS policy in `supabase/migrations/`, or the auth/session handling.

**Common root causes → smallest fix:**

- `new row violates row-level security policy` — the RLS policy blocks this insert/update for the current role. Fix: correct the policy in `supabase/migrations/` (e.g. `auth.uid() = user_id`), or set the missing column (like `user_id`) the policy checks. Do not disable RLS to "fix" it.
- `PGRST116` (0 rows for `.single()`) — expected one row, got none. Fix: use `.maybeSingle()` and handle null, or correct the filter.
- `JWT expired` — stale session. Fix: refresh the session / re-auth; check the client is using the current session, not a cached token.
- `duplicate key` / `foreign key` violation — constraint hit. Fix: upsert instead of insert, or ensure the referenced row exists first; correct the client logic, not the constraint.
- `column "x" does not exist` — schema drift between code and DB. Fix: correct the column name, or add the migration. Regenerate typed client if types are stale.
- `permission denied for table` — RLS/grant missing for the role. Fix: add the policy/grant in a migration.

**VERIFY:** re-run the query/mutation; for RLS, run the query as the affected role or inspect the policy in `supabase/migrations/`.

---

## Cross-family notes

- **Trust the deepest repo frame, not the library frame.** The fix is almost never inside `node_modules/`, `site-packages/`, or `dist/`.
- **Fresh git recency = prime suspect.** If the marked line was last touched in the latest commit, it is the likely regression.
- **One error, one fix.** If you spot a second, unrelated bug while reading context, note it in one line after VERIFY — do not fix it in the same pass.
- **Boundaries:** deep serving-correctness review → v-ml; loading/empty/error UX gaps → v-ux; secrets/RLS hardening → v-security; commit message for the fix → v-git.
