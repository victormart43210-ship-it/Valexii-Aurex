# KUSANAGI CCCXLVIII — SOVEREIGN ASCENSION Ω
Status: REVIEWABLE DESIGN FREEZE; no runtime implementation or benchmark claim
Parent foundation: `docs/operations/KUSANAGI_CCCXLVII_GENESIS_ASCENSION_FOUNDATION.md`
Canonical repo: `victormart43210-ship-it/Valexii-Aurex`
MERGE AUTHORITY NONE | PRODUCTION HOLD | FINANCIAL AUTHORITY NONE | PAID INFERENCE OFF | CUSTOMER DATA PROHIBITED

## North star
Maximize independently verified useful work per total dollar and second, subject to hard security, privacy, quality and human-authorization constraints. “100×” is an experiment hypothesis, not an achieved speedup or guarantee. Avoid optimizing proxy benchmarks at the expense of real correctness.

## Identity and coordination
- XAELI: user intent, explanations, owner decisions; no trusted effect authority.
- ZAYLI: candidate task graphs, bounded worker assignment, conflict detection; no trusted effect authority.
- Governors are on-demand role capabilities: OCH architecture; PHUL understanding; PHALEG adversarial tests; OPHIEL engineering; BETHOR cost; HAGITH UX; ARATRON qualification coordination. None is a sole witness or policy authority.
- Ghost: stable agent identity and lineage, cryptographically bound to registered manifests. Never interpret “ghost” as sentience.
- Shell: isolated execution instance with signed/validated configuration, tenant scope, process/resource limits, lease, generation and authority epoch.
- Face: presentation plus *requested* capability profile. Switching face never directly grants tools, identity, data access, or permission.
- AUREX trusted control plane owns state transitions, policy decisions and durable receipts; AUSEKLIS/CUSTOS/SHRIKE and independent tests qualify consequential results.

## Core invariants (P0)
1. Deny by default. Validate capability, owner authorization, tenant, budget, expiry, generation, policy epoch and evidence freshness immediately before each consequential effect.
2. No descendant, face, shell or model can amplify its ancestor's permissions, financial limits, tenant access or external network access.
3. Leases and generation fencing are durable; stale workers fail closed after crash, retry, cancellation, reconfiguration and face transition.
4. A face switch is a transaction: PREPARE → CHECKPOINT → VALIDATE → FENCE_OLD → ACTIVATE_NEW → RECEIPT; failure must roll back or stay safely blocked. Prevent old/new simultaneous effect authority.
5. Model output is untrusted data. Never execute model-produced commands or tool arguments without schema validation and explicit policy authorization.
6. Evidence is an append-only DAG with source hashes, root independence, timestamp/freshness and qualification. Copied or distilled answers do not become independent witnesses.
7. Historical success is not current authority. UNKNOWN, STALE, CONTRADICTED and WITHHELD never silently become CLEAR.
8. Training data, model artifacts and benchmarks are provenance-bound; no contamination of held-out evaluation by candidate training or prompt selection.
9. Human approval is required for production release, spending, customer-data access, external paid inference and privileged capability changes.
10. UI and persona are presentation-only. They cannot set policy, write qualification, bypass review or self-certify.

## Minimal versioned contract proposals
`TwinMission.v1`: mission_id, owner_scope, tenant_id, objective_digest, risk_tier, created_at, policy_epoch, max_cost_usd, deadline, approved_tools, approval_receipt.
`TaskNode.v1`: node_id, mission_id, dependencies, input_digests, output_schema, capability_requirements, timeout, retry_limit, idempotency_key, verification_policy.
`AgentGenome.v1`: agent_id, parent_id, governor_role, ghost_id, model_digest, adapter_digest, allowed_faces, max_children, permissions, tenant_scope, cost_cap, creation_receipt.
`ShellLease.v1`: shell_id, agent_id, mission_id, tenant_id, generation, authority_epoch, lease_id, expires_at, allowed_effects, cancellation_token.
`FaceManifest.v1`: face_id, version, compatible_models, required_tools, retrieval_scopes, display_profile, input_output_schema, risk_tier.
`TransitionReceipt.v1`: from_shell, to_shell, from_face, to_face, old_generation, new_generation, policy_decision_digest, checkpoint_digest, outcome, timestamp.
`ExperimentReceipt.v1`: source_sha, environment_digest, model_hash, dataset_roots, train_test_split_digest, seed, baseline, metric_definitions, results, reviewer_id, independence_attestation, cost.
Schemas must be reconciled with existing repo models before implementation; don't create shadow registries.

## Capability compiler and scheduler
- Parse user request into proposed task graph, validated against a deterministic schema.
- Prefer Tier 0 deterministic computation; Tier 1 approved local model; Tier 2 qualified specialist; Tier 3 external paid inference requires separately explicit approval (OFF by default).
- Route on measured correctness/calibration, latency, memory, energy if measurable, privacy and total cost. Never trade away mandatory verification.
- Reuse a qualified agent before generating a new one; reuse model weights with distinct role configurations when isolation permits.
- Cache only tenant-scoped, non-sensitive, provenance-qualified outputs with freshness and invalidation; avoid cached authority decisions.
- Batch compatible read-only inference, enforce backpressure, concurrency ceilings and cancellation; do not launch seven Governors for every task.
- Model Forge should try deterministic rules, retrieval, prompt optimization and adapter selection before costly fine-tuning; all changes held for qualification.

## Experiment plan: prove or falsify 100×
Baseline: existing deterministic DISPATER reconciliation plus existing Model Forge starter; document what actually runs. Use fixed synthetic fixtures, held-out ground truth, multiple seeds, and representative difficult cases.
Comparators: deterministic-only, local-small-model, selective escalation, Governor swarm, and proposed adaptive router.
Metrics: verified correct findings per dollar, precision, recall, false-positive rate, p50/p95 latency, peak RSS, queue throughput, energy when measured, cost breakdown, tenant leakage, unauthorized effects, cancellation/replay failures. Report denominators, confidence intervals when appropriate, hardware and model identity.
“100×” may only be reported when measured on a specified workload, against a disclosed baseline, with equivalent quality and independent reproduction. Otherwise report actual factor or NOT_VERIFIED.

## Implementation waves
W0 inspect current main, open PRs and original MEDAURUS/BCXMET source/APK availability; transfer only independently verified behavior, label specification-only reuse.
W1 P0 trusted policy enforcement, durable lease fencing and adverse tests.
W2 Ghost/Shell/Face contracts, atomic transition state machine and rollback/replay tests.
W3 TwinMission/task compiler, seven Governor registry, scheduler and cost telemetry.
W4 Model Forge provenance, held-out experiment ledger and gated candidate nursery.
W5 GENESIS-001 DISPATER synthetic comparison and adversarial evaluation.
W6 dashboard with NOW → CHANGED → NEXT → WHY → PROOF; accessibility and reduced motion.
W7 exact-SHA CI, independent security and cost evaluation; owner approval required to advance.

## Acceptance tests (negative cases mandatory)
Cross-tenant read/write denied; revoked capability denied at effect time; old-generation tool call denied; duplicate idempotency key not double-applied; expired lease denied; crash during face switch cannot leave two authorized shells; failed checkpoint blocks transition; child privileges are subset; model injection cannot execute tools; derived evidence cannot increase independent-root count; stale benchmark cannot promote candidate; failed or missing reviewer cannot certify; zero-dollar cap blocks paid inference; cancellation and rollback preserve audit; offline/low-memory mode degrades gracefully.

## No false completion
This document freezes proposed architecture and testable contracts only. It does not assert runtime code, actual BCXMET APK fidelity, autonomous training, 100× gains, 9.9 quality, passed CI, or production readiness. Do not merge or deploy on the strength of this document.
