# CCXLVIII financial assurance

Recorded 2026-11-06 9:27 AM CT (`2026-11-06T15:27:40Z`).

Repository: `victormart43210-ship-it/Valexii-Aurex`.

Candidate: `cursor/kusanagi-ccxlvi-sovereign-ascendancy-4082` at `cf083f7f531207c1fe77fec6d127e53e52584123`.

Parent of the follow-up repair: `75d93fc8499aefc5f30a3751f69c127c0a25c574`.

Prior green head: `0f32769db5469d45e59434e34e803a95155b95fd`.

Production is HOLD. Financial authority is NONE. Confirmed recovery stays `0.00`.

## What was reproduced and repaired

The golden synthetic audit remains identified `385.00`, withheld `150.00`, confirmed `0.00`. The `110.00` invoice against a `100.00` rate remains identified `10.00` and confirmed `0.00`. No repair turns an unverified finding into confirmed recovery.

| Defect | Result on `cf083f7` |
|---|---|
| Caller-supplied `HUMAN` with no reviewer | Refused. A reviewer id is required and cannot be the authorization id, the tenant id, or a role word. `grantor_verified` stays false. A non-role string is still only a string. |
| Caller clock and expiry | Expiry is compared with the caller clock and the wall clock. A clock more than 48 hours from the wall clock is refused. A lifetime longer than 7 days is refused. |
| Caller-supplied `SYNTHETIC_ONLY` | The dossier sets `synthetic_label_verified` false. Legitimate synthetic audits still run. The label is not proof. |
| Declared byte length | A length that does not match the canonical admitted rows is refused, including `999999`. `byte_length_verified` stays false because source-file bytes are not accepted. `admitted_row_byte_length_matches` records the row check. |
| One unbilled job and one orphan invoice | Both findings remain. Both exposures become `0.00`. The amounts move to withheld. Larger ledgers are not joined. |
| Unkeyed hash treated as a signature | A report that carries `receipt_auth`, `receipt_mac`, or `receipt_binding=BOUND_V2` must pass `verify_mac`. A legacy report with only a hash remains an integrity check. |
| Paid `100.00` with `50.00` applied and `50.00` misapplied | Identified `50.00`, once, on the misapplied payment. The status gap is reduced by the excluded cash. |
| Two misapplied `100.00` payments on one invoice | Identified `0.00`, withheld `200.00`. |
| Lone `100.00` reversal on a paid `100.00` invoice | Identified is capped at the invoice, `100.00`, and the excess `100.00` is withheld. |
| Nested `recovered_usd` in an offline evaluation | The case fails. Confirmed recovery in the score stays `0.00`. |

## Review

[Independent financial review](bc-8d014e21-f195-52e8-a120-cc026e7cfd43) read `75d93fc` and then `cf083f7` on this same checkout and interpreter. It did not edit files. Its verdict is NO-GO for merging pull request 180 to `main`. It is not a separate runner.

Residuals it left open:

- An unbilled job and an orphan invoice in a ledger with more than one invoice are not treated as one event.
- `grantor_kind` is still the string `HUMAN`. There is no human signature.
- Rows labeled `SYNTHETIC_ONLY` are not proven synthetic.
- Source-file bytes are not read.
- Stripping `receipt_binding`, `run_id`, and `created_at` and recomputing the hash makes `verify_receipt` an integrity check again. Stored runs still require `verify_mac`.
- Prose such as "we recovered 50 USD" can still pass the offline scorer. The score's confirmed recovery stays `0.00`.
- The monitor chain is an unkeyed hash.
- The withheld total for two misapplied payments counts both amounts.

## Tests on this candidate

`pytest -q` on Python 3.12.3: 705 passed, 1 skipped, exit 0. The skip is `training/tests/test_lora_smoke.py` because `torch` is not installed. That skip is not a pass.

`ruff check .` exited 0. `mypy aurex` exited 0 on 104 files.

These counts belong to `cf083f7` only.
