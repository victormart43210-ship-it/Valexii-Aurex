# Private Onyx deployment assessment — no deployment authorized

Observed 2026-10-25 America/Chicago. Upstream source pin: 616a4b1a9c75cc07e9645069c672f3e8fb029ca8.
Read alongside ONYX_CAPABILITY_MATRIX.md and ONYX_AUREX_CONTRACT.md.

## Published resource floor (not measured by Work)
Official Standard minimum: 4 vCPU, 10 GB RAM, 32 GB disk plus roughly 2.5× indexed data;
preferred 8+ vCPU, 16+ GB RAM. Lite has a lower 2-vCPU/2-GB/10-GB floor, but this
adapter's search endpoint requires a vector database. Do not substitute Lite without
verifying that requirement. Source: https://docs.onyx.app/deployment/getting_started/resourcing

## Platform comparison
| Factor | Hetzner private VM | Railway existing AUREX service |
|---|---|---|
| Current capacity | NOT VERIFIED; paid account is not a server inventory | NOT VERIFIED; do not colocate in AUREX container |
| CPU/RAM/storage | Must meet Standard floor plus AUREX headroom if colocated (prefer separate private host) | Multiple persistent services and memory allocations need a new cost assessment |
| Index/database | Upstream pinned compose: PostgreSQL, OpenSearch, Redis/cache, object store | Requires separate private services and volumes, not AUREX SQLite |
| Workers/models | Background, indexing and inference services; disable external model configurations | Same requirements; no assumption of free capacity |
| Network | Firewall to AUREX only, approved TLS origin; internal index/DB ports unpublished | Private network where available plus approved TLS ingress; no public admin UI |
| Costs | Existing plan/usage/bandwidth/backups unknown; do not buy or resize | Additional services likely consume resources; no spending approval |
| Upgrade | Pin image digests, rehearse migrations and restore on disposable clone | Same, with coordinated multi-service rollback |
| Readiness | NOT VERIFIED | NOT VERIFIED |

## Admission before any live request
1. Inventory actual CPU/RAM/disk, free capacity, region and backup arrangements without exposing credentials.
2. Verify edition/license for requested permission sync and user/group features. CE license alone does not establish feature availability.
3. Use dedicated synthetic-only single-owner index and least-privilege READ_SEARCH key; never an admin search route.
4. Verify with provider configuration and egress-denial tests that query expansion, filter detection,
   federated search, embeddings and reranking cannot invoke paid/cloud providers. The adapter's
   skip_query_expansion flag alone does NOT establish this. No model downloads authorized here.
5. Verify TLS certificates, DNS resolution, firewall rules and credential consumers. Origin allowlisting
   is not a DNS-rebinding defense. Socket timeout is not a strict end-to-end deadline; live admission
   must add an outer process/request deadline and concurrency/rate limits.
6. Capture two-user denial and revoked-access tests if expanding beyond the single owner. Otherwise
   multi-tenant deployment BLOCKED. No client-supplied tenant claim may authorize a retrieval.
7. Back up PostgreSQL, search index/object store, configuration and secrets through approved secure storage.
   Rehearse restore and deletions; no backups have been created by this operation.
8. Owner approves a specific costed staging change; independent reviewer approves admission evidence.

## Optional live test (NOT RUN)
First index ONLY the six fictional records returned by `synthetic_corpus()` in
`aurex/integrations/onyx_demo.py` through a separately authorized ingestion procedure.
No indexing endpoint has been invented or called here. Configure a private origin, exact host,
and a secret through secure runtime controls: AUREX_ONYX_ORIGIN, AUREX_ONYX_ALLOWED_HOST,
AUREX_ONYX_TOKEN. After admission, set AUREX_ONYX_ISOLATED_SYNTHETIC=1,
AUREX_ONYX_LOCAL_ONLY_INFERENCE=1, AUREX_ONYX_LIVE_TEST=1 and run:
`python -m pytest -q tests/test_onyx_live.py`.
These flags record operator intent, not independent proof. Never place the token in chat or Git.

## Rollback
No infrastructure was changed. Source rollback: revert this PR's commits. Future live rollout must
record actual pre-change instance/image/config IDs and backup checksum, stop retrieval, restore
compatible services/data from tested backups, then verify AUREX remains available. Provider downgrade
alone may not reverse database migrations. Production and existing Railway volumes stay untouched.
