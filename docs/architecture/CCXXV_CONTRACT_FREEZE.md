# CCXXV implementation plan and contract freeze

Owner directive: OPERATION KUSANAGI CCXXV, 2026-11-05. Production HOLD; financial authority NONE; synthetic only; no paid inference, merge or deployment.

## Decisions
Fresh-main branch from 99af5fd8a2c1340bcf5d2eda03bb6dbe65e5a661. Selectively restore runtime, tests and frontend from reviewed #163 snapshot 9395e71099a8dc9d4f1c63a558917c714febb5b6, then verify locally. This reconciles #159–#163 without merging branches. #164 is documentation reconnaissance. Prefer a Python module over a new service or Kotlin port; preserve existing SQLite store/HMAC receipts.

## Shared interface and ownership
- Lane A: recovery and transfer matrix documents only.
- Lane B: `aurex/evidence_integrity.py`, `tests/test_evidence_integrity.py`. Domain-neutral immutable evidence graph, all-parent root dedup, freshness, explicit qualification and fail-closed capability evaluation. No HTTP, DB or model calls. Agent publishes exact signatures before integration.
- Lane C/coordinator: `aurex/dispater_intelligence.py`, additive evidence integration; existing input contract retained; each snapshot is ONE unverified source root, not independent records. Original and normalized digests remain distinct. Unknown freshness remains UNKNOWN. No promotion to independently verified or actual recovery from supplied flags.
- Lane E: frontend contract + reconciliation console + tests only. Additive verification metadata; fail-closed older-report display; advisory XAELI only.
- Lane D: independent read-only review and adversarial testing after implementation; no implementation ownership.

## Implementation tasks
1. Recover historical source and reconcile candidate paths; run baseline pytest, Ruff, strict Mypy and frontend checks.
2. Test then implement immutable evidence DAG with missing/cyclic/foreign-domain/foreign-tenant rejection; transitive all-parent roots; duplicate content root collapse; timezone-aware expiry and future timestamp handling; distinct observation and claim states; no model or financial authority.
3. Adapt each financial finding to the shared kernel; include complete supporting rate evidence for unbilled amounts, preserve original bytes via snapshot digest and normalized row lineage; mark missing/conflicting evidence; deterministic advisory explanation.
4. Implement bounded synthetic recovery lifecycle evaluation with independent payment/deposit evidence, decimal-safe arithmetic and no automatic actions. No real recovery represented without trusted external verification; any prototype limitations explicit.
5. Display qualification/uncertainty/root count and source digests. Never infer VERIFIED from AUDIT_COMPLETE or a receipt hash.
6. Separate reviewer challenges lineage spoofing, stale/future clocks, duplicate/cross-tenant evidence, arithmetic, lifecycle and presentation. Fix verified defects; record deferred ones.
7. Run backend/frontend regression, static checks and builds; record actual commands/results; create draft PR against main and machine-readable handoff. No merge or deploy.

## Review focus
Untrusted root labels cannot establish independence; trusted ingest is not yet available. Cycles and missing parents must fail closed. Synthetic claims cannot become actual revenue. Stale evidence must not retain a strong current conclusion. Local tests do not prove deployment or commercial accuracy.

## Rollback
Close draft PR; main and deployed systems untouched. No DB migration.
