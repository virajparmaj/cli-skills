# Audit Playbook

## Audit Posture

- Audit first. Do not make code changes unless the user explicitly asks.
- Tie every finding to concrete files, code paths, scripts, manifests, tests, or project structure.
- Prefer high-confidence findings over generic advice.
- Use the default exclusions unless a generated artifact is itself evidence:
  - `node_modules`
  - `dist`
  - `build`
  - `out`
  - `.next`
  - `.nuxt`
  - `.git`
  - `.venv`
  - `venv`
  - `coverage`
  - `__pycache__`
  - temp, export, cache, and other derived output folders

## Evidence Model

Label each finding with both:

- `Measured`: backed by timings, sizes, counts, benchmarks, or tool output you actually observed
- `Likely`: strongly supported by static code or config evidence, but not benchmarked in this audit
- `Speculative`: plausible opportunity that still needs measurement or runtime confirmation

Also assign:

- `Severity`: `critical`, `high`, `medium`, or `low`
- `Confidence`: `high`, `medium`, or `low`

If something is uncertain, say exactly what is known, what is inferred, and what should be measured next.

## Phase 1: Load Context

Read the project context that best explains architecture, workflows, and constraints. Prioritize what exists:

- `CLAUDE.md`
- `README*`
- architecture or notes docs
- dependency manifests and lockfiles
- package or tool scripts
- build config
- CI or CD config
- release or deploy scripts
- startup or bootstrap entrypoints
- tests around risky or expensive paths

Use `scripts/surface-map.sh` first so the audit starts from the real repo layout instead of assumptions.

## Phase 2: Inspect by Dimension

### Dead Code

Look for:

- unused files, modules, helpers, classes, constants, feature flags, assets, and scripts
- unreachable branches or legacy code paths
- commented-out code that should likely be deleted
- stale tests for removed behavior
- dependencies that appear unused or replaceable

### Redundancy

Look for:

- duplicate logic across files or layers
- parallel utilities that solve the same problem
- repeated transforms, parsing, validation, or formatting
- overlapping scripts that should be merged or standardized

### Code Efficiency

Look for:

- repeated scans, repeated parsing, repeated serialization, or unnecessary allocations
- expensive work redone instead of cached
- excessive file I/O or network calls
- poor batching, sequencing, or concurrency
- synchronous work on hot paths that could be deferred or lazy-loaded

### Latency and Responsiveness

Look for:

- slow startup or initialization paths
- expensive synchronous work on request, render, CLI, or bootstrap paths
- main-thread or UI-thread blocking work
- repeated work during load, render, bootstrap, or command execution
- avoidable round-trips, retries, or sequential waits

### Compute and Resource Usage

Look for:

- unnecessary CPU work
- memory retention or oversized in-memory objects
- avoidable disk churn or repeated writes and copies
- excessive logging, retries, polling, or watchers
- wasteful background jobs or repeated rebuilds

### Script and Build Performance

Look for:

- slow scripts with redundant steps
- repeated installs, copies, transpilation, or code generation
- tooling that prevents incremental or cached execution
- inefficient shell usage
- local feedback loops that are slower than they need to be

### Size Reduction

Look for:

- heavy dependencies with low value
- oversized bundles, binaries, packages, or assets
- missed tree shaking, code splitting, lazy loading, compression, or tighter packaging
- duplicated assets or duplicate libraries serving the same purpose

### Maintainability and Simplicity

Look for:

- unnecessary abstractions
- patterns that hurt readability and also cost runtime or bundle size
- inconsistent implementations of the same workflow
- places where a smaller direct implementation would lower long-term cost

### Reliability and Safety

Look for:

- performance ideas that are risky without benchmarks
- fragile scripts that hide failures
- missing tests around critical or expensive paths
- refactors or cleanup work likely to regress behavior if done blindly

### Strategic Improvements

Separate:

- quick wins with high impact and low risk
- medium-effort improvements with clear payoff
- high-effort refactors worth considering later
- standardization opportunities that reduce future cost

## Output Contract

### 1. Executive Summary

Include:

- the biggest engineering waste patterns in the repo
- the top highest-impact improvement opportunities
- the best quick wins
- the biggest likely causes of latency
- the biggest likely causes of unnecessary compute or size

### 2. Findings

For each finding include:

- `ID`
- `Severity`
- `Confidence`
- `Evidence type`: `Measured`, `Likely`, or `Speculative`
- `Category`
- `File path(s)`
- `Short title`
- `Why this matters`
- `Evidence`
- `Recommended fix`
- `Expected payoff`
- `Estimated effort`
- `Change risk`

Rank findings by impact-to-effort when possible. Avoid repeating the same advice in multiple findings.

### 3. Dead Code Candidates

List likely safe deletions separately:

- file or path
- why it appears unused
- confidence
- how to validate before deletion

### 4. Redundancy Candidates

List likely duplicate or overlapping logic:

- file or path
- duplication pattern
- consolidation suggestion
- expected benefit

### 5. Performance Opportunities

Cover:

- runtime hotspots
- startup bottlenecks
- script and build bottlenecks
- compute waste
- size reduction opportunities
- low-latency opportunities

### 6. Action Plan

Split into:

- do now
- validate with benchmark first
- refactor later
- nice-to-have
- risky and should be deferred

### 7. Measurement Plan

Recommend what should be benchmarked next:

- startup time
- script runtime
- build time
- memory usage
- bundle or package size
- disk I/O
- network round-trips
- responsiveness or throughput

Call out what must be measured before making risky optimizations.

## Required Closing Lists

End the audit with:

- Top 20 changes by impact-to-effort ratio
- Top 10 likely sources of wasted compute
- Top 10 likely sources of latency
- Top 10 safest cleanup or deletion candidates

## Constraints

- Be specific, practical, and critical but fair.
- Do not pad with generic best practices.
- Distinguish measured issues, likely issues, and speculative opportunities.
- If the repository type changes the priorities, adapt automatically.
- If a claim depends on runtime data you do not have, treat it as a hypothesis and say how to validate it.
