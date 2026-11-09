# OPERATION KUSANAGI CCCLVI — IMPLEMENTATION BACKLOG

This implementation backlog consolidates all verified, pending, and candidate engineering initiatives across the VALEXII ecosystem, classified by strict operational priority.

---

## Priority 0 (P0) — Critical Security, Integrity & Mainline Convergence

### P0-1: Sovereign Kernel Convergence
- **Branch Candidate:** `origin/work/valexii-sovereign-kernel-foundation-20261108` (Commits: `5001962`, `a14a92a`)
- **Objective:** Merge fail-closed proposal evaluation, shell transition preflight, and tests rejecting stale evidence, self-witness, and privilege carryover.
- **Dependencies:** Canonical main (`fc2bed4`).
- **Acceptance Criteria:** Fast-forward or clean rebase/merge onto main; `tests/test_sovereign_kernel.py` passes 100%; strict mypy clean.

### P0-2: Model Forge & Adversarial Evaluation Convergence
- **Branch Candidates:** `origin/cursor/kusanagi-ccxcvii-model-forge-4082`, `origin/cursor/kusanagi-ccxcviii-adversarial-repair-4082`
- **Objective:** Integrate `aurex/ox/forge.py` and adversarial tests (`tests/test_forge_adversarial.py`, `tests/test_ox_model_forge.py`) separating training completion from evaluation and deployment approval.
- **Dependencies:** P0-1.
- **Acceptance Criteria:** Torch remains an optional dependency (`work/kusanagi-cccxiv-forge-ci-optional-torch`); all non-torch tests pass cleanly.

### P0-3: Container & Entrypoint Runtime Observability
- **Branch Candidate:** `origin/cursor/kusanagi-ccxciv-live-acceptance-4082` (Commit: `f014111`)
- **Objective:** Integrate `docker/entrypoint.py` and updated `Dockerfile` ensuring service user privilege drop after chowning `/data` mount and observable Qwen verifier checks.
- **Dependencies:** Mainline container build pipeline.
- **Acceptance Criteria:** Docker container builds and executes as non-root user; SQLite persistent storage initializes cleanly.

---

## Priority 1 (P1) — Integration, Full-Stack Convergence & Telemetry

### P1-1: Unified Website-to-AUREX Server Client Stabilization
- **Status:** Verified on main (`99b2531`).
- **Objective:** Maintain AbortController timeout handling in `website/src/lib/aurex-client.server.ts` to ensure Bun runtime event-loop continuity.
- **Acceptance Criteria:** All 173 frontend tests pass; zero timeout hangs under concurrent simulated load.

### P1-2: DISPATER Digital Audit Binder Full Persistence Integration
- **Objective:** Connect the frontend Digital Audit Binder directly to SQLite table `dispater_audit_packages` with verifiable SHA-256 manifests.
- **Acceptance Criteria:** Audit binder round-trip verified in browser console with zero client-side private key exposure.

### P1-3: Continuous Monitoring Daemon Health Checks
- **Objective:** Implement health ping endpoint for `ContinuousMonitoringEngine` background worker.
- **Acceptance Criteria:** Worker heartbeat observable in `/v1/health` with strict timeout bounds.

---

## Priority 2 (P2) — Commercial Pilot & Partner Readiness

### P2-1: DISPATER Industrial Pilot Ingestion Workflows
- **Objective:** Deploy customer pilot batch ingestion for commercial towing operations with automated CSV sanitization and FMCSA Part 390-396 compliance mapping.
- **Acceptance Criteria:** Ingestion passes adversarial formula injection tests; 100% tenant isolation verified.

### P2-2: Sovereign Executive Command Center Enhancement
- **Objective:** Complete the 8-module Executive Command Center in `website/src/components/dispater-command-center.tsx` following the 5-step XAELI framework (NOW -> CHANGED -> NEXT -> WHY -> PROOF).
- **Acceptance Criteria:** Client renders without WebGL/canvas regressions; passes all accessibility and semantic UI tests.

---

## Priority 3 (P3) — Advanced Model Research & Evaluation Harnesses

### P3-1: HLE Practice Lab & Black Diamond Benchmark Execution
- **Objective:** Complete the offline evaluation harness for Humanity's Last Exam (HLE) practice questions in `workstation/hle_practice.py`.
- **Acceptance Criteria:** Zero benchmark contamination risk; offline reproducibility verified.

### P3-2: Governed LoRA / QLoRA Local Fine-Tuning Pipeline
- **Objective:** Verify tiny CPU/GPU LoRA fine-tuning for Qwen 2.5 0.5B/7B with immutable dataset provenance receipts in `training/`.
- **Acceptance Criteria:** Baseline vs adapter evaluation report generated with deterministic scoring.
