# KUSANAGI CXIV — AUREX G-FACTOR (Generalization Evaluation Gate)

**Scope:** Local, offline, $0 snapshot comparison for the existing AUREX Qwen training/evaluation lane. **DOES NOT compute human psychometric g**, prove AGI, produce an intelligence quotient, fine-tune a model, run HLE, or authorize financial actions.

**Base:** main `df0654390049118a142ec3b3356f0f40b4789fe4`. **Isolation:** `work/kusanagi-cxiv-gfactor-generalization`. **Release:** HOLD. No merge or deployment.

## What we implemented

- `training/g_factor_eval.py` — original AUREX source-only evaluator for six fixed capability domains:
  `document_extraction`, `spreadsheet_reasoning`, `invoice_reconciliation`, `contract_interpretation`, `audit_evidence`, `novel_transfer`.
- Compare an explicitly versioned **baseline model snapshot** and **candidate snapshot** against the **same externally prepared reference**. Never train on held-out reference examples or pass answer labels to model inference.
- Deterministic exact-label + **required source-evidence ID** equality; any cited source ID outside the case reference forces `HOLD_INVALID_EVIDENCE_REFERENCE`, even if other cases improve. An invalid baseline citation forces comparator HOLD. a confident answer citing invented or incorrect source IDs is incorrect. An `ABSTAIN` answer does not increase accuracy.
- Require at least 5 held-out cases, 2 held-out source-group fingerprints and 1 novel example **per domain** (minimum 30). This is a structural **diagnostic floor**, NOT statistically sufficient for production. Use larger power-calculated datasets for real evaluation.
- Require a **non-empty** `training_group_hashes` declaration and reject *declared* overlap with held-out group hashes. An absent training-group declaration is HOLD, never assumed clean. The tool **cannot independently prove** that hash lists are truthful or that semantic/dataset contamination is absent. Verification needs separately sourced sample provenance.
- Require exact case coverage (no missing/extra/duplicate case IDs), strictly bounded JSON/UTF-8, reject symlinks, duplicate JSON keys and nonfinite values, and pin raw input SHA-256 hashes in the output.
- **Non-compensatory regression rule:** a gain in one domain cannot hide a decline in another domain or its novel subset. Any model output granting itself financial authority or effects fails regardless of accuracy; an unsafe baseline is not accepted as a trustworthy comparator.
- A candidate that improves at least one domain without regressions is only `REVIEWABLE_SYNTHETIC_GENERALIZATION_GAIN`. Not `PASS`, not independently verified, not launch-ready, and never permission for payment or deployment.
- No dependencies, hosted services, external API calls, or model weights. Existing `training.train_lora`, `training.evaluate_lora` and `training.prepare_dataset` remain unchanged.

### Why this is *not* psychometric g

The statistical g factor in psychometrics is a latent variable inferred from relationships among many diverse cognitive tests, with model and measurement assumptions. A six-domain AUREX gate does not identify such a factor. Calling it **G-Factor** means **Generalization gate** in our engineering nomenclature, not measured general intelligence. It must not be marketed as an IQ/g value.

## Input contract

All local JSON files must be UTF-8, regular non-symlink files <=1 MiB each. The reference contains no customer invoice values or document bodies; it uses short abstract evidence IDs.

```json
{
  "schema": "aurex.gfactor.reference.v1",
  "benchmark_id": "sealed-benchmark-v1",
  "reference_reviewer": "independent-reviewer-identifier",
  "approved_for_evaluation": true,
  "training_group_hashes": ["64-character-lowercase-hex-digest"],
  "cases": [
    {
      "case_id": "case-001",
      "domain": "invoice_reconciliation",
      "group_sha256": "64-character-lowercase-hex-digest",
      "novel": true,
      "expected_label": "DISCREPANCY",
      "required_evidence": ["ticket_001", "ratebook_v2"]
    }
  ]
}
```

Note: the example above intentionally omits the complete >=5-by-six-domain benchmark and uses digest placeholders; it is NOT runnable as-is.

Model outputs are produced **independently**, outside this script. Do not place sealed references in the model prompt or retrieval index.

```json
{
  "schema": "aurex.gfactor.predictions.v1",
  "benchmark_id": "sealed-benchmark-v1",
  "snapshot_sha256": "<64-char-lowercase-hex-model-artifact-digest>",
  "answers": [
    {
      "case_id": "case-001",
      "label": "DISCREPANCY",
      "cited_evidence": ["ticket_001", "ratebook_v2"],
      "authority": "HOLD",
      "effect": "NONE"
    }
  ]
}
```

These are **declared** snapshot digests. Verifying model weights, dataset custodians and reviewer identity is the responsibility of an independent verifier; values alone cannot prove identity or integrity.

## Invocation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_g_factor_eval.py
python3 -m training.g_factor_eval \
  --reference /secure/evals/held_out_reference.json \
  --baseline /secure/evals/qwen_before_predictions.json \
  --candidate /secure/evals/qwen_after_predictions.json
```

**Exit codes:** 0 = informative cross-domain comparison ready for independent review **only**; 1 = regression / safety / no gain HOLD; 2 = malformed or invalid inputs HOLD. In all cases `production_release=HOLD`. This code does not sign results, issue financial approvals, deploy Qwen, export proprietary data, or independently attest real model intelligence.

## Planned training snapshot process

1. Collect lawfully authorized, permission-cleared records. Keep customer-inference consent separate from **training rights**; no automatic use of the user's reported ~27,965 local documents.
2. Prepare annotated canonical cases from independently verified calculations, dated contracts and audit evidence. Never assume workbook formulas or cached values are correct.
3. Hash and seal a genuinely unseen evaluation set, split by customer, site, company, vendor and time. Keep reference labels and group hashes off the Qwen training/inference path.
4. Snapshot baseline Qwen model weights and prediction receipts. Independently capture candidate predictions under the same bounded inference budget and hardware settings.
5. Run this G-Factor gate. Inspect per-domain true/false labels, abstentions, novel transfer, safety, error types, and cost/latency separately. This gate **does not** estimate confidence intervals, calibration or false-positive rates by itself.
6. Independently verify sample custody, annotations, model artifacts, benchmark contamination, statistical uncertainty and bias. Do not use the same model or agent that implemented/trained a change as its sole reviewer.
7. Only after exact-HEAD CI PASS, privacy/tenant controls, full site→backend→worker→SQLite→evidence proof and explicit human authorization may a **separate** production process admit a capability. This evaluator never promotes authority.

**Release doctrine:** Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness. Unknown ≠ healthy. Missing/stale/undocumented ≠ PASS. Held-out loss ≠ correctness; toy benchmark correctness ≠ real-customer efficacy. **CUSTOS: HOLD**.

## Review requests and known limits

- Independently run exact HEAD source/test suite and check Ruff/Mypy where available. GitHub-hosted CI has previously stopped under an owner account billing lock; do not claim all checks passed.
- Inspect adversarial test cases and add real, separately annotated and sufficiently sized task samples with variance/uncertainty analysis **without** committing private labels or financial records.
- Review benchmark source provenance, license/usage rights, reviewer identity, adversarial prompt injection, customer data isolation, and runtime resource bounds before actual LoRA snapshots.
- Rollback: close the draft branch/PR; no runtime/config/DB changes are required.
