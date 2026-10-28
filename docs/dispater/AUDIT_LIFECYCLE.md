# DISPATER.AI Audit Lifecycle & Governance Enforcement

**Platform:** DISPATER.AI
**Governance Infrastructure:** AUREX-OX
**Date:** October 2026
**Status:** SPECIFICATION & AUDIT LIFECYCLE REFERENCE
**Release Authority:** HOLD

---

## 1. Complete Industrial Audit Lifecycle

DISPATER.AI enforces a strict 9-stage continuous audit and monitoring lifecycle for all operational records across oilfield, towing, flowback, and facility operations.

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 1. Operational Record   │ ──► │ 2. Continuous           │ ──► │ 3. Discrepancy &        │
│    Ingestion (Pydantic) │     │    Monitoring Event     │     │    Rule Evaluation      │
└─────────────────────────┘     └─────────────────────────┘     └────────────┬────────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 6. XAELI 5-Step         │ ◄── │ 5. AUREX Evidence       │ ◄── │ 4. Audit Finding        │
│    Explanation          │     │    Ledger Registration  │     │    Generation           │
└────────────┬────────────┘     └─────────────────────────┘     └─────────────────────────┘
             │
             ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 7. Corrective Action    │ ──► │ 8. Remediation          │ ──► │ 9. Independent Retest   │
│    Assignment           │     │    Evidence Submission  │     │    & Verified Closure   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Stage Details & Requirements

### Stage 1: Operational Record Ingestion
- **Contract:** `OperationalRecord`
- **Fields:** `record_id`, `tenant_id`, `source`, `timestamp`, `payload`, `content_sha256`.
- **Requirement:** Cryptographic SHA-256 content digest computed immediately upon intake.

### Stage 2: Continuous Monitoring Observation
- **Contract:** `MonitoringObservation`
- **Fields:** `observation_id`, `tenant_id`, `record_ids`, `observed_at`, `observation_type`, `severity`, `details`, `evidence_sha256`.
- **Requirement:** System records immutable observation event in memory and SQLite backing store.

### Stage 3: Rule Evaluation
- **Contract:** `AuditRule`
- **Rules Evaluated:**
  1. `RULE-INSP-MISSING`: Mandatory daily pre-job safety inspection check (`CRITICAL`).
  2. `RULE-OPER-DISCREPANCY`: Telemetry vs reported operating hours mismatch (`HIGH`).
  3. `RULE-REMEDIATION-OVERDUE`: Overdue corrective action item check (`HIGH`).
  4. `RULE-DATA-QUALITY`: Digest and schema integrity check (`MEDIUM`).

### Stage 4: Finding Generation & Classification
- **Contract:** `AuditFinding`
- **Fields:** `finding_id`, `rule_id`, `tenant_id`, `severity`, `title`, `description`, `source_record_ids`, `evidence_sha256`, `status`, `assigned_owner`, `audit_event_ref`.
- **Initial Status:** `OPEN`.

### Stage 5: AUREX Evidence Ledger Registration
- **Contract:** `EvidenceEnvelope` (`aurex/evidence.py`)
- **Requirement:** Stores timestamped evidence envelope with claims and `content_sha256` digest in AUREX ledger.

### Stage 6: XAELI 5-Step Grounded Explanation
- **Contract:** `Xaeli5StepFinding` (`aurex/dispater_intelligence.py`)
- **Structure:**
  - **NOW:** Operational audit finding statement and severity level.
  - **CHANGED:** Discrepancy delta across involved source records.
  - **NEXT:** Recommended human action for remediation and independent retest.
  - **WHY:** Governing regulatory or operational rule reference.
  - **PROOF:** Cryptographic SHA-256 digest and audit event reference.

### Stage 7: Corrective Action Assignment
- **Contract:** `CorrectiveAction`
- **Fields:** `action_id`, `finding_id`, `tenant_id`, `assigned_to`, `due_date`.
- **Status Transition:** Finding status transitions from `OPEN` to `ASSIGNED`.

### Stage 8: Remediation Evidence Submission
- **Contract:** `CorrectiveAction`
- **Fields Updated:** `remediation_notes`, `remediation_evidence_sha256`, `retest_status="INDEPENDENT_RETEST_REQUIRED"`.
- **Status Transition:** Finding status transitions from `ASSIGNED` to `REMEDIATED`.

### Stage 9: Independent Retest & Verified Closure
- **Governance Safeguard:** Critical and High severity findings (`CRITICAL`, `HIGH`) **CANNOT be closed automatically by AI models or unverified scripts**.
- **Requirement:** Explicit human reviewer signature (`closed_by_human`) and an independent retest record must be provided.
- **Status Transition:** Finding status transitions from `REMEDIATED` to `CLOSED`.

---

## 3. Negative Security Assertions

1. **Unauthorized Self-Closure Prevention:**
   - Attempting to invoke `execute_independent_retest` on a `CRITICAL` or `HIGH` finding with `closed_by_human=None` raises a `PermissionError` / HTTP 403 Forbidden.
2. **Missing Retest Evidence:**
   - Retest fails if no retest record or invalid digest is submitted.
3. **Digest Tampering Detection:**
   - Mismatch between stored payload and recomputed SHA-256 digest triggers a `RULE-DATA-QUALITY` finding (`FND-QUAL-*`).
