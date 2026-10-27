# Private Qwen runtime repair

Owner instruction: “Fix it.” Scope: existing private staging model service only.
Branch: `work/kusanagi-clxxix-sovereign-unification`, PR #154.
Previous remotely verified checkpoint: `30eac28a1ccc565809444dce4190d8c97ec4887a`.
The containing Git commit is the recovery checkpoint; obtain its exact SHA with `git rev-parse HEAD` after fetching the remote branch.

## Target and diagnosis

- Project: `78095d3d-5911-41c8-aa3e-f9ebf5d81054`
- Environment: `98c103eb-a1af-46b6-948e-19c80e4d720d` (`aurex-staging`)
- Service: `707e28bb-554c-444c-b669-01ad61da2832` (`qwen-private-staging`)
- Original deployment: `b5d29764-8194-4a7a-be36-5e9884ece69b`

Original deployment reported SUCCESS but runtime logs showed router mode with zero models. Configured CLI model arguments alone had not established model loading. The exact cause of the earlier model-selection behavior is not established.

## Applied configuration

Existing image `ghcr.io/ggml-org/llama.cpp:server`, CPU 1, memory 2,000,000,000 bytes, one replica and `/health` remain unchanged. No volume, domain or TCP proxy was added.

Eight nonsecret environment variables were set:

```text
LLAMA_ARG_MODEL_URL=https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf
LLAMA_ARG_ALIAS=qwen2.5-0.5b-instruct-q4_k_m
LLAMA_ARG_CTX_SIZE=2048
LLAMA_ARG_N_PARALLEL=1
LLAMA_ARG_N_PREDICT=128
LLAMA_ARG_THREADS=1
LLAMA_ARG_PORT=8080
LLAMA_ARG_HOST=::
```

Official configuration reference: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

First repair deployment `f9043881-7788-47c8-b5b8-b9fca0fb8ecd` reached SUCCESS. Runtime evidence:

```text
2026-10-27T06:28:31.656594707Z loading model 'bartowski/Qwen2.5-0.5B-Instruct-GGUF'
2026-10-27T06:28:49.429633276Z llama threadpool init, n_threads = 1
2026-10-27T06:28:49.429639988Z initializing, n_slots = 1, n_ctx_slot = 2048
2026-10-27T06:28:49.429646842Z model loaded
```

Logs established that command-line `--host 0.0.0.0` overrode the environment host. Changed only that command argument to `--host ::`, then redeployed the existing build:

```text
/app/llama-server --hf-repo bartowski/Qwen2.5-0.5B-Instruct-GGUF --hf-file Qwen2.5-0.5B-Instruct-Q4_K_M.gguf --host :: --port 8080 --ctx-size 2048 --parallel 1
```

Latest deployment: `8239c124-c77e-47fb-aa0e-425bc28bf1a3`. Terminal verification is recorded below.

## Remaining verification and boundaries

A generated synthetic response is NOT RUN. The connected Railway tools can read logs and configure this service but cannot execute a private HTTP request inside its container. No public endpoint may be created as a workaround.

From an authorized private container shell, inspect `/v1/models`, then submit this bounded fictional request to the local server:

```sh
curl --noproxy '*' --fail-with-body --max-time 60 \
  -H 'Content-Type: application/json' \
  --data '{"model":"qwen2.5-0.5b-instruct-q4_k_m","messages":[{"role":"user","content":"Synthetic connectivity check. Reply with READY."}],"max_tokens":16,"temperature":0,"stream":false}' \
  'http://127.0.0.1:8080/v1/chat/completions'
```

Capture the actual response and deployment ID; successful loading does not establish successful generation. Then test authenticated AUREX transport separately. The canonical ask endpoint remains deliberately denied; do not bypass its authorization gate. XAELI live integration remains NOT VERIFIED.

The model server reports no API key and permissive CORS. It remains private without a public domain or TCP proxy; application-layer authentication and least-privilege service access remain prerequisites before wider integration. Private transport alone is not tenant authorization. Model and image immutable digests remain NOT VERIFIED. The image logs a control-token metadata warning; no successful generation claim is made.

No production service, credentials, database, volume or public website was changed. No paid-provider request was executed. Existing Railway compute remains in use; this is not a claim of zero hosting cost. No new resource or larger resource allocation was requested.

## Rollback

The first repaired build `f9043881-7788-47c8-b5b8-b9fca0fb8ecd` is the model-loaded reference. To revert only the binding change, restore `--host 0.0.0.0` and redeploy that build, retaining the model variables; this may not support private IPv6 clients. To restore the full original configuration, remove the eight added variables, restore the original host and redeploy the prior image/build. That original state had zero models and is not a functional fallback. Redeploying a build alone may retain current service variables, so verify configuration and logs after any rollback.

Production release: HOLD. Independent live verification: NOT VERIFIED.

## Final observed runtime

Deployment `8239c124-c77e-47fb-aa0e-425bc28bf1a3`: SUCCESS.

```text
2026-10-27T06:31:52.061183649Z model loaded
2026-10-27T06:31:52.061189318Z listening on http://0.0.0.0:8080
```

Model loading: PASS, based on runtime logs. Private IPv6 binding: NOT VERIFIED. The saved command was updated to `--host ::`, but this redeployment still logs IPv4. It is not established whether build redeployment retained an older runtime command or the image overrides it. Do not claim this change is active merely from configuration readback. Next inspect actual process arguments and sockets through authorized container access, reconcile the effective command, and submit the bounded localhost prompt above. Generated response: NOT RUN. Website-to-model integration: NOT VERIFIED. No regression suite was rerun for these infrastructure-only settings; prior source test results remain associated with their recorded source checkpoint.
