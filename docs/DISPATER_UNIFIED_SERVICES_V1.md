# DISPATER.AI — Unified Business Operations & Private AI Services

**Product charter — v1 proposal; 2026-10-23**  
**Status:** DESIGN LOCK / SYNTHETIC SOURCE CANDIDATE; not a customer-ready service, live CRM, compliance certification, payroll system, model-training platform, or production deployment.  
**Owner umbrella:** VALEXII.AI. **Governance and evidence layer:** existing AUREX/OX, where separately integrated and admitted. **No separate production repository or platform.**

## Product promise

**DISPATER.AI connects the work a business performs to the records, people, systems, and decisions that make it profitable.**

Initial focus: oilfield service companies and towing / roadside recovery operators; later suitable adjacent service businesses through domain-specific adapters.

Positioning: custom **business operations implementation + workflow automation consulting + private company AI enablement**, rather than an unproven turnkey app. Start with a small paid, scoped diagnostic and controlled pilot; build a repeatable SaaS offering only after demand and safeguards are verified.

### Pillar A — Operations & Revenue Intelligence

Service discovery and prototype roadmap:
- CRM contacts/accounts, dispatch/call intake, crew/driver and equipment assignments.
- Ticket / work order capture, electronic signatures with provenance where applicable, rate-card and PO reconciliation.
- Job → approved field ticket → draft invoice → payment matching; flag possible unbilled jobs, duplicate references, outdated rates, orphaned payments, unapproved discounts.
- Human-reviewed candidate findings, **not** automatic collection, invoices, tax positions, wage changes, or legal findings.
- Customer-provided IRS and DOT **record inventories** with applicability judged by qualified personnel. The software flags missing or expired *metadata in supplied documents*; never describes itself as an IRS/DOT audit, DOT-compliant system, tax service, or certification.
- Synthetic dashboard concepts already stored in Lovable: oilfield control view; field ticket; towing dispatch view. All demo visuals must say **CONCEPT PREVIEW · FICTIONAL DATA · NOT LIVE**.

### Pillar B — Managed Workflow Automation Consulting

Map the customer's existing stack; do not force migration. Implement on customer-authorized tools such as **Make, Zapier, approved APIs or self-hosted orchestration** when permitted by contract and technical review.

Example reviewed workflows:
- **Oilfield:** CRM accepted job → draft crew dispatch → field-ticket reminder → rate exception queue → **draft** invoice → human sign-off.
- **Towing:** authorized dispatch request → driver acknowledgement → ETA update → impound/storage document preparation → invoice verification queue.
- **Back office:** CRM ↔ document library ↔ approved finance/payroll *read-only* exports → exceptions and missing-record notifications; no payroll mutations without separate design, dual approval and tested safeguards.
- **Office knowledge:** approved document updates → indexed corpus → evidence citations → internal staff assistance.

Safeguards required before client pilot: written authorization and data-processing terms; inventory of data flows and subprocessors; connector least privilege; server-side encrypted secret store; allowlist; per-tenant segregation; scoped service identities; event authenticity, retry/idempotency; replay rejection; fail-closed queue; rate/cost limits; immutable/auditable run receipts; recovery and rollback. **No client secret, API key, employee record, payment record or payroll data in the frontend or public repository.** All irreversible actions require authorized human approval.

Technology vendors are **optional**, not assumed connected or endorsed; billing and subcontracting require separate customer sign-off. Paid provider spend **$0 by default** during development.

### Pillar C — Private Company Knowledge & LLM Enablement

Offer an implementation and training service for existing businesses:
1. **Knowledge discovery:** identify authorized company policies, SOPs, job procedures, inventory manuals, safety rules, employee handbooks and document retention obligations.
2. **Access-controlled knowledge front door:** authenticated company portal; role and tenant scoped retrieval with source citations, source dates, permissions, redaction and retention rules, deletion handling, and explicit uncertainty.
3. **AI-assisted questions:** selectable approved Claude/ChatGPT/other model adapter behind a company-controlled server boundary only after data-processing agreements, provider configuration, privacy/security assessment and signed authorization. No customer data sent to any external model by default.
4. **Employee AI training and adoption:** teach staff safe prompting, source checking, privacy handling, review and escalation.
5. **Optional fine-tuning / custom model training:** a *distinct paid, opt-in R&D workstream*, never the default. Document owner consent, dataset license, minimization, isolated evaluation, hosting, weights ownership, costs, regurgitation testing and independent security review.

**Important distinction:** connecting a company knowledge library to an LLM through retrieval (RAG) is not the same as training a model's weights. Marketing and sales copy must use accurate terminology. The first pilot should be retrieval with citations, **not** claim proprietary model training.

## Combined customer experience

A service operator sees three tabs in one future DISPATER owner dashboard:

**Operations** (jobs, dispatch, tickets, draft invoices, review-required exceptions); **Automations** (reviewed workflows, consent, activity, failures, rollback); **Knowledge AI** (employee role, approved document library, cited answers and training). Underneath, an **Evidence & Controls** drawer exposes source, captured time, verification limitations, owner approval and immutable receipt/provenance linkage.

AUREX provides candidate challenges and evidence classification only where a real backend integration has passed testing. **The model never authorizes its own output or action.** Canonical line: **Evidence → Qualification → Reality → Authority → Effect**. No security or finance authority transfers between VALEXII products.

### Cross-sell progression

1. Discovery / record-flow mapping for one real vertical.
2. Synthetic workflow and invoice/ticket gap diagnostic.
3. Client-authorized, isolated **read-only** pilot with sample or explicitly permitted data.
4. Paid managed automation(s) with human approval, logging, and rollback.
5. Private knowledge gateway and staff training; optional separately governed model customization.
6. Only after measurable outcomes, expand to repeatable industry templates and subscription support.

**Commercial pricing:** discovery, deployment, ongoing maintenance and training quoted after scoping; indicative pricing is not a guarantee, and no recovered revenue, regulatory compliance or AI accuracy is promised. Obtain contracts, limitation of liability, data-processing agreements, support SLAs, and qualified legal/tax review before real business operations.

## Minimal technical contracts — this PR

Three **offline, fictional-only** Python demonstrations (no API registration, no network, no provider calls, no DB writes):
- `aurex/dispater_pilot.py`: deterministic rate/job/invoice/payment exception detector, source-row SHA-256 proof pointers, self-issued consistency digest; current authority **HOLD**.
- `aurex/dispater_evidence.py`: demo-rule IRS/DOT *record-index completeness* with missing/expired and applicability-unknown outcomes. Rule applicability is *never* inferred by the model.
- `aurex/dispater_workflow.py`: dry-run workflow proposal allowlist, payroll/billing mutation blockers, and synthetically tenant/role-filtered *retrieval candidates*. This is **not a secure authentication system** or a model answer service.

`tests/test_dispater_pilot.py`: fail-closed synthetic cases for mismatched rates, unbilled work, payments, tenant/role scoping, secrets, readiness uncertainty and no external side effects. **Tests have not been executed in the connector session; exact-head CI and independent review remain pending.**

Next technical integration is contract freeze → real consent/AuthZ server design → persisted encrypted audit-event schema → bounded leased workers → independent verification → owner-authorized staging → human-reviewed first-customer onboarding. Existing AUREX worker and schema PR backlog must be reconciled; do not create another competing backend.

## Website information architecture — implementation pending

Home: prominent **DISPATER.AI: Business Operations + Automation + Private AI** card near AUREX, distinct from the two already user-approved, **matching colorful animated OX orbits** (these must remain untouched).

`/dispater`: flagship landing page; three service pillars plus industry examples, strong concept illustrations, `/contact` inquiry link and `/solutions/business-operations` detail.

`/solutions/business-operations`: unified consulting/services landing page and request-a-discovery-call CTAs; proposed scope, illustrative pricing only, risk disclosures.

`/aurex`: short explanation of evidence-aware, human-governed automation layer; never say it is already integrated to CRM or payroll.

Navigation/footer: DISPATER.AI accessible on desktop/mobile; premium near-black/deep navy, teal/cyan and restrained gold/imperial design.

**Site build blocker (2026-10-23):** Lovable editor request rejected because workspace is out of credits. Existing 3 illustration assets and project knowledge are saved, but updated page UI and navigation **are not deployed**. No deceptive 'live customer product' claim.

## Acceptance criteria (not yet met)

- [ ] A domain lead confirms both vertical workflows map to a real customer's processes and data definitions.
- [ ] Signed pilot consent, DPA, subprocessor inventory, sensitive-data inventory, documented use of Claude/ChatGPT/Make/Zapier if chosen.
- [ ] Versioned website ↔ backend schema; no open proxy or browser secrets.
- [ ] Tenant-isolation tests, role denial, data deletion test, connector-offline fail-closed, event replay, retry idempotency and rollback proof.
- [ ] Payroll, payments, invoices and regulatory effects require verified human authority.
- [ ] Reference docs cite source and access rights; tests for cross-tenant retrieval and prompt-injection resistance pass.
- [ ] Independent review of each feature and measured accuracy/false-positive rate on consented examples.
- [ ] Exact GitHub SHA, Ruff, mypy, pytest and reproducible evidence recorded; draft PR reviewed; no automatic merge.
- [ ] Owner authorizes controlled staging; staging is independently observed before production approval.
- [ ] Lovable credits available; frontend changes implemented, built, verified and published separately.
- [ ] Testimonials, revenue improvements, saved hours, retention and customer logos only after documented consent and measurement.

## Governance / release gates

Status of charter: **LOCKED PROPOSED SCOPE**. Implementation: **SYNTHETIC CANDIDATE**. Tests/independent review: **NOT RUN**. Staging/production: **HOLD**. Finance, HR and regulatory effects: **HOLD**. This charter adds a new service line without merging AUREX staging candidates or altering live VALEXII.COM.

**Do not publish private internal codenames on website; do not introduce CoreGuard or Quilla in public copy.**
