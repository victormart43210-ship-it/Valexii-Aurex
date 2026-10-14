# AUREX → valexii.com deployment readiness

Canonical domain: **valexii.com** (www redirects to apex). Status today: **NOT CONNECTED**.

## Current state (verified in source)
- Public `/aurex`: static capability registry + `AurexOxStatus` panel; no owner calls, no live data.
- Owner `/admin/aurex-control`: `ssr: false`, `noindex`, every server function behind `requireSupabaseAuth` + `assertOwner` (`AUREX_OWNER_USER_ID`), fails closed.
- Server-only client `src/lib/aurex-client.server.ts`: https, non-local hosts only, bearer read from server secrets, no redirects, size/timeout caps.
- Contract: `docs/aurex-api/openapi.yaml`.
- The owner's local Phase 5 advisory API runs on a local machine and **cannot** be reached by the website. Phase 6/7 build files were not supplied to this project and are not bundled.

## Requirements to connect
1. Host the advisory service on owner-controlled infrastructure with a public **HTTPS** address (no tunnels to a personal device).
2. Implement the contract endpoints: `GET /v1/health` (+ `/v1/capabilities`, `/v1/evidence`, `/v1/budgets` read-only). The local `/health`, `/api/audit`, `/api/proposals`, `/api/backend-tests` paths need an adapter or mapping to `/v1/*`; not done yet.
3. Generate a ≥32-character token; store it on the service and in Project Settings → Secrets as `AUREX_SERVICE_TOKEN`; set `AUREX_SERVICE_URL` (server-only, never `VITE_`).
4. Set `AUREX_OWNER_USER_ID` to the owner's account ID if not already set.
5. Keep `AUREX_BUDGET_USD` unset/0 until spending is explicitly approved.
6. Service: CORS off (server-to-server), rate limits, logs without secrets.

## Verify owner-only access (after publish)
- Signed out → `/admin/aurex-control` shows "Access denied" with the sign-in blocker.
- Signed in as a non-owner → "this account is not the configured owner."
- Owner → "Run diagnostics": `urlSet`/`tokenSet` yes, `health: ok`. Any error code ⇒ stays NOT CONFIGURED.
- Calling the server functions without a session returns 401; check the service never receives requests from browsers.
- `/aurex` still shows NOT CONNECTED rows (they are static by design; change them only with evidence).

## Rollback
- Delete or blank `AUREX_SERVICE_URL` / `AUREX_SERVICE_TOKEN` → client fails closed to NOT CONFIGURED immediately in preview; publish to apply to valexii.com.
- Rotate the token on the service if exposure is suspected.
- Revert to the previous project version from history if UI changes misbehave. No DNS changes are involved.

## Not done here
No deployment, publishing, DNS, secrets, payments, or remote execution. No telemetry is shown or claimed.
