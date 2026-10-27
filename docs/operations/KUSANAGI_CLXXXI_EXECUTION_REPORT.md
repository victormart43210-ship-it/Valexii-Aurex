# CLXXXI — NVIDIA/XAELI source convergence

Main refreshed: 551625e5be41ef6fd16e70e7a72404400032f4bc. Continues existing PR150 branch work/kusanagi-clxxxiv-inference-guard; no duplicate PR or repository. Parent durable CLXXXIV checkpoint 5df3290dea3affa20fc2a3fc51eb110c00dcc04f remains preserved.

## Discovery

Lovable project 811ffc43-2c8b-4c88-ab4c-4de668d089cb at d11d8a6a3e2f6b43860092988bb198271ffe8308 has owner-only NVIDIA console and server RPCs calling /v1/agent/status and /v1/agent/ask. These routes were absent from canonical main (four regression tests reproduced 404). Its existing gate conflates missing website service configuration with inference enablement and permits ask POST when flags and chatConfigured are true, without durable monetary admission. Actual hosted variable values were not inspected; the exact live Not configured cause remains NOT VERIFIED.

Current main website copy lacks these newer owner-console files. The server helper is reused from the pinned Lovable source and repaired in canonical repository as a narrow sync candidate; its RPC/component remain on Lovable and have NOT been overwritten or published.

Existing NVIDIA branches: zero-spend gate af7a5a05037169a98e060176833e2490e7f6eaed adds an unmounted probe; owner NIM candidate feb27f28e5f569eaee30b855ef3b133a8eba8cd6 adds an unmounted live urllib probe using a different secret name without durable accounting. Neither imported. Existing draft PR150 remote denial remains authoritative for this candidate.

Railway reinspection still selects main and /integrations/kusanagi-xvi/backend, no staged changes. Required NVIDIA variable names exist, not proof of valid values. Earlier deployment metadata: 8fe3f398-4e6f-4bfa-8c79-da1b84ccefb4 SUCCESS; reported deployed f2db438f0020dbd455bcb5c7b21b7352d133bf2c not independently refreshed here. Volume isolation remains unresolved; no deploy/write.

## Changes and actual validation

- Canonical authenticated /v1/agent/status returns disabled-by-policy, missing credential/model categories, zero budget and NOT_VERIFIED. No secret/model values or network call.
- /v1/agent/ask authenticates then always returns 403 REMOTE_INFERENCE_DISABLED. No body parsing or provider dispatch.
- Website helper preserves owner boundary, allows read-only diagnostics independently of enable flags, reports auth denial, rejects decoded credential echoes, and always refuses ask without network.
- Backend RED: four missing-route failures. GREEN: four passed. Full backend: 454 passed, 1 skipped, one existing Starlette warning; Ruff PASS; MyPy PASS 79 files.
- Website RED: paid POST attempted under flags; diagnostics hidden behind enablement; later auth error collapsed into unavailable. GREEN: four convergence tests pass. Full Vitest 152 passed, 2 failed (existing consolidated-editorial/domain-directions copy assertions).
- TypeScript FAIL on existing contact-route search/optional-property errors. A new test-union access error was corrected. No claim of all frontend checks passing.

## Remaining

No live provider call, mock model success claim, ledger write, stored inference receipt or cross-tenant integration claim. Existing deterministic DISPATER tests pass without NVIDIA. CLXXIX/CLXXX reported 555-test baseline is not the current main suite and was not adopted. OpenShell runtime NOT VERIFIED; PR145 policy flaw remains recorded in prior recovery.

Next: independently review PR150, reconcile current Lovable helper and compatible RPC return types in an authorized preview without publishing, resolve frontend baseline failures, verify staging volume isolation/deployment root and exact SHA. Any eventual paid path needs durable accounting before separate operator authorization. No Copilot credits used; no paid services, production changes, secret edits or merges.
