# OPERATION KUSANAGI CXV — FIRST CUSTOMERS: AUREX FIELD AUDIT

**Commercial objective:** establish a genuine, independently verified, repeatable oilfield financial-reconciliation business, starting in the Midland–Odessa Permian Basin. **Positioning:** "Protect Every Dollar. Verify Every Record. Stay Audit-Ready." This is a customer-discovery and readiness program; no customer-data pilot or paid service is claimed to exist.

**Base:** canonical main `df0654390049118a142ec3b3356f0f40b4789fe4`. **Status:** DEVELOPMENT / CUSTOMER DATA HOLD. Existing draft PRs #99 (synthetic reconciliation), #100 (commercial design), #101 (offline evidence receipts), #102 (cross-domain G-Factor evaluation) are unmerged; this branch does not incorporate them and does not modify the backend or website.

## 1. One technology spine, two buyers

| Buyer | What needs independent verification | Who must be involved |
|---|---|---|
| **Oilfield service company (AR)** | Signed field tickets and work logs vs dated approved labor, equipment, rentals, materials and invoiced line items; potential unbilled work, missed approved revenue or unauthorized credits | Owner/controller, field supervisor and customer billing lead |
| **Operator/E&P company (AP)** | Vendor invoices vs approved contracts/ratebooks, field tickets, PO and changed work orders; wrong rates, duplicate bills, questionable hours and missing approvals | AP controller, procurement and operations reviewer |

Tenant data **must not** be shared across the two sides of a transaction without lawful consent and authorization. **Qwen** is not a beta prerequisite. Start with deterministic review of fictional documents; once independently admitted, LLM assistance may suggest extractions and explanations but never authorize money or records.

## 2. Commercial milestone: 2–3 independent discovery companies, THEN beta

1. **NOW — FREE discovery:** 15–20 minute conversations, fictional demo only, no financial records collected, no claim that customer software is live.
2. **VALIDATE pain:** ask about the monthly ticket volume, current review tools, which exceptions actually hurt, reviewer time, documentation retrieval, objections and value.
3. **CLOSED PILOT ADMISSION:** do not accept real records until the 11 safeguards listed below have been independently evidenced and the owner has obtained appropriate legal/contracting authorization.
4. **CONDITIONAL 60–90-day founding pilot:** proposed $499/month with written scope and explicit customer approval *after* beta admission and contracting review; no checkout, no billed customer now.
5. **SUBSCRIPTION VALIDATION:** test $499 Starter, $1,499 Professional and $3,999+ Enterprise; pricing is hypothetical until customers, measured costs and contracts validate it. First traction is one customer willing to renew from independently verified value—not a vanity-signup count.

No arbitrary launch dates, guaranteed savings, guaranteed audit pass, regulatory certification, claims of AI reasoning efficacy, or signed professional audit opinions.

## 3. New offline admission gate

`workstation/field_pilot_admission.py` is a **local manifest inspector only**, not a customer-data ingestion engine. It requires exact defined statuses, SHA-256-shaped witness digests, timestamps and reviewers for:
1. `EXACT_HEAD_CI`
2. `AUTHENTICATED_E2E`
3. `TENANT_ISOLATION`
4. `SOURCE_CUSTODY`
5. `CONSENT_AND_RIGHTS`
6. `SECURE_DOCUMENT_INTAKE`
7. `DETERMINISTIC_QUALITY`
8. `INDEPENDENT_SECURITY_REVIEW`
9. `HUMAN_REVIEW`
10. `BACKUP_AND_ROLLBACK`
11. `CUSTOMER_CONTRACT`

A failed/unknown/absent/stale or self-witness check returns HOLD. Even when every check is *declared* PASS, output is only `INDEPENDENT_ADMISSION_REVIEW_REQUIRED`, **never** data access or release permission; a reported digest and reviewer name do not verify that source or person's identity. Separate independent reviewers must authenticate evidence and customer rights. Model modes are `deterministic_only` and `qwen_advisory` (advisory remains prohibited for real customers without further model validation). $0 external spend; payment authorization NONE. Test locally with:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_field_pilot_admission.py
python3 -m workstation.field_pilot_admission --manifest /path/to/independently-reviewed-admission.json
```

Existing hosted GitHub CI failures remain unresolved; do not claim PR tests passed in CI or conceal failed checks. Real customer files, payment systems, Qwen weights, database changes and auto-deployment remain out of scope.

## 4. Buyer discovery: first 9 questions

1. Are you a service-company billing team or an operator/AP team? Who owns the process?
2. Roughly how many invoices and field tickets per month? (Range only.)
3. Which current ticketing and accounting systems do you use? (Product names, not passwords.)
4. Which documented exceptions occur most often: omitted work, rates, equipment, hours, duplicate invoices or missing approval?
5. How are contract changes and effective dates reflected in pricebooks?
6. How are disputes resolved, who reviews them and where is evidence stored?
7. How much review time is spent per month on invoices and gathering audit support?
8. What would constitute a verifiable pilot success and who has contracting authority?
9. What would you pay per month for *independently confirmed* reductions in review effort or leakage?

**No actual names of vendors, values, rates, invoices, bank data, driver records, tax IDs or user credentials** requested in discovery. Do not share pilot material with prospective customers as though it were live proof.

## 5. Measured outcomes — preregister denominators

- Human-reviewed **exception precision** and **recall** on independently labeled sample, by service vs operator; don't infer recall without a complete label set.
- Unsupported flags / 100 documents, manual reviewer minutes / 100 documents and missing-rate/approval proportion.
- Source completeness: authorized document lineage available / eligible reconciliation cases.
- Separate **suggested discrepancy**, **independently confirmed discrepancy**, **book adjustment** and **cash recovered**: never equate them.
- Observed customer workflow preparation time vs baseline; case exports with source links, versioned rates and outstanding uncertainties.
- Actual storage/compute, OCR, support and reviewer costs against willingness to pay; validate margin before launching tiers.

A synthetic example with invoice $28,750 and ticket $25,000 yields a $3,750 **provisional variance**, *not an overcharge finding*: authorized additions, credits, taxes and effective rates remain to be checked. The only final outcome in this demo is human-review HOLD.

## 6. Official-site prospect research — unsent

Public contacts are discovery hypotheses, not active partnerships, warm leads or proof of need. Verify addresses before contacting.

| Prospect | Side | Why it may fit | Official source |
|---|---|---|---|
| **Rush Energy Services** | Service AR | Odessa flowback and well testing: equipment/crew ticket-to-invoice flow | https://rush-energy.com/ ; published info@rush-energy.com |
| **Premier Flow Control** | Service AR | Odessa flowback, nitrogen, equipment rental / possible rental-hours reconciliations | https://premierflowcontrol.com/ |
| **ProPetro** | Service AR (later/larger) | Midland fracturing/cementing and wireline operations; potential enterprise design partner | https://www.propetroservices.com/contact/ ; published Sales@propetroservices.com |
| **Three Span Oil & Gas** | Operator AP | Independent Midland operator; published accounts-payable contact | https://www.threespan.com/ ; published ap@threespan.com |
| **Boaz Energy II** | Operator AP | Independent Midland/Permian operator; AP workflow discovery | https://boazenergy.com/ ; published info@boazenergy.com |
| **UTPB SBDC** | Business advising | Texas startup entity, insurance, pilot contracts, legal/privacy readiness | https://www.utpb.edu/directory/office/sbdc |

Research on official websites is not due diligence on procurement authority or vendor workflow. Company contact emails are published business contacts, not a personal-information corpus.

### Three introductory drafts — created in Gmail, not sent

**Service AR — Rush**: Ask for 15–20 minutes with the owner of ticket-to-invoice reconciliation; no uploads requested; explicitly developmental.
**Operator AP — Three Span**: Ask AP reviewer about invoice↔contract↔field-ticket workflows; fictional demonstration only.
**Business formation — SBDC**: Ask for advising meeting on entity formation, pilot agreements, security expectations, insurance, and first paying customers.

Full, individually tailored draft bodies are saved in Gmail for owner review. No external email has been sent; do not send automatically.

## 7. Acceptance and rollback

**Evidence → Qualification → Reality → Authority → Effect** and *the system may never be its own sole witness*. A prospect agreeing to talk never authorizes ingestion. Passing a toy synthetic gate never proves real-customer accuracy. No unverified amount is a recoverable dollar.

Independent reviewer must attest the actual controlled environment, real measured benchmark, rights, source provenance, separate tenant authority, E2E and backups. Hosted CI and legal/customer signatures are currently **NOT VERIFIED**. A business entity must be able to enter contracts and meet applicable obligations before money collection.

**Rollback:** this new draft branch only adds three dev files; no data, site, production service, API contract, database or deployment was changed. Close draft PR to discard if requirements change. **CUSTOS = HOLD**.