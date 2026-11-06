# PROJECT GEMINI — LOCKED TWIN INTELLIGENCE ARCHITECTURE
Date: 2026-11-06
Status: OWNER ARCHITECTURE DIRECTIVE / DESIGN LOCK ONLY
Production: HOLD. Financial authority: NONE. Security authority: NONE without separately verified policy engine.
Related: CCLXIII website foundation; CCLXIV model upgrade foundation; CCLXV Cursor execution handoff.

## Owner intent
XAELI and Zaylee are **two distinct, cooperating intelligence systems** powering VALEXII.AI. Neither replaces the other. They share governed AUREX-OX infrastructure. XAELI is the primary human-facing conversational intelligence; Zaylee is the introspective system-model and improvement intelligence. Both may use replaceable pretrained models but must preserve role separation and evidence provenance.

## Custos research incorporation
Research reference: https://custosagent.ai/ (Custos Runtime's Plan/Execution/Rationale model). Distinguish this vendor from similarly named Custos offerings. This design borrows the publicly described PER observation pattern; it does not claim an integration, endorsement, license clearance, or installed SDK.
- PLAN: Record the proposed action, target, scope, expected effects, permitted tools, and preconditions BEFORE execution.
- EXECUTION: Capture actual invoked tool/API/command, immutable request metadata, authorization outcome, result, and timestamps.
- RATIONALE: Capture agent explanation and link to pre-existing evidence; a retrospective rationale is not proof of prior intent.
- CONSISTENCY: Independently check plan ↔ execution ↔ rationale, as well as policy compliance, before action authorization where possible and after action for auditing.
- PER evidence is supplementary: policy enforcement must use deterministic, default-deny controls for critical operations, not a sole LLM judge. Sign/hash receipts, use append-only audit logs and independent replay.

## Architectural layers
1. Observable reality: read-only authorized code metadata, versioned APIs, service health, logs, model identities, datasets, CI results, telemetry and approved documents. Missing/stale observations must be labeled unknown.
2. Zaylee cognitive digital twin: time-stamped typed system graph of components, dependencies, capabilities, evidence, observed state, causal hypotheses, change proposals, simulated impacts, confidence and falsification tests. Never conflate graph prediction with actual state.
3. XAELI user interface: translates owner goals into scoped queries, presents Zaylee's sourced findings, uncertainty, alternatives, and approval requests. It cannot manufacture receipts or present simulation as production.
4. AUREX execution governance: identity, scoped capability tokens, typed tool contracts, tenant boundaries, budgets, rate limits, model policy, evidence qualification, human approval, rollback and stop switch.
5. Independent witness: verifier runs separate tests/observations; model agreement or two agents citing the same source does NOT count as independent verification.

## Canonical owner-facing loop
Goal → XAELI clarifies → Zaylee observes and models → Zaylee proposes options → AUREX qualifies evidence and policy → owner authorizes bounded change → isolated execution → independent verification → evidence receipt → XAELI explains outcome → graph updates with observed state.

## Non-negotiable rules
- Evidence → Qualification → Reality → Authority → Effect.
- The system may never be its own sole witness.
- No direct model-to-production, model-to-payment, model-to-security-enforcement, or model-to-self-modification authority.
- No unapproved model training, data collection, spending, external inference or automatic deployment.
- Orb presentation only; no animation return path to authority.
- DISPATER calculations are deterministic and receipt-backed; model extracts candidate facts but never certifies financial outcomes.
- Zero trust for prompt content, retrieved documents, model outputs and other agent messages.
- Human approval is action-specific, expiring and revocable; permissions are least-privilege and fail-closed.
- Preserve tenant isolation, privacy, source licensing and data-retention boundaries.
- CCLXV is not complete unless independent tests confirm both full-stack flows.

## Greek academic methodological alignment
Use published approaches as references, not institutional endorsements:
- NTUA: knowledge graphs + AI / manufacturing digital twins.
- University of Patras LMS: adaptive manufacturing and robotics, simulation, human-system interaction.
- Aristotle University CoDiBio: hybrid modelling and experimental validation.
- University of Piraeus CBML AI4WORK: human-centred digital twins and trustworthy AI.
Digital twin here means a continuously reconciled model of real observed AUREX system state; two AI personas alone are NOT a digital twin.

## Contract objects to implement and test
- TwinObservation: observation_id, source_id, captured_at, valid_until, source_digest, tenant_scope, confidence, observation_type, payload_ref.
- TwinGraphNode/Edge: stable_id, type, revision, provenance, temporal validity, dependency semantics.
- TwinHypothesis: claim, evidence_refs, counterevidence_refs, alternatives, uncertainty, test_plan, status.
- TwinChangeProposal: target_sha, expected benefit, safety impact, cost cap, required approvals, rollback, success/failure thresholds.
- PERActionReceipt: actor, action_id, plan_ref (pre-execution), execution_ref, rationale_ref, policy_version, decision, timestamps, evidence_digest, independent_verifier_ref.
- TwinReview: owner approval, scope, expiry, deny/revoke, verifier outcome, observed result.
Never store raw secrets in receipts.

## Minimum demonstration (synthetic data only)
A) Website → XAELI asks why a DISPATER synthetic reconciliation is delayed.
B) Zaylee reads authenticated staging metrics and graph, identifies a testable bottleneck hypothesis; if metrics unavailable, says UNKNOWN.
C) XAELI presents observations vs hypotheses, with linked provenance.
D) Zaylee proposes a bounded code/config improvement, with rollback and test plan.
E) AUREX rejects action without explicit approval, checks PER consistency and deterministic policy.
F) In isolated test environment, approved change runs; independent verifier compares before/after metrics and security regressions.
G) Receipt and final explanation show observed outcome, not claimed improvement.

## Failure tests
Reject fabricated telemetry, stale observation, mismatched PER intent/execution, post-hoc plan mutation, tenant-crossing reads, unauthorized tool calls, unsupported model identity, self-certified success, prompt-injected documents, budget overrun, expired approval, unavailable verifier and missing rollback. Verify both agents fail closed.

## Implementation waves
W0 contracts and baseline; W1 read-only telemetry and temporal system graph; W2 XAELI↔Zaylee request/response with citations; W3 PER receipts and deterministic policy checks; W4 simulation and change-proposal engine; W5 owner approval and sandbox executor; W6 independent verifier, adversarial evaluation, and owner-only UI. Parallelize only after contracts freeze; serialize integration.
Required durable artifacts: GEMINI_CONTRACTS.md, GEMINI_GRAPH_SCHEMA.json, GEMINI_PER_RECEIPTS.json, GEMINI_EVAL_RESULTS.json, GEMINI_OWNER_HANDOFF.md, RECOVERY.json, RESUME.md.

## Lock scope
This document freezes **intended architectural doctrine**, not claims of implemented code, installed Custos software, verified production functionality, or external institutional affiliation. Changes require explicit owner decision and reviewable revision; no unsafe merges or deploys.
