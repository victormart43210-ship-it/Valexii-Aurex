# KUSANAGI CXXVIII — Unix Worker & Python Labs

**Status:** Candidate / draft / NOT DEPLOYED. **Authority:** NONE. **Release:** HOLD.

## Scope and source

Base: PR #110 `candidate/aurex-ox-24x7-agent-20261022T162607Z` at
`53bc2fa50e4990767928752919d0be3ad3e6f8c8`.
This is an isolated *stacked* repair, not a mainline merge or production update.
Do not confuse the parallel canonical API integration in PR #109 with the older
Railway-bridge backend addressed here.

## Reliability gaps addressed

1. **Failed worker claims**: previously an exception during `store.finalize`
   could leave a `running` job and live lease until expiration. A new
   `store.fail_claim` atomically demotes only a currently held lease to
   `failed`, increments fencing generation, clears worker ID/token/lease,
   and creates no evidence. Cancelling or superseding a claim wins.
2. **Unix supervisor**: validates absolute SQLite path, bounded numeric port,
   and opt-in mounted-volume guard before launching any child. API, worker
   and observer are launched with *no shell* in separate Unix process groups;
   SIGTERM/SIGINT and child failures stop/reap all processes. A child crash
   deliberately exits service for platform restart (not fabricated health).
3. **Worker identity**: stable across process loops and unique across restarts.
   Both worker and observer remain disabled unless explicitly opted in.
4. **Python lab CLI**: `backend.lab` defaults to `STAGED / NOT RUN`; explicit
   `--execute` runs **two zero-cost, temporary SQLite tests**:
   - fixed binary SQLite round-trip, evidence SHA-256 and idempotent replay;
   - cancellation and stale-lease takeover, with expected denial for old owner.
   It does not connect to Railway, invoke NVIDIA, read real financial records,
   access production SQLite or use API keys.
5. **CI and Docker**: workflow `.github/workflows/cxxviii-unix-labs.yml`
   tests failures and forged lease states, local CLI behavior, read-only API
   auth/default-off, and a disposable container with worker and observer
   explicitly enabled. Docker smoke creates only one fixed offline probe and
   verifies matching unverified evidence. This is **not** a 24-hour uptime test.

## How to run on Chromebook (after checking out this exact branch)

```bash
git fetch origin work/kusanagi-cxxviii-unix-worker-python-labs
git switch --track origin/work/kusanagi-cxxviii-unix-worker-python-labs

python -m pip install -r integrations/kusanagi-xvi/backend/requirements.txt
python -m pip install "httpx>=0.27,<1" "pytest>=8,<10"

PYTHONPATH=integrations/kusanagi-xvi python -m backend.lab
PYTHONPATH=integrations/kusanagi-xvi python -m backend.lab --execute
python -m pytest -q tests/test_cxxviii_unix_worker_labs.py
```

No service token, provider credential or database path should be pasted into
issue comments, website code or chat. Do not run against production.

## Important non-claims / deployment gates

- PR #110's Railway candidate is not verified in production.
- A 24/7 observer records *local operations*, never independent financial
  efficacy. A successful fixed probe is NOT an invoice audit or NVIDIA run.
- Even opt-in LLM requests are separately governed; provider credentials,
  quota/spend accounting, human consent and separate service/auth controls
  require independent review before enabling. Keep
  `AUREX_LLM_ENABLED=false` and `AUREX_LLM_ALLOW_BILLING=false`.
- The observer's `running` flag is last-snapshot freshness, not proof that
  the daemon will stay running.
- For persistent Railway storage: set a private, dedicated volume at
  `/data`, `AUREX_DB_PATH=/data/aurex.sqlite3`, and
  `AUREX_REQUIRED_VOLUME=true` **only after** a staging mount exists;
  confirm uid 10001 write privileges, durability through restart and
  database backups/restore.
- A dedicated staging service/environment, no production data, rollback,
  resource limits, no secrets in browser, and explicit owner approval are
  prerequisites. No production configuration patch is authorized.
- PRs #104/#106/#107/#109 implement separate financial, document,
  NVIDIA and receipt candidates; this change does not magically combine them.
  Full source convergence and independent financial tests remain open.
- Exact CI outcomes must be checked from the completed run for the final SHA.

## CUSTOS

`UNIX WORKER FAILURE FENCING: CANDIDATE`

`TEMPORARY PYTHON LABS: CANDIDATE`

`PRODUCTION 24X7 SUPERVISION: NOT VERIFIED`

`NVIDIA INFERENCE: NOT RUN`

`REAL FINANCIAL AUDIT ACCURACY: NOT MEASURED`

`AUTHORITY: NONE`

`RELEASE: HOLD`
