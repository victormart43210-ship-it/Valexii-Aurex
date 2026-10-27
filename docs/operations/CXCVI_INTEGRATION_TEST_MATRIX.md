# OPERATION KUSANAGI CXCVI — INTEGRATION TEST MATRIX

**Ecosystem:** VALEXII.AI / AUREX-OX / DISPATER.AI / XAELI
**Base Commit:** `1c05a95f9c8a54854d31657c315864d93931d848`
**Working Branch:** `jules/kusanagi-cxcvi-sovereign-convergence`

---

## 1. Integrated Security & Functional Test Matrix

| Area | Scenario / Attack Vector | Execution Test Command | Expected Result | Gate Status |
| --- | --- | --- | --- | --- |
| **Document Security** | Malformed / Oversized PDF file ingestion | `pytest tests/test_dispater_e2e_workflow.py` | Rejected fail-closed with `FAILED_OVERSIZED` or malformed error status | PASS |
| **Document Security** | Formula injection in CSV input (`=SUM(...)`) | `pytest tests/test_dispater_pilot_journey.py` | Sanitized to `'=SUM(...)` before CSV processing | PASS |
| **Financial Correctness** | Fixed-decimal rounding vs floating point | `pytest tests/test_dispater_operational_intelligence.py` | `Decimal` `ROUND_HALF_UP` precision enforced across all rules | PASS |
| **Financial Correctness** | Category separation (Potential vs Recovered) | `pytest tests/test_dispater_e2e_workflow.py` | Potential exposure remains distinct from confirmed recovered revenue | PASS |
| **Tenant Isolation** | Cross-tenant decision recording attempt | `pytest tests/test_dispater_pilot_journey.py` | `ValueError` raised fail-closed; 0 cross-tenant leaks | PASS |
| **Tenant Isolation** | Sibling tenant identifier collision | `pytest tests/benchmarks/dispater/test_2000_case_commercial_challenge.py` | 0 tenant leaks across 2,000 challenge cases | PASS |
| **AI Security** | Prompt injection requesting secret keys | `pytest tests/test_local_inference.py` | Returned response is unverified evidence; `authority_granted = False` | PASS |
| **AI Security** | Unauthorized financial payment instruction in prompt | `pytest tests/test_local_inference.py` | `authority_granted` remains strictly `False` (`AUTHORITY = NONE`) | PASS |
| **AI Security** | Inference provider timeout / unavailability | `pytest tests/test_local_inference.py` | Catches `LocalInferenceError` and fails closed to local fallback | PASS |
| **Workflow Correctness** | 8-stage customer pilot journey | `pytest tests/test_dispater_pilot_journey.py` | Auditable state transitions from Onboarding to Recovery | PASS |
| **Website Presentation** | Server proxy token authentication & freshness | `bun test src/components/aurex-wave2.test.ts` | Invalid token / clock skew >60s rejected | PASS |

---

## 2. Benchmark Summary

- **1,000-Case Revenue Benchmark:** `tests/benchmarks/dispater/test_1000_case_revenue_benchmark.py` (1.0 Precision, 1.0 Recall, $887.5k exposure)
- **2,000-Case Adversarial Challenge:** `tests/benchmarks/dispater/test_2000_case_commercial_challenge.py` (1.0 Precision, 1.0 Recall, $4.6M exposure, 0 leaks)
- **End-to-End Demonstration Test:** `tests/test_dispater_e2e_workflow.py` ($500 equipment hour discrepancy workflow)
