# XIX analytics storage

Implemented `aurex.analytics` on the existing SQLite connection helper. It adds only
`analytics_events` and its timestamp index. No external analytics provider, browser
tracking SDK, extra service, paid dependency, production write, or deployment was used.

## Callable contract

- `record_event(db_path, event, route='/', device='unknown') -> str`
- `summary(db_path) -> dict[str, int]`
- `retention(db_path, days=30) -> int` (explicit cleanup, bounded to 1–365 whole days)

Supported events: `page_view`, `navigation`, `job_submitted`, `job_completed`,
`job_failed`, `job_cancelled`. Supported device categories: `unknown`, `mobile`,
`tablet`, `desktop`. Routes are a fixed public-page allowlist in `ROUTES`; arbitrary
paths, complete URLs, and dynamic user identifiers are rejected. Query strings and
fragments are discarded before storage. Input is bounded to 2048 characters before
normalization. SQL values are parameterized.

The schema contains only random event ID, event name, allowlisted route, device
category, and UTC collection timestamp. No cookies, visitor IDs, IPs, user agents,
referrer URLs, credentials, full prompts, or evidence content are accepted. Counts
are **observed event counts**, not unique visitors, sessions, retention, or security
efficacy. Repeated calls create repeated observations; no deduplication is claimed.

## Integration boundaries

These helpers do not authorize callers or provide routes. API integration must
validate and authenticate callers, enforce request/rate limits, and protect summary
and retention operations. Browser-originated collectors should permit only
`page_view` and `navigation`; job outcomes must come from trusted job lifecycle
code. Do not treat client-submitted operational events as proof of execution.

Retention is explicit, not a background scheduler. Operators must invoke it on a
schedule; data is not automatically deleted after 30 days by this module alone.
Cleanup touches only analytics rows older than the UTC cutoff. No job or evidence
record is deleted. Backup retention must be governed separately. Analytics helper
failures must not roll back successful model execution: capture failures honestly
and handle observability separately from job authority.

The first-use table creation is additive and idempotent. Existing global SQLite
schema version remains managed by `aurex.database`; this module introduces no
independent schema-version claim and no destructive migration.

## Verification

Base commit: `503f7e9` (XIV working integration). Tests use isolated temporary SQLite
databases, not production data.

- TDD: 15 tests failed with `analytics collector missing` before implementation.
- Targeted suite: 15 passed.
- Full backend suite in this isolated lane: 176 passed, 1 skipped, 1 warning.
- Ruff on the two added Python files: PASS.
- Strict Mypy on `aurex/analytics.py`: PASS.
- Warning: existing Starlette TestClient/httpx deprecation.
- Native Qwen execution, deployed event collection, owner dashboard, unique visitors,
  service availability, and real user traffic: NOT VERIFIED by this lane.

Reproduce from repository root:

```sh
python -m pytest tests/test_analytics_xix.py -q
python -m pytest -q
python -m ruff check aurex/analytics.py tests/test_analytics_xix.py
python -m mypy --strict aurex/analytics.py
```
