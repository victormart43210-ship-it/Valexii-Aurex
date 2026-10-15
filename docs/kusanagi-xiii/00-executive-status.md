# OPERATION KUSANAGI XIII — Sovereign convergence report

Date: 2026-10-14 UTC. **FINAL VERDICT: PARTIAL. RELEASE: BLOCKED.**

The backend baseline tests reproduce, but they do not establish a working bridge. Eleven new adversarial cases failed against the baseline. This branch repairs false execution evidence, unauthenticated health, unbounded input, terminal-state overwrites, and self-supplied verification keys. All changes await independent review; nothing was merged or deployed.

The actual website source was inspected directly through Lovable at `8353b5e9ac32e6c5d983151acfabd02f29e46bd8`. The proposed GitHub website repository contains only LICENSE. A separate exact-revision website adapter patch was prepared and tested, not applied to Lovable or published.

Native Qwen, Phase 44/45 Linux source, authenticated staging, full website build, and end-to-end inference remain BLOCKED/NOT VERIFIED. No real inference occurred.

Baseline: 124 passed, 1 skipped; Ruff and strict mypy pass. Repair branch: 138 passed, 1 skipped; Ruff, strict mypy and wheel build pass. Website patch: 3 focused adversarial tests pass; this is not a website build or full suite. One Starlette TestClient deprecation warning remains.

See [inventory](01-repository-inventory.md), [findings](09-adversarial-findings.md), [test matrix](08-test-matrix.md), and [release report](11-final-evidence-report.md).
