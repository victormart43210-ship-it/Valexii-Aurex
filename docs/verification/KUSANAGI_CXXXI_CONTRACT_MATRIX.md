# KUSANAGI CXXXI — Contract Matrix (Wave One, PARTIAL)

Source inspected: `work/kusanagi-cxxix-staging-convergence@6adc1936d09534b134182e769f88fea9c5a0125a` (`aurex/api.py`, `aurex/pipeline_receipts.py`).
NOT YET INSPECTED: `aurex/fenced_worker.py`, `aurex/database.py`, `integrations/kusanagi-xvi/backend/`, `website/src/lib/*`, `website/docs/aurex-api/openapi.yaml`.
Declared route != route available in Railway entrypoint. Source declarations below do NOT prove runtime integration.

| Route | Declared in `aurex/api.py` | Auth in source | Railway staging entrypoint | Status |
|---|---|---|---|---|
| GET /v1/health, /health | yes | **none** | NOT VERIFIED | see finding F1 |
| GET /v1/capabilities | yes | bearer | NOT VERIFIED | |
| GET /v1/jobs | yes | bearer | NOT VERIFIED | |
| POST /v1/jobs | yes | bearer + Idempotency-Key | NOT VERIFIED | gated by env flags |
| GET /v1/jobs/{id} | yes | bearer | NOT VERIFIED | |
| POST /v1/jobs/{id}/cancel | yes | bearer | NOT VERIFIED | |
| GET /v1/jobs/{id}/receipt | yes | bearer | NOT VERIFIED | |
| GET /v1/evidence | yes | bearer | NOT VERIFIED | |
| GET /v1/budgets | yes | bearer | NOT VERIFIED | |

## Findings (source-level, not yet reproduced by a running test)
- **F1 — health auth drift:** the earlier PR #104 repair required authenticated health on the read-only bridge. `aurex/api.py` health handler has no `authenticate` dependency. Needs a decision by Work; a contract test should pin whichever is intended.
- **F2 — version drift:** API reports `0.1.0a1`; production reports `1.0.0-readonly`.
- **F3 — entrypoint gap:** staging Railway builds with root `/integrations/kusanagi-xvi/backend` (per CXXIX recovery JSON) so root `aurex/` modules are not in the build; route declaration alone cannot expose canonical financial jobs.
- **F4 — kind pattern vs behavior:** `JobCreateRequest.kind` regex accepts `benchmark` and `hypothesis_test`, but the handler rejects anything except `regression_scan` with 400. Schema is wider than behavior.
- **F5 — dual execution modes:** `AUREX_JOB_EXECUTION_MODE=queued` returns a queued job without a worker in this process; contract tests must cover both modes.
- **F6 — digest serialization:** receipt digest = `sha256(json.dumps(observation, sort_keys=True).encode())` (default separators). Verifier in `scripts/cxxxi_receipt_verify.py` mirrors it.
- **F7 — storage isolation:** staging and production report the same volume id `4d23b1e6-3625-4def-aa97-82e10859f04d`; isolation NOT VERIFIED; staging writes stay blocked.

Authority NONE · Independent verification NOT VERIFIED · Release HOLD
