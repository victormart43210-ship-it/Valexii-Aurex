# Copilot Recovery Handoff (KUSANAGI CCXIII)

- Branch: `copilot/kusanagi-ccxiii-dispater-beta-recovery` (based on Jules PR #159 head `df7db18`; PR #159 untouched).
- Code milestone commit: `f35a9bf2c9e5e3c75ec7c16b584dc8d6a20ff7c4`.
- Continue from: this file + `KUSANAGI_CCXIII_COPILOT_REPORT.md`.
- Setup: `python -m venv .venv && .venv/bin/pip install -e ".[dev]"`; website `npm install` (bun not available here).
- Open work: independent verification, staging deploy, UI display of the exposure breakdown, rate limiting, access audit log.
- Conflict risk: PR #159 must merge first (or this PR retargeted); PR #151 predates both and was not reconciled.
