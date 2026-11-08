# 🔒 OPERATION KUSANAGI CCCLIV — SOVEREIGN CONTRACT FREEZE
## VALEXII ONE CANONICAL SYSTEM CONTRACT MATRIX

**FREEZE STATUS:** ACTIVE & NON-DELEGABLE
**PRODUCTION RELEASE:** HOLD
**FINANCIAL AUTHORITY:** NONE
**EXTERNAL PAID INFERENCE:** OFF
**CUSTOMER DATA:** PROHIBITED
**GOVERNING AXIOM:** *The system may never be its own sole witness.*

---

### I. CANONICAL TRANSITION PIPELINE

All autonomous, assisted, or administrative operations within VALEXII/AUREX strictly adhere to the invariant transition chain:

$$\\text{Evidence} \\longrightarrow \\text{Qualification} \\longrightarrow \\text{Reality} \\longrightarrow \\text{Authority} \\longrightarrow \\text{Effect}$$

No layer (model, agent, dashboard, background task, or orchestration engine) may grant itself authority or bypass intermediate gates.

---

### II. SUBSYSTEM CONTRACT DEFINITIONS

#### 1. EVIDENCE
- **Identity & Roots:** Must possess at least 2 distinct, immutable cryptographic roots.
- **Content Integrity:** Strict SHA-256 content digesting.
- **Provenance:** Source locator, timestamp, tenant binding, and immutable byte digests.
- **Replay Protection:** Unique run bindings and monotonic nonce/timestamp verification.

#### 2. QUALIFICATION (CUSTOS / AUSEKLIS)
- **Independent Witness:** A witness distinct from the proposer/ghost (`independent_witness_id != ghost_id`).
- **Freshness & Expiry:** Evidence must be verified current (`evidence_current=True`).
- **Treasury Seed Validation:** Candidate-only registration without autonomous training promotion.

#### 3. REALITY (SOVEREIGN KERNEL / BIAN-LIAN)
- **State Attestation:** Verified system capability, shell attestations, and environment truth.
- **Fail-Closed Preflight:** `evaluate_proposal` and `evaluate_shell_transition` return `ELIGIBLE_FOR_AUTHORITY_REVIEW` or `HOLD`. They NEVER grant execution authority (`authority_granted=False`).
- **Capability Scoping:** Actions strictly constrained to declared shell capabilities.

#### 4. AUTHORITY (SOVEREIGN OWNER / GOVERNANCE)
- **Explicit Scoping:** Authenticated owner token hash grants tenant-bound permissions.
- **Financial Prohibitions:** All autonomous financial executions (`EXECUTE_FINANCIAL`) strictly evaluate to `HOLD`. Confirmed recovery is immutable at `$0.00` absent verified admissible proofs.
- **Revocation & Non-Delegation:** Bian-Lian transitions enforce prior capability revocation before new shell attestation.

#### 5. EFFECT (AUREX-OX / DISPATER / WORKSTATION)
- **Deterministic Receipts:** HMAC-signed receipts (Receipt v2 bound with `run_id`, `created_at`, `BOUND_V2`).
- **Truthful Status Codes:** Frontend strictly displays truthful states: `CONNECTED`, `OFFLINE`, `SIMULATED`, `BLOCKED`, `UNVERIFIED`.
- **Model Forge Containment:** Acquisition, training, and promotion remain decoupled. Self-approvals and forged evaluation receipts are strictly rejected.
