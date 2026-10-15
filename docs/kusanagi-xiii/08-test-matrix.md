# Test matrix

| Stage | Result | Evidence / limits |
|---|---|---|
| Backend baseline suite | PASS | baseline-pytest.txt: 124 passed, 1 skipped |
| Baseline Ruff / mypy | PASS | baseline-ruff.txt / baseline-mypy.txt |
| Adversarial baseline | FAIL | adversarial-before.txt: 11 failures reproduced |
| Repaired backend suite | PASS | final-pytest.txt: 138 passed, 1 skipped |
| Repaired Ruff / strict mypy | PASS | final logs, 40 checked source files |
| Wheel build | PASS | wheel-build.txt; no reproducible-byte claim |
| Dependency integrity | PARTIAL | python-environment.txt; broad dependency ranges, no project lockfile |
| Original-SHA GitHub CI | PASS | runs 38510700399 and 38484346784 report success at f8df262; raw logs not independently audited |
| Repair-SHA hosted CI | NOT VERIFIED | check PR workflow after upload |
| Bearer negative tests | PASS | existing auth tests + authenticated health regression |
| Input/body caps | PASS | nested/oversized params and actual oversized request |
| No-worker evidence suppression | PASS | no new jobs/evidence on rejected dispatch |
| Terminal-state integrity | PASS | restart rejected, stored result preserved |
| Ed25519 trust/timestamp | PASS | unknown/revoked key, stale/future timestamp, timestamp tamper cases; not operational key custody |
| Full website build/test suite | NOT RUN | upstream/source checkout not established |
| Website adapter patch | PASS | 3 focused tests in separate private patch packet |
| Cross-repository contract | PARTIAL | real TestClient payloads through website functions, mocked HTTP transport |
| Signed-out website console | PASS | Access denied observed; no authenticated test |
| Mobile / accessibility | NOT RUN | no UI modified |
| Staging pipeline | BLOCKED | no configured host/session |
| Live Linux Qwen | BLOCKED | local host/source unavailable |
| Complete real inference pipeline | BLOCKED | no real worker or traceable website response |
| Independent review of new repairs | BLOCKED | Astral runtime preflight unavailable |

Additional unexecuted gates: concurrent idempotency races, cross-user job reads/cancel, gateway replay, revoked session access, stale evidence qualification through UI, DNS rebinding, process crash recovery and inference outage. These are not PASS.

Reproduce backend checks at the PR source using Python >=3.12:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/mypy aurex --strict
.venv/bin/pip wheel --no-deps --wheel-dir /tmp/aurex-wheel .
```

Optional training smoke skipped because optional dependencies were absent. A Starlette TestClient deprecation warning remains. Test suite counts are not benchmark or native-model validation.
