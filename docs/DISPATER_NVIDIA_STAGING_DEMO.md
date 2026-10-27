# DISPATER / NVIDIA zero-spend demonstration

This is a LOCAL SOURCE TEST, not live NVIDIA or deployed staging verification.

```sh
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_xaeli_nvidia_contract.py tests/test_remote_inference_hold.py tests/test_model_execution.py tests/test_dispater_demo.py tests/test_dispater_demo_server.py
cd website
npx vitest run src/lib/aurex-nvidia-convergence.test.ts
```

Expected: missing bearer rejected; authenticated status explicitly DISABLED_BY_POLICY; ask denied even with billing flags; no provider HTTP request; owner-only website diagnostics; deterministic towing findings and review acknowledgment continue with NVIDIA NOT RUN and financial authority NONE.

Existing synthetic input: examples/dispater_towing_synthetic.json. Prior actual deterministic output: docs/verification/CLXXXIV_SYNTHETIC_TOWING_OUTPUT.json. No inference receipt or provider evidence is invented. A full website → deployed AUREX → qualified ledger workflow remains blocked on source convergence, preview sync and storage isolation. Do not send a test POST to Railway while that isolation remains unresolved.
