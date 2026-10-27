---
name: v-vibe-ml
description: "Review-only post-vibe audit for AI, LLM, GenAI products, and autonomous agent workflows. Audits prompt injection and jailbreak defenses (raw f-string interpolation, delimiter hygiene, markdown exfiltration), agent loop circuit breakers (infinite while loops, iteration guards, execution sandboxes), tenant token and spend caps (denial-of-wallet defense, rate limits), model versioning and multi-provider fallback resilience, automated LLM eval harnesses, RAG multi-tenant vector isolation, response streaming (SSE), and structured output schema enforcement. Trigger on audit ml, audit ai, audit llm, v-vibe-ml, v-vibe-ai, prompt injection audit, agent safety audit."
---

# Post-Vibe AI, LLM & Agentic Product Audit

Use this skill when auditing an AI product, LLM-powered application, GenAI API, RAG system, or autonomous agent workflow. Stay in review mode unless the user explicitly requests implementation.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found in repository`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Exhaust the search.** For discovery, keep going until two consecutive passes surface nothing new; do not stop at the first plausible batch. Never silently cap coverage — state what you skipped and why.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_ml_vibe.py" --repo "<repo>"
   ```
2. Read the domain references before evaluating:
   - [references/llm-agentic-production-checklist.md](references/llm-agentic-production-checklist.md) for prompt injection and agent loop defense
   - [references/ai-security-spend-evals.md](references/ai-security-spend-evals.md) for spend caps, model fallback, and eval harnesses
   - [references/streaming-serving-resilience.md](references/streaming-serving-resilience.md) for streaming UX, structured output, and RAG isolation

## Workflow

### 1. Absorb Context & AI Architecture
- Inspect `pyproject.toml`, `package.json`, LLM provider clients (OpenAI, Anthropic, Gemini, LangChain, LlamaIndex), and agent prompt templates.
- Map the AI pipeline: User Input -> Prompt Assembly -> LLM Provider -> Output Parsing / Tool Invocation -> Execution / Response.

### 2. Audit Prompt Security & Injection Defenses
- **Raw String Interpolation**: Flag any raw string formatting (`f"System: {user_input}"`) that tangles instructions with untrusted user input.
- **Delimiter Hygiene**: Verify explicit structural separation (XML tags like `<user_query>` or structured role messages).
- **Indirect Prompt Injection**: Ensure documents retrieved from external sources (web search, email, uploaded PDFs) are marked untrusted and cannot trigger direct tool execution.
- **Unsafe Code Execution**: Flag any `eval()` or `exec()` executed directly on LLM output without an isolated microVM/sandbox.

### 3. Audit Agent Safeguards & Spend Defense
- **Loop Circuit Breakers**: Verify all agent tool loops have strict termination bounds (`max_iterations`, `max_turns`, timeout).
- **Per-Tenant Spend Caps**: Check for token tracking and budget limits that cut off runaway costs or denial-of-wallet attacks.
- **Human-in-the-Loop (HITL)**: Verify destructive operations (file deletion, financial charge, external email) require explicit human approval.

### 4. Audit Model Reliability, Versioning & Fallback
- **Pinned Snapshots**: Verify production uses explicit pinned model snapshots (e.g. `gpt-4o-2024-08-06`) instead of unpinned moving aliases.
- **Multi-Provider Fallback**: Check for failover logic if the primary LLM provider suffers an outage (5xx/429).
- **Automated Evals**: Verify presence of golden benchmark test suites to detect prompt regressions.

### 5. Audit RAG Multi-Tenancy & Serving UX
- **Tenant Isolation in Vector DB**: Verify all vector similarity searches include an explicit tenant/user metadata filter (`filter={"tenant_id": ...}`) to prevent cross-customer data leakage.
- **Response Streaming**: Ensure interactive endpoints stream tokens via SSE or WebSockets to minimize Time To First Token (TTFT).
- **Structured Output Enforcement**: Verify native JSON schema or Pydantic validation on structured LLM outputs.

## Output Contract

Produce the audit report in this exact structure:

```markdown
# AI, LLM & Agentic Product Production Audit: [Project Name]

**Scanned Path**: `<path>`
**AI Framework & Providers**: `OpenAI / Anthropic / Gemini / LangChain / LiteLLM`
**Vector Store**: `Pinecone / Qdrant / PGVector / Chroma / None`
**AI Production Readiness Verdict**: `READY TO SHIP` | `HIGH RISK (SPEND/INJECTION DEFECTS)` | `NO-SHIP (UNSANDBOXED/DATA LEAK)`

## 1. Executive Summary
- 3-5 sentence synthesis of AI safety posture, prompt injection vulnerability, cost defense, and serving resilience.

## 2. AI Security & Architecture Scorecard
| Pillar | Status | File Evidence | Notes |
|---|---|---|---|
| Prompt Separation / Delimiters | `ENFORCED / RAW F-STRINGS` | `path:line` | ... |
| Unsafe Eval / Exec on LLM Output| `CLEAN / DETECTED` | `path:line` | ... |
| Agent Loop Circuit Breaker | `BOUNDED / UNPROTECTED LOOP`| `path:line` | ... |
| Tenant Spend & Token Caps | `CONFIGURED / MISSING` | ... | ... |
| Pinned Model Snapshots | `PINNED / UNPINNED ALIASES` | ... | ... |
| Multi-Provider Fallback | `CONFIGURED / SINGLE VENDOR`| ... | ... |
| Automated Eval Test Suite | `PRESENT / MISSING` | ... | ... |
| RAG Tenant Metadata Filter | `ENFORCED / CROSS-TENANT RISK`| `path:line` | ... |
| Response Token Streaming (SSE) | `IMPLEMENTED / BLOCKING` | ... | ... |
| Structured Output Enforcement | `SCHEMA VALIDATED / NAIVE JSON`| ... | ... |

## 3. Findings by Severity (P0, P1, P2, P3)

### [P0/P1/P2/P3-CODE] Title
- **Severity**: P0 (Unsandboxed code execution / cross-tenant RAG leak / unlimited spend) | P1 (Prompt injection / unpinned model / no timeout) | P2 (Missing streaming / missing eval) | P3 (Minor prompt polish)
- **Status**: Verified | Unverified Concern
- **File**: `path/to/file:line`
- **What**: Exact code or prompt evidence.
- **Why it matters**: Attack scenario, financial loss, or silent output degradation.
- **Smallest fix**: Targeted, minimal refactor with code snippet.
- **Verification**: Test prompt or curl command to verify fix.

## 4. Prioritized Cleanup Backlog
- **Quick Wins (< 30 mins)**: Pinning model dates, adding XML delimiters to prompts, setting loop iteration guards.
- **Targeted Refactors (1-3 hours)**: Adding tenant filter to vector search, wrapping outputs in Pydantic/Instructor, adding multi-provider fallback.
- **Strategic Upgrades (Half-day to 2 days)**: Automated eval test harness in CI/CD, sandboxed tool runner, per-tenant Redis token budget tracker.

## 5. What's Already Good
- Highlight well-structured prompts, safe tool implementations, and sound AI patterns.
```
