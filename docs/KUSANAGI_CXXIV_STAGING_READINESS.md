# OPERATION KUSANAGI CXXIV — RAILWAY STAGING READINESS
**October 21, 2026 · AUREX Railway Staging Deployment Specification**

## Overview
This document specifies the deployment configuration, environment variables, security boundaries, and rollback procedures for deploying `work/kusanagi-cxxiv-sovereign-convergence` as an isolated staging service on Railway.

---

## 1. Production Service Isolation
- **Existing Railway Service:** `VALEXII-AUREX / aurex-api` (online, 1/1 replicas, running read-only version `1.0.0-readonly`).
- **Rule:** The existing production service remains **UNTOUCHED**. No unapproved deployment patches shall be applied to production.

---

## 2. Staging Deployment Configuration

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY aurex/ ./aurex/
COPY integrations/ ./integrations/
COPY workstation/ ./workstation/
RUN pip install .
RUN useradd -u 10001 -m aurex && chown -R aurex:aurex /app
USER 10001
EXPOSE 8080
CMD ["sh", "-c", "uvicorn aurex.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

### Environment Variables for Staging
- `AUREX_SERVICE_TOKEN`: Secret Bearer token (min 32 chars)
- `AUREX_DB_PATH`: `/data/aurex_jobs.db`
- `AUREX_ENABLE_OFFLINE_LAB`: `1`
- `AUREX_NVIDIA_DOCS_ENABLED`: `0` (Disabled by default)
- `AUREX_BUDGET_USD`: `0.00`

---

## 3. Staging Admission Checklist
- [x] Pytest backend suite passes (393 passed)
- [x] Ruff check passes (0 errors)
- [x] Mypy strict type check passes (0 issues)
- [x] Bun website unit tests pass (139 passed)
- [x] Bun website production build succeeds
- [x] Non-root Docker runtime verified (UID 10001)
- [x] Persistent SQLite database path `/data/aurex_jobs.db` configured
- [x] Paid inference disabled by default ($0 budget)
- [x] Product owner authorization required prior to live deployment

---

## 4. Rollback Procedure
If staging exhibits unexpected behavior:
1. Revert Railway deployment image to previous immutable image SHA.
2. Verify `/data/aurex_jobs.db` SQLite integrity.
3. Confirm `/v1/health` returns HTTP 200 OK.
