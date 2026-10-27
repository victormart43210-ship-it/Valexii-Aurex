# Onyx bridge verification — 2026-10-26

Executor: ChatGPT Work, local Python 3.12.14. Independent reviewer: NOT RUN.
Implementation changes through CP004 are identified by its containing Git commit; consult RECOVERY.json and remote branch history. CP003 source was 0fbf956df03e0b702713291eb817911f2d96dd51.

## Actual execution

- RED: initial missing adapter/route tests failed before implementation.
- Initial GREEN: 26 contract tests passed.
- Expanded RED: 2 failures (reflected service credential and unbounded demo body), 37 passed.
- Expanded GREEN: 39 adapter/security tests passed after repairs.
- `python -m ruff check .`: PASS.
- `python -m mypy aurex`: PASS, 79 source files.
- `env -u ALL_PROXY -u HTTPS_PROXY -u HTTP_PROXY -u all_proxy -u https_proxy -u http_proxy python -m pytest -q --tb=short`: 475 passed, 3 skipped, one existing Starlette warning.
- Real local Uvicorn process, ephemeral loopback port and synthetic bearer: missing bearer 401, authenticated demo 200, six candidates, no admitted evidence. Sanitized response: ONYX_SYNTHETIC_HTTP.json. No live Onyx service was contacted.
- Optional live test: NOT RUN, skipped without explicitly admitted private synthetic environment.

Coverage includes malformed/oversized requests and provider responses, missing metadata, stale/future timestamps, unsafe source URLs, bearer rejection, cross-principal/tenant rejection before network, disabled admission gates, duplicate JSON keys, timeout/unavailability, duplicate results/replay, inert prompt injection, secret reflection, content and metadata tampering, and fixed advisory authority. Mock transport validates the pinned upstream wire schema; it does not prove live interoperability.

## GitHub CP003 observations

Exact SHA: 0fbf956df03e0b702713291eb817911f2d96dd51.
Independent-runner smoke and canonical Railway Docker checks passed. This is automated CI, not independent financial or security certification.
CI and CLIV failed during collection: tests/test_dispater_proof.py cannot import dispater_proof using the pytest executable. The existing setuptools package selection excludes that package; module invocation includes the repository root.
CLII Python tests passed; website Vitest reported 148 passed and 2 failed. Existing assertions expect `Private repositories exist, as reported by the project owner` and `Intelligence Beneath the Surface` in website/src/routes/dispater.tsx. Onyx changes do not modify that website source or those assertions.
The added Onyx workflow runs the complete Python suite through `python -m pytest`; no existing failing checks were disabled or marked passing.

## Limits and release

No persistence or receipt was fabricated: retrieval candidates remain HOLD and are never written into the evidence ledger. Deterministic reconciliation uses a separate server-owned structured fixture, not retrieved prose. Existing owner bearer is not proof of multi-tenant authorization. Real Onyx ACL enforcement, network isolation, cost controls, hardware capacity, restart behavior and website-to-Onyx execution are NOT VERIFIED. Live endpoint is not exposed. Ordinary demo records are not described as immutable.

The adapter socket timeout is not a total wall-clock deadline. Before live admission, add a bounded outer execution deadline and concurrency/rate controls appropriate to the actual deployment. Confirm provider egress and inference are local-only; skip_query_expansion alone does not establish zero cost.

No production systems, credentials or infrastructure were modified. Production authority NONE; release HOLD.
