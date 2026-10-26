# KUSANAGI CLXXIX — Project Iron Unification (partial)

Base SHA: 52c6453 (main at 1c05a95 + CLXXI). Production: HOLD. Data: SYNTHETIC ONLY.

## Reconciliation of referenced work
Open PRs (not merged, not integrated here): #145 CLXXII Iron Convergence (Jules), #146 CLXXVI Onyx governed retrieval bridge, #147 audit-readiness website copy, #148 NVIDIA $0 gate. #132 not inspected. Closed unmerged: #141–#144.
Absent on this branch: `docs/marketing/`, `website/src/components/dispater-audit-console.tsx`, `website/src/lib/dispater-audit-client.server.ts`, `aurex/openshell_policy.py` (only in closed #143). No Onyx adapter on main.

## Inventory
| Item | State |
|---|---|
| Synthetic audit (`aurex/dispater_pilot.py`, `dispater_evidence.py`) | Implemented on main; self-issued digests only |
| Experiment ledger (`aurex/experiments/ledger.py`) | Implemented, not wired to DISPATER |
| Onyx bridge | Implemented in #146, NOT integrated, NOT verified |
| CSV reconciliation (`aurex/dispater_csv.py`) | NEW, unit-tested, not exposed via API |
| Excel intake, formula validation, schema mapping | Missing |
| Frontend console wiring | Blocked (files not on this branch; await #147/#145) |
| Railway volume isolation | NOT VERIFIED (no Railway access) |
| OpenShell containment | NOT VERIFIED |
| Live Onyx interoperability | NOT RUN |

## Change in this PR
Deterministic Decimal-based CSV reconciliation (invoices vs tickets vs approved rates): duplicate lines, missing/unbilled tickets, service/quantity/rate mismatch, with variance. Findings are proposals only; authority financial/model = NONE.

## Tests
`pytest -q`: baseline 386 passed, 1 skipped; plus 4 new in tests/test_dispater_csv.py. `ruff` and `mypy aurex` clean. Frontend suites NOT RUN. Historical 402/149 figures not reproduced.

## Blockers / next
Merge order of #145/#146/#147 by owner; then Ledger↔Onyx contract, API endpoint with tenant auth, Excel intake, frontend wiring, Railway audit.
