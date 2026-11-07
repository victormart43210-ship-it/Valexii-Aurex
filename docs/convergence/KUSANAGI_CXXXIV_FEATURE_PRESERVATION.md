# KUSANAGI CXXXIV — Feature Preservation Checkpoint

**Status: requirements recorded; preservation not yet independently demonstrated.** No code was merged or changed by this checkpoint.

The consolidation audit must explicitly preserve and test the following behavior on the final exact `main` SHA:

- Canonical FastAPI service and stable API/website contracts; no competing production backend.
- Fail-closed bearer authentication, constant-time credential comparison, owner-only authority, and replay/idempotency protections.
- SQLite transaction integrity, fenced worker leases, stale-worker rejection, cancellation behavior, restart recovery, and durable evidence.
- Integrity-checked receipts, evidence provenance, and independent witness boundaries; no system self-certifies.
- Synthetic-only financial fixtures and deterministic execution; no real customer records, transactions, or paid provider calls.
- Ed25519 verification, challenger/evaluation integrity, scientific evaluation boundaries, and regression coverage.
- Optional NVIDIA/Qwen/local model adapters remain disabled unless separately authorized; practice scores are not independent benchmark claims.
- Deployment behavior is not inferred from source merge or CI; Railway staging/production volume identity and isolation remain unresolved.

## Evidence currently available

- PR #97's observed head `f44571a463ea46cd00c25bb1f672dd5fe6e9e382`: eight check runs passed, but there is no review record and this is not proof that all listed capabilities are preserved on `main`.
- PR #117 head `82d70c0da20ba5128c48c254987cb433ddae6b35`: nine observed check runs passed; draft and no review.
- PR #118 head `6adc1936d09534b134182e769f88fea9c5a0125a`: nine observed check runs passed; draft and no review.
- PR #119 head `522807e0b9b9ff5ba6e996fb4a154c0fd8455ea6`: Ruff and test failures; no review.
- PR #120 head `3e7ce03d72031e048f0101e3484f176b56b542fa`: four observed check runs passed; draft and no review.

These check results are PR-specific and do not independently establish the full preservation checklist on canonical `main`. Required follow-up: map each capability to existing tests, add/repair only evidence-backed regression coverage, and obtain an independent exact-SHA review before any merge.
