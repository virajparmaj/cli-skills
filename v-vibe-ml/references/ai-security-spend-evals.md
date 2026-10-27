# AI Security, Spend Defense & Automated Evals

Uncontrolled token spend, vendor lock-in, and silent regression are the three biggest failure modes of vibe-coded AI products.

---

## 1. Denial-of-Wallet & Tenant Spend Caps
- **The Threat**: A malicious user or runaway scraper floods an LLM endpoint with 100k-token prompts, running up thousands of dollars on your API bill in hours.
- **Defenses**:
  - **Per-Tenant Hard Spending Limits**: Track cumulative token cost per user/tenant in Redis. Cut off or throttle requests when monthly threshold is reached.
  - **Token Rate Limiting**: Limit tokens-per-minute (TPM) and requests-per-minute (RPM) per user.
  - **Input Truncation**: Enforce maximum input character/token lengths on user inputs before dispatching to the LLM.
  - **Cloud Budget Alerts**: Configure daily anomaly alerts and hard billing limits on OpenAI, Anthropic, and Google Cloud consoles.

## 2. Multi-Provider Fallback & Redundancy
- Major LLM providers suffer frequent outages (HTTP 500, 503, 429 rate limit saturation). A single-provider architecture results in an app-wide outage.
- **Fallback Architecture**:
  - Configure automatic failover using an abstraction layer (LiteLLM, Portkey, or custom router).
  - Primary: `claude-3-5-sonnet` -> Fallback: `gpt-4o` -> Emergency Fallback: `gemini-1.5-pro` or fast local model.
  - Wrap API calls in retry loops with exponential backoff and circuit breakers.

## 3. Pinned Model Snapshots vs Moving Aliases
- Moving aliases like `"gpt-4o"` or `"claude-3-sonnet"` are silently updated by providers. An unannounced prompt drift can break structured JSON outputs or alter classification accuracy.
- **Rule**: Pin explicit immutable model snapshot dates in production:
  - `gpt-4o-2024-08-06`
  - `claude-3-5-sonnet-20241022`
  - `gemini-1.5-pro-002`

## 4. Automated LLM Eval Harness
- Never deploy prompt changes or model upgrades based on "vibes" from 3 manual test inputs.
- **Eval Pipeline**:
  - Build a curated golden test dataset of 50-100 real-world inputs with expected outputs and edge cases.
  - Automate evaluations in CI/CD before merging prompt changes (using DeepEval, Ragas, Promptfoo, or custom evaluators).
  - Score against:
    - JSON schema validity (100% required)
    - Hallucination rate
    - Tone and safety compliance
    - Cost and latency delta

## 5. Telemetry & PII Sanitization
- Store prompt inputs and completions in an observability platform (Langfuse, Helicone, OpenLIT) for debugging.
- **Privacy Rule**: Strip user credentials, API keys, Social Security numbers, and credit cards before persisting prompts to database or third-party loggers.
