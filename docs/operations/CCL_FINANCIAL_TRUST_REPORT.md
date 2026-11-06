# CCL financial trust report

Tested code: `4d9beb1c4b0156799de88b31aff6f6eb2c0b46e8`.

Repository: `victormart43210-ship-it/Valexii-Aurex`.

Branch: `cursor/kusanagi-ccxlvi-sovereign-ascendancy-4082`.

Golden synthetic result on this SHA: identified `385.00`, withheld `150.00`, confirmed `0.00`. The `110.00` invoice against a `100.00` rate remains `10.00` identified and `0.00` confirmed. `pytest -q` was 709 passed, 1 skipped, exit 0. The skip is `training/tests/test_lora_smoke.py` because torch is absent.

## Closed or narrowed on this code

| Item | State |
|---|---|
| Caller clock as freshness | Expiry uses `datetime.now(UTC)`. A caller clock more than two minutes away is refused. |
| Caller-supplied verification field | `grantor_verified` or `authority_verification` on the authorization is refused. The dossier still hardcodes `authority_verification: UNVERIFIED`. |
| Reviewer token | Required, and recorded as `TOKEN_NOT_SIGNATURE`. It is not a signature. |
| Action and scope | The action must match the purpose. The scope must be `tenant` plus a token suffix. |
| Receipt downgrade | `receipt_authenticity` returns `NONE` when a sealed receipt is stripped and rehashed. `verify_receipt` can still return true for that integrity hash. Stored reads require `MAC`. |
| Monitor chain | New events carry an HMAC under the server receipt key. A rehashed payload with the old MAC fails verification. The key is symmetric and the chain head is not anchored outside the database. |
| Received document bytes | Ingest records `byte_length` of the bytes it received and labels the scope `RECEIVED_REQUEST_BYTES`. It does not accept a caller-declared length. |
| Promotion and training | `promotion_decision` does not become eligible from a `HUMAN` string. `training_reuse` stays refused. |

## Still open

- `grantor_kind: HUMAN` is still a string. There is no identity provider and no human signature.
- `SYNTHETIC_ONLY` is still a caller label. Real-looking rows with that label are still audited. The dossier says the classification is unverified.
- The historical path hashes normalized rows. It does not read source files.
- One unbilled job and one orphan invoice are withheld only when that invoice is the only invoice. A larger snapshot is not joined, so both findings can still carry dollars. The golden ledger depends on that restraint.
- Deleting the tail of the monitor chain inside the same database is not detected by an outside anchor.
- An age-based purge can remove the oldest monitor events and leave `verify_monitor_chain` false. That fails closed.
