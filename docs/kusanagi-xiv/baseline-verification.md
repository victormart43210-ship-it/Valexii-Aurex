# Baseline verification (OPERATION KUSANAGI XIV)

This file documents how to reproduce the baseline verification locally or on a staging host. It intentionally records exact commands and the expected baseline values so an independent verifier can reproduce the environment.

Baseline: the repository's CI reported successful checks for a recent commit. Independent local execution is required to confirm.

Environment

- Python: 3.12
- Install with dev extras: python -m pip install -e ."[dev]"
- Optional: create and activate a virtualenv

Commands to run (exact)

1. Upgrade pip

   python -m pip install --upgrade pip

2. Install project and dev dependencies

   pip install -e ".[dev]"

3. Static checks

   ruff check .
   python -m mypy aurex --strict

4. Tests

   python -m pytest -q

Expected baseline (as reported by CI logs)

- Python tests: 124 passing (repository reported in CI summary)
- Ruff: pass
- Mypy strict: 0 errors

How to collect evidence

- Capture full stdout/stderr for the commands above and save as artifacts.
- Record the commit SHA used when running the checks.
- If any command fails, collect the failing test names, stack traces, and the environment (OS, Python, pip list).

Notes and limitations

- CI logs are a useful indicator but do not substitute for running tests against the actual staging runtime (native Qwen, local loopback services).
- Several verification steps require local services (native model server) to be running on loopback; these cannot be executed from this agent without a reachable staging endpoint or shared artifacts.

