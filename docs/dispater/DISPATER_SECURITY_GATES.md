# DISPATER.AI — SECURITY GATES & RELIABILITY CONTROLS
**Operation:** KUSANAGI CCX
**Auditor:** Jules (Independent Autonomous Verification)

---

## 1. Non-Delegable Authority Boundaries
1. **The System May Never Be Its Own Sole Witness**: AI model outputs and deterministic reconciliation results are evidence candidates. They possess `HUMAN_REVIEW_REQUIRED` status and can never execute financial writebacks, bank transfers, or accounting journal entries.
2. **Production Release Authority**: Permanently locked on `HOLD`.
3. **Financial Authority**: `NONE`.
4. **External Paid Inference**: `OFF`.

---

## 2. Threat Modeling & Defenses Verified

### Tenant Isolation
- **Defense:** Strict tenant comparison between requester and dataset.
- **Verification:** `test_tenant_isolation_boundary` verifies that submitting cross-tenant payloads raises `InvalidSnapshot`.

### CSV & Spreadsheet Formula Injection
- **Defense:** `sanitize_formula_field` checks record strings and prefixes leading `=`, `+`, `-`, `@`, `\t`, and `\r` with `'`.
- **Verification:** `test_formula_injection_defense` confirms all payload strings are sanitized prior to reconciliation.

### Replay & Evidence Tampering
- **Defense:** Deterministic SHA-256 digest computed for each individual record (`digest(rec)`) and the cumulative report receipt (`receipt_sha256`).
- **Verification:** Altering any field alters the receipt SHA-256 hash.

### Input Bounds & Memory Denial of Service
- **Defense:** Max 2,000 records per category (`jobs`, `invoices`, `rates`, `payments`). Rejects oversized requests fail-closed.
- **Verification:** `_validate_rows` enforces bound limits and strict key checks.
