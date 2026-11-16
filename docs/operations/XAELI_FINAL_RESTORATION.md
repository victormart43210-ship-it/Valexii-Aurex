# XAELI Final Restoration (Operation Kusanagi — Project Phoenix)

Base commit: `2af1a8f` (main). Production **HOLD**. Merge authority **NONE**. Paid inference **OFF**.
Machine-readable twin: [`XAELI_FINAL_RESTORATION.json`](XAELI_FINAL_RESTORATION.json).

## Finding

`POST /v1/xaeli-chat/ask` existed in **no** branch, tag or commit of this repository (searched all 1,501 commits, `git log --all -S"xaeli-chat"`, and every file). Only `/v1/xaeli-staging/explain` (synthetic, three fixed prompts) exists. The website's *in-repo* server function also targets only that synthetic route. The live gateway that calls `/xaeli-chat/ask` is not in this repository. The 404s are therefore explained: the route was never in the canonical backend (commit `de6a78d` is not resolvable here; PRs #157/#208 contain no such route).

## Recovered vs reconstructed

| Item | Status |
| --- | --- |
| Adapter, identity check, auth, zero-budget gate, unsafe-output filter, private-Qwen URL rules | **Recovered** (existing, reused unchanged) |
| `/v1/xaeli-staging/explain` | **Recovered**, untouched |
| `/v1/xaeli-chat/ask` route, request/response schema, grounding, rate/concurrency limits, body cap | **Reconstructed** (`aurex/xaeli_chat.py`, `aurex/xaeli_knowledge.py`). The original gateway contract is unavailable; the schema below is a proposal the gateway must match |
| Promotion gate `tools/verify_xaeli_chat_route.py` | **New** |

## Contract (verify against the live gateway before use)

`POST {AUREX_SERVICE_URL}/v1/xaeli-chat/ask` — server-to-server only.

Headers: `Authorization: Bearer $AUREX_SERVICE_TOKEN`, `x-aurex-operator-approval: advisory-chat`, `Content-Type: application/json`.
Body: `{"message": str(1..800), "history": [{"role": "user"|"assistant", "content": str(1..400)}] (max 4)}`; extra fields rejected; body ≤ 16 KiB (413).
Response 200: `state=HOLD`, `authority=NONE`, `independent_verification=NOT VERIFIED`, `mode`, `paid_inference=OFF`, `execution` PASS|FAIL, `generated_answer` (null unless PASS), `model{provider,model,runtime,quantization,identity_check}`, `grounding_version`, `diagnostic_ref`, `input_sha256`, `output_sha256`, `elapsed_ms`, `error_code`.
Status codes: 401 bad token · 403 no approval · 422 invalid · 413 too large · 429 rate/busy · 503 disabled/budget. Gateway timeout: **≥ 110 s** (adapter 90 s + 10 s model check). Show an answer only when `execution=="PASS"` and `generated_answer` is non-empty; otherwise show the unavailable state. Never retry automatically more than once.

## Railway `aurex-api` requirements (not applied; no Railway access)

`AUREX_XAELI_CHAT_ENABLED=1`, `AUREX_XAELI_OPERATOR_APPROVED=1`, `AUREX_SERVICE_TOKEN` (32+ chars), `AUREX_QWEN_BASE_URL=http://qwen-private-staging.railway.internal:8080/v1`, `AUREX_RAILWAY_PRIVATE_QWEN_ENABLED=1`, `AUREX_MODEL_API_KEY` (must equal the model server's key), `AUREX_BUDGET_USD=0`. The model service must serve id `qwen2.5-0.5b-instruct-q4_k_m` at `/v1/models`, bind a host reachable over Railway private networking (IPv6-capable `::`), port 8080. Context 2048 is tight: grounding ≈ 750 tokens plus bounded history plus 256 output tokens.

## Grounding gaps (owner action)

The repo has no approved public text for **CODEX 666, ARBATEL Seven, VCX2S**, and only one line for LUX. XAELI is instructed to say no approved description exists rather than invent one. Supply approved copy and update `aurex/xaeli_knowledge.py`.

## Regression protection

`tests/test_xaeli_chat.py` (31 collected cases, real local llama.cpp-protocol server driving the production adapter): route registration, response contract, auth/approval, disabled flags, zero budget, malformed/oversized input, timeout, transport/DNS/private-flag failures, wrong served model, empty/failed output, unsafe and guarantee output, prompt-injection fencing, rate limit, concurrency, log/secret hygiene, synthetic endpoint compatibility, DISPATER/AUREX surfaces.

Promotion gate (run before promoting any staging deployment):

```
python tools/verify_xaeli_chat_route.py https://<aurex-staging>            # route exists, anonymous rejected
AUREX_SERVICE_TOKEN=… python tools/verify_xaeli_chat_route.py https://<aurex-staging> --inference
```

A 404/405 or missing OpenAPI path exits non-zero.

## Results (actual)

- `pytest tests`: 971 passed, 1 skipped, **1 failed** — `test_forge_adversarial.py::test_execute_blocks_unapproved_data_wrong_tenant_and_low_storage`; it fails identically on unmodified `main` (pre-existing, unrelated, not touched).
- `tests/test_xaeli_chat.py`: 31 passed.
- `ruff check aurex tests tools/verify_xaeli_chat_route.py`: pass.
- `mypy aurex aurex_foundation`: 1 pre-existing error (`torch` stub missing in `aurex/ox/forge.py`); no new errors.
- Frontend Bun tests/build, Docker build: **NOT RUN** (no bun/node_modules; website and Dockerfile unchanged).
- Mocked/local-server tests do **not** establish live private-Qwen inference.

## Not done / blockers

1. Railway deployment `6ad48a93-…` was not inspected (no access); nothing deployed.
2. Lovable gateway not inspected; it must be aligned to the contract above (minimal patch: path, two headers, body/response mapping, timeout). No Lovable credits spent.
3. Live acceptance on https://valexii.com/xaeli with the eight questions: **NOT RUN**. Final acceptance requires it.
4. Live Qwen identity, DNS and health: unverified.
5. Independent verification and merge/release: pending owner; this PR must not be self-certified.

## Rollback

Revert the PR; `/v1/xaeli-chat/*` disappears and no other route changes (`aurex/api.py` adds one router and one path-scoped middleware).
