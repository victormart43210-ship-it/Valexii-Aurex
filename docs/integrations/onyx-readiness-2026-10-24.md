# Onyx × AUREX — integration readiness (2026-10-24)

Status: **PREPARATION ONLY / NOT INTEGRATED / RELEASE HOLD**. No credentials, model calls, indexing, external data transfer, production changes, or paid deployment authorized.

## Purpose
Evaluate Onyx Community Edition as an **untrusted, read-only retrieval source** for owner-only XAELI and AUREX. Onyx does **not** become an authority or challenger capable of certifying its own outputs.

## Target topology
1. Authorized operator requests retrieval through the existing AUREX API.
2. AUREX authenticates, enforces tenant/source allowlists and query budgets, and asks an optional Onyx adapter for relevant documents.
3. Onyx returns excerpts with document identifiers, source URIs, timestamps, access metadata and retrieval method when available.
4. AUREX records evidence provenance, independently checks source and freshness, then applies Evidence → Qualification → Reality → Authority → Effect.
5. Missing source, denied access, stale evidence, provider errors, ambiguous citations, or conflicting evidence yield **HOLD / INSUFFICIENT / STALE**, never PASS.
6. Website displays sourced explanation with a clear **NOT VERIFIED** label; no write/action capability is granted.

## Pilot boundary
- **First dataset:** small synthetic documents written for this evaluation, with explicit false/conflicting/stale cases.
- **Excluded:** customer records, email bodies, financial transactions, industrial operational secrets, BCXMET proprietary detection logic, private repositories, credentials, production logs, and patent-sensitive internals.
- **Access:** owner-only, server-to-server, default disabled; no browser API key; no public XAELI indexing.
- **Cost:** $0 authorized external inference spend. Self-hosted software may still incur infrastructure cost: request approval before starting containers or cloud services.
- **Privacy:** no indexing or telemetry export until data retention, access control, deletion and licensing are reviewed.
- **Safety:** no prompt from a retrieved document can change policy, call tools, issue commands, or grant authority.

## Adapter contract proposal (freeze before implementation)
```json
{
  "provider": "onyx",
  "status": "UNVERIFIED",
  "query_id": "opaque-request-id",
  "retrieved_at": "RFC3339 timestamp",
  "results": [{
    "source_id": "stable-id-or-null",
    "source_uri": "allowlisted-uri-or-null",
    "title": "document-title",
    "excerpt": "untrusted-text",
    "source_updated_at": "RFC3339-or-null",
    "retrieval_score": null,
    "access_scope": "operator-approved-scope"
  }],
  "errors": []
}
```
Contract is a **proposal**, not a claim about Onyx's current API response. Map and version it only after verifying actual Onyx API docs and sample payloads. Never treat scores as truth.

## Work packages
1. Confirm Community Edition MIT / Enterprise Edition restrictions and features; record exact Onyx version/commit.
2. Determine whether Onyx exposes an authenticated **search-only** endpoint with per-document citations and usable ACL enforcement; capture sanitized example response.
3. Assess deployment footprint. Onyx's full Docker stack requires databases/search infrastructure; do not assume it fits the small Chromebook or current Railway budget.
4. Implement an optional, fail-closed adapter behind `ONYX_ENABLED=false` with short timeouts, no retries by default, strict host allowlist, redacted logs, and zero authority.
5. Add contract tests: disabled provider, timeout, invalid JSON, stale source, missing URI, duplicate citations, injection attempt, forbidden tenant/source, empty result, contradictory sources, revoked access.
6. Integrate into owner-only XAELI **only after** independent tests, privacy review, deployment-cost approval, and explicit release approval.

## Questions for Lindsey Milberg — October 28, 2026, 10:00–10:30 Central
- What is the supported API for retrieving ranked source passages and stable citations **without** generating an LLM answer?
- Can Onyx index a private GitHub repository with path-level permissions, and what is retained after connector removal?
- Which features require Enterprise licensing (SSO/RBAC/ACL, connectors, API access, audit logs)?
- Can Community Edition run entirely self-hosted with local embeddings and Ollama, without paid model APIs?
- What is the minimum realistic CPU, RAM, disk, and ongoing cost for a 1–5-user pilot?
- How can we prevent indexed content from being sent to third-party inference providers?
- Can they supply a sandbox or a 30-minute technical walkthrough using synthetic documents?

## Acceptance evidence (currently NOT RUN)
- [ ] Exact version/license recorded
- [ ] Retrieval-only API demonstrated with citations
- [ ] ACL/tenant isolation independently tested
- [ ] Injection and stale-source demotion tests PASS
- [ ] Synthetic-only end-to-end test through AUREX PASS
- [ ] Cost and retention reviewed
- [ ] Operator explicitly approves staging activation

References: https://github.com/onyx-dot-app/onyx ; https://github.com/onyx-dot-app/onyx/blob/main/LICENSE ; https://github.com/onyx-dot-app/onyx/blob/main/deployment/docker_compose/README.md
