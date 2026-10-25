# KUSANAGI CLXX — Sovereign Intake R13
Architecture and offline reference implementation for VALEXII.COM / DISPATER.AI → Sovereign Studio → AUREX-OX.

**Status:** ADDITIVE CANDIDATE / HOLD. Not merged, deployed, certified, independently verified, or connected to production. Does not include upstream third-party source code; catalog links identify dependencies for separately reviewed installation. No network activity by default.

## Sequence
Acquire → Quarantine → Preserve → Identify → Deduplicate → Classify → Extract → Normalize → Reconcile → Challenge → Human Review → Package/Receipt.

Keep original bytes, derivatives, assertions, and findings separate. Never silently modify evidence. An unexplained variance is not fraud. Unknown ≠ Safe; missing/stale evidence ≠ PASS. No system may be its own sole witness.

## Local offline smoke tests
`python3 -m unittest discover -s tests -v`
`python3 -m sovereign_intake.demo` (run with PYTHONPATH=src, or `PYTHONPATH=src python3 -m sovereign_intake.demo`)

## Integration
See docs/INTEGRATION.md. Review and merge only into the canonical Valexii-Aurex repository after an independent test pass. No automatic installation or deployment.
