# CCLII independent assurance

Reviewer: [Independent CCLII assurance](bc-e9b27565-bdc2-5023-830e-691bc4f6bc32). Checkout `/tmp/cclii-review`, detached, last confirmed at `aa9ab47238324b25932767c8e0d20894d780b8d5`. The reviewer did not edit the tree and did not use the implementer's pytest cache.

The review ran on the same machine and the same agent platform as the implementer.

**INDEPENDENT HUMAN ASSURANCE: OPEN.**

Verdict on the reviewed code: **NO-GO** for merge, production, and customer data.

## Closed in this operation

- Golden totals stay `$385.00` / `$150.00` / `$0.00`, labeled `NO_RELATIONSHIP_EVIDENCE`.
- Multi-row unresolved unbilled jobs and orphan invoices are withheld, not paired.
- A case-variant job id is withheld. A blank customer id is not treated as proof of a distinct event.
- The anchor key cannot be the receipt key. A revoked active key does not insert a new row. Replaying an older source does not rewind the checkpoint.
- Deleting rows while the anchor file remains fails verification.
- Document responses include `source_bytes_status` and `source_identity`.
- An empty data-key object is `NOT_CONFIGURED`. With a real key, the report blob is AES-GCM.
- A deletion request does not delete. A filled authorization claim stays `UNVERIFIED` with effect `NONE`.
- An unlisted connector host is refused, including after `base_url` is changed on the object.

## Residuals the reviewer left open

- Deleting the rows, the sidecar, and the anchor together still verifies. Restoring an older copy of all three still verifies.
- The same user who holds both keys can rewrite the chain.
- `EXTERNAL_ANCHOR` stays `NOT_VERIFIED`.
- Finding columns and monitor payloads stay plaintext.
- Egress is an application check, not a host or Railway firewall.
- The monitor-head sidecar can still lose updates across processes.
- An age-based purge can leave the chain permanently unverified.
- Lookalike customer ids are still treated as distinct.
- An orphan payment is outside the unbilled/orphan rule.

Those residuals are not informational. They are why the release stays NO-GO.
