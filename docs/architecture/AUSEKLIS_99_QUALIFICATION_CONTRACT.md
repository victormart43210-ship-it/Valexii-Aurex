# OPERATION KUSANAGI CCCXXIX — AUSEKLIS 9.9 Qualification Contract
Status: DRAFT / DESIGN ONLY / NO PRODUCTION AUTHORITY
Scope: canonical Valexii-Aurex repository; BCXMET runtime remains separately governed.
Date: 2026-11-07

## Non-negotiable existing boundary
This repository already contains an **advisory** AUREX research spine at `aurex/governance_math/spine.py` (retrieve → plan → test next). The BCXMET Android `UnifiedReasoningSpine` is a **different existing runtime boundary**. Do not replace, rename, duplicate, or assert these are one executable service. Converge by a versioned, non-authoritative interoperability contract; BCXMET retains its Metatron/Judge/EMET effect boundary. AUSEKLIS coordinates missions only. Production release HOLD; financial authority NONE; paid inference OFF; customer data prohibited in pilot; human approval for merge/release.

## Proposed 4D mission schema (v0; not yet implemented)
`MissionState {mission_id, intent, evidence_refs[], authority_snapshot_ref, observed_at, expires_at, policy_epoch, provenance_digest, tenant_scope, status}`
Original 4D: Ω_t=(I_t,E_t,A_t,τ_t). Authority snapshot is informational, not a bearer capability or persistent execution grant.
All missing, stale, ambiguous, invalid, conflicting, revoked, or unverified evidence yields explicit HOLD/REVIEW; never PASS.

## Component roles (one owner per responsibility)
- **AUSEKLIS:** orchestration, scheduling, budgets, bounded delegation, retries and recovery; NO effect authorization.
- **AUREX research spine:** local read-only retrieval, planning and proposed next tests; advisory-only.
- **BCXMET UnifiedReasoningSpine:** existing Android evidence and reasoning route; remains in its own canonical repository.
- **EvidenceLedger/provenance graph:** immutable source, digest, timestamps, dependencies and contradictory evidence; no fabricated observations.
- **Math Fabric:** typed registry of ProbabilityMath, NoisyOrFusion, robust baseline, entropy, JS divergence, EWMA, Bayesian and dependency-aware algorithms; each reports inputs, lineage, uncertainty, calibration, resource cost and expiry; no new global verdict score.
- **ZALI/Zaylee and XAELI:** differentiated candidate hypotheses, explanations and preserved dissent; no authority; avoid assuming independence when models/data overlap.
- **SHRIKE:** adversarial falsification; **SHRIKE Ghost:** reverse clean-room reconstruction, independently verified.
- **CUSTOS:** admissibility and governance challenge, can demote/HOLD, not self-authorize.
- **NIPSON:** forward/reverse convergence predicate; failure => HOLD.
- **LEVEL / Metatron / Judge / EMET:** existing product-specific deterministic effect gate and action governance; no authority imported from research proposals.
- **Sentinel:** integrity monitoring and demote-only intervention.
- **Teth Matrix:** nine-domain research taxonomy; historical/symbolic hypotheses never physical-security facts.
- **Hyperbolic Time Chamber:** task-appropriate metamorphic/adversarial test matrix, historically 7×8; not literal time.
- **POST-9.9:** reproducibility/qualification rubric; not an empirical score by its name.
- **Model Forge:** versioned skill/memory/training candidates, contamination checks and human-approved promotion; no self-modification of authority.
- **ASIE-1000/HLE:** held-out assessment; HLE evaluation-only, never training data.

## Safety properties to encode as executable tests
1. AUREX advisory response cannot mint BCXMET `GateDisposition` or effect authorization.
2. Loss of freshness, provenance, independence, verifier health or policy validity cannot increase authority.
3. Child capability is a subset of parent; tenant and purpose scopes never broaden.
4. Forward/reverse reconstruction disagreement => HOLD, even when twin models agree.
5. Duplicate sources/common-cause reports cannot satisfy independent-witness quorum.
6. Untrusted retrieved instructions cannot alter tool permissions, policies or effect boundaries.
7. Retried external effects use durable intent/idempotency; ambiguous completion => UNKNOWN_EFFECT reconciliation, not blind retry.
8. Crash recovery revalidates current evidence and authority; persisted pending intent is not permission.
9. Learning/memory proposals cannot change authority schemas, gates or thresholds without independent evaluation and human approval.
10. Golden Ledger synthetic case: identified $385; withheld $150; confirmed recovery $0; invoice discrepancy $10; confirmed invoice recovery $0. No exposure-to-recovery promotion.
11. Tests prove mathematical calibration, finite numerical outputs, invariance, provenance lineage and out-of-distribution abstention.
12. Physical Android and hosted staging claims remain NOT_RUN until exact SHA evidence exists.

## Qualification rubric (proposed; not achieved)
To earn a 9.9/10 engineering claim: all 12 critical invariants pass at exact candidate SHA; independently reviewed synthetic end-to-end AUSEKLIS → AUREX → BCXMET contract demonstration; failure injection and recovery; measured false positives/calibration/latency; security/tenant boundary verification; reproducible CI and reviewer signoff. No weighted average may compensate for a critical-gate failure. Score remains UNRATED pending evidence.

## Implementation sequence
W0 inventory actual source and reconcile two spines; freeze typed contract.
W1 write failing contract/property tests (no production effect code).
W2 add advisory adapters only, default disabled; verify schema and no new authority.
W3 test twin challenge and provenance-independent witness checks.
W4 synthetic Golden Ledger and BCXMET fixtures; chaos/failure recovery.
W5 independent review at exact SHA; owner decides any merge or deployment.

No auto-merge, release, deploy, customer data or spending authorized by this document.
