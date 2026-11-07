# DISPATER.AI — SECURITY & OPEN-SOURCE LICENSE REVIEW
**Standard:** Fail-Closed Sovereign Architecture & Permissive Licensing
**Review Date:** November 5, 2026

---

## I. OPEN-SOURCE TECHNOLOGY EVALUATION

| Candidate Project | Domain | License | Security & Architectural Assessment | Adoption Decision |
|---|---|---|---|---|
| **Docling** | Document Extraction | MIT | High quality PDF text/table parsing; requires PyTorch/HF dependencies in full mode. | **Architectural Patterns Adopted** (lightweight internal parser maintained to avoid heavy container footprint). |
| **OpenContracts** | Contract Intelligence | Apache 2.0 | Clean structured clause extraction and contract versioning models. | **Schema Patterns Adopted** (implemented in rate schedule effective-date windowing). |
| **OpenMetadata** | Lineage & Governance | Apache 2.0 | Provenance graph and entity digest tracking. | **Digest Patterns Adopted** (SHA-256 evidence chain on all finding records). |
| **PM4Py** | Process Mining | GPLv3 / AGPL | Workflow discrepancy discovery. Strong copyleft creates severe licensing friction. | **REJECTED (GPL/AGPL Gate)**; deterministic state-machine dispatch matching used instead. |
| **ERPNext** | Billing Reconciliation | GPLv3 | Reference architecture only. | **Reference Model Only**; zero code imported. |

---

## II. SECURITY GATES VERIFICATION
1. **Tenant Isolation**: Bearer tokens verified via SHA-256 grants mapping (`AUREX_DISPATER_TENANT_GRANTS`). Uniform 403 on unauthorized tenants.
2. **Formula Injection Defense**: All exported cells neutralized against `=`, `+`, `-`, `@`, `\t`, `\r`.
3. **Stream Limiting**: 5MB ceiling enforced on raw ASGI stream before body buffering.
4. **Receipt Integrity**: HMAC-SHA256 signature and SHA-256 body hash verification.
