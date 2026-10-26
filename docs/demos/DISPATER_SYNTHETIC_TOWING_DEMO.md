# DISPATER.AI Commercial Synthetic Towing Audit Demo

## Overview
This document describes the reproducible demonstration procedure for a prospective towing & recovery customer using synthetic records.

## Demo Scenario: Permian Recovery Services (Fictional)
Permian Recovery Services submits fictional operational records covering CDL driver qualification, vehicle brake/rigging inspections, winch maintenance logs, and heavy recovery service tickets.

### Step 1: Towing Audit Dashboard & Record Selection
1. Open the DISPATER dashboard at `/dispater`.
2. Select the **Commercial Towing Field Record Audit** console.
3. Choose the target synthetic records:
   - `demo-driver-01`: CDL Driver Qualification & Medical Certificate
   - `demo-vehicle-01`: Heavy Wrecker Annual Inspection (Expired)
   - `demo-maint-01`: Winch Pressure Log Copy A
   - `demo-maint-02`: Winch Pressure Log Copy B (Conflicting Digest)
   - `demo-ticket-01`: Service Ticket #9042 (Unverified Source Hash)

### Step 2: Authenticated Audit Execution
Click **Initiate Authenticated Audit**. The frontend submits the validated synthetic selector to `POST /v1/industrial/audit/demo`.
- Real execution state transitions from `SUBMITTING` → `AUDITING` → `COMPLETED`.

### Step 3: XAELI Evidence Findings Review
AUREX returns 5-step XAELI findings:
1. **NOW**: Category inventory (`driver_qualification`: PRESENT_NOT_VERIFIED, `vehicle_inspection`: EXPIRED, `maintenance`: CONFLICTING, `service_ticket`: NOT_VERIFIED, `incident_register`: MISSING).
2. **CHANGED**: Snapshot delta (`NOT_VERIFIED_NO_PRIOR_SNAPSHOT`).
3. **NEXT**: Mandatory actions (`HUMAN_REVIEW_REQUIRED`).
4. **WHY**: Bounded synthetic reasoning scope explanation.
5. **PROOF**: Evidence ledger verification status.

### Step 4: Human-in-the-Loop Review Controls
The human reviewer reviews each category finding and logs decisions:
- Accept
- Reject
- Request Additional Evidence

### Step 5: Report & Verifiable Cryptographic Receipt
The system generates a summary report and an Evidence Ledger Receipt ID (e.g., `rcpt-towing-20261025`).
The reviewer inputs the Receipt ID into the Verification Tool to confirm:
- Verifier identity (`AUREX-OX-CUSTOS-V1`)
- SHA-256 evidence digest integrity
- Receipt status (`VERIFIED`)
