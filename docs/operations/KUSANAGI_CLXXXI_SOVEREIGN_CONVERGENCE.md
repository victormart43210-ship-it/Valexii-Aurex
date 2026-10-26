# KUSANAGI CLXXXI — Project Sovereign Convergence (partial)

Main SHA: 551625e (551625e). Production: HOLD. Data: SYNTHETIC ONLY.

## Findings
- **Main CI was failing** (run 40254351534): `tests/test_dispater_proof.py` raised `ModuleNotFoundError: dispater_proof` because `pyproject.toml` package discovery omitted `dispater_proof*`. Fixed here by adding it to `[tool.setuptools.packages.find].include`.
- **PR #145** is `mergeable_state: dirty` against main 551625e: content conflicts in `.github/workflows/ci.yml`, `RECOVERY.json`, `RESUME.md`, `aurex/openshell_policy.py`, `tests/test_openshell_policy.py` (confirmed via local merge-tree against this branch, which also carries CLXXI/CLXXIX files). Not resolved: it needs a rebase on its own Jules branch by its owner, keeping the audit console and OpenShell policy. Its claimed 402 backend / 146 frontend results are NOT VERIFIED.
- **PR #149** (runner smoke, draft): runner remains NOT CONNECTED / NOT VERIFIED — no self-hosted job has run; the "AUREX independent runner smoke checks" success (run 40254381225) executed on a GitHub-hosted run, which is not runner evidence. Its CI failures are the same dispater_proof packaging error.
- #147 and Jules' Onyx branch (#146) were not integrated.

## Verification (this branch, after merging main)
`pytest -q`: 440 passed, 2 skipped. `ruff check .`: clean. `mypy aurex`: clean (78 files). Frontend Bun/tsc/build: NOT RUN.

## Status
Runner: NOT VERIFIED. Onyx: NOT INTEGRATED (no live interop). Evidence Ledger↔DISPATER: NOT INTEGRATED. Frontend↔backend: NOT RUN. Railway isolation: NOT VERIFIED. OpenShell runtime: NOT VERIFIED. Lovable: untouched, no credits used.

## Next
Owner merges this CI fix first; Jules rebases #145; then run #149 smoke on the real runner; then Onyx/Ledger contract and frontend wiring.
