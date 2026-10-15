# Actual API contract

Inspected API routes: `/health`, `/v1/health`, `/v1/capabilities`, GET/POST `/v1/jobs`, GET `/v1/jobs/{job_id}`, POST `/v1/jobs/{job_id}/cancel`, `/v1/evidence`, `/v1/budgets`. Discovery names `/api/v1/*` and `/v1/challenge` are not this API's contract.

| Boundary | Baseline | Repair / remaining gap |
|---|---|---|
| Health auth | Public; cannot prove valid credentials | Bearer required on both aliases |
| Capabilities | `regression_scan` / `remote_inference` violate website hyphen-only schema | `regression-scan` / `remote-inference`; unavailable, no evidence links |
| Job creation | 200 succeeded without worker | 503 unavailable, zero job/evidence side effects |
| Params | Arbitrary nested dict | At most 16 scalar values, bounded names/strings; body <=16384 bytes |
| State | Arbitrary updates | queued→running/cancelled/failed; running→succeeded/failed/cancelled; terminal immutable |
| UI mapping | Website supports succeeded, not completed/expired | COMPLETED would map to succeeded; EXPIRED not implemented |
| Evidence | Unbounded list, untrusted historical records | No new fabricated records; historical remediation still required |
| OpenAPI | FastAPI generated schema differs from website draft | Full contract convergence NOT COMPLETE |

Website draft expects 201 on creation, structured `error` envelopes, required idempotency headers, max-200 lists and explicit bearer security. Backend does not yet meet those guarantees. No prompt/answer job kind, result response, job-scoped evidence endpoint, or principal ownership exists. Keep the owner-only model until a reviewed identity contract is implemented.

Read-only fixture probe fed actual backend TestClient responses into pinned website functions. Baseline capabilities returned `malformed`; repaired backend passes that schema. Old website checker stayed OFFLINE because it expected health.capabilities. The supplied website patch reuses canonical health and capabilities calls. HEALTHY here means API health only, never verified inference or security efficacy.
