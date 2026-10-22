# OPERATION KUSANAGI CXX — INTEGRATION COMPATIBILITY MATRIX
**October 21, 2026 · AUREX Subsystem Integration Mapping**

## Overview
This matrix maps the source components, contracts, and authority rules consolidated from PRs #99, #104, and #106 into the unified `work/kusanagi-cxx-jules-convergence` candidate branch.

---

## Subsystem Source & Integration Mapping

| Subsystem / Feature | Originating PR | Primary Files | Reconciled Path | Integration Status |
| --- | --- | --- | --- | --- |
| Field Audit Reconciliation Rules | PR #99 (`8e859304`) | `aurex/field_reconciliation.py` | `aurex/field_reconciliation.py` | **INCORPORATED & VERIFIED** |
| Oilfield 9-Document Audit Pilot | PR #99 (`8e859304`) | `aurex/audit_pilot.py`, `aurex/audit_challenge.py` | `aurex/audit_pilot.py` | **INCORPORATED & VERIFIED** |
| Folio Ledger Index | PR #99 (`8e859304`) | `aurex/folio_index.py` | `aurex/folio_index.py` | **INCORPORATED & VERIFIED** |
| 100-Case Synthetic Gate & Pipeline | PR #99 (`8e859304`) | `workstation/field_audit_beta_gate.py`, `workstation/field_audit_beta_pipeline.py` | `workstation/field_audit_beta_pipeline.py` | **INCORPORATED & VERIFIED** |
| International Assurance Controls | PR #99 (`8e859304`) | `aurex/field_assurance.py` | `aurex/field_assurance.py` | **INCORPORATED & VERIFIED** |
| Canonical FastAPI App & Endpoints | PR #104 (`3b3d1de6`) | `aurex/api.py` | `aurex/api.py` | **INCORPORATED & VERIFIED** |
| Fenced Worker & SQLite Lease Engine | PR #104 (`3b3d1de6`) | `aurex/fenced_worker.py`, `aurex/database.py` | `aurex/fenced_worker.py` | **INCORPORATED & VERIFIED** |
| NVIDIA Doc Intelligence V4 | PR #106 (`17fdd827`) | `integrations/kusanagi-xvi/backend/doc_intelligence.py` | `aurex/nvidia_doc_v4.py` & `integrations/kusanagi-xvi/backend/app.py` | **INCORPORATED & VERIFIED** |
| Website Client Adapter | PR #104 (`3b3d1de6`) | `website/src/lib/aurex-client.server.ts` | `website/src/lib/aurex-client.server.ts` | **INCORPORATED & VERIFIED** |

---

## Architectural Resolution of PR #106 vs PR #104
- **Problem:** PR #106 introduced a separate FastAPI bridge in `integrations/kusanagi-xvi/backend/app.py` while PR #104 modified canonical `aurex/api.py`.
- **Resolution:** `doc_intelligence.py`'s `register_document_routes` and `budget_snapshot` were integrated into BOTH canonical `aurex/api.py` and `integrations/kusanagi-xvi/backend/app.py`. Both endpoints use identical bearer token authentication (`authenticate` / `authorize`), identical SQLite document daily budget tracking (`document_quota`), and identical Pydantic schema validation (`AnalyzeInput` / `Analysis`).
- **Authority Unification:** There is ONE governed authority model across all routes: outputs carry `verification_status: "NOT_VERIFIED"`, `authority: "NONE"`, and `release: "HOLD"`.

---

## Excluded or Deferred Components
1. **Paid External Model Inference:** All paid inference endpoints remain disabled by default ($0.00 default budget).
2. **Direct Main Merge:** Wholesale auto-merging of PRs #99, #104, #106 into protected `main` is withheld pending explicit product owner approval.
3. **Lovable Dashboard Publication:** Source code changes are verified locally; no production deployment or live Cloudflare publication performed.
