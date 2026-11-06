# CCLXIX backend report

Code SHA `44b30cb68269e4a36e7edac3a4773b5b095ae7ef`.

`POST /v1/dispater/observations` accepts a tenant-scoped observation and calls `aurex.ascendancy.proposal.propose`. The response keeps effect `NONE`, financial authority `NONE`, and launch `NOT_STARTED`. A body that asks for `DEPLOY` is recorded as `REFUSED`. Empty counterevidence abstains. An observation older than 24 hours is refused as stale. Another tenant receives HTTP 403. The observation is not written as a financial run.

The existing history and export routes were already present. The website now calls `GET /v1/dispater/runs` with limit 8 and `GET /v1/dispater/runs/{run_id}/export`. The adapter rejects a mismatched tenant, a mismatched run id, a count that does not match the list, and receipt authenticity `FAIL`.

Commands:

- `python3 -m pytest -q`: 776 passed, 1 skipped, in 9.15 seconds.
- `python3 -m ruff check .`: pass.
- `python3 -m mypy aurex`: pass, 111 files.
- Golden ledger: identified 385.00, withheld 150.00, confirmed 0.00.

An in-process TestClient measured a mean of 0.0036 seconds across 20 identical reconciliation posts after one warmup. That figure is local process time for a repeated synthetic payload. It is not deployed latency, throughput, or memory use.

`dispater-web` `node --test tests/*.test.mjs`: 25 passed. Docker was not run in this environment.
