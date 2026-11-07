# DISPATER.AI — FINANCIAL RECOVERY VERIFICATION MATRIX
**Scope:** U.S. Towing & Roadside Revenue Recovery Engine
**Engine File:** `aurex/dispater_intelligence.py`
**Test Verification:** `tests/test_dispater_financial_recovery.py` (10/10 PASS)
**Governance:** Production HOLD | Financial Authority: NONE | Deterministic Decimal: ENFORCED

---

## I. TOWING LIFECYCLE COVERAGE
Every financial recovery workflow follows the strictly segregated deterministic lifecycle:
`Dispatch -> Contract -> Rate -> Expected Charge -> Invoice -> Payment -> Deposit -> Finding -> Review -> Recovery`

---

## II. 10 SCENARIO TEST MATRIX & INDEPENDENT ORACLE PROOFS

| ID | Scenario Name | Detection Rule / Mechanism | Exposure Class | Expected Exposure | Confirmed Recovery | Status |
|---|---|---|---|---|---|---|
| 1 | Unbilled Completed Tow | Completed CAD dispatch ticket without generated invoice | `POTENTIAL_UNDERBILLING` | $125.00 | $0.00 | **PASS** |
| 2 | Incorrect Contracted Rate | Billed $100.00 vs active contract rate $125.00 | `POTENTIAL_UNDERBILLING` | $25.00 | $0.00 | **PASS** |
| 3 | Unbilled Storage Days | Lot retention logged 3 days at $45/day billed at $0 | `POTENTIAL_UNDERBILLING` | $135.00 | $0.00 | **PASS** |
| 4 | Incorrect After-Hours Surcharge | Night dispatch billed $50.00 vs contracted $75.00 | `POTENTIAL_UNDERBILLING` | $25.00 | $0.00 | **PASS** |
| 5 | Partial Motor Club Payment | Roadside club remitted $80.00 on $125.00 callout | `POTENTIAL_UNDERBILLING` | $45.00 | $0.00 | **PASS** |
| 6 | Duplicate Invoice | Single dispatch referenced by 2 distinct invoices | `POTENTIAL_OVERBILLING` | $125.00 | $0.00 | **PASS** |
| 7 | Missing Deposit Reconciliation | Bank deposits $400.00 vs recorded payments $500.00 | `UNVERIFIED_EXPOSURE` | $100.00 | $0.00 | **PASS** |
| 8 | Contract Amendment Effective Date | Mid-year rate amendment billed under prior tariff | `POTENTIAL_UNDERBILLING` | $30.00 | $0.00 | **PASS** |
| 9 | Disputed Charges | Customer damage claim withholding invoice payment | `UNVERIFIED_EXPOSURE` | $125.00 | $0.00 | **PASS** |
| 10 | Payment Recovery Invariant | Negative assertion: AI model cannot book cash | `CONFIRMED_RECOVERY` | Locked at $0.00 | $0.00 | **PASS** |

---

## III. NON-DELEGABLE FINANCIAL RECOVERY SEPARATION
The engine strictly enforces separate financial state categories:
1. `potential_underbilling_usd`: Discovered revenue opportunity; candidate for invoice creation or appeal.
2. `potential_overbilling_usd`: Billed amounts exceeding contracted schedules; candidate for credit memo.
3. `unverified_exposure_usd`: Suspense items, orphan documents, or unapplied cash receipts.
4. `confirmed_recovery_usd`: Guaranteed at `$0.00` until counter-party remittance and human validation.
