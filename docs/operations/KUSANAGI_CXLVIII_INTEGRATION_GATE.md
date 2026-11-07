# KUSANAGI CXLVIII — Mainline integration evidence gate

Baseline main SHA: `f2db438f0020dbd455bcb5c7b21b7352d133bf2c` (PR #128 merge).
Status: **INVESTIGATION / PRODUCTION HOLD**. This document does not assert deployment or inference success.

## Verified from GitHub connector
- PR #128 merge commit is in recent repository history.
- A separate PR-triggered workflow lookup for that merge SHA returned no runs; this is **not** evidence that all CI failed or passed.
- Several open draft PRs exist, including #129 (OPA pilot, tests NOT RUN), #127 (optional integrations), #126 (private admin VPN), and #125 (DISPATER presentation). These are not automatically admitted to main.

## Observed from public AUREX/OX page on 2026-10-24
- Public HTTP 200.
- Railway connection: Unavailable.
- API checks: Unavailable.
- Timestamp: INVALID / FUTURE TIME.
- NVIDIA / XAELI: research not deployed; inference off; $0 default budget.
These are public-page observations, not authenticated backend telemetry.

## Verification sequence (do not skip)
1. Record exact `main` SHA, website deployment SHA, Railway deployment SHA and environment (never log secrets).
2. Reproduce server-side authenticated GET health/capabilities/evidence/budget/jobs checks against documented paths. Capture sanitized status, latency and response schema; no client-side bearer tokens.
3. Reconcile the future-time error using server clock, UTC parsing, maximum evidence age and PR #128 semantics. Do not accept future evidence to make status green.
4. Run the full existing backend and website suites at the exact candidate SHA. Preserve logs and report skipped/not-run tests.
5. Exercise NVIDIA adapter with mocked successful and failing responses. Live calls require explicit approval and a bounded nonzero budget; otherwise mark NOT RUN.
6. Verify that owner-only XAELI staging route fails closed for unauthenticated, stale, cross-tenant and over-budget requests.
7. Obtain independent reviewer evidence before merge. No production deployment or spend without operator authorization.

## Exit report
Use PASS / FAIL / NOT RUN / NOT VERIFIED per component; cite exact SHA, CI run URL, deployment ID, redacted probe evidence, reviewer identity, rollback path and unresolved blockers.

Canonical law: Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness.
