# OPERATION KUSANAGI CXXVII — RAILWAY STAGING ADMISSION GATE
**October 22, 2026 · Railway Staging Readiness & Staging Deployment Gate**

## Executive Summary
This document specifies the staging container build, environment variables, non-root runtime permissions, and deployment admission requirements for deploying the canonical backend onto Railway.

---

## 1. Production Service Isolation
- **Existing Production Service:** `VALEXII-AUREX / aurex-api` (online, running read-only version `1.0.0-readonly`).
- **Rule:** The existing production service remains **UNTOUCHED**. No unapproved deployment patches shall be applied to production.

---

## 2. Canonical Docker Configuration (`Dockerfile.aurex`)

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

---

## 3. Staging Admission Gate Criteria

| Gate | Requirement | Status |
| --- | --- | --- |
| Gate 1 | Pytest backend suite passes | PASS (393 passed) |
| Gate 2 | Ruff lints pass | PASS (0 errors) |
| Gate 3 | Mypy strict type checks pass | PASS (0 issues) |
| Gate 4 | Bun website tests pass | PASS (139 passed) |
| Gate 5 | Non-root container execution (UID 10001) | PASS |
| Gate 6 | Persistent SQLite path `/data/aurex_jobs.db` | PASS |
| Gate 7 | $0 default authorized spend limit | PASS |
| Gate 8 | Product owner staging authorization | **HOLD (Awaiting owner signoff)** |

---

## 4. Rollback Procedure
If staging exhibits unexpected behavior:
1. Revert Railway deployment image to previous immutable image SHA.
2. Verify `/data/aurex_jobs.db` SQLite integrity.
3. Confirm `/v1/health` returns HTTP 200 OK.
