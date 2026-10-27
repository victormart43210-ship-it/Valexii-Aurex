# DISPATER.AI — Commercial ROI & Financial Accounting Validation Framework

**Ecosystem:** VALEXII.AI / AUREX-OX Execution Engine
**Module Reference:** `aurex/dispater_intelligence.py` & `aurex/dispater_pilot.py`

---

## 1. Six Strictly Separated Financial Categories

To prevent misleading or inflated commercial claims, DISPATER strictly enforces 6 non-overlapping financial categories:

1. **Potential Revenue Exposure:** Estimated financial variance detected by automated reconciliation rules before human review.
2. **Analyst-Confirmed Discrepancies:** Discrepancies reviewed and verified as genuine operational exceptions by an authorized human analyst.
3. **Customer-Approved Corrections:** Financial adjustments formally approved by customer management and authorized for billing correction.
4. **Actual Recovered Revenue:** Cash or credit adjustments collected and verified against bank/ERP accounting records.
5. **Operational Savings:** Administrative labor hours saved through automated ticket and invoice reconciliation.
6. **Estimated Return on Investment (ROI):** Calculated net value derived from user-supplied operational assumptions.

> **CRITICAL RULE:** Category 1 (Potential Revenue Exposure) is NEVER classified or advertised as Category 4 (Actual Recovered Revenue).

---

## 2. Sensitivity Scenarios & Formulae

$$\text{Monthly Evaluated Revenue} = \text{Monthly Job Volume} \times \text{Average Ticket Value}$$

$$\text{Revenue At Risk} = \text{Monthly Evaluated Revenue} \times \text{Estimated Leakage \%}$$

$$\text{Monthly Admin Savings} = (\text{Job Volume} \times \text{Admin Hrs/Job} \times \text{Automation Rate}) \times \text{Hourly Labor Rate}$$

### Scenario Models:
- **Conservative Scenario:** 1.5% Revenue Leakage, 40.0% Admin Automation Rate.
- **Baseline Scenario:** 3.5% Revenue Leakage, 65.0% Admin Automation Rate.
- **Optimistic Scenario:** 5.0% Revenue Leakage, 80.0% Admin Automation Rate.

---

## 3. Financial Precision & Integrity Controls

- **Decimal Arithmetic:** All monetary calculations use `Decimal` with `ROUND_HALF_UP` precision to prevent floating-point rounding errors.
- **Audit Event References:** Every financial discrepancy links to an immutable audit event reference (`AUDIT-EXC-XXXX`).
- **Human Approval Boundary:** Automated rules generate exception queues; financial posting requires explicit human authorization (`AUTHORITY = NONE` for AI models).
