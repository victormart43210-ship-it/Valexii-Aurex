# Operation KUSANAGI CCXLIII — UAE × CERN research-adapter groundwork

Status: DESIGN/TEST CONTRACT ONLY. Production HOLD; financial authority NONE; paid inference OFF. This branch deliberately starts from `main` to avoid modifying the open stacked #171/#174/#177/#178 candidate. It does not merge Jules #172/#176 or Copilot #175.

## Purpose

Measure whether UAE model research and CERN scientific-workflow practices improve DISPATER's industrial audits without replacing AUREX's evidence, exact financial calculations, or human authorization. THE BIG ONE is an authorized real-company *validation dataset*, never an algorithm archive, training corpus, public fixture, or default input. No real records are admitted in this branch.

## Candidates and primary upstream sources

| Candidate | Source | License / caution | Initial decision |
|---|---|---|---|
| REANA | https://github.com/reanahub/reana | MIT; full platform requires infrastructure | Prototype *reproducibility contract*, do not deploy REANA |
| Rucio | https://github.com/rucio/rucio | Apache-2.0; heavyweight distributed storage | Study data identity/replication patterns only |
| KITAB-Bench | https://github.com/mbzuai-oryx/KITAB-Bench | MIT repository; inspect individual datasets/model licenses | Adopt evaluation methodology on synthetic industrial documents |
| AIN | https://github.com/mbzuai-oryx/AIN | MIT code repository; verify weights/dataset terms independently | Evaluation-only; no default model download |
| K2 Horizon 0.9B / 3.7B | https://huggingface.co/IFM/K2-Horizon-0.9B ; https://huggingface.co/IFM/K2-Horizon-3.7B | Verify exact model revisions, weights license, remote code, memory/runtime | Isolated challenger model, no authority |
| Falcon-H1 0.5B / 1.5B | https://github.com/tiiuae/falcon-H1 | Custom Falcon-LLM license; legal review for commercial use | Isolated challenger only |
| ROOT | https://root.cern/ | Review core and component licenses | Optional research/statistics, never Decimal accounting |
| InvenioRDM | https://inveniosoftware.org/products/rdm/ | Inspect component licenses and infrastructure | Metadata/versioning patterns only |

Do not interpret an open model's weights as standard OSI-licensed software. Do not execute unreviewed model repository code (including unrestricted `trust_remote_code`). Never enable network downloads, inference charges, or customer-data transfer without separate approval.

## Frozen integration boundary

Implement only behind explicit opt-in feature flags and versioned typed contracts. Default `enabled=false` for all new adapters. Existing DISPATER results and receipts must be byte-for-byte unchanged with flags off.

**Audit replay manifest v1** (local, deterministic JSON, canonical serialization):
- schema_version; tenant_pseudonym; audit_run_id; source_digest_set (sorted SHA-256, no original names); normalized_schema_version
- rule_pack_digest; adapter_ids_and_pinned_revisions; code_commit; environment_lock_digest; model_id_revision_or_null
- deterministic_parameters; decimal_context; event_graph_digest; output_digest; created_at (metadata only, excluded from deterministic digest)
- `manifest_digest` from canonical payload; independent replay compares output digest and economic-event allocations.
- HMAC/signature is an additional authenticated receipt, not equivalent to plain SHA-256. Never expose signing keys.

**Document evaluation record v1**:
- synthetic_fixture_id, source_type, extraction_engine_and_version, field_type, expected_literal, extracted_literal, page_or_cell_locator
- exact-match for invoice number/date/currency/amount, normalized edit distance for text, table cell association, false-positive and withheld rates
- no model-generated answer key. Human-curated or deterministic oracle only.

**Challenger result v1**:
- fixture_id; prompt_digest; model_revision; output_digest; cited_source_ids; proposed_hypothesis; disagreement_flags; latency_ms; peak_memory_bytes
- `authority=NONE`, `financial_effect=NONE`, `network_allowed=false`; model may propose but cannot qualify or approve.

## Work packages

1. **Cursor — audit replay:** compare #178's computation manifest before adding code; extend only missing pieces; synthetic 36-month ledger; replay with changed rule pack must detect invalidation; corrupt a cent and prove failure; reject shared-root circular witnesses.
2. **Jules — document evaluation:** compare #174's digital PDF/XLSX parsers and #172 pipeline; implement a synthetic-only test harness for scanned tables, dates, amounts, handwritten cases where an actual licensed OCR backend exists; fail closed otherwise. Preserve original document bytes and per-field provenance.
3. **Copilot — independent oracle:** write *independent* expected financial totals, adversarial tests, dependency and license inventory, supply-chain/remote-code audit. Confirm #175 assurance fixes survive #177/#178 integration. The author of the algorithm must not be its sole verifier.
4. **Coordinator — integration:** freeze contracts first; keep independent worktrees; integrate serially on reviewed candidate; do not merge or deploy without owner approval.

## Gate tests (must pass before any enablement)

- Flags off: no regression or external calls; receipts and monetary outputs unchanged.
- Replays: same inputs/rules/version -> same economic result; changed source/rules -> new identity; replay is independently reproducible.
- Finance: Decimal-only; no double counting; misallocated/reversed payments withheld; `confirmed_recovery=0` without independently approved and settled evidence.
- Documents: unsupported OCR -> WITHHELD; page/field provenance survives extraction; no fabricated text.
- Models: malformed/circular citations rejected; contradictory evidence does not auto-authorize; no credentials/customer data in prompts; bounded time, memory, tokens and network.
- Tenant separation; encrypted local storage; no public sensitive manifests; no unauthorized USB access.
- Performance: compare against current Qwen baseline on same *synthetic* cases; report correctness, false positives, hallucinations, CPU/RAM, elapsed time, costs; don't infer results from upstream benchmarks.
- Commercial license and dependencies verified at pinned versions before importing model weights.

## Owner-local THE BIG ONE protocol (not executable here)

Confirm authorization and exact USB mount on Chromebook. Inventory read-only in owner-controlled environment; generate pseudonymized counts and salted/controlled digests for review; no raw paths or records in public PR. Audit with independent reference samples and preserve zero-findings as valid outcomes. Never claim the USB was inspected until actually accessed.

## Acceptance / reporting

Deliver an independently reviewable draft PR and `docs/operations/JULES_CHATGPT_HANDOFF.json` (or an additive CCXLIII handoff if that file already exists) with exact commits, tested commands, passes/failures, unresolved security/license issues, model memory and cost results, and explicit NOT RUN items.

This document is a groundwork contract only: no new engine, runtime dependency, model, OCR installation, or customer-data ingestion is asserted. Production HOLD. Financial authority NONE.
