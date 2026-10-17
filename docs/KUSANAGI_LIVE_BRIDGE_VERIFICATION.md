# Operation IRON BRIDGE — Live Verification Architecture

- **Production Backend URL:** `https://aurex-api-production-c535.up.railway.app`
- **Allowlisted Hosts:** `aurex-api-production-c535.up.railway.app`, `127.0.0.1`, `localhost`
- **Verification Harness:** `scripts/verify_live_bridge.py`

## Endpoint Verification Contracts
1. `GET /health` - Public/Authenticated health response
2. `GET /v1/capabilities` - Capability listing (`regression_scan` / `regression-scan`)
3. `GET /v1/evidence` - Evidence records ledger
4. `GET /v1/budgets` - Budget status ($0.00 default)
5. `GET /v1/jobs` - Active/Historical job list
