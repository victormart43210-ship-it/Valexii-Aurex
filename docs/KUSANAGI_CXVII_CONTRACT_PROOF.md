# KUSANAGI CXVII — AUREX SOURCE-BOUND FRONTEND/BACKEND CONTRACT AND SYNTHETIC HTTP PROBE

**Status:** DRAFT / DEVELOPMENT / RELEASE HOLD. **Canonical base:** `df0654390049118a142ec3b3356f0f40b4789fe4` from `victormart43210-ship-it/Valexii-Aurex:main`. **Owned branch:** `work/kusanagi-cxvii-contract-sqlite-proof`. **Do not merge, deploy, expose customer data, or modify the Lovable website without separate authorization and independent verification.**

## Concrete defect

The canonical FastAPI `GET /v1/capabilities` reports service IDs like `regression_scan`, `memory_graph`, and `remote_inference` (underscores). Its fenced-worker receipts use `kind=offline_probe`, `capabilityId=regression_scan`. The GitHub website's strict `CapabilitySchema` disallowed underscores and `EvidenceSchema` disallowed `offline_probe`. Thus a genuine successful backend response could be rejected as malformed. In addition, GitHub frontend client token preflight allowed 16 characters while Python requires at least 32. OpenAPI incorrectly documented job creation as HTTP 201 whereas the FastAPI route returns HTTP 200.

These are **verified source-level contract mismatches**, not evidence of current live production failure. The deployed Lovable source is separately versioned and may differ from the GitHub website source.

## Changes

1. `website/src/lib/aurex-api-schema.ts`: accept bounded underscore/hyphen capability IDs and the existing `offline_probe` evidence kind; unknown/extra fields remain rejected.
2. `website/docs/aurex-api/openapi.yaml`: align wire-value enums, ID pattern and POST /jobs HTTP 200; remain development-only, not independent host proof.
3. `website/src/lib/aurex-client.server.ts`, `website/src/lib/aurex-service.server.ts`: require 32-character bearer preflight, matching backend security floor (backend still performs constant-time comparison).
4. `website/src/components/aurex-api-schema.test.ts`: five fixture-based frontend schema checks, including invalid IDs/kinds and raw Python source contracts.
5. `tests/test_api_sqlite_contract.py`: nine backend TestClient tests for authenticated job → claim/lease → SQLite observation → SHA-linked evidence; replay/idempotency, budget, unauthorized input, worker disabled, conflicting auth tokens; plus explicit synthetic financial path.
6. Selectively copy exactly five files from existing **unmerged draft PR #99** into this isolated base branch: `aurex/field_reconciliation.py`, `workstation/field_audit_beta_gate.py`, `workstation/field_audit_beta_pipeline.py`, and the two associated test files. Original source Git blob IDs must be checked against the PR #99 head before admission. This is **not** the entire financial platform nor a new runtime; the same canonical AUREX job and evidence storage are used.
7. `aurex/api.py`: preserve existing `POST /v1/jobs` schema and add a fixed additional `regression_scan` probe `{"probe":"synthetic_field_audit_v1"}` that is only available with BOTH server-only env flags `AUREX_ENABLE_OFFLINE_LAB=1` and `AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT=1` plus a valid authenticated bearer and idempotency key. The probe accepts **NO customer uploads, prompt text, invoice amounts or arbitrary documents**. It generates the fixed 100-case fictional suite, invokes the deterministic rule engine and fixture oracle, and writes bounded result summary and SHA observation through the existing fenced worker and SQLite evidence path. The HTTP POST and status read remain within the existing website v1 job schema; this is not Qwen inference.

**Example local-only synthetic request** — NEVER run against production without an explicit bounded owner-approved scope:

```http
POST /v1/jobs
Authorization: Bearer <server-side 32+ byte secret>
Idempotency-Key: synthetic-probe-20261021-atleast16
Content-Type: application/json

{"kind":"regression_scan","params":{"probe":"synthetic_field_audit_v1"},"maxCostUsd":0}
```

Successful local synthetic observation (in server-side SQLite, **not exposed as public document data**) includes `synthetic=true`, `case_count=100`, `exact_case_matches=100`, `finding_labels=70`, `false_positive_flags=0`, `false_negative_flags=0`, `real_document_accuracy=NOT_MEASURED`, `independent_verification=NOT_VERIFIED`, `authority=HOLD`, `effect=NONE`, `production_release=HOLD`.

**Important:** 100/100 vs a transparent fictional oracle verifies *that one synthetic fixture set only*. It does not establish cross-site frontend integration, live Qwen performance, independent reconciliation accuracy, or authorization to use customer financial data.

## Validation performed

- **PASS, local actual-source verification of copied PR #99 artifacts:** 5 Git blob hashes match origin PR #99. `21 passed in 0.06s` for `tests/test_field_audit_beta_gate.py` and `tests/test_field_audit_beta_pipeline.py` (synthetic only). Running the pure function in-process against those files yielded 100 exact fictional-case matches and 70 fixture finding labels, 0 FP/FN; all results remain HOLD for production.
- **NOT RUN in this environment:** full repository `tests/test_api_sqlite_contract.py` because the connected private GitHub repository is not clonable from this environment; exact source and dependencies exist in GitHub PR but not in a complete local checkout.
- **NOT RUN in this environment:** frontend Vitest, TypeScript, build, full backend pytest/Ruff/Mypy, independent security review, real deployed site-to-backend flow, mobile rendering, Qwen. GitHub Actions may start but must be checked for actual executed steps and conclusion.
- **Independent reviewer:** NOT ASSIGNED.
- **Merge and deployment:** NONE, `main` unchanged.

Commands in the repo checkout after reviewing PR and dependencies:

```bash
git fetch origin work/kusanagi-cxvii-contract-sqlite-proof
git switch --track origin/work/kusanagi-cxvii-contract-sqlite-proof
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q \
  tests/test_api_sqlite_contract.py tests/test_field_audit_beta_gate.py \
  tests/test_field_audit_beta_pipeline.py
python3 -m ruff check aurex/api.py aurex/field_reconciliation.py \
  tests/test_api_sqlite_contract.py workstation/field_audit_beta_pipeline.py
cd website
bunx vitest run src/components/aurex-api-schema.test.ts
bun run build
```

## Remaining acceptance gates

1. **P0: GitHub hosted CI repair.** Existing GitHub Actions runs on upstream drafts have failed with no executed job steps in returned metadata; account billing/runner configuration requires owner-side investigation. Don't disable CI to conceal it. Run full backend+frontend tests on exact candidate head and obtain separate review.
2. **P0: Job-error lease lifecycle.** An exception after the worker claims a job currently returns a 503 but leaves the job in `running` until its lease expires. The negative test confirms it does NOT record success/evidence, but proper lease-fenced terminal failure and retry/recovery need a dedicated independently reviewed fix before any larger workloads.
3. **P0: Real data source integrity.** Synthetic canned JSON only. Real PDF/OCR/XLSX, formula recalculation, source signatures, scoped tenant roles, consent, insurance, backups, and security review remain unverified.
4. **P0: Documented job result presentation.** Current website v1 API returns job status and evidence receipt summaries, not the detailed persisted observation to a user UI. An owner-only, privacy-reviewed bounded result retrieval route and Lovable UI integration require a separately frozen contract. No fabricated live results on the website.
5. **P0: Lovable divergence.** Production `valexii.com` and preview use the existing Lovable project at separate commit `0cc4f81e0fa423247be834d45451ed66e1e9487b`, not this GitHub website copy. Lovable reported no workspace credits earlier. Do not claim this PR updated or published the website.
6. **P1: Qwen and G-Factor.** Draft PR #102 is a separate non-authorizing evaluator, not a trained or currently running financial model.
7. **P1: independent pen tests/reliability/timeouts, budget, failure injection and accessibility.**

**Governance:** Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness. Unknown != healthy; all financial effects NONE; release authority HOLD. **CUSTOS = HOLD.**

**Rollback:** close the new draft PR; no database migrations, secrets, cloud credentials, Lovable edits, DNS changes, billing, branch merges, deployments or customer contacts were performed.
