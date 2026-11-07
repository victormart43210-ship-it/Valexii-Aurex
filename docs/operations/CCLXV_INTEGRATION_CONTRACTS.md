# CCLXV integration contracts

Tested code `cfbf5386e679696048318ad843aeb29b520654bb`. These contracts are the ones already implemented. Parallel work was not allowed to invent a second API.

## Website to AUREX

`website/src/lib/dispater.functions.ts` calls `executeDispaterReconciliation` and `readDispaterRun`. The browser sends a fixture name. The server adds the tenant and the bearer token. Local HTTP is allowed only when `NODE_ENV` is not `production`. A missing token or URL raises `DISPATER backend is not configured`. The timeout is 6 seconds. There is no retry. A non-OK response becomes `DISPATER API error (<status>)` and the backend body is dropped.

## AUREX to DISPATER

`POST /v1/dispater/reconciliation` accepts `SYNTHETIC_ONLY` only. The engine returns `confirmed_recovery_usd` as `0.00`. `GET /v1/dispater/runs/{run_id}` reads that stored run for the same tenant. The run id is `run-` plus 32 hex characters. Another tenant receives 401 or 403.

## AUREX to a private model

`POST /v1/xaeli-staging/explain` stays disabled unless `AUREX_XAELI_STAGING_ENABLED` and `AUREX_XAELI_OPERATOR_APPROVED` are both `1`, the budget is zero, and the header is `synthetic-only`. The adapter target is `AUREX_QWEN_BASE_URL` or `http://127.0.0.1:8080/v1`. There is no paid fallback.

## Evidence to authority

A model evaluation report from `aurex/ox/evaluation.py` sets `live_connection` to `NOT_VERIFIED`, `financial_authority` to `NONE`, and `approval_state` to `CANDIDATE`. `aurex/model_lab.py` does not assign scores. An authorization claim returns `effect: NONE`.

## Training

`training_decision` returns `REFUSED` or `READY_NOT_LAUNCHED`. `launch` is always `NOT_STARTED`. Customer data, a paid budget, a missing license review, or a missing owner flag refuses the job.
