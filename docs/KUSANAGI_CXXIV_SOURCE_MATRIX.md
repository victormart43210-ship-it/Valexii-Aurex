# OPERATION KUSANAGI CXXIV — SOURCE CONVERGENCE MATRIX
**October 21, 2026 · AUREX Subsystem Source Provenance & PR Reconciliation**

## Overview
This matrix tracks all source code modules, tests, fixtures, and documentation merged into `work/kusanagi-cxxiv-sovereign-convergence` from the four candidate PRs (#99, #104, #106, #107) and the recovered CXX integration work.

---

## PR Source Provenance & Reconciled Target Paths

| Originating PR / Work | Source Commit SHA | Original File Path | Reconciled Target Path | Status |
| --- | --- | --- | --- | --- |
| PR #99 Financial Audit | `8e859304` | `aurex/field_reconciliation.py` | `aurex/field_reconciliation.py` | **CONVERGED** |
| PR #99 Financial Audit | `8e859304` | `aurex/audit_pilot.py` | `aurex/audit_pilot.py` | **CONVERGED** |
| PR #99 Financial Audit | `8e859304` | `aurex/audit_challenge.py` | `aurex/audit_challenge.py` | **CONVERGED** |
| PR #99 Financial Audit | `8e859304` | `aurex/folio_index.py` | `aurex/folio_index.py` | **CONVERGED** |
| PR #99 Financial Audit | `8e859304` | `aurex/field_assurance.py` | `aurex/field_assurance.py` | **CONVERGED** |
| PR #99 Financial Audit | `8e859304` | `workstation/field_audit_beta_pipeline.py` | `workstation/field_audit_beta_pipeline.py` | **CONVERGED** |
| PR #104 API & SQLite | `3b3d1de6` | `aurex/api.py` | `aurex/api.py` | **CONVERGED** |
| PR #104 API & SQLite | `3b3d1de6` | `aurex/fenced_worker.py` | `aurex/fenced_worker.py` | **CONVERGED** |
| PR #104 API & SQLite | `3b3d1de6` | `aurex/database.py` | `aurex/database.py` | **CONVERGED** |
| PR #106 NVIDIA Doc V4 | `17fdd827` | `integrations/kusanagi-xvi/backend/doc_intelligence.py` | `aurex/nvidia_doc_v4.py` & `integrations/kusanagi-xvi/backend/app.py` | **CONVERGED** |
| PR #107 NVIDIA Finance 4 | `b2960cfd` | `aurex/nvidia_finance/offline.py` | `aurex/nvidia_finance/offline.py` | **CONVERGED** |
| PR #107 NVIDIA Finance 4 | `b2960cfd` | `workstation/nvidia_fsi_lab.py` | `workstation/nvidia_fsi_lab.py` | **CONVERGED** |
| KUSANAGI CXX | `1dee5cd` | `docs/KUSANAGI_CXX_*` | `docs/KUSANAGI_CXX_*` | **RECOVERED & VERIFIED** |

---

## Architectural Resolutions
1. **API Contract Unification:** Merged PR #104's `aurex/api.py` with PR #106's `doc_intelligence.py` and PR #107's `nvidia_finance`. All endpoints share `get_token` and `authenticate` bearer protection.
2. **Worker Lease Fencing:** Unified `aurex/fenced_worker.py` to handle both offline SQLite roundtrip probes and lease-fenced terminal failures (`fail_job`).
3. **Budget Governance:** Consolidated budget checking so `get_budgets` reports spend from both offline budget guard and NVIDIA document quota SQLite table.
