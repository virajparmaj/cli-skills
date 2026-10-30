# Global User Preferences & Skill Execution Rules

## CLI Skill Triggers (v-* Skills)
When the user enters or mentions a skill or folder name (e.g., `v-git`, `v-auth`, `v-security`, `v-frontend`, `v-triage`, `v-venv-doctor`, or any `v-*` skill listed below):
1. **Direct Execution**: Treat the name as an immediate command to execute that skill in the current project or workspace. Do not ask for confirmation or explain what the skill is. Start execution immediately.
2. **Load & Read Skill**: Access and follow the instructions in `~/.gemini/config/skills/<skill-name>/SKILL.md` (or `/Users/veerr_89/Work/cli-skills/<skill-name>/SKILL.md`).
3. **Execution Standards**: Execute any scripts in the skill's `scripts/` directory against the target repo/path, follow all operating standards, and output the result strictly according to the skill's output contract.

## Registered Skill Directory Names (44 Skills)
- `v-auth`: Authentication, authorization, session integrity, protected routes, and Supabase RLS audit.
- `v-backtest-audit`: Backtest & signal evaluation leakage, lookahead, and realism audit.
- `v-backtest-report`: Standardized, assumption-honest quantitative backtest report generation.
- `v-baselines`: Baseline model zoo (Dummy, Linear, RF, XGBoost) under shared CV protocol.
- `v-chrome-extension`: Chrome Web Store pre-release compliance and security audit.
- `v-dataset`: Pre-training dataset audit (missingness, imbalance, split overlap, leakage).
- `v-delovable`: Strip Lovable / GPT-Engineer artifacts, telemetry, and boilerplates.
- `v-duckdb-layer`: DuckDB/Parquet data layer schema drift, timezone, and key uniqueness audit.
- `v-frontend`: Vite + React + TS + Tailwind frontend performance, bundles, and query waterfall audit.
- `v-git`: Write short, low-effort conventional commit messages from git status/diff.
- `v-git-multi`: Cluster and split working tree into N logical commits with strict formatting.
- `v-macos`: Mac App Store pre-release readiness, sandbox, and privacy audit.
- `v-metric-math`: Verify custom financial/ML metric implementations against textbook definitions.
- `v-ml`: ML inference correctness, serving reliability, and operational safety audit.
- `v-ml-deploy`: Vite/React + FastAPI ML serving audit (feature parity, cold starts, contract drift).
- `v-notebook`: Notebook convention enforcement, cell structure standardization, and output cleanup.
- `v-notes`: Generate repo-specific `notes/` documentation suite (00-13).
- `v-notes-update`: Update existing `notes/` docs against current codebase state.
- `v-phase`: Execute next numbered phase-doc contract (`phase-NN.md`).
- `v-production`: Pre-launch production readiness and deployment safety audit.
- `v-provenance`: Dataset provenance tracking, content hashing, and source auditing.
- `v-readme-app`: Transform desktop/app README into user-first product documentation.
- `v-readme-web`: Transform web app README into user-first product documentation.
- `v-regression-diagnostics`: Statistical validity checks for regression and hypothesis models.
- `v-run-ledger`: Zero-infra experiment tracking appending runs to `experiments/runs.csv`.
- `v-scaffold`: Scaffold new web or python projects with Veer's stack conventions.
- `v-scripts`: Engineering audit for dead code, build latency, and performance bottlenecks.
- `v-security`: Security, secrets, input validation, and API-hardening audit.
- `v-shots`: Automated route screenshot capture for Vite/React web apps.
- `v-supa-migrate`: Generate next timestamped Supabase migration with RLS stubs.
- `v-test-functional`: End-to-end user workflow and functional testing.
- `v-test-handling-fallback`: Test error handling, timeouts, fallbacks, and recovery flows.
- `v-test-input-edge`: Input validation and edge-case testing (boundary, malformed, offline).
- `v-test-system-reliability`: System reliability, crash recovery, and consistency audit.
- `v-timeseries-leakage`: Temporal and statistical leakage audit for time series ML pipelines.
- `v-triage`: Error diagnosis and smallest fix for stack traces / build errors.
- `v-ux`: UX trust, loading/empty/error states, and user flow completeness audit.
- `v-venv-doctor`: Python virtual environment diagnosis on Apple Silicon.
- `v-vercel-doctor`: Diagnose local vs Vercel production deployment divergence.
- `v-vibe`: Post-vibe code maintainability, codebase slop, and design slop architecture debt audit.
- `v-vibe-app`: Post-vibe SaaS & backend audit (19 distributed systems pillars, 80+ enterprise readiness, codebase slop, pre-launch 20).
- `v-vibe-macos`: Post-vibe macOS desktop audit (App Sandbox, entitlements, PrivacyInfo.xcprivacy, atomic writes, WAL mode).
- `v-vibe-ml`: Post-vibe AI/LLM/agent audit (prompt injection, tenant spend caps, model fallback, evals, RAG isolation).
- `v-vibe-web`: Post-vibe website & marketing audit (GEO/AI search discovery, 20-point speedmaxxing, design slop, Core Web Vitals).
