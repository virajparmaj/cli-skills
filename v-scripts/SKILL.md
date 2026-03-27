---
name: v-scripts
description: >
  Perform deep repo-level engineering audits for dead code, redundant code, duplicate logic, slow scripts, startup and build latency, wasted CPU or memory or disk or network work, oversized dependencies, oversized bundles, and maintainability issues in local repositories. Use when asked to audit a repo for performance, cost, dead code, bundle size, slow startup, slow builds, unnecessary abstractions, or engineering cleanup opportunities. Typical triggers: "audit this repo", "find dead code and bottlenecks", "what is slowing this down", "reduce bundle size", "find duplicate logic", "review scripts and build performance", or "make this codebase leaner and cheaper to run".
---

# Repo Efficiency Audit

Stay in audit mode unless the user explicitly asks for code changes.

## Workflow

1. Confirm the target repo. If the user says "this repo", use the current working directory.
2. Run [`scripts/surface-map.sh`](scripts/surface-map.sh) first to collect docs, manifests, entrypoints, scripts, build tooling, CI files, large files, and likely performance-sensitive patterns while skipping generated folders.
3. Read the highest-value context that exists before making claims:
   - `CLAUDE.md`
   - `README*`
   - dependency manifests and lockfiles
   - build config
   - CI or release config
   - startup or bootstrap entrypoints
   - architecture or notes docs
4. Use [`references/audit-playbook.md`](references/audit-playbook.md) as the audit contract for scope, evidence rules, confidence labels, output format, and prioritization.
5. Classify each claim as `measured`, `likely`, or `speculative`. If runtime behavior is unknown, say what evidence exists and what still needs measurement.
6. Prefer high-confidence, high-impact findings over generic best practices.

## Priorities

Focus first on:

- dead code, stale files, unused dependencies, and stale scripts
- duplicated logic, repeated parsing or transforms, and overlapping tooling
- slow startup paths, blocking synchronous work, repeated scans, and avoidable I/O
- build, test, release, and automation steps that can be cached, skipped, parallelized, or made incremental
- oversized packages, bundles, binaries, and assets with low payoff
- maintainability problems that directly increase runtime, size, cost, or fragility

## Output

Return the sections from [`references/audit-playbook.md`](references/audit-playbook.md):

1. Executive Summary
2. Findings
3. Dead Code Candidates
4. Redundancy Candidates
5. Performance Opportunities
6. Action Plan
7. Measurement Plan

Close with:

- Top 20 changes by impact-to-effort ratio
- Top 10 likely sources of wasted compute
- Top 10 likely sources of latency
- Top 10 safest cleanup or deletion candidates
