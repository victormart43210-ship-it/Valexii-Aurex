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
