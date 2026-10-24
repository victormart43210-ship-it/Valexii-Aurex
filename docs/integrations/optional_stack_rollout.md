# AUREX optional integration rollout (draft / not deployed)

Source checkouts reviewed locally by operator (not installed):
- OpenTelemetry Python: 9d7aad1848401427c24af045d30d74c1566770af
- Grafana Alloy: 3b2a3565546bd36592dc49ca28604ad187f0fb85
- Open Policy Agent: 83a65784cbc60c8bbf73d46fd4b4489c5b0e2d76
- Docling: 53c11a20a5dd6ac0d85fe88cc257ca3b4b3a72d4
- Hatchet: af128ec1672adaf8e3cc4afd339ce5c2c6f08c35

These are source snapshots, not verified dependency versions or approved supply-chain attestations.

## Phase A: safe pilot boundary
- Added a pure-Python fail-closed interpreter for an external OPA decision.
- This does NOT connect to OPA, install OPA, or authorize execution.
- It accepts only synthetic inputs, explicit operator approval and exact boolean allow.
- Its positive decision has authority NONE. Existing AUREX authority controls remain binding.

## Phase B: OpenTelemetry and Alloy (NOT IMPLEMENTED)
- Design tracing with opt-in dependency groups, trace ID propagation, and secret/PII redaction.
- Keep exporters disabled by default; verify collector destination and retention.
- No automatic instrumentation or external export until reviewed.

## Phase C: Docling (NOT IMPLEMENTED)
- Isolated resource-limited process, bounded synthetic documents, no network by default.
- Reject oversize/unsafe files; persist source hashes and parser version.

## Phase D: Hatchet — DEFERRED
- Do not install, deploy, or run Hatchet in AUREX.
- Adapt useful design patterns only: idempotency keys, bounded retries with backoff, concurrency caps, cancellation and durable receipts.
- Existing SQLite queue remains the sole job engine; any pattern implementation must undergo compatibility review and tests.
- Upstream references: https://docs.hatchet.run/v1/idempotency.md and https://docs.hatchet.run/v1/retry-policies.md.

## Acceptance gates
1. Unit tests pass locally and CI; no inferred PASS.
2. Independent security/license/dependency review.
3. Railway staging and production runtime DB isolation verified.
4. Full-volume backup/restore and restart persistence verified.
5. Synthetic website -> API -> worker -> evidence -> display receipt demonstrated.
6. Production unchanged pending explicit separate approval.

Status: DRAFT / TESTS NOT RUN / DEPLOYMENT HOLD.
