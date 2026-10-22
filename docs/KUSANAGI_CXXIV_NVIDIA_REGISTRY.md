# OPERATION KUSANAGI CXXIV — NVIDIA INTEGRATION REGISTRY
**October 21, 2026 · NVIDIA Model & Research Module Catalogue**

## Overview
This registry catalogs all NVIDIA integrations, model specifications, research modules, and authority bounds implemented across the converged AUREX backend.

---

## 1. NVIDIA Document Intelligence V4
- **Primary Module:** `aurex/nvidia_doc_v4.py` / `integrations/kusanagi-xvi/backend/doc_intelligence.py`
- **Target Provider Model:** `nvidia/nemotron-3.5-lightning-30b-a3b`
- **Endpoints:**
  - `GET /v1/documents/status` → Status report (`STAGED_ENABLED` / `DISABLED`)
  - `POST /v1/documents/analyze` → Bounded document analysis & citation verification
- **Activation Prerequisites:**
  1. `AUREX_NVIDIA_DOCS_ENABLED=1`
  2. `AUREX_NVIDIA_API_KEY` (minimum 20 characters)
  3. `X-Aurex-Cloud-Consent: approved` header
  4. Valid daily quota reservation in `/data/aurex-document-quota.sqlite`
- **Authority:** `NONE` (`verification_status: "NOT_VERIFIED"`, `release: "HOLD"`)

---

## 2. Four NVIDIA Financial Research Modules (PR #107)

### Module A — Quantitative Signal Discovery Agent
- **Module:** `aurex/nvidia_finance/offline.py` (`QuantitativeSignalDiscoveryAgent`)
- **Capability:** Candidate quantitative financial pattern discovery and hypothesis testing.
- **Authority:** `NONE` (Trading authority: `NONE`).

### Module B — Transaction Foundation Model
- **Module:** `aurex/nvidia_finance/offline.py` (`TransactionFoundationModel`)
- **Capability:** Transaction sequence analysis and anomaly candidate detection.
- **Authority:** `NONE` (Deterministic feature extraction; no autonomous transaction authority).

### Module C — AI Model Distillation for Financial Data
- **Module:** `aurex/nvidia_finance/offline.py` (`FinancialModelDistillationEngine`)
- **Capability:** Teacher/student dataset comparison and model evaluation harness.
- **Authority:** `NONE` (Dataset provenance evaluation only; no live training).

### Module D — Financial Fraud Detection
- **Module:** `aurex/nvidia_finance/offline.py` (`FinancialFraudDetector`)
- **Capability:** Suspicious transaction pattern risk scoring.
- **Authority:** `NONE` (Unverified risk score; no automatic transaction blocking).

---

## 3. Deployment Status
All NVIDIA cloud inference capabilities remain **DISABLED BY DEFAULT** with $0.00 allocated spend until explicit product owner consent, valid API credentials, and approved budgets are provided.
