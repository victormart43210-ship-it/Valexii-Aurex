# Railway migration admission — CLXXXIII

PR150 branch work/kusanagi-clxxxiv-inference-guard; source CP001 edf081138bd73204b29d2337d08db079fb4494c4. Status: HOLD, not applied.
Read-only provider inspection on 2026-10-26:
- Project 78095d3d-5911-41c8-aa3e-f9ebf5d81054; service 2b51dfe6-2175-4cb0-aac2-eb40ecbc3a1d.
- Staging 98c103eb-a1af-46b6-948e-19c80e4d720d: main, root /integrations/kusanagi-xvi/backend, Dockerfile, sfo one replica. No staged changes.
- Latest deployment 8fe3f398-4e6f-4bfa-8c79-da1b84ccefb4 SUCCESS, created 2026-10-24T12:23:27.131Z. Source SHA f2db438f0020dbd455bcb5c7b21b7352d133bf2c is historical reported, NOT freshly verified by these tools. Runtime health NOT RUN.
- Production metadata read only: environment 9a139b10-9e6b-4ebd-89c7-731855cbbb5c; deployment ee18058c-cde8-4611-b0bd-443e124c9761 SUCCESS. No production data accessed.
- Both metadata views expose volume 4d23b1e6-3625-4def-aa97-82e10859f04d at /data, 50000MB, sfo. This does not establish either shared or separate backing storage. Physical isolation NOT VERIFIED.

Application comparison:
| Candidate | Entry | Status |
|---|---|---|
| Current root | uvicorn app:app | Legacy bridge; does not import canonical XAELI router |
| Repository root Dockerfile | uvicorn aurex.api:app | Canonical authenticated status/ask and industrial audit; loopback tested |
| Jules PR151 | Additional components/policy on canonical source | Unmerged; browser-local queue/binder; do not substitute for persisted tenant isolation |

Prepared configuration change after all gates: retain project/service/domain/volume; source root /, Dockerfile path Dockerfile; reviewed immutable PR150 candidate SHA (not floating main); existing CMD binds PORT or8080 as UID10001. Root image creates /data for UID10001, but mounted-volume ownership requires separate verification. Root Dockerfile local build NOT RUN: docker unavailable. Existing .github/workflows/railway-image.yml is the CI build/smoke gate; obtain exact-head PASS before approval.
Canonical DB path AUREX_DB_PATH is captured at import (default /tmp/aurex_jobs.db). Set an explicitly isolated persistent staging path before process starts; do not assume /tmp is durable. Do not open legacy SQLite with canonical get_db: CREATE TABLE IF NOT EXISTS is not a schema migration; legacy params versus canonical params_json/evidence_records remains incompatible. Use isolated synthetic storage only after ownership/isolation confirmed, without detaching production. Preserve existing DB backup; no backup availability verified here.
Health contract changes: canonical /v1/health is public; protected API requires valid server bearer of at least32 chars, SERVICE/ADMIN aliases must not conflict. Diagnose proxies using those actual contracts. Keep LLM enabled/billing false; remote denial also unconditional in source. Canonical towing worker is bounded synchronous execution, not evidence that legacy supervisor reliability has migrated.

Rollback reference: prior staging deployment ID above and current root/main configuration. Reverting code alone cannot repair migrated data. Before deployment obtain verified snapshot/restore procedure, immutable source SHA, staging-only token ownership, isolated backing-volume evidence, exact-head CI, independent review, and explicit staging approval. No backup, restart, rollback or deployment was performed. Do not stage config now; production unchanged. Next: provider/owner establishes environment-scoped backing storage and restorable backup via metadata/support, without writing production records.
