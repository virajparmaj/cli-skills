# Scaffold Conventions

The exact convention set this skill enforces. The scaffolders (`scripts/scaffold-web.sh`,
`scripts/scaffold-py.sh`) are the source of truth; this file documents what they write and
why. Never pad a scaffold beyond this list — extra boilerplate is a defect here.

---

## Web track (Vite + React 18 + TS strict + Tailwind + shadcn/ui)

### Files written

| Path | Purpose |
|------|---------|
| `package.json` | React 18 + Vite deps only; `dev`/`build`/`preview`/`lint` scripts. `build` runs `tsc -b && vite build`. |
| `tsconfig.json` | `strict: true`, `noUnusedLocals`, `noUnusedParameters`, `@/*` -> `./src/*` alias. |
| `vite.config.ts` | React plugin + `@` alias mirroring tsconfig. |
| `tailwind.config.ts` | `darkMode: ["class"]`, content globs for `index.html` + `src/**/*.{ts,tsx}`. |
| `postcss.config.js` | tailwindcss + autoprefixer. |
| `components.json` | shadcn/ui config: `new-york` style, aliases for components/ui/lib/hooks/utils. |
| `index.html` | Root div + module script. |
| `src/main.tsx` | Mounts `<App />` wrapped in `<ErrorBoundary>` inside `React.StrictMode`. |
| `src/App.tsx` | Minimal shell using Tailwind + shadcn design tokens (`bg-background`, `text-foreground`). |
| `src/index.css` | Tailwind base/components/utilities directives. |
| `src/lib/utils.ts` | `cn()` helper (clsx + tailwind-merge) — required by every shadcn component. |
| `src/components/ErrorBoundary.tsx` | Class component with graceful fallback UI; logs error context. |
| `src/types/index.ts` | Home for shared types, imported as `@/types`. |
| `src/vite-env.d.ts` | Vite client types (typed `ImportMetaEnv` when `--supabase`). |
| `vercel.json` | SPA rewrite skeleton (all routes -> `/`). |
| `.gitignore` | node_modules, dist, env actuals; keeps `.env.example`. |
| `.env.example` | Committed. Actual env goes in `.env.local` (gitignored). |
| `README.md` | Getting-started + scripts. |

### With `--supabase`

| Path | Purpose |
|------|---------|
| `src/lib/supabase.ts` | Typed client from `lib/`; fails fast if env vars are missing. |
| `src/types/supabase.ts` | Placeholder `Database` type; regen with `supabase gen types typescript`. |
| `.env.example` | Adds `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`. |

### Rationale

- **shadcn/ui as default** — don't reinvent UI primitives. `cn()` and `components.json` are the
  prerequisites shadcn needs before `npx shadcn@latest add <component>` works.
- **Typed Supabase client from `lib/`** — matches the documented pattern; the throw-on-missing-env
  guard turns silent misconfiguration into a startup error.
- **types/ directory** — dedicated home for shared types, per the TS conventions.
- **ErrorBoundary at root** — graceful React error handling instead of a blank page.
- **.env.example committed, .env.local gitignored** — examples in git, actuals out.
- **vercel.json SPA rewrite** — client-side routing survives hard refreshes on Vercel. Deeper
  Vercel config is out of scope (that is v-vercel-doctor's job).
- **No install performed** — the script writes files and prints the exact `npm install` lines so the
  caller controls when packages are pulled. The dep versions in `package.json` are the intended pins.

---

## Python track (Python 3.11 ML/data)

### Files written

| Path | Purpose |
|------|---------|
| `pyproject.toml` | Metadata, `requires-python = ">=3.11,<3.12"`, pinned deps, `[tool.black]` line-length 100, `[tool.isort]` black profile, src-layout packages. |
| `requirements.txt` | Pinned runtime stack (mirror of pyproject deps for non-pyproject workflows). |
| `requirements-dev.txt` | `-r requirements.txt` + Black/isort/ipykernel. |
| `src/<pkg>/__init__.py` | Package marker + `__version__`. |
| `src/<pkg>/data.py` | `load_csv()` with Google-style docstring and explicit missing-file handling. |
| `tests/__init__.py`, `tests/test_data.py` | pytest suite covering `load_csv` happy + error path. |
| `notebooks/01_explore.ipynb` | Clean notebook: config -> data -> preprocessing -> modeling, each block ending with a `✅` success print. |
| `data/.gitkeep` | Keeps `data/` in git; contents gitignored. |
| `.gitignore` | venv, `__pycache__`, `.ipynb_checkpoints`, data contents, `.env`. |
| `README.md` | Setup + layout. |
| `.venv/` | Per-project venv created with Python 3.11 (unless `--no-venv` or 3.11 is absent). |

### Pinned ML stack (single source of truth)

```
numpy==2.1.2
pandas==2.2.3
scipy==1.14.1
scikit-learn==1.5.2
xgboost==2.1.0
statsmodels==0.14.4
matplotlib==3.9.2
seaborn==0.13.2
structlog
```

Dev tooling:

```
black==24.10.0
isort==5.13.2
ipykernel
```

### Rationale

- **Per-project venv on 3.11** — the documented standard is a venv per project, never the global
  interpreter. If Python 3.11 is missing, the script writes files and reports the exact fix rather
  than creating a wrong-version venv.
- **Black line-length 100 + isort (black profile)** — the documented formatting rules, encoded in
  `pyproject.toml` so `black .` and `isort .` need no flags.
- **Exact pins for the ML stack** — reproducibility; these versions are the documented set. `structlog`
  is intentionally unpinned to track the latest, matching the documented stack.
- **src/ layout** — importable package with stable logic; keeps notebooks thin.
- **Clean notebook order** — config cell, data cell, preprocessing, modeling, each ending with a
  `✅` success print. Stable logic graduates from the notebook into `src/`.
- **Google-style docstrings + type hints** — on reusable functions like `load_csv`.
- **Explicit missing-data handling** — `load_csv` raises on a missing file instead of failing later.
- **No pip install performed** — the script prints `pip install -e ".[dev]"` so the caller controls it.

---

## Commit conventions (both tracks)

Finish with an initial commit in Veer's format. Default type `chore` for a plain scaffold.

```bash
git init
git add .

git commit -m "chore : scaffold <name> project" \
  -m "- vite react ts tailwind shadcn setup
- error boundary + types dir
- env example + vercel skeleton"
```

Types: `chore` (default for scaffold), `feat`, `fix`, `docs`, `refactor`, `test`, `style`.
Summary is 4-5 words; body bullets start with `- ` and can be rough grammar.

---

## Hard limits

- Do not add routing libraries, state managers, testing frameworks (beyond the Python pytest stub),
  UI kits other than shadcn, or any dependency not listed above unless the user explicitly asks.
- Do not run `npm install`, `pip install`, or `git commit` unless the user asks you to run them —
  present them as ready-to-run blocks.
- Do not overwrite existing files without `--force`; report skipped files honestly.
