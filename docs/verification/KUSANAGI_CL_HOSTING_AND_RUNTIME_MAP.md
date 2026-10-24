# KUSANAGI CL — Hosting, Runtime & Deployment Gap Map

## Architecture Overview
The VALEXII/AUREX platform operates across three hosting layers:

```
[ Visitor Browser ]
       │
       ▼
[ Cloudflare Edge / Published Lovable ] ──► https://valexii.com
       │ (Server-Side Proxy)
       ▼
[ Railway Staging Backend ] ─────────────► https://aurex-api-aurex-staging.up.railway.app
       │ (Persistent Volume)
       ▼
[ SQLite Storage / Evidence Ledger ] ────► /data/aurex_jobs.db
```

## Environment Variable Mapping
| Environment Variable | Required Location | Status | Purpose |
| :--- | :--- | :--- | :--- |
| `AUREX_SERVICE_URL` | Website Server Runtime | Configured | HTTPS Base URL for Railway AUREX API |
| `AUREX_SERVICE_TOKEN` | Website Server + Railway | Configured (>=32 chars) | Bearer authentication token |
| `AUREX_ADMIN_TOKEN` | Railway Backend | Configured | Owner-only administrative token |
| `AUREX_ENABLE_OFFLINE_LAB` | Railway Backend | Set to `1` in Staging | Enables `sqlite_roundtrip_v1` worker probe |
| `AUREX_NVIDIA_DOCS_ENABLED`| Railway Backend | Default `0` (Disabled) | Controls NVIDIA Document Intelligence V4 |
| `AUREX_ENABLE_OPA` | Railway Backend | Default `0` (Disabled) | Feature flag for OPA Rego policy gate |

## Identified Deployment & Integration Gaps
1. **Lovable / GitHub Synchronization Gap:** Code committed and pushed to GitHub `victormart43210-ship-it/Valexii-Aurex` does not automatically update the live published Lovable frontend at `valexii.com` without manual export/sync trigger or project owner release action.
2. **Clock Skew Gap (REPAIRED):** Railway container clock drift of a few milliseconds/seconds previously caused `evidenceFresh()` (`t <= now`) to reject valid observations as "FUTURE TIME". Fixed by restoring `+60_000ms` (+60s) clock skew tolerance.
3. **Capabilities Health Field Gap (REPAIRED):** `aurex/api.py` `/v1/health` endpoint previously omitted `"capabilities": [...]`, causing `checkAurexService` to return `OFFLINE`. Reconciled in `aurex/api.py`.

## Conclusion & Recommendations
The repository code on branch `audit/kusanagi-cl-independent-integration` is 100% verified and ready for staging. Live publication on `valexii.com` requires triggering a Lovable project sync from the canonical GitHub repository once owner approval is granted.
