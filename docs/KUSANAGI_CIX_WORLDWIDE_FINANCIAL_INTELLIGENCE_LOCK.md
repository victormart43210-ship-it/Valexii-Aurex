# OPERATION KUSANAGI CIX — WORLDWIDE FINANCIAL INTELLIGENCE PRODUCT LOCK
**Status: PRODUCT DIRECTION LOCKED FOR DEVELOPMENT / CODE & BETA RELEASE HOLD**
**Research date:** 2026-10-20
**Canonical repository:** victormart43210-ship-it/Valexii-Aurex
**main_base_sha:** df0654390049118a142ec3b3356f0f40b4789fe4
**Change class:** Research-driven, original AUREX product and engineering contract; no dependency installs, no ingestion, no fine-tuning, no customer upload, no website deployment.
**Dependencies:** Draft PR #99 (synthetic oilfield evaluation), draft PR #89 (original nine-document pilot), other release candidates must be independently evaluated before selective admission; they are NOT canon.

## 1. Owner-approved commercial positioning

**AUREX FIELD AUDIT: Protect Every Dollar. Verify Every Record. Stay Audit-Ready.**

One enterprise product, one canonical AUREX backend, two distinct buyer workflows:
- **Revenue Protection** (oilfield service company): unbilled field tickets, billable labor/equipment/materials omitted, undercharges, disputed or rejected invoices, changing rate cards, credits missing from receivables.
- **Expense Protection** (operator/buyer): vendor overbilling, duplicate invoices or payments, incorrect approved contract/rate, excess hours or quantities, unsupported charge, unapproved change orders, missed credits.
- **Continuous Audit Readiness** (both): indexed and provenance-linked contracts, field tickets, signed approvals, rate books, invoices, payments, ledger entries, reconciliations, exception history, and exportable review packages.
- **Qwen-assisted Financial Intelligence**: consent-cleared extraction, classification, grouping, discrepancy explanations and review suggestions; model has zero financial decision authority.

One shared deterministic reconciliation core with tenant-segregated evidence, separate receivables/payables views, and human decision points. Workflows may match an inter-company transaction only with explicit lawful permissions from all applicable parties. No side has implicit access to the other side's materials.

**Selling outcome:** reduced missing revenue and leakage, fewer unsupported invoices, and less time gathering records when an audit or customer inquiry arrives. **Never claim zero errors, guaranteed savings, guaranteed audit pass, statutory audit opinion or regulatory certification.**

## 2. Competitive features to adapt — NOT copy

| Public reference | Valuable pattern | AUREX-owned implementation boundary |
|---|---|---|
| BILL (USA) | Two-/three-way matching, routing disputed invoices to reviewers | Two-way invoice↔PO; three-way invoice↔PO↔receipt/field-ticket; role-limited review queues and exception reasons. No payment execution by default. |
| Fieldwire (USA) | Field forms, versioned field documents, inspections and reports | Offline-friendly evidence capture and indexed job/project daily record timeline, with signed/timestamped versions. |
| Veryfi (USA) | Structured invoice OCR, line-item fields and source-region confidence | Bounded extractor adapters yielding source-page/box references, data confidence and uncertain-field HOLD. Provider optional; not a verified authorizing source. |
| Enverus OpenTicket (USA) | Contract price validation, field tickets, timestamps and bulk review | Effective-dated rate book, equipment/labor units, ticket↔invoice checks, bounded manual batch review. No wholesale copying of proprietary interface or algorithms. |

Market competitors already support substantial overlapping features. **Our proposed distinction is continuously verifiable, reviewable audit-evidence readiness across both AR and AP, not the invention of matching or oilfield ticketing.** Conduct buyer interviews to prove willingness to pay.

Primary research:
- BILL: https://www.bill.com/blog/announcing-automated-three-way-matching-with-bill
- Fieldwire: https://www.fieldwire.com/blog/best-construction-field-management-platform/
- Veryfi: https://www.veryfi.com/invoice-ocr-api/
- Enverus: https://www.enverus.com/products/openticket/

## 3. Worldwide standards and implementation crosswalk

These are **design inspirations / optional jurisdictional profiles**, not declarations that specific foreign law applies to a Texas pilot.

| Region / body | Validated public insight | Adopt now vs later |
|---|---|---|
| **USA — IRS** | Business accounting records substantiate income, costs and tax positions; retention depends on record and circumstances | **NOW**: original record vault, searchable source links, retention policy metadata; do not promise tax compliance. https://www.irs.gov/businesses/small-businesses-self-employed/recordkeeping |
| **UK — FRC / ICO** | GenAI/agentic audit-quality risks and meaningful human review with challenge/override logging | **NOW**: no-self-witness, material audit-review trail; professional audit remains with qualified humans. https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/ ; https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/human-review/ |
| **EU — EN 16931 / Peppol** | Machine-readable e-invoices with shared semantic models and validation constraints | **LATER** optional UBL/EN16931 mapping + legal applicability check, not a US beta prerequisite. https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108950/EN+16931+compliance ; https://peppol.org/ |
| **EU — DORA** | ICT risk-management requirements for in-scope financial entities | **LATER** relevant for eligible EU financial-market customers only, not default oilfield compliance. https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng |
| **Canada — CRA** | Electronic records need continuing readability and reliable access, with recoverable backups | **NOW design**: tested restore/export and searchable originals; Canadian retention & storage rules only if business jurisdiction requires. https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/ic05-1/electronic-record-keeping.html |
| **Australia — ATO** | Business records must preserve relevant detail and support reconstruction; many records retained five years with exceptions | **NOW design**: integrity, retention metadata, reproducible reprocessing; do not apply universal five-year retention to all jurisdictions. https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/record-keeping-for-business/overview-of-record-keeping-rules-for-business |
| **Singapore — IMDA (October 2026)** | Agentic safety testing includes agent/tool actions, unauthorized access, and post-change reevaluation | **NOW tests**: tool-call/adversarial/replay evaluation; no claimed IMDA accreditation. https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/new-initiatives-to-strengthen-ai-safety-and-resilience |
| **India — GST eInvoice** | JSON schema and invoice registration formats can drive structured exchange | **LATER** explicit India connector with local tax expert; no blanket jurisdiction claims. https://einvoice1.gst.gov.in/others/bulkgenerationtools |
| **International — ISO 15489** | Records management needs declared metadata, responsible custody, record controls, monitoring and processes | **NOW design**: original bytes, provenance, lifecycle, access, deletion holds; don't claim ISO certification. https://committee.iso.org/sites/tc46sc11/home/projects/published/iso-15489-records-management.html |
| **International — W3C PROV-O** | Entity, Activity, Agent and derivation concepts model reproducible document lineage | **NOW**: AUREX witness/event ledger fields map to source / action / actor / derived output. https://www.w3.org/TR/prov-o/ |
| **International — OpenLineage** | Jobs, runs and datasets provide reproducible cross-system processing lineage | **LATER** optional event export; use local AUREX minimal event schema initially. https://openlineage.io/docs/spec/object-model/ |
| **International — IFRS XBRL** | Financial disclosures can use machine-readable taxonomy, but are specialized reporting artifacts | **LATER** only if customer requires financial reporting. https://www.ifrs.org/digital-financial-reporting/ |

## 4. Locked canonical capability boundaries

**Canonical governed flow:** Evidence → Qualification → Reality → Authority → Effect.
Reverse challenge: ROTAS. **The system may never be its own sole witness.**
- **IN**: authenticated tenant/actor, authorized source, content hashes, rights/consent, declared policy & business purpose.
- **CORE**: extract data; normalize with units and currencies; compute **integer cents / Decimal** comparisons; check contract effectiveness and supporting facts; independent challenger; log uncertainty and exceptions.
- **OUT**: explainable exceptions, evidence-linked review packets, human decisions, suggested corrected invoice line items. Model text and UI/Orb cannot mutate governed truth.
- **TIME**: source date, field-work date, rate effective interval, invoice date, transaction time, evaluation timestamp, snapshot ID, audit-period closing, expiry/revocation and legal hold.
- **Authority**: HUMAN_REVIEW_REQUIRED or HOLD until verified. A matching invoice is NOT 'financially certified'; no receipt is a pass simply because it is present.
- **Effect**: no automatic transfers, bank account changes, payment instructions, claim of fraud, tax filings or external delivery without a separately specified and freshly authorized workflow. Default external LLM budget $0.
- **Tenant confidentiality**: enforce tenant ID in every read, storage key, index query, model retrieval and processing lease. No vendor/operator data crossover by shared identifiers or prompts.

## 5. One package per transaction — audit-readiness differentiator

AUREX's **Audit Readiness Packet v1** is a manifest + linked originals + findings + human adjudications, with:
- tenant + audit scope/period, rule and model versions, manifest SHA-256, original file SHA-256, file type and declared origin;
- canonical job/project/vendor/invoice/payment identifiers, line-item provenance to page/region/cell/source row and rate effective date;
- expected vs present evidence by policy; each missing record explicitly **MISSING**, stale **STALE**, inaccessible **NOT VERIFIED**, conflicting **CONTESTED**;
- normalized values, independently recomputed math, reconciliation differences, tolerance/policy overrides with approver & timestamp;
- human decisions with identity verified at authorization boundary, scoped permission, reason and immutable history; revocations change current authority, never rewrite history;
- source license and permitted data use, retention/hold/delete schedule, export access log, export destination policy;
- reproducible export of index, exception list and referenced original files. Do not add hidden customer data to model training outputs.

Define 'audit-ready' as **documentation retrieval and completeness against the customer's agreed checklist**. Distinguish package completeness from correctness or sufficiency of any underlying transaction.

## 6. Spreadsheet formula knowledge without trusting spreadsheet truth

Capture workbook SHA, sheet/cell coordinates, raw formula bytes, cached Excel value **separately**, named ranges, external links, references, effective date, locale, currency/unit and calculated lineage. openpyxl's data_only returns values last stored by Excel; it is **not independent recalculation**. Extract candidate equation patterns only after review: hours×rate, equipment×rate, material units×price, tax/surcharge, invoice/PO/ticket/paid variance, credit/void and duplicates. Preserve original formula as evidence, derive authorized contract rules from signed source documents, and recalculate in a pinned independent decimal engine. Detect broken links, circular references, macros, hidden sheets, stale caches, unauthorized manual changes, formula-injection and inconsistent date/rate application. Never run spreadsheets' macros, DDE or external links during ingestion. Excel file receipt alone never authorizes a financial conclusion.

Source: https://openpyxl.readthedocs.io/en/3.1/tutorial.html

## 7. Local ~26k-28k file corpus — inventory first, training later

The previously discussed ~27,965 file count / ~23,640 PDFs / 1,928 Excel files / ~1.69M formula cells is **user-reported historic inventory, not current measured repository data**. The USB drive and local SQLite ingest database were **not mounted or read** for this research. Do NOT claim ingestion progressed.

Plan: re-inventory drive → capture total, type/byte count, file dates, source rights & checksum baseline → immutable local backup → bounded incremental scan → quarantine malformed/unparseable/infected files → native text/table extraction before selective OCR → Excel formula/cached-value classification → provenance and per-file status ledger → validate packet summaries and independent samples. Report each run: attempted / completed / skipped / failed / quarantined / OCR-needed / duplicated / bytes and elapsed time, preserving resume cursor. No entire corpus or commercial customer records pushed into GitHub, external OCR, unapproved cloud model endpoints or public benchmarks. Review original source licenses/permissions before training.

Document-parser evaluation: optional **Docling** for PDF tables/layout/OCR and source coordinate extraction; evaluate open-source license, model asset licenses, CPU/memory load, rendering fidelity and adversarial upload safety before admission. https://github.com/docling-project/docling ; https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

## 8. Qwen fine-tuning policy

Qwen's publisher said **Qwen 4 was still in training** in its September 2026 roadmap. Do not assign Qwen 4 weights or licenses before an official release is verified. Use an explicit, pinned available model and our existing training/ LoRA pipeline as baseline; no fake Qwen4 run. https://www.alibabacloud.com/blog/alibaba-clouds-2026-apsara-conference-full-stack-ai-roadmap-along-with-global-market-expansion-plan_603598

**Model duties:** OCR field extraction aids, record classification, entity matching suggestions, evidence-linked narrative generation, under/overbilling investigation prioritization and request-for-missing-evidence drafts.
**Deterministic code duties:** normalized arithmetic, rate validity, exact bounds, hashes, case completeness, identity/tenant guards, spending/payment authority, retention policy enforcement and status promotion.
**Training input gate:** no PII or commercial confidential source without lawful purpose, consent/contract rights, deidentification review, explicit training license, and test/train isolation. Being allowed to *process* a client's invoice ≠ being allowed to *train* on it.

Full snapshot-and-blind-evaluation contract is in **docs/KUSANAGI_CIX_DATA_TRAINING_EVAL_CONTRACT.md**; its gates precede production fine-tuning.

## 9. Pricing and commercialization (hypotheses, NOT market-validated)

Buyer profiles:
- Service companies: recover billable hours/materials, reduce rejections; show reconciled AR/field-ticket revenue and verified corrections.
- Operators: reduce improper AP and manual review; show reconciled PO/field-tickets/contracts/invoices and independently confirmed disputed costs.
- Both: lower review preparation time, improve records retrieval and human accountability.

Proposed test offers: founder pilot $499/month (only when secure), Starter $499, Professional $1,499, Enterprise $3,999+ with contract-specific volume limits, privacy and implementation costs priced explicitly. These are **positioning experiments, not published AUREX contracts nor validated willingness-to-pay**. Price based on confirmed customer economic value, extraction/storage/compute costs, review labor, integration and legal/security overhead. Never bill clients based on unconfirmed AI 'savings'.

## 10. Sequenced delivery and hard release gates

**P0 — Repair independent CI and audit baseline:** Resolve owner GitHub Actions billing lock *as reported by Jules CVIII*, independently confirm fix from GitHub account status, rerun exact SHA. Jules' 382-pass report and 100/100 synthetic findings are **reported not independently validated in this branch**, and GitHub workflows have reported failure. Do not disable checks to fake a pass.

**P1 — Complete owner-local evidence ingestion:** Inventory 27k-class drive, bounded PDF/Excel extraction, provenance/permissions ledger, error and restore drill, no silent failures, verified read-only document lineage and one-way replay into internal test fixture.

**P2 — One reconciler, dual views:** Own-source selection from draft PR #99 + #89 by independent reviewer; do not bulk merge. Synthetic 100-case regression, unknown/duplicate/stale/source tamper, rules/tolerance/rate changes, inter-tenant rejection, $0 budget, trace from source to exception. Owner view for AP/AR separate but same engine.

**P3 — Audit readiness packets:** Per-policy required evidence matrix, gap flags, retrievable originals and decisions, documented human review/overrides, export, integrity checks, tenant isolation, rollback and deletion/legal hold test.

**P4 — Qwen model snapshots:** Authorized corpus only, train vs held-out split by source company/vendor/workbook family/time; baseline model, subsequent LoRA revisions, sealed blind tests, independent annotators and full regression. No Qwen4 until weights/license verified. Include manual-review workload and error costs.

**P5 — Closed industrial pilot:** One service company and one operator **separately** under written agreement, explicit data use, account isolation and authorized reviewer. Prove real precision/recall and false-negative bounds on independently labelled real cases, time-to-export audit packet, retrieval completeness, cost/case, time saved and **confirmed** invoice corrections. Do not claim third-party audit certification. Commercial launch only following fresh explicit owner permission.

**P6 — Global capability profiles:** Peppol/EN16931, India GST eInvoice, IFRS/XBRL, Canada/Australia retention rules and qualified advisors only where customer need and jurisdiction warrant. Do not let profile selection auto-certify compliance.

### Non-negotiable beta acceptance ledger
- Every control assigned PASS / FAIL / HOLD / NOT RUN / NOT VERIFIED **from independent evidence**, not a model claim.
- Exact source SHA, dependency versions, configuration, test provenance and independent reviewer identity.
- Reproducible clean-run script and exact-head CI; separate local runner evidence when hosted CI billing locked.
- No old draft branch treated as mainline; one verified, owner-authorized merge at a time.
- Website ↔ backend ↔ worker ↔ evidence store proof must be observed, with zero unauthorized spend.
- No unapproved deployment, payment or customer-data upload. Ouroboros is **presentation only; motion authority NONE**.
- The expected beta-revenue and customer ROI are measurable hypotheses, not already-achieved facts.

**Decision recorded:** This document locks the *agreed product direction*, not a live release, regulation compliance or an authorized code merge. Its addition in a draft PR is a proposed canonical spec pending review/mainline admission.
