# DISPATER.AI — AUDIT PACKAGE SPECIFICATION
**Specification Version:** `dispater.synthetic.audit_package.v1`
**Date:** November 2026
**System:** AUREX-OX / DISPATER.AI Compliance Intelligence

---

## 1. Overview & Purpose

The Audit Package Generator (`AuditPackageGenerator` in `aurex/dispater_intelligence.py`) produces reproducible, source-linked compliance evidence binders for commercial towing and motor carrier operations.

It solves regulatory readiness by linking operational certificates, driver credentials, vehicle safety inspections, and corrective actions into a cryptographically sealed package.

---

## 2. Core Capabilities

1. **Source-Linked Document Inventory:**
   - Every document record captures `document_id`, `document_type`, `title`, `jurisdiction`, `issue_date`, `expiration_date`, and a SHA-256 content digest.
2. **Freshness & Expiration Intelligence:**
   - Evaluates expiration dates relative to target `as_of_date`.
   - Flags expired items and calculates `days_to_expiry` for forward renewal scheduling.
3. **Regulatory Requirements Cross-Referencing:**
   - Evaluates mandatory rules from FMCSA (e.g., 49 CFR 396 periodic vehicle inspections), state DOTs, and local towing authorities (e.g., TDLR).
   - Generates compliance exceptions when mandatory requirements lack unexpired supporting documents.
4. **Corrective Action Tracking:**
   - Tracks remedial assignments, responsible owners, status, and overdue flags.
5. **Reproducible Evidence Manifest:**
   - Compiles a complete SHA-256 hash list of all underlying documents and corrective action records.
   - Computes an overall immutable package hash (`package_sha256`).

---

## 3. Governance Invariants

- **Non-Delegable Authority:** Missing evidence is documented as an exception requiring human review; the engine never autonomously clears a carrier or certifies regulatory compliance.
- **Fail-Closed Storage:** Packages are saved with tenant scoping in `dispater_audit_packages` table in SQLite storage with WAL mode and foreign key constraints.
