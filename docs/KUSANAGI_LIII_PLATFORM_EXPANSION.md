# KUSANAGI LIII — One AUREX, staged capability delivery

Status: **HOLD** for production expansion. This is a dependency-controlled program, not a claim of working integrations.

## Locked cross-system rules
- One canonical backend authority boundary; no independent security authority from agents, website UI, XAELI, or orb.
- Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness.
- Default budget $0; no outbound messages, model spending, publishing, merges, or deployments without approval.
- Owner-only controls, server-side credentials, auditable actions, strict input schemas, no untrusted code execution outside isolation.
- Every capability reports **UNAVAILABLE / NOT VERIFIED / VERIFIED** based on observed evidence. UI demo is separate.

## Wave 0 — operational proof (blocking all other waves)
- Canonicalize regression_scan and regression-scan at ingress; persist only regression_scan.
- Implement real sqlite_roundtrip_v1 worker with fenced claim, cancellation, idempotency and atomic evidence finalization.
- Add negative tests: concurrent claims, lease expiry, cancellation races, idempotency conflict, DB failure, false success, auth, zero budget.
- Owner website button → authenticated proxy → worker → evidence → UI, proven with a recorded exact SHA and independent verifier.
- Never convert self-reported worker evidence to VERIFIED without an independent check.

## Wave 1 — Division A: Engineering Studio
- Read-only repository inventory and consented per-repo scopes.
- Bounded lint/test/contract jobs in ephemeral isolated workers, with resource and egress limits.
- Versioned reproducibility manifests, artifact hashes, and release readiness dashboard.
- No automatic PR merge or deployment.

## Wave 2 — Division B: Intelligence Studio
- Scientific experiment registry: dataset provenance, hypothesis, protocol, control, execution and adversarial evaluation.
- Optional model adapters disabled until configured; explicit per-job budget authorization.
- Voynich/Rongorongo/Linear A corpus studies are hypotheses, never verified translations without independent anchors.
- Signed evidence verification with trust roots independent of the worker.

## Wave 3 — Division C: Growth Studio
- Draft-only marketing research, positioning, outreach and investor materials with sourced claims.
- Website analytics only with configured consent/privacy-safe data sources; no invented visitor counts.
- No emails, social posts, purchasing, or campaign launch without explicit per-action approval.
- Pricing hypotheses must not be reported as revenue or demand.

## Wave 4 — BCXMET / XAELI / DISPATER
- BCXMET receives advisory evidence only; security authority remains with canonical app owner.
- XAELI explains state and proof, cannot grant clearance or execute privileged changes.
- DISPATER remains separate industrial domain with explicit permissions and safety review.
- No cross-tenant data access, no credentials exposed in frontend, no app security guarantees from demos.

## Wave 5 — Agent command center and SaaS
- Coordinator DAG, isolated worktrees, role-scoped agents, bounded execution, human release gate.
- Tenant isolation, quota enforcement, metering, billing integration only after explicit authorization.
- Security review, privacy/retention, recovery, incident response and independent acceptance tests before external customers.

## Frontend alignment
Lovable project 811ffc43-2c8b-4c88-ab4c-4de668d089cb, /admin/sovereign-studio.
Preview commit 5931bf878d9bddc22fd65c7232fee5d7a27fa4c0 reported 183 tests passing, typecheck passing; owner-authenticated end-to-end test **NOT RUN**.
Frontend capability identifiers for BCXMET/XAELI/orchestration are provisional and must be contract-frozen before declaring availability.

## Release proof per wave
Exact main base SHA; change SHA; test commands and logs; failure-injection results; independent verifier identity and evidence; backend/website contract check; explicit merge and deployment approvals.
Any missing critical proof => HOLD.
