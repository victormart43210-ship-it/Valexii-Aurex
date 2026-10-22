# OPERATION KUSANAGI CXXVII — SOURCE RECONCILIATION REPORT
**October 22, 2026 · AUREX Sovereign Pipeline Closure Source Inventory**

## Executive Summary
OPERATION KUSANAGI CXXVII reconciles six open pull requests (#99, #104, #106, #107, #108, #109) and the recovered CXX integration work into a single governed candidate on branch `work/kusanagi-cxxvii-jules-pipeline-closure`.

- **Baseline Main SHA:** `df0654390049118a142ec3b3356f0f40b4789fe4` (origin/main)
- **Integration Target Branch:** `work/kusanagi-cxxvii-jules-pipeline-closure`

---

## 1. Pinned Source PR Inventory

| Pull Request | Target / Stack | Pinned Commit SHA | Primary Capabilities | Reconciled Target Paths |
| --- | --- | --- | --- | --- |
| **PR #99** | `main` | `8e859304d14c6aaa2cd4ed84d2e9db93fe9700b9` | Field Financial Audit Beta, 100-case gate, 9-doc oilfield pilot, 12 assurance controls | `aurex/field_reconciliation.py`, `aurex/audit_pilot.py`, `aurex/field_assurance.py`, `workstation/field_audit_beta_pipeline.py` |
| **PR #104** | `main` | `3b3d1de63f764a777758f709130a91324bcd06ca` | Canonical API, SQLite jobs, worker lease fencing, contract tests | `aurex/api.py`, `aurex/fenced_worker.py`, `aurex/database.py` |
| **PR #106** | `main` | `17fdd82718178544146fe7e8870b0d6eb1d56f1a` | NVIDIA Document Intelligence V4, Nemotron prompt template, quote verification | `aurex/nvidia_doc_v4.py`, `integrations/kusanagi-xvi/backend/doc_intelligence.py` |
| **PR #107** | PR #104 | `b2960cfd0911c21bc96798bead4f60f7808a3907` | Four NVIDIA Financial Research Modules (Signal, Transaction, Distillation, Fraud) | `aurex/nvidia_finance/offline.py`, `workstation/nvidia_fsi_lab.py` |
| **PR #108** | `main` | `eb707fd0ad6729768451be2256160369c31f41a7` | CXXV Workstation Bridge, snake_case capabilityId schema alignment | `website/src/lib/aurex-cxxv-bridge.ts`, `website/src/components/aurex-cxxv-bridge.test.ts` |
| **PR #109** | `main` | `155ce1e969ae58df6b5400d38e5db5c1f840a047` | CXXVI Pipeline Receipts, Dockerfile.aurex, receipt verification tests | `aurex/pipeline_receipts.py`, `Dockerfile.aurex`, `tests/test_cxxvi_pipeline_receipts.py` |

---

## 2. CXXIV Recovery Analysis
- **Remote Branch Query:** `work/kusanagi-cxxiv-sovereign-convergence` was not found on remote origin during last inspection.
- **Recovery Resolution:** Recovered the full source implementation from commit `1dee5cd57297eefb3c89fb4581cbb477e7707bc6` on local submit branch `origin/kusanagi-cvii-mainline-ascension-4026168584527254885`, incorporating all 12 financial audit files, NVIDIA Doc V4 files, and CXX deliverables (`docs/KUSANAGI_CXX_*`).
- **Evidence Verification:** Reproduced 393/393 backend pytest passes, 139/139 website bun test passes, and 100/100 synthetic field audit matches.

---

## 3. Reconciled Contract Alignment
1. `capabilityId` naming aligned to `snake_case` (`regression_scan`, `evidence_vault`, `memory_graph`, etc.) matching PR #104 and PR #108.
2. `aurex/api.py` imports `register_document_routes` from `aurex.nvidia_doc_v4` and registers `/v1/documents/status` and `/v1/documents/analyze`.
3. `aurex/pipeline_receipts.py` generates SHA-256 evidence digests linking job ID, worker ID, observation, and receipt verification status.
