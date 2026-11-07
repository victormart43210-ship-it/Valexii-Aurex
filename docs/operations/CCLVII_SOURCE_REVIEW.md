# CCLVII bounded repair source review

Review date: 2026-11-06. Reviewer: separate Codex source-review agent `/root/cclvii_review`; this is agent separation, not external or organizational independence.

## Scope and disposition

Reviewed working-tree changes against `c4f45925e086bbb23b643e66707b224419d52b60` in `aurex/local_inference.py`, `aurex/adapters/ollama.py`, `aurex/dispater_intelligence.py`, `aurex/dispater_api.py`, and the three `tests/test_cclvii*.py` files. Read root `AGENTS.md`, the knowledge playbook, and mainline policy. HEAD remained the base SHA during review; this report does not attest a final commit or CI run. No product code, branches, merges, deployments, or external services were changed by the reviewer.

No critical or important defect found in the bounded repair. Source disposition: acceptable for coordinator integration, subject to exact-final-SHA checks and CI. Production/CUSTOS gate remains HOLD.

* Duplicate equipment identity (equipment ID plus service date) now withholds the entire unbilled hourly estimate at zero exposure, with insufficient-evidence qualification and human authority. Every submitted equipment row plus job and rate is included as a source digest in that duplicate finding. Existing unique ticket-ID validation still rejects repeated ticket IDs before reconciliation.
* Both local HTTP clients explicitly install `ProxyHandler({})`; environment proxy discovery cannot forward the prompt. Existing redirect-denial handlers, response read bounds, and socket timeout settings remain in place. This is source/client behavior, not proof of host-level egress isolation or a total wall-clock deadline.
* The API carries optional equipment/labor collections to the canonical engine. Omitted or null optional collections are excluded from the engine dataset; explicitly empty lists are preserved. Existing fields still use the prior model defaults. Consequently the legacy dataset serialization/hash is unchanged when these collections were absent. No response authority or recovery contract was relaxed.

## Additional synthetic checks

Ran an independent stdlib-only Python check from the repository using the real engine and both clients; no real model, paid call, or non-loopback service. It passed:

1. Two distinct machines on the same day price 16 hours at $25 = $400.
2. One machine on two distinct days also prices $400. These counterexamples check that the duplicate guard does not reject all multi-ticket jobs.
3. A duplicate pair plus a separate machine withholds the complete estimate at $0 rather than silently pricing a partial source set.
4. For each HTTP status 301, 302, 303, 307, and 308, both clients refused the redirect. A local synthetic receiver observed exactly the initial `/api/generate` request, with no redirected request (10 cases).

The added implementation tests were read, not rerun here. System `python` lacks pytest/FastAPI; the reviewer did not install dependencies or rerun unchanged full suites. The coordinator owns full dependency-backed API tests, proxy regression tests, lint/type checks, final SHA and CI evidence.

## Cursor182 integration comparison

Read `git diff c4f45925e086bbb23b643e66707b224419d52b60 8323f6db` for the candidate changes, including `dispater_store.py` and `egress.py`. The final commit alone is documentation-only, so comparison used the complete base-to-candidate range. There is a shared file (`dispater_intelligence.py`), but disjoint functional hunks: CCLVII changes `_append_unbilled_hours`; Cursor182 changes customer/event separation and orphan-payment withholding. Other production files do not overlap. The local inference clients do not call the connector allowlist modified by Cursor182. Duplicate findings have zero exposure and a non-unbilled finding code, so Cursor182's positive-unbilled-amount withholding logic does not re-add or reinterpret their dollars. No apparent integration conflict found by source review; no combined-tree execution was performed.

## Limits and follow-up observations

Existing `HOURS_SOURCE_CONFLICT` evidence references only job/rate, omitting equipment/labor source digests. The new duplicate-specific branch retains all relevant equipment evidence, but this review does not certify all existing conflict paths retain every source row. This predates the repair and is not a blocker to its bounded acceptance.

Equipment identity is exact string identity; the repair does not establish semantic equivalence of differently formatted machine IDs/dates or determine whether same-day shifts are genuinely distinct. Conservative withholding is intentional. The adapter still accepts `localhost` rather than pinning it to numeric loopback; that existing DNS behavior is outside this proxy repair. No claim of deployment, current remote main freshness, organizational independence, total network isolation, or business correctness beyond these synthetic cases is made.

Rollback: coordinator can revert the final bounded repair commit after recording its exact SHA; this reviewer did not create or alter that commit.

## Ingestion preservation addendum

Reviewed the subsequently supplied bounded changes to `aurex/dispater_ingest.py`, `aurex/dispater_documents.py`, and `tests/test_cclvii_ingest_semantics.py` against the same base. The shared explicit field allowlist preserves rate unit/supersession, payment direction/attribution, invoice customer and labor overtime across extraction and dataset construction. Required-field checks, sanitization, byte/row bounds and original source digest handling remain. Unknown columns do not enter the reconciler dataset. The additions do not overlap the Cursor182 production-file hunks. No critical or important issue found by source review.

An additional independent stdlib-only synthetic check passed: a JSON orphan REVERSAL of $40 survives ingestion as REVERSAL and yields $0 incoming exposure through the actual reconciliation engine; an unrecognized CSV `authority` column is omitted; a truncated CSV row raises `IngestError` rather than producing a record or an unhandled missing-cell exception. This targets payment-direction inflation rather than merely checking the implementation's field mapping. Read the four new format tests, but did not execute PDF/XLSX dependency-backed checks in the reviewer environment. Agent-reported test results are not substituted for reviewer-observed checks. The coordinator retains responsibility for final dependency-backed tests, combined Cursor182 execution, exact final SHA, and CI.
