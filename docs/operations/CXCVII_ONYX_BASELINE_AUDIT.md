# OPERATION KUSANAGI CXCVII — ONYX BASELINE AUDIT

**Date:** October 27, 2026
**Execution Agent:** Google Jules
**Canonical Repository:** `victormart43210-ship-it/Valexii-Aurex`
**Working Branch:** `jules/kusanagi-cxcvii-onyx-bridge`
**Base Commit SHA:** `1c05a95f9c8a54854d31657c315864d93931d848`
**Audit Status:** RECONNAISSANCE & ADAPTER CONTRACT DEFINED

---

## 1. Executive Summary & Infrastructure Reconnaissance

A baseline audit of the canonical repository confirms the current status of the Onyx integration:

- **Onyx Implementation State:** `UNCONFIGURED / ADAPTER IMPLEMENTATION REQUIRED`.
- **AUREX Governance:** Active in `aurex/api.py` and `aurex/dispater_intelligence.py`.
- **Document Intelligence:** Ingestion and record extraction active in `aurex/dispater_documents.py`.
- **Local Inference Adapter:** Governed loopback execution active in `aurex/local_inference.py`.

---

## 2. Integration Baseline Requirements

To connect Onyx correctly to AUREX, DISPATER, and XAELI without compromising governance:
1. Implement `aurex/integrations/onyx.py` as a fail-closed knowledge retrieval adapter (`OnyxKnowledgeAdapter`).
2. Enforce strict server-side tenant isolation (`tenant_id` scoping) on all queries.
3. Link all retrieved document passages to original SHA-256 document digests.
4. Integrate retrieval into XAELI explanation workflows with zero model self-authorization (`AUTHORITY = NONE`).
