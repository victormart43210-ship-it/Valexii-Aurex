# Onyx capability inventory — CLXXVI CP001

Inspected 2026-10-26 UTC (2026-10-25 America/Chicago). Source-level verification only; live interoperability NOT RUN.
AUREX main: `551625e5be41ef6fd16e70e7a72404400032f4bc`. Upstream Onyx: `616a4b1a9c75cc07e9645069c672f3e8fb029ca8`.

| Capability | Source observation | Admission |
|---|---|---|
| Search | POST /api/search, SearchRequest.query and skip_query_expansion | Implement strict version-pinned parser; default disabled |
| Result schema | results: citation_id (nullable int), title, content, link (nullable), source_type, updated_at (nullable string) | No invented document ID, version, score or ACL proof |
| Identity | require_permission(READ_SEARCH); API keys resolved server-side to user | No shared-key multi-tenant admission |
| Permissions | Search claims user-filtered results; source permission synchronization and group RBAC documented as enterprise features | Deployment-level verification required; candidate ACL NOT VERIFIED |
| Provenance | link and source_type available; citation_id is response-local | Preserve locator; missing source = NOT VERIFIED; no citation ID as stable identity |
| Cost | Search calls get_default_llm and SearchTool, filter detection and optional query expansion | skip_query_expansion does NOT prove zero cost; outbound live calls gated |
| License | MIT outside ee directories; separate enterprise license inside ee | Adapter implements wire contract without copying upstream implementation |
| Index | Standard compose includes PostgreSQL, OpenSearch, cache, object store, background and model servers | No second AUREX database; no deployment |
| Existing AUREX | Local TF-IDF and synthetic knowledge demo remain; canonical API uses one owner/service bearer | Preserve; no claim of authenticated multi-tenant identity |

## Repository reconciliation
PR #132 merged as 0ebc3b193f7c959f82fe3ec30f1351e89a731537: readiness documentation only, reused.
PR #145 is OPEN, unmerged, conflicting at d25ee5f0663f15c817cda92ea710f935986b081d. Not imported; no dependency on its new workflow/UI.
Recent main merges include #133, #135, #130, #126, #124, #144. Current deterministic DISPATER and SQLite fenced-worker interfaces inspected.
Root RECOVERY.json and RESUME.md absent at base; existing docs/operations/* and integrations/private-admin recovery histories retained unchanged.

## Primary references
- https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/backend/onyx/server/features/search/api.py
- https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/backend/onyx/server/features/search/models.py
- https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/backend/onyx/auth/users.py
- https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/LICENSE
- https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/deployment/docker_compose/docker-compose.yml
- https://docs.onyx.app/admins/getting_started/enterprise_edition
- https://docs.onyx.app/deployment/getting_started/resourcing

## Ownership and acceptance
Work owns aurex/integrations/onyx*.py, tests/test_onyx*.py, synthetic fixture, one router inclusion, listed docs and root recovery files. No parallel writers. Rollback: revert feature commits; no infrastructure change. Independent reviewer: Jules pending, NOT RUN. Acceptance: bounded authenticated synthetic retrieval, strict schema, denied unknown identity/access, no writes or external inference, regression tests and exact-SHA durable handoff.
