# AUREX/OX — Open-source contract convergence (2026-10-22)

**Status:** source-only candidate; **Authority NONE · Verification NOT VERIFIED · Release HOLD**.

## Existing assets, not replacements

- Frontend: existing Lovable **Valexii Ai** project; keep TanStack server-only service bearer, Zod response validation, raw-byte limits, explicit HTTP redirect refusal and separate owner-only staging proof.
- Backend: **same** `victormart43210-ship-it/Valexii-Aurex` repository, Railway service `aurex-api`, production and isolated `aurex-staging` environment. No new service/repo needed.
- Website OpenAPI: `docs/aurex-api/openapi.yaml` currently lives in the Lovable project. `openapi-typescript` is installed **as a frontend build-only tool**; generated types do *not* grant authority or replace Zod.
- The existing offline SQLite worker and evidence ledger remain the truth of recorded events, not model efficacy.

## This bundle's concrete addition

`tools/aurex_bridge_probe.py` compares the **five fixed, authenticated GET** transport endpoints in staging with the public website's read-only handshaking surface. **Default is offline.** Execution requires a second explicit `--approve-staging` flag and an exact allowlisted HTTPS staging hostname, with no redirect and a 256-KiB response cap per call. It does not submit jobs, query models or leak records. It reports *hashes*, shape checks and a permanent HOLD status. It is not an exhaustive OpenAPI schema validator or security audit.

```bash
# Stage locally: NO network
python3 tools/aurex_bridge_probe.py

# OPT-IN staging-only, using existing backend token in environment.
# Do not paste real tokens into the chat, command history, or frontend bundle.
export AUREX_STAGING_URL=https://aurex-api-aurex-staging.up.railway.app
# AUREX_SERVICE_TOKEN must be securely set for this command.
python3 tools/aurex_bridge_probe.py --execute --approve-staging

# Offline regression tests, no server or provider required
python3 -m unittest discover -s tests -p test_aurex_bridge_probe.py -v
```

## Sequencing after source-only admission

1. Lock one versioned FastAPI ↔ Lovable OpenAPI contract; add backend snapshot export and compare generated frontend types. The frontend's current hand-written YAML is a **draft mirror**, not authoritative direct export yet. Use `oasdiff` in CI for breaking-change review.
2. Add opt-in OpenTelemetry FastAPI traces on Railway with redaction, short retention, and correlation IDs. Never emit bearer tokens, customer documents, model prompts, financial values or unredacted source excerpts.
3. For larger document work, evaluate open-source Docling or MarkItDown in a bounded isolated Linux worker. Keep original SHA-256, page offsets and exact/format-normalized quotation matches. These *do not* establish factual validity; Challenger and CUSTOS remain separate.
4. Keep existing SQLite and Unix worker until measured scaling justifies introducing Dramatiq/Redis. Do **not** add queue, database, gateway, vector DB or paid observability service without real need.
5. Evaluate OPA only for future centralized policy decisions, never as a substitute for the canonical AUREX authority gate. Defer LiteLLM; its March 2026 supply-chain incident justifies additional trust and dependency verification, and direct NVIDIA NIM wire provenance is still provisional.

## Deployment rules

- Never push commits to the Railway auto-deploy staging or production source branch without an explicit review gate. Integrate through a draft PR in the **existing repository**.
- No Railway variables, DNS, secrets, frontend publication, paid inference, model-efficacy claims or authorization changes in this batch.
- CI regression checks are not production verification. All backend versions, receipts and hashes must be compared at exact SHAs before release.
- Revoke any previously exposed NVIDIA token and replace securely prior to future remote AI work.