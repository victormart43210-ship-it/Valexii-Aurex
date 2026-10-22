# KUSANAGI CXXVI — PIPELINE REPAIR / ADMISSION GATE

Date: 2026-10-22. **NO MERGE, NO DEPLOY, NO PAID INFERENCE.**

## Proven bottleneck
Railway `VALEXII-AUREX` production `aurex-api` is healthy but its source is
`integration/kusanagi-xvi-railway@57a079f93b947594f1a6f854aa46a6f606f86f76`,
root `/integrations/kusanagi-xvi/backend`, Dockerfile `Dockerfile`.
It deploys a separate *read-only bridge*, version `1.0.0-readonly`. The website's
five GET checks succeed but **GET /v1/jobs is empty by construction**. It does
not execute an audit, cannot return a result or use NVIDIA. The canonical
`aurex.api` on `main@df0654390049118a142ec3b3356f0f40b4789fe4` has
a SQLite worker and a disabled-by-default fixed offline roundtrip probe,
but its source is NOT what production Railway currently builds.

**Do not interpret 5/5 read-only GET checks as a working financial AI pipeline.**

## Implemented on isolated branch (base exact main SHA)

- `aurex/pipeline_receipts.py` and authenticated
  `GET /v1/jobs/{jobId}/receipt`: owner-readable **local observation** and
  SQLite evidence digest, requiring successful fenced job, matching linked
  receipt, fixed probe type, exact strict fields, recorded integrity and
  unverified status. Corruption, missing or cancelled jobs return fail-closed
  error; observation is not an independent witness or financial authorization.
- `website/src/lib/aurex-api-schema.ts`, `website/src/lib/aurex-client.server.ts`
  and OpenAPI: typed server-only readback, deliberately no public browser
  server function or consumer-data ingestion.
- Python unit/integration tests exercise bearer auth, 1-step idempotent replay,
  worker→SQLite→evidence→receipt, deliberate SQL/evidence corruption,
  untrusted observation fields, $0 and default-off probe.
- `Dockerfile.aurex` packages the **canonical** app from the repository root
  with non-root UID, persistent `/data` path, both execution flags off.
- `.github/workflows/cxxvi-pipeline.yml` checks Python tests, website schema
  tests, builds a disposable Docker image and asserts 401 missing auth and
  503 default-off worker.

## What remains blocked

1. **Deploy source**: Railway still points at legacy `/integrations/kusanagi-xvi/backend`.
   This branch does NOT alter Railway configuration or replace the healthy service.
2. **Synthetic financial engine**: candidate PR #104, not on main, contains a
   gated fixed 100-case fictional job. Incorporate separately after independent
   review of dependency/lease semantics. This branch's receipt schema is ready
   to display its bounded *fictional* summary, not ingest real customer files.
3. **Document/NVIDIA**: candidate PRs #106 / #107 are NOT deployed. Their
   provider budget must remain $0 and efficacy remains NOT VERIFIED.
4. **Frontend owner action**: deployed Lovable /admin/sovereign-studio is
   currently fictional-local. It must not expose a Run Backend Audit button
   until a production/staging candidate supports POST and owner-only auth is
   independently tested, including no browser secrets and real receipt binding.
5. **Production database**: mounted Railway volume `/data` exists, but deploy
   plan must verify backups, permissions, migration, rollback and same-path
   SQLite writes before changing service root/build/start command.
6. **CXXIV**: no integration branch observed. Resolve collisions with
   #104/#106/#107/#108 before admitting any combined integration.
7. **Validation**: recorded receipt digest = storage consistency, not third-party
   financial accuracy; no automatic payments, trades or customer fraud verdicts.

## Roll-forward plan (NOT performed)

After independent review & successful CI, stage isolated canonical container
(`Dockerfile.aurex` from repo root, Python 3.12, `uvicorn aurex.api:app`)
under controlled environment with distinct credentials and disposable/isolated
volume. Keep `AUREX_ENABLE_OFFLINE_LAB=0`,
`AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT=0`, budget $0.
First verify 5 authenticated GETs, 401 on invalid bearer, 503 on POST,
no empty false success. Then in an approved **non-production** synthetic
test only, enable offline lab and run the fixed test probe with an
idempotency key and inspect its digest-linked GET receipt. Restore flags off,
test restart/persistence and rollback. Never send actual bank records.

No new live service or billing resources were provisioned here.

**Current production state:** read-only healthy.
**New capability source state:** candidate PR only, awaiting CI/adversarial review.
**Financial/AI model runtime:** HOLD / NOT DEPLOYED.
**Authority:** NONE; **merge/deploy:** NOT AUTHORIZED.
