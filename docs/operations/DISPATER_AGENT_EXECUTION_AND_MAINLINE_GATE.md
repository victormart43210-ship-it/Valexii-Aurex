# DISPATER agent execution contract and mainline qualification gate
Status: branch-local candidate; no production or merge authority
Applies to Cursor, Jules, Copilot, ChatGPT Work, and other code agents.

## Mission and authoritative context
Build a narrow, verifiable field-ticket-to-cash industrial product, then extend asset management. The strategy lock and IFS public capability blueprint are requirement references, not permission to copy or deploy.

## Dependency order (no parallel edits to shared contracts)
0. Baseline: inspect current main and open PRs, list overlapping modules, record exact base SHA; freeze data schemas and endpoint contracts.
1. Test existing `aurex/dispater_maintenance_advisory.py` and `aurex/auseklis/knowledge_treasury.py` and their new tests; fix errors without changing financial or security authority.
2. Implement work-order proposals in a bounded module with versioned state transitions, idempotency and an external human-approval seam. NO automatic approval.
3. Implement signed/evidence-linked field ticket proposals and contract rate references; preserve existing revenue reconciliation invariants.
4. Connect one synthetic end-to-end workflow asset -> maintenance -> work order proposal -> field ticket -> invoice comparison -> XAELI explanation -> independent verification.
5. Only after verification, add crew matching, inventory, shift logs, repair/replace economics, skill registry and agent evaluations.

## Agent lanes
- Coordinator (Opus/Work): contract freeze, scope, dependency sequencing, SHA tracking, integration, never self-approve.
- Implementer A (Cursor/Grok): asset/work-order lifecycle and tests in isolated worktree.
- Implementer B (Copilot): field-ticket/AP matching and tests only after frozen shared schema.
- Challenger (SHRIKE role): adversarial, cross-tenant, forged provenance, injection and financial-effect tests; must not share implementer's evaluation as independent proof.
- Verifier (Jules/CUSTOS role): independently rerun at exact candidate SHA and review outputs; separate reviewer identity required for independent approval.
Agents may be unavailable; roles are assignments, not claims of active workers.

## Pull-request template for every implementation
- Base SHA / candidate head SHA / changed files and contract impact.
- Exact tests and commands run, logs and failures; never replace with narrative.
- Synthetic evidence fixtures and expected findings.
- Security matrix: authentication, tenant separation, replay/idempotency, provenance, prompt injection, egress, approval bypass, recovery.
- Independent review identity and decision.
- Rollback procedure; migration or data compatibility plan.
- Production authority: NONE. Financial authority: NONE. Paid inference: OFF. Customer data: PROHIBITED.
- Merge decision: HOLD until every mandatory gate is explicitly satisfied.

## Mandatory mainline gates
G0 canonical repository and overlap inventory complete.
G1 frozen contracts and compatible versioned schemas.
G2 targeted tests + full repository CI (ruff, mypy, pytest, frontend/build if affected) green on exact head SHA.
G3 negative tests for tenant isolation, source forgery, duplicate work orders, payment/dispatch denial, stale evidence and unknown outcome recovery.
G4 independent reviewer reproduces relevant evidence at same SHA; no self-witness.
G5 no uncontrolled training, paid inference, customer data, secrets or live external effects.
G6 PR review/branch protection requirements met and owner explicitly approves merge.
G7 production remains HOLD until separately approved release checks.
A gate not measured is OPEN, never PASS. Do not bypass failed checks to merge.

## Machine-readable handoff example
```json
{
  "schema": "valexii.dispater.agent_handoff.v1",
  "mission": "D-02 work order proposals",
  "base_sha": null,
  "head_sha": null,
  "contract_frozen": false,
  "synthetic_only": true,
  "financial_authority": "NONE",
  "production_authority": "NONE",
  "tests": {"targeted": "NOT_RUN", "full_ci": "NOT_RUN"},
  "independent_review": "PENDING",
  "merge": "HOLD",
  "rollback": "revert candidate commit; no production effects"
}
```
