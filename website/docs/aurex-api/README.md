# AUREX service contract v1 (DRAFT — no hosted service exists)

- Contract: `openapi.yaml` (OpenAPI 3.1). TypeScript mirror: `src/lib/aurex-api-schema.ts` (zod, strict, bounded).
- Client: `src/lib/aurex-client.server.ts` (server-only; https non-local URL, bearer from server secrets, 0.5–10s timeout, no redirects, 256 KB cap, typed errors, idempotency keys on POST).
- Reference backend: `examples/aurex-backend/` — NOT deployed, dev-only. `app.py` (FastAPI, health + capabilities only, all `available: false`), `budget.py` (stdlib SQLite reservation ledger), `test_budget.py` (stdlib unittest; run from that folder: `python3 -m unittest test_budget.py`).

## Fail-closed rules
- Any network, timeout, auth, size or schema failure ⇒ capability NOT CONFIGURED.
- A capability is evidence-backed only if `available`, linked to evidence for the same capability, collected ≤ 7 days ago and not in the future.
- Budget limit 0 (default) refuses all spend. Reserve before work; commit ≤ reserved; release on cancel.
- Jobs accept named kinds with bounded scalar params only — never code, shell commands or URLs.

## Deployment checklist (owner, before connecting)
1. Host the service on owner-controlled infrastructure with a public https address (no localhost/Chromebook tunnels).
2. Generate a ≥32-char random token; store as `AUREX_SERVICE_TOKEN` on the service and in Project Settings → Secrets; set `AUREX_SERVICE_URL`.
3. Replace dev SQLite with a durable database; keep `BEGIN IMMEDIATE`/row-locking semantics for reservations.
4. Implement `/v1/evidence` and `/v1/budgets` read-only; add jobs only with allowlisted kinds and sandboxed workers.
5. Rate-limit and log (no secrets); restrict CORS to none (server-to-server only).
6. Run the website's owner diagnostics; capabilities turn REAL only with fresh evidence.

## Open-source patterns adopted (ideas only, no dependencies added)
| Project | License | Idea used | Why no dependency |
|---|---|---|---|
| LangGraph | MIT | Durable, resumable job states | Contract only; no agent runtime needed on website |
| Temporal | MIT | Idempotency keys, explicit cancel, workflow state enum | Heavy cluster; overkill for draft |
| LiteLLM | MIT (core) | Budget reserve → commit/release | Website must not route paid models |
| OpenTelemetry | Apache-2.0 | Value-free structured audit events | Add SDK when a collector exists |
| vLLM | Apache-2.0 | Self-hosted model serving as future service backend | GPU service, outside website |

Versions are not pinned because no dependency was introduced. Tradeoffs: in-memory TS ledger is reference semantics only; the service's database is authoritative. Licenses checked from each project's public repository; verify before adoption.
