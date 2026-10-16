# OPERATION KUSANAGI LXVII — Railway × Python 3.15 × LLM Training Research

**Scope:** research-driven additions to the one canonical AUREX repository. **Proposed / draft only.**  
**Main-base exact commit:** `c41675fc0830be5f1b66e2f75782b139668b6cb3` (2026-10-16).  
**Research as of:** 2026-10-16. All sources are upstream vendor or primary research/documentation; claims are not external AUREX benchmarks.  
**Release:** HOLD. **No Railway/Cloud deployment, feature-flag change, model training, production data collection, Lovable credits or paid GPUs.**

## Current Railway baseline (read-only verified, do not confuse staged with live)

- Project `VALEXII-AUREX`; service `aurex-api` currently reporting successful deployment with one running replica.
- Live source is `victormart43210-ship-it/Valexii-Aurex` branch `integration/kusanagi-xvi-railway`, source directory `/integrations/kusanagi-xvi/backend`, not canonical current `aurex/api.py` / `main`.
- Current live bridge is **read-only**, with `/v1/health`, `/v1/capabilities`, `/v1/evidence`, `/v1/jobs`, `/v1/budgets`. Its capability flags are explicitly unavailable and evidence/jobs empty. It does **not** execute new research algorithms or train models.
- Four pending environment patch changes include a **not-yet-live** SQLite volume at `/data` plus path and feature variables. Do not auto-accept the patch; prior user explicitly requested research only and live changes need separate approval.
- Python distributed tracing and automatic instrumentation currently disabled; no configured healthcheck. Neither tracing nor OX live job instrumentation can be claimed active.
- Read-only GitHub tree checks on both `main` (`c41675fc...`) and the deployed branch (`57a079f...`) found the backend `Dockerfile` but **no `railway.json`, `railway.toml`, or `.railway/railway.ts`**. Thus no existing legacy Config-as-Code migration requirement was established in those branches. The December 1 cutoff matters *if legacy CaC is later discovered elsewhere*; IaC remains beneficial for future reproducibility, but no emergency migration is implied.
- Read-only 24-hour Railway observations: 232 HTTP requests, 0 reported 5xx, 9 reported 4xx; no existing project feature flags or project webhooks. These are measurements only for the current read-only bridge, **not** proof that AUREX intelligence or LLM training is running.
- Railway volume-backed services cannot overlap two active deployments; expect short redeploy downtime even with healthcheck. A future dedicated stateful service is safer than pretending stateless API + attached SQLite supports seamless replicas. Backups restore only within original project/environment; test restore separately before relying on them.
- An authenticated successful deployment is **not** independent evaluation proof or production AUREX intelligence.

## Railway: ranked innovations and adoption contract

| Upstream feature | New original repo support | Activation prerequisite |
| --- | --- | --- |
| Distributed tracing/OpenTelemetry (Sep 25, 2026) | `aurex/llm_telemetry.py` typed **no-export** events; existing `aurex/tracing.py` correlation helpers retained | Separate opt-in OTel Python dependencies, privacy/PII/SQL attribute review, bearer and owner gates, staging traces, exact version; no trace SDK added in this PR |
| Observability HTTP metrics (Jul 31, 2026) | Events can report observed latency and counts with evidence SHA; never manufacture OX graphs | Real service-specific monitoring, independent provenance and only owner-visible visualization |
| IaC (project-level), legacy Config as Code sunset **Dec 1, 2026** | `aurex/railway_readiness.py` reports drift/staged/deprecated config; migration runbook here | Inspect existing `railway.json/toml` in **actual deployment source**, run `railway config migrate` preview and `railway config plan`; preserve variables as `preserve()`; do not apply/cut over until reviewed |
| Project webhooks with secret headers (Oct 1, 2026) | `aurex/railway_webhook.py` checks secret, scope, timestamp and payload bounds; returns `RECONCILE_WITH_RAILWAY_API` | Railway webhooks have **NO cryptographic signatures**, no ordering or delivery guarantees. Requires independently querying current Railway API and durable dedupe before reflecting even owner-only event; no receiver endpoint added |
| Railway Sandboxes GA (Sep 17, 2026) | Training recipe requires sandbox policy evidence for async GRPO; architecture runbook only | Isolated network and secrets, separate quota, pinned image, disallow untrusted egress, replay/cleanup, billing review and independent verification. No paid sandboxes created |
| Railway Feature Flags (Jul 9, 2026) | Recipe classification can inform future rollout review; **no runtime flag grants security authority** | SDK compatibility review (documented TypeScript SDK; AUREX currently Python), operator-created flag default false; signed authorization remains separate |
| Railway Authentication (Oct 9, 2026) | **Not activated** | Changelog indicates Enterprise-only at announcement; not a substitute for service bearer or Lovable owner gate |
| Railway Agent OpenRouter beta & ChatGPT subscription (Sep/Oct 2026) | Research-only; optional coding assistant, **not AUREX model-inference credentials** | Permission, cost and usage ceilings separate; no API token movement or auto model calls |
| Activity-feed filtering and cron CLI (Oct 16, 2026) | Runbook: review service/variable/volume events and scheduled execution receipts | Railway cron remains infrastructure process; must not imply automatic LLM evaluation or human authorization |

### Railway sequencing (proposed only, no changes)

1. Resolve **canonical branch/source root**, signed release candidate and current *staged* volume patch independently; review old read-only deployment against true desired backend contract.
2. Investigate Config as Code files; plan read-only migration before **2026-12-01**. `railway config pull` preserves values by default. **Never** use `--include-variables` into version control; never run `railway config apply`, `migrate cutover`, or `accept-deploy` implicitly.
3. Prepare separate staging/preview without copying production private data/secrets into untrusted PR builds. CI + exact-SHA health/readiness with the appropriate path and port.
4. Audit Python FastAPI OTel PII and SQL disclosure risks. Only after approval enable tracing; add explicit `OTEL_METRICS_EXPORTER=none` and `OTEL_LOGS_EXPORTER=none` for Railway's traces-only collector as documented. Do not turn on opaque eBPF or SQL tracing before privacy review.
5. Instrument **actual** AUREX job/LLM stage timings and counts, not animation frame timings. Output `NOT_INSTRUMENTED` if missing, `NOT VERIFIED` if source-reported.
6. Consider limited alert webhooks after independent reconciliation, owner-only UI contract verification, budgets, error handling, rollback and explicit deployment authorization.
7. **P0 UX remains Ouroboros page lag**: fix mobile/static-by-default/pause/scroll first when Lovable credits resume, before adding new visualization loops.

### Vendor sources
- [Railway Oct 16 activity feed / guided IaC / cron CLI](https://railway.com/changelog/2026-10-16-activity-feed-filters)
- [Railway Oct 9 Railway Auth & OpenRouter beta](https://railway.com/changelog/railway-ios-auth-openrouter)
- [Railway Oct 1 webhook headers](https://railway.com/changelog/2026-10-02-mongodb-high-availability)
- [Railway Sep 25 tracing](https://railway.com/changelog/2026-09-25-free-vms-without-an-account)
- [Railway Sep 17 sandboxes & optional ChatGPT subscription](https://railway.com/changelog/2026-09-18-railway-sandboxes)
- [Railway Jul 31 observability panels](https://railway.com/changelog/2026-07-31-railway-plugin-for-chatgpt)
- [Railway IaC and migration](https://docs.railway.com/infrastructure-as-code)
- [Python OpenTelemetry tracing](https://docs.railway.com/observability/tracing/python)
- [Webhook limitations and payload](https://docs.railway.com/observability/webhooks)
- [Volume caveats](https://docs.railway.com/volumes/reference), [volume backups](https://docs.railway.com/volumes/backups)
- [PR canaries and healthcheck limitations](https://docs.railway.com/guides/ship-on-merge-pr-canaries)
- [Railway feature flags](https://docs.railway.com/feature-flags)

## Google Dorkster / public-documentation OSINT with Firecrawl

A specifically named, authoritative software product called **“Google Dorkster”** was **not verified** in searches. Rather than downloading an unreviewed OSINT scanner, this investigation used **Google-dork-style advanced search operators with Firecrawl** to locate public release notes, upstream docs and technical issues, *not other people's secrets*. Representative safe queries:

```text
site:python.org inurl:2026 "3.15" "released"
site:docs.python.org "Tachyon" "profiling"
site:huggingface.co/blog "Async GRPO" "LoRA" 2026
site:github.com/huggingface/trl "AsyncGRPOTrainer"
site:docs.railway.com/infrastructure-as-code "2026-12-01"
site:railway.com/changelog "Oct 16, 2026"
```

Do not automate arbitrary-target dork enumeration, Google ToS violations or leaked secrets. Public Google indexing is not permission to access private credentials, exploit systems or import data into training. Cite and validate primary sources. Do not treat indexing date as paper publication date.

## Latest Python development findings: October 2026

**Python 3.15.0 shipped 2026-10-09.** The Python release team documents:
- **PEP 810 explicit lazy imports** (startup optimization); **PEP 686 UTF-8 by default**; `sentinel` and `frozendict` builtins; improvements to stable ABI/free-threading.
- **PEP 799 new profiling package and Tachyon high-frequency statistical sampling profiler.** Candidate for locating Python CPU latency in future AUREX worker processes, rather than overengineering yet another profiler.
- Upgraded *experimental* JIT: reported upstream roughly **7–8%** geometric-mean speedup on their x86-64 Linux benchmarks, **not** an AUREX measured speedup. Differences depend on platform/benchmark/JIT build.
- **Do not change the current tested Python 3.12 production Docker image** until PyTorch/Transformers/PEFT/cryptography/FastAPI compatibility is checked with pinned dependencies, repeatable profiling, and a separate staging matrix. Free-threaded builds and JIT need further threading, C-extension and benchmark validation.

Primary: [Python official announcement](https://blog.python.org/2026/10/python-3150-final-is-here/), [What’s New 3.15](https://docs.python.org/3/whatsnew/3.15.html), [Tachyon reference](https://docs.python.org/3.15/library/profiling.sampling.html).

## LLM training innovations: September–October 2026

**Existing code already includes `training/train_lora.py`, `training/prepare_dataset.py`, pinned Qwen2.5-0.5B Instruct, assistant-only labels, artifact hashes and `--execute` gating. Do not duplicate or replace it silently.** `training/innovation_plan.py` adds offline gates for alternative research recipes only.

| Method | Why it matters | Gate |
| --- | --- | --- |
| **SFT LoRA** | Existing low-parameter baseline; cheapest controlled path to evaluate on original authorized datasets | Default existing method; control dataset provenance, withheld eval, exact pinned model, measured costs |
| **SFT QLoRA** | Quantized PEFT fine-tuning can lower GPU memory requirements | Require GPU/bitsandbytes compatibility benchmarks and resource evidence; no automatic download or quantization |
| **DPO LoRA** | Learn from explicit high-quality preference comparisons rather than untrusted generic rewards | Require authorized preference pairs and independent held-out evaluation |
| **Async GRPO LoRA** | Hugging Face **2026-09-10** shows `AsyncGRPOTrainer` with LoRA adapter-only sync to vLLM, TRL v1.14, for separate trainer/inference resources | Must validate **verifiable** reward function, reference independence, cost, isolated rollout environment, adapter revision, policy lag/stale weights and weight-version tracking; NO automatic RL start |
| **vLLM async RL** | vLLM explicitly documents pause/resume and weight-version spans for asynchronous updates | Never mix stale KV cache/rollout output into purported exact-revision evidence. Both training and inference require proper identity and source provenance |
| **Python profiling** | Python 3.15 Tachyon may support later performance investigations | Independent opt-in A/B benchmark; do not assume speedup or move production runtime |

Upstream references:
- [Hugging Face Async GRPO + LoRA across Jobs (Sep 10, 2026)](https://huggingface.co/blog/asyncgrpo-lora-hfjobs) — illustrative training example's latency reduction is theirs, *not AUREX's*.
- [TRL AsyncGRPOTrainer](https://huggingface.co/docs/trl/en/async_grpo_trainer), [TRL overview](https://huggingface.co/docs/trl/en/index)
- [Hugging Face GRPO and vLLM cookbook](https://huggingface.co/learn/cookbook/en/grpo_vllm_online_training)
- [Hugging Face PEFT LoRA methods](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)
- [vLLM async RL and version spans](https://docs.vllm.ai/en/latest/training/async_rl/)
- [vLLM training integration](https://docs.vllm.ai/en/latest/training/trl/)

### New code contracts and verification

1. `aurex/railway_readiness.py`: typed snapshot; missing/stale/staged deployment, old branch, absent tracing/healthcheck, backup and stateful volume risk reported as **HOLD**. Even a complete snapshot returns **INDEPENDENT_RELEASE_REVIEW_REQUIRED**, not automatic release.
2. `aurex/railway_webhook.py`: constant-time bearer-header validation, 16-KiB bound, project/environment scoping, age check and body digest. Returns only **RECONCILE_WITH_RAILWAY_API**, never signed/trusted witness. No HTTP handler or incoming webhook created.
3. `aurex/llm_telemetry.py`: allowlisted numerical observations for real backend/test/training/eval/inference events. Strict event ordering, SHA identity, clock freshness, no prompts/PII or secrets. Empty = `NOT_INSTRUMENTED`; any nonempty summary = `OBSERVED_NOT_VERIFIED` at best. No model/GPU inference or automatic animation.
4. `training/innovation_plan.py`: purely local stdlib training-method readiness CLI. `SFT_LORA`, `SFT_QLORA`, `DPO_LORA`, `ASYNC_GRPO_LORA` options, $0 default, pinned checkpoint/dataset digests, signed research *provenance claims not established*, dependency guards. Never calls existing `train_lora.py`; best gate = `OPERATOR_REVIEW_REQUIRED_NOT_EXECUTED`.

Example: save a locally reviewed **synthetic** proposal as JSON, never weights or datasets in Git:
```json
{
  "recipe_id": "sft-lora-research-01",
  "method": "SFT_LORA",
  "base_model": "Qwen/Qwen2.5-0.5B-Instruct",
  "revision": "dddddddddddddddddddddddddddddddddddddddd",
  "training_data_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "heldout_data_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "provenance_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "training_rows": 40,
  "heldout_rows": 16,
  "max_steps": 20,
  "estimated_cost_usd": "0"
}
```
```bash
python -m training.innovation_plan --input /tmp/aurex-research-recipe.json
python -m pytest -q tests/test_railway_research_safety.py tests/test_llm_telemetry_contract.py tests/test_training_innovation_plan.py
ruff check .
mypy aurex
```

Those example IDs/hashes are **not evidence of a real dataset or training run**. The CLI emits HOLD unless all conditions are *claimed* satisfied, and even after that always requires independent review and authorization.

## Release, security, privacy and finance invariants

- **Evidence → Qualification → Reality → Authority → Effect**; ROTAS reverse audit; **unknown ≠ safe**; no sole self-witness; historical FAIL immutable; CUSTOS demote-only.
- Private signed admissions, lease/fencing, existing `aurex/experiments/admission.py` and owner-only Lovable security remain the authority boundaries. No new model, metric, event or feature flag bypasses them.
- No signed webhooks supplied by Railway; event data can be spoofed if secret leaks. Enforce rate limits, signed API reconciliation, deduplication and owner-only delivery before production transport.
- Railway tracing can capture sensitive URLs, SQL and network attributes. Never send raw prompts, PII, authentication headers or code secrets to OX/public UI; preserve server-side owner gate.
- `railway config pull --include-variables` may expose secrets; avoid entirely. Separate test/staging from production data. Sandbox/Cloud Agent/tracing cost not assumed free.
- AUREX's **$0 default** applies to provider calls/paid training; user authorization required for any actual usage cost or deployment.
- **AUREX/OX P0 remains Ouroboros lag**, to be fixed before new dashboard animations. No Lovable credits used by this work.
- Other drafted #53 (Helsinki) and #54 (global university) are **NOT MERGED**. This independent #55 branch is based on main, not those PRs; exact-head CI and serialized integration must follow canonical `docs/AGENT_MAINLINE_POLICY.md`.
- **No training ran, new models downloaded, Railway changes applied, UI published or security scan performed.** Upstream novelty is not AUREX efficacy until independently measured.

## Next admission gates

1. CI exact-head `pytest`, Ruff, Mypy and independent runner smoke.
2. Separate CUSTOS audit on webhook source assumptions, telemetry clock/ordering, privacy risks and training plan false-PASS safety.
3. Qualified owner-only live telemetry adapter and versioned contract if/when the backend actually emits events, no fabricated graph.
4. Reconcile staging `/data` volume/healthcheck and old deployed branch with canonical release *without auto deployment*.
5. Python 3.15 runtime benchmark and LoRA/GRPO model training are **NOT RUN** until authorized budgets, hardware, pinned dependencies, data rights and independent evaluation.
