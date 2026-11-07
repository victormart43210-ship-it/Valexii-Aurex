# CCLIX frontend to backend map

Tested code `ba6db1bac46e76317e6218301f1d71f051781636`. Observed on this machine unless marked assumption.

| Surface | Client | Endpoint | Authorization | Service | Data | Evidence | UI response |
|---|---|---|---|---|---|---|---|
| DISPATER console | `website/src/lib/dispater.functions.ts` server function | `POST /v1/dispater/reconciliation` | Bearer from `AUREX_SERVICE_TOKEN` or `AUREX_STAGING_SERVICE_TOKEN`. Tenant from server env, not the browser. | `aurex/dispater_api.py` to `RevenueLeakageEngine` | Synthetic fixture only | Receipt fields parsed by Zod. `confirmed_recovery_usd` must be the literal `0.00`. | LOADING, CONNECTED, DISCONNECTED, UNAVAILABLE, or ERROR. Idle SSR text is `API link: DISCONNECTED`. |
| DISPATER CSV admit | `admitSyntheticDispaterCsv` | `POST /v1/dispater/documents` | Same server token | `aurex/dispater_ingest.py` | One synthetic CSV | Document schema stays HOLD / financial authority NONE | Same console states |
| XAELI page | `readXaeliStagingStatus` | `POST /v1/xaeli-staging/explain` only when staging flags, Qwen URL, service URL, and a 32+ character token are set | Server bearer plus the fixed synthetic-only operator header | `aurex/xaeli_staging.py` to local Qwen | One of three synthetic prompts | A PASS answer is shown as staging text, not authority | Otherwise `unavailable`, `disconnected`, or `error`. Scripted page copy stays labeled scripted. |
| AUREX-OX pages | static routes `/aurex-ox` | none in this change | none | `aurex/ox` registry is offline | no live model | evaluation cannot authorize money | unchanged status copy |
| BCXMET | `website/src/routes/bcxmet.tsx` | none | none | presentation | none | Orb has no security effect | unchanged |
| DISPATER-web | separate package | its own staging adapter | fails closed when unconfigured | not the `aurex` process | fixtures | local receipt check | 25 tests passed |

`website/` is the VALEXII.COM source in this repository. `dispater-web/` is a separate package and is not the deployed homepage. No Lovable project is connected from this checkout. Railway readiness code exists in `aurex/railway_readiness.py` and does not deploy.

Observed: `AUREX_XAELI_STAGING_ENABLED` is not 1, `AUREX_QWEN_BASE_URL` is unset, and `127.0.0.1:8080` refused a connection. XAELI live connection is NOT_VERIFIED.
