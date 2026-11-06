# LOCKED OWNER DIRECTIVE — DISPATER × AUREX × MEDAURUS × BCXMET

Date: 2026-11-05
Status: **OWNER-APPROVED ARCHITECTURAL DIRECTION**; implementation and independent verification **NOT COMPLETE**.
Canonical repository: `victormart43210-ship-it/Valexii-Aurex`
Implementation track: draft PR #169 (international evidence-processing convergence).

## Mission
Build DISPATER as an **AI-assisted, evidence-governed industrial audit and continuous-monitoring platform**, not an LLM-only document reviewer.

The default historical review target is **36 months**, configurable according to authorized data availability, customer agreement, and applicable constraints. This is a **product requirement**, not a claim of proven 36-month capacity or recoverable funds.

## Processing and authority contract
1. Ingest approved documents and records; retain originals, tenant ownership, source identifiers, hashes, timestamps, and page/row locators.
2. Use verified, licensed, task-appropriate open-source components for OCR, layout, tables, extraction, normalization, and deterministic reconciliation. Do **not** route every document through every model.
3. Use AI only for bounded assistance: classification, ambiguous field mapping, anomaly suggestions, language interpretation, and readable explanations.
4. Normalize into typed, provenance-linked evidence records; preserve original content and distinguish source facts from model hypotheses.
5. Apply **Evidence → Qualification → Reality → Authority → Effect**. A model may not self-certify its claims. **The system may never be its own sole witness.**
6. Verify financial discrepancies against independently qualified documents and deterministic calculations. Label potential exposure as potential, not recovered revenue.
7. Present NOW → CHANGED → NEXT → WHY → PROOF, with direct original-source navigation and human review.
8. Continue from historical audits into **authorized, tenant-isolated continuous monitoring**; new or corrected records must invalidate or requalify affected prior findings.

## Reuse from MEDAURUS / BCXMET
- **Evidence freshness / lifecycle:** stale, revoked, superseded, or contradictory inputs force requalification and withholding of prior authority.
- **Independent witness challenge:** challenge important findings against independent records; multiple models agreeing is not independent evidence.
- **Security monitoring:** detect access anomalies, tampering, unexpected changes, and unauthorized operations, without claiming unimplemented controls.
- **Identity / isolation:** tenant-specific authorization, audit trails, secrets protection, and least privilege.
- **XAELI advisory presentation:** explain recommendations and uncertainty without authorization to bill, pay, change records, or deploy.
- **BCXMET presentation principles:** routine versus critical events clearly differentiated; Orb/animation is **presentation-only**, never an authority signal.

## Product boundaries
- Reuse shared AUREX evidence contracts and tested patterns; keep Android VPN, call blocking, device security, and platform-specific runtime controls inside MEDAURUS/BCXMET.
- No duplicate canonical repositories, duplicate financial ledgers, or shadow authority engines.
- Upstreams from Norway, Greece, China, and Uzbekistan must be inventoried by exact project, version, license, digest, installed location, and passing test before being called integrated.
- Offline Chromebook/USB implementations are not presumed to match the canonical repository.
- **Production HOLD; financial authority NONE; external paid inference OFF; customer data prohibited; uncontrolled self-modification prohibited.**
- No merge, production deploy, payment, or customer-data onboarding without explicit approval and independent verification.

## Acceptance gates
- Frozen synthetic 36-month corpus including invoices, tickets, contracts, adjustments, and payments; run full intake-to-dashboard audit.
- Original source and lineage preserved across every required processing layer.
- Positive and negative tests for tenant isolation, tampering, stale evidence, duplicate documents, OCR errors, contradictory records, prompt injection, financial arithmetic, and human-review gating.
- Baseline versus AI-assisted extraction comparison on labeled synthetic documents: precision/recall, false positives, cost, throughput, and abstention.
- Demonstrate corrected-contract ingestion invalidates affected findings; demonstrate monitoring adds new events without rewriting history.
- Capture exact code SHA, dataset hashes, dependency versions, commands, CI and independent witness results. Unrun tests remain NOT RUN.

## Commercial positioning
**36-month historical industrial audit → independently qualified findings → authorized ongoing monitoring.**
Business value and market demand must be validated with real pilots before being claimed as proven.

This file locks the **design direction**; it does not declare any missing software, integration, or production gate complete.
