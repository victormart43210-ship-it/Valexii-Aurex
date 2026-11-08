# KUSANAGI CCCXLVII — GENESIS ASCENSION Foundation Contract
Status: DESIGN FROZEN FOR REVIEW ONLY / IMPLEMENTATION NOT VERIFIED
Canonical repository: victormart43210-ship-it/Valexii-Aurex
Merge authority: NONE. Production: HOLD. Financial authority: NONE. Paid inference: OFF. Customer data: PROHIBITED.

## Objective
Integrate MEDAURUS/BCXMET's evidence, freshness, lifecycle and fail-closed principles into the existing AUREX Model Forge. XAELI is the human-facing interpreter; ZAYLI the proposed mission planner. Both are advisory and neither is an execution authority. AUREX is the sole trusted scheduler and policy-enforcement boundary. Governors: OCH architecture, PHUL understanding, PHALEG adversarial testing, OPHIEL engineering, BETHOR budgets, HAGITH experience, ARATRON qualification coordination. AUSEKLIS/CUSTOS and independent ground truth supply qualification; human owner retains release authority.

## Grounded baseline / limitations
- `docs/architecture/BCXMET_AUREX_DISPATER_TRANSFER_MATRIX.md` states that `aurex/evidence_kernel.py` implements adapted provenance, independent roots, freshness, qualification. It explicitly states that JOSAI capability authorization is **library-only**, not wired to API endpoints; recovery chain is not persisted; Shield-to-job fencing not implemented. Matrix is based on specifications, **not APK code inspection**.
- `docs/architecture/BCXMET_APK_IMPLEMENTATION_INVENTORY.md` says APK/source inspection NOT PERFORMED. Do not assert Android behavior is verified.
- `workstation/model_forge.py` supports synthetic bigram demonstration and hashing a user-reviewed model manifest; no transformer training, fine-tuning or verified model-license authentication.
- Reuse existing `aurex`, workstation and website contracts; avoid duplicate repositories, control planes and synthetic claims of implementation.

## Transfer priority and engineering acceptance
P0 **Effect-time capability authorization**: enforce before every tool invocation and state mutation, not merely at plan creation. Tests: denied capability, tenant mismatch, revoked permission, stale generation, expired lease, failed verification, missing witness; zero unauthorized effects.
P0 **Generation/lease fencing** (Shield lifecycle analogue): mission_id, agent_id, generation, authority_epoch, lease_id, lease_expiry, tenant_id, cancellation state, idempotency_key; reject old workers after restart/reassignment. Persist fencing in durable storage, transactional compare-and-swap before effects; deterministic crash/replay tests.
P0 **Fail-closed truth**: UNKNOWN/STALE/WITHHELD/CONTRADICTED are never CLEAR. Historical PASS does not imply current authority. Qualification is demote-only without independently verified new evidence.
P0 **Independent provenance**: evidence DAG with root independence, content digest, model artifact hashes, dataset split identity, training recipe and exact source commit. Derivatives of one root never count as separate witnesses.
P1 **Agent Genome v1**: versioned schema with parent, model/adapter digests, tools, tenant, risk, budgets, expiry, no recursive privilege amplification; validate at registration and dispatch.
P1 **TwinMission/TwinPlan/TwinHandoff**: XAELI and ZAYLI separate roles and memories, shared immutable mission identifier; disagreement remains visible. Both are non-authoritative.
P1 **Governor capability registry**: seven named, on-demand roles; no permanently running seven-model requirement. Governor identity is a role, not independent proof.
P1 **Budget-aware intelligence router**: tier 0 deterministic, tier 1 local approved small model, tier 2 approved specialist, tier 3 paid external OFF unless separately explicitly authorized; benchmark quality, latency, RAM and total cost. Never bypass mandatory checks to save cost.
P1 **Sandbox nursery**: no production secrets, no customer data, no paid inference, no network by default, bounded runtime/children; candidate outputs quarantined.
P1 **Qualification ledger**: append-only experiment manifests, hidden holdout tests, ground-truth source, adversarial cases, rollback and negative results.
P2 **Optional LoRA training**: gated only after model license, data provenance, compute, reproducibility and security review. No auto-download or auto-promotion.
P2 **Twin dashboard**: NOW → CHANGED → NEXT → WHY → PROOF; display currentness, disagreement, provenance and approval state without inventing reality.

## Genesis-001 reference mission
Create and evaluate one synthetic DISPATER equipment-hours discrepancy specialist. Compare deterministic baseline, existing qualified local model (if available), and candidate agent on identical held-out fixtures. Capture precision/recall, false positives, calibration where applicable, p95 latency, memory, estimated cost, and unauthorized-action count. Candidate must not see hidden answers. Distinguish proposed design from observed outcome. Any improvement claim requires reproducible evidence and independent reviewer.

## Engineering execution order
0. Inspect main and open PRs (#209-#214, #193) and canonical backend/test contracts; produce a dependency/consolidation matrix; do not silently merge.
1. Add schemas and negative tests for AgentGenome, TwinMission and capability envelopes, extending existing contracts.
2. Wire enforcement at actual execution/API boundaries, with epoch/lease fencing and recovery tests.
3. Build durable registry and experiment/qualification receipts, retaining provenance and failed results.
4. Add on-demand Governor orchestration and cheapest-qualified-route selector.
5. Implement Genesis-001 synthetic end-to-end benchmark; test adverse inputs and cancellation.
6. Independent verification at exact candidate SHA: pytest, website tests, Ruff, Mypy, TS/build, workflow checks, security/tenant/epoch/replay tests. Record any NOT_RUN explicitly.
7. Keep draft PR and production HOLD until independent approval.

## Explicit non-goals
No Android APK equivalence claim without source/artifact inspection. No unsupervised self-modification, recursive privilege delegation, unauthorized tool actions, live paid inference, production promotion, customer-data training, arbitrary external model download, or new shadow backend.

## Quality gates
Target 9.9-class engineering means independently demonstrated quality, not an invented numeric score. Measure reproducibility, adversarial resistance, isolation, cost/quality, audit coverage, currentness and recovery. The system may never be its own sole witness.
