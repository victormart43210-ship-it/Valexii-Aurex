# KUSANAGI XCIV — Qwen + AUREX full-stack staging (source-only)

Status: **DRAFT / NOT MERGED / NOT DEPLOYED / LOCAL QWEN INFERENCE NOT VERIFIED**. The purpose of this slice is safe, reproducible local readiness checks and a truthful owner-only frontend staging panel. No model downloads, API spending, public inference routes, frontend publication, Railway changes, Cloudflare changes, or merges.

## Canonical source of truth

- Backend repository: `victormart43210-ship-it/Valexii-Aurex`, main.
- This proposal is a **single isolated branch** off canonical main, not a competing AUREX backend.
- Website staging mirror lives in this repo's `website/` tree. It is **not automatically synchronized with the live Lovable editor**. Only sync changes after comparing live Lovable source and securing an owner-approved website review. Lovable credits were exhausted during the previous frontend transport security implementation; do not claim this repo's frontend changes are on valexii.com.
- Existing private development gateway from draft PR #81 remains a separate, unmerged proposal. This PR does not start or expose it.
- Production Railway still uses the older read-only bridge unless independently proven otherwise.

## Local machine prerequisites

1. Install Ubuntu 24.04 on Windows 11 using WSL2 (`wsl --install -d Ubuntu-24.04`) or use a verified existing Linux installation. Do **not** erase Windows. Reboot if prompted.
2. Install Python 3.12+, Git, and packages declared in `pyproject.toml`; no paid provider is required.
3. In a checkout of THIS BRANCH, create/activate a virtualenv and run:

       python -m pip install -e '.[dev]'
       PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_qwen_readiness.py tests/test_qwen_proxy_boundary.py tests/test_local_inference.py
       python -m compileall -q aurex workstation tests
       ruff check workstation/qwen_readiness.py tests/test_qwen_readiness.py tests/test_qwen_proxy_boundary.py aurex/local_inference.py
       mypy --strict workstation/qwen_readiness.py

   All above are instructions for the owner workstation; the CI and full-repository results **have not been observed on this exact GitHub commit**.

## Qwen startup — **no automatic download or upload**

A Qwen2.5 0.5B quantized GGUF file was previously reported on the owner's local machine. Its actual filesystem path, checksum, and successful server startup are NOT VERIFIED in this repository. Never include the path, weights, or model prompt in public website telemetry.

For an **already installed** llama.cpp binary, use the existing local file manually, in a separate terminal:

    llama-server -m '/absolute/path/to/your-existing-Qwen.gguf' --host 127.0.0.1 --port 8080 -c 2048 -t 4 -ngl 0

Do not run if the file or server binary is missing. Never bind 0.0.0.0 or tunnel port 8080. Confirm the exact registered identifier privately from the local server's `/v1/models` reply, then run:

    python -m workstation.qwen_readiness --backend llama.cpp --model '<exact-loaded-model-id>' --check

The `--check` operation performs **GET to numeric loopback only** and verifies only that the local server advertises the selected identifier. It returns `MODEL_ADVERTISED_UNVERIFIED`, *not* "Qwen inference working."

Only if the operator explicitly wants a synthetic local inference:

    python -m workstation.qwen_readiness --backend llama.cpp --model '<exact-loaded-model-id>' --infer --approve-local

This may take time on a CPU-only Intel desktop. No response text is printed: only status, response character count, and SHA-256 of output. A SHA-256 digest is not authenticity or independent verification. Status `LOCAL_INFERENCE_OBSERVED_UNVERIFIED` records an observation, NOT a validated benchmark, security decision, or production service.

If Ollama is installed with a **locally already-loaded** Qwen model, use `--backend ollama --model '<exact-local-model-id>' --check`; by default the CLI checks `127.0.0.1:11434/api/tags`. The CLI does not pull a model or start Ollama. For inference add `--infer --approve-local`.

## Backend ↔ frontend boundary

The new `website/src/components/aurex-qwen-readiness.tsx` is **information-only**, mounted within an existing owner-authenticated control route in the **checked-in website mirror**. The view does not request browser access to localhost, display prompt/model file paths, send credentials, or invoke backend inference.

This is deliberately **not** a functioning chat feature or production AUREX job. The public API's five authenticated read-only endpoints remain unchanged:
`GET /v1/health`, `GET /v1/capabilities`, `GET /v1/evidence`, `GET /v1/budgets`, `GET /v1/jobs`.
No inference POST route has been created, and no runtime callback to the new CLI has been added to the public website.

Before promoting frontend changes, compare this website mirror against current Lovable SHA, reapply only the reviewed component in the true existing Lovable project, rerun relevant Vitest/build/typecheck and owner auth checks, and keep all production secrets server-side. Existing Lovable transport hardening change `b1d00f6bfac7e5abe38fd1de0ca9378f680fc6e7` remains separate and its previously reported 1 failing synthetic response fixture must be corrected before admission.

## Security/rollback checks

- NEGATIVE: no server ⇒ SERVER_UNAVAILABLE; model name absent ⇒ MODEL_NOT_LISTED; malformed or >64KiB response ⇒ INVALID_MODEL_LIST; missing --approve-local ⇒ exit before local inference.
- POSITIVE: synthetic model-list fixture ⇒ advertised only, not execution. Mocked one-shot inference ⇒ LOCAL_INFERENCE_OBSERVED_UNVERIFIED with no raw output.
- No inherited HTTP(S) proxy route is permitted for local inference; `ProxyHandler({})` is explicit.
- No Cloudflare Tunnel to Ollama or llama.cpp. For a future remote workstation dashboard, Access owner-only authorization MUST precede any tunnel, gateway remains read-only and separate.
- Stop local model server manually with Ctrl+C; revert this draft PR to remove code if review fails. Leave Railway/Lovable/Cloudflare production unchanged.
- Full suite, full Ruff/Mypy, actual local model inference, owner website build and published browser path are **NOT RUN / NOT VERIFIED** until independent execution.

Governance: Evidence → Qualification → Reality → Authority → Effect. Missing/failed observations HOLD. No self-witness. Default external spend $0. ORB MOTION AUTHORITY = NONE.
