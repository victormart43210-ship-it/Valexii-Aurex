# OPERATION KUSANAGI CXXIV — WORKSTATION CONTRACT COMPATIBILITY MATRIX
**October 21, 2026 · VALEXII.COM / Lovable Owner Workstation Contract Mapping**

## Overview
This document details the frontend/backend contract compatibility between the Lovable AUREX/OX Workstation (`811ffc43-2c8b-4c88-ab4c-4de668d089cb`, snapshot `c45e3585c9986e7fec87fa35a08fd28f4b392d74`) and the converged AUREX FastAPI backend (`work/kusanagi-cxxiv-sovereign-convergence`).

---

## 1. Verified Read-Only API Endpoints

| Endpoint | Method | Response Schema | Backend Implementation | Compatibility Status |
| --- | --- | --- | --- | --- |
| `/v1/health` | GET | `{"status": "ok", "version": "...", "time": "..."}` | `aurex/api.py:health` | **VERIFIED (200 OK)** |
| `/v1/capabilities` | GET | `{"capabilities": [{"id": "...", "available": bool}]}` | `aurex/api.py:capabilities` | **VERIFIED (200 OK)** |
| `/v1/evidence` | GET | `{"evidence": [{"id": "...", "sha256": "..."}]}` | `aurex/api.py:get_evidence` | **VERIFIED (200 OK)** |
| `/v1/budgets` | GET | `{"limitUsd": float, "spentUsd": float}` | `aurex/api.py:get_budgets` | **VERIFIED (200 OK)** |
| `/v1/jobs` | GET | `{"jobs": [{"id": "...", "state": "..."}]}` | `aurex/api.py:get_jobs` | **VERIFIED (200 OK)** |

---

## 2. Document & Financial Review Workflow Endpoints

| Endpoint | Method | Request Payload | Response Payload | Status |
| --- | --- | --- | --- | --- |
| `/v1/jobs` | POST | `{"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"}}` | `{"id": "...", "state": "succeeded"}` | **VERIFIED** |
| `/v1/jobs/{id}` | GET | None | `{"id": "...", "state": "succeeded"}` | **VERIFIED** |
| `/v1/jobs/{id}/cancel` | POST | None | `{"id": "...", "state": "cancelled"}` | **VERIFIED** |
| `/v1/documents/status` | GET | None | `{"status": "STAGED_ENABLED" / "DISABLED"}` | **VERIFIED** |
| `/v1/documents/analyze` | POST | `{"text": "...", "source_label": "..."}` | `{"summary": "...", "evidence_quotes": [...]}` | **VERIFIED** |

---

## 3. Security Boundaries
- **Server-Only Credentials:** Service Bearer tokens (`AUREX_SERVICE_TOKEN`) are handled strictly server-side in server functions (`website/src/lib/aurex-client.server.ts`). Credentials are never exposed to browser clients.
- **SSRF Protection:** `AUREX_BACKEND_BASE_URL` origin pinning prevents client adapter from redirecting or sending credentials to unauthorized external origins.
