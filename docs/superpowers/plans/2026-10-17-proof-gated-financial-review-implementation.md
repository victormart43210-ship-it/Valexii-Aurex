# KUSANAGI OMEGA — Proof-Gated Financial Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a **review-only, zero-cost, synthetic-data Python pilot** which produces complete tamper-evident financial comparison receipts and always holds financial authority for human review.

**Architecture:** Separate immutable Pydantic v2 evidence contracts, deterministic versioned canonical hashing, pure discrepancy comparison, and a fail-closed review gate. The caller passes explicit synthetic inputs and evaluation time. Evidence shows what was compared; the gate cannot independently authenticate source custody or authorize any payment.

**Tech Stack:** Python >=3.12, Pydantic >=2.9, stdlib `decimal`, `datetime`, `hashlib`, existing `aurex.provenance.canonical_json`; pytest, Ruff, Mypy strict.

**Spec:** `docs/superpowers/specs/2026-10-17-proof-gated-financial-review-design.md`. Owner approved the design direction October 17; the **plan and implementation method still require owner review**.

## Global Constraints

- Work in the existing `victormart43210-ship-it/Valexii-Aurex` only. Create a **fresh isolated branch from current main** after refreshing its exact SHA; no bulk merge from the divergent convergence branch.
- Owned product paths: `aurex/financial_review/` and corresponding `tests/test_financial_review_*.py`. Preserve all unrelated changes, open PRs, installed connectors and project source.
- Offline synthetic fixtures only. No file scans, USB access, raw invoice uploads, paid inference, network calls, payments, new API routes, database migrations, agent jobs or financial effect.
- Money is `Decimal` (finite, non-negative, two-place scale for v1 USD/EUR/GBP); **reject float and Boolean input**. Missing is `None`, NEVER zero.
- All input `SourceRef` authenticity/custody claims are **UNVERIFIED metadata**. Hashes prove byte consistency **only if recomputed against independently held originals**, which this pilot does not see.
- `review_case` always returns `authority="HOLD"` and `human_review_required=True`; finding is `DISCREPANCY`, `NO_DISCREPANCY_DETECTED`, or `INDETERMINATE`. No ADMIT, clearance, approval or payment effects.
- Full normalized receipt digest must cover **all fields** including date, tax, line items, evidence provenance, source SHA claims, evaluation time, policy, finding, uncertainty, and source-claim status.
- Report `PASS / FAIL / NOT RUN / NOT VERIFIED` by exact SHA; independent human review and CI are mandatory before release admission. No publish/merge/deploy without separate approval.

## Proposed File Ownership and Contracts

`aurex/financial_review/models.py` — strict frozen Pydantic v2 `SourceRef`, `FieldEvidence`, `InvoiceLine`, `InvoiceFacts`, `ReferenceFacts`, `ReviewCase`, `Discrepancy`, `ReviewReceipt`. Proposed fields:
- `SourceRef(source_id:str, kind:Literal["INVOICE","PURCHASE_ORDER","FIELD_TICKET"], sha256_original_bytes:str, custody_root:str, obtained_at:datetime, source_verification_claim:Literal["UNVERIFIED","CLAIMED_VERIFIED"]="UNVERIFIED")`.
- `FieldEvidence(field_name:str, source_id:str, origin:Literal["MANUAL_ENTRY","PARSER"], text_span:tuple[int,int]|None=None, verification_status:Literal["UNVERIFIED","REVIEWED"]="UNVERIFIED", unknown_reason:str|None=None)`.
- `InvoiceLine(description:str, quantity:Decimal|None, unit_price:Decimal|None, amount:Decimal|None)`; use decimal-safe validation and bounded text. No floats or implicit USD.
- `InvoiceFacts(source_id:str, vendor_id:str|None, invoice_number:str|None, invoice_date:date|None, currency:Literal["USD","EUR","GBP"]|None, grand_total:Decimal|None, tax_amount:Decimal|None, line_items:tuple[InvoiceLine,...]=(), field_evidence:dict[str,FieldEvidence])`.
- `ReferenceFacts(source_id:str, reference_id:str|None, vendor_id:str|None, currency:Literal["USD","EUR","GBP"]|None, authorized_total:Decimal|None, item_quantities:dict[str,Decimal]=..., field_evidence:dict[str,FieldEvidence])`.
- `ReviewCase(case_id:str, invoice:InvoiceFacts, reference:ReferenceFacts|None, sources:tuple[SourceRef,...])`.
- `Discrepancy(field:str, invoice_value:str, reference_value:str, source_ids:tuple[str,...])` (represent exact canonical value strings, never user-entered arbitrary markup).
- `ReviewReceipt(schema_version:Literal["pilot-v1"], case_id:str, evaluation_time:datetime, policy_version:str, normalized_inputs:dict[str,Any], source_claims:tuple[SourceRef,...], discrepancies:tuple[Discrepancy,...], unresolved:tuple[str,...], finding:Literal["DISCREPANCY","NO_DISCREPANCY_DETECTED","INDETERMINATE"], authority:Literal["HOLD"], human_review_required:Literal[True], digest_sha256:str)`.

`aurex/financial_review/canonicalize.py` — `receipt_digest(body: dict[str, object]) -> str` using domain-separated SHA256 of `b"AUREX-FIN-REVIEW\x00v1\x00" + canonical_json(body)`. Canonicalization is deterministic: Decimal fixed-scale strings, ISO date and UTC timestamps, preserved semantic line-item order, sorted source IDs only when order is irrelevant.

`aurex/financial_review/compare.py` — `compare_case(case:ReviewCase) -> tuple[tuple[Discrepancy,...],tuple[str,...]]`: report missing fields as unresolved, exact vendor/currency/amount mismatches as discrepancies, include source citations. Do not assume a date matches across independent PO/tickets unless both carry an explicitly comparable date.

`aurex/financial_review/gate.py` — `review_case(case:ReviewCase, *, evaluation_time:datetime, policy_version:str="pilot-v1") -> ReviewReceipt`. Compute finding as INDETERMINATE when any required data/reference missing, otherwise DISCREPANCY on known mismatch, otherwise NO_DISCREPANCY_DETECTED. Set authority HOLD and review required unconditionally.

`aurex/financial_review/__init__.py` — re-export `ReviewCase`, `ReviewReceipt`, `review_case` only.

## Review Focus (five likely product-breaking inputs)

1. Fake `source_verification_claim="CLAIMED_VERIFIED"` with different `custody_root` values MUST NOT raise authority or report custody authenticity. Test in Task 4.
2. `grand_total=None` while `tax_amount=0` must remain unknown—not a zero-total match. Task 3 and Task 4.
3. Two invoices matching the same PO but with **different item lines/tax** must generate distinct digests even when the comparison finding is the same. Task 2.
4. Boundary monetary inputs (float/NaN/Infinity/-0.01/excess decimal places) must fail validation rather than round silently. Task 1.
5. Same semantically normalized records inserted in different source order should hash identically; different source custody and text-span claims must hash differently. Task 2.

---

### Task 1: Strict Financial Models and Synthetic Fixtures

**Files:** Create `aurex/financial_review/models.py`, `aurex/financial_review/__init__.py`, `tests/test_financial_review_models.py`.

**Interfaces:** Produce the Pydantic models listed above, used by Tasks 2–4. Preserve source field references; validate every referenced source ID exists in `ReviewCase.sources`, source IDs unique, reference source different from invoice source, UTC-aware `obtained_at`, valid 64-hex source hash, bounded field and source IDs, and duplicate `FieldEvidence` key consistency.

- [ ] **Step 1 RED:** Write `test_money_rejects_float_nan_negative_and_overprecision`, `test_missing_grand_total_is_none`, `test_source_refs_require_known_unique_source_ids`, `test_real_calendar_dates_only`, `test_invalid_source_digest_rejected`. Build synthetic `invoice_fixture`, `reference_fixture` in test module; ensure no external document.
- [ ] **Step 2 Verify RED:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_financial_review_models.py`. Expect failures due to missing types.
- [ ] **Step 3 GREEN:** Implement strict frozen Pydantic validators; `Decimal` via strings; reject bool/float before coercion; normalize `Decimal("-0")` to allowed zero only if explicit; two decimal places for monetary totals; quantities may have up to three; dates as actual `date` objects.
- [ ] **Step 4 Verify:** Rerun targeted tests, expect full PASS; `python -m ruff check aurex/financial_review tests/test_financial_review_models.py`; `python -m mypy --strict aurex/financial_review`.
- [ ] **Step 5 Commit:** `git add aurex/financial_review tests/test_financial_review_models.py && git commit -m "feat(omega): add strict synthetic financial evidence contracts"`.

### Task 2: Complete, Deterministic Evidence Receipt Digest

**Files:** Create `aurex/financial_review/canonicalize.py`, `tests/test_financial_review_digest.py`.

**Interfaces:** Consume a complete `ReviewReceipt` body **without `digest_sha256`** using `receipt_digest(body:dict[str,object])->str`. Reuse `aurex.provenance.canonical_json` and stdlib `hashlib`, not an external hashing library.

- [ ] **Step 1 RED:** `test_receipt_same_canonical_inputs_same_digest`, `test_digest_changes_for_date_tax_items`, `test_digest_changes_for_original_byte_hash_custody_status_and_policy`, `test_digest_changes_for_provenance_text_spans`, `test_source_order_only_does_not_change_digest`. Use complete synthetic receipt-body fixtures, no default runtime timestamps.
- [ ] **Step 2 Verify RED:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_financial_review_digest.py`. Expect missing function failures.
- [ ] **Step 3 GREEN:** Implement canonical recursive serialization with explicit type support (`Decimal` as fixed-scale string, aware `datetime` to UTC ISO, `date` ISO, Pydantic `model_dump(mode="python")` without computed digest). Reject unsupported types/non-finite numbers; use `SHA256(domain||canonical_json(...))`. Keep invoice line order.
- [ ] **Step 4 Verify:** Targeted pytest and Ruff/Mypy checks PASS; run a mutation sweep over every `InvoiceFacts`, `InvoiceLine`, `SourceRef`, `FieldEvidence` property and record unsupported/exempt field list (ideally none).
- [ ] **Step 5 Commit:** `git add aurex/financial_review/canonicalize.py tests/test_financial_review_digest.py && git commit -m "feat(omega): bind complete provenance to versioned receipt digest"`.

### Task 3: Deterministic Comparison and Fail-Closed Unknowns

**Files:** Create `aurex/financial_review/compare.py`, `tests/test_financial_review_compare.py`.

**Interfaces:** Consume `ReviewCase` and return `(discrepancies,unresolved)`; no network, external data, model inference or payment action.

- [ ] **Step 1 RED:** `test_equal_vendor_currency_total_has_no_discrepancy`; `test_total_difference_cites_both_sources`; `test_missing_total_is_unknown_not_zero`; `test_currency_vendor_mismatch`; `test_conflicting_values_never_silently_converted`; `test_missing_reference_yields_unresolved`. Validate that invoice ID/date must be present and valid but are not compared against an unrelated PO ID/date.
- [ ] **Step 2 Verify RED:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_financial_review_compare.py`.
- [ ] **Step 3 GREEN:** Implement exact Decimal comparisons; cite field and source IDs. Detect `None` explicitly and append stable unresolved reasons; comparison of amounts only when currency available; no automatic FX.
- [ ] **Step 4 Verify:** Rerun tests, Ruff and Mypy strict; check permutations of missing fields and conflicting fields produce deterministic ordering and no false match.
- [ ] **Step 5 Commit:** `git add aurex/financial_review/compare.py tests/test_financial_review_compare.py && git commit -m "feat(omega): report explainable exact discrepancies and unknowns"`.

### Task 4: Advisory-Only Human Proof Gate

**Files:** Create `aurex/financial_review/gate.py`, `tests/test_financial_review_gate.py`. Update `aurex/financial_review/__init__.py`.

**Interfaces:** `review_case(case:ReviewCase, *, evaluation_time:datetime, policy_version:str="pilot-v1")->ReviewReceipt`. In all successful returns, `authority=="HOLD"`, `human_review_required is True`.

- [ ] **Step 1 RED:** `test_human_review_required_even_on_equal_claims`; `test_authority_remains_hold_for_verified_claim_strings`; `test_discrepancy_finding_is_not_approval`; `test_missing_reference_returns_indeterminate`; `test_same_inputs_same_evaluation_time_same_digest`; `test_any_mutated_field_changes_digest`; `test_naive_or_future_timestamps_rejected_or_explicitly_flagged`; `test_receipt_never_includes_unmasked_source_text_or_auth_secrets`.
- [ ] **Step 2 Verify RED:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_financial_review_gate.py`.
- [ ] **Step 3 GREEN:** Collect complete `ReviewCase.model_dump(mode="python")`; apply `compare_case`, classify the finding with INDETERMINATE precedence on missing required fields, set authority HOLD unconditionally, record exact `evaluation_time` and `policy_version`, canonical-hash record excluding the digest itself. No filesystem/network/API actions.
- [ ] **Step 4 Verify:** Targeted tests and type/lint; inspect exact serialized receipt to ensure only synthesized structured field values and source hash claims are present.
- [ ] **Step 5 Commit:** `git add aurex/financial_review tests/test_financial_review_gate.py && git commit -m "feat(omega): issue deterministic advisory review receipts without authority"`.

### Task 5: Exact-SHA Acceptance, Negative Matrix and Independent Review

**Files:** Create `tests/test_financial_review_adversarial.py` and a brief scoped `docs/KUSANAGI_OMEGA_STAGE1_REVIEW.md`. Do not change existing API, Railway or website.

- [ ] **Step 1 RED:** Add tests attacking malicious self-verified custody metadata, same-root documents, duplicate case/source IDs, revoked/expired source assertions, mutated dates/tax/lines, subtotal-as-total attempts (typed source explicitly required), unknown fields, oversized text, dates without timezone, hash spoofing and attempted float/bool monetary coercion. Add a test asserting the receipt schema has **no** authorization or payment effect and no network calls.
- [ ] **Step 2 Verify RED:** Run new tests on a deliberately tampered pre-fix fixture or affected earlier version; prove tests actually catch the named defects. A red because a test is wrong doesn't count.
- [ ] **Step 3 GREEN:** Repair only scoped model/gate/hashing defects; don't patch failing tests into false passes.
- [ ] **Step 4 Full checks:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q`; `python -m ruff check .`; `python -m mypy --strict aurex`; `python -m compileall -q aurex`. Record exact tool versions, times, outputs and the HEAD SHA. Mark commands NOT RUN if tools unavailable.
- [ ] **Step 5 Independent review:** Another reviewer inspects exact PR SHA; challenge correctness, digest completeness, unknown/false-zero behavior, provenance/custody limitations and unauthorized effects. Report actual results, uncertainties, dependencies and why project remains financial authority HOLD.
- [ ] **Step 6 Draft PR:** Publish only an isolated **draft** PR based on fresh main. Include tests, review report and rollback (discard branch). No merge, release, deployments, data migration or real invoices.

## Explicitly Deferred / Not a Stage-1 Done Condition

- Automatic OCR or repair of the old `aurex/financial_extractor.py`; the seven legacy parsing failures are a separate Stage 2 adapter task.
- Independent authentication of invoice issuers or signatures, revocation services, external procurement API, human approval state, live AUREX/OX UI and BCXMET policy binding.
- Any production claim, customer saving, claimed extraction accuracy, commercial pilot or payment execution.
- Do not imply that an advisory HASH proves invoice authenticity. The human reviewer must check evidence outside the pilot.

## Acceptance and Next Gate

Stage 1 acceptance is **reviewable source + complete synthetic RED/GREEN tests + explicit human HOLD + independent review**. Exact-head CI must run; do not infer it from a narrative release report. Production decision remains **HOLD**.

**Owner plan review gate:** This plan is proposed for review. The approved *design* alone does not authorize writing product code. After owner reviews this plan, choose a supported execution route (native or worker-assisted) and implement on fresh main in a new branch. No background automation.
