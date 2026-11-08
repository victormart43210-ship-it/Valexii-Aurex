# Mainline verification report - PR #212

Date: 2026-11-08. Base (`main`): `fc2bed4dd98054503254ad1a4c11fbecd7b0deca`. Head: `edbdc11336f4ec177b5e0cc326f372c18000bc04` (confirmed via `gh pr view 212`; draft, mergeable).

## Verified (V)
| Check | Result |
|-------|--------|
| GitHub CI at head: docker-build-and-smoke, integration, offline-practice, synthetic-contracts, test (x2), verify | all pass |
| `ruff check .` (local checkout of head) | All checks passed |
| `mypy aurex` (local) | no issues in 131 source files |
| `pytest -q` (local, Python 3.12) | 954 passed, 2 skipped |

The earlier 10 Mypy errors are not present at this head.

## Not verified / outstanding
- G4: independent reproduction by a separate reviewer - not done (this run is the author side).
- G3: tenant-isolation/approval-bypass negative tests for the new modules were not separately audited here.
- G6: branch-protection settings not inspected. G7: no owner approval.
- Frontend tests/build, dependency and secret scanning: not run in this session.
- #209-#211 fail CI (see `MAINLINE_CONVERGENCE_MATRIX.md`); #212 does not depend on them.

Decision: **HOLD** (draft). Merge, deployment and all financial/production authority: not granted.
