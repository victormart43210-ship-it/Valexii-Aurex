# KUSANAGI CLVI — China/Singapore reference pattern admission

Status: **RESEARCHED / INTEGRATION NOT VERIFIED**. This document records upstream design patterns and guarded pilot candidates; it does not declare any third-party dependency installed, model connected, new functionality operational, or production-safe.

## Canonical guardrails

Preserve **Evidence → Qualification → Reality → Authority → Effect** and **the system may never be its own sole witness**. AUREX is an evidence witness, not the final source of authorization. No third-party model, external agent, evaluation score, or visual workflow may grant itself authority, certify DOT/IRS compliance, suppress NOT_VERIFIED, expose tokens, or initiate production deployment. Existing `docs/AGENT_MAINLINE_POLICY.md` takes precedence. Production: **HOLD**.

## Source inventory and proposed adaptation

| Origin / system | Primary source | Candidate adaptation | Admission barrier |
| --- | --- | --- | --- |
| China / AgentScope 2.0 | https://agentscope.io/ , https://github.com/agentscope-ai/agentscope | Typed tool calling, agent visibility, bounded multi-agent orchestration; selectively adapt patterns, not an overlapping second scheduler | Review exact version/license/dependencies; compare to existing AUREX orchestrator; no duplicated authority |
| China / AgentScope OpenJudge | https://github.com/agentscope-ai/OpenJudge | **Independent** judge harness for XAELI explanation quality and adversarial synthetic audit tasks | Calibration, reviewer independence, judge-disagreement receipts, prompt-injection tests |
| China / AgentScope ReMe | https://github.com/agentscope-ai/ReMe | Optional durable, scoped retrieval of prior synthetic cases | Tenant segmentation; retention and deletion tests; avoid unverified memory being promoted to evidence |
| China / Qwen Code | https://github.com/QwenLM/qwen-code | Vibe-code sandbox for developer PR generation using selectable local/provider models | Agent generates PRs only; limited permissions; no GitHub main merges or Railway deployments; constrained spend |
| Singapore / AI Verify Foundation Project Moonshot | https://aiverifyfoundation.sg/tools/moonshot/ , https://github.com/aiverify-foundation/moonshot | LLM red-team and benchmark suite for prompt-injection, leakage, groundedness, and safety on XAELI | Confirm compatible versions and licenses; run in isolated CI, record manifest, seeds, exact model and commit |
| Singapore / SEA-LION | https://sea-lion.ai/ , https://sea-lion.ai/models/ | Optional multilingual experimental model adapter, contingent on business requirements | Validate weights/model license, privacy, latency, inference cost, English and domain accuracy; default disabled |

These are **research candidates, not adopted runtime dependencies**. Assess the upstream source/license/SBOM and data-routing jurisdiction before any install, especially for customer data. Sandbox all externally generated code and treat tool descriptions, retrieved text and model output as untrusted.

## Minimal viable feature admission — prioritized

1. **Testing first:** add an optional external safety-evaluation harness behind an offline flag. Baseline with synthetic towing/oilfield fixtures. A test case must contain `scenario_id`, `input_fixture_hash`, `expected_security_property`, `observed_result`, `engine_version`, `source_commit_sha`, `reviewer`, and `evidence_receipt` (nullable; absence is never PASS).
2. **Governed vibe coding:** design a proposal-only pipeline `user intent → isolated code agent → diff + tests → adversarial reviewer → PR → human approval`. No autonomous production effects. Start with existing Copilot/Jules workflow before evaluating Qwen Code.
3. **Agent observability:** prototype role/tool/event tracing without sensitive prompts, credentials, tenant data or unbounded logs. Prefer extending existing tracing and receipt logic instead of installing parallel orchestration.
4. **Optional model routing:** assess SEA-LION only for multilingual demand; never substitute model output for evidence or reviewer authority.

## Mandatory acceptance tests

- Missing/malformed/expired authorization fails closed with expected 401/403; no token leak.
- One tenant cannot access another tenant's prompts, documents, memory, logs, cases or receipts.
- Unsupported statement and missing evidence remain `NOT_VERIFIED`, never PASS.
- Prompt injection in retrieved documents cannot trigger tool execution or change authorization.
- An implementation agent cannot approve its own output as an independent reviewer.
- A failed evaluation runner/provider is `NOT RUN` / `NOT VERIFIED`, not success.
- Deterministic synthetic towing and oilfield fixtures, replayed at exact head SHA.
- Resource and cost limits enforced; default external-provider budget $0.
- Any application UI reflects real backend status only; no simulated result masquerading as live.

## Current staging alignment

On 2026-10-24 Railway `aurex-staging` was observed online with one healthy replica and a volume mounted at `/data`, deployed from `main` commit `f2db438f0020dbd455bcb5c7b21b7352d133bf2c`. **This does not establish that the latest industrial audit code or any upstream reference system is deployed.** Recheck deployment SHA before end-to-end testing.

## Execute next, in the existing mainline pipeline

- Copilot: inspect existing APIs and test harness; choose **one** smallest noninvasive capability (prefer isolated synthetic safety-evaluation adapter), implement on a fresh branch, add regression tests, and open PR.
- Jules: independently attack auth, tenant isolation, provenance, prompt injection and judge independence against exact PR head SHA.
- ChatGPT Work: verify full VALEXII frontend → AUREX staging flow against **deployed** SHA; compare observed outputs and receipt chains.
- Integrator: merge only authorized verified changes serially; independently authorize staging deployment. Production remains HOLD.

## Provenance and confidence

Primary vendor/project pages checked using Firecrawl on 2026-10-24:
- https://agentscope.io/
- https://aiverifyfoundation.sg/tools/moonshot/
- https://sea-lion.ai/

Their capabilities are claims from project-maintainer descriptions, **not independently measured against VALEXII**. Open-source status does not imply unconditionally permissive licenses or that local operation is free. No specific code, weights, benchmark scores, or compliance endorsements copied from upstream.
