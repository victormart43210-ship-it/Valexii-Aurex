# CCL no-contact and no-action tests

Tested code: `4d9beb1c4b0156799de88b31aff6f6eb2c0b46e8`.

Repository: `victormart43210-ship-it/Valexii-Aurex`.

`aurex/customer_sovereignty.py` is the refusal point. It does not open a socket, send mail, or change a ledger.

`tests/test_customer_sovereignty.py` covers:

- A `HUMAN` approval aimed at a vendor. Result: `contacted` false, reason `FORGED_OR_UNVERIFIED_APPROVAL`.
- A model instruction that says to ignore policy and email a vendor. Result: `MODEL_INSTRUCTION_IS_NOT_AUTHORITY`.
- The same decision submitted again. Result: still not executed.
- A missing decision. Result: `DECISION_MISSING`.
- A collection instruction. Result: `records_modified` false.
- A training checkbox. Result: `allowed` false and `training_started` false.
- An admin bearer token reading a tenant run. Result: HTTP 401.
- `DELETE` of a run. Result: HTTP 405.
- JSON export. Result: `third_party_release` false, `receipt_authenticity` `MAC`, confirmed recovery `0.00`.

DISPATER reconciliation, document ingest, and export call `assert_no_effect()` before they read or write tenant data. The module constants `THIRD_PARTY_CONTACT` and `FINANCIAL_ACTION` are `NONE`.

This is a refusal inside the process. It is not an egress firewall, and it is not proof that some other program on a future host cannot send mail.
