# DISPATER OPERATION KUSANAGI CCXIV — CONTRACT FREEZE

**Date:** November 2026
**Operation:** KUSANAGI CCXIV (214) — Sovereign Beta Final Convergence
**Status:** FROZEN

---

## 1. Frozen System Boundaries

1. **Authority Chain:** Evidence → Qualification → Reality → Authority → Effect.
2. **Sole Witness Rule:** The system may never be its own sole witness. Model consensus, heuristic findings, and automated reconciliation are advisory only (`HUMAN_REVIEW_REQUIRED`).
3. **Release & Financial Constraints:**
   - Production Release Authority: `HOLD`
   - Financial Authority: `NONE`
   - External Paid Inference: `OFF`
   - Live Customer Data: `PROHIBITED`
   - Confirmed Recovery: permanently `$0.00` until verified human cash settlement.

---

## 2. API & Storage Schema Contracts

### A. Tenant Authorization
- Authentication: Bearer token whose SHA-256 hash maps to a tenant in `AUREX_DISPATER_TENANT_GRANTS`.
- Unconfigured grants => HTTP 503 Service Unavailable (fail-closed).
- Tenant ID manipulation across boundaries => HTTP 403 Forbidden.

### B. Persistent SQLite Storage
- Default location: persistent mount `/data/aurex_dispater.db` with fail-safe fallback to `AUREX_DISPATER_DB`.
- Tables: `dispater_runs`, `dispater_findings`.
- Journal mode: `WAL` with `busy_timeout = 30000`.
- Cryptographic integrity: Re-verified via `verify_receipt` upon retrieval.

### C. Financial Exposure Categories
- `potential_underbilling_usd`: Unbilled tickets or invoices below agreed rate.
- `potential_overbilling_usd`: Billed rates exceeding contract or duplicate billing.
- `unverified_exposure_usd`: Ambiguous or missing master rates and orphan billing entries.
- `human_confirmed_discrepancy_usd`: Discrepancy confirmed by an authorized human auditor.
- `confirmed_recovery_usd`: Realized financial recovery ($0.00 default).

### D. Finding Format
- Canonical 5-Step XAELI sequence: **NOW → CHANGED → NEXT → WHY → PROOF**.
