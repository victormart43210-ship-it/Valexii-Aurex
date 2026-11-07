# AUREX Global Assurance — London, NYC/New York & global beta controls

**Source review: 2026-10-19. Code scope: optional, offline, synthetic-only beta admission sidecar. Production = HOLD.**

We adapted public research and official guidance into **our own AUREX control catalogue**, not someone else's audit product or proprietary source. It is an engineering checklist, **not regulatory certification**. UK and New York financial regulatory frameworks do not automatically apply to a Texas oilfield pilot; assess applicability independently.

## Source-to-feature crosswalk

| Source/geography | Verified primary reference | Implemented AUREX design rule |
| --- | --- | --- |
| London: UK Financial Reporting Council, 2026 GenAI/agentic audit guidance | https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/ | `record_provenance`: bind source and audit-rule versions before financial analysis. This is not a statutory audit opinion. |
| London: UK Information Commissioner's Office, human review | https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/human-review/ | `human_override_trace`: evidence of meaningful review, logging reviewer challenges/overrides. ICO flags guidance as under review. |
| London: ICO accountability and privacy | https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/governance-and-accountability-in-ai/ | `privacy_processing_scope`: scope purpose, processor access, retention, and personal information controls. |
| London: Financial Conduct Authority AI Lab | https://www.fca.org.uk/firms/innovation/ai-lab | `synthetic_sandbox_first`: staged synthetic testing before any production invoices. We are **not** an FCA program participant. |
| UK AI Security Institute, Inspect | https://inspect.aisi.org.uk/ | `independent_eval_replay`: reproducible external evaluator and negative cases; **Inspect not installed**, no source borrowed. |
| NYC market reference: New York State DFS 2026 cybersecurity risk assessments | https://www.dfs.ny.gov/industry_guidance/industry_letters/il20260910-cyber-risk-assessment | `third_party_dependency_inventory`, `change_triggered_risk_review`: account for APIs, vendors, concentrations and material changes. NYDFS is a **New York State** regulator, not NYC City government. |
| NYC market reference: NYDFS 2024 AI cybersecurity letter | https://www.dfs.ny.gov/industry-guidance/industry-letters/il20241016-cyber-risks-ai-and-strategies-combat-related-risks | `least_privilege_tool_access`: separate private audit/reviewer rights from execution access and protect sensitive records. |
| Global workflow documentation: LangGraph interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts | `resume_requires_authority`: checkpoint resume rechecks actor, tenant, lease, source hash and idempotency. LangGraph is *optional*, not installed or deployed. |
| Global application security: OWASP Agentic AI 2026 | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | `unauthorized_action_adversarial`: test prompt injection and unauthorized tool/agent actions. |
| Singapore IMDA, Agentic Testing Starter Kit | https://www.imda.gov.sg/about-imda/emerging-technologies-and-research/artificial-intelligence | `agent_path_monitoring`: evaluate tool calls, handoffs, approvals and regression over time. |
| AUREX existing policy | https://github.com/victormart43210-ship-it/Valexii-Aurex/blob/main/AGENTS.md | `zero_spend_no_side_effect`: preserve $0 external spending, human HOLD and separation of evidence and authority. |

## What is actually implemented

New `aurex/field_assurance.py` contains **12 AUREX-authored controls** anchored to source URLs, a deterministic versioned SHA-256 profile, a sample synthetic claim manifest, and a strict offline validator for evidence **metadata**, rather than the underlying evidence or financial documents.

The validator rejects: changed profile SHA, extra/unexpected fields, non-synthetic input, missing/duplicate controls, invalid or duplicate JSON keys, malformed hash IDs, unknown statuses, empty/future/stale (>30 days) claimed reviews, unrecorded source commit, reviewer string equal to implementer string, oversize input and symlinked input. A `NOT_RUN`, `HOLD`, or `FAIL` control cannot include unverified evidence blobs.

**Very important limitations:** The code does not authenticate reviewers, inspect actual evidence bytes, test business accuracy, validate provenance signatures, establish GDPR/NYDFS applicability, or confer independent verification. Even a structurally complete set of 12 claimed PASS statuses returns **`REVIEWABLE_CLAIMS_NOT_ATTESTED`**, **`independent_verification=NOT_VERIFIED`** and **`production_release=HOLD`**. Approval and payments remain forbidden.

## How to run without billable services

```bash
python3 -m aurex.field_assurance --profile > /tmp/aurex-assurance-profile.json
python3 -m aurex.field_assurance --template > /tmp/aurex-assurance-claims.json
# Template exits 1 (HOLD), because no independent reviews have been run:
python3 -m aurex.field_assurance --assess /tmp/aurex-assurance-claims.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_field_assurance.py
```

Exit 0 = claim metadata ready for independent review **only**, NOT permission to launch. Exit 1 = HOLD due to missing/inconsistent claims. Exit 2 = malformed/invalid manifest.

## Integration plan for one canonical AUREX backend

- **Existing PR #99:** 100 deterministic synthetic oilfield audit fixtures and candidate scorer. This assurance sidecar extends **the same draft PR**, no competing repository, no extra audit engine.
- **Existing PR #89:** synthetic nine-source financial review engine; independent code, CI and adversarial review still required before choosing a selective mainline integration.
- **Existing PR #80:** encoded local financial kit; inspect/check digest and security before any use. No bulk merge.
- **LangGraph:** only after an isolated optional adapter can demonstrate resumable checkpoints with canonical SQLite/worker fencing and fresh authorization. Neither graph state nor animation may grant authority.
- **Sovereign Studio:** when independently verified, show control gaps, evidence receipts, review decisions and operator HOLD status through owner-authenticated views. No public uploads, real invoices, or unrestricted tools in this draft.

## Admission gates not yet achieved

Actual candidate outcomes on 100 fixtures; separately sourced held-out oilfield samples; independent proof of evidence hashes and reviewer identities; tenant authorization, encryption, deletion/retention, and customer consent; real authenticated website → worker → SQLite → evidence retrieval; human-signed commercial SOP; measured accuracy, false-positive rate, review cost, and customer value; exact-head independently passing GitHub CI, which was failing as last checked. **No merge, production change, legal compliance assertion or beta release was authorized.**

**Invariant:** Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness. No self-issued PASS.
