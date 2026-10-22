# OPERATION KUSANAGI CXXVII — WORKSTATION CONTRACT MATRIX
**October 22, 2026 · AUREX/OX Workstation Frontend/Backend Integration**

## Overview
This document specifies the contract compatibility and integration mapping between the AUREX/OX Workstation (`website/src/lib/aurex-client.server.ts` and `website/src/lib/aurex-cxxv-bridge.ts`) and the canonical FastAPI backend (`aurex/api.py`).

---

## 1. Five Read-Only Base Endpoints

| Endpoint | Method | Request Headers | Backend Handler | Response Contract | Status |
| --- | --- | --- | --- | --- | --- |
| `/v1/health` | GET | `Authorization: Bearer <token>` | `aurex/api.py:health` | `{"status": "ok", "version": "...", "time": "..."}` | **VERIFIED** |
| `/v1/capabilities` | GET | `Authorization: Bearer <token>` | `aurex/api.py:capabilities` | `{"capabilities": [{"id": "...", "available": bool}]}` | **VERIFIED** |
| `/v1/evidence` | GET | `Authorization: Bearer <token>` | `aurex/api.py:get_evidence` | `{"evidence": [{"id": "...", "sha256": "..."}]}` | **VERIFIED** |
| `/v1/budgets` | GET | `Authorization: Bearer <token>` | `aurex/api.py:get_budgets` | `{"limitUsd": float, "spentUsd": float}` | **VERIFIED** |
| `/v1/jobs` | GET | `Authorization: Bearer <token>` | `aurex/api.py:get_jobs` | `{"jobs": [{"id": "...", "state": "..."}]}` | **VERIFIED** |

---

## 2. Governed Pipeline Execution Endpoints

| Endpoint | Method | Input Contract | Output Contract | Verification Status |
| --- | --- | --- | --- | --- |
| `/v1/jobs` | POST | `JobCreateRequest` (`kind`, `params`, `maxCostUsd`) | `JobResponse` (`id`, `state`, `reservationUsd`) | **VERIFIED** |
| `/v1/jobs/{job_id}` | GET | None | `JobResponse` | **VERIFIED** |
| `/v1/jobs/{job_id}/receipt` | GET | None | `PipelineReceiptSchema` | **VERIFIED** |
| `/v1/jobs/{job_id}/cancel` | POST | None | `JobResponse` (`state: "cancelled"`) | **VERIFIED** |
| `/v1/documents/status` | GET | None | `{"status": "STAGED_ENABLED" / "DISABLED"}` | **VERIFIED** |
| `/v1/documents/analyze` | POST | `AnalyzeInput` (`text`, `source_label`) | `Analysis` (`summary`, `evidence_quotes`) | **VERIFIED** |

---

## 3. Security Boundary Rules
1. **Server-Side Token Handling:** The Railway service Bearer token (`AUREX_SERVICE_TOKEN`) is used strictly in server-side functions (`website/src/lib/aurex-client.server.ts`). Tokens are never sent to browser clients.
2. **SSRF Origin Pinning:** `AUREX_BACKEND_BASE_URL` origin pinning prevents client proxy from sending Bearer tokens to arbitrary external destinations.
3. **Receipt Qualification:** Pipeline receipts strictly require `integrity: "RECORDED"`, `verification: "NOT VERIFIED"`, and `authority: "NONE"`.
