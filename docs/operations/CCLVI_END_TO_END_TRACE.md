# CCLVI end-to-end trace

Synthetic data only. Tested code `bd1c4d00559bed86d4e37aab103204cf95829769`. Production HOLD. Financial authority NONE.

## 1. Data intake

- Entry: `POST` document and batch routes in `aurex/dispater_api.py`.
- Source: `aurex/dispater_ingest.py`.
- Inputs: CSV, JSON, PDF, or XLSX bytes, plus optional declared length.
- Outputs: a canonical snapshot or HTTP 400.
- Authority: no financial effect. A non-synthetic JSON `dataset_type` is refused. Unlabeled batches are stamped synthetic; that stamp is not a content check.
- Tests: `tests/test_enterprise_assurance.py`, ingest tests. Observed: declared length mismatch is rejected. XAELI live path was not used.
- Failure: oversize body, bad file, or a declared length that does not match the received bytes.

## 2. Parsing

- Source: `aurex/dispater_ingest.py` with pypdf and openpyxl.
- Inputs: received bytes.
- Outputs: rows plus `source_bytes_status: VERIFIED_RECEIVED_BYTES` and `source_identity: UNVERIFIED`.
- Authority: parsed fields are not source-file identity.
- Tests: PDF/XLSX tests from CCXXXV, still present. Scans are not treated as OCR.
- Failure: macro workbooks and image-only PDFs are rejected. OCR is not installed.

## 3. Reconciliation

- Entry: `RevenueLeakageEngine.reconcile_records` in `aurex/dispater_intelligence.py`.
- Inputs: jobs, invoices, rates, payments.
- Outputs: findings and `financial_summary`.
- Authority: identified exposure is not recovered revenue. `confirmed_recovery_usd` is `0.00`.
- Tests: `tests/test_dispater_golden_audit.py` observed identified `385.00`, withheld `150.00`, confirmed `0.00`, event separation `NO_RELATIONSHIP_EVIDENCE`. Invoice discrepancy remains `10.00` with confirmed invoice recovery `0.00`.
- Failure: ambiguous unbilled and orphan invoices are withheld. A confusable customer id is not proof of a different customer. An unequal one-to-one pair with no shared job id stays identified.

## 4. Evidence

- Source: `aurex/dispater_receipt.py`, `aurex/dispater_store.py`, `aurex/dispater_anchor.py`.
- Inputs: the report and monitor events.
- Outputs: content digest, HMAC, sidecar head, anchor checkpoint.
- Authority: a hash is not a signature. The anchor key is a second server key. `EXTERNAL_ANCHOR` remains `NOT_VERIFIED`.
- Tests: receipt and enterprise tests. Deleting rows, sidecar, and anchor together still verifies. That residual stands.
- Failure: a bad MAC fails closed. Age-based purge can leave the chain unable to verify.

## 5. Intelligence

- Source: `aurex/ox/` and the explanation fields on findings.
- Inputs: synthetic scores and the deterministic finding text.
- Outputs: labels. No change to the Decimal totals.
- Authority: model text cannot authorize money, contact, or training.
- Tests: OX registry and evaluation tests passed in the full suite. No live model response was observed.
- Failure: paid providers stay off. Empty model digests are rejected.

## 6. Persistence

- Source: `aurex/dispater_store.py`.
- Inputs: sealed report.
- Outputs: tenant-scoped rows. Identical dataset hash returns the existing run.
- Authority: reads require a verifying MAC.
- Tests: store and tenant tests in the full suite, 732 passed, 1 skipped.
- Failure: optional AES-GCM covers the report blob only. Finding columns and monitor payloads stay plaintext. A missing data key stores plaintext and says `NOT_CONFIGURED`.

## 7. API

- Source: `aurex/dispater_api.py`.
- Inputs: bearer token and tenant.
- Outputs: JSON or CSV with no-store headers. Lifecycle routes record requests and do not delete.
- Authority: cross-tenant access is 403 or 404. DELETE of a run is 405.
- Tests: `tests/test_dispater_security.py` and sovereignty tests.
- Failure: no grants configured returns 503.

## 8. Website

- Source: `website/src/routes/dispater.tsx` and `website/src/components/dispater-reconciliation-console.tsx`.
- Inputs: the API report.
- Outputs: synthetic banner, identified and withheld figures, customer-decides copy.
- Authority: the page cannot start a collection or a payment.
- Tests: Vitest 157 passed, `tsc` exit 0, production build exit 0. These files were not changed in the CCLVI commits.
- Failure: the console shows the server's `confirmed_recovery_usd` string. The schema does not force the literal `0.00`.

## 9. XAELI

- Source: `aurex/xaeli_staging.py` and `website/src/routes/xaeli.tsx`.
- Observed: staging flags unset, `AUREX_QWEN_BASE_URL` unset, `127.0.0.1:8080` raised `URLError`.
- Result: **NOT_VERIFIED**. The public page says it is scripted and is not a connected assistant. No response was fabricated.

## 10. Customer authority

- Source: `aurex/customer_sovereignty.py`.
- Observed: contact, financial action, and training reuse refuse. Confirmed recovery stays `0.00` in the probes below.
- Tests: `tests/test_customer_sovereignty.py`.
- Failure: a UI string or a model sentence is not a grant. No route in this trace sends a notice or changes an invoice.
