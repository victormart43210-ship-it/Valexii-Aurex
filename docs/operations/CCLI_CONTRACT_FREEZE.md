# CCLI contract freeze

Operation KUSANAGI CCLI. Recorded 2026-11-06 11:27 AM CT.

Repository `victormart43210-ship-it/Valexii-Aurex`. Branch `cursor/kusanagi-ccxlvi-sovereign-ascendancy-4082`. Pull request 180 stays draft. Base branch `cursor/kusanagi-ccxli-aurex-ascendancy-4082`.

Starting head `cd0e571485045fd9d8357be71f586290fdf60e39`. Tested code `6cf405f300cbeea20eea6e03b7c05e749c1c5b44`. The docs commit that adds this file is not the tested code.

## Frozen results

The 36-month synthetic fixture stays at identified `$385.00`, withheld `$150.00`, confirmed recovery `$0.00`. The synthetic invoice discrepancy stays `$10.00` with confirmed invoice recovery `$0.00`. Those dollars are not customer revenue.

## Frozen authority

- Production HOLD. Financial authority NONE. Paid inference OFF. Training reuse NOT_AUTHORIZED. Customer data NOT_AUTHORIZED. Third-party contact NONE. Merge authority NONE.
- A `HUMAN` string, a reviewer id, or a caller field named `grantor_verified` is not a signature and not an identity-provider assertion. Authority stays `UNVERIFIED` unless a separate authenticated identity exists. None exists in this tree.
- `receipt_sha256` is an integrity hash. `receipt_mac` is an HMAC with the server receipt key. Neither is a digital signature.
- `receipt_class` `SEALED_V2` means the report was sealed with a MAC. Stripping the MAC while leaving that class fails verification. Stripping the class and recomputing the hash leaves an unsealed integrity hash (`receipt_authenticity` `NONE`).

## Frozen event rule

An unbilled job and an orphan invoice are not joined by guesswork.

- No unbilled job, or no orphan invoice: `NOT_APPLICABLE`.
- Every orphan invoice has a customer id, and none of those ids match an unbilled job after case-folding: `PROVEN_DISTINCT`. Both amounts stay.
- Exactly one unbilled job and exactly one orphan invoice, not proven distinct, with one unbilled finding (`UNBILLED_JOB`, `UNBILLED_EQUIPMENT`, or `UNBILLED_LABOR`) and one `ORPHAN_INVOICE` of the same positive amount: `WITHHELD_AMBIGUOUS`. Both amounts move to withheld.
- Every other unbilled-plus-orphan snapshot: `NOT_PROVEN`. Dollars stay in their own findings and the summary says the separation is not proven. The golden `$100` job and `$40` invoice are this case. Multiple rows are not paired.

## Frozen privacy

Tenant bearer grants isolate API reads. An admin token is not a DISPATER grant. Export stays `no-store` and is not a third-party release. DELETE of a run stays 405. `aurex/egress.py` refuses financial transmission inside the process. It is not a host firewall.

## Work assignment

The financial, store, ingest, and adapter files overlap, so this session edited them in one checkout and then reviewed `6cf405f` from the detached worktree `/tmp/ccli-review`. That worktree is the same machine. It is not an outside witness.
