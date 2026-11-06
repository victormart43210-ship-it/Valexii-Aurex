# CCXXIV Independent Review — PR #162 (status: PARTIAL, production HOLD)

Tested base: `e5115a613d0e7a28beda2266b47761db0b863428` (CI green, 5 workflows). Patch is stacked on the #162 branch; it is not a competing candidate.

## Coordination
Issue #152 had no comments; no Jules CCXXIII work is published. #159 advanced to `08cf6b4` (touches `api.py`, `dispater_api.py`, docs). This patch touches `dispater_store.py`, `dispater_intelligence.py`, new `dispater_receipt.py`, and tests — no overlap. Only shared file: `COPILOT_CHATGPT_HANDOFF.json` (Copilot-owned).

## Findings
1. **HIGH — receipts forgeable (fixed).** `receipt_sha256` is unkeyed; a DB writer could edit a report and recompute it. Added HMAC-SHA256 `receipt_mac` + `receipt_auth{alg,kid}` over canonical JSON (covers tenant, amounts, evidence digests). Verified on every read; signing/verification fail closed without keys. Rotation via multi-key map + active kid. Unsigned legacy rows are rejected, including on idempotent resubmit.
2. **MEDIUM — duplicate-charge exposure depended on input row order (fixed).** Same data gave $60 or $100. Invoices now sorted by `invoice_id`. Owner must confirm intended semantic (sum of non-primary invoices vs. total minus contract rate).
3. **LOW — masked error (fixed).** `ROLLBACK` after `COMMIT` raised `OperationalError`, hiding `IntegrityError`.

## Security properties (distinct)
| Property | State |
|---|---|
| Request authentication | Bearer-token grants (existing); not changed |
| Replay prevention | No durable nonce. Idempotent on (tenant, dataset hash): replay is harmless (tested). Nonce NOT implemented |
| Receipt authenticity | HMAC, local-tested. Symmetric: a key holder can forge; no asymmetric signing or external anchor |
| Evidence truth | Not established by any of the above |
| RFC 8785 | Not conformant (sorted compact JSON) |
Recommendation for stronger audit: Ed25519 signatures with an offline/verifier public key and periodic externally anchored hash-chain checkpoints.

## Storage
Existing tests cover ephemeral/symlink rejection, WAL+FULL, replaced file, concurrency, corruption, backup/restore. Added SIGKILL mid-write recovery. **BLOCKED:** real Railway volume — no staging access; needs owner-provided volume mount (expected `/data`, `AUREX_DISPATER_DB=/data/...`, `AUREX_DISPATER_REQUIRE_PERSISTENT=1`) and the two receipt key vars as Railway secrets.

## Financial oracle
Externally researched 0; implemented 41 (new 40 seeded multi-job + 1 order test) + 25 prior single-job; passing all; failing 0. Not modelled by engine (BLOCKED/out of scope): rate changes, amendments, equipment hours/units, currency, stale sources, credit reversals. Exposure ≠ confirmed loss ≠ recovered money: `confirmed_recovery_usd` stays `0.00`.

## Verification (local, clean venv)
pytest 591 passed/1 skipped; ruff pass; mypy strict `aurex aurex_foundation` pass; `dispater-web` npm test 25/25, build OK. Not run: `website/` tests, browser E2E, live XAELI–Qwen, staging, 108-run battery.

## Release gate
EXPERIMENTAL. Missing: staging, 108-run battery, shadow/canary, SLO, owner authorization, independent CI on patch commit. Production **HOLD**; financial authority NONE.

## Rollback
Revert the patch commit; unset receipt env vars; purge the DISPATER DB (signed reports are incompatible with the old hash check).
