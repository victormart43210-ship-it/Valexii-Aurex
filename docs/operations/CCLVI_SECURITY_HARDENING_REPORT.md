# CCLVI security hardening

Tested code `bd1c4d00559bed86d4e37aab103204cf95829769`. Production network settings were not changed.

## Closed in this review

- The website connector no longer treats an arbitrary loopback port as allowed. `http://127.0.0.1:6379` is refused unless the host is on `AUREX_EGRESS_ALLOWLIST`. Local inference still uses `destination_allowed`, which accepts loopback HTTP with an explicit port and rejects every other purpose. `transmit_financial_record` still raises `FINANCIAL_EGRESS_PROHIBITED`.
- The monitor sidecar write now uses an exclusive file lock on this host, plus a unique temporary name. The lock is not an outside witness. It does not cover a network filesystem.

## Checked and left as they were

- Tenant tokens: unknown token 401, wrong tenant 403, cross-tenant run 404, admin token is not a DISPATER grant.
- SQL access in the store is parameterized and filtered by tenant.
- CSV export keeps no-store headers. Formula injection remains a spreadsheet concern for exported text; the export is a report, not an executed sheet.
- Uploads reject a declared length that does not match received bytes. Path traversal is not given a filesystem root beyond the configured database path.
- Report encryption is optional AES-GCM of the report blob. Finding columns and monitor payloads stay plaintext. Empty key material is `NOT_CONFIGURED`.
- Prompt-injection tests in the existing suite still pass. No new model tool was enabled.
- Secrets were not printed. Receipt and anchor keys come from the test fixture, not from a committed file.

## Open

- Application allowlists are not a container, host, or Railway firewall. DNS rebinding, redirects, and IPv4/IPv6 edge cases are not a production control. Railway egress is NOT_VERIFIED.
- Coordinated deletion of rows, sidecar, and anchor still verifies. Revoked-key reuse is refused before insert for the anchor. Historical chain rewriting by a holder of both keys is still possible.
- A deletion request is recorded and does not delete. Retention is not enforced. Backup deletion and legal hold are `NOT_IMPLEMENTED`.
- Source identity stays `UNVERIFIED`. Received-byte verification is not source-file verification.
- `fcntl` is POSIX-only. This tree's CI runs on Linux.
- Dependency review and a human secret-scan triage were not completed. Copilot's CCLV note says detect-secrets hits were untriaged. This review did not treat those hits as cleared.
