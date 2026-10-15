# AUREX / OX integration admission gate

Status: **PROPOSED / NOT RUN**. No production changes authorized.

## Purpose
Prove a real, authorized, zero-paid-cost workflow through the API before claiming the website is integrated. The script in `scripts/aurex_api_e2e_gate.py` exercises authentication denial, health, capabilities, zero-dollar budget, creation of a bounded regression-scan job, job persistence and evidence endpoint shape. It does **not** prove that the evidence is independent, that inference works, or that a browser displayed the result.

## Staging run (owner/operator)
1. Deploy an approved, reviewed commit to a **staging** service with isolated persistent storage and a strong token. Never paste the token into a chat or commit it.
2. Configure environment variables in the operator's terminal or CI secrets:
   - `AUREX_E2E_BASE_URL=https://<staging-host>`
   - `AUREX_E2E_TOKEN=<staging-token>` (at least 32 characters)
3. Run `python scripts/aurex_api_e2e_gate.py` from the repo root.
4. Preserve exact commit SHA, staging deployment identifier, command exit code, timestamp and sanitized output. The script creates one real zero-budget job and an evidence record; it is **not** read-only.
5. Do not promote until independent negative-path checks pass: unauthorized/invalid token, malformed job kind, paid budget rejected, duplicate/idempotent request, cancellation and restart persistence.

## Frontend-to-backend gate (separate, required)
Use an **owner-authorized server-side proxy**, never a bearer token in the browser. From the published/staging AUREX / OX UI, submit a zero-budget `regression_scan`, then display the real job ID, server-reported state and evidence reference. Ensure unknown, absent, stale and failed states remain visibly unverified. Capture a redacted browser network trace and screenshot and independently reconcile the job ID with staging API storage. A static demo or transport-only health check is not sufficient.

## Promotion criteria
- One canonical OpenAPI contract, backend and frontend generated/validated against the same revision.
- Backend unit tests, Ruff, Mypy, security tests and staging API smoke gate pass at an exact SHA.
- Browser-to-staging workflow passes, no secrets in JS bundles/network responses, cross-origin and authorization negative tests pass.
- Independent reviewer confirms evidence provenance and no-self-witness; no unverified capability promoted to PASS.
- Owner explicitly approves any mainline merge and production deployment.

## Boundaries
No automatic deployment, paid provider invocation, native Qwen inference claim, or mainline merge. Do not run the API smoke gate against production by default. An API success is not proof of production readiness.
