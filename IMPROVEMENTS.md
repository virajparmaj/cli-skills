# Skill improvements and installation

Reviewed and improved all 44 existing skills: 39 primary workflows and 5 nested UI specialists. Preserved the existing consolidation work and Git index; no commits or pushes were requested or performed.

A subsequent [deeper skill-by-skill review](reviews/2026-11-06-skills.md) covers additional helper fixes, current-source updates, benchmarks, and the expanded regression suite. The findings below describe the first pass.

## Instruction improvements

- Shortened discovery descriptions and clarified overlapping skill boundaries.
- Replaced repeated maximum-effort and exhaustive-search instructions with relevant evidence, scope, and stopping rules.
- Applied the user's frequency × impact scoring, threshold of 5, review-only boundaries, and deduplicated deferral policy where reviews and fixes occur.
- Resolved bundled scripts and references relative to each loaded skill, with explicit target repositories.
- Updated references to consolidated skills and corrected the security skill's invocation metadata.
- Preserved personal-project `main` and human Git identity rules; tightened intended-change staging, push-remote selection, and no-change behavior.
- Removed requirements to invent rejection probabilities or treat optional marketing, desktop, and enterprise checklists as universal defects.
- Kept UI implementation compatible with the project's stack, tokens, browser support, and existing files.

## Verified fixes

Confidence is confirmed from inspected instructions, code, configuration, or fixture behavior. Frequency estimates describe how often the concrete trigger arises in the relevant workflow; they are separate from confidence. All listed fixes meet the default threshold of 5.

| Concrete trigger and defect | Frequency and reason | Impact and reason | Score | Result |
| --- | --- | --- | --- | --- |
| Invoking retired skills through dangling Codex links after consolidation | 4: 11 dangling links were present in the active installation | 4: affected skills could not load | 4 × 4 = 16 | Installed canonical skills and removed only checkout-owned retired aliases |
| A failed declutter verification follows `git checkout -- .` | 2: rollback after a failed cleanup is uncommon | 9: could erase unrelated uncommitted work | 2 × 9 = 18 | Restore only task-owned changes |
| A Chrome audit requests a numeric rejection probability without supporting data | 10: required by the previous audit contract | 3: creates a misleading quantitative result | 10 × 3 = 30 | Report qualitative risk backed by evidence |
| A launch audit treats analytics, Product Hunt, and badges as mandatory | 8: normal launches encounter these checklist items | 3: creates false blockers and unwanted work | 8 × 3 = 24 | Treat these as optional, goal-dependent checks |
| `robots.txt` blocks `/` and lacks a sitemap directive | 3: reachable staging/default configuration | 4: a `FAIL` was downgraded to `WARN` | 3 × 4 = 12 | Preserve the blocking status |
| No inspectable HTML exists for title/description checks | 3: generated and server-rendered projects can have this layout | 4: scanner falsely reported verified metadata | 3 × 4 = 12 | Report unverified coverage instead of `PASS` |
| Baseline features contain missing values | 7: missing numeric values are common | 7: full-dataset median imputation contaminated cross-validation | 7 × 7 = 49 | Fit imputation inside each training fold |
| Baseline dates use non-lexicographic formats or an explicit missing date column | 4: ordinary CSV/date configuration variants | 7: could use incorrect chronological order or fall back to shuffled validation | 4 × 7 = 28 | Parse dates before sorting and reject invalid explicit configuration |
| Cross-validation fails or produces non-finite scores on small/imbalanced folds | 4: recurring model-evaluation inputs | 6: invalid scores could enter model comparisons | 4 × 6 = 24 | Exclude invalid model results and fail when no comparison remains |
| A returns series begins with a loss or loses all capital | 5: ordinary strategy-return patterns | 7: drawdown or total-loss CAGR understated risk | 5 × 7 = 35 | Include initial capital in drawdown; return −100% CAGR for total loss |
| Metric audits use the supplied Sharpe, Sortino, volatility, or log-loss fixtures | 8: these anchors are reused during normal metric audits | 7: incorrect anchors can reject correct implementations | 8 × 7 = 56 | Recomputed anchors and explicit conventions |
| An annualized headline Sharpe is compared directly to a threshold in standard-error units | 8: previous headline comparisons followed this path | 8: could produce a false backtest-validity verdict | 8 × 8 = 64 | Require sample length, convert units, and disclose heuristic limits |
| The dependency-free split checker reads two CSVs with the same header | 6: normal split files share a schema | 6: headers were counted as leaked observations | 6 × 6 = 36 | Hash data rows only and fail visibly on unreadable inputs |
| A split file cannot be loaded because of a file or dependency error | 3: recurring operational failure | 7: empty hashes could falsely suggest no overlap | 3 × 7 = 21 | Report the comparison as unverified and exit unsuccessfully |
| Project requirements use ranges/markers or different pins from a historical stack | 7: common dependency declarations | 5: valid environments received incorrect repair advice | 7 × 5 = 35 | Parse specifiers and markers; compare historical pins only on request |
| First migration discovery runs without a `src/` folder | 4: normal bootstrap layout | 4: helper aborted before drafting | 4 × 4 = 16 | Handle the absent source directory |
| Both a Supabase client initializer and generated types are present | 5: normal typed-client setup | 7: regeneration advice could overwrite initialization | 5 × 7 = 35 | Prefer generated types and protect hand-maintained clients |
| Playwright is installed in the target project rather than the linked skill | 7: typical local skill installation | 4: screenshot capture failed to resolve it | 7 × 4 = 28 | Resolve the dependency from the target project |
| A dynamic route has a valid sample path | 4: regular router configuration | 3: documented screenshot behavior silently skipped it | 4 × 3 = 12 | Capture the supplied sample route |
| A screenshot route returns HTTP 404 | 4: ordinary missing-route failure | 4: an error-page screenshot was reported as success | 4 × 4 = 16 | Reject HTTP error responses |
| Vercel environment listings indent environment names | 5: expected CLI formatting | 4: present keys were reported missing | 5 × 4 = 20 | Accept leading whitespace |
| A draft contract hardcodes `origin` despite a different verified push remote | 2: less common personal-repo configuration | 4: commands could fail or target the wrong remote | 2 × 4 = 8 | Use the verified configured push remote |
| The security skill's default prompt names a nonexistent skill | 5: selecting its suggested prompt is a normal entrypoint | 3: dispatch can misroute | 5 × 3 = 15 | Reference `$v-security` |

## Installation

Installed all 44 skills into each existing destination:

- `~/.codex/skills`
- `~/.claude/skills`
- `~/.gemini/skills`
- `~/.config/opencode/skills`
- `~/.gemini/config/skills`

Created 146 links, retained 74 correct links, and retired 26 checkout-owned aliases. A subsequent `--check` verified all 220 canonical links without further changes. Unrelated installations remain intact. The install action report, including original link targets, is at `/tmp/cli-skills-improvement/installed-links.json` for this session.

The reusable installer defaults to preview, supports exact destinations, and preflights all naming conflicts before mutation. Isolated independent tests verified two-destination installation, repeat runs, legacy cleanup, unrelated-folder preservation, and conflict handling. See [README.md](README.md) for commands.

## Validation and limits

- Official Skill Creator validation passed for all 44 entrypoints.
- All bundled Python, shell, and Node helpers passed syntax checks.
- All 26 installer and domain regression tests passed, covering the changed calculations, validation protocol, split overlap, and post-launch statuses. Baseline tests used the existing `/Users/veerr_89/.venvs/global/bin/python`; other regression suites used `python3`.
- Temporary fixtures exercised migration discovery, screenshot control flow, Vercel environment parsing, and audit inventories, including paths with spaces.
- An independent report run verified a two-observation returns CSV against arithmetic, including total return of −5.5% and drawdown of −10% from initial capital.
- Local reference targets resolve; screenshot paths in documentation are intentionally illustrative examples.
- `git diff --check` passed. The original staged patch is unchanged.

These checks do not establish automatic skill-selection quality for every prompt or certify projects audited later. Screenshot control flow was tested with a Playwright fixture; live Chromium rendering, production crawling, store acceptance, and signed releases were not exercised.

## Deferred issues

No verified issues below the default threshold were identified during this scoped pass. No remote issues were created.
