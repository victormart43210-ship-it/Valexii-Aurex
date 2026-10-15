# OPERATION KUSANAGI XIII — SOVEREIGN CONVERGENCE REPORT

DATE: 2026-10-14 UTC

BACKEND REPOSITORY: victormart43210-ship-it/Valexii-Aurex
BACKEND BASE SHA: f8df262ce39be2ba3b25046d94632e86179e15dd
REPAIR TARGET: work/kusanagi-xiii-evidence-repair; use PR head SHA and manifest for final source identity.

WEBSITE REPOSITORY: NOT VERIFIED; Valexii-nexus is not the website source at inspected main.
WEBSITE SOURCE SHA: 8353b5e9ac32e6c5d983151acfabd02f29e46bd8 (Lovable source, not verified deployed SHA)
LOVABLE PROJECT: 811ffc43-2c8b-4c88-ab4c-4de668d089cb — Valexii Ai
GITHUB SYNC STATUS: NOT VERIFIED

CLAUDE WORK RECOVERED: NOT VERIFIED (Phase 44/45 missing)
COPILOT WORK RECOVERED: PARTIAL (XI branch exists, no distinct diff)
JULES WORK RECOVERED: PARTIAL (merged source and VIII–X metadata; no VIII–X file changes; XII not found)

BACKEND BUILD: PASS (wheel)
BACKEND TESTS: PASS (138 passed, 1 skipped locally; baseline 124 passed, 1 skipped)
RUFF: PASS
MYPY: PASS (strict, 40 files)
WEBSITE BUILD: NOT RUN
WEBSITE TESTS: PARTIAL (3 focused patch tests; full suite NOT RUN)

AUTHENTICATION: PARTIAL (local bearer tests pass; cross-user/session lifecycle gates outstanding)
ED25519: PARTIAL (trust/freshness repair tests pass; independent review and key custody outstanding)
SQLITE JOBS: PARTIAL (transition repair tested; ownership/idempotency/durable deployment gaps)
OPENAPI CONTRACT: PARTIAL (documented incompatibilities remain)
INFERENCE ADAPTER: PARTIAL (code exists; API dispatch and live model NOT VERIFIED)
WEBSITE API ADAPTER: PARTIAL (existing source + tested unapplied patch)
MOCKED INTEGRATION: PARTIAL (actual API response schemas through website functions; no full pipeline)
STAGING INTEGRATION: BLOCKED
LIVE LINUX QWEN: BLOCKED

SECURITY FINDINGS: See 09-adversarial-findings.md.
REPAIRS COMPLETED: Backend fail-closed integrity repairs on isolated branch; exact-revision website patch prepared.
UNRESOLVED BLOCKERS: Website upstream/sync; Linux source/access; real job worker; identity and evidence contract; independent security review; complete staging tests.
PULL REQUESTS: Draft backend PR prepared/opened as reported with this deliverable. Website PR blocked on canonical upstream.
PRODUCTION DEPLOYMENT: NOT AUTHORIZED
FINAL VERDICT: PARTIAL — RELEASE BLOCKED

The test runner independently reran prior agents' source, but this author has not obtained a separate review of its new security changes. Do not treat this report as its own sole witness.
