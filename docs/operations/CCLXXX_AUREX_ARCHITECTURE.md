# CCLXXX AUREX-OX architecture

Observed at 10:20 PM CT on November 6, 2026. One backend remains `aurex/api.py`. No second AUREX process was added.

The chain stays Evidence → Qualification → Reality → Authority → Effect. A page cannot create financial or security authority. A model cannot grant itself permission. Confirmed recovery from the explanation path stays `0.00`.

| Layer | What this repository already uses |
|---|---|
| Inputs | Website server functions, DISPATER records, the gated XAELI staging route |
| Identity | Bearer token for AUREX routes; tenant grant hash for DISPATER |
| Evidence | Source hashes, receipt MAC, cell or row provenance |
| Qualification | Frozen finding qualifications and the evidence class map |
| Reality | Decimal reconciliation and stored runs |
| Authority | Hold, no financial authority, human review required |
| Effect | Read-only reports and explanations |
| Presentation | Existing DISPATER and XAELI pages |

`GET /health` now returns `process: PROCESS_HEALTHY` separately from `readiness`. Readiness is `DEPENDENCY_UNAVAILABLE` with HTTP 503 when a required SQLite parent cannot be used. An open store on `/tmp` is `DEGRADED`, not `READY`. A configured private Qwen host outside Railway is `MODEL_UNAVAILABLE`. The health request does not call the model.

`GET /v1/providers` requires the server bearer and returns the same provider description. It does not include a URL or a credential.
