# KUSANAGI CXCII — Sovereign First Light (PARTIAL; staged only)

Starting commit: `7c4e9907dd0ff6821a35e23f3f71da389f726814`. Ending commit / PR URL: see the PR (not merged, not deployed).

## Inspection findings
- No `/v1/agent/status` or `/v1/agent/ask` existed anywhere in the repo; they are now the canonical routes (`aurex/agent.py`).
- Existing Qwen path: `aurex/adapters/ollama.py`, intentionally **loopback-only** (rejects non-loopback hosts, no redirects). Hence Railway cannot reach Hetzner `127.0.0.1:11434`.
- No existing website chat component calling AUREX-OX was found; no frontend change made. DISPATER components named in the directive (`dispater-audit-console.tsx`, `dispater-audit-client.server.ts`) were not located/modified. Open PRs/branches and CLXXII–CXCI reports were not reviewed (shallow clone).

## Implemented
- `GET /v1/agent/status` (auth): active probe of Ollama `/api/tags`; reports READY / MODEL_MISSING / UNREACHABLE / MISCONFIGURED.
- `POST /v1/agent/ask` (auth): question ≤1000 chars, deterministic routing (non-chat types are REFERRED, never sent to Qwen), public-only retrieval with citations, shared rate limit, 60 s timeout, `<think>` reasoning stripped (unterminated reasoning => error), structured 429/502/503 errors with request ID (`X-Request-ID`), no fabricated answers on failure.
- Config (names only): `AUREX_QWEN_URL` (loopback), `AUREX_QWEN_MODEL` (default `qwen3:0.6b`), `AUREX_QWEN_TIMEOUT`.
- Tests: `tests/test_cxcii_agent.py`.

## Tests run
`python -m pytest tests -q`: 442 passed, 1 skipped. `ruff check` on new files: pass. Mypy, Bun frontend tests, staging e2e: **not run**.

## Verified vs unverified
- Verified (mocked adapter only): reasoning stripping, auth, failure handling, routing, bounds, correlation ID.
- **Unverified: any real Hetzner Qwen response, the "What is DISPATER.AI?" staging demonstration, Railway↔Hetzner connectivity, streaming, ONYX integration (synthetic in-memory store only; no DISPATER.AI knowledge exists, so the answer would be ungrounded), deterministic audit calculation integration, DISPATER synthetic towing audit, OpenShell runtime containment.**

## Human actions required
1. Provide a private channel (e.g. WireGuard/Tailscale or SSH tunnel) from the AUREX-OX host to Hetzner that exposes Qwen at a loopback address on the API host; never expose Ollama publicly. Set `AUREX_QWEN_URL` accordingly.
2. Set `AUREX_SERVICE_TOKEN` on staging; website server-side code must call `/v1/agent/ask` with it (token never in the browser).
3. Run `/v1/agent/status`, then ask "What is DISPATER.AI?" on staging and capture sanitized evidence.
4. Supply approved public DISPATER.AI knowledge for ONYX.

## Remaining blockers
Frontend wiring, public (unauthenticated) rate-limited proxy, ONYX/Codex integration, DISPATER convergence, security regression pass.
