# DISPATER.AI — SECURITY GATES & RELIABILITY CONTROLS
**Operation:** KUSANAGI CCXVIII
**Auditor:** Jules (Project Adversarial Truth — 100% Closed-Beta Acceptance)

---

## 1. Non-Delegable Authority Boundaries
1. **The System May Never Be Its Own Sole Witness**: AI model outputs and deterministic reconciliation results are evidence candidates. They possess `HUMAN_REVIEW_REQUIRED` status and can never execute financial writebacks, bank transfers, or accounting journal entries.
2. **Authority Invariants (Gate 6)**: Malicious instructions embedded in tickets, invoices, or reports cannot self-authorize release, modify confirmed recovery, or alter tenant boundaries.
3. **Production Release Authority**: Permanently locked on `HOLD`.
4. **Financial Authority**: `NONE`.
5. **External Paid Inference**: `OFF`.

---

## 2. Threat Modeling & Defenses Verified

### Cross-Tenant Principal Authorization (Gate 4)
- **Vulnerability Addressed:** Prevention of caller-supplied tenant ID spoofing.
- **Defense:** `authenticate_principal` binds bearer token SHA-256 digests to permitted tenant IDs in `AUREX_DISPATER_TENANT_GRANTS`. `authorize_tenant` enforces uniform HTTP 403 Forbidden on mismatch without leaking tenant existence.
- **Verification:** Verified via `tests/test_dispater_security.py` (30 tests passing).

### Durable SQLite Persistence & Mount Validation (Gate 2)
- **Vulnerability Addressed:** Ephemeral loss of audit state during pod/container restarts and unverified memory mutations.
- **Defense:** Validation of storage directory writability before database connection; rejection of `/tmp` when `AUREX_DISPATER_REQUIRE_PERSISTENT=1`; atomic persistence to `dispater_runs` and `dispater_findings` with WAL checkpointing and receipt verification.
- **Verification:** Verified across simulated service restarts and receipt tampering in `tests/test_dispater_security.py`.

### Request Stream Bounds & Starvation Defense (Gate 3)
- **Defense:** Asynchronous request body stream inspection enforcing 5MB limit in `limit_body` dependency, caching the body in `request._body` so downstream handlers access the payload without starvation.
- **Verification:** Verified via `tests/test_dispater_security.py`.

### Independent Financial Calculation (Gate 5)
- **Defense:** Independent reference calculator checks underbilling, overbilling, and unverified exposure separately from the engine.
- **Verification:** Verified via `test_independent_financial_oracle_reconciliation`.
