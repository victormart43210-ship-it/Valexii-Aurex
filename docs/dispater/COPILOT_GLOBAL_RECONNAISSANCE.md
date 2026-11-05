# Copilot Global Reconnaissance — DISPATER (Stage 1)

Production: HOLD. Financial authority: NONE. Docs-only change; no code or dependencies introduced.

## Verified status (inspected 2026-11-05)

| Item | State | Evidence |
|---|---|---|
| `main` | `99af5fd8a2c1340bcf5d2eda03bb6dbe65e5a661` | 433 passed, 1 skipped, ruff clean (local venv, `pip install -e ".[dev]"`) |
| PR #162 | OPEN, draft, base `main`, head `e5115a6` (`copilot/kusanagi-ccxxi-iron-convergence`) | CI checks all SUCCESS; unmerged |
| PR #163 | OPEN, draft, base = #162 branch, head `9395e71` (`copilot/kusanagi-ccxxiv-receipt-auth`) | Stacked on #162; unmerged |
| Issue #152 | OPEN coordination hub | Latest comment: Copilot owns `dispater_store.py`, `dispater_intelligence.py`, `dispater_receipt.py`, new tests; Jules owns `dispater_api.py`, `api.py`, frontend |

## Key finding

The reconciliation engine, store, API, receipts and the `/dispater` console are **not on `main`**. They exist only in unmerged draft PRs #162/#163. On `main`, DISPATER consists of the demo/pilot/proof layer:

- `aurex/dispater_demo.py`, `dispater_demo_server.py`, `dispater_pilot.py`, `dispater_evidence.py`, `dispater_workflow.py`, `industrial_execution.py`, `dispater_proof/`, `dispater-web/`
- Tests: `tests/test_dispater_{demo,demo_server,pilot,proof}.py`

Implementing the Revenue Recovery engine on `main` now would duplicate #162. Work must stack on #162/#163 after owner decisions.

## Code paths added by PRs (not yet on main)

- #162: `aurex/dispater_{api,intelligence,store}.py`; tests for reconciliation, oracle differential, security, storage, body limit; `website/src/routes/dispater.tsx`, `dispater-reconciliation-console.tsx`, `dispater-contract.ts`.
- #163: `aurex/dispater_receipt.py` (HMAC-SHA256 + kid, fail-closed), multijob oracle, receipt-authenticity and store-crash tests.

## Unresolved dependencies / blockers (from #152)

- Owner decisions: duplicate-exposure semantic; provisioning `RECEIPT_KEYS`/`ACTIVE_KID`; nonce policy.
- Not implemented: durable request nonce, RFC 8785 canonicalization, asymmetric signing/anchoring.
- Blocked/not run: Railway volume test, staging, browser E2E, 108-run battery.

## Gaps vs. directive (not started)

Contract-rate validation, storage-fee/after-hours rules, payment-to-deposit reconciliation, audit-readiness engine, evidence qualification states, the 8-module command center, OSS matrix and license review. Candidate OSS (OpenContracts, Docling, OpenMetadata, PM4Py [AGPL gate], ERPNext [GPL, reference only]) have **not** been evaluated yet; no license or commit pins are claimed.

## Next steps

1. Merge or retarget #162/#163 (human decision), then branch from the result.
2. Stage 2 contract freeze, then Stage 3 challenge on `dispater_intelligence.py`.
3. OSS matrix with pinned commits and license review.
