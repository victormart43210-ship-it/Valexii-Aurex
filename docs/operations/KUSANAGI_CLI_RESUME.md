# KUSANAGI CLI — Resume & Industrial Audit Protocol

## Overview
OPERATION KUSANAGI CLI establishes the VALEXII Industrial Audit Intelligence Platform across VALEXII.AI / AUREX-OX / DISPATER.AI.

## Current Repository Verification State
- **Branch:** `work/kusanagi-cli-jules-industrial-audit`
- **Canonical Main SHA:** `f2db438f0020dbd455bcb5c7b21b7352d133bf2c`
- **Pytest:** 449 passed, 1 skipped.
- **Ruff:** 0 errors (all checks passed!).
- **Mypy Strict:** 0 issues across 77 source files.
- **Website Bun Tests:** 165 passed, 0 failed across 24 test files.
- **Website Build:** Nitro server/client production build succeeded.

## Industrial Audit Deliverables
1. **Industrial Audit Platform (`aurex/industrial_audit.py`):** Tenant-scoped evidence models and deterministic audit-readiness evaluator supporting Sector A (Oilfield) and Sector B (Towing). Flags missing, expired, and duplicate records.
2. **XAELI Readiness Contract (`aurex/api.py`):** Endpoint `GET /v1/industrial-audit/readiness` returning tenant readiness evaluations structured into the 5 XAELI steps (`NOW`, `CHANGED`, `NEXT`, `WHY`, `PROOF`).
3. **Adversarial Security Test Suite (`tests/test_industrial_audit.py`):** 9 security and isolation tests verifying cross-tenant isolation, expired record detection, duplicate digest flagging, prompt injection safety, and unauthenticated fail-closed behavior.

## Nonnegotiable Governance
- Default Authorized Spending: $0.00.
- All model outputs carry `verification_status: "NOT_VERIFIED"` and `authority: "NONE"`.
- Production Release: `HOLD`.
