# KUSANAGI XXVI — ONE MAINLINE / BRIDGE HARDENING

This package is an **additive staging and verification workflow**, not an automatic repository merger or production deployment. It does not claim that remote branches, Railway, or Lovable are fixed.

## Confirmed local baseline (reported by operator)
- 62 pytest cases plus 5 subtests passed; Ruff passed.
- 8 local HTTP tests passed: frontend assets, 401 for unauthenticated endpoints, 503 for missing database.
- 7 E2E assertions passed: three persisted jobs retrieved with no payload/result exposure and no execution.

## Important unresolved blockers
1. Canonical GitHub mainline reconciliation: website PR #21 and security PR #22, Copilot branch, Jules reviews, and integration branch must be compared by SHA. No blind merging.
2. Existing Railway gateway differs from local XXV read-only bridge; no live end-to-end verification or proven durable database path.
3. Browser-facing bearer-token entry is **not** a safe production authentication design. Lovable must use a server-side proxy with authenticated user session and scoped read authorization. Never put AUREX_READ_TOKEN in client JS, localStorage, HTML, or VITE_* variables.
4. No fake success, synthetic evidence, self-supplied signature trust anchors, or inferred PASS.
5. Production needs durable database, ownership/tenant isolation, token rotation, audit logs, rate limits, CORS/CSP, accessibility, error UX, observability, idempotency and concurrent mutation review.
6. Native Qwen/loopback adapter stays local; do not expose localhost or pretend Railway can reach Chromebook.

## Installation
Run `python3 install.py --repo ~/Valexii-Aurex` to preview; use `--apply` only after review. The installer copies **only new** files under `xxvi_verification/` and refuses any existing destination. No merges, pushes, deploys, DNS changes, or credential writes.

## Verification
Run `python3 xxvi_verification/verify.py` from repository root. It executes local tests and prints a JSON report. It does not start a server or modify production. `tests/test_xxvi_bridge.py` is an additive security regression suite; review any failing tests as legitimate defects rather than changing assertions to pass.

## Next stage
Follow `docs/MAINLINE_CONVERGENCE.md` and `lovable/FRONTEND_HANDOFF.md`. Require separate approval for merge and deployment; stage Lovable changes in the canonical website source, not a parallel production repository.
