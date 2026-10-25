# DISPATER Synthetic Towing Audit Commercial Demonstration Script

Date: October 25, 2026
Platform: DISPATER.AI / AUREX Industrial Audit Intelligence Engine
Dataset: 100% Fictional Towing & Recovery Records (Permian Recovery Services)

---

## 1. Demonstration Objective

Demonstrate an end-to-end synthetic towing audit workflow for prospective fleet operators and insurers. The demonstration showcases:
1. Intake of synthetic tow jobs, rate schedules, invoices, and vehicle compliance files.
2. Automated discrepancy detection (unbilled jobs, rate table mismatches, partial payment status).
3. Record readiness checks (expired DOT vehicle inspection records).
4. XAELI findings and explanations (NOW, CHANGED, NEXT, WHY, PROOF).
5. Human review decisions (Acknowledge, Dispute, Refer to Specialist) with persistent review state.
6. Generation of exportable audit reports and self-issued cryptographic receipts.

---

## 2. Step-by-Step Execution Script

### Step 1: Open DISPATER Dashboard
- Navigate to `https://valexii.com/dispater`.
- Verify clear labeling: "Developmental / Industrial intelligence — Fictional Data — Not Live".

### Step 2: Select Synthetic Towing Packet
- Click **Towing & Recovery (Synthetic)** preset.
- Observe pre-loaded synthetic job records (`TOW-100`, `TOW-101`), invoice (`INV-100`), payment (`PAY-100`), and vehicle compliance document (`D-1`).

### Step 3: Initiate Authenticated Audit
- Click **Execute Audit**.
- Server sends authenticated job request to `/v1/industrial/audit/demo` or `/v1/jobs`.

### Step 4: Inspect Discovered Audit Findings
Observe 5 flagged findings across REVENUE and RECORD_READINESS domains:
1. `UNBILLED_JOB`: Job `TOW-101` completed on 2026-10-21 has no associated invoice.
2. `RATE_MISMATCH`: Invoice `INV-100` ($150.00) differs from contracted rate table ($180.00).
3. `PAID_STATUS_UNRECONCILED`: Payment `PAY-100` ($140.00) does not match invoice `INV-100` ($150.00).
4. `EVIDENCE_MISSING_OR_EXPIRED`: Inspection document `D-1` for `TRUCK-5` expired on 2026-09-01.
5. `EVIDENCE_MISSING_OR_EXPIRED`: Receipt index requirement requires human verification.

### Step 5: Execute Human Manager Review
- For `UNBILLED_JOB`, click **Acknowledge** and attach note: "Fictional dispatcher notified to generate invoice".
- Observe updated counts: Reviewed 1 / Total 5. Status remains `AUTHORITY: HOLD`.

### Step 6: Verify Cryptographic Audit Receipt
- Click **Verify Receipt Integrity**.
- System compares SHA-256 evidence digest against `self_issued_receipt_sha256`.
- Result displays: `Receipt digest matched. Audit evidence integrity confirmed (Self-Issued)`.

---

## 3. Mandatory Governance & Legal Boundaries

- **Fictional Data Only:** No actual customer data, driver PII, or vehicle numbers are accepted or processed.
- **No Automatic Financial Adjustments:** Findings provide decision support only. No payments, dispatch changes, or bank transactions occur.
- **Release Authority:** `PRODUCTION RELEASE = HOLD`.
