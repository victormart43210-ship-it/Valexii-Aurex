# KUSANAGI CXXV — Checkpoint 2: Contract Bridge (isolated candidate)

Date: 2026-10-22. Production authority **NONE**, release **HOLD**.
Branch `work/kusanagi-cxxv-copilot-iron-bridge` was created from
`main@df0654390049118a142ec3b3356f0f40b4789fe4`.
This is **NOT** a Jules CXXIV merge or a completed end-to-end deployment.

## Source freeze

| Source | Inspected SHA | Role |
|---|---|---|
| main | `df0654390049118a142ec3b3356f0f40b4789fe4` | branch base |
| PR #99 | `8e859304d14c6aaa2cd4ed84d2e9db93fe9700b9` | financial audit beta **review only** |
| PR #104 | `3b3d1de63f764a777758f709130a91324bcd06ca` | canonical API/SQLite, owner of Python reconciliation and job behavior |
| PR #106 | `17fdd82718178544146fe7e8870b0d6eb1d56f1a` | NVIDIA document candidate, **not deployed** |
| PR #107 | `b2960cfd0911c21bc96798bead4f60f7808a3907` | four NVIDIA offline research baselines, **not deployed** |

The purported CXXIV branch and its canonical diff were **not found** on the remote during this checkpoint.
Do not infer source integration or PASS from an absent remote branch.

## Measured code changes (Checkpoint 2)

1. `website/src/lib/aurex-api-schema.ts`: accept canonical underscore
   capability IDs (`regression_scan`, `memory_graph`, `remote_inference`) and
   `offline_probe` evidence. Previously, valid Python responses were rejected.
2. `website/docs/aurex-api/openapi.yaml`: mirror the exact schema
   changes and Python's idempotent POST /v1/jobs HTTP 200 contract.
3. `website/src/lib/aurex-cxxv-bridge.ts`: typed offline versioned contract:
   - strict `BETA-###` / `INV-####` synthetic cases with exact integer cents,
     positive rate/hour bounds, max 100 rows, duplicate *case* IDs denied
     atomically. Duplicate invoice IDs are permitted for future flagging by
     the canonical Python reconciliation engine. No AI inference or finance effect.
   - five registered **candidate-only** NVIDIA lanes: document (#106) plus
     quantitative signals, transaction features, financial distillation, fraud review
     (#107), all `NOT DEPLOYED / NOT RUN / HOLD`.
   - exactly ten OX workstation sections, strict service-reported snapshot
     projection with 90s freshness and **independentVerification: NOT VERIFIED**
     even when capability/evidence IDs match.
4. `website/src/components/aurex-cxxv-bridge.test.ts`: contract regression,
   adversarial financial validation, registry and workstation projection tests.
5. `tests/test_cxxv_contract_inventory.py`: Python-side source contract
   inventory and bearer-auth denials, no network or DB writes.

## Convergence map — no overlapping backend ownership

| Area | Jules CXXIV authority | CXXV responsibility |
|---|---|---|
| FastAPI routes / job engine | Sole owner | Python/TS contract checks; no route edits |
| Deterministic Python financial engine | Sole owner | Typed **staging input only**; no duplicate audit engine |
| NVIDIA model/runtime | Review + deployment gates | Display research registry as unavailable |
| SQLite, leases, evidence / authority | Sole owner | Validate response shape and freshness semantics, never promote |
| Lovable AUREX/OX visuals | Existing owner project | Candidate ten-lens schema only; **not published** |
| Railway deployment, secrets, budget | Existing read-only production | **No changes, no inference, $0** |

### Not implemented, not assumed

- No real financial audit HTTP endpoint added or claimed.
- No document uploads, payment authorization, transfers, trades or bank access.
- No NVIDIA models trained or connected; no GPU or remote inference.
- No privileged Lovable changes, Railway deploy or DNS changes.
- CXXIV compatibility not assessed until recoverable head exists.
- No independent anti-fraud efficacy test, real financial accuracy claim,
  production permission, or full end-to-end security verification.

## Test instructions / remaining gate

Run tests on **the final exact commit**, not the source freeze SHA:

```bash
python -m pytest -q tests/test_cxxv_contract_inventory.py
python -m pytest -q
ruff check .
mypy aurex
cd website
bunx vitest run src/components/aurex-cxxv-bridge.test.ts
bunx vitest run
bun run build
```

GitHub Actions/CI and complete frontend/backend tests must be reported
from actual workflow logs. If not executed, label `NOT RUN`. Passing
contract checks are **not** independently verified capability.

**Final status for this checkpoint:** Code committed to isolated CXXV branch;
source-level contract adapters added. Independent reality, worker/Jules
convergence, staging, production authority **HOLD**.
