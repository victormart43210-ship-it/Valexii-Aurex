# CCLII enterprise demo readiness

Tested code `aa9ab47238324b25932767c8e0d20894d780b8d5`. Recorded 2026-11-06 1:03 PM CT.

The public console was not rebuilt. Chrome headless loaded `http://127.0.0.1:5173/dispater` and the first paint contained "Synthetic demonstration. These dollars are not customer savings or recovered revenue.", "You decide", "does not contact", and "Unbilled tow ticket". A screenshot is at `/opt/cursor/artifacts/cclii-dispater.png`. The relationship label is rendered when a report is loaded. It is not on the idle screen.

## What the customer sees

| Item | Where |
|---|---|
| NOW, CHANGED, NEXT, WHY, PROOF | Each finding card |
| Affected record | Finding code and subject |
| Evidence | Proof line and receipt SHA-256 |
| Identified vs withheld | Identified exposure, withheld amount, and `event_separation` |
| Confirmed recovery | `$0.00` |
| Next human review | NEXT text. XAELI cannot approve recovery. |
| Decision authority | "you decide the next action · no vendor is contacted" |
| Synthetic label | The banner above the console |

`NO_RELATIONSHIP_EVIDENCE` and `WITHHELD_AMBIGUOUS` are visible on a loaded report. A withheld amount is not labeled as recovered revenue. A planted fixture is labeled "Planted differences", not as proof of production accuracy.

## 36-month demonstration

The frozen fixture remains the industrial history: identified `$385.00`, withheld `$150.00`, confirmed `$0.00`. It includes a rate discrepancy, an unbilled job, an orphan invoice, duplicate-invoice withholding, and no automated contact or payment. The `$100` job and `$40` invoice stay separate because there is no shared reference. That label has to be read as "not joined", not as "confirmed savings".

DISPATER's value in this demo is a repeatable reconciliation with a receipt, a withheld bucket, and a customer decision. This session did not compare it with ChatGPT or another product.

Customer-hosted deployment and private inference remain offerings. They were not verified here. XAELI staging is NOT_VERIFIED: flags off, base URL unset, and `127.0.0.1:8080` refused a connection.
