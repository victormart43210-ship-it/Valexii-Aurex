# Contributing to VALEXII-AUREX

Thank you for helping test an open, independent evidence and challenge engine.

## Boundaries first

AUREX is a witness, **never** the product authority. Contributions must preserve the rule: **the system may never be its own sole witness**. Do not connect public challenge results to proprietary BCXMET runtime authority or upload private BCXMET implementations.

Do not submit secrets, API keys, private datasets, user information, unlicensed model weights, production telemetry, or non-public customer artifacts to issues, fixtures, pull requests, or CI logs. Use minimal synthetic fixtures.

## Contribute safely

1. Fork the repository, create a branch, and keep changes focused.
2. Set up Python 3.12 or newer. Install the development extras with `python -m pip install -e ".[dev]"`.
3. Run `ruff check .`, `mypy aurex`, and `pytest -q`.
4. Document affected interfaces and the threat model. Add adversarial tests for new trust-boundary behavior.
5. Open a pull request. A maintainer reviews before any merge. No unapproved deployments, publishing, model downloads, or paid API use.

Use GitHub issue forms for reproductions and benchmark evidence. File vulnerabilities using [SECURITY.md](SECURITY.md), not a public issue containing exploit details or credentials.

## Evidence rules

Separate tool execution from independent verification. For reported benchmark results, include: exact code commit, dataset identity and licensed provenance, model/backend version, system hardware, seeds, prompts/configuration, metric definitions, raw results or reproducible artifacts, evaluator independence, contamination controls, and known limitations.

Valid challenge statuses are `SUPPORTED`, `CONTESTED`, `INSUFFICIENT`, `STALE`, and `HOLD`. Missing or infrastructure-failed checks are not PASS. Never invent measured uplift, accuracy, security coverage, or runs.

## Changes that need extra review

Protocol/schema changes, challenge authority boundaries, evidence provenance or freshness, secret handling, untrusted-data execution, outbound network operations, CI workflow permissions, and dependency additions require explicit adversarial review.

See [the CUSTOS test matrix](docs/CUSTOS_TEST_MATRIX.md) before proposing new tools or benchmarks.

## License note

Project metadata declares Apache-2.0. Maintainers should verify the repository includes the authoritative license notice and any required third-party notices before distributing packaged binaries or accepting contributions requiring special licensing.
