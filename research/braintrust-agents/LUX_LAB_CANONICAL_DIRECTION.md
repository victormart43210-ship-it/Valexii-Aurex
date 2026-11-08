# VALEXII LUX Laboratory — Canonical Product Direction (2026-11-08)

Status: **DESIGN LOCK / NOT DEPLOYED**. Production HOLD; financial authority NONE; paid inference OFF. This document records owner-approved product direction; implementation, privacy/legal review, and independent verification remain required.

## Minimal website footprint

- **Public LUX Laboratory:** integrate into an existing public page/section when practical; at most one dedicated `/ai-lab` route if required. No separate page for each manuscript or model.
- **Private Sovereign Studio:** preserve `/admin/sovereign-studio` as one owner-only workspace with internal panels, tabs, drawers, and workflow viewer. Server-side authorization and MFA, not hidden navigation, protect operations. Future delegated users have narrowly scoped permissions; never owner authority.
- Reuse AUREX backend APIs, identity, observability, evidence storage and common UI components. Avoid duplicate services or architectures.

## Public research missions

1. **Voynich Manuscript:** documented glyph-sequence patterns, illustrations, competing hypotheses and reproducible evaluation.
2. **Linear A:** sign distributions, cross-inscription comparisons and consistency checks.
3. **Rongorongo:** documented glyph sequences, structural patterns and culturally responsible interpretation, involving Rapa Nui perspectives when appropriate.

None has a generally accepted complete decipherment. Never market a generated interpretation as a proven translation. Every hypothesis needs source provenance, uncertainty, counterevidence and independent review. Respect image rights, research permissions and cultural context.

## Three public engagement mechanisms

1. Weekly interactive manuscript challenges using verified source samples.
2. Human-plus-AI hypothesis comparisons across two initially approved lightweight models, with a third optional after license/runtime/safety benchmarking. Candidates include Qwen3 and a suitably small RWKV model; no model is approved/deployed by this document.
3. **LUX Discovery Brief** weekly newsletter featuring reviewed results, failures, new challenges and consented contributor recognition.

## Registration and marketing

- Verified email and versioned Responsible Use Agreement acceptance before using the interactive lab.
- Separate, optional, affirmative marketing/newsletter consent; no automatic subscription from registration; unsubscribe and deletion flows.
- Server-side abuse controls, quotas, rate limits, privacy notices and data minimization. Legal review required; a waiver does not replace security or remove liability.
- Public users never receive private training data, GitHub write authority, coding-agent access, Studio access or unrestricted tools.

## Sovereign Studio operations

- Single workflow console for XAELI/ZAYLI, Model Forge, Braintrust coding agents, DISPATER, security and LUX research.
- Owner can review submissions, approve curated datasets, launch bounded authorized jobs, inspect progress and export JSON evidence for GPT or XAELI.
- Public contributions are **not** automatically training data. Require explicit reuse consent, licensing, provenance, moderation and quality gates.
- Workflow results must separate OBSERVED, HYPOTHESIS, WITHHELD, NOT_RUN and independently VERIFIED states. No self-certification.

## Versioned JSON evidence contract

Minimum keys: `schema`, `report_id`, `workflow`, `status`, `authority`, `source_refs`, `model_ids`, `hypotheses`, `counterevidence`, `evaluations`, `evidence_hashes`, `independent_verification`, `consent_scope`, `redactions`, `next_actions`, `approval`. Do not export raw personal email addresses, private source records or secrets to external models by default.

## Implementation order

1. Freeze contracts and secure Studio/public authorization boundaries.
2. Build shared workflow console and JSON report/export contract.
3. Connect two independently tested model endpoints and the three curated manuscript missions.
4. Add registration, responsible-use agreement, optional newsletter and weekly challenge scheduling.
5. Verify accessibility, abuse prevention, source provenance, security and exact-SHA end-to-end behavior before launch.

**Authority doctrine:** Evidence → Qualification → Reality → Authority → Effect. The system may never be its own sole witness. Owner approval required for sensitive publication, merges and releases.
