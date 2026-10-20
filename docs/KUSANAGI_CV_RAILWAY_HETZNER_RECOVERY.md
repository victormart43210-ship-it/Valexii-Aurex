# KUSANAGI CV — RAILWAY / HETZNER RECOVERY (October 19, 2026)

## Read-only evidence confirmed from connected providers

**Railway** VALEXII-AUREX / `aurex-api` / production has **1/1 online**, last SUCCESS from **Oct 14**, 0 recent crashes. Live source is still GitHub `integration/kusanagi-xvi-railway` at commit `57a079f93b947594f1a6f854aa46a6f606f86f76`, with root directory `/integrations/kusanagi-xvi/backend`. This is an older, authenticated, 5-GET, read-only bridge. It is NOT canonical `main`, ORCA R8, Qwen, or a live evidence/job worker.

A **four-change staged patch** is present and **NOT LIVE**: add `/data` volume mount, create `aurex-evidence-db`, set `AUREX_DB_PATH`, and set `AUREX_ENABLE_OFFLINE_LAB`. These are safe-looking in resource inventory (non-destructive) but values are redacted and the live read-only branch has no durable worker contract. No staging patch has been committed in this operation.

Railway service domain (do not assume it was reachable from website): `aurex-api-production-c535.up.railway.app`. No custom domain, no configured healthcheck or tracing. Access to authenticated `/v1/health` must be tested without printing secrets.

**Hetzner billing gate:** The owner's Hetzner invoice was $4.62 on Oct 17, and an Oct 18 provider email says the credit-card payment **failed** and asks for immediate settlement. Payment status after that email is NOT VERIFIED; do not assert suspension or live server failure. **Only the account owner can complete this billing operation.** Open Hetzner Accounts directly, check invoice/payment status and reconcile with provider. Do not copy card details, tokens or account passwords into tools/CI/logs. Cloud node outage message dated Sep 26 was later marked resolved; that older event does NOT prove any present Hetzner cloud problem.

**Hetzner runner:** Previous architecture specified a CX33, label `medaurus-runner-01`, but there is no Hetzner or GitLab administration connector with which to confirm current server power, IP, registration, runner online status or tags. The read-only preflight / manually-triggered exact-SHA GitLab CI bridge is in draft GitHub PR #92; no proven live GitLab job exists. GitHub Actions jobs previously failed *before running steps*; do not misrepresent them as failed code tests.

## Source repair in this PR (not deployed)

- `/health`: **PUBLIC**, infrastructure liveness/readiness (no secrets, no capability claims).
- `/v1/health`: **REQUIRES same service bearer as private /v1 endpoints**, as agreed with currently deployed bridge and website server contract.
- Update `tests/test_kusanagi_workflow.py` so unauthorized 401, wrong bearer 401, valid bearer 200, and public `/health` 200.
- Update `.github/workflows/railway-image.yml` to poll `/health`, then verify private `/v1/health` fails closed without authentication and succeeds with bearer.
- This is a **draft**, awaiting actual exact-head independent Python+container runs. No merge, deploy, billing or service-domain action.

## Correct order to make Railway useful

1. **Account owner confirms Hetzner billing status** and, if unpaid, settles it with Hetzner, then checks project/server power state.
2. On the existing server (using its authorized SSH session), inspect read-only `systemctl is-active gitlab-runner`, `gitlab-runner status`, and run the branch-reviewed `ci/hetzner/read_only_preflight.sh` from PR #92. Review runner registration in GitLab project Settings → CI/CD → Runners. Do NOT expose `config.toml`, registration token or IP publicly.
3. If a runner exists, ensure AUREX uses a dedicated nonprivileged Docker executor, `privileged=false`, no Docker host socket, no private USB mounts, no production secrets. If absent, create project/group runner in GitLab UI first (modern `glrt-` authentication token), register on Hetzner with reviewed GitLab procedure, and keep token solely on host.
4. Pin a CI-only protected GitLab pipeline to reviewed PR #92 commit. Manually verify one **trusted exact-SHA GitHub PR**, capturing machine-verifiable dependency/run output. No CI bypass or mainline merge. If GitLab UI/project cannot be accessed, no runner activation claim.
5. Use independent runner to check this PR, frontend-backend contract PR #93 and ORCA private status PR #94; reconcile latest source and conflicts **before** integration. Full pytest/Ruff/Mypy and isolated Docker build/smoke; checks failing or not run = HOLD.
6. Only then stage canonical API root Dockerfile `Dockerfile` with GitHub canonical source under `/` and appropriate `/health` path (NOT `/v1/health` for Railway healthchecks). Confirm `AUREX_ENABLE_OFFLINE_LAB=0`, `AUREX_BUDGET_USD=0`, SSL service token, nonroot UID, single region/SQLite semantics, persistent `/data` with backups and rollback. **The current four staged changes are production pending**. Avoid accepting them on the old bridge just to 'make progress'.
7. Run a separately owner-approved isolated staging deployment and confirm (a) GET `/health` 200, (b) /v1 with no/wrong auth 401, (c) valid bearer 200 and typed five-GET contracts, (d) exact deployed source/branch SHA and request attribution, (e) durable synthetic SQLite restart proof. Never read private customer docs. Keep paid model inference/Qwen disabled until its own gate.
8. After frontend owner-only Lovable code has separately passed exact-SHA review and deploy authorization, use Cloudflare→Railway attributed E2E request tests and ORCA telemetry. Update master issue #75 with proofs; only then remove HOLD.

## Status decisions

| Gate | Truth |
|---|---|
| Current old Railway deployment | ONLINE, read-only, 1/1 instance |
| Four Railway changes | STAGED, NOT COMMITTED |
| Current canonical AUREX backend deployed | NO |
| Hetzner invoice payment | FAILED Oct 18 (later state unknown) |
| Hetzner machine / GitLab Runner | NOT VERIFIED |
| New health-auth source fix | COMMITTED TO DRAFT BRANCH |
| Exact-head tests and CI | NOT RUN |
| Railway migration / Qwen / live ORCA | NOT DEPLOYED |
| Production release / independent authority | HOLD / NONE |

Governing architecture: **Evidence → Qualification → Reality → Authority → Effect**. The system may never be its own sole witness. Unknown ≠ healthy.
