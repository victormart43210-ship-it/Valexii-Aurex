# OPERATION KUSANAGI CXXIV — CANONICAL INTEGRATION ARCHITECTURE
**October 21, 2026 · VALEXII.AI / AUREX Governance & Integration Architecture**

## Executive Overview
OPERATION KUSANAGI CXXIV establishes ONE unified, governed AUREX backend architecture consolidating financial audit intelligence, NVIDIA document processing, four NVIDIA financial research modules, and website workstation contract endpoints into a single execution spine.

- **Baseline Canonical Main SHA:** `df0654390049118a142ec3b3356f0f40b4789fe4`
- **Integration Branch:** `work/kusanagi-cxxiv-sovereign-convergence`
- **Governance Sequence:** Evidence → Qualification → Reality → Authority → Effect
- **Core Governing Rule:** "The system may never be its own sole witness."

---

## 1. Single Execution Spine Architecture
All API contracts, worker execution, document intelligence, and financial reconciliation flow through one governed FastAPI application registered in `aurex/api.py`.

```
               +-------------------------------------------------+
               |  VALEXII.COM / Lovable Owner Workstation       |
               +-----------------------+-------------------------+
                                       |
                          HTTPS / Bearer Auth Header
                                       v
               +-------------------------------------------------+
               |          AUREX FastAPI Canonical API            |
               |                 (aurex/api.py)                  |
               +---+-------------------+-------------------+-----+
                   |                   |                   |
                   v                   v                   v
     +-------------------+   +-------------------+   +-------------------+
     | Financial Audit   |   | NVIDIA Doc V4     |   | NVIDIA Finance 4  |
     | Engine            |   | Intelligence      |   | Research Modules  |
     | (aurex/field_     |   | (aurex/nvidia_    |   | (aurex/nvidia_    |
     |  reconciliation)  |   |  doc_v4.py)       |   |  finance/)        |
     +---------+---------+   +---------+---------+   +---------+---------+
               |                       |                       |
               +-----------------------+-----------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |        Atomic SQLite Fenced Worker              |
               |             (aurex/fenced_worker.py)            |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |           Immutable Evidence Ledger             |
               |        (SHA-256 Digest / NOT VERIFIED)          |
               +-------------------------------------------------+
```

---

## 2. Core Subsystems

### A. Financial Audit Intelligence Subsystem
- **Modules:** `aurex/field_reconciliation.py`, `aurex/audit_pilot.py`, `aurex/audit_challenge.py`, `aurex/folio_index.py`, `aurex/field_assurance.py`.
- **Arithmetic Rule:** Exact `Decimal` and integer cent representations (`invoice_cents`, `ticket_cents`). Floating-point arithmetic is strictly prohibited for monetary reconciliation.
- **Rules:** Invoice vs field-ticket variance, rate approvals, quantity/rate variance, duplicate invoice IDs, and missing documentation.

### B. NVIDIA Document Intelligence V4 Subsystem
- **Modules:** `aurex/nvidia_doc_v4.py`, `integrations/kusanagi-xvi/backend/doc_intelligence.py`.
- **Pipeline:** Document Ingestion → File Hashing → Bounded Segmentation (max 2 parts, 3500 chars) → Nemotron Candidate Analysis → Quotation Match Verification (`EXACT_MATCH` / `NORMALIZED_MATCH`) → Evidence Ledger Record.
- **Budget Guard:** Atomic SQLite daily call and dollar limits (`document_quota`). Disabled by default (`AUREX_NVIDIA_DOCS_ENABLED=1` required).

### C. Four NVIDIA Financial Research Modules
- **Modules:** `aurex/nvidia_finance/offline.py`, `workstation/nvidia_fsi_lab.py`.
- **Module A:** Quantitative Signal Discovery Agent (trading authority: NONE).
- **Module B:** Transaction Foundation Model (RAPIDS/NeMo feature baseline).
- **Module C:** AI Model Distillation for Financial Data (teacher/student evaluation interface).
- **Module D:** Financial Fraud Detection (unverified fraud-score intake).

---

## 3. Authority & Governance Boundaries
1. **Advisory Outputs Only:** All AI findings are candidate reports carrying `verification_status: "NOT_VERIFIED"` and `authority: "NONE"`.
2. **Zero Payment Authority:** No AI model or automated job can authorize payment, issue refund, or make legal claims.
3. **$0 Default Spending Policy:** External AI API spend defaults to $0.00. Paid inference is disabled by default.
4. **Human Review Required:** All findings require independent human review prior to action (`HUMAN_REVIEW_REQUIRED`).
