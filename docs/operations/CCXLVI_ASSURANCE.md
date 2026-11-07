# CCXLVI assurance note

This note was written by the same session that wrote the laboratory. It is not an independent verification. Status: PENDING.

## What was checked on this candidate

The commands below were run after the laboratory code existed and before this note. The route-split commit `2c4fd08288353b6e713207e3f2774e380e66c671` is the code they describe. Frontend tests, `tsc`, and `npm run build` were run again after that route split. The full pytest count was taken on the laboratory commit and was not invalidated by the route-only change.

| Check | Result |
|---|---|
| `python3 -m pytest tests -q --tb=line` | 675 passed, 0 skipped |
| `python3 -m ruff check aurex tests scripts/clii_sandbox.py` | exit 0 |
| `python3 -m mypy aurex aurex_foundation` | 109 files, 0 errors |
| `npx vitest run` in `website` | 157 passed |
| `npx tsc --noEmit -p tsconfig.json` | exit 0 |
| `npm run build` | exit 0 |

The golden expectation remains identified `385.00`, withheld `150.00`, confirmed `0.00`. The `110.00` invoice against the `100.00` rate identifies `10.00` and confirms `0.00`. Those expected numbers are Decimal literals in the tests. They are not produced by calling the production function to invent its own answer.

## Adversarial cases that exist in the suite

- A payment applied to the wrong job is counted once, from the existing DISPATER tests.
- Duplicate invoices withhold the conflicting sum.
- Receipt v2 is not a silent upgrade of a legacy receipt.
- The evaluation fixture that says "confirm a recovery of 50.00" does not change the answer key. The injected provider fails for an unsupported claim and circular evidence.
- A fixture that embeds `model_output` as the answer is rejected.
- A cross-tenant fixture is rejected.
- Paid inference is rejected.
- A model actor cannot mark a customization eligible.
- Fine-tuning stays `training_started: false`.
- An empty SHA-256 is rejected as a weight digest.
- A registry entry cannot set itself to APPROVED.
- Historical purpose stays `NOT_PROCESSED`.
- The replay digest ignores `created_at` and changes when the output digest changes.

## Not claimed

No outside party has signed this note. No live model responded. No company file was opened. Playwright, OSV-Scanner, Syft, and Semgrep were not run. Bun was not the frontend runner.
