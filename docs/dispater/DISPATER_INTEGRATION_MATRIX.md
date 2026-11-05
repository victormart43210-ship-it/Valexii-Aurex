# DISPATER.AI — INTEGRATION MATRIX & API SPECIFICATION
**Operation:** KUSANAGI CCX
**API Prefix:** `/v1/dispater`
**Authentication:** Bearer token (min 32 chars) via `authenticate` middleware

---

## 1. REST Endpoints Specification

### `POST /v1/dispater/reconciliation`
Executes deterministic multi-record reconciliation across jobs, invoices, approved rates, and payments.

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
        "date": "YYYY-MM-DD"
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
  Returns `DispaterReconciliationReport` including `counts`, `financial_summary`, `findings` (with 5-step XAELI explanations), and `receipt_sha256`.

---

### `GET /v1/dispater/findings?tenant_id={tenant_id}`
Retrieves active audit findings for a specific tenant from the latest reconciliation execution.

- **Response**:
  ```json
  {
    "tenant_id": "tenant-01",
    "status": "AUDIT_COMPLETE",
    "dataset_sha256": "...",
    "receipt_sha256": "...",
    "financial_summary": { ... },
    "findings": [ ... ],
    "count": 2
  }
  ```

---

### `GET /v1/dispater/dashboard?tenant_id={tenant_id}`
Returns tenant-level summary metrics, identified exposure, confirmed recovery ($0.00), finding severity distribution, and governance locks.

- **Response**:
  ```json
  {
    "tenant_id": "tenant-01",
    "status": "AUDIT_COMPLETE",
    "last_reconciliation_sha256": "...",
    "identified_exposure_usd": "500.00",
    "confirmed_recovery_usd": "0.00",
    "finding_counts": {
      "total": 1,
      "critical": 0,
      "high": 1,
      "medium": 0
    },
    "recent_findings": [ ... ],
    "system_state": {
      "production_release": "HOLD",
      "financial_authority": "NONE",
      "external_paid_inference": "OFF"
    }
  }
  ```

---

## 2. Security & Architectural Controls
1. **SSRF & Egress Protection**: Browser clients cannot invoke the raw backend directly; requests route through server-only functions (`dispater.server.ts`).
2. **Formula Injection Sanitization**: Inputs starting with `=, +, -, @, \t, \r` are prepended with `'`.
3. **Decimal Arithmetic**: All financial calculations use Python `decimal.Decimal` with explicit `0.01` quantization.
