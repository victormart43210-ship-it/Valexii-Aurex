# Branch reconciliation matrix for OPERATION KUSANAGI XXVI

This document summarizes the repository state as inspected from GitHub. It is intentionally conservative and records only what was verified from the repo state, branch diffs, and CI logs. Live website / Railway / Qwen runtime remain NOT VERIFIED unless the operator provides a staging endpoint or runtime access.

## Canonical repository

- Repository: victormart43210-ship-it/Valexii-Aurex
- Canonical integration branch: main
- Current main SHA: c98ca176ee0fb0e2f4a79427d0ee225eca6b0305
- Working integration branch created by Copilot: copilot/kusanagi-xi-sovereign-activation
- Working branch SHA: 1174179946c171f140c4aec6877e53321e0f9fbf

## Branch classifications

- main: ALREADY INCLUDED
  - Canonical source of truth for the repo.
  - Contains the mainline baseline and CI infrastructure.

- integration/kusanagi-xxii-governed-execution: PARTIALLY_INTEGRATE
  - Adds a governed workflow engine, local-inference boundary, recovery utilities, and tests.
  - Valuable work but overlaps with repo-side job store and local inference code; needs consolidation to avoid duplicate engines.

- integration/kusanagi-xx-local-inference: PARTIALLY_INTEGRATE
  - Adds a local inference boundary and tests.
  - Overlaps heavily with the XXII branch; prefer one canonical local inference API surface.

- integration/kusanagi-xix-agentic-workflows: HOLD
  - Advanced workflow/agentic functionality needs an explicit security review before merge.
  - Autonomous or agentic execution should remain gated and bounded.

- integration/kusanagi-xvi-railway: INTEGRATE (read-only bridge)
  - Adds a read-only bridge and contract tests.
  - Useful as a staging contract and fail-closed backend skeleton; can be used for website-side integration tests without enabling live write operations.

- fix/kusanagi-xxiv-fail-closed-security: PRIORITY_INTEGRATE
  - Security-oriented work is important and likely overlaps evidence-integrity and fail-closed enforcement.
  - Must be merged only after security-negative tests pass.

- work/kusanagi-xiii-evidence-repair: PARTIALLY_INTEGRATE
  - Evidence integrity and repair work overlaps provenance/evidence-tracking code.
  - Merge only the code that matches the required canonical evidence model.

- copilot/kusanagi-xi-sovereign-activation: PARTIALLY_INTEGRATE
  - Good repo-side scaffolding including adapter, docs, execution metadata, trace context, and tests.
  - Safe staging-only changes but not a production claim.

- feature/* branches: HOLD or PARTIALLY_INTEGRATE
  - These feature branches contain useful components but need file-by-file review for overlap and compatibility.
  - Most should be either superseded by the canonical workflow + local inference + evidence model or held until the mainline is stabilized.

## Core consolidation guidance

1. Choose one canonical workflow engine and one canonical local inference boundary.
   - Best candidate: integration/kusanagi-xxii-governed-execution as the canonical workflow path.
   - Merge the best local inference implementation from the XX/XXII branches into a single surface.
2. Keep the read-only bridge under integrations/kusanagi-xvi as a contract test asset, not as a production write path.
3. Preserve security fixes from fix/kusanagi-xxiv and evidence repair work from work/kusanagi-xiii after verification.
4. Do not merge feature branches wholesale; port only the validated diffs that are consistent with the chosen canonical schema.

## Live/runtime status

- Website source: present in repo under website/ but not independently verified against a live deployment.
- Railway deployment: NOT VERIFIED.
- Native Qwen runtime: NOT VERIFIED.
- Live website integration: NOT VERIFIED.

These items require a reachable staging environment or an operator-run smoke test on the target host. Without those, they remain unsafe to label as PASS.
