# Agent execution contract

Extends `DISPATER_AGENT_EXECUTION_AND_MAINLINE_GATE.md` and root `AGENTS.md`. Roles are assignments, not claims that an agent ran.

## Roles
- **Copilot**: contract-safe code, tests, CI diagnosis, integration prep.
- **Coordinator**: freezes contracts, sequences dependencies, tracks SHAs.
- **Independent verifier (Jules or other reviewer)**: reproduces tests at the exact SHA; must differ from the author.
- **SHRIKE**: adversarial tests (tenant, provenance, approval bypass, forged receipts, replay, injection, financial effects).
- **CUSTOS**: checks evidence supports readiness claims and whether human approval is needed.

## Rules
1. Work only in `victormart43210-ship-it/Valexii-Aurex`; no new repo, backend or orchestrator.
2. Never force-push shared branches, close PRs without reviewing unique work and owner authorization, or merge/deploy autonomously.
3. A gate is PASS only with command output or CI logs at the exact head SHA. A commit is not evidence.
4. No weakening of lint, typing, or tests to get green.
5. Agents may propose skills/memory/changes; promotion to production authority requires human approval and independent review. Receipts are immutable; every release has a rollback.
6. Production NONE, financial NONE, paid inference OFF, customer data PROHIBITED.

## Gates
G0 inventory, G1 contracts frozen, G2 CI at exact SHA, G3 negative security tests, G4 independent reproduction, G5 no unauthorized effects, G6 reviews and branch protection, G7 owner approval. Any unresolved gate keeps the PR DRAFT/HOLD. Merge to main is not deployment permission.

## Recommended branch protection (not verified as configured)
Require status checks `test`, `verify`, `integration`, `synthetic-contracts`, `docker-build-and-smoke`, `offline-practice`; require 1+ non-author approving review; require up-to-date branch; disallow force-push and deletion; no admin bypass.
