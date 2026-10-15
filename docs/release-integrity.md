# AUREX Release Integrity Gate

The Release Integrity Gate enforces that no release candidate can be admitted to production without passing complete, exact-SHA verification against the pinned Git commit.

## Requirements
1. **Commit Pinning:** Candidate SHA must match active `git rev-parse HEAD`.
2. **Ruff Lints:** 0 lint errors (`ruff check .`).
3. **Mypy Strict:** 0 type errors (`python3 -m mypy aurex --strict`).
4. **Pytest Suite:** 100% test pass rate (`pytest`).
5. **Fail-Closed:** Any mismatch, error, or missing evidence results in status `HOLD`.
