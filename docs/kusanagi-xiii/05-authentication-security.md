# Authentication and verification boundary

Backend bearer comparison uses `hmac.compare_digest`; service/admin configuration requires >=32 characters. Invalid/missing authentication is rejected in tests. Repair compares encoded bytes safely and authenticates health. Shared bearer identifies one service principal; it is not a multi-user authorization system. User token lifecycle/revocation and operational provisioning remain NOT VERIFIED.

Website source uses Supabase claim validation and an owner-ID server-side check. A signed-out visit to `/admin/aurex-control` displayed Access denied on 2026-10-14. This UI observation does not prove all direct server-function authorization cases. Non-owner, revoked session, cookie/CSRF behavior and session lifecycle need authenticated staging tests. No secrets were read or placed into bundles.

Ed25519 baseline verified a key supplied in the same attestation: an attacker could generate a new key and self-certify. Repair requires an operator-supplied verifier-to-key map, default HOLD, exact identity bindings, a signed timestamp and a five-minute freshness window. Removing/replacing a pin denies the old key in tests. Existing signatures must be regenerated because timestamp now participates in the digest. Operational key storage, rotation distribution, replay-use policy, independent signer custody and protocol version migration remain required before release.

SQLite repair serializes state changes with BEGIN IMMEDIATE and validates transitions. It does not repair all database concerns: idempotency lacks a unique constraint/concurrent reservation protocol; evidence insertion permits replacement; default DB path is /tmp; job ownership and retention/pagination remain absent. Job dispatch remains disabled to prevent false execution claims.

Paid job creation remains rejected and API budget remains zero. Direct external adapters do not call BudgetGuard; zero API budget must not be represented as a universal provider-spend enforcement guarantee. No paid inference was run.
