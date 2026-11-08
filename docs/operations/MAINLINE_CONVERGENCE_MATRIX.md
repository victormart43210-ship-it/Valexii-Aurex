# Mainline convergence matrix (OPERATION KUSANAGI CCCXXXIV)

Recorded 2026-11-08. `main` = `fc2bed4dd98054503254ad1a4c11fbecd7b0deca` (merge-base of PR #212, verified).
Legend: **V** = verified by command/log in this session, **P** = planned / unverified.

| PR | Head SHA | State | Diff | CI at head (V) | Unique functionality | Overlap / conflict | Disposition (proposal, owner decides) |
|----|----------|-------|------|----------------|----------------------|--------------------|---------------------------------------|
| #212 | `edbdc11336f4ec177b5e0cc326f372c18000bc04` | Draft, mergeable | Knowledge Treasury, maintenance advisory, mainline gate workflow | All 7 checks pass; local ruff/mypy/pytest pass (954 passed, 2 skipped) | AUSEKLIS treasury, DISPATER advisory | None with #208-#211 by file | Canonical foundation. Hold for G4/G6/G7 |
| #211 | `96254c0c57fc` | Draft, stacked | +2652/-58, 27 files | **integration, test x2, verify FAIL**: `tests/test_forge_adversarial.py::test_execute_blocks_unapproved_data_wrong_tenant_and_low_storage` expects exit 2, gets 1 (`ModuleNotFoundError: transformers` in `training.train_lora`) | Optional-torch mypy fix over #210 | Superset of #209/#210 files (`aurex/ox/forge.py`, `registry.py`, `llama_cpp.py`) | Preferred Forge line, after test repair (preflight must fail closed with exit 2 before importing transformers) |
| #210 | `b3d4062771ab` | Open | +2651/-58, 27 files | Same failing jobs as #211 (expected, #211 is its stacked fix; per-job log not re-read) | Adversarial repair of Forge | Duplicates #209 | Superseded by #211 if #211 lands; do not merge both |
| #209 | `b995df784182` | Open | +1401/-12, 15 files | **FAIL**: mypy `aurex/ox/forge.py:392 Cannot find ... module "torch"` | First Forge cut | Superseded by #210/#211 | Superseded; close only after owner review |
| #208 | `f014111853c3` | Open | +333/-60, 4 files | All checks pass | Qwen live-check observability, staging data dir (`Dockerfile`, `docker/entrypoint.py`, `tools/verify_xaeli_private_qwen.py`) | Disjoint from other PRs by file | Independent; candidate to merge separately. Security-sensitive (Docker entrypoint): needs independent review |

## Already merged (V, from PR list)
#196 industrial linkage, #198 client timeout, #199-#201 fullstack/health, #203-#205 verified ZIP recovery and DISPATER detectors/audit-package. Closed: #197 (recovered via #205), #202 (rehearsal).

## Conflicts and risks
- Shared contract files across #209/#210/#211 (Forge): choose #211 line as canonical; one Forge implementation only.
- `docs/operations/JULES_MODEL_FORGE_HANDOFF.json` touched by all three Forge PRs: expect textual conflicts.
- Unverified claims: Forge PR verification JSONs under `docs/verification/` report training/benchmark results; not reproduced here (P).
- Security-sensitive: #208 (container entrypoint, private model probe), Forge data-tenant gating.
- Needed before integration: repair #211 failing test, rerun full CI, independent reproduction, no migrations identified (P - not exhaustively audited).
