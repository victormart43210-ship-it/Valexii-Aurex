# OPERATION KUSANAGI CCLXXV
## CROSS-SYSTEM CONTRACT AUDIT & SUBSYSTEM BOUNDARY CLASSIFICATION

**Date:** 2026-11-07
**Commit SHA Audited:** `061b97022797013ccd1395a377b9489e59ba83f3` (merged mainline post-PR #194)
**Assurance Lead:** Google Jules

---

### I. EXECUTIVE SUMMARY & AUTHORITY CHAIN

The canonical VALEXII / AUREX system enforces the non-delegable authority chain:
$$\text{Evidence} \longrightarrow \text{Qualification} \longrightarrow \text{Reality} \longrightarrow \text{Authority} \longrightarrow \text{Effect}$$

Under Operation KUSANAGI CCLXXV, an independent verification of all cross-system implementation boundaries was executed. No synthetic demonstration is promoted to operational authority, no financial exposure is converted to recovery ($0.00 confirmed recovery), and no unverified boundary is mislabeled as live integration.

---

### II. BOUNDARY CLASSIFICATION MATRIX

| Boundary | Path / Subsystem | Implementation Classification | Evidence & Contract Enforcement |
| :--- | :--- | :--- | :--- |
| **B1: Website → AUREX Service** | `website/src/lib/aurex-client.server.ts` → `aurex/api.py` | **IMPLEMENTED_AND_TESTED** | Fail-closed URL parsing (`validServiceUrl`), bearer auth with $\ge 32$-char token requirement, request timeout handling with `AbortController`, typed Pydantic/Zod schemas, body ceiling guards (5MB). |
| **B2: Website → XAELI → AUREX** | `website/src/routes/xaeli.tsx` → `website/src/lib/xaeli.functions.ts` → `aurex/xaeli_staging.py` | **PARTIAL** | Scripted examples displayed clearly labeled as scripted. Server function `readXaeliStagingStatus` invokes `/v1/xaeli-staging/explain` fail-closed. Real local model probe returns `OFFLINE` when backend local inference is unavailable. Never mocks live model responses. |
| **B3: DISPATER Console → Server Functions** | `website/src/components/dispater-reconciliation-console.tsx` → `website/src/lib/dispater.server.ts` | **IMPLEMENTED_AND_TESTED** | Server-side bearer auth, server-enforced tenant ID (`demo-oilfield-tenant`), backend body leakage prevented, MAC receipt validation round-trip tested. |
| **B4: DISPATER → AUREX Engine → Persistence** | `website/src/lib/dispater.server.ts` → `aurex/dispater_api.py` → `aurex/dispater_intelligence.py` → `aurex/dispater_store.py` | **IMPLEMENTED_AND_TESTED** | Deterministic revenue reconciliation engine with SHA-256 evidence digests, formula-injection defense, SQLite persistent storage (`dispater_runs`, `dispater_findings`), HMAC-SHA256 Bound v2 receipts, 36-month audit tested against independent mathematical oracle. |
| **B5: Industrial Towing Admission** | `website/src/lib/industrial.server.ts` → `aurex/industrial_execution.py` | **IMPLEMENTED_AND_TESTED** | Advisory fixed towing admission, owner and origin checked, cross-user rejection verified, payload bounded to prevent memory exhaustion. |
| **B6: Owner Administration & Control** | `website/src/routes/admin.aurex-control.tsx` → `website/src/lib/aurex-control.functions.ts` | **IMPLEMENTED_AND_TESTED** | Supabase owner session required, fail-closed without configured owner, strict SSRF allowlist on observe paths (`valexii.com` paths only), PROPOSE/APPLY gates disabled without explicit credentials and owner approval. |
| **B7: MEDAURUS / BCXMET Boundary** | `website/src/routes/bcxmet.tsx` & `website/src/routes/medaurus.tsx` | **PARTIAL** (Simulated / Spec) | Client-side architectural simulation models (`telemetry-universe-model.ts`, `phone-scenarios.ts`). Negative tests verify that simulated instruments never promote demo progress to evidence, clearance, or authority. No live hardware/BLE interface claimed. |
| **B8: Manuscript Forensics Research Lab** | `aurex/ascendancy/` (PR #193 branch) | **BLOCKED** (Pending review) | Mainline contains foundational graph/hypothesis models in `aurex/ascendancy/`. Full imaging laboratory remains isolated in PR #193 on Cursor's branch. Mainline does not pretend manuscript imaging is connected. |

---

### III. DETAILED CROSS-SYSTEM SECURITY & INTEGRATION AUDIT

#### 1. Authentication & Tenant Isolation
- **Tenant Grants:** Enforced in `aurex/dispater_api.py` via `_verify_tenant_access`. Bearer tokens are SHA-256 hashed and matched against tenant grant mappings; cross-tenant spoofing yields uniform HTTP 403 responses.
- **Filesystem & Store Isolation:** `aurex/dispater_store.py` canonicalizes paths and validates database mount directory. Sibling tenant injection (`tenant-a` vs `tenant-a-other`) is strictly rejected.

#### 2. Evidence Provenance & Golden Financial Invariants
- **Evidence Ledger:** SHA-256 content addressing on all admitted tickets, invoices, and contracts. Findings contain raw value, normalized decimal, locator, and byte digests.
- **Golden Rule Verification:**
  - Exposure Identified: **$385.00**
  - Potential Underbilling: **$100.00**
  - Potential Overbilling: **$130.00**
  - Unverified Exposure: **$155.00**
  - Withheld Unresolved: **$150.00**
  - Confirmed Recovery: **$0.00** (strict lock)
  - Authority State: **HOLD**
- No automated algorithm or model consensus has authority to release funds or mark money recovered.

#### 3. Fail-Closed Network & Resource Limits
- Request timeouts strictly enforced via `AbortController` in TypeScript.
- Server-side body size limit middleware enforces 5MB maximum request size in ASGI backend (`aurex/api.py`, `aurex/dispater_api.py`).
- Input sanitization blocks formula injection (`=`, `+`, `-`, `@`, `\t`, `\r`) in CSV ingestion.

#### 4. Environment & Virtualization Limitations
- In the local testing sandbox, Docker build fails on containerd overlayfs cache mounts (`mount source: overlay... err: invalid argument`) due to unprivileged container virtualization constraints. Native host execution passes 100% of linting, typing, unit, and integration tests.
