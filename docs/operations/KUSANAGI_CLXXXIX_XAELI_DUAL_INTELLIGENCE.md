# KUSANAGI CLXXXIX — XAELI Dual-Intelligence (staged, not deployed)

Starting commit: `551625e5be41ef6fd16e70e7a72404400032f4bc`. Status: **STAGED in PR only**; not merged, not deployed, not independently verified. Production HOLD.

## Files
- `aurex/xaeli/core.py` – routing, Tier 1 Cloudflare Workers AI adapter, rate limiter, Tier 2 gate, ledger, knowledge interface.
- `aurex/xaeli/api.py` – `GET /v1/xaeli/status`, `POST /v1/xaeli/chat` (public), `POST /v1/xaeli/audit/{tenant}/jobs` and `.../cancel` (service token + tenant allow-list).
- `aurex/api.py` – router registered. `tests/test_clxxxix_xaeli.py` – tests.

## Behaviour
- Tier 1 is off unless `AUREX_XAELI_TIER1_ENABLED=1` plus credentials/model are set. 401/403/429/402 never retried; no paid fallback; on any failure/limit the response is a non-generative LIMITED answer with approved public snippets.
- Routing is a deterministic regex table; model output is never consulted, so a model cannot self-escalate.
- Public chat searches only `visibility=public` docs; private docs require matching tenant. `KnowledgeStore` is the ONYX adapter boundary (synthetic in-memory stand-in; ONYX is **not** connected yet).
- Tier 2: `tier2_gate` denies unless authenticated, tenant authorized, valid job owned by tenant, enabled, provider approved, estimate within per-job/monthly/global ceilings, and an authorization receipt present. It records every decision to the ledger and **never executes a provider** (no executor exists). Duplicates and cancelled jobs are denied. Defaults: all ceilings $0.
- Math/reconciliation are routed to the deterministic engine (not invoked from chat).

## Environment (names only)
`AUREX_SERVICE_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `AUREX_XAELI_TIER1_ENABLED`, `AUREX_XAELI_TIER1_MODEL`, `AUREX_XAELI_USER_LIMIT`, `AUREX_XAELI_DAILY_LIMIT`, `AUREX_XAELI_TENANTS`, `AUREX_XAELI_TIER2_ENABLED`, `AUREX_XAELI_TIER2_PROVIDERS`, `AUREX_XAELI_TIER2_{GLOBAL,MONTHLY,JOB}_USD`. Keep server-side only (Hetzner/Railway secrets).

## Findings / gaps
- Tests: 434 passed, 1 skipped (incl. new XAELI tests, mocked transport).
- Actual provider connectivity: **not tested** (no credentials, no network). Free-tier eligibility/quotas/model choice: **unverified**; no model chosen — set `AUREX_XAELI_TIER1_MODEL` after checking current Cloudflare docs. Daily limit is app-level, not a guarantee.
- Not done: website chat UI wiring (no existing chat frontend targeting this backend was found beyond `dispater-web`), streaming, ONYX integration, Tier 2 executor, persistent ledger/job store (in-memory; per-process limiter), per-user identity beyond IP, Hermes-style agents, Railway/Hetzner config changes. Jules CLXXXVIII not reviewed.
- Security: single shared service token means tenant allow-list is not identity-bound; must be replaced with per-tenant credentials before real use. IP rate limit trusts socket address (behind proxy it will be the proxy).
- Estimated additional spend: $0.

## Rollback
Revert the PR (remove router include in `aurex/api.py`). No data migrations.

## Next steps
Per-tenant auth; ONYX adapter; persistent ledger; verify Cloudflare free tier and model; frontend wiring; independent review.
