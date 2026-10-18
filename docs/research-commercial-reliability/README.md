# Research-to-product review: reliable AUREX outcomes

Status: development repair; production HOLD. Research collected October 17–18, 2026 UTC.
Base: df0654390049118a142ec3b3356f0f40b4789fe4, canonical Valexii-Aurex main.
Branch: work/research-commercial-reliability. No new production backend.

## Source assessment

This is a selected review of primary research and engineering/product reports, not an exhaustive paper survey or replication. Vendor benchmarks and commercial claims are not AUREX measurements.

| Source | Date | Applicable lesson | Decision |
| --- | --- | --- | --- |
| Anthropic: Investigating unintended model actions https://www.anthropic.com/research/investigating-unintended-model-actions | 2026-10-09 | Persistent agents can work around limits; control effects outside the model and retain honest failures. | Repair durable failure reporting under existing lease authority. |
| Anthropic: AI models may be capable of self-replicating without access to a datacenter https://www.anthropic.com/research/self-replicating-ai | 2026-10-12 | Small/local models are not automatically harmless. The report studies replication capabilities, not safe product deployment. | Retain bounded workers, no autonomous installation/replication or public inference exposure. No offensive implementation. |
| Anthropic: The AI expectations gap https://www.anthropic.com/research/ai-expectations-gap | 2026-10-16 | Survey expectations differ; expectations are not measured customer ROI. | Measure saved work and accepted outcomes before making commercial claims. |
| Anthropic: Demystifying evals for AI agents https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 2026-01-09 | Grade actual outcomes, inspect traces, repeat trials; combine code, human and calibrated model grading. | Failure-injection and real SQLite/API regression tests; retain independent review. |
| xAI: Grok 4.7 https://x.ai/news/grok-4-7 | 2026-09-21 | Vendor reports longer-horizon coding and knowledge work improvements. Self-checking is not an independent witness. | Optional future evaluated model; no paid API activated. |
| xAI: Grok Bot customer support https://x.ai/news/grok-bot-customer-support | 2026-09-22 | Describes internal-note/human-approval rollout, traces and task cost measurement. Commercial results are vendor-reported. | Candidate business workflow: human-reviewed evidence/research/support drafts. No automated sends, refunds or billing. |
| xAI: Grok Voice 3.0 https://x.ai/news/grok-voice-3 | 2026-10-14 | Recent voice product report, not an AUREX validation or research-paper replication. | Defer until core execution, demand and unit economics are established. |

The Anthropic research index https://www.anthropic.com/research also listed October 16 quantum-circuit and ECDSA-origin publications. These were screened by title only; their results were not evaluated or imported. Latest-by-date is not necessarily highest product value. xAI index: https://x.ai/news.

## Implemented defect repair

Owned files: aurex/fenced_worker.py, aurex/api.py, tests/test_worker_failure_persistence.py, this directory.

Before: an exception in the synchronous API offline probe returned HTTP 503 while leaving its durable job `running`. Idempotent replay returned this misleading state.

After: a conditional SQLite transaction records a generic EXECUTION_FAILURE, sets `failed`, and clears the lease only if state, worker ID, token, generation and unexpired deadline all match. Cancellation, replacement, expiry or a previously finalized result prevent the write. Storage errors return a separate redacted HTTP 503, never a claim of persisted failure. No synthetic evidence is created.

Compatibility: unchanged routes and JobResponse schema; existing `failed` state. No schema migration, provider change, new dependency, billing or deployment. Same idempotency key retrieves the same failed job; this does not implement automatic retries. A new authorized request requires a new key. Crash/expired-lease reaping remains a separate concern; this change does not promise full asynchronous recovery.

Rollback: revert this branch's repair commit before deployment; no data migration required. A rollback restores the original misleading-state defect.

## Commercial decision (engineering judgment, not validated demand)

Prioritize one productized, human-reviewed workflow: customer supplies a question and permitted sources; AUREX returns a source-linked brief, explicit uncertainty and an audit record. Prospective customers could be small technical teams needing repeatable research/support preparation. Customer discovery and willingness to pay remain NOT VERIFIED.

Measure repeat-task acceptance, citation correctness, review time, failure/abstention rate, retention and total cost per accepted deliverable (including failed attempts, reviewer time and hosting). Unknown costs stay unknown; local inference is not free infrastructure. Price and margin require these observations. Do not transfer xAI's reported costs or conversion rates into AUREX claims.

Order: (1) honest execution and failure records [implemented here for current probe]; (2) real authenticated website-to-Qwen workflow [NOT VERIFIED]; (3) limited human-reviewed pilot with consent and retention controls [PLANNED]; (4) measured pricing/quotas and payments after separate approval [NOT IMPLEMENTED].

The current canonical API only admits the bounded SQLite regression probe. This repair does not turn it into live Qwen execution, a customer-facing research service, multi-tenant authorization or a payment product. Production remains HOLD.

## Verification

Baseline full suite: 303 passed, 1 skipped, 2 failures caused by absent socksio while constructing mocked HTTP clients under the host SOCKS proxy. Tests: test_web_adapter.py::test_create_job_and_get_job and ::test_missing_token. No network request was needed for those mocked tests.

Red test: test_api_failure_is_durable_and_redacted failed with actual `running`, expected `failed`. Cancellation/replacement tests already passed and protect existing behavior.

Final commands and results are recorded in verification.txt. Offline suite unsets proxy variables only for this local mocked test process; this does not change runtime networking or application configuration. One existing Starlette/httpx deprecation warning remains. The skipped test is not PASS.

Independent review: separate read-only reviewer agent, same model family; not independent model-family or production attestation. See review.md for findings and scope.

Live Qwen, frontend-to-backend round trip, revenue, conversion, cost savings, production deployment: NOT VERIFIED / NOT RUN. No paid model calls, merges, DNS changes or production deployment performed.
