# BCXMET Ascension Verification (synthetic, local)

Base `main` `974eecff4c3d1f554882a94903bbc873e0ea537f`.

| Command | Result |
|---|---|
| `pytest tests -q` | 612 passed (baseline 592 incl. 1 skip noted earlier; +20 new) |
| `ruff check .` | All checks passed |
| `mypy --strict aurex` | Success, 84 files |
| `website: npx vitest run` | 23 files, 156 tests passed (+3 receipt round-trip) |
| `website: npx tsc --noEmit` | exit 0 |
| `website: npm run build` | succeeded |
| `dispater-web: npm test` | 25 pass (earlier run, same code) |

Not run: browser E2E, live/staging backend, independent verification, dependency/secret scans on this branch. Tests are synthetic; no live verification exists.
