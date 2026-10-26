# OPERATION DISPATER PROOF — first runnable vertical slice

Status: CANDIDATE / REVIEW REQUIRED / PRODUCTION HOLD.

This is a deliberately small deterministic reconciliation demo with synthetic data. It is **not** a customer-ready ingestion service, a compliance determination, an independent witness, or proof of superiority over ChatGPT/Claude.

## Run locally

From repository root, using the project's existing Python environment:

```sh
python -m dispater_proof.reconcile
python -m pytest tests/test_dispater_proof.py -q
```

Inputs: `dispater_proof/fixtures/dispatches.csv` and `invoices.csv`. No credentials, external network, model downloads, paid calls, or customer records.

Output: review-only findings with per-invoice canonical JSON SHA-256. This hash establishes deterministic content identification **only**, not source authenticity, chain of custody, or independent verification.

## Follow-up gates

1. Independently run and inspect tests; record SHA and failures.
2. Add tenant-aware ingestion and security review before accepting any customer data.
3. Add original file hashes, source/version metadata, evidence persistence, idempotency and replay.
4. Add review queue with human authorization and audit receipts.
5. Benchmark against deterministic-only and LLM baselines using blinded synthetic fixtures.
6. Keep financial/regulatory authority NONE and release HOLD until separately approved.

Never claim models were fine-tuned or that the system automatically satisfies DOT/IRS rules.
