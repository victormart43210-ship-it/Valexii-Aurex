# DISPATER implementation roadmap

Status: **PLANNED** unless marked V. Authority: production NONE, financial NONE, paid inference OFF, customer data PROHIBITED. Extends `DISPATER_INDUSTRIAL_INTELLIGENCE_STRATEGY_LOCK_2026-11-07.md` and `DISPATER_AGENT_EXECUTION_AND_MAINLINE_GATE.md`; does not replace them.

Doctrine: Evidence -> Qualification -> Reality -> Authority -> Effect. No system is its own sole witness.

## Existing foundation (V, PR #212 head `edbdc11336f4`)
- `aurex/dispater_maintenance_advisory.py` with tests (V: ruff/mypy/pytest green).
- `aurex/auseklis/knowledge_treasury.py` with tests (V).
- `.github/workflows/dispater-mainline-gate.yml` (V: passing at head).
- Existing reconciliation/audit-package engine merged to main (#196, #205).

## Contract freeze (G1) - PLANNED, must precede Wave 1
Reuse existing models in `aurex/dispater_*`; add versioned (`schema_version`) contracts only where absent: asset/meter, policy/finding, work order, field ticket, handover, PO/rate/invoice, discrepancy; agent identity/permissions, skill manifest, treasury record, eval result, memory provenance, approval, receipt/rollback.

## Waves (dependency order, each bounded PR, each with negative tests)
1. **Wave 1 Industrial foundation** - tenant-scoped asset registry; advisory/service intervals (exists); human-approved work-order state machine (idempotent, no auto-approve); field-ticket evidence records; link to existing invoice reconciliation. Acceptance: synthetic maintenance -> evidence-linked invoice discrepancy. Not started.
2. **Wave 2 Field operations** - handovers, crew qualification, parts/inventory, fleet downtime, repair-vs-replace. No dispatch/purchase/accounting effects.
3. **Wave 3 Industrial AI** - skills, sandboxed eval, separated memory types, approval queue, versioned releases + rollback, SHRIKE evals, CUSTOS qualification. Agents propose; never self-promote.
4. **Wave 4 Product** - dashboard + XAELI exposing NOW -> CHANGED -> NEXT -> WHY -> PROOF; suspected exposure is never shown as confirmed recovery.

## Required test classes per wave
Tenant isolation, approval bypass, provenance/tampering, duplicate/replay, forged receipts, prompt injection, unauthorized financial effect, API contract, synthetic E2E.
