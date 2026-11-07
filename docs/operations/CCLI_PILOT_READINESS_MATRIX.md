# CCLI pilot readiness matrix

Tested code `6cf405f300cbeea20eea6e03b7c05e749c1c5b44`. Recorded 2026-11-06 11:27 AM CT. The frontend was not rebuilt. Copy that overclaimed a result was corrected.

Rendered check: Chrome headless loaded `http://127.0.0.1:5173/dispater` from the local Vite server. The page contained "You decide", "does not contact", "Unbilled tow ticket", and "Planted differences". The empty-finding sentence is shown only after a clean report exists, so that sentence was confirmed in source and not in the first paint.

## What a customer can see

| Question | Where it is answered | Limit |
|---|---|---|
| NOW | Each finding's `xaeli_explanation.now` and the console finding card | Advisory text. Not a decision. |
| CHANGED | `xaeli_explanation.changed`, including the withheld-ambiguity sentence when that rule fires | |
| NEXT | `xaeli_explanation.next` | The next step is a human review, not an automatic contact. |
| WHY | Candidate language. Unbilled work is "candidate underbilling, not confirmed leakage." A rate difference is "a candidate discrepancy, not confirmed leakage or a penalty." | |
| PROOF | Source digest on the finding, receipt binding on the report | The receipt MAC is a server HMAC, not a customer-held signature. |
| Potential vs confirmed | Identified exposure is labeled for human review. Confirmed recovery stays `$0.00`. | `NOT_PROVEN` dollars can still sit inside identified exposure. The summary field `event_separation` says so. The console does not yet print that label. |
| Withheld | `withheld_unresolved_usd` is shown | |
| Authority | "you decide the next action · no vendor is contacted" on a loaded report. The page says DISPATER discovers and the customer decides. | |

## Privacy sentences on the page

- The customer controls the decision.
- The page does not contact vendors.
- Zero-knowledge encryption is not claimed. `/development-status` marks privacy as LIMITED and says tenant bearer tokens isolate API reads.
- External AI processing stays off unless a separate configuration is enabled. XAELI staging was not verified here.
- Customer-hosted deployment remains an offering. This session did not deploy one and did not verify its network.

## Synthetic demonstration vs pilot

The public console can run the existing synthetic fixtures. That is a demonstration with generated data. It is not a customer pilot. A pilot still needs owner approval for privacy, security, legal terms, retention, deletion, and a deployment whose egress has been tested in that environment.
