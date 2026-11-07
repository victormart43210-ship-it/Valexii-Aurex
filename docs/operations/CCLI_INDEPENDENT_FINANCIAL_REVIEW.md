# CCLI independent financial review

Reviewer: [Independent financial review](bc-409de4ae-11b5-5f92-90f5-541c3c16d874). Model class Opus. Checkout `/tmp/ccli-review`, detached at `6cf405f300cbeea20eea6e03b7c05e749c1c5b44`. The reviewer did not edit the tree. The review ran on the same machine and the same agent platform as the implementer.

**INDEPENDENT ASSURANCE: OPEN.** Verdict on the reviewed code: **NO-GO** for merge, production, and customer data.

## What the reviewer reproduced

The reviewer ran the golden, convergence, sovereignty, historical, security, document, ingest, and adapter tests in that checkout with a fresh temp directory and without the implementer's pytest cache. The reviewer also ran probes from `/tmp`, outside the repo.

Golden totals on `6cf405f`: identified `$385.00`, withheld `$150.00`, confirmed `$0.00`. The `$10.00` invoice discrepancy remains on the synthetic document path, with confirmed invoice recovery `$0.00`.

## Closed in this operation

- One unbilled job and one orphan invoice of the same amount are withheld, including when another matched invoice is present, and including hourly equipment and labor findings.
- Customer ids that differ only by letter case are not treated as proof of distinct events.
- A sealed receipt that loses its MAC but keeps `SEALED_V2` fails `verify_receipt`.
- Deleting monitor rows in SQL, while the sidecar still names the old head, fails the chain.
- A count-zero sidecar entry with a forged MAC fails the chain.
- JSON that declares a dataset type other than `SYNTHETIC_ONLY` is refused.
- `WebsiteAdapter.create_job` no longer posts invoice keys, JSON blobs, or other values outside a short token. ISO timestamps that use `+00:00` are kept.

## Left open

- Several unbilled jobs and several orphan invoices are labeled `NOT_PROVEN` and are not all withheld. Pairing them would invent a join. Withholding every unequal pair would move the frozen golden `$100` and `$40`.
- An orphan payment is outside that rule.
- A customer id that differs by punctuation or a lookalike character is still treated as distinct. That is weak proof, and fuzzy matching would risk merging different customers.
- Stripping `receipt_class` and recomputing the hash yields authenticity `NONE`. Store reads still require a MAC.
- Deleting the monitor rows and the sidecar entry together looks like a tenant that never wrote an event. The same user who holds the receipt key can rewrite the database, the sidecar, and the key. Restoring an older pair of files is not visible. This is not an outside witness.
- Age-based purge can leave a chain that fails closed, with no separate re-anchor.
- Unlabeled uploads are still stamped `SYNTHETIC_ONLY`. That stamp is not a verification of the bytes.
- `source_sha256` on the historical dossier is the digest of normalized rows. `byte_length_verified` stays false.
- `reviewer_id` is an unauthenticated token. `human_approval: true` only removes a dry-run blocker. Execution stays `DRY_RUN_ONLY` and state stays `HOLD`.
- The adapter can still POST to whatever base URL the process was given. Short tokens can still carry encoded text such as `I1:385.00+C1`. `egress.py` is not on that path and is not a firewall.

The reviewer found no new financial double-count on the one-to-one equal-dollar case after `c4f6088`. The later commits did not change those totals.
