# Operation KUSANAGI LXXVI — Four AUREX/OX Integration Gates

**This is a source/contract verification handoff, not a production deployment or an admission.** Owner requested to connect the four displayed `valexii.com` integration gates. The front-end is a separate Lovable/GitLab project and cannot be modified by this backend repository.

## Observed, October 17, 2026 (independent control-plane reads)

- **GitHub canonical main:** `df0654390049118a142ec3b3356f0f40b4789fe4`. The associated CI job **completed successfully**, including Ruff, strict Mypy and pytest. This is source-level proof on that commit only.
- **Railway production:** project `78095d3d-5911-41c8-aa3e-f9ebf5d81054`, `aurex-api`, deployment `59ca0ec7-e1db-481f-984e-1aadbcfcc15d` is **SUCCESS**, but runs branch `integration/kusanagi-xvi-railway` at commit `57a079f93b947594f1a6f854aa46a6f606f86f76` with root `/integrations/kusanagi-xvi/backend`. That is the **read-only bridge**; not canonical backend `aurex.api:app`.
- **Railway has a staged patch**, ID `814e3b02-7f90-4812-b107-32e3e7aad529`, with 4 pending changes: add volume `aurex-evidence-db`, mount `/data`, set variables `AUREX_DB_PATH` and `AUREX_ENABLE_OFFLINE_LAB`. Changes are **NOT LIVE**. Do NOT press accept-deploy on the staged patch without explicitly reviewing the correct rootDir, exact main SHA, worker OFF flag, secrets, backup and rollback. Applying the staged patch alone **does not switch the old bridge into the new backend**.
- **Railway last 72h GET requests**, aggregated without collecting IPs or tokens:
  
  | v1 GET path | 2xx | 4xx |
  | --- | ---: | ---: |
  | /v1/health | 119 | 6 |
  | /v1/capabilities | 101 | 3 |
  | /v1/evidence | 101 | 3 |
  | /v1/budgets | 101 | 3 |
  | /v1/jobs | 7 | 3 |
  
  These counts confirm the server handled successful requests on **all five paths**; they do **not prove** the requests came from the published website, from a properly authenticated owner, or were contemporaneous/same-request snapshots. 2xx does not establish independent intelligence.
- **Lovable project** `811ffc43-2c8b-4c88-ab4c-4de668d089cb` published at source SHA `94ecb8d82f97bc5f1abfc4489eee1c2a2e970358`. Inspection of `src/lib/aurex-client.server.ts`: constructed server-side URL `/v1${path}`, 5-second timeout, manual redirect, bearer auth, strict Zod parsing. `getSovereignStudio` server action requires Supabase owner auth. Public `getPublicAurexStatus` exposes allowlisted summarized results but **not** private jobs/evidence. The current UI's `2026-10-16` integration bars are static roadmap **not live telemetry**.
- Lovable workspace **ran out of credits** while attempting the P0 Ouroboros performance fix, which remains UNAPPLIED; see Issue #71. No publication or source code modification to Lovable was authorized/performed by this backend PR.

## Gate matrix — status grounded in evidence

| Website label | Evidence | State |
| --- | --- | --- |
| Canonical backend API + CI | Main commit SHA and successful CI | **PASS — CODE/CI ONLY** |
| Canonical Railway deployment | Running old read-only bridge, canonical image not live, DB volume staged | **HOLD — NOT DEPLOYED** |
| Website server proxy + owner auth | Source inspection supports server-only client and owner check; read-only Railway GET counters positive | **PARTIAL — PUBLISHED OWNER HANDSHAKE NOT INDEPENDENTLY ATTRIBUTED** |
| API → worker → SQLite → evidence → website | Main repo contains fenced worker, offline probe, SQLite persistence code; production is old read-only bridge and no live write/evidence validation | **HOLD — NOT VERIFIED** |

### What this PR improves immediately

1. Adds `tests/test_website_bridge_contract_replay.py`, which replays **all five** v1 read-only endpoints against both the old bridge and canonical FastAPI app in **isolated TestClient** instances. Includes strict shape, enum, size, time, auth and fail-closed negatives. All credentials and DBs are synthetic. The canonical worker flag remains OFF; no live calls or jobs.
2. Corrects the checked-in website OpenAPI draft to include `offline_probe` and underscore-capable capability IDs; replaces the obsolete assertion that no hosted server exists. The **actual Lovable project is separate**, so this GitHub spec adjustment must be reconciled with Lovable's own `docs/aurex-api/openapi.yaml` later.
3. Preserves the no-self-witness rule: passing a response schema or a self-reported status does not prove AI capability, production authority, job execution or security clearance.

### Exact safe closure order

**A — Contract admission (current PR).** Independently check exact-head CI, compare response contracts and verify no regression vs the published Lovable Zod schemas. Keep normal backend CI and the separate IRON BRIDGE script repair PR #66.

**B — Canonical image release candidate (new controlled review).** Verify a **Docker image built from one exact SHA**, verify nonroot user, read-only network / auth handling, DB mount and deterministic 503 when worker disabled. Prove dedicated persistent volume ownership and encrypted backup/restore. The current production bridge must remain available for rollback; staged /data volume alone is not persistence proof.

**C — Authenticated owner read-only handshake.** With owner authorization and without exposing bearer values, collect a timestamped result for all **five** GETs from the **published** website's owner-only server action; verify all five statuses, schema compatibility, zero-budget report and correct 90-second UI freshness. Confirm browser never receives token or raw private evidence. Railway request counts do not replace this.

**D — Fenced offline worker, DB and evidence.** Only after A/B/C: separately approve controlled, synthetic **$0** `sqlite_roundtrip_v1` owner-only POST to canonical backend, follow ID to terminal state, verify durable SQLite record and explicit `offline_probe` evidence under valid lease; restart and retest durability/cancel/idempotency. Evidence observation stays `UNVERIFIED` until an independent Policy/World/Adversarial review. Backend should keep `AUREX_ENABLE_OFFLINE_LAB=0` until explicit sign-off.

**E — Update the website accurately.** Once A/B/C/D have independently verified proof, replace the screenshot's static roadmap strings with explicit dated evidence references. Do not turn bars green based solely on source code or response 200. Preserve 10 OX tabs, owner Studio A/B/C, public privacy, and prior first-priority Ouroboros performance fix.

### Release prohibitions

No secrets read or surfaced, no paid inference, no finance documents uploaded, no legacy branch wholesale merge, no staged Railway patch acceptance, no `Lovable.deploy_project` call, no DNS changes, no worker enabling or job submission as part of this PR. **Production remains HOLD until owner approval and independent evidence.**

Canonical governance: **Evidence → Qualification → Reality → Authority → Effect**; unknown/stale/failed is HOLD, never PASS.

## 2026-10-17 — Railway operator reconciliation and LXXV security convergence

**Scope:** existing Railway project `78095d3d-5911-41c8-aa3e-f9ebf5d81054`, environment `9a139b10-9e6b-4ebd-89c7-731855cbbb5c`, service `aurex-api`. No new service, project, deployment or custom domain created.

- **Live deployment is unchanged:** `59ca0ec7-e1db-481f-984e-1aadbcfcc15d`, GitHub source `integration/kusanagi-xvi-railway` commit `57a079f93b947594f1a6f854aa46a6f606f86f76`, root `/integrations/kusanagi-xvi/backend`. This is the authenticated read-only bridge and remains the rollback base.
- **Observed Railway health:** production `aurex-api` ONLINE/SUCCESS. Last 24 hours: **132 HTTP requests** (120 2xx, 12 4xx, 0 5xx). Observed latest p95 41ms and sampled worst p95 48ms for the window; these are edge-reported response times, not browser/Ouroboros performance or owner-auth proof.
- **Staged infrastructure:** patch `814e3b02-7f90-4812-b107-32e3e7aad529` remains **STAGED**, **four changes**, non-destructive as classified by Railway: create `aurex-evidence-db` volume, mount it at `/data`, and add `AUREX_DB_PATH` and `AUREX_ENABLE_OFFLINE_LAB` variables. The two staged variables were explicitly set on 2026-10-17 to `AUREX_DB_PATH=/data/aurex_jobs.db` and `AUREX_ENABLE_OFFLINE_LAB=0`. Railway subsequently confirmed changeCount=4 and `STAGED`. Secret values were not read; the deployed bridge is untouched.
- **Security convergence:** the exact reviewed `scripts/verify_live_bridge.py` and `tests/test_bridge_security_adversarial.py` from **draft PR #66** were added to **draft PR #72**, byte-identical in a connector readback: blobs `9b687484308210a2c7ad7d767d41ea24f002ae9c` and `cef0b9b7fb69e0082b89654b2114ac23b9fda1e7`. This consolidates origin confinement, redirects blocked, mandatory Bearer, strict schema, capped body, sanitized transport-only report, and prior **41 isolated locally run adversarial cases**. Prior tests are not proof of exact-HEAD CI.
- **Static review checks:** 14 source-invariant checks passed for the PR #72 snapshot (health Bearer, public /health, $0 default, worker-off, fixed GET paths, strict five shapes, redirect/body caps, adversarial tests and CI smoke provisions). These were **static checks only**. No source-level test outcome was inferred from Railway serving 2xx.
- **CI and integration HOLD:** exact-HEAD GitHub Actions CI/Docker/offline-practice jobs report **FAILURE with steps=null; remote job-log fetch returned BlobNotFound**. This suggests tests never executed but cannot establish the administrative cause. CI admission is **NOT VERIFIED**. The published website's authenticated owner-to-Railway five-GET call is likewise **NOT VERIFIED**; user-facing live status must stay separate from static roadmap gates.
- **Releasing the candidate remains prohibited** until an independently verified exact-SHA CI/test matrix, explicit Railway service source/rootDirectory comparison, persistent-volume restore plan, unauthenticated health and Bearer contract checks, and separately documented owner permission to accept the staged changes. **No `accept-deploy` or source switch has occurred.**

**Advisory:** The superseded LXXVII convergence branch is 25 commits ahead / 117 behind canonical `main`; its last submission commit adds no file changes and contains an unauthenticated versioned health route plus an older vulnerable bridge script. Do **not** deploy or bulk-merge that branch. The reviewed release candidate is the scoped main-derived draft #72.

