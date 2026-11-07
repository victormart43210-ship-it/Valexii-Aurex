# KUSANAGI LXXV — IRON BRIDGE read-only verifier remediation

**Scope:** isolated verifier and deterministic adversarial tests; no production deployment, merge, payment, credentials, workflow execution or public-website publication.

**Source:** independently reviewed LXXIV convergence implementation at `6848d9199525e0aa23e5805b0df2d7a30b8416c1`; remediated files are being proposed against canonical `main` rather than merging the divergent branch.

## Repaired conditions

- Rejects HTTP 200 `{}` **and** incomplete or type-invalid shapes at every v1 endpoint, matching strict public Zod contracts in the existing Lovable application. Rejects unknown keys, invalid IDs, invalid timestamps, invalid enums, invalid monetary values, oversized arrays/strings, duplicate JSON keys and NaN/Infinity.
- Requires a credential of at least 32 characters **before opening a network connection**. A token's presence does not independently prove the server authenticated it; a successful authenticated server response is required for transport PASS.
- Checks **both canonical origin and fixed endpoint** before constructing a URL. No `urljoin`, arbitrary path, query, userinfo, or unexpected port. HTTPS enforced for the pinned production hostname; isolated HTTP loopback fixtures require explicit test mode.
- Disables urllib redirects via `NoRedirectHandler`; 3xx responses cannot forward Bearer tokens to a second host.
- Caps streamed response read at 256 KiB + 1, uses bounded timeouts, makes no automatic retries, and rejects non-200 statuses.
- Reports ONLY sanitized endpoint metadata; no raw evidence or job records, no credentials. Hash of canonical report bytes is a **self-generated integrity digest, not independent attestation**.
- Calls exactly `GET /v1/health`, `/v1/capabilities`, `/v1/evidence`, `/v1/budgets`, `/v1/jobs` — the deployed `integration/kusanagi-xvi-railway` bridge, **not** the divergent branch's `/health` alias.

## Verification commands

```
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_bridge_security_adversarial.py
python3 -m compileall -q scripts/verify_live_bridge.py
```

Optional, when dependencies are installed: `ruff check scripts/verify_live_bridge.py tests/test_bridge_security_adversarial.py` and `mypy --strict scripts/verify_live_bridge.py`.

## Gates still unresolved

- `BACKEND LIVE`: requires authorized token available securely in execution environment and real read-only transport evidence.
- `WEBSITE → BACKEND LIVE`: requires separately observed signed-in **deployed frontend server-side** diagnostics; direct verifier pass **cannot** establish this.
- `GitHub CI`: exact-commit green runs or documented runner-allocation gaps; local pytest alone does not attest full repository coverage.
- `AEGIS`: persona claims are never authority; PR #63 and any privilege invariants remain independent security gates.
- `RELEASE`: **HOLD** pending independently verified live production handshake and admission criteria.

The five HTTP GET calls are read-only; do not run live tests without appropriate token management and authorization. Set `AUREX_SERVICE_TOKEN` using an approved secrets channel; do not paste it in logs, PRs, chat or command-line arguments.
