# OPERATION KUSANAGI CCCLVI — JULES SUCCESSION PROTOCOL

## Executive Transition Summary

This document governs the orderly, evidence-backed succession from Google Jules to a unified, controlled engineering mainline orchestrated by **ChatGPT Work**, supported by **GitHub** as the canonical single source of truth, and assisted by **Cursor / Copilot** for bounded, targeted coding repairs.

The historical pattern of scattered engineering assignments across multiple uncoordinated AI coding agents generated 145+ unmerged branches, redundant implementations, and fragmented handoff records. This succession protocol eliminates agent fragmentation and establishes one authoritative workflow.

---

## Tool Division of Responsibility

| Tool / System | Successor Role | Governing Boundary |
|---|---|---|
| **ChatGPT Work** | Lead Investigator, Architect, Integration Coordinator, Audit Authority | Issues all technical directives; synthesizes multi-system state; prepares formal PR specifications and merge packages. |
| **GitHub** | Canonical Source of Truth, PR Review, CI Enforcement | Mainline repository (`victormart43210-ship-it/Valexii-Aurex`); branch protection; signed releases; issue tracking. |
| **Cursor / Copilot** | Targeted Code Implementation, Bounded Refactoring | Executes single-purpose, bounded coding assignments under strict TDD and acceptance contracts formulated by ChatGPT Work. |
| **CI / Automated Test Suites** | Deterministic Quality Gates | Pytest (backend), Ruff (lint), Mypy (strict typing), Bun (frontend test & build), Docker (container build). |
| **Owner Authority** | Non-Delegable Product & Financial Authority | Sole authority to execute main merges, production deployments, and financial confirmations. |

---

## Jules Work Recovery & Preservation

Before Jules workspace retirement, all unique engineering contributions must be accounted for and verified on canonical main or preserved in tracked branches:

1. **DISPATER Operational Intelligence:** PR #159 (Jules DISPATER baseline convergence) and PR #205 (financial recovery, detectors, stateless audit packages) have been successfully merged into canonical `main` (`fc2bed4`).
2. **Deterministic Golden Financial Fixture:** Golden financial oracle test suite and exposure invariants (`tests/test_dispater_reconciliation.py`) are fully active on main.
3. **Verified ZIP Extraction Safety:** Test regression in `tests/test_aurex_verified_zip_finder.py` has been repaired and verified.
4. **Handoff Artifacts:** All historical Jules handoffs in `docs/operations/` (`JULES_CHATGPT_HANDOFF.json`, `CCLXII_JULES_RECOVERY_RECONCILIATION.json`, etc.) remain archived in version control.

---

## Operating Protocol for ChatGPT Work

1. **Single Branch Merges:** Never merge multi-branch chains simultaneously. Each candidate branch (e.g., `work/valexii-sovereign-kernel-foundation-20261108`, `cursor/kusanagi-ccxcvii-model-forge-4082`) must be reviewed independently, rebased against current `main`, tested against full test gates, and merged via individual PR with owner sign-off.
2. **Zero Unverified Fallbacks:** Any agent proposing a feature must supply the automated tests before implementation. If an external service or hardware adapter is unavailable, code must fail closed (e.g. `NOT_CONFIGURED` or `HOLD`), never mock success.
3. **No Paid Inference Without Authorization:** Staging and development must enforce zero API spend. Model adapters must default to local or simulated private inference.
4. **Durable Ledger Updates:** Every major milestone must produce an audit or handoff update in `docs/audits/` or `docs/operations/` pinned to exact Git commit SHAs.

---

## Jules Decommissioning Checklist

- [x] Full-system evidence audit executed (OPERATION KUSANAGI CCCLVI).
- [x] All 939 backend pytest tests passing, 0 linter errors, 0 strict type errors.
- [x] All 173 frontend bun tests passing, production build passing.
- [x] 222 remote branches cataloged and classified in `CCCLVI_BRANCH_PR_MATRIX.csv`.
- [x] No orphaned local work left uncommitted or unpushed.
- [x] Complete system inventory, failure ledger, backlog, and handoff generated in `docs/audits/`.
- [x] Succession protocol transferred to ChatGPT Work.
