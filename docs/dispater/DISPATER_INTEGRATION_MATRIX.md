# DISPATER.AI — INTEGRATION MATRIX & API SPECIFICATION
**Operation:** KUSANAGI CCXII
**API Prefix:** `/v1/dispater`
**Authentication & Authorization:** Principal token binding via `authorize_tenant_principal`

---

## 1. REST Endpoints Specification

### `POST /v1/dispater/reconciliation`
Executes deterministic multi-record reconciliation across jobs, invoices, approved rates, and payments, persisting findings into durable SQLite storage.

- **Request Headers**:
  `Authorization: Bearer <token>` (min 32 chars, authorized for `tenant_id`)
- **Request Schema**:
  ```json
  {
    "tenant_id": "string (1-64 chars)",
    "dataset_type": "SYNTHETIC_ONLY",
    "jobs": [
      {
        "job_id": "string",
        "customer_id": "string",
        "service_code": "string",
        "date": "YYYY-MM-DD",
        "hours": "optional float"
      }
    ],
    "rates": [
      {
        "rate_id": "string",
        "customer_id": "string",
        "service_code": "string",
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD",
        "amount": "0.00"
      }
    ],
    "invoices": [
      {
        "invoice_id": "string",
        "job_id": "string",
        "amount": "0.00",
        "status": "open | paid | disputed"
      }
    ],
    "payments": [
      {
        "payment_id": "string",
        "invoice_id": "string",
        "amount": "0.00"
      }
    ]
  }
  ```
- **Response**:
  Returns `DispaterReconciliationReport` including `run_id`, `counts`, `financial_summary` (with separate accounting for underbilling, overbilling, and unverified exposure), `findings` (with 5-step XAELI explanations), and `receipt_sha256`.

---

### `GET /v1/dispater/findings?tenant_id={tenant_id}`
Retrieves active audit findings for a specific tenant from durable SQLite persistence.

---

### `GET /v1/dispater/dashboard?tenant_id={tenant_id}`
Returns tenant-level summary metrics, identified exposure, confirmed recovery ($0.00), finding severity distribution, and governance locks.

---

## 2. Security & Architectural Controls
1. **Principal-Tenant Binding**: Principal credentials must match the tenant authorization registry (`AUREX_TENANT_TOKEN_<TENANT>`) or administrative service tokens (`AUREX_SERVICE_TOKEN`). Unauthorized cross-tenant queries fail closed with HTTP 403.
2. **Durable SQLite Persistence**: Audits are written atomically to `dispater_audit_runs` table in SQLite, preserving run metadata across container restarts.
3. **Formula Injection Sanitization**: Inputs starting with `=, +, -, @, \t, \r` are prepended with `'`.
4. **Decimal Arithmetic**: All financial calculations use Python `decimal.Decimal` with explicit `0.01` quantization.
