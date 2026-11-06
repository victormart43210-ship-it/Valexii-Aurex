# CCLVII financial hardening

The existing engine remains canonical. No second financial engine or service was introduced.

## Repairs

- Duplicate equipment identity and service date are checked before pricing unbilled hours. Two eight-hour tickets at $25/hour previously booked $400. The engine now returns `DUPLICATE_FIELD_TICKET`, `INSUFFICIENT_EVIDENCE`, zero identified exposure, and the job/rate/both-ticket digests. A single ticket still prices $200. Distinct equipment or service dates remain separate controls.
- The reconciliation HTTP request carries optional equipment and labor collections, each bounded to 2,000 rows. Omitted/null collections preserve the old dataset digest and replay identity.
- Existing JSON, CSV, PDF and XLSX parsers preserve supplied rate unit/supersession, payment direction/attribution, invoice customer, and labor overtime fields. Unknown fields stay excluded. Eight hours at $25 prices $200 through both API paths; a $100 payment less $40 reversal remains $60.

## Frozen financial contract

| Metric | Verified expected result |
|---|---:|
| Identified exposure | $385.00 |
| Withheld unresolved | $150.00 |
| Confirmed recovery | $0.00 |
| Synthetic invoice discrepancy | $10.00 |
| Confirmed invoice recovery | $0.00 |

Existing expectations were not edited. The full suite on `a8ee5cb7abb1454058f693dc8165ae6dbad58117` passed, including golden, historical, sovereignty and new boundary tests.

`NO_RELATIONSHIP_EVIDENCE`, `WITHHELD_AMBIGUOUS`, customer-decides authority and no-contact restrictions remain. Neither a receipt nor an AI explanation creates financial authority. Received-byte verification is not source authenticity or independent evidence. Conflicting job/customer references and repeated parser fields remain recorded follow-up defects.
