# DISPATER.AI — SECURITY GATES & RELIABILITY CONTROLS
**Operation:** KUSANAGI CCXV
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
- **Defense:** `authenticate_principal` binds bearer token SHA-256 digests to permitted tenant IDs in `AUREX_DISPATER_TENANT_GRANTS`. `authorize_tenant` enforces uniform HTTP 403 Forbidden on mismatch without leaking tenant existence.
- **Verification:** Verified via `tests/test_dispater_security.py` (30 tests passing).

### Durable SQLite Persistence & Anti-Tampering
- **Vulnerability Addressed:** Loss of audit state during pod/container restarts and unverified memory mutations.
- **Defense:** Atomic persistence to `dispater_runs` and `dispater_findings` in SQLite with WAL checkpointing, mount validation, and cryptographic receipt check (`verify_receipt`).
- **Verification:** Verified across simulated service restarts and receipt tampering in `tests/test_dispater_security.py`.

### CSV & Spreadsheet Formula Injection
- **Defense:** `sanitize_formula_field` checks record strings and prefixes leading `=`, `+`, `-`, `@`, `\t`, and `\r` with `'`.
- **Verification:** Verified via `tests/test_dispater_reconciliation.py`.

### Request Stream Bounds & Memory Denial of Service
- **Defense:** Asynchronous raw request body stream inspection enforcing 5MB limit in `limit_body` dependency, plus 2,000 row limits per array.
- **Verification:** Verified via `tests/test_dispater_security.py`.
