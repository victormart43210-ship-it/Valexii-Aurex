# VALEXII / AUREX — Braintrust Agent Research Catalog

Status: **RESEARCH ONLY / LOCKED CANDIDATE LIST** (not an approved dependency lockfile).

Created 2026-11-08. Canonical repository: `victormart43210-ship-it/Valexii-Aurex`. This research branch contains links and evaluation guidance only; it does **not** install, vendor, execute or approve third-party code.

## Candidate catalog (26)

| Category | Project | Upstream |
|---|---|---|
| orchestration | Crewly | https://github.com/stevehuang0115/crewly |
| orchestration | Ruflo | https://github.com/ruvnet/ruflo |
| orchestration | LangGraph | https://github.com/langchain-ai/langgraph |
| orchestration | CrewAI | https://github.com/crewAIInc/crewAI |
| coding | OpenHands | https://github.com/All-Hands-AI/OpenHands |
| orchestration | AutoGen | https://github.com/microsoft/autogen |
| orchestration | AG2 | https://github.com/ag2ai/ag2 |
| orchestration | Google ADK | https://github.com/google/adk-python |
| orchestration | OpenAI Agents SDK | https://github.com/openai/openai-agents-python |
| coding | MetaGPT | https://github.com/geekan/MetaGPT |
| coding | ChatDev | https://github.com/OpenBMB/ChatDev |
| coding | SWE-agent | https://github.com/SWE-agent/SWE-agent |
| coding | DeerFlow | https://github.com/bytedance/deer-flow |
| orchestration | Paperclip | https://github.com/paperclipai/paperclip |
| orchestration | Orbi | https://github.com/orbi-ai/orbi |
| memory | Letta | https://github.com/letta-ai/letta |
| memory | Mem0 | https://github.com/mem0ai/mem0 |
| memory | Graphiti | https://github.com/getzep/graphiti |
| memory | Zep | https://github.com/getzep/zep |
| memory | Cognee | https://github.com/topoteretes/cognee |
| evaluation | Braintrust Python SDK | https://github.com/braintrustdata/braintrust-python |
| evaluation | Arize Phoenix | https://github.com/Arize-ai/phoenix |
| evaluation | Langfuse | https://github.com/langfuse/langfuse |
| evaluation | DeepEval | https://github.com/confident-ai/deepeval |
| evaluation | Ragas | https://github.com/explodinggradients/ragas |
| evaluation | AutoEvals | https://github.com/braintrustdata/autoevals |

## Evaluation procedure

1. Verify upstream repository identity, license, release activity, supply-chain risks and resource requirements before cloning.
2. Inventory Chromebook agents and credentials **without displaying secrets**; inspect CPU/RAM/disk before choosing local workers.
3. Trial **one coordinator plus one bounded worker** in disposable Git worktrees; do not run all frameworks concurrently.
4. Use read-only discovery first. Keep external paid inference OFF unless owner explicitly approves a cost cap.
5. Run static checks, unit/integration tests and independent GitHub Actions against exact commits. Preserve test evidence.
6. Require owner approval for merges, publishing sensitive IP, deployment and financial actions.

## Shortlist

- Crewly — agent coordination UI and CLI interoperability (verify compatibility).
- LangGraph — stateful, explicit control graph and approval boundaries.
- Ruflo — swarm patterns (higher complexity and security review).
- OpenHands — software-engineering worker (potentially resource-heavy).
- Arize Phoenix — traces, evaluation and evidence.

## VALEXII authority constraints

Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness. Production HOLD; financial authority NONE; paid inference OFF; no customer data; no unauthorized sensitive-IP publication. An agent must never self-approve its own PR or elevate its privileges.

## Repository status

This is a research directory within the **existing** canonical repository, not a newly created standalone GitHub repository. The infographic's standalone `VALEXII-AI/AUREX-Braintrust-Agents` address is a design placeholder, **not a verified live URL**. Do not clone that placeholder.
