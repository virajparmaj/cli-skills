# 19 Distributed Systems Pillars for Vibe Coders

Every vibe-coded app starts as a single monolithic script on a laptop. Before scaling to paying customers and distributed traffic, understand and implement these 19 architectural fundamentals.

---

### 1. Rate Limiting
- **Why**: Prevents brute-force attacks, credential stuffing, scraping, and runaway billing costs from malicious or malfunctioning clients.
- **Algorithms**: Token Bucket, Leaky Bucket, Sliding Window Counter.
- **Implementation**:
  - Edge/Proxy rate limiting (Cloudflare, Nginx `limit_req_zone`).
  - Application middleware (`@upstash/ratelimit`, `express-rate-limit`, `slowapi`).
  - Tiered rate limits: unauthenticated IPs (20 req/min), authenticated users (120 req/min), internal webhooks (unlimited or high threshold).

### 2. Caching
- **Why**: Reduces primary database read load, drops latency from 150ms to < 5ms.
- **Patterns**: Cache-Aside (Lazy loading), Write-Through, Write-Behind.
- **Stampede & Dog-Piling Prevention**: When a cached item with 10,000 req/sec expires, all 10,000 requests hit the database simultaneously. Use distributed mutexes or probabilistic early expiration (`XFetch`).
- **Invalidation Strategy**: Set strict TTLs; explicitly invalidate related cache keys on database write.

### 3. Load Balancing
- **Why**: Distributes incoming traffic across multiple healthy instances to prevent single-node saturation.
- **Layers**: Layer 4 (TCP/UDP, fast packet routing) vs Layer 7 (HTTP/HTTPS, path/header-based routing).
- **Health Checks**: Configure `/healthz` (liveness) and `/readyz` (readiness) endpoints that verify database connectivity before routing traffic.
- **Statelessness**: Ensure application servers store zero in-memory session state so requests can route to any worker.

### 4. Reverse Proxies
- **Why**: Shields internal services, terminates TLS/SSL, compresses payloads (Gzip/Brotli), and buffers slow client connections.
- **Technologies**: Nginx, Caddy, Traefik, AWS ALB.
- **Rules**: Always forward real client IP via `X-Forwarded-For` and protocol via `X-Forwarded-Proto`.

### 5. API Gateways
- **Why**: Centralized entry point managing cross-cutting concerns: authentication, protocol translation (REST to gRPC), route versioning, request transformation, and global analytics.
- **Technologies**: Kong, Envoy, KrakenD, AWS API Gateway.

### 6. CI/CD Pipelines
- **Why**: Guarantees that code is automatically linted, typechecked, and tested before merging; deploys reproducibly without human error.
- **Rules**: Branch protection on `main`, required PR approval, automated test suite must pass 100%, automated staging environment previews.

### 7. Docker
- **Why**: Solves "works on my machine" by packaging application, runtime, libraries, and OS configuration into immutable containers.
- **Security Best Practices**:
  - Multi-stage builds to keep final images small (< 100MB).
  - Never run as `root` (use `USER node` or `USER appuser`).
  - Use `.dockerignore` to exclude `.env`, `node_modules`, and `.git`.

### 8. Kubernetes / Container Orchestration
- **Why**: Automates container deployment, scaling, healing, and rolling updates across clusters.
- **Critical Configs**:
  - Explicit resource `requests` and `limits` (prevent OOMKilled domino cascades).
  - Liveness and readiness probes.
  - Horizontal Pod Autoscaler (HPA) based on CPU/memory/queue depth.

### 9. Service Discovery
- **Why**: Allows microservices and workers to locate dynamic ephemeral IP addresses of dependencies without hardcoded configs.
- **Implementations**: Kubernetes CoreDNS, AWS Cloud Map, HashiCorp Consul.

### 10. Circuit Breakers
- **Why**: Stops cascading failures when a downstream dependency (Stripe, OpenAI, email provider) suffers an outage.
- **States**:
  - `Closed`: Normal operation; calls pass through.
  - `Open`: Downstream failed repeatedly; calls fail immediately without waiting for timeouts.
  - `Half-Open`: Tests a small fraction of requests to see if the dependency recovered.
- **Libraries**: `opossum` (Node.js), `pybreaker` (Python), `resilience4j` (Java).

### 11. Timeouts
- **Why**: A service without explicit timeouts will hold connections open indefinitely during downstream outages, exhausting database/socket pools and crashing the entire server.
- **Rules**: Configure explicit connect (e.g. 2s) and read timeouts (e.g. 5-10s) on every HTTP client (`fetch`, `axios`, `requests`, `httpx`) and database query.

### 12. Retries
- **Why**: Overcomes transient network blips and momentary drops.
- **Rules**:
  - Only retry **idempotent** operations (GET, PUT, DELETE, or requests with an idempotency key).
  - Never retry HTTP 4xx client errors (400, 401, 403, 404, 422).
  - Cap maximum retry attempts (typically 3).

### 13. Exponential Backoff & Jitter
- **Why**: Retrying immediately or on a fixed 1-second interval causes the "thundering herd" problem, slamming a struggling service simultaneously.
- **Algorithm**: `delay = min(max_delay, base * (2 ^ attempt)) + random_jitter`. Jitter desynchronizes competing clients.

### 14. Idempotency
- **Why**: If a network drops after a customer submits payment, retrying must not charge their credit card twice.
- **Pattern**: Client sends a unique `Idempotency-Key` UUID in the request header. The server records the key in Redis/DB with an active lease. Subsequent requests with the same key return the cached original response without re-executing business logic.

### 15. Message Queues
- **Why**: Decouples fast HTTP request-response cycles from slow, asynchronous work (generating PDFs, sending emails, processing uploads, calling LLMs).
- **Technologies**: BullMQ (Redis-backed), Celery, Amazon SQS, RabbitMQ.
- **DLQ (Dead Letter Queue)**: Always route jobs that fail all retry attempts to a DLQ for inspection rather than silently dropping them.

### 16. Pub/Sub (Publish/Subscribe)
- **Why**: Enables one-to-many event distribution without the publisher knowing who or how many consumers exist.
- **Technologies**: Redis Pub/Sub, Kafka, Google Cloud Pub/Sub, AWS SNS.

### 17. Event-Driven Architecture & Transactional Outbox
- **Why**: Eliminates dual-write bugs where a database row is committed but publishing the message to Kafka/RabbitMQ fails (or vice versa).
- **Outbox Pattern**: Write the domain entity and an outbox event into the *same database transaction*. A background worker reads the outbox table and relays messages to the message broker safely.

### 18. Distributed Transactions
- **Why**: When a business process spans multiple independent databases or microservices, traditional ACID database transactions do not apply.
- **Guideline**: Avoid distributed two-phase locking (2PC) in high-throughput web systems due to lock contention and coordinator single-points-of-failure. Favor eventual consistency and compensation.

### 19. Saga Pattern
- **Why**: Manages long-lived transactions across distributed services.
- **Structure**: A sequence of local transactions. Each transaction updates data in a single service. If a step fails, the saga executes compensating transactions to undo the previous steps in reverse order (e.g., Refund Payment -> Restock Inventory -> Cancel Order).
