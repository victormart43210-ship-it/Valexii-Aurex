# KUSANAGI CIX — AUREX DATA, FORMULA, SNAPSHOT & EVALUATION CONTRACT v1

**Mode:** CONTRACT ONLY / NOT AN IMPLEMENTED TRAINING RUN
**Parent:** docs/KUSANAGI_CIX_WORLDWIDE_FINANCIAL_INTELLIGENCE_LOCK.md
**Mainline base:** df0654390049118a142ec3b3356f0f40b4789fe4
**Budget:** $0 automatic external model/API spend. No data exfiltration. No payment authority.

## A. One chain of custody from physical file to client review

AUREX records three independent facts: **the bytes observed**, **the extracted/normalized claims**, and **the independently justified accounting treatment**. Do not collapse them.

### A1 — Document receipt v1

Fields MUST include:
- tenant_id, project_id, ingestion_job_id (canonical typed IDs scoped to tenant)
- original_sha256, original_mime_detected, original_filename_display (never trusted path), byte_length, collected_at, recorded_at
- origin_type and source_system, source_document_identifier, original_uri (private vault; authorization-bound)
- ownership/licensing/processing_rights/training_rights separately stated; training_rights defaults FALSE
- retention_policy_id, jurisdiction, deletion_hold, personal_data_classification, data_boundary
- extractor_name + pinned version + options, document_parse_status (SUCCESS/PARTIAL/FAILED/NOT_RUN), bounded runtime cost and error category
- original bytes held separately from extracted facts, with tamper-evident ledger and access log.
- Source signature / hash verification is **not** a substitute for proving the document was issued by the claimed counterparty.

### A2 — Spreadsheet cell witness v1

Fields MUST include:
- document SHA, workbook/sheet/cell and named range, formula_text_raw, formula_language/locale;
- last_stored_cached_value (if present), cache_observed_at (if known), cache_trust=UNVERIFIED;
- independently_recalculated_value (if supported), decimal_currency, quantity_units, evidence_reference list;
- external workbook links, named ranges, hidden sheets and macro presence flags;
- rule_id + rule_version + signed agreement/effective date, reviewer disposition and divergence reason.

**Three-way epistemic split:**
1. Excel formula is evidence of a workbook's intended computation.
2. Cached value is evidence of its last stored result, not a verified recomputation.
3. AUREX result is evidence of code execution against explicit inputs, not proof the approved rate or underlying field work was genuine.

Always compare formula-vs-cache-vs-AUREX-vs-contract where independently possible. If formulas are unsupported or external links missing, output HOLD/NOT VERIFIED instead of silently substituting cached result. Pinned read-only library; never execute embedded macros, malicious links, DDE, vendor-supplied scripts or formulas on upload.

Source: https://openpyxl.readthedocs.io/en/3.1/tutorial.html

### A3 — Transaction / line claim v1

Normalized monetary amounts use integer minor currency units or Decimal with currency and explicit rounding rule. No binary floats for authoritative money.
- role=AR_SERVICE_COMPANY or AP_OPERATOR, tenant_id, project/work order/crew/asset IDs
- contract_id, effective_rate_version, line_type (LABOR/EQUIPMENT/MATERIAL/SURCHARGE/TAX/CREDIT), period_start/end
- documented_qty + units, authorized_unit_price, invoiced_amount, payable_amount, received/paid_amount, currency
- approved PO scope, signed field ticket & supporting hours, valid signed change orders, owner-authorized tolerances
- source references for **each** non-derived field: original SHA + location (PDF page/bbox, workbook sheet/cell, database row)
- exception_type, comparator version, review identity and effective auth lease at decision time.

### A4 — Evidence/decision v1 (W3C PROV-influenced)

**Entity**: original documents, extracted fields, normalized transaction, exception report, audit packet.
**Activity**: ingest/extract/reconcile/challenge/review/export.
**Agent**: machine adapter, model or authenticated human, with agent_type and source/tenant scope.
**Links**: used source → activity → produced derivative, rule version, time, run ID, idempotency key.
**Authority is separate**: historical observations cannot authorize current payment; revocation does not erase historic decision. Present 'NOT VERIFIED' until independent witness verifies original provenance.
Source: https://www.w3.org/TR/prov-o/ ; https://openlineage.io/docs/spec/object-model/

## B. Ingestion of legacy ~27k-class local folder

**Current progress: NOT RUN in CIX research.** Last-reported source count is historic and must be remeasured. The source USB is not available to these GitHub writes.

Incremental importer MUST:
1. Acquire lock/checkpoint with source-root fingerprint + latest complete cursor, preserve immutable raw source bytes, take verified database backup.
2. First pass filename/type/magic/size + SHA inventory (no OCR). Classify PDFs, xlsx, xls, csv, doc, zip and unknown separately.
3. Second pass safer native parsers: PDF text and tables, spreadsheet formulas + cache, native invoice JSON. Do not trigger active content or fetch external references.
4. Optional OCR only on candidates with inadequate native content and authorized computing resources. Quarantine malformed documents, bombs, password-protected files, scanner crashes, ambiguous OCR output and unsupported financial structures.
5. Never mark a batch PASS on mere file discovery. Use attempted/completed/partial/failed/unsupported/duplicate/quarantined counts; checksum results and persist cursor only after atomic per-file commit.
6. Dedupe by source hash, preserve duplicates that have different business meaning; never merge customer invoices based on matching amounts alone.
7. Verify restorability and sample against independently inspected originals; detect extraction drift after parser updates.
8. No upload to Google/GitHub/Firecrawl/hosted LLM by default. Publish only redacted counts, synthetic exemplars and non-sensitive code artifacts.

Data integrity against uncontrolled files informed by OWASP secure upload guidance:
https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

## C. Financial control library

Original AUREX-owned rule families with explicit logic and source-required fields:
- **LABOR_BILLING**: approved hours × effective role/location/time rate; compare to billed and signed ticket; overtime/travel conditions explicitly declared.
- **EQUIPMENT_BILLING**: approved run/standby hours × signed equipment rate, minimum hours, rounding and exclusions; compare invoice.
- **MATERIAL_BILLING**: units × effective unit prices plus approved freight; verify signed quantity/receipt.
- **RATE_EFFECTIVE_DATE**: every invoice line has an applicable signed rate revision for work date; future/stale/overlapping rate cards route HOLD.
- **PO_INVOICE_MATCH**: match order, amended order, ticket/receipt, invoices and authorized caps (2-way / 3-way plus service confirmation).
- **AR_MISSING_REVENUE**: approved billable work vs issued customer invoices and credits; missing billing a candidate, not a guarantee of recoverability.
- **AP_OVERCHARGE**: approved payable amount vs invoice lines + adjustments, tax jurisdiction checks delegated to qualified advisor.
- **DUPLICATE**: same counterparty/ref/time/amount plus supporting semantics; probable duplicate only, no fraud declaration.
- **PAYMENT_POSTING**: payment against invoice approval and bank/ledger evidence; absence of payment proof = unknown, not unpaid.
- **BALANCE_RECONCILIATION**: ledger/net totals by period/currency/unit, separately validated contra entries.
- **AUDIT_DOCUMENT_GAP**: required evidence manifest completeness by customer/jurisdiction policy, not universal certification.
- **CHANGE_APPROVAL**: exception resolution tied to actor/lease/version, append-only decision log.

All rules versioned, tested with positive/negative cases, explicit tolerance and rounding, and require independent domain review for contract edge cases. The model may suggest a rule but cannot mutate a rule or fabricate source references.

## D. Qwen: train → snapshot → blind eval → compare → gated admission

### D1 — Base-model resolution
- Baseline uses only **actually available, license-reviewed pinned weights**. AUREX main already has training/README.md and an optional Qwen2.5-0.5B-instruct LoRA pipeline; no production claim implied.
- Qwen 4 remains a future candidate based on 2026 official 'in training' statement. Before any use verify exact public model repo, weight checksum, architecture support, tokenizer/template, license and commercial data terms, and compatible GPU/RAM/storage.
- LoRA/QLoRA training occurs on separately authorized equipment; no unbudgeted remote cloud/GPU. Training GGUF directly not assumed; original Transformers weights and explicit tested export procedure.

### D2 — Dataset and rights registry
Every example has dataset_id, record_id, source_type, source_sha, label_maker, rights_category, training_permission, retention/deletion status, redaction/pseudonymization status, language/locale, case_family, vendor/customer-group ID and time bucket. NEVER train on documents merely because they were ingested for a customer audit. Keep multi-tenant and embargo restrictions per customer. Separate synthetic/public licensed vs consented-private, and store any sensitive datasets outside git.

### D3 — Four dataset partitions (by organization/time/document family)
- TRAIN: learning examples, many document styles and legitimate/erroneous cases.
- DEV: supervised tuning feedback; can be reused, never called blind.
- LOCKED VALIDATION: reviewer-labeled independent records, used for candidate admission but not for gradient tuning.
- PRIVATE FINAL HOLDOUT: sealed, different counterparties/templates/time slices, with answers inaccessible to inference worker, trainers, prompt engineers and benchmark collection processes. One-time use per version; regenerate after accidental leakage.

Official Humanity's Last Exam reserves private questions to assess overfitting. AUREX adopts that evaluation principle; its internal industrial financial benchmark is **not official HLE**, not evidence of HLE performance and not a substitute for real-world auditing.
Source: https://lastexam.ai/

### D4 — Per-snapshot immutable manifest

For snapshot n:
~~~
snapshot_id
git_head_sha, training_pipeline_sha, exact_model_base_revision, model_license_review
weights_sha256 / LoRA_adapter_sha256 / tokenizer_sha256
dataset_manifest_sha256 + rights_review_sha256 + split_manifest_sha256
train_config_hash, seed, hardware, duration, total cost, external inference spent
baseline_snapshot_id, evaluator_code_sha, calibration_data_set, locked_test_version
line_item_field_precision/recall, discrepancy_precision/recall, FN/FP counts
false_authority_attempts, source_citation_accuracy, cross_tenant_violations
critical_financial_errors, downstream human_review_minutes, export_retrieval_latency
raw_independent_score_receipts, adjudicator IDs, exceptions and release HOLD/PASS gate
~~~

A synthetic evaluator that imports the same oracle as the candidate is not independent. Treat quality as independently witnessed only when domain-label sources and held-out test integrity have been checked by reviewers **outside the model builder's sole authority**.

### D5 — Snapshot evaluation task families
1. Controlled invoice OCR/line item extraction with line-to-page/cell citations and missing field abstention.
2. Rate- and effective-date-sensitive arithmetic, unit conversion, credit/void/tax isolation and rounding.
3. Two-way, three-way and field-ticket matching with valid and invalid exceptions.
4. Same-looking legitimate invoice pairs vs true duplicates, with evidence requirements.
5. Missing document vs definitely mismatched document vs contradictory signatures.
6. AR missed billable work vs unbillable work; AP overcharge vs valid surcharge.
7. Prompt injection embedded in invoice/Excel cells instructing the AI to approve a payment.
8. Malicious retrieval provenance, poisoned worksheet formula, changed rate book, stale cached formula.
9. Retrying or resuming LangGraph checkpoints after ACL revocation, expired review lease, deleted doc, vendor changes or worker crash.
10. Audit-packet completeness versus actual validity; forbid statements of certified compliance.
11. Boundary cases using different currencies, locales, decimals and rate book units.
12. Confidential record isolation and memorization extraction tests across tenants.

### D6 — Metrics and gate thresholds

Track measured: confusion matrix, precision, recall, false negative rates **on a labeled denominator**, exact amount and unit correctness, extraction field F1, unsupported-source citation rate, false approval/unauthorized tool side-effects, reviewer agreement, document-packet retrieval coverage, retrieval time, rework and operational cost. Store raw confusion counts as first-class evidence; never present synthetic 100/100 as real-domain accuracy. Pre-register acceptance thresholds with independent oilfield reviewers and customer before test execution; **thresholds TBD**, not invented.

Absolute safety gate: **0 observed unauthorized external payments, tenant data leaks or permission bypass in the tested scope**; one such event fails release, but zero in tested cases is not universal safety proof. Unknown, missing or stale evidence = HOLD. A regression in critical financial misstatements forbids automatic promotion even if averaged loss improves.

Optional research tools: MLflow local versioned eval dataset and model snapshots; UK AISI Inspect for independent model/agent tests; no dependency or SaaS authorization implied. Sources:
https://mlflow.org/docs/latest/genai/datasets/
https://inspect.aisi.org.uk/
https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/new-initiatives-to-strengthen-ai-safety-and-resilience

## E. Runtime graph and authority separation

Optionally place LangGraph around deterministic AUREX actions for stateful retries/interrupts, not as source of financial authority. A checkpoint captures cursor/progress; on resume, canonical AUREX rechecks actor, tenant, permissions, rate-book snapshot, rule version, source hash, current lease, budget, idempotency and existence/retention of originals. Every external effect requires a fresh action-specific approval checked inside canonical backend, not a string like 'approved' from model/state checkpoint. Production durable checkpoint store must be isolated per tenant and protected by authorization, deletion and retention. **Graph node may output interpretation but never authority_granted=true.**

Source: https://docs.langchain.com/oss/python/langgraph/interrupts

## F. Independently auditable export packet and product metrics

Required export acceptance:
- Document inventory count by expected source type, including missing and rejected files.
- Original reference (when authorized) and sha256, extracted claim with source coordinate.
- Rate/PO/ticket/invoice/payment reconciliation and all exception history with approved/disputed/unreviewed.
- Effective-dated policy and rule versions, human signatures/identity verification and revocation visibility.
- JSON/CSV summary + PDF/readable packet, non-plaintext secret handling, restricted download + export event log.
- Artifact manifest with content SHA and generation time and independent replay script. A hash provides tamper evidence only relative to a separately trusted prior root.
- Sample external auditor/accountant review confirms package usability; no AUREX-issued assurance opinion.

Measure customer ROI with validated outcomes only: verified corrections, verified recovered/captured payments, AP review time saved, AR rejection rates, dispute resolution, prepared-packet retrieval time, per-case total cost. **No 'savings' claimed from speculative flagged amounts or unbilled hours without adjudication.**

## G. Required exit evidence by wave

| Phase | Observable acceptance artifact | Status entering CIX |
|---|---|---|
| Corpus | Newly measured local file tally + hash manifest, backup/restore, per-batch success/fail/quarantine counts | NOT RUN |
| Financial engine | Exact-head, independently run real candidate and synthetic source-linked replay, negative multi-tenant and permission tests | HOLD (draft PR #99) |
| Packet | Sample generated 9-doc + 100-case evidence trail and verified export/reimport/read access | NOT RUN |
| Qwen baseline | License-pinned hardware/weights, training rights review, sealed split hashes and held-out scores | NOT RUN |
| Snapshot compare | Pre-registered blinded performance deltas + critical regressions with independent reviewer | NOT RUN |
| Customer pilot | Written permission, per-tenant isolation, audit packet accepted by qualified finance reviewer, verified ROI | NOT RUN |
| CI/production | Exact-head independent CI and hosted API↔worker↔UI evidence plus explicit owner deployment authorization | HOLD |

This is a **specification**, not an assertion that any executable path or model training is ready or running. No keys, original financial files, user-private personal data or unlicensed third-party datasets are embedded here.

## H. Review gate
CUSTOS = HOLD pending cross-family independent source review and verification, exact head SHA CI recovery, and owner approval for integration/merge. Separate UI/orb animation remains presentation-only, motion authority NONE. The user allocated five Lovable credits to Ouroboros; this contract expends none.
