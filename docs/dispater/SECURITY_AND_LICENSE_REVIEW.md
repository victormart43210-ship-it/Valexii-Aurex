# DISPATER.AI — SECURITY AND LICENSE REVIEW
**Date:** November 2026
**System:** AUREX-OX / DISPATER.AI
**Scope:** Commercial Pilot Convergence, Dependencies, and Authority Constraints

---

## 1. Security Architecture & Threat Defense

1. **Fail-Closed Tenant Isolation:**
   - Bearer tokens are mapped via SHA-256 digests in `AUREX_DISPATER_TENANT_GRANTS`.
   - Any unauthenticated, malformed, or cross-tenant request receives an invariant 401 or uniform 403 Forbidden.
2. **Raw ASGI Stream Body Limiting:**
   - `BodyLimitMiddleware` intercepts raw HTTP stream chunks to enforce a strict 5MB limit before request buffering or parsing.
3. **Formula Injection Sanitization:**
   - Spreadsheet injection characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are neutralized upon ingestion and escaped during CSV generation.
4. **Persistent Mount Protection:**
   - `validate_storage_mount` prevents execution on volatile storage or `/tmp` when persistent volumes are mandated (`AUREX_DISPATER_REQUIRE_PERSISTENT=1`).
5. **Tamper-Evident Receipts:**
   - Database reads verify report SHA-256 receipts against content bodies, raising `IntegrityError` if disk data is modified out-of-band.

---

## 2. Dependency & Licensing Audit

- **Core Dependencies:** Python standard library (`decimal`, `hashlib`, `json`, `sqlite3`), FastAPI, Pydantic, Uvicorn, and Cryptography.
- **Licenses:** MIT, Apache 2.0, and BSD-3-Clause.
- **Copyleft / GPL Restrictions:** No AGPL or GPL dependencies are imported or linked into proprietary components.
- **External AI Inference:** Paid inference remains hard-coded to `OFF`. Engine execution is deterministic and local.
