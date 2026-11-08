# Untangle change boundaries

Use this lens for requested codebase untangling or when the inventory reveals concrete coupling. The question is: **should these pieces change together?** Read the active entry points and their callers before proposing changes. Use existing dependency maps and Git co-change history when available; absent history is unavailable evidence, not proof of low usage. A compact import map or signature inventory can aid discovery, but inspect full implementations before editing.

## Find misplaced relationships

- **Hidden links:** the same policy or logic is repeated; code relies on a global, file, or call order established elsewhere; one feature requires synchronized edits across unrelated folders. Trace the concrete shared requirement and all consumers.
- **Needless links:** callers rely on internals, stable policy imports a volatile implementation, or a shared interface contains details understood by only one workflow. Check whether the dependency actually forces unrelated changes before introducing an abstraction.
- **Surplus:** a wrapper contributes no behavior or contract, an extension point has no current variation, or an unreachable branch remains. Check CLI entry points, dynamic discovery, compatibility exports, and tests before removing it.

Retries, sleeps, swallowed exceptions, disabled tests, and value-specific branches are inspection leads. Establish the requirement each serves. Keep rate limits, asynchronous readiness, provider differences, compatibility, provenance, and other demonstrated constraints explicit. Minimizing the number of special cases is not an acceptance criterion.

## Group evidence under a small fix

Record decisions before mutation, using the action table plus a short log when needed:

| Proposed fix | Evidence and current change trigger | Affected consumers/contracts | Validation | Decision |
| --- | --- | --- | --- | --- |
| Share one immutable research exclusion policy | Dataset labeling, training, and comparison repeat the same exclusion set; changing policy requires all three edits | Preserve existing exported names and serialized values | Existing exclusion and protocol tests | Apply if authorized |

Group several symptoms under one fix only when they share a verified cause. Prefer a local extraction or an explicit dependency over a system redesign. A shared policy belongs in a stable, dependency-light owner; preserve compatible exports when consumers already import them. Similar-looking code may implement different contracts and should remain separate.

Score verified bugs using the skill's frequency × impact policy. For structural improvements, explain the current maintenance friction and expected reduction in synchronized edits; do not label duplication alone a runtime bug. Review requests produce proposals. Cleanup requests permit scoped implementation. Low-score bug deferrals remain nonblocking.

Preserve comments explaining external constraints and existing tests. If comment or test cleanup is explicitly requested, assess it separately after the structural change: show why a comment adds no external context or a test cannot detect a regression before removing it; rewrite tests tied to internals around observable behavior when coverage remains useful.

## Verify and stop

Run the repository's applicable checks, trace affected callers again, and compare relevant contracts and data. Source-hash or protocol fingerprints may change after refactoring: preserve immutable historical records and describe any resulting recomputation or version boundary. A source map is discovery evidence, not runtime verification. Use one bounded independent review when useful and authorized; further passes require a concrete regression, failed check, or unresolved finding.

Stop when the requested simplification works, in-scope findings meeting the threshold are addressed, and required checks pass. Report unavailable checks and retained constraints. Do not expand to unrelated bugs or keep refactoring until every exception, duplicate, or abstraction disappears.

## Source and license

Adapted from [caldoai/skills: untangle-codebase](https://github.com/caldoai/skills/blob/main/skills/untangle-codebase/SKILL.md), retrieved November 6, 2026. The change-relationship lens and decision-log approach are incorporated into `v-declutter` with its existing authorization, evidence, and stopping rules. Original source [license](https://github.com/caldoai/skills/blob/main/LICENSE):

```text
MIT License

Copyright (c) 2026 Maze

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
