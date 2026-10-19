# KUSANAGI CIV — ORCA R8 → AUREX → owner-only website status

**Source candidate only; no merge, secret change, DNS change, Railway deploy, Lovable
credit spend, Cloudflare publish or laptop execution performed. Release HOLD.**

## Verified boundaries at implementation time

- Owner screenshot showed **local** `localhost:8769`, R8 private harvest, 38/84
  batches, 1,088 selected rows remaining. A screenshot cannot establish a live
  machine-readable checkpoint, a network route, or correctness of records.
- Railway currently deploys the **older read-only five-GET bridge**, not canonical
  `aurex/api.py`. Production has pending changes; a volume is **staged-create**.
- Lovable has a newer published-project source than historical GitHub `website/`.
  The new GitHub owner panel is a **migration candidate only**: do not overwrite the
  newer Lovable source or assume site publication.
- No API route on a personal laptop is exposed. No extra Lovable credits used.

## Data flow

```
Existing ORCA R8 local job [not accessed by this work]
  └─ required: an owner-reviewed SAFE JSON counters-only export to local file
       └─ workstation/orca_r8_publisher.py (--once or explicit --follow)
          outbound HTTPS POST; AUREX_ORCA_PUSH_TOKEN (write-only)
             └─ canonical backend /v1/orca/r8/status
                strict Pydantic allowlist, <=2 KiB; replay/clock gates
                one SQLite latest-status row (unverified)
                   └─ HTTPS GET with separate AUREX_SERVICE_TOKEN
                      website server function + authenticated owner UUID
                         └─ private AUREX console ORCA panel
```

This is **status observation**, not a verification of private evidence.
Never send corpus files, filenames, paths, tax records, case contents, prompts,
credentials, full R8 logs or row samples in the status file. The UI cannot assign
independent PASS or production authority. Fresh stored status = `OBSERVED`;
after 120s without fresh delivery = `STALE`.

## Strict status file format

Illustrative **synthetic** example; do NOT treat these values as current:

```json
{
  "sourceId": "orca-r8",
  "runId": "r8_run_example_001",
  "sequence": 1,
  "observedAt": "2026-10-19T03:00:00Z",
  "status": "RUNNING",
  "completedBatches": 38,
  "totalBatches": 84,
  "rowsRemaining": 1088,
  "etaSeconds": 6180,
  "checkpointAgeSeconds": 83
}
```

The `observedAt` value **must be fresh** (not older than 10 min or >1 min in
the future), timezone-aware and generated from the real exporter when it observes
state. The `sequence` must increase for every update; different `runId` may
replace latest state only if observation time is newer. `COMPLETED` is only
accepted with all batches completed. Extra fields are rejected.

The existing ORCA R8 localhost UI's export/status route is **unknown** and was
not probed. Before real use, inspect its code privately on the laptop, implement
a simple *local file writer* that emits ONLY the schema above from actual
checkpoint state, and test it in offline mode. Never copy private corpus content
to a GitHub issue or Lovable prompt.

## Backend setup (after owner-approved staging, not automatic)

On the **canonical** backend, with a persistent owner-approved SQLite volume:

```
AUREX_DB_PATH=/data/aurex_jobs.db
AUREX_ORCA_SYNC_ENABLED=1
AUREX_ORCA_PUSH_TOKEN=<unique randomly generated 32+ char secret>
AUREX_SERVICE_TOKEN=<different 32+ char server-to-server read token>
AUREX_ENABLE_OFFLINE_LAB=0
AUREX_BUDGET_USD=0
```

Generate secure unique tokens locally with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`.
Only variable *names* go in docs; never commit token values.
Configure the `AUREX_SERVICE_URL` and `AUREX_SERVICE_TOKEN` only in the
website's **server secrets** (not `VITE_`), and the canonical
`AUREX_OWNER_USER_ID` as before. The ingest token belongs **only** on the
laptop and backend, never Lovable browser/client, source or public API.

The disabled-by-default push endpoint returns 503. The enabled GET endpoint
requires existing canonical service auth. The POST endpoint accepts only the
dedicated push token. This separation should also be tested to confirm keys
are different before production enablement. Protect the service with rate
limiting / WAF where applicable; SQLite latest-row writes assume one writer.

## Laptop execution (NOT RUN)

From the canonical checkout after dependency installation:

```bash
python -m workstation.orca_r8_publisher --status-file /path/to/orca-status.json --dry-run
# Only after staging backend and private counter export are verified:
export AUREX_ORCA_SYNC_URL=https://your-owner-approved-aurex-api-host.example
export AUREX_ORCA_PUSH_TOKEN=<set privately, never paste in chat or logs>
python -m workstation.orca_r8_publisher --status-file /path/to/orca-status.json --once
# After safe updates are operational, optional explicit continuous upload:
python -m workstation.orca_r8_publisher --status-file /path/to/orca-status.json --follow --interval 30
```

The script never binds a port, opens a public tunnel, or reads documents.
Status files must be tiny regular JSON files, not symlinks. Upload attempts
are HTTPS-only, no redirects, and limited to the allowlisted counters.
This does not automatically discover, start, or control the ORCA job.

## Required verification before *any* live connection claim

1. Independent review of exact PR SHA and all changed files; detect source
   leakage, token reuse, malformed JSON, replay, unsupported timestamp, forged
   Content-Length, overlarge streamed response, cancellation and owner bypass.
2. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_orca_r8_sync.py`;
   `ruff check aurex/orca_r8_sync.py workstation/orca_r8_publisher.py
   tests/test_orca_r8_sync.py`; `mypy aurex`; existing full regression suite.
3. Docker staging run from the exact SHA; ensure persistent `/data` and
   non-root identity. No action on Railway's existing four staged changes.
4. Authorized synthetic status only: check unauthorized POST/GET => 401;
   wrong tokens => 401; oversized/extra fields => 413/422; stale/read order =>
   `STALE`/409; owner authenticated website read => counters + `NOT VERIFIED`.
5. Separately review the **newer Lovable source** and cherry-pick/adapt only
   the owner server function and component, using previously-approved credit
   limits; test unauthorized owner path, tests, typecheck and build, then publish
   only with explicit owner release consent.
6. Prove Cloudflare-to-Railway source and request attribution, and record both
   exact source and deployed SHAs. No live status until authenticated requests
   and actual workstation checkpoint export have both been demonstrated.

### Current evidence statuses

- Github source branch: PRESENT after connector writes.
- Offline test *file authored*: PRESENT. Test run: **NOT RUN**.
- Laptop exporter adaptation and execution: **NOT VERIFIED**.
- Canonical backend active on Railway: **NOT DEPLOYED**.
- Owner panel present on actual live Lovable site: **NOT DEPLOYED**.
- Cloudflare-to-Railway status route: **NOT VERIFIED**.
- Independent corpus verification: **NOT VERIFIED**.
- Production effect/authority: **NONE**; **HOLD**.

Owner source of truth remains one GitHub AUREX repository; no second repository,
no self-certification, and no automatic promotion of workstation reports to
security conclusions.
