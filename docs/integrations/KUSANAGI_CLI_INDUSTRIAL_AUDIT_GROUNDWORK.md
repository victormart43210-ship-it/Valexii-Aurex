# KUSANAGI CLI — Industrial Audit Groundwork (design baseline)

Status: **DRAFT / NOT VERIFIED / NO PRODUCTION AUTHORITY**. Scope: oilfield and towing/recovery audit readiness. This document does not assert DOT or IRS compliance.

## Objective and bounded first slice
Reuse the canonical AUREX EvidenceLedger, existing SQLite storage, API authentication, and XAELI presentation. The existing `aurex/governance_math/industrial_readiness.py` is synthetic-only, read-only and advisory. Do **not** connect it to live customer records before tenant and source-admission controls are independently tested.

## Three research candidates (adoption gated)
1. **OPA (Apache-2.0)**: evaluate Rego or equivalent deterministic rules against a versioned, independently reviewed applicability matrix. Prototype out-of-process with synthetic inputs and a pinned upstream version. Do not let OPA independently authorize an effect or declare regulatory compliance. Benchmark against existing Python classifier before adding deployment dependencies. https://github.com/open-policy-agent/opa
2. **Docassemble (MIT)**: study guided questionnaires and reproducible document assembly; prototype a minimal PDF audit-packet generator using the existing Python toolchain before adding a full server. Maintain attribution for reused code. Include missing-record notices and evidence manifests; never claim a packet proves compliance. https://github.com/jhpyle/docassemble
3. **immudb (Business Source License for current code)**: **DESIGN REFERENCE ONLY**, not a dependency or code-copy target. Its commercial license must be reviewed before any incorporation. Prefer strengthening the existing SQLite evidence ledger with SHA-256 canonicalization, previous-record hash linkage, external checkpoint signatures, independent verifier, tamper/replay tests and restore verification. https://github.com/codenotary/immudb

## Regulatory evidence rule contract
A rule is a reviewed, versioned record: `rule_id`, `version`, `jurisdiction`, `operator_scope`, `effective_from`, `effective_to`, `source_url`, `source_retrieved_at`, `reviewer_id`, `reviewed_at`, `required_category`, `applicability_predicate`, `retention_basis`, `finding_severity`.
- A rule is **NOT APPLICABLE / UNKNOWN** unless its operator, vehicle, driver and jurisdiction scope is explicitly established. A missing applicability decision never becomes PASS.
- Regulatory text and forms are **untrusted inputs** until checked against current official FMCSA/eCFR sources by a human reviewer. No scraping-driven automatic rule promotion.
- Start with **illustrative** categories: driver qualification, inspection, maintenance, accident register, dispatch/service tickets and insurance; do not assert universal applicability or retention intervals. Relevant official reference: https://www.fmcsa.dot.gov/regulations/search and https://csa.fmcsa.dot.gov/safetyplanner/MyFiles/SubSections.aspx?ch=23&sec=66&sub=152

## Evidence and tenancy contract
Each admitted item needs `tenant_id`, `record_id`, `category`, `source_sha256`, `received_at`, `effective_at`, `expires_at`, `origin`, `provenance`, `redaction_status`, `review_state`, `revision_of`, and `evidence_receipt_id`. An authorized backend MUST derive tenant identity from the authenticated principal, never from an arbitrary browser-supplied tenant ID. Isolate database queries, storage paths, and audit exports. Enforce least privilege and avoid logging credentials or unredacted sensitive data.

The first classifier checks **inventory only**, not source authenticity, regulatory applicability, or external independence. Distinct hashes do not necessarily indicate a genuine conflict (e.g. legitimate revisions); its CONFLICTING finding requires human review.

## Planned UX contract
- **NOW:** observed missing, expired, conflicting, unverified inventory counts.
- **CHANGED:** changes since last independently evidenced snapshot.
- **NEXT:** bounded recommendations and human-review assignments, never unauthorized effects.
- **WHY:** applicable rule version, explanation and limits.
- **PROOF:** source digest, receipt, provenance, review state, and independently verifiable ledger checkpoint.
Never display a green compliance badge based on document presence or AI agreement.

## Synthetic acceptance gates
- [ ] Existing classifier passes Ruff, Mypy and pytest; negative tests for duplicates, malformed digests, future-dated and expired records, revisions, unavailable rule source, conflicting policy versions and missing applicability.
- [ ] Test tenant A cannot query tenant B through API, export, retrieval or background worker.
- [ ] Test adversarial input in uploaded text cannot change rule policy or authorization.
- [ ] Test tampered ledger entry, missing receipt, replay, key rotation and restored backup; failure must demote to NOT VERIFIED.
- [ ] Test authenticated server-side proxy -> API -> SQLite receipt -> read-only findings -> XAELI presentation with synthetic records and exact SHA evidence.
- [ ] Generate a synthetic, clearly labeled audit packet with a manifest, missing-document section, timestamps, and disclaimer.
- [ ] Independent reviewer reproduces results and confirms no customer data, paid inference, new public endpoints, or production deployment.

## Integration and release
Before any implementation beyond this branch: inspect current `origin/main`, compare the October 22 Railway deployment (still tracking `integration/kusanagi-xvi-railway` when checked) against main, and establish the published Lovable source revision. Do not equate a healthy Railway service with a verified worker/database transaction. Preserve website pictures, homepage BCXMET security positioning, and canonical architecture. No extra repositories, no new cloud services, no external paid inference. PR into main after independent review; **MERGE HOLD / DEPLOY HOLD**.
