# CCLII financial reconciliation report

Tested code `aa9ab47238324b25932767c8e0d20894d780b8d5`. Recorded 2026-11-06 1:03 PM CT.

The 36-month fixture still identifies `$385.00`, withholds `$150.00`, and confirms `$0.00`. Its event label is `NO_RELATIONSHIP_EVIDENCE`. The `$100` unbilled job and `$40` orphan invoice are not joined, because the amounts differ and the invoice has no job id. The `$10.00` synthetic invoice discrepancy is unchanged, and confirmed invoice recovery stays `$0.00`.

## What changed

- Several unresolved unbilled jobs and orphan invoices are withheld from the identified total and disclosed as `WITHHELD_AMBIGUOUS`. They are not paired by equal amounts.
- One equal-dollar pair is still withheld, including hourly equipment and labor findings, and including a matched invoice beside the pair.
- A different customer id, compared without regard to letter case, still keeps both amounts.
- A blank customer id does not prove the records are distinct.
- A job id that differs only by letter case is withheld. The finding text does not say there is no shared reference.

## Still open

- An unbilled job and an orphan payment are outside this rule.
- Customer ids that differ by punctuation, a suffix, or a lookalike character are still treated as distinct. Fuzzy matching would risk merging different customers.
- A one-to-one pair with different amounts and no shared job id stays in the identified total. That is required to keep the golden fixture.
- No path in this engine proves two records are the same event from equal dollars alone.
