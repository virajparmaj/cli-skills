# Global User Preferences & Skill Execution Rules

## CLI Skill Triggers (v-* Skills)
When the user invokes a skill to perform a task (for example, `v-auth` or "use v-git to commit and push"), load its instructions and begin the authorized work. Mentioning a skill while discussing, editing, or comparing skills does not invoke its workflow.

1. **Load the skill**: Read `~/.gemini/skills/<skill-name>/SKILL.md`, falling back to `~/.gemini/config/skills/<skill-name>/SKILL.md` or this checkout. Nested UI skills live under `v-ui/` in the checkout.
2. **Keep scope**: A review stays read-only unless fixes are requested. A draft Git message does not authorize a commit or push. Use the user's existing authorization without asking again.
3. **Run relevant helpers**: Resolve bundled paths relative to the loaded skill directory and pass the target project explicitly. Inspect helper arguments and side effects; do not run every script merely because it exists. Scanner output is a lead to verify against source, configuration, data, or runtime evidence.
4. **Finish the requested work**: Follow the skill's output contract, identify validation gaps, and stop once the requested behavior and required checks are satisfied.

## Practical review and implementation

For each verified bug, give the reachable trigger and evidence, frequency (1-10) in current usage, impact (1-10), brief reasons for both ratings, and `frequency x impact = score`. Keep confidence separate. The default fix threshold is 5: defer lower-scoring issues once in an existing local backlog or the report's **Deferred issues** list; create remote issues only with authorization. Scores of 5 or more permit only in-scope, authorized fixes. Checklist examples are inspection prompts. Re-review affected code after changes; expand only for new evidence or failed checks.

## Registered Skill Directory Names (39 primary skills)
- `v-auth`: Authentication, authorization, session integrity, protected routes, and Supabase RLS audit.
- `v-backtest-audit`: Backtest & signal evaluation leakage, lookahead, and realism audit.
- `v-backtest-report`: Standardized, assumption-honest quantitative backtest report generation.
- `v-baselines`: Baseline model zoo (Dummy, Linear, RF, XGBoost) under shared CV protocol.
- `v-chrome-extension`: Chrome Web Store pre-release compliance and security audit.
- `v-dataset`: Pre-training dataset audit (missingness, imbalance, split overlap, leakage).
- `v-declutter`: Audit and streamline local repository file architecture, directory hierarchy, naming redundancy, fragmented patch sprawl, Lovable/GPT-Engineer boilerplate, and dead code while strictly preserving functionality and test suites.
- `v-duckdb-layer`: DuckDB/Parquet data layer schema drift, timezone, and key uniqueness audit.
- `v-frontend`: Vite + React + TS + Tailwind frontend performance, bundles, and query waterfall audit.
- `v-git`: Write short, low-effort conventional commit messages from git status/diff.
- `v-git-multi`: Cluster and split working tree into N logical commits with strict formatting.
- `v-metric-math`: Verify custom financial/ML metric implementations against textbook definitions.
- `v-ml`: ML inference correctness, serving reliability, training-serving skew, and operational safety audit.
- `v-notebook`: Notebook convention enforcement, cell structure standardization, and output cleanup.
- `v-notes`: Generate repo-specific `notes/` documentation suite (00-13).
- `v-notes-update`: Update existing `notes/` docs against current codebase state.
- `v-perf`: Web application and site performance audit across the 20 vibe coder checks (LCP <= 2.5s, INP < 200ms, CLS < 0.1, hero image priority, bundle splitting, render hotspots, waterfalls, slow queries, caching).
- `v-phase`: Execute next numbered phase-doc contract (`phase-NN.md`).
- `v-post-launch`: Post-launch website checklist audit (noindex cleanup, GSC, GA4, robots.txt, www/non-www redirect, sitemap, meta titles/descriptions, Bing/IndexNow, Product Hunt, trust badge).
- `v-provenance`: Dataset provenance tracking, content hashing, and source auditing.
- `v-readme`: Transform app, desktop software, or web README into user-first product documentation with auto-detected app type.
- `v-regression-diagnostics`: Statistical validity checks for regression and hypothesis models.
- `v-run-ledger`: Zero-infra experiment tracking appending runs to `experiments/runs.csv`.
- `v-scaffold`: Scaffold new web or python projects with Veer's stack conventions.
- `v-scripts`: Engineering audit for dead code, build latency, and performance bottlenecks.
- `v-security`: Security, secrets, input validation, and API-hardening audit.
- `v-shots`: Automated route screenshot capture for Vite/React web apps.
- `v-supa-migrate`: Generate next timestamped Supabase migration with RLS stubs.
- `v-test`: Unified end-to-end testing suite (functional user flows, error handling & fallbacks, input edge cases, and pre-release system reliability).
- `v-timeseries-leakage`: Temporal and statistical leakage audit for time series ML pipelines.
- `v-triage`: Error diagnosis and smallest fix for stack traces / build errors.
- `v-ui`: Build, restyle, or review web UI, pages, dashboards, forms, navigation, responsive layouts, and product demo illustrations (Good CSS, Component Gallery, EasyUI, BoardUI, Stageshow).
- `v-venv-doctor`: Python virtual environment diagnosis on Apple Silicon.
- `v-vercel-doctor`: Diagnose local vs Vercel production deployment divergence.
- `v-vibe`: Post-vibe code maintainability, codebase slop, and design slop architecture debt audit.
- `v-vibe-app`: Post-vibe SaaS & backend audit (19 distributed systems pillars, 80+ enterprise readiness, codebase slop, pre-launch 20).
- `v-vibe-macos`: Post-vibe macOS desktop audit (App Sandbox, entitlements, PrivacyInfo.xcprivacy, atomic writes, WAL mode, App Store readiness).
- `v-vibe-ml`: Post-vibe AI/LLM/agent audit (prompt injection, tenant spend caps, model fallback, evals, RAG isolation).
- `v-vibe-web`: Post-vibe website & marketing audit (Google 20-point technical SEO & ranking checklist, GEO/AI search discovery, 20-point speedmaxxing, design slop, UX trust, Core Web Vitals).

## UI specialists (5 skills, 44 total)

- `boardui`: Work within an existing or explicitly selected BoardUI design system.
- `component-gallery`: Find suitable interface patterns and adapt them to the project.
- `easyui-components`: Adapt suitable EasyUI React components to the project's stack.
- `good-css`: Apply modern CSS techniques while checking target-browser support.
- `stageshow`: Create product UI illustrations and animated demo compositions.

## Install or refresh

Run `python3 scripts/install-skills.py` from this checkout to preview changes, then add `--apply` to install. The installer links all 44 skills into Codex and existing Claude, Gemini, and OpenCode skill folders. It preserves unrelated skills and real directories, and removes retired aliases only when their links belong to this checkout. Run with `--check` to verify the installation. Use `--target <skills-directory>` to select an exact destination.
