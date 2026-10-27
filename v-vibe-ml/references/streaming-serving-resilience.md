# Streaming UX, Structured Outputs & RAG Multi-Tenancy

Production serving guidelines for LLM applications.

---

## 1. Response Token Streaming (SSE / WebSockets)
- Users will abandon an app if they wait 10-15 seconds for an entire completion before seeing a single word.
- **Server-Sent Events (SSE)**: Stream tokens via standard `text/event-stream`.
- **Time To First Token (TTFT)**: Target TTFT under 800ms.
- **Connection Resilience**: Implement client-side reconnection logic; handle aborted streams gracefully without leaving orphaned LLM tasks running on the server.

## 2. Guaranteed Structured Outputs
- Never rely on prompting the LLM: *"Please output only valid JSON without markdown formatting."* In production, the model will inevitably wrap the JSON in backticks or add introductory commentary.
- **Methods**:
  - OpenAI / Gemini Native Structured Outputs (`response_format={"type": "json_schema", ...}`).
  - Tool/Function Calling (passing a JSON schema as a tool definition).
  - Pydantic validation with Instructor (`instructor.from_openai(...)`).
  - Automated retry loop with error feedback if JSON parsing fails on first attempt.

## 3. RAG Multi-Tenancy & Vector DB Isolation
- **The Cross-Tenant RAG Breach**: If tenant A uploads proprietary company secrets to your vector database and tenant B asks a relevant question, naive vector similarity search will retrieve tenant A's chunks and inject them into tenant B's prompt!
- **Mandatory Filter**:
  ```python
  # SECURE RAG QUERY:
  results = vector_db.query(
      vector=query_embedding,
      top_k=5,
      filter={"tenant_id": current_user.tenant_id}  # NEVER OMIT THIS FILTER
  )
  ```
- **Embedding Consistency**: Ensure the embedding model used for queries matches the exact model and dimensionality used when populating the index (e.g. `text-embedding-3-small` 1536d).

## 4. Cold-Start & GPU Inference Optimization
- For self-hosted or open-source models (vLLM, Ollama, Hugging Face TGI):
  - Use continuous batching and PagedAttention.
  - Implement speculative decoding for high-throughput endpoints.
  - Keep warm pool instances ready for high-priority user paths.
