# DISPATER.AI — End-to-End Synthetic Commercial Demonstration Script

**Ecosystem:** VALEXII.AI / AUREX-OX
**Test File Reference:** `tests/test_dispater_e2e_workflow.py`

---

## Demonstration Workflow ($500 Equipment Hour Discrepancy Scenario)

1. **Document Intake & Extraction (`aurex/dispater_documents.py`):**
   - System ingests synthetic CSV field ticket `FT-E2E-101` for $3,000.00 (12 equipment hours @ $250/hr).
   - Generates SHA-256 document digest and page-level field provenance.

2. **Cross-Document Reconciliation (`aurex/dispater_intelligence.py`):**
   - Ingests customer invoice `INV-E2E-101` billing $2,500.00 (10 equipment hours @ $250/hr).
   - Reconciles ticket against invoice, PO `PO-E2E-100`, and rate sheet `RIG-HR` ($250/hr).
   - Detects `MULTI_RECORD_DISCREPANCY` exception ($500.00 unbilled equipment exposure).

3. **XAELI 5-Step Explanation:**
   - **NOW:** Operational Exception [MULTI_RECORD_DISCREPANCY]: Exposure $500.00 USD.
   - **CHANGED:** Discrepancy detected across source records: FT-E2E-101, INV-E2E-101.
   - **NEXT:** Audit underlying field tickets and align invoice line items.
   - **WHY:** Invoice header total does not equal sum of underlying field ticket subtotals.
   - **PROOF:** SHA-256 Digest & Audit Ref `PILOT-AUDIT-BATCH-E2E-01`.

4. **Human Review & Revenue State Transition (`aurex/dispater_pilot.py`):**
   - Operations Manager reviews exception queue.
   - Manager submits decision `APPROVED_CORRECTION` with approved adjustment $500.00.
   - System updates actual recovered revenue from $0.00 to $500.00 USD while keeping potential exposure category distinct.
