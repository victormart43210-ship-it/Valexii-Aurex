# OPERATION KUSANAGI CCLXIII — VALEXII.COM Implementation Foundation

Date: 2026-11-06
Status: PLANNING ONLY / PRODUCTION HOLD
Source: Firecrawl public-site inventory and crawl, 2026-11-06; PR #186 observed head 5285202699c362c7a10abcb02a8b5c8591517f7c.
Scope: one canonical Valexii-Aurex repository. This document is not evidence of deployment, independent runtime verification, or completed implementation.

## Baseline and nonnegotiable gates

- Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness.
- Financial authority NONE; production release HOLD; paid external inference OFF; customer data prohibited pending authorized pilot readiness.
- XAELI advisory only; BCXMET Orb presentation only.
- Preserve $385 identified, $150 withheld, $0 confirmed recovered in synthetic golden ledger.
- Never merge old Jules code over hardened financial controls. Verify the recovery branch and exact SHA before importing.
- No secrets in browser, public JSON, logs, or Git.

## Workstreams / implementation contracts

### W0 — Inventory and deployment identity (blocking)
Owner: integration coordinator.
Inventory public routes, protected routes, current frontend and backend branches, actual deployed Railway service SHAs, auth boundary, and all demo/live status badges. Produce machine-readable route-to-capability matrix with owner, backend endpoint, data class, deployment SHA, evidence status, and tests. Never treat an old passing CI commit as current deployment proof.
Exit: every major website surface maps to a real implementation, simulated fixture, or explicit NOT_VERIFIED.

### W1 — Website-to-AUREX transport (P0)
Owner: website/backend integration.
Verify server-side API proxy, service authentication, health/capability/evidence/budget/job read-only checks, freshness clocks, CORS, errors, timeouts, and secret redaction. Use staging and synthetic fixtures only. Invalid/future timestamps fail closed.
Exit: browser → website server → authenticated AUREX endpoint → correlated evidence receipt, with unauthorized and outage tests.

### W2 — DISPATER authenticated audit (P0)
Owner: DISPATER + frontend.
Build a typed request/response contract with tenant scope, synthetic fixture ID, evidence IDs/digests, Decimal amounts, qualified findings, NOW/CHANGED/NEXT/WHY/PROOF, reviewer HOLD, and receipt. Wire existing hardened reconciliation endpoint; no browser API secrets; no auto-approval.
Exit: Playwright or equivalent browser E2E demonstrates one synthetic audit and exact ledger, plus negative tests for duplicate/orphan/tenant mismatch/invalid provenance.

### W3 — XAELI private Qwen (P0)
Owner: AUREX model runtime.
Verify deployed model identity, internal network, service auth, private staging request, timeouts, no external paid fallback, response provenance and distinction between scripted and live. No model claims of audit/security authority.
Exit: real synthetic prompt through website server with traceable model identity and explicit NOT_VERIFIED if blocked.

### W4 — Durable audit storage and replay (P1)
Owner: backend/platform.
Verify worker execution, durable job/evidence read-back, restart recovery, backups, deletion and retention, tenant isolation, rollback; distinguish volume attachment from persistence proof.
Exit: restart-and-read-back test and restore drill with independently inspected receipts.

### W5 — Offline ZIP/USB bridge (P1)
Owner: offline engineering.
Build on scripts/valexii_offline_kit.py. One safe launcher: locate archives in home/Downloads/mounts; hash and verify; reject traversal, symlinks and decompression bombs; detect duplicates; preserve originals; discover real Git checkout; resume via checkpoints; produce manifest and synthetic offline test. USB access is environment-dependent.
Exit: one-command synthetic test and documented real-device verification steps; never assert inaccessible USB was processed.

### W6 — Customer pilot boundary (P1, no real data yet)
Owner: platform/security.
Design authenticated tenant/RBAC, secure upload quarantine, data agreements, retention and purge, immutable evidence and independent reviewer gates. Begin with authorized CSV/Excel adapter, then consider one documented external connector. Teams/QuickBooks/etc remain PLANNED until separately verified.
Exit: synthetic cross-tenant isolation, retention/deletion, authorization, and provenance tests.

### W7 — Website lead capture and truthfulness (P1)
Owner: website.
Verify pilot form validation, consent, anti-spam, durable inquiry storage, notification delivery separately from storage; no live sensitive customer records. Consolidate product readiness from a single versioned status manifest. Public statuses must reflect deployed SHA and independently verified checks, not draft branch achievements.
Exit: form test receipts and consistent labels across /, /development-status, /dispater, /dispater/showcase, /xaeli, /aurex/ox.

### W8 — Launch assurance (P2)
Owner: independent verifier.
Accessibility including keyboard/TalkBack/reduced motion; mobile responsive; OWASP and authorization tests; dependency/secret scanning; CI and deployment provenance; rollback and observability; human release approval.
Exit: reviewable release packet, explicit blocked conditions, no automatic deploy.

## Execution waves

0. Inventory and contract freeze (W0), create issue/PR mapping; savepoint.
1. Parallel W1 and W2 contract tests after freeze; serialize shared auth and evidence changes; savepoint.
2. W3 model verification and W5 offline bridge in isolated branches; savepoint.
3. W4 persistence and W6 pilot gates; savepoint.
4. W7 public truthfulness and W8 independent assurance; final review PR.

## Evidence and acceptance schema

For each workstream record: source SHA, deployment SHA (if any), branch/PR, endpoint/route, synthetic fixture, exact command, environment, result PASS/FAIL/SKIP/BLOCKED/NOT_VERIFIED, independent witness, unresolved risks, and next action.

Required artifacts: docs/operations/CCLXIII_ROUTE_CAPABILITY_MATRIX.json; CCLXIII_API_CONTRACTS.md; CCLXIII_DEPLOYMENT_EVIDENCE.json; CCLXIII_E2E_TEST_REPORT.json; CCLXIII_SECURITY_GATES.json; CCLXIII_RELEASE_DECISION.json; RECOVERY.json; RESUME.md.

## Public crawl observations requiring verification

- /dispater/showcase is display-only, with simulated tenant selectors and approvals; Teams and other connectors PLANNED.
- /xaeli is scripted/developmental; private live model not independently verified.
- /aurex/ox shows UNKNOWN/HOLD for live API checks and reports historical staging observations.
- /development-status is a manually published snapshot, not live telemetry.
- /contact distinguishes saved inquiry from email delivery.
- Public route inspection does not verify protected owner routes or live backend.

## Stop conditions

Stop and preserve a savepoint on unexpected financial result, tenant leakage, unverifiable model identity, lost evidence lineage, secret exposure, storage corruption, unauthorized infrastructure action, or source/deployment SHA mismatch. No unsafe merge, no production deployment, no paid inference without owner authorization.
