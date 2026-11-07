# AUREX Evidence Integrity Kernel

`aurex/evidence_kernel.py`: pure, dependency-free, no I/O or model calls. Tests: `tests/test_evidence_kernel.py`.

Chain preserved: Evidence → Qualification → Reality → Authority → Effect.

- **Roots:** corroboration counts disjoint evidence *roots*, not records (PDF → OCR → DB row = one root).
- **Freshness:** CURRENT / STALE / UNKNOWN / UNAVAILABLE / DEGRADED / CONFLICTED; only CURRENT can support a claim.
- **Claims:** DETECTED → SUSPECTED → CORROBORATED → VERIFIED (+ DISPUTED, REJECTED). Models cannot corroborate/verify; VERIFIED needs a named human, ≥2 independent roots, CURRENT evidence.
- **Capabilities:** deny by default; `EXECUTE_FINANCIAL` is never granted to anyone; models cannot export or propose adjustments.
- **Outcomes:** DETECTED_EXPOSURE → VERIFIED_DISCREPANCY → SUBMITTED → APPROVED → CONFIRMED_RECOVERED. No skipping; recovery needs intact payment evidence independent of the claim's own sources and cannot exceed the claim.

## Integration status
Wired: signed finding history (`dispater_store.finding_history`). **Not yet wired:** the engine, API endpoints, persistence of claims, XAELI and dashboard do not call the kernel yet. It is a tested foundation, not an enforced boundary.

## Limits
HMAC receipts are symmetric and prove neither source authenticity nor admissibility. Root identity depends on callers recording honest `source_system`/`source_record_id`/parents. API exports include unsigned `run_id`/`created_at`; remove them before `verify_mac` (design decision for owner: exclude them from the MAC or keep as is).
