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

## Existing retrieval convergence — repository inspection (2026-10-24)
Inspected canonical `main` at `f2db438f0020dbd455bcb5c7b21b7352d133bf2c`. Do **not** replace or duplicate these existing capabilities:

| Existing file | Observed behavior | Integration decision |
| --- | --- | --- |
| `aurex/governance_math/retrieval.py` | Deterministic, local $0 TF-IDF incident nearest-neighbor search; bounded corpus (1000), description (4096), query (512), deduplicated lineage; each match `CANDIDATE_ONLY_NOT_VERIFIED`. | **Retain** as local/offline incident baseline; no new embedding dependency. |
| `aurex/governance_math/spine.py` | Read-only `retrieve → plan → test next` combining incident candidates with bounded remediation and information-gain probes. | **Retain** as advisory reasoning path; no automatic effects. |
| `aurex/web_adapter.py` | Existing website/backend job adapter; not a document search index. | **Reuse existing API/auth conventions**, do not treat as retrieval evidence. |
| `aurex/adapters/ollama.py` | Existing optional local model adapter. | Potential future embedding/inference provider only after separate benchmark; no automatic model download. |

Search of default-branch code found **no confirmed ChromaDB, FAISS, or Deep Lake integration**. Absence in code search does not prove absence in other repositories, branches, or local worktrees. Audit those separately before adopting dependencies.

### Unified retrieval contract (proposed)
AUREX calls a single `RetrievalBroker` interface, not a chain of competing agents:
- **local_incident**: existing TF-IDF `retrieve_incidents` for bounded, admitted incident records.
- **onyx**: optional external search connector for owner-approved document sources; default disabled.
- **deeplake**: **NOT ADOPTED**; evaluate only if Onyx's native hybrid index fails measured needs.
- All sources produce candidate passages with `provider`, `source_id`, `source_uri`, `content_digest`, `retrieved_at`, `source_updated_at`, `access_scope`, `status=CANDIDATE_ONLY_NOT_VERIFIED`, and errors. Local incident matches keep existing immutable fields and are adapted without changing their public API.
- Broker must never silently combine incompatible relevance scores. Rank within provider, dedupe by source digest and lineage, and expose provenance for independent qualification.
- Validate allowlisted URI schemes/hosts, deny cross-tenant access, enforce size/query limits and timeouts, redact logs, and refuse external egress by default.
- All retrieved text is untrusted input. **AUREX alone** determines admissibility; Brain Trust provides independent challenge; XAELI displays explanation. **Hermes deferred by operator**.

### Implementation sequence
1. Inventory other user-owned GitHub repositories and active PR branches for existing parsers, embeddings, vector indexes, hybrid search and source adapters. Do not claim the canonical-main search covers all of them.
2. Freeze and test the normalized candidate schema against existing incident search, with no behavior changes.
3. Add a **disabled** Onyx adapter behind explicit owner-only configuration; synthetic fixture tests only.
4. Run baseline TF-IDF vs Onyx hybrid retrieval on the same synthetic documents, measure citation coverage, stale-source rejection, latency and resource cost.
5. Admit a second vector store **only if** Onyx cannot meet measured requirements and licensing/security review approves.
6. Preserve KUSANAGI CL timestamp/auth fixes and keep production HOLD. Never merge audit branches blindly.

## BCXMET canonical spine convergence — architecture proposal (2026-10-24)

**Scope:** integrate the existing read-only AUREX `governance_math.spine.advise` and Onyx retrieval candidates with BCXMET's existing governance **without** importing proprietary BCXMET code into this public repository. This is a design/contract amendment only, not a running implementation.

### Control-plane and evidence-plane separation

```text
BCXMET / XAELI user intent
   → owner/tenant authentication + IN/CORE/OUT/TIME scope
   → AUREX coordinator: define claim, scope, budgets, evidence requirements
   → retrieval broker (local TF-IDF | optional Onyx) [UNTRUSTED CANDIDATES]
   → evidence ledger: source digest, identity, scope, timestamps, lineage
   → QUALIFICATION: provenance, ACL, freshness, contamination, independence
   → REALITY: independent source check / adversarial challenge (Brain Trust)
   → AUTHORITY: BCXMET's existing authorized policy/lease/revocation gate
   → EFFECT: only explicitly authorized action; default no effect / HOLD
   → XAELI explanation + source citations + uncertainty
```

**Do not confuse roles:** AUREX can independently challenge and report evidence, but **cannot itself grant BCXMET runtime authority**. The BCXMET authority boundary is separate and must explicitly consume admitted evidence. Brain Trust disagreement demotes or triggers review; model consensus cannot self-certify.

### Preserve both spines
- **BCXMET UnifiedReasoningSpine:** product's canonical evidence/qualification/reality/authority/effect progression, EvidenceLedger, Advocate/Challenger/Arbiter, Sentinel/CUSTOS demote-only oversight, historical truth vs current authority, lease freshness/revocation.
- **AUREX research spine (`aurex/governance_math/spine.py`):** `retrieve → plan → test next` advisory analysis, `ResearchAdvice.gate` REVIEW_REQUIRED/HOLD, `authority=ADVISORY_ONLY_NO_EXECUTION`. This is a **subroutine inside investigation**, not a replacement for the BCXMET spine.
- **Onyx:** optional untrusted retrieval adapter; never grants authority, writes product policy, or supplies its own independent witness.
- **IIT Delhi LRPlan-inspired planning:** optional proposal generator only after independently verifying upstream identity/license and actual benefit; no automatic install.
- **Hermes and Deep Lake:** explicitly DEFERRED per operator decision.

### BCXMET Home and presentation boundary
- Canonical presentation: **NOW → CHANGED → NEXT → WHY → PROOF**. Show observed current state, evidence-backed delta, next safe review step, explanation and citations; absent evidence shows NOT YET VERIFIED, not SAFE.
- XAELI actions: Explain it / Show proof / Help me review it. No authority promotion via UI.
- Orb: COMET DYNAMICS presentation only, **ORB MOTION AUTHORITY = NONE**; no return edge from animation to evidence, policy, or security decisions.
- Product authority requires a separate explicit product policy decision with current lease and revocation checks; never infer authority from historical CLEAR or a prior passing audit.

### Proposed normalized handoff
```json
{
  "request_id": "opaque-id",
  "tenant_scope": "authorized-tenant",
  "claim_id": "opaque-claim",
  "candidate_evidence": [],
  "qualification": "NOT_VERIFIED",
  "reality": "NOT_VERIFIED",
  "challenge": "NOT_RUN",
  "authority": "NONE",
  "effect": "NONE",
  "presentation": {"now": "UNKNOWN", "changed": [], "next": "REVIEW", "why": "insufficient verified evidence", "proof": []}
}
```
This is a proposed boundary envelope, **not an existing API contract**.

### Required negative tests before any implementation admission
1. Onyx returns an injected instruction to disable BCXMET policy → ignored, HOLD.
2. Local TF-IDF yields high similarity with invalid/absent independent source → candidate only.
3. Same document retrieved by Onyx and local search → **one lineage**, not two independent witnesses.
4. Expired lease or revoked permission after prior CLEAR → no current authority.
5. Source updated in the future, stale, missing digest, or unauthorized tenant → demote.
6. Brain Trust agrees with its own generated answer → not independent verification.
7. Offline Onyx or model → existing local retrieval continues where authorized, but never invents missing proof.
8. Orb/comet rendering state changes → zero impact on authority or policy.
9. Website request tries to invoke retrieval with browser-held service token → reject.
10. Verify reverse audit **ROTAS**: Result → Authority → Truth → Admissibility → Source, with immutable historical failures.

### Integration acceptance
Freeze the contracts, identify BCXMET private boundary owners, compare against current CL timestamp regression fix, run exact-SHA tests and independent adversarial review. Public repository receives **interfaces and synthetic fixtures only**; private BCXMET code remains private. No merge or deployment without explicit authorization.
