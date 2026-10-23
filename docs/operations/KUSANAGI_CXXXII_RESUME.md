# KUSANAGI CXXXII — checkpoint 001: schema admission guard

## Where Work left off
Resume from CXXIX PR #118 @ `6adc1936d09534b134182e769f88fea9c5a0125a` (439 locally reported passing, one skipped; queued 100-case fictional audit persisted locally). Canonical main remains separate. This CXXXII branch is an intentionally isolated continuation, not a merge or deploy.

## Actual execution performed
Read-only provider inspection: Railway staging `aurex-api` is SUCCESS at commit `d22e06e9412a07e06ab8bd597e0e5ebf5b8c125c`, build root `/integrations/kusanagi-xvi/backend`, boot -> supervisor -> backend.app. Production still uses `57a079f93b947594f1a6f854aa46a6f606f86f76`. No Railway, production, Lovable or database mutation performed.

Inspected real source layouts:
- Canonical `aurex/database.py`: `jobs.params_json`, `evidence_records`, owner-token financial receipt.
- Legacy `integrations/kusanagi-xvi/backend/store.py`: `jobs.params`, `evidence`, `workers`.
Blindly starting canonical code against legacy SQLite could damage or fail on existing data. Added `aurex/staging_schema_preflight.py` (source-only) to classify quiescent, isolated SQLite snapshots. It refuses missing/unsafe/WAL/mixed/unrecognized files and always returns release HOLD. It NEVER creates/migrates database, never establishes environment isolation.

Local isolated test (not full repo CI): `python -m pytest -q tests/test_cxxxii_staging_schema_preflight.py` → **6 passed**. Python compileall PASS. Ruff **NOT RUN** in this container. Do not extrapolate these tests to full backend compatibility.

## Admission gates remaining
The provider reports the same project-level logical Railway volume ID in staging and production. Railway documentation distinguishes per-environment volume instances; the connector did not expose instance IDs, and backup/restore remain NOT VERIFIED. Source changes are not deployed. Staging writes and release remain HOLD.

Next: reconcile canonical financial worker into actual Railway boot/supervisor with explicit isolated DB/migration semantics, test actual entrypoint with disposable SQLite, independently verify storage/rollback, then integrate owner-only website bridge. Stage deployment only after exact-head CI and safety review; do not invoke Railway accept-deploy without user's confirmation.

## Recovery
Fetch this branch HEAD and PR (to be opened), inspect exact source, consult CXXIX and CXXXI changes. Update manifest each checkpoint, commit/push and remotely read back. The JSON cannot contain its enclosing Git SHA. No production deploy, real documents, paid model inference, payment authority or main merge.

## Checkpoint 002 — verified CI and critical source convergence blocker

Remote checkpoint 001 commit `fdc80e29c5d438778884591f0a82a0faef13051a` was read back through GitHub. GitHub Actions run `39881783231` on that exact SHA completed successfully: **445 passed, 1 skipped, 1 warning**, Ruff PASS, MyPy PASS (77 source files). Canonical Railway image smoke `39881783210` PASS and independent practice runner `39881783213` PASS. These do not test the actual staging service.

Read-only Railway health inventory showed the existing staging deployment ONLINE, 1/1 replicas, 0 provider warnings/criticals. No live financial audit executed.

**Source convergence blocker confirmed:** `integrations/kusanagi-xvi/backend/supervisor.py`, `boot.py`, `store.py`, and `worker.py` exist at the deployed CXXVIII staging commit `d22e06e...` but are absent from CXXIX PR #118's source tree. The CXXIX tree instead contains the older document-candidate read-only bridge. Before integrating, compare and reconcile BOTH source histories; do not blindly copy the new `aurex/api.py` module into the existing Dockerfile or overwrite CXXVIII startup.

Next safe action: implement a versioned, local staging runtime with CXXVIII's actual boot/supervisor and CXXIX canonical queued financial engine using an isolated disposable SQLite database. Preserve existing owner routes; run source Docker smoke tests and migration/rollback checks. Obtain actual environment-specific volume instance and backup evidence before staging writes. Deploy only after explicit Railway staged-change confirmation and independent review.

No Railway environment, production, website, data, or secrets were modified.
