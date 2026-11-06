# Spend, provider failures, model configuration, and evals

Apply the entrypoint’s practical scoring and scope policy. Review the current product and provider contract; do not require extra vendors or infrastructure without a demonstrated need.

## Spend and retry boundaries

Trace maximum input/output, per-request cost, concurrency, tool turns, retries, cancellation, and the user/tenant charged. A provider budget alert is not automatically an enforced spending cap. Verify where limits are enforced and what happens on races or provider errors. Use existing storage/limits when adequate; do not prescribe Redis by default.

Retries must be bounded and distinguish retryable provider failures from refusals, invalid requests, or authentication errors. Verify cancellation stops billable work where supported. Fallback providers are optional and must preserve privacy, tool, and output contracts.

## Model configuration

Resolve the model actually used from code, environment, routers, and defaults. Preserve the user’s selected provider/model. The scanner classifies literal identifiers as dated, numbered, or undated; naming alone cannot prove immutability, availability, or a defect. Check current official model/version documentation and deprecation notices before recommending changes. Avoid frozen recipes of obsolete model IDs. For OpenAI, use the [official model catalog](https://developers.openai.com/api/docs/models).

## Validation and telemetry

Choose representative eval cases for actual failure costs and compare quality, schema validity, latency, and cost under the same setup. Keep test inputs and expected behavior stable enough to detect regressions; an arbitrary case quota is not a release criterion.

Record only needed telemetry under the product’s data policy. Redact credentials and sensitive payloads before storage, and verify who can access retained prompts. Do not add a third-party logger or retain full conversations automatically. Consult applicable [official safety guidance](https://developers.openai.com/api/docs/guides/safety-best-practices) for the deployed workflow.
