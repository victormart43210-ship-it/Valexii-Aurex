# KUSANAGI CXXVII — remote recovery candidate and source custody

**Status: CANDIDATE ONLY · CI NOT YET VERIFIED · STAGING NOT DEPLOYED · AUTHORITY NONE · RELEASE HOLD**

This new GitHub branch is an independently **reconstructed source candidate**, not the owner's claimed local Jules head. Do **not** identify this as the exact CXXVII Final Head until Jules supplies a full immutable commit SHA and its source bytes are compared. The originally reported local branch `work/kusanagi-cxxvii-jules-pipeline-closure` and CXXIV source SHA `1dee5cd57297eefb3c89fb4581cbb477e7707bc6` could not be resolved in the connected GitHub repository on October 22, 2026.

## Exact source map
- Protected main baseline: `df0654390049118a142ec3b3356f0f40b4789fe4`.
- Candidate parent: CXXVI draft #109 `155ce1e969ae58df6b5400d38e5db5c1f840a047` (canonical receipt endpoint and typed client preserved).
- Financial modules, fictional fixtures and review tests: #99 `8e859304d14c6aaa2cd4ed84d2e9db93fe9700b9`.
- Fenced terminal-failure worker, field-reconciliation module and testing: #104 `3b3d1de63f764a777758f709130a91324bcd06ca`; its fixed-fixture job code is selectively integrated into CXXVI's `create_job_endpoint` while retaining CXXVI's authenticated receipt route. No wholesale replacement of CXXVI schemas.
- Document-analysis *disabled-by-default candidate* source: #106 `17fdd82718178544146fe7e8870b0d6eb1d56f1a`. It is derived from the older legacy bridge and is **NOT reconciled with the deployed CXXVIII Unix worker**.
- NVIDIA financial research *offline only*: #107 `b2960cfd0911c21bc96798bead4f60f7808a3907`.
- Website contract helpers and tests: #108 `eb707fd0ad6729768451be2256160369c31f41a7`, excluding its older overlapping schemas, OpenAPI and client which remain from #109.

## Specific proof gates, all initially HOLD
1. Confirm exact-head GitHub CI results, not source PR historical results; run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q`, `ruff check .`, `mypy`, `cd website && bun test && bun run build`, plus Docker smoke. Retain intermediate failures.
2. Test two opt-in synthetic probes: `sqlite_roundtrip_v1` and `synthetic_field_audit_v1`; synthetic field path requires `AUREX_ENABLE_OFFLINE_LAB=1`, `AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT=1`, valid Bearer, no external input, fixed $0 job. Confirm bad/missing idempotency, lease failure and digest-corruption hold.
3. Independently re-run 100 *fictional* scorer cases and adversarial tests. An internally generated fixture is not an independent effectiveness benchmark, real customer audit, fraud verdict or certification.
4. Review CXXVI–CXXVIII overlapping `integrations/kusanagi-xvi/backend/app.py`, Docker, quotas, service-to-service auth, nonroot /data, SQLite schema migration and restart behavior before any staging rollout. The live staging branch is a **different** SHA. Never overwrite it blindly.
5. Verify staging and production data-volume independence: Railway currently displays the same volume ID in both environments. Treat isolation as NOT VERIFIED until a provider-specific test proves separation.
6. Only after independent source/CI/security review and owner-controlled staging approval, test a single synthetic website → Railway → worker → evidence → receipt → website loop. NVIDIA, Qwen, Ollama paid inference, payments, real financial data, production and automatic merging remain disabled.

**Canonical policy:** Evidence → Qualification → Reality → Authority → Effect; no system may be its own sole witness. Unknown ≠ healthy. Final release HOLD.
