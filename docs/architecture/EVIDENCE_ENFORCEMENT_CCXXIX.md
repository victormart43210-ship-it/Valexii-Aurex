# Evidence Enforcement (CCXXIX)

Status: implemented and tested synthetically; **independent human review and live/staging verification NOT done**. Production HOLD, financial authority NONE.

## What is now enforced (code + tests)

| Control | Where | Test |
|---|---|---|
| Receipt v2: `run_id`, `created_at`, `tenant_id` inside the HMAC body; version marker (`receipt_auth.v=2`) is signed so v2 cannot be downgraded | `dispater_receipt.sign_report_v2`, `dispater_store.save_run/_verified` | `tests/test_dispater_receipt_v2.py` |
| Legacy (v1) receipts keep verifying under their original contract; their `run_id`/`created_at` are returned flagged `unauthenticated_fields` | `dispater_store._verified` | same |
| Row/receipt substitution (cross-run, cross-tenant, edited timestamp) fails closed | `_verified` | same |
| Key rotation and retired/missing keys fail closed | `dispater_receipt` | same |
| Recovery claims persisted as one MAC-signed document; unsigned columns are identifiers cross-checked on read | `aurex/dispater_claims.py` | `tests/test_dispater_claims.py` |
| One claim per (tenant, finding): no double counting of an obligation | UNIQUE index + idempotent create | claims tests |
| VERIFIED_DISCREPANCY needs ≥2 independent roots and CURRENT evidence; reviewer = authenticated principal (never client-supplied) | kernel + `advance_claim` | claims tests |
| CONFIRMED_RECOVERED needs payment evidence that is new, root-disjoint from all prior claim evidence, dated after submission, ≤ claim amount, and not already applied to another claim | `advance_claim` | claims tests |
| Conflicting evidence is refused (409) and preserved in a bounded per-tenant quarantine (original claim untouched) | `_quarantine` | claims tests |
| Concurrency: advances serialized by `BEGIN IMMEDIATE`; replays fail | `advance_claim` | concurrent test |
| Frontend export keeps `receipt_auth`/`receipt_mac`/`created_at`/`unauthenticated_fields`; UI states the trust level instead of "Cryptographically Sealed" | `website/src/lib/dispater-contract.ts`, console | `dispater-contract.test.ts` |

API: `POST /v1/dispater/claims`, `GET /claims`, `GET /claims/{id}`, `POST /claims/{id}/advance`, `GET /quarantine`. There is no actor or reviewer field in the request; models have no route to advance a claim.

## Receipt nonce / replay policy
No nonce. Replaying an identical submission is idempotent by dataset hash (returns the existing run). Replaying a claim transition fails (state already advanced). A receipt moved to another run/tenant fails v2 identity checks. Legacy receipts cannot prove identity or time.

## Known limitations (honest)
1. **Independence is client-asserted.** `source_system`, `source_record_id`, `derived_from`, `event_time` and `content_sha256` come from the caller; the server cannot verify a "bank-feed" record is a real bank record. A dishonest authorised reviewer can fabricate independent-looking evidence. Mitigations: authenticated reviewer identity recorded in signed history, quarantine, one-payment-one-claim, date bounds. Needed next: server-side attestation or allow-listed ingestion connectors, and hash verification against stored source documents.
2. A payment is deduplicated by `(source_system, source_record_id)`; re-labelling the same cash under a different id is not detected.
3. Partial recovery may reach CONFIRMED_RECOVERED with the exact amount recorded; policy owner should decide if partial recoveries need their own state.
4. Symmetric HMAC: no source authenticity or legal admissibility; key holders can forge.
5. Not wired: reconciliation engine output does not yet gate on kernel challenges; XAELI explanations and dashboard claim views are unchanged (no claims UI). Lifecycle fencing not added because no durable async job queue exists.
6. Jules "Global Ascension III": no branch or PR was found on the remote at the time of work; no overlap resolution was possible.
