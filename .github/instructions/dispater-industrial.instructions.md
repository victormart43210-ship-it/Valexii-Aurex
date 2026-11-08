---
applyTo: "aurex/dispater_*.py,tests/test_dispater_*.py,docs/competitive/**,docs/operations/DISPATER_*.md"
---
# DISPATER industrial engineering instructions for coding agents

Before editing, read:
- `docs/operations/DISPATER_INDUSTRIAL_INTELLIGENCE_STRATEGY_LOCK_2026-11-07.md`
- `docs/competitive/IFS_PUBLIC_CAPABILITY_DISPATER_BLUEPRINT_2026-11-07.md`
- `docs/operations/DISPATER_AGENT_EXECUTION_AND_MAINLINE_GATE.md`
- repository root `AGENTS.md` and `docs/AGENT_MAINLINE_POLICY.md`.

Work only in the canonical Valexii-Aurex repository. No new repositories, no duplicate orchestration spines, no new production services without approval. Reuse existing DISPATER endpoints and data models; freeze a typed contract before implementation.

Treat IFS as a capability benchmark, not a source of proprietary code or confidential APIs. Use synthetic-only fixtures. No autonomous financial postings, invoice changes, payments, procurement, field dispatch or production changes. AI recommendations never grant authority. Require tenant isolation, independent witness and evidence digests.

For every code slice: name the existing modules touched; list acceptance tests; implement bounded behavior; run targeted and full CI; record exact head SHA, failures, security review, independent reviewer and rollback. Never claim passing checks without their logs. Keep PR draft until all gates are met. No agent may merge or deploy based only on its own assessment.
