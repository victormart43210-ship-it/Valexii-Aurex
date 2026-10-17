# KUSANAGI 9.9 — VALEXII-AUREX Financial Commercialization Target

**TARGET LOCKED FOR EVALUATION: 9.9/10 potential (ASPIRATIONAL, NOT ACHIEVED).**

**Admissibility: HOLD.** A subjective business-potential rating cannot become a fact just because a model assigns 9.9. Product success, real customer revenue and security must be evidenced independently. This milestone commits to pursuing the target, not fabricating its accomplishment.

## Canonical first product

**AUREX Financial Evidence Review** — evidence-backed, human-reviewable investigation of vendor invoices, work tickets, purchase orders, spreadsheet calculations, payments, credit memos and suspected duplicate charges. Build a defendable first wedge with *oilfield service businesses and contractors*, then expand to adjacent field-service and accounts-payable workflows.

No AI system may approve payments, move money, falsely clear risks, or claim verified customer value without evidence. All financial results are advisory. This is a separate business stream from the BCXMET cybersecurity application.

## Thresholds proposed as requirements for a future 9.9 assessment

| Qualification | Target | Verification requirement |
| --- | --- | --- |
| Market willingness to pay | **3 independently verified paying businesses**, each observed for >=30 days | Signed contract, payment reconciliation and customer interview |
| Evidence volume | **>=1,000** consented documents, >=100 per pilot; **>=5,000** labeled critical fields and **>=1,000** reconciliation decisions | Representative blinded review, field-by-field human ground truth |
| Machine-readable documents | **>=95%** text availability after local extraction and/or consented OCR | Separate scanned-PDF cohort and quality evidence |
| Correct critical fields | **>=99%** | Independent reviewer audits amount/date/vendor/item/category accuracy |
| Reconciliation precision | **>=99%** | Reconcile TP/FP from independent labels; minimize false positives |
| Reconciliation recall | **>=95%** | Reconcile TP/FN from independent labels |
| Critical discrepancies | **Zero known misses within independently reviewed pilot sample** | An observed sample is not proof of zero possible missed fraud |
| Time saved | **>=40%** human review time including correction and appeal | Timed comparable workflows; document manual baseline |
| Unit economics | **>=70%** fully loaded delivery gross margin | Verified collected receipts and costs (OCR, storage, cloud, support, operator labor) |
| Governance | Consent, documented review and source integrity; zero known pilot privacy incidents | Independent privacy/security verification, retention/deletion controls |
| Live delivery | Authenticated owner-only published website → Railway bridge proven | Close GitHub Issue #65 / IRON BRIDGE PR #66 separately |

These are **proposed** evidence thresholds, not forecasts, achieved business metrics, security certifications, or guarantees of a 9.9/10 outcome. Retention, competition, legal/accounting liability, defensible IP, and real market feedback can still prevent a 9.9 rating.

## Baseline versus the target

- In the *Create Logo Options* workstream, the 100-PDF controlled batch **reportedly** produced **15 native text extractions** and **85 NO_TEXT_LAYER** results. This is not equivalent to >=95% document usability. OCR for scanned documents and independent extraction accuracy validation are priority blockers. Do not claim OCR is implemented from this result.
- The reported Excel inventory includes 1,690,160 formula cells; inventory != verified recalculation or financial accuracy.
- Synthetic reconciliation examples and local-source inventory do not establish real-world reconciliation accuracy or customer savings.
- The financial engine's latest source is on an owner-managed Chromebook and is not confirmed imported into canonical main. Draft PR #67 prepares the privacy-safe source inventory. **Do not place any PDFs, spreadsheets, SQLite evidence files, OCR contents, names or financial records in GitHub.**
- Railway API is ONLINE; its published website-to-backend authenticated integration remains **NOT VERIFIED**. Draft PR #66 is a review candidate, not a release admission.

## Four execution waves to earn commercial potential

**WAVE A — Single-repository convergence.** Finish read-only published frontend/Railway authentication evidence. Safely inventory and import the local financial modules as reviewed source-only commits in Valexii-Aurex. Do not merge the divergent convergence branch wholesale, alter live Railway changes, or launch paid agents.

**WAVE B — Document understanding and reconciliation.** Add opt-in, local-first OCR for scanned PDFs; record text-layer availability, page-level extraction quality, file hashes and source lineage; implement deterministic cents-based invoice/payment/ticket/credit matching and incomplete-data HOLD conditions. Independently measure precision, recall, error classes and missed critical discrepancies. Preserve originals on the USB drive.

**WAVE C — Three limited paid pilots.** Secure three independent consenting businesses, at least 30 days each, with manual-review requirements. Test one saleable outcome: clearly evidenced potential invoice discrepancies that reduce labor or prevent overpayment. Pilot pricing remains a hypothesis until signed paying customers and documented costs exist. No automatic billing, financial transfers or customer outreach without approval.

**WAVE D — Outside verification and commercialization decision.** Publish only privacy-safe aggregate statistics; have an independent evaluator validate pilot measurements, financial cost allocation, contract/revenue proof and security. Re-rate commercial potential after comparison with real alternatives and demonstrated retention. A self-reported JSON file is never an independent witness.

## Automated aggregate scorecard (standalone, offline, non-authoritative)

Code: aurex/commercial/pilot_gate.py; script: scripts/check_financial_pilots.py; synthetic tests: tests/test_financial_pilot_gate.py. The scorecard reads a locally supplied JSON document containing **only pseudonymous aggregate pilot totals**, rejects extra fields or suspect types, evaluates the proposed thresholds, and returns blocking gate codes and ratios. **It always returns HOLD even when the reported targets match.** The CLI exits with nonzero status, never grants deployment authority, never contacts a network, and never handles raw financial documents.

Commands, from the repository root:

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_financial_pilot_gate.py
    python3 scripts/check_financial_pilots.py --input /private/local/aggregate_pilots.json

Never commit the private aggregate input, real invoices, bank data or customer identities. Do not mistake SHA-256 of local evidence for an independent witness. Real consent, independent labels, market validation, owner-only integration, recurring revenue and privacy/security review are required for any future upgrade.

## Constitutional lock

- **9.9/10 is the north-star commercial potential target, not the current score.**
- **Unknown ≠ healthy; no self-witness; authority NONE for model or report self-assertions.**
- **Evidence → Qualification → Reality → Authority → Effect.**
- **Default budget $0**; no external paid inference or live financial execution.
- **No production publish, protected merge, finance upload, charges, or real financial-document reads without explicit owner authorization.**
- Keep the financial-engine integration in **canonical Valexii-Aurex**, with separate accountable milestones for UX, security, OCR, reconciliation, and paying customers.
