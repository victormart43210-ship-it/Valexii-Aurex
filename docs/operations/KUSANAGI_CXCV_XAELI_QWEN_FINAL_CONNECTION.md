# CXCV — XAELI/Qwen final connection evidence

## CP001: inspected and repaired existing PR156

Starting PR156 SHA: `758448b29be48f86cfcf5f634707f6afe0451346`.
Main SHA: `585023a09fdbff5ec2349a67cc50ef45a9b6f9fd`.
Branch: `work/kusanagi-qwen-private-bridge-20261027` (existing draft PR156).
Final source SHA is the containing Git commit, obtainable after remote fetch with `git rev-parse HEAD`; it cannot be embedded in its own content.

Changes: exact private URL allowlist; no redirects or ambient proxies; server-only AUREX_MODEL_API_KEY; authenticated bounded model discovery; configured model must match live inventory before generation; bounded JSON and answer validation; fixed prompt, no request body/query; staging-only flag; no retries; one generation per process at a time; sanitized failures; correlation ID, timestamp, measured latency; no database writes or authority promotion.

Dedicated tests import the exact `app.py` copied by this Railway root's Dockerfile and exercise the registered endpoint. Tests use mocked upstream HTTP; they are not live Qwen evidence.

Executed commands in isolated worktree:

```sh
python -m pytest tests/test_qwen_private_bridge.py -q
ruff check . --fix
mypy aurex
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy python -m pytest -q --tb=short
```

Results: dedicated 34 PASS; full Python 483 PASS, 2 skipped, 5 subtests PASS; Ruff initially reported misplaced imports, repaired; MyPy PASS across 78 canonical files. The legacy bridge is covered by endpoint tests and Ruff, not the `mypy aurex` scope. Existing Starlette/httpx deprecation warning remains. No frontend changes or Bun execution in this checkpoint.

## Railway read-only observations

Project `78095d3d-5911-41c8-aa3e-f9ebf5d81054`; staging `98c103eb-a1af-46b6-948e-19c80e4d720d`.
AUREX service `2b51dfe6-2175-4cb0-aac2-eb40ecbc3a1d`: deployment `6dcfb6e3-3ef7-4491-ad2a-69c11ee726cb` SUCCESS, deployed main SHA `585023a09fdbff5ec2349a67cc50ef45a9b6f9fd`. Source root `/integrations/kusanagi-xvi/backend`, Dockerfile copies only app.py. This deployed main does not include PR156.
Qwen service `707e28bb-554c-444c-b669-01ad61da2832`: deployment `7fe45d88-c560-4c18-b990-64f34376b8aa` SUCCESS. Runtime at 2026-10-27T06:54:55Z reports model loaded and listening on `http://[::]:8080`. No public domain or TCP proxy. Variable name LLAMA_ARG_API_KEY is present, but startup explicitly says no API key is set. Effective authentication is NOT VERIFIED; presence of a variable is insufficient.

AUREX variables list AUREX_MODEL_API_KEY and older Qwen/XAELI flags, but not AUREX_QWEN_STAGING_ENABLED or AUREX_QWEN_MODEL required by this probe. No values were displayed or changed. Do not assume keys match or infer actual API model ID from logs.

Staging API still mounts evidence volume `4d23b1e6-3625-4def-aa97-82e10859f04d` at `/data`; prior production isolation concern remains unresolved. No mutation, migration, production operation or inference request was performed in this checkpoint.

## Admission and next executable actions

1. Independently review exact candidate and verify its CI. Preserve no redirects/proxies and no arbitrary prompts.
2. Through authorized private container access, GET `/v1/models` with the configured model credential and test rejection without it. Record actual model ID and response, not an inferred repository name. Current connected Railway tools do not expose private exec; local Railway CLI is absent. Do not expose Qwen publicly as a workaround.
3. Establish staging storage isolation and reviewed exact-head deployment prerequisites. Only then deploy PR156 to staging, enable its explicit flag there, and set the model ID from live discovery. Do not merge main to trigger production.
4. Perform one authenticated empty-body POST `/v1/staging/qwen/synthetic-probe`; correlate actual Qwen logs and returned request ID. Record actual response and latency. Website work follows this gate; reuse existing owner adapter rather than inventing another UI.

Gate A private reachability: NOT VERIFIED. Gate B generation: NOT RUN. Gate C live AUREX result: NOT RUN. Gate D dedicated mocked security tests: PASS at this checkpoint. Gate E XAELI consumption: NOT RUN. Gate F live website: NOT RUN. Gate G no secret exposure: source-tested only, hosted NOT VERIFIED. Gate H production authority NONE: preserved in source and no production mutation.

Independent review: pending. Production release HOLD. External paid inference OFF. Existing source-only PR154 convergence work is separate and was not overwritten. Do not describe this report as completion of CXCV.

## CP002: independent repair and retest

Implementation remote SHA: `e5e5cf82dd9a6ec43b12d7bcdaf51217d1125bd4`. Equivalent local implementation commit: `ab527411450eafab841cdc027b9caf4e49f35366`.

Separate read-only reviewer `/root/cxcv_review` reproduced three defects: truncated HTTP response and deeply nested JSON returned 500; malformed non-ASCII bearer also returned 500. Repairs catch HTTP parser/depth exceptions and compare UTF-8 bearer bytes in constant time. Retest: 38 dedicated tests PASS; independent manual truncated response, bad status line and nested JSON each sanitized 502; malformed bearer denied 401. Full backend rerun: 487 PASS, 2 skipped, 5 subtests PASS. Ruff PASS. No source behavior changed after this retest.

Reviewed SHA-256 files:
- app.py: `9a7a7592820002fd3d65ffe8b984bd09975964291a2599ccc1eeb904d32ffef0`
- tests/test_qwen_private_bridge.py: `e82ac58ffc3ff57266508f9639617cf1647e56c8851847b380811e398ab22598`

This separate-agent review is source/mock evidence, not external certification or live validation. Socket timeouts are per operation, not an absolute wall-clock bound; concurrency lock is per process. Wider activation remains HOLD.

Exact implementation CI observed: runner smoke 40511472819 PASS; CI 40511472591, CLII 40511472654, CLIV 40511472687 IN PROGRESS. Do not mark required CI PASS until terminal results are read.

No Railway mutations were performed during CXCV. Existing private model loading is verified from logs; actual model ID, key enforcement and inference remain unverified. The requested live response has not been produced. Frontend changes are deliberately pending the first live backend gate and existing source reconciliation; no website publication occurred.
