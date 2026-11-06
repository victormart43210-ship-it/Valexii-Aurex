# GEMINI implementation foundation — 2026-11-06
Status: DESIGN/CONTRACTS ONLY; not deployed, not merged; production HOLD.

## Objective
Build XAELI (user-facing twin) + Zaylee (system-introspection twin) atop one AUREX-OX governance plane, without duplicating models, repositories, authority or unverifiable claims.

## Contract freeze / dependency order
G0 baseline inventory: identify actual canonical main SHA, existing routes, auth, test harnesses, Railway service, website deployments, model registry, telemetry and current blockers. No invented paths.
G1 freeze API, event, graph, action receipt and authorization contracts; threat model and test fixtures. Independent review before parallel implementation.
G2 build read-only Zaylee observation adapters for source, CI, runtime and synthetic DISPATER jobs. Source timestamps, TTL, hashes and tenant scope mandatory. Missing means UNKNOWN.
G3 construct temporal knowledge graph; distinguish observed fact, derived inference, simulation and proposal. Provenance and counterevidence mandatory.
G4 XAELI↔Zaylee mediated interface with scoped auth, correlation IDs, bounded budgets, no direct privileged tools.
G5 Plan/Execution/Rationale action receipt with immutable pre-execution plan, deterministic deny-by-default policy checks, replay and independent witness.
G6 sandbox proposal simulation and owner approval; no production writes or autonomous merge. Separate verifier compares baseline/candidate.
G7 website owner-only Gemini panel: NOW → CHANGED → NEXT → WHY → PROOF; accessibility, large text, reduced motion, no misleading simulated-live status.
G8 staged end-to-end synthetic demo, adversarial tests, provenance and evidence packet, rollback and release recommendation (HOLD unless explicitly authorized).

## Agent ownership after contract freeze
A contracts/auth; B read-only telemetry + temporal graph; C XAELI UX; D policy/PER audit; E independent red-team verification. Isolated worktrees, serialized integration, no unsafe merges.

## Release gates
- Staging deployed source SHA matches independently tested source SHA
- Two authenticated vertical slices: DISPATER synthetic ledger and real private Qwen inference (if available; else BLOCKED)
- Zaylee observations are fresh, source-backed and tenant-isolated
- XAELI never describes simulated result as live
- Critical action requires deterministic policy, explicit bounded owner approval and independent witness
- No raw secrets in logs, receipts or graph; budgets fail closed
- Tests for injection, replay, stale evidence, cross-tenant, prompt tampering, unauthorized action, model identity and rollback
- CI green is necessary but insufficient for release
- Financial recovered value stays $0 unless independently verified

## Existing work constraints
Canonical repository: victormart43210-ship-it/Valexii-Aurex. Existing CCLXV and PR #187 convergence work must be inspected and reconciled before coding. Do not assume ~/Valexii-Aurex exists on Chromebook. Hardware-constrained training: baseline before candidate; no unapproved weights/downloads/spending.
## Required completion artifacts
docs/operations/GEMINI_BASELINE.json, GEMINI_CONTRACT_REVIEW.md, GEMINI_THREAT_MODEL.md, GEMINI_EVAL_RESULTS.json, GEMINI_INDEPENDENT_VERIFICATION.md, RECOVERY.json, RESUME.md.
