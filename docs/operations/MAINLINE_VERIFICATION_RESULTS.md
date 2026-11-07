# Mainline Verification Results (CCXXVI)

Candidate: `main` @ `99af5fd` + merge of PR #163 head `9395e71` (which contains #162 `e5115a6`). The resulting tree is byte-identical to #163's head. Executed locally on 2026-11-05 in a clean venv / `npm ci`.

| Gate | Command | Actual result |
|---|---|---|
| Backend tests | `pytest tests -q` | 591 passed, 1 skipped |
| Baseline `main` | `pytest tests -q` | 433 passed, 1 skipped |
| Ruff | `ruff check .` | All checks passed |
| Mypy | `mypy --strict aurex` | Success, 83 files (CI itself runs `mypy aurex`) |
| dispater-web | `npm ci && npm test && npm run build` | 25/25 pass; build OK |
| website unit | `npx vitest run` | 22 files, 153 tests passed |
| website types | `npx tsc --noEmit` | exit 0 |
| website build | `npm run build` | succeeded (nitro output) |
| Dependency audit | `pip-audit` | No known vulns reported; own package skipped (not on PyPI). `npm audit` NOT run. |
| Secret scan | `detect-secrets scan` on changed files | 7 hits, all git SHAs in handoff JSON (false positives, reviewed) |

DISPATER-specific suites (reconciliation, oracle differential/multijob, security, storage, store crash, body limit, receipt authenticity) are inside the 591 backend tests.

## NOT run
Browser E2E, Railway volume/staging test, 108-run battery, a website-to-live-backend contract test, real XAELI inference-denial beyond existing unit tests, and independent (non-Copilot) verification of the combined branch. Green results here do not prove production readiness.

## Not implemented (from CCXXV list)
Signed-history-field verification on history endpoints, receipt-field preservation in frontend export, and the Evidence Integrity Kernel were NOT investigated or changed in this operation. Owner decisions from #152 (duplicate-exposure semantic, `RECEIPT_KEYS`/`ACTIVE_KID`, nonce policy) remain open.
