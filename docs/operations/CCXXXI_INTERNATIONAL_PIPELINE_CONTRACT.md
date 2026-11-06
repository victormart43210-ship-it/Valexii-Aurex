# CCXXXI — International open-source processing convergence contract

Status: **CANDIDATE / NOT IMPLEMENTED / PRODUCTION HOLD**
Base: canonical `main`. This document defines a proposed integration boundary, not evidence that any candidate upstream is installed.

## Verified mainline entry points
- `aurex/dispater_api.py`: authenticated tenant-bound DISPATER API, 5 MiB request-body guard.
- `aurex/dispater_intelligence.py`: deterministic Decimal-based reconciliation and candidate findings.
- `aurex/dispater_store.py`: tenant-scoped SQLite runs and receipt checks.
- `aurex/dispater_evidence.py`: **synthetic-only** evidence-readiness demonstration.
- `aurex/dispater_workflow.py`: **synthetic-only** workflow and retrieval demonstration.
- `aurex/evidence_kernel.py`: evidence graph and fail-closed independence checks.
- `docs/international-model-convergence-wave1.md`: international candidate list explicitly marked DESIGN ONLY.

## Country/project attribution register
| Region | Reported source | Repository-confirmed status | Action |
|---|---|---|---|
| Norway | Specific upstream not yet identified; earlier Helsinki/MinnaLearn-inspired work is **Finnish**, not Norwegian | NOT VERIFIED | Recover exact upstream URL, license, version, code SHA, and integration tests |
| Greece | FiNER / GovDoc / Elefthero-related concepts mentioned in prior discussion | NOT VERIFIED on main | Verify project identity and provenance before attribution |
| China | Qwen local development demonstrated; PaddleOCR, DeepSeek, MiniCPM, ms-swift are candidates in design document | MIXED: local test / DESIGN ONLY | Pin model digest and distinguish tested adapter from deployed model |
| Uzbekistan | Specific upstream not yet identified | NOT VERIFIED | Recover exact upstream URL, license, version, code SHA, and integration tests |

Never infer nationality from a project name, and never mark an upstream INSTALLED based only on a plan, documentation reference, or local test in a different checkout.

## Canonical per-document envelope (proposal v0)
Every admitted item must retain: `tenant_id` (server-authorized), `source_id`, `source_record_id`, `source_kind`, `content_sha256`, `ingested_at_utc`, `media_type`, `byte_count`, `original_artifact_ref`, `source_attestation_status`, `processing_state`, `schema_version`.
Each derived observation must additionally record: `parent_content_sha256`, `adapter_id`, `adapter_version`, `adapter_artifact_digest`, `operation`, `page_or_row_locator`, `raw_value`, `normalized_value`, `confidence_or_null`, `language`, `verification_state`, and `warnings`. Raw source and transformed content must remain distinct.

## Ordered gates
1. **Admission:** authorization from server principal; consent; MIME and size limits; malware/zip-bomb/path traversal defenses; preserve original bytes; tenant separation. Reject unknown/unauthorized.
2. **Classification:** select only needed adapters. PDF/image -> optional OCR/layout; structured CSV/JSON -> schema parser; language mismatch -> optional translation. Do **not** run every model on every file.
3. **Extraction:** page/row-level provenance, source-linked values, bounded worker resources, explicit errors. No fabricated defaults.
4. **Normalization:** schema-versioned deterministic field mapping; Decimal money; original value retained; currency/date/units checked; disagreements recorded, not silently reconciled.
5. **Evidence qualification:** validate origin, lineage, integrity, freshness, and independent roots. Client-asserted source IDs alone do not prove independence.
6. **Reconciliation:** use deterministic DISPATER engine only on admitted structured records; potential exposure is not recovered revenue.
7. **Challenge and authority:** independent verifier and human review; model agreement alone is not a witness. Unknown/stale/contradictory -> WITHHELD/HOLD.
8. **Presentation:** NOW -> CHANGED -> NEXT -> WHY -> PROOF with source locators and explicit qualification state; XAELI advisory only.

## Integration invariants
- No new parallel database, duplicate API authority, or independent financial ledger.
- Preserve PR #167 fail-closed behavior; evaluate PR #168 separately before merging.
- No paid inference, customer data, live financial actions, or production deployment.
- Network crawling disabled unless allowlisted, SSRF-protected, and approved.
- Each adapter must expose `INSTALLED | PROPOSED | LOCAL_ONLY | NOT_VERIFIED` with evidence links; failures must never be reported as success.
- Offline Chromebook and USB source trees are **not** assumed identical to canonical GitHub.

## Acceptance tests required before implementation can be admitted
- Same document twice -> stable content digest, idempotent handling.
- Tenant A cannot access or influence tenant B, including cached OCR/model outputs.
- Tampered source, fake source IDs, stale source, cycles, and missing parents -> fail closed.
- OCR/translations preserve raw source and page locators; adversarial multilingual negation tested.
- Invalid/malformed documents, oversized files, PDF bombs, CSV formulas, model timeout -> bounded failures.
- Financial arithmetic uses Decimal; no NaN/Infinity; no recovered-revenue claim without independently verified payment and human approval.
- Golden synthetic PDF/CSV/image corpus exercises every **installed** adapter and verifies canonical records -> reconciliation -> audit receipt -> dashboard.
- Exact branch SHA, adapter versions, dataset digests, pytest/Ruff/Mypy/frontend build/CI evidence recorded; unrun = NOT RUN.

## Implementation sequence
1. Inventory actual repository dependencies, import graph, worker entrypoints, and local-only artifacts.
2. Recover Norway/Greece/China/Uzbekistan upstream identities and licenses; publish a machine-readable admission registry.
3. Implement typed canonical envelopes and adapter registry with no new required dependencies; add negative tests.
4. Connect existing deterministic ingestion and reconciliation paths without changing their authority.
5. Wire dashboard evidence navigation and independent end-to-end golden corpus.
6. Request independent review; **do not merge or deploy without owner approval**.

**No runtime integration is claimed by this contract.**
