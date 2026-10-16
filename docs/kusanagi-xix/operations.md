# Local operations and deployment gates

This is a review candidate, not a production release. No hosted resources were changed.

## Reproduce backend

Use Python 3.12. Create a virtual environment, then install with the tested dependency snapshot:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -c docs/kusanagi-xix/evidence/python-environment.txt -e '.[dev]'
python -m pytest -q
python -m ruff check .
python -m mypy aurex
python scripts/verify_backbone_local.py
```

The last command launches actual local API and worker processes against a temporary SQLite DB and deliberately unavailable loopback model endpoint. It verifies honest failure, NOT native Qwen success. The worker test suite also uses an explicitly synthetic loopback HTTP fixture. Neither is evidence of real inference.

## Owner-controlled local runtime

Set `AUREX_DB_PATH` to an owner-writable persistent local disk path shared by API and worker. `/tmp` is the legacy development default, not production durability. Generate a service credential of at least 32 characters outside source control. Export it as `AUREX_SERVICE_TOKEN`; do not put it in VITE variables. `AUREX_USER_TOKENS` optionally maps owner IDs to distinct server-side tokens; the browser cannot choose owner scope. These are operator-managed static credentials, with immediate revocation by configuration removal, not an expiring session-token service.

Set `AUREX_LOCAL_MODEL` to the actual installed model identity and `AUREX_LOCAL_MODEL_URL` to its literal-loopback OpenAI-compatible root, e.g. `http://127.0.0.1:8080/v1`. No model is downloaded by this package. Run:

```sh
python -m uvicorn aurex.api:app --host 127.0.0.1 --port 8000
```

In another process with the same DB configuration:

```sh
python -m aurex.worker
```

Enable submissions explicitly with `AUREX_EXECUTION_ENABLED=true` in the API environment. Only `local_inference` executes. Existing regression/benchmark kinds remain closed. The owner-authorized prompt is advisory input, never executable code or a tool command. No external tool adapters or side effects are enabled.

`/health/live` checks process availability. `/health/ready` requires valid credential configuration, DB access, execution enabled and a fresh configured worker heartbeat. It explicitly reports model NOT VERIFIED: accepting jobs does not prove the model is running. `/health/dependencies` is service-owner-only. Read-only API status survives missing model runtime. Admission requires an Idempotency-Key. Same owner/key/body repeats return the same job; changed body conflicts.

Worker leases are 30 seconds, renewed about every 5 seconds, with a monotonically increasing fence. Default job deadline is 180 seconds, up to 3 attempts; one inference subprocess is capped at 120 seconds. Cancelled or expired leases cannot finalize a result. Retries are bounded and immediate; no external effect is assumed exactly once. Failed rows retain dead-letter information. API labels preserve queued/running/succeeded/failed/cancelled/expired. Qualification is request validation/authentication; lease/verification are internal transactional stages, not new public states.

## Storage and recovery

SQLite is supported on ONE host with API and workers sharing one local durable filesystem. Do not mount a SQLite file across independent Railway hosts or network filesystems. No measured need for PostgreSQL has been established. Schema 0/1 to 2 migration is atomic and additive; ambiguous legacy idempotency duplicates fail closed and require explicit reconciliation. It was tested only on temporary fixtures. No live data was migrated.

### Tested backup command

In a trusted owner-controlled directory on Linux, create a new snapshot:

```sh
python -m aurex.backup /absolute/path/jobs.db /absolute/path/backups/jobs-new.db
```

The destination parent must already exist. The command uses SQLite online backup (including committed WAL data), validates the current schema version, integrity and foreign keys, and publishes with atomic no-overwrite semantics and mode 0600. It refuses missing sources, occupied destinations and unsupported schema versions. It never restores over a live database. Keep both directories protected; backups contain sensitive prompts and results. Filesystem access controls do not encrypt backups. The 30-second progress deadline bounds SQLite backup retries; filesystem operations and integrity checking are not a hard real-time guarantee. If publication succeeds but a later filesystem sync fails, an intact destination may remain; inspect it instead of overwriting it.

Local verification: 212 backend tests passed, 1 skipped, with the existing Starlette/httpx deprecation warning; see `evidence/backup-backend-tests.txt`. Four new real-SQLite tests cover WAL restoration with owner preservation, overwrite refusal, missing-source refusal and unsupported-schema cleanup. Ruff and strict Mypy passed (44 source files). This does not establish production RPO/RTO, evidence truth, or a live disaster-recovery exercise. Independent review of the new backup command: NOT RUN.

Before any approved live migration, stop admission, drain or fence workers, take a SQLite online backup using the standard `sqlite3.Connection.backup` API, and run `PRAGMA integrity_check` on the backup. Restore-test a copy to an isolated path; compare job/evidence IDs and digests before starting test workers. Never restore over a live database. Backups contain prompts/results and require the same access controls as the source. Actual production RPO/RTO and backup scheduling are NOT VERIFIED.

Analytics stores allowlisted event/route/device dimensions only, with 30-day default retention applied on analytics read/write. No visitor identifiers, prompts or credentials are stored there. Unique visitors and retention cohorts are not measured. Job-state counts are derived from durable job rows rather than browser assertions. API request logs contain server-generated request ID, route template, status and elapsed time, no content. Full distributed tracing and request-to-worker lineage IDs remain unimplemented. Ingress rate limiting is per process/peer (120/min, max1024 peers), not a multi-host quota; verify reverse-proxy addressing and tune before production.

## Website and release

See `website/docs/sovereign-frontend.md`. `npm ci --ignore-scripts`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build` succeed outside Lovable. The existing authenticated server bridge requires an HTTPS backend and Supabase owner configuration. Do not expose loopback model ports. No public tunnel is activated.

Railway currently has one read-only bridge service and NO persistent volume. Its deployed branch is not this candidate. Before any authorized preview: reconcile newer Lovable source, provision or approve persistence and private model connectivity, select one canonical database/worker, verify owner authentication, run native model task and outage recovery, validate restore and rollback on a copy, then obtain explicit approval for production changes. Production DNS, source branch, credentials and data stay untouched. Rollback must preserve the new schema and evidence; use a tested compatible release or stop admission, not a blind downgrade.

BCXMET boundary: advisory explanations only. No API here changes Android protection state. ORB MOTION AUTHORITY = NONE.
