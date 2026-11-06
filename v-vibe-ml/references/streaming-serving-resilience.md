# Serving, structured output, and retrieval isolation

## Interactive responses

Assess time to first useful output, complete-response latency, cancellation, and retry behavior for the actual user flow. Streaming is optional when a short response suffices. If streaming exists, verify disconnect handling, partial-output state, bounded retries, and that reconnecting cannot repeat a side effect.

## Structured outputs

Use the deployed provider and installed SDK’s supported schema mechanism for machine-consumed output. APIs differ; do not copy one universal `response_format` shape into every provider/client. Validate the response before downstream actions and handle refusal, incomplete output, transport failure, and validation failure explicitly. Bound any repair/retry path. See [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Retrieval boundaries

Trace the authenticated identity into every retrieval, document lookup, cache, and citation download. Tenant separation may use distinct indexes/namespaces, RLS, or enforced filters; the presence of a `tenant_id` string does not prove isolation, and a missing metadata-filter pattern does not prove a leak. Test tenant A versus tenant B at the actual boundary when authorized.

Query embeddings must be compatible with the populated index’s model, dimensions, and preprocessing. Verify the configured index/version rather than assuming a fixed embedding model or dimension.

## Hosting efficiency

For self-hosted inference, measure cold starts, queueing, resource utilization, and cancellation before prescribing warm pools, batching, or speculative decoding. These have costs and depend on the installed serving stack and workload.
