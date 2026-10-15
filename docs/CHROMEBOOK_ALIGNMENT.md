# Chromebook Alignment for AUREX-OX

This document records the repository facts and Chromebook integration points derived from the repository's current contents. It is intended to guide the Chromebook ZIP reconciliation step and to preserve machine-readable configuration expectations.

Do not include secrets in this file.

Repository facts (repo-derived)
- Python runtime used in CI: 3.12 (see .github/workflows/ci.yml)
- CI runner OS: ubuntu-latest (Linux)
- Dev install: pip install -e "[dev]" (project defines dev extras)
- Key environment variables referenced in code: AUREX_SERVICE_TOKEN, AUREX_DB_PATH, AUREX_LEDGER_PATH
- Default DB path: /tmp/aurex_jobs.db (DEFAULT_DB_PATH in aurex/database.py)
- Local ledger default path: $HOME/aurex-evidence-ledger.jsonl (workstation/evidence_ledger.py)
- Local inference loopback-only enforcement (aurex/local_inference.py and tests): only 127.0.0.1, localhost, ::1 and explicit port; refuses redirects and non-loopback hostnames.
- API routes present in repository: /v1/health, /v1/capabilities, /v1/jobs, /v1/evidence, /v1/budgets, /v1/jobs/{jobId}/cancel
- Database tables discovered: jobs (id, kind, state, idempotency_key, params_json, reservation_usd, created_at, updated_at, result_json), evidence_records (id, capability_id, kind, collected_at, sha256, summary)
- Test commands (from CI): ruff check ., mypy aurex, pytest -q

Chromebook integration notes
- The Chromebook branch (integration/kusanagi-xxii-governed-execution) contains local-first workflow engine code and local inference adapters which must be reconciled into the canonical backend. Do not blindly replace mainline code — preserve provenance and tests.
- Expected Chromebook developer environment:
  - OS: Linux (ChromeOS Linux container / chroot)
  - Python: 3.12
  - Dev install: pip install -e "[dev]"
  - Local model endpoint: http://127.0.0.1:<port> (explicit port required)
  - Local inference approval flag required (approved=True) for any invocation in codebase

Compatibility guidance
- Ensure loopback-only checks remain (127.0.0.1/localhost/::1), explicit port required.
- Ensure budget enforcement remains at $0.00 by default; paid providers must be opt-in and explicitly approved by operator.
- Preserve evidence ledger path semantics; avoid symlinks for ledger file.

Files relevant to Chromebook alignment
- aurex/local_inference.py (if present on the Chromebook branch)
- aurex_workflows/core.py
- aurex_workflows/local_executor.py
- aurex_workflows/recovery.py
- scripts/local_inference_smoke.py
- scripts/aurex_convergence_audit.py
- tests/test_local_inference.py
- tests/test_workflows.py

Machine-readable integration manifest
- See config/chromebook-integration-manifest.json for a parsed copy of the above facts.

