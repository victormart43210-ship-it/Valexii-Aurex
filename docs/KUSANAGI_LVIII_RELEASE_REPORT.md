# KUSANAGI LVIII — Sovereign Ignition Railway Recovery Report

- **Canonical Repository:** `victormart43210-ship-it/Valexii-Aurex`
- **Railway Service:** `aurex-api` (Environment: `production`)
- **Mount Path:** `/data/aurex_jobs.db`
- **Candidate Branch:** `aurex-mainline-convergence-5126581965977077235`

## Verification Summary
- **Dockerfile Build Check:** PASS (Non-root user `aurex`, `$PORT` dynamic binding, `/data` volume)
- **Python Syntax Check (`compileall`):** PASS
- **Ruff Lints:** PASS (0 errors)
- **Mypy Strict:** PASS (0 errors across 40 source files)
- **Pytest Suite:** PASS (130 passed)
- **Release Integrity Gate:** PASS (status: ADMIT)

## Railway Deployment Configuration Instructions
1. **Dockerfile:** Set buildpack or Dockerfile path to `Dockerfile`.
2. **Mount Volume:** Add persistent volume `aurex-evidence-db` mounted at `/data`.
3. **Environment Variables:**
   - `AUREX_DB_PATH=/data/aurex_jobs.db`
   - `AUREX_SERVICE_TOKEN=<min_32_char_secret_token>`
4. **Deploy Command:** Handled via CMD in Dockerfile (`uvicorn aurex.api:app --host 0.0.0.0 --port ${PORT:-8000}`).

## Release Decision
**ADMIT FOR OWNER REVIEW** (Production deployment remains separately gated).
