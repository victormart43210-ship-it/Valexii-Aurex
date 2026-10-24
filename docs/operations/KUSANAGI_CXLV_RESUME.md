# KUSANAGI CXLV — Resume & Continuation Protocol

## Overview
OPERATION KUSANAGI CXLV establishes Project Sovereign Intelligence across VALEXII.AI / DISPATER.AI / AUREX-OX.

## Current Repository Verification State
- **Branch:** `work/kusanagi-cxlv-sovereign-intelligence`
- **Canonical Main SHA:** `415dbab72fe00ad65be379979c0ee213059054b5`
- **Pytest:** 440 passed, 1 skipped.
- **Ruff:** 0 errors (all checks passed!).
- **Mypy Strict:** 0 issues across 76 source files.
- **Website Bun Tests:** 157 passed, 0 failed across 23 test files.
- **Website Build:** Nitro server/client production build succeeded.

## Sovereign Intelligence Deliverables
1. **OpenTelemetry Request Tracing (`aurex/telemetry.py` & `website/src/lib/telemetry.server.ts`):** W3C traceparent headers, correlation propagation, and secret redaction.
2. **IBM Docling Industrial Extraction (`aurex/docling_adapter.py` & `workstation/docling_lab.py`):** Structured field extraction for oilfield tickets, towing invoices, equipment logs, and DOT forms (100.0% benchmark accuracy on synthetic fixtures).
3. **Open Policy Agent Evaluator (`aurex/opa_policy.py`):** Feature-gated (`AUREX_ENABLE_OPA=0`) Rego policy evaluation enforcing AI model self-authorization prohibitions and $0 spend limits.

## Nonnegotiable Governance
- Default Authorized Spending: $0.00.
- All model outputs carry `verification_status: "NOT_VERIFIED"` and `authority: "NONE"`.
- Production Release: `HOLD`.
