# CCLII evidence anchor report

Tested code `aa9ab47238324b25932767c8e0d20894d780b8d5`. Recorded 2026-11-06 1:03 PM CT.

## EXTERNAL ANCHOR: NOT VERIFIED

The monitor checkpoint is a local JSON file beside the SQLite database, MAC'd with `AUREX_DISPATER_ANCHOR_KEYS`. That key must not be the receipt key. A revoked active key id is refused before a new row is inserted. Replaying an older source does not move the checkpoint backward.

Trust boundary: the database and the checkpoint are both files the server process can write. Authentication is HMAC-SHA256, not a signature and not an outside witness. Freshness is the head hash plus the event count. A first tenant has no checkpoint and no rows. Rows with no checkpoint fail. A checkpoint with no rows fails. Deleting the rows, the sidecar, and the checkpoint together looks like a tenant that never wrote. Restoring an older copy of all three also verifies. The same operating-system user who holds both keys can rewrite the chain. Anchor loss fails closed for later reads. Key rotation keeps old keys for verification and uses the active id for new notes. A kid listed in `AUREX_DISPATER_ANCHOR_REVOKED_KIDS` does not verify.

The anchor file uses a per-process temporary name and a lock on one host. The monitor-head sidecar does not have that lock. A lock does not hold across hosts. Age-based purge can still leave a chain that fails closed.

## Source authenticity

| Layer | Status |
|---|---|
| Caller-supplied metadata | A declared length is accepted only when it matches the received bytes. |
| Received original bytes | Ingest records SHA-256 and length of the received bytes. Status `VERIFIED_RECEIVED_BYTES`. The document response includes that status. |
| Parsed rows | Reconciliation uses the normalized rows. |
| Calculated source digest | The historical dossier hash is the normalized rows. It is not the original file. |
| Authenticated source identity | `UNVERIFIED`. |
| Independent source verification | Not implemented. Historical status `SOURCE_BYTES_UNVERIFIED`. `byte_length_verified` stays false. |

## Human authorization

`authorization_decision` returns `verification: UNVERIFIED` and `effect: NONE` even when actor, action, scope, expiry, and tenant are present. The reason is `NO_IDENTITY_PROVIDER`. Missing fields use `MISSING_AUTHORIZATION_FIELDS`. No financial action is executed.
