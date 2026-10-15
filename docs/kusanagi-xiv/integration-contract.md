# Integration contract (AUREX website adapter)

This contract defines the minimal server-side adapter responsibilities for VALEXII.COM to interact with AUREX.

API surface (canonical AUREX server)

- GET  /health
- GET  /v1/capabilities
- GET  /v1/jobs
- POST /v1/jobs
- GET  /v1/jobs/{job_id}
- POST /v1/jobs/{job_id}/cancel
- GET  /v1/evidence
- GET  /v1/budgets

Adapter responsibilities (server-side; NEVER in-browser)

1. Authentication
   - Maintain service token(s) in server environment variables or secret store.
   - Set Authorization: Bearer <service-token> for requests to AUREX API.
2. User identity
   - Authenticate visitors using the website's session mechanism and map to user identities.
3. Validation
   - Validate incoming request sizes, schemas, and rate-limit per-user.
4. Rate limiting & quotas
   - Apply per-user and per-session rate limits.
5. Timeout & retries
   - Enforce short synchronous timeouts (e.g., 10s) and use background polling for long-running jobs.
6. Idempotency
   - Forward Idempotency-Key header for repeatable job submission where appropriate.
7. Sanitization
   - Sanitize any AUREX response before returning it to the browser; never include raw service tokens or private fields.
8. Correlation
   - Correlate website request_id <-> job_id <-> evidence_id across logs and returned payloads.

Typed client recommendation

- Generate a typed client from an OpenAPI specification when available.
- As a lightweight alternative, the repository includes `aurex/web_adapter.py` (server-side, minimal) to integrate quickly with Lovable.

