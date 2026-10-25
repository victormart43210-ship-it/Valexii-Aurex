# Fresh source review

Reviewer: separate fresh-context agent `canada_finland_review`, GPT-6-astra high, same Work tool environment. Read-only; no sub-reviewers. Source review, not independent financial certification.

Exact reviewed local head: e44e68b1b2a6270929e0624c97e1b85818fb02ae.
Equivalent remote CP002: 927ea8bbaf437331410049e74b4214e27a08e16c. Coordinator verified equal Git tree hashes.
Base: 2ce2f654b0d5d1f21786dd587d9137d77695f420.

Verdict: PASS for bounded offline source candidate; no Critical or Important findings. No merge/deployment authorization. All 10 changed paths read against repository instructions and scoped plan.

Independent commands (from repo root, interpreter ../aurex/.venv/bin/python):
- With ALL_PROXY/HTTP_PROXY/HTTPS_PROXY and lowercase unset: `python -m pytest -q tests/test_canada_finland.py`: 18 passed.
- Same environment: `python -m pytest -q`: 496 passed, 1 skipped, 1 existing Starlette/httpx deprecation warning, 8.74s.
- Same environment: `python -m robot --variable PYTHON:../aurex/.venv/bin/python --outputdir /tmp/canada-finland-independent-review acceptance/canada_finland.robot`: 3 passed.
- `python -m ruff check .`: PASS.
- `python -m mypy aurex`: PASS, 77 files.
- With AUREX_BROWSER_STAGING_ADMITTED and AUREX_OWNER_STORAGE_STATE unset: `python -m robot --output NONE --log NONE --report NONE acceptance/website.robot`: expected exit1, admission HOLD before Browser import/navigation.
- Temporary-only fault injection: patched Path.open to raise OSError on manifest-sha256.txt after payload creation; original error propagated and incomplete destination removed: PASS.

Confirmed exact synthetic observation comparison, canonical verifier reuse, output bound before writes, exclusive output directory, private permissions, narrow owner/host/port grants, no network/enrollment actions, CI invoking only offline tests. Existing canonical runtime and wg-easy candidate unchanged.

Minor deferred: no committed fault-injection cleanup regression test. Observed behavior passes, but future cleanup regressions have weaker automated protection. No source repair required.

Reviewer declined to judge; coordinator rulings:
1. Live UI selectors, owner session and admitted Browser runtime: NOT RUN, keep activation HOLD. Cost if assumed working: unusable or misleading demonstration.
2. Archivematica ingest/AIP/retrieval/preservation: NOT RUN, claim only validated BagIt export. Cost if assumed complete: unproven retention.
3. Tailscale enforcement/revocation/identity/staging host: NOT RUN, candidate JSON only. Cost if assumed safe: unintended access.
4. Railway isolation/production state/cost/financial accuracy: NOT VERIFIED in this change, preserve all existing gates. Cost if bypassed: production/data/cost exposure.
5. Remote CI was not queried by reviewer: coordinator independently read GitHub CP002 run conclusions and verified source tree. Do not label CI results independently reviewer-queried.

Later checkpoint changes add evidence/recovery documentation only, not new runtime behavior. No financial authority or source-truth certification granted.
