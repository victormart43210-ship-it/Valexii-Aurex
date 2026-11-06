# CCLI evidence and authority report

Tested code `6cf405f300cbeea20eea6e03b7c05e749c1c5b44`. Recorded 2026-11-06 11:27 AM CT.

## Human authorization

`aurex/ascendancy/historical_audit.py` refuses a caller field named `grantor_verified` or `authority_verification`. The dossier hardcodes `authority_verification: UNVERIFIED` and `reviewer_binding: TOKEN_NOT_SIGNATURE`. A reviewer id is required and cannot be the role words human, model, system, or agent, but it is still a string. There is no identity provider and no human signature. Variants of the refused field name are ignored; they do not become verified.

`aurex/customer_sovereignty.py` treats `grantor_kind: HUMAN` and `approved: true` as `FORGED_OR_UNVERIFIED_APPROVAL`. No collection, dispute, payment, or contact is started.

## Source provenance

| Layer | What this tree does |
|---|---|
| Caller-declared metadata | A declared byte length on `POST /v1/dispater/documents` is accepted only when it equals the received bytes. A mismatch is HTTP 400. |
| Canonical admitted rows | Reconciliation hashes the normalized rows. |
| Actual source-file bytes | The document API records `byte_length` of the received request and `byte_length_scope: RECEIVED_REQUEST_BYTES`. The historical gate does not read a source file. |
| Verified source digest | Not claimed. `byte_length_verified` stays false. Scope on the historical path remains `NORMALIZED_ROWS_NOT_SOURCE_FILE`. |
| Independently authenticated source identity | Not implemented. |

JSON that declares `dataset_type` other than `SYNTHETIC_ONLY`, including a different letter case, is refused. CSV and unlabeled JSON are still labeled synthetic. That label is not a check of the contents. THE BIG ONE was not mounted or read.

## Receipts

`seal_run` sets `receipt_class` to `SEALED_V2` before the content digest and the HMAC. `verify_receipt` requires the MAC when the class, the auth object, the MAC, or binding `BOUND_V2` is present. Store reads require the MAC as well.

Removing the class and recomputing the hash is still an unsealed integrity check. The hash is not promoted to a signature.

## Monitoring chain

Each event carries an HMAC over the chain body, using the server receipt key. The key is symmetric.

`db_path + ".monitor-head.json"` stores, per tenant, the head, the count, and a MAC of that record. `verify_monitor_chain` fails when the sidecar disagrees with the rows, including a forged count of zero. `purge_tenant` rewrites the sidecar inside the same maintenance action.

Limitations, which keep release on HOLD:

- The sidecar is on the same machine and uses the same receipt key. It is not an external anchor and not a paid service.
- Deleting the rows and the sidecar file together is not distinguishable from a tenant that never recorded an event.
- The sidecar write is outside the SQLite transaction. Two processes can race. That race was identified by reading the code and was not reproduced.
- An age-based purge that breaks `prev_sha256` still fails closed. There is no second anchor that can rebuild trust after that purge.

No production dependency was added.
