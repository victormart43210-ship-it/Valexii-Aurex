# VALEXII-AUREX

**External evidence, challenge, and evaluation engine for governed AI systems.**

AUREX is an open-source project for independently challenging claims, normalizing evidence, running reproducible evaluations, and returning machine-readable verification reports.

> **Core law:** the system may never be its own sole witness.

## Boundary

AUREX is a **witness, not an authority**. It may challenge, score, reproduce, or dispute a claim, but it does not grant security authority or control BCXMET/VALEXII runtime decisions.

This public repository intentionally excludes proprietary BCXMET detection logic, private orchestration, credentials, production telemetry, and patent-sensitive implementation details.

## Initial architecture

- `protocol/` — public request/result contracts
- `evidence/` — evidence envelopes and provenance
- `challengers/` — independent challenge interfaces
- `adapters/` — model/tool adapters
- `evals/` — reproducible evaluation harnesses
- `benchmarks/` — benchmark manifests and runners
- `api/` — external challenge API
- `cli/` — local command-line client
- `tests/` — contract and adversarial tests
- `docs/` — threat model, governance, integration guidance

## Canonical challenge result

AUREX reports one of:

- `SUPPORTED`
- `CONTESTED`
- `INSUFFICIENT`
- `STALE`
- `HOLD`

No result is silently promoted to product authority.

## Planned stack

Python + typed schemas + JSON Schema interoperability, with a small HTTP API and CLI. Model providers remain adapters so evaluations can compare identical tasks across providers and local models without coupling the protocol to one vendor.

## Independent open-source witness bridges (proposed)

Experimental adapters under `aurex/adapters/oss_witnesses.py` and the
local-only `python -m aurex.adapters.oss_cli` tool can ingest MobSF reports
with exact APK SHA-256 qualification, calculate Astronomy Engine lunar context,
record optional OpenTelemetry spans, and frame local MADLAD output as an
unverified translation hypothesis. All remain demote-only external witnesses.

See [open-source witness bridge](docs/open-source-witness-bridge.md) for
execution instructions, licenses, risk controls and CI status. **This work is
not a BCXMET production integration, release PASS or verified decipherment.**

## Evaluation doctrine

Benchmark claims remain **WITHHELD** until a reproducible run produces evidence. Projected uplift is never reported as measured performance.

## Status

Bootstrap / pre-alpha. Interfaces are expected to change until the v0 protocol is frozen.

## Security

Do not submit secrets, private user data, production credentials, or proprietary BCXMET internals to public fixtures or issues. See `SECURITY.md`.
