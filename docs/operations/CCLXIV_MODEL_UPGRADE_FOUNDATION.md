# OPERATION KUSANAGI CCLXIV — Sovereign Model Upgrade Foundation

Date: 2026-11-06
Status: PLANNING ONLY / no model installed / no inference verified
Related: CCLXIII_WEBSITE_IMPLEMENTATION_FOUNDATION.md, PR #186.

## Mission
Discover and assess pretrained open-weight models worldwide; safely benchmark upgrades to the existing AUREX Qwen baseline, document OCR for DISPATER, and optional specialized LoRA adapters. All changes stay in the one canonical Valexii-Aurex repository. No automatic download, model execution, merge, production deploy, or paid API use.

## Nonnegotiable safeguards
- Evidence → Qualification → Reality → Authority → Effect; the system may never be its own sole witness.
- Financial authority NONE; production release HOLD; external paid inference OFF; no customer data.
- XAELI advisory only; BCXMET Orb presentation only.
- Model-generated values are candidate interpretations, never verified accounting amounts or evidence receipts.
- Preserve exact golden ledger: $385 identified, $150 withheld, $0 confirmed recovered.
- Never load unreviewed remote model code or execute downloaded scripts. Pin revisions, hash files, check license and supply-chain provenance, inspect safetensors/GGUF, isolate runtime, disable egress by default.
- No unattended external downloads, inference fees, or training runs. A model listed on USB is not a verified installed weight.

## Wave 0: inventory and contracts
1. Inspect repo's actual model adapters, model selection configuration, Ollama manifests, Qwen staging contracts, CI, and test fixtures; do not assume nonexistent paths.
2. Read installed model inventory from each authorized host only. Record hash, local path, architecture, tokenizer, context, runtime, quantization, size, RAM/disk, licensing, source commit, and test status. Mark inaccessible USB as BLOCKED.
3. Establish typed model registry from the accompanying JSON candidate list. Record discovery != approval != installed != verified.
4. Freeze runtime boundary: model outputs → schema validation → deterministic tools → evidence qualification → human review; no model output may authorize payments, invoice approval, or security actions.

## Wave 1: shortlist and security/license review
Candidates: Qwen3.5-0.8B, Falcon-H1-1.5B-Instruct, Granite-4.0-Micro, Ministral-3-3B-Reasoning-2512-GGUF; PaddleOCR-VL and DeepSeek-OCR-2 for document extraction; EXAONE-4.0-1.2B restricted research only. Check each official model card and immutable revision immediately before use. Confirm commercial terms; noncommercial licenses are not eligible for commercial pilots without explicit clearance. Distinguish model weights from third-party quantizations and from host execution capabilities.

## Wave 2: reproducible offline benchmark harness
Synthetic/permissioned cases only. Test baseline vs candidate on: general QA, abstention on unknowns, tool-call schema compliance, prompt-injection resistance, tenant leakage, evidence citation fidelity, deterministic financial arithmetic (tool only), document extraction precision, hallucination, latency, CPU RAM, disk, energy/thermal, and startup. Record versions, seed, exact commands, SHA256 of fixtures and weights, outcomes PASS/FAIL/SKIP/BLOCKED/NOT_VERIFIED. Separate quality from safety. Independent verifier must re-run key cases. No fabricated scores.

## Wave 3: low-cost upgrade strategies
A. Retrieval first: indexed approved documents with immutable references and explicit source timestamps. No direct prompt trust from retrieved documents.
B. Tool integration: Decimal-based reconciler and typed OCR evidence adapters; model does not perform authoritative arithmetic.
C. Quantization: benchmark candidate GGUF and supported Ollama formats with resource ceilings; compare quality loss.
D. LoRA/QLoRA only after baseline passes: small curated, de-identified synthetic training/eval splits; base-model architecture and revision must match adapter; keep eval holdout untouched. Never assume a Qwen3 adapter works with Qwen3.5.
E. Distillation only if licensing permits, data provenance is clean, and independently evaluated.

## Wave 4: controlled staging integration
Keep production model unchanged. Expose an owner-only staging model selector through server-side auth with explicit feature flags and rollback. Verify model identity from runtime and independent host observation; test no external paid fallback; prove fail-closed when unavailable. Ensure UI differentiates scripted fixture, local inference, private staging, and verified production (last category remains HOLD).

## Wave 5: release decision
Gate on pinned artifact hashes, license clearance, dependency/remote-code audit, privacy/tenant tests, financial regression, exact deployment SHA, rollback, independent witness, and human approval. If any unknown, mark HOLD. Never automatically switch models.

## Required artifacts
- docs/operations/CCLXIV_MODEL_CANDIDATES.json (discovery inventory; not approval)
- docs/operations/CCLXIV_INSTALLED_MODEL_INVENTORY.json (future runtime-produced)
- docs/operations/CCLXIV_LICENSE_AND_SECURITY_REVIEW.json
- docs/operations/CCLXIV_EVAL_PLAN.md
- docs/operations/CCLXIV_BENCHMARK_RESULTS.json
- docs/operations/CCLXIV_RELEASE_DECISION.json
- RECOVERY.json and RESUME.md savepoints per implementation wave

## Suggested first tests
1. Registry schema rejects absent model ID, source URL, or license status.
2. Unreviewed models cannot be selected for staging.
3. Any unknown or mismatched model hash prevents inference.
4. Offline fixture runs without network access.
5. OCR cannot invent provenance or promote an uncertain extraction to a financial finding.
6. Golden ledger remains unchanged across all model upgrades.
7. Browser never receives runtime secrets.
8. Missing Qwen service produces NOT_VERIFIED, not a fake answer.

## Acceptance
Foundation complete when source contracts and registry exist in Git, and implementation begins only in a separate reviewable branch after contract freeze. This document alone is not implementation, a verified model download, or production approval.
