# KUSANAGI LXXI — Website-to-AUREX token egress boundary

**Scope:** draft source changes only. No website session gateway implemented, no Railway deploy, no Lovable integration or credits.

## P0 historical flaw

The previous `WebsiteAdapter(base_url)` forwarded `AUREX_SERVICE_TOKEN` to any syntactically valid URL, including plaintext remote HTTP. A malicious or incorrectly injected base URL could send a service credential to an attacker-controlled host.

## Server-only deployment contract

- Install the optional website HTTP adapter dependency only in trusted server-side code: `python -m pip install '.[website]'`. The canonical AUREX core Docker image does not require it.
- Configure `AUREX_BACKEND_BASE_URL` to the **exact** HTTPS AUREX API origin authorized by the operator, e.g. `https://aurex-api-production-c535.up.railway.app`; resolve and verify the current domain before using it. A mismatch, missing pin, arbitrary path, alternate host, insecure HTTP, URL userinfo, query or fragment fails before a token can be forwarded.
- Keep `AUREX_SERVICE_TOKEN` in server-only secret storage, never in a `VITE_*` variable, frontend bundle, page HTML, browser storage, logs, URL or query string.
- HTTPS uses ordinary certificate validation, does not follow HTTP redirects and does not trust process-proxy environment variables. To exercise a local development backend, pin the exact numeric loopback origin and **explicitly** set `AUREX_ALLOW_HTTP_LOOPBACK=1`. Never use the opt-in for non-loopback origins.
- Only the `AUREX_SERVICE_TOKEN` env var name is permitted by this adapter. Response payloads permit only the existing job metadata allowlist.
- The adapter's `create_job` method is server-only plumbing, **not** a user-authorized public Execute button. Before exposing any frontend POST, require authenticated website owner, scoped permissions, idempotency, budget and explicit release authority. First public integration should remain read-only.
- Review HTTPX security patch releases and its transitive dependencies before serving production traffic; this PR does not alter the deployment or check external package supply-chain status.

## Tests and admission

`tests/test_web_adapter.py` uses a fake in-memory client. It checks pinned HTTPS, rejected alternative hosts/plaintext, explicit numeric loopback, invalid credential sources, safe job IDs, bounded idempotency keys, redirect policy and redacted response fields. These tests make **zero real backend calls**.

**Release HOLD:** require exact-head `ruff check .`, `mypy aurex`, `pytest -q`, integration against an isolated staging adapter with TLS/auth, a server-side owner session, independent CUSTOS, and deployment permission. GitHub runner allocation incident: #58. Public frontend not wired by this PR.
