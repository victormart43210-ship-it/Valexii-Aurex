# DISPATER.AI — SECURITY GATES & RELIABILITY CONTROLS
**Operation:** KUSANAGI CCXII
**Auditor:** Jules (Maximum Available Engineering Effort Verification)

---

## 1. Non-Delegable Authority Boundaries
1. **The System May Never Be Its Own Sole Witness**: AI model outputs and deterministic reconciliation results are evidence candidates. They possess `HUMAN_REVIEW_REQUIRED` status and can never execute financial writebacks, bank transfers, or accounting journal entries.
2. **Production Release Authority**: Permanently locked on `HOLD`.
3. **Financial Authority**: `NONE`.
4. **External Paid Inference**: `OFF`.

---

## 2. Threat Modeling & Defenses Verified

### Cross-Tenant Principal Authorization
- **Vulnerability Addressed:** Prevention of caller-supplied tenant ID spoofing.
- **Defense:** `authorize_tenant_principal` binds authenticated bearer token credentials to tenant-scoped permission domains.
- **Verification:** Verified via `test_scenario_h_cross_tenant_access_rejection` (HTTP 403 Forbidden).

### Durable SQLite Persistence & Anti-Tampering
- **Vulnerability Addressed:** Loss of audit state during pod/container restarts and unverified memory mutations.
- **Defense:** Atomic persistence to `dispater_audit_runs` in SQLite with deterministic SHA-256 receipts.
- **Verification:** Verified via `test_scenario_i_service_restart_durable_storage_recovery` and `test_scenario_j_tampered_receipt_detection`.

### CSV & Spreadsheet Formula Injection
- **Defense:** `sanitize_formula_field` checks record strings and prefixes leading `=`, `+`, `-`, `@`, `\t`, and `\r` with `'`.
- **Verification:** Verified via `test_scenario_l_malformed_or_hostile_input`.

### Input Bounds & Memory Denial of Service
- **Defense:** Max 2,000 records per category (`jobs`, `invoices`, `rates`, `payments`). Rejects oversized requests fail-closed.
- **Verification:** Verified via `_validate_rows` enforcing bound limits and strict key checks.
