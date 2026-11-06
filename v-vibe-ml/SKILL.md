---
name: v-vibe-ml
description: "Review LLM, GenAI, RAG, and agent products for prompt injection, unsafe tool execution, tenant isolation, runaway cost, and serving reliability. Use for an AI product or agent audit; use v-ml for conventional model-inference correctness."
---

# Post-Vibe AI, LLM & Agentic Product Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill when auditing an AI product, LLM-powered application, GenAI API, RAG system, or autonomous agent workflow. Stay in review mode unless the user explicitly requests implementation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_ml_vibe.py" --repo "<repo>"
   ```
2. Read only domain references relevant to this review:
   - [references/llm-agentic-production-checklist.md](references/llm-agentic-production-checklist.md) for prompt injection and agent loop defense
   - [references/ai-security-spend-evals.md](references/ai-security-spend-evals.md) for spend caps, model fallback, and eval harnesses
   - [references/streaming-serving-resilience.md](references/streaming-serving-resilience.md) for streaming UX, structured output, and RAG isolation

## Applicability

Map actual provider, tenant, tool, and trust boundaries first. Delimiters alone do not prevent injection; trace how untrusted text can cause an unauthorized action. Model aliases, single-provider operation, and non-streaming responses are design choices unless they violate a concrete contract or produce a verified failure. Preserve existing authorization for external actions.

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
- **Action Authorization**: Trace whether side-effecting tools enforce the user’s permitted scope and handle destructive or irreversible actions appropriately; a valid existing authorization need not be requested again.

### 4. Audit Model Reliability, Versioning & Fallback
- **Model Versioning**: Check whether the chosen alias or snapshot matches the product’s stability and upgrade policy; verify provider support before recommending a version.
- **Provider Failures**: Verify bounded retries, timeouts, and a clear failure response for 5xx/429. Assess additional providers only when required, including privacy, tool, and output-contract differences.
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
- **Severity**: P0/P1/P2/P3 based on the verified consequence and scope, not the presence or absence of a checklist item
- **Status**: Verified | Unverified Concern
- **Trigger and score**: frequency (1–10, reason) x impact (1–10, reason) = score; confidence stated separately
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
