# Onyx → AUREX contract v1 — CP002

Scope: optional read-only retrieval, no agent actions, no independent witness, no production authority.
Upstream pin and observed wire schema: ONYX_CAPABILITY_MATRIX.md.

## Transport
POST {approved HTTPS origin}/api/search with server-only Bearer credential and JSON
`{"query": "bounded text", "skip_query_expansion": true}`. No arbitrary endpoint,
redirect, ambient proxy, retries, model/provider override or browser credential.
5-second socket timeout, 256 KiB response maximum, 20 results, 8 KiB per content excerpt.
Live requires explicit enabled, isolated single-owner deployment and local-only inference
admission settings. These are operator attestations, NOT proof or multi-tenant isolation.
Deployment must independently enforce egress and disable automatic filters, external embedding,
reranking, federated search and paid providers. The endpoint still initializes an LLM.
No public live route is added until that admission is independently verified.

## Identity and policy
Existing AUREX bearer authenticates one service/owner, not multiple tenants. Synthetic API
POST /v1/retrieval/onyx/demo derives owner and tenant from server-owned fixture constants;
request accepts only fixed scenario. No client tenant, credential, query, URL or record input.
Adapter requires an explicit trusted Principal from server authentication; it must match
its configured single owner and tenant before any network call. A shared multi-tenant index
is prohibited. This does not retrofit tenant enforcement into existing AUREX endpoints.

## Normalized candidate (frozen typed model)
request_id, tenant_id, principal_id, source_system=onyx, source_document_id=null,
retrieved_at (aware UTC), document_version=null, source_modified_at (nullable), content_excerpt,
citation/source_locator (nullable HTTPS allowlisted host, never fetched), retrieval_score=null,
access_control_state=NOT_VERIFIED, provenance_state=NOT_VERIFIED,
content_digest=SHA256 UTF-8 excerpt, index_freshness_state=NOT_VERIFIED,
source_age_state=RECENT|STALE|NOT_VERIFIED, qualification_state=HOLD.
Upstream citation_id is request-local; never repurpose it as stable source document identity.
Recent source timestamps do not prove index freshness. Naive/future timestamps stay unknown.
An envelope digest binds all normalized fields for tamper detection, not authentication.
Unknown provider metadata cannot set ACL, authority, verification or qualification.
Duplicates within a response collapse by source locator and content digest; different excerpts
remain separate candidates, not independent witnesses. Replay is read-only with no effects.

## Errors and evidence
Missing principal/tenant or mismatches: ACCESS_NOT_VERIFIED, no candidates or call.
Disabled/unadmitted/timeout/network/HTTP failure: RETRIEVAL_UNAVAILABLE.
Malformed schema/unsafe source URL/oversize/duplicate JSON keys: INVALID_RESPONSE.
401=AUTHENTICATION_FAILED, 403=AUTHORIZATION_FAILED. No upstream exception/body echoed.
Audit log contains fixed event/status/count only, never query, credential or document content.
No candidate is written to SQLite or promoted to admissible evidence. Existing evidence ledger
and fenced finalization remain authoritative. Live proof and manager approval are unfinished.

## Synthetic DISPATER seam
Mock upstream-schema corpus: towing dispatch/invoice/service evidence, oilfield ticket,
equipment record and procedure. Fixed towing fixture invokes existing Decimal audit engine
separately; retrieved prose is never parsed as a charge or approval. XAELI NOW/CHANGED/NEXT/WHY/PROOF
shows candidates with HOLD, no historical delta and human-review next step. No new UI/app/database.
The demo proves contract plumbing, NOT real Onyx interoperability or indexed-source authenticity.

## Verification plan and rollback
Tests cover strict schema, denial before egress, timeout/401/403/503, bounds, missing metadata,
stale/future dates, injection inertness, replay, redacted failures and digest tampering.
Full existing pytest, Ruff and Mypy; optional explicitly gated live test remains NOT RUN.
Rollback: revert feature branch commits; no data migration or deployment to roll back.
