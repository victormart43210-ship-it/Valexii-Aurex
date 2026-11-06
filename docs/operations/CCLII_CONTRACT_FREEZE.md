# CCLII contract freeze

Operation KUSANAGI CCLII. Recorded 2026-11-06 1:03 PM CT.

Repository `victormart43210-ship-it/Valexii-Aurex`. Branch `cursor/kusanagi-ccxlvi-sovereign-ascendancy-4082`. Pull request 180 stays draft. Base `cursor/kusanagi-ccxli-aurex-ascendancy-4082`.

Starting head `3880be625bf8a36aee64892772b07737c5561a21`. That head has six successful GitHub workflow runs (two of them are named CI). The handoff said five. Tested code for this operation is `aa9ab47238324b25932767c8e0d20894d780b8d5`. `origin/main` is `34cda4bd8f207f5b1284093b87e4760d782a4903`. This stack is not rebased onto main.

## Frozen dollars

Identified `$385.00`, withheld `$150.00`, confirmed `$0.00`. Invoice discrepancy `$10.00`, confirmed invoice recovery `$0.00`. These are synthetic.

## Event rule

- No unbilled job, or no orphan invoice: `NOT_APPLICABLE`.
- Every orphan invoice has a customer id, every unbilled job has a customer id, and none of the orphan ids match an unbilled job after case-folding: `PROVEN_DISTINCT`. Dollars stay.
- A blank customer id is not proof of a distinct event.
- One unresolved pair with different amounts and no shared job id, even ignoring letter case: `NO_RELATIONSHIP_EVIDENCE`. Dollars stay. This is the golden `$100` job and `$40` invoice.
- One unresolved pair with equal amounts, or with job ids that match after case-folding: `WITHHELD_AMBIGUOUS`. Dollars leave the identified total.
- More than one unresolved record on either side: `WITHHELD_AMBIGUOUS`. They are not paired.
- Equal amounts alone are not proof of the same event.

## Evidence and privacy

- `EXTERNAL_ANCHOR` is `NOT_VERIFIED`. The checkpoint uses a second server key. The same user who can edit the files and both keys can still rewrite them.
- Received ingest bytes are `VERIFIED_RECEIVED_BYTES` with `source_identity` `UNVERIFIED`. The historical dossier is `SOURCE_BYTES_UNVERIFIED`.
- Deletion requests do not delete. Retention requests are not enforced.
- `connector_destination_allowed` is an application check. It is not a host or Railway firewall.
- AES-GCM covers the report blob only when a 32-byte server key is configured. It is not zero-knowledge.

Production HOLD. Financial authority NONE. Customer data NOT AUTHORIZED. Third-party contact NONE. Merge authority NONE.
