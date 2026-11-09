# OPERATION KUSANAGI CCCXXXIII — Public IFS capability intelligence for DISPATER
Date: 2026-11-07
Status: RESEARCH / ENGINEERING BACKLOG ONLY; NOT CODE VERIFIED; RELEASE HOLD
Source method: Firecrawl search, product URL map, targeted official-page scrapes.
License boundary: Capability-level functional requirements only. No IFS source code, proprietary product designs, private APIs, internal datasets, IFS trademarks or protected interface assets are imported.

## Public capability sources (official IFS pages)
- [Cloud EAM](https://www.ifs.com/en/products/alm/eam/ifs-cloud-eam): lifecycle asset records, maintenance, performance, procurement, finance, FMECA/anomaly concepts.
- [Field Service Management](https://www.ifs.com/en/products/fsm): workforce scheduling, parts logistics, repair, contractors, mobile worker workflows.
- [Workforce scheduling](https://www.ifs.com/en/products/fsm/workforce-scheduling-and-planning): skills-based crew assignment, resource availability and routing constraints.
- [Oil and gas](https://www.ifs.com/en/products/upstream-oil-and-gas): production, financial accounting and related asset operations.
- [AP invoice](https://www.ifs.com/en/products/upstream-oil-and-gas/accounting/ap-invoice): capture, validation, routing, exception visibility; payment claims are not authorization to implement autonomous payments.
- [Shift log](https://www.ifs.com/en/products/upstream-oil-and-gas/production-operations/ifs-shift-log): handovers, incident tracking, auditable forms, role-based logs.
- [Continuous asset decision intelligence](https://www.ifs.com/en/products/alm/continuous-asset-decision-intelligence): repair, defer, replace decision support and condition / cost / risk tradeoffs.
- [Industrial Digital Workers](https://www.ifs.com/en/products/ai/agentic-ai): governed workflows, shared skills and connectors, operational context.
- [Loops Agent Studio](https://www.ifs.com/en/products/ai/agentic-ai/loops-agent-studio): configure, sandbox, test, release, monitor, learn; approval queues, agent evaluation, immutable release versions, memory separation.
- [IFS Intelligence](https://www.ifs.com/en/products/ai/ifs-intelligence): natural-language operational query, saved skills, permissions and activity log.
- [Finance ERP](https://www.ifs.com/en/products/erp/finance): management reporting and forecasting.

The pages describe vendor claims, not independently measured results. Public pages do not disclose implementation algorithms, model weights, security internals or unrestricted data rights.

## Reuse existing VALEXII modules first
- `aurex/dispater_intelligence.py`: deterministic reconciliation and five-part evidence-linked findings.
- `aurex/dispater_api.py`, `aurex/dispater_store.py`: existing tenant and persistence contracts; do not invent duplicate APIs.
- `aurex/dispater_maintenance_advisory.py` on this candidate branch: synthetic read-only service-threshold proposals; review/test before reuse.
- `aurex/ox/registry.py`, `aurex/ox/evaluation.py`, `workstation/model_forge.py`: candidate training and evaluation boundaries; do not call these an operational LLM fine-tuning system.
- `aurex/auseklis/knowledge_treasury.py` on this candidate branch: candidate knowledge registry checks.
- Android BCXMET authority chain remains separate and cannot be minted through this backend.

## Original engineering backlog
| ID | Priority | Slice | Acceptance contract |
|----|----------|-------|--------------------|
| D-01 | P0 | Asset registry / meter history | Tenant-scoped immutable record revisions, origin digests, duplicate/conflict rejection and interval validation. |
| D-02 | P0 | Work order state machine | DRAFT -> PROPOSED -> APPROVED -> ASSIGNED -> IN_PROGRESS -> COMPLETED -> VERIFIED; human transition authority and idempotency; advisory never self-approves. |
| D-03 | P0 | Digital field ticket | Signed evidence manifest, status and timestamp lineage, synthetic-only ingestion, versioned rate references. |
| D-04 | P0 | AP reconciliation proposals | Invoice ↔ PO ↔ receipt ↔ approved rate three-way match; Decimal-safe; no payments, vendor contact or autonomous postings. |
| D-05 | P0 | Shift handover ledger | Shift, equipment, alerts, unresolved issues, independently attributable acknowledgement; append-only semantics. |
| D-06 | P0 | Evidence-first dashboard | NOW / CHANGED / NEXT / WHY / PROOF and withheld-vs-confirmed exposure; drill-down to source digests. |
| D-07 | P1 | Crew qualification matching | Skills, certifications, availability and priority; suggestions only, no routing of real personnel without consent. |
| D-08 | P1 | Parts inventory and procurement | Reorder recommendations, reservations and stock reconciliation, with budget and approval gates; no autonomous purchase. |
| D-09 | P1 | Fleet utilization and maintenance | Uptime, downtime windows, unplanned events, maintenance thresholds and cost breakdowns. |
| D-10 | P1 | Repair vs defer vs replace | Transparent deterministic cost/risk scenarios, independent comparison and operator sign-off. |
| D-11 | P1 | Agent Studio analogue | Original versioned skill manifests, isolated sandbox, hidden holdouts, test diff, approval queue, rollback and observable traces. |
| D-12 | P1 | Knowledge and memory governance | Separate provenance-addressed semantic/procedural/episodic memory; expiry, tenant isolation, no self-training approval. |
| D-13 | P2 | Condition-based analytics | Approved sensor connectors, time-series anomaly evaluation, labeled historical asset failures and calibrated abstention. |
| D-14 | P2 | Scheduling optimizer | Constraint solver with skill, part, geography and shift constraints; human dispatch approval. |
| D-15 | P3 | Oil and gas accounting extensions | Only after buyer validation: production allocations, joint venture, royalty/land complexities and legal review. |

## Preferred data model (all fields typed and versioned)
`Asset(tenant_id, asset_id, meter, revision, service_policy, source_digest)`
`WorkOrder(tenant_id, work_order_id, asset_id, state, policy_epoch, source_refs, version)`
`FieldTicket(tenant_id, ticket_id, job_id, asset_ref, approved_rate_ref, author_ref, receipt_digest)`
`InvoiceMatch(tenant_id, invoice_id, po_ref, receipt_ref, comparison, qualification, evidence_refs)`
`ShiftHandover(tenant_id, shift_id, outgoing_ack, incoming_ack, open_issues, source_refs)`
`AgentSkill(skill_id, version, tools_allowlist, sources, evaluation_digest, approval_state)`

## Acceptance / no-go
1. No critical permission bypass, cross-tenant reads, unverified evidence promotion, false confirmed recovery or unauthorized financial effect.
2. Every API and field change backward compatible or explicitly versioned.
3. All data synthetic until owner-approved customer pilot with contract, retention and deletion controls.
4. Exact Git SHA full pytest / type checking / lint / website build and independent reviewer. Mere documentation is NOT PASS.
5. End-to-end synthetic scenario: asset -> maintenance advisory -> work-order proposal -> signed field ticket -> invoice discrepancy -> XAELI explanation -> separate independent verification, with no autonomous financial or dispatch action.
6. Preserve existing product release HOLD; use branch-based PR review and existing canonical repository.

## Commercial thesis
Start with a narrow oilfield field-ticket-to-cash assurance product, then extend into maintenance and work orders. Optimize measured reconciliation accuracy, exception triage time, uptime and realized customer outcomes, not number of features. IFS is a competitor and capability benchmark; no affiliation or official integration is claimed.
