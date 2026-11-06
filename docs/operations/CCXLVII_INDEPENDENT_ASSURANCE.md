# CCXLVII independent assurance

Recorded 2026-11-06 8:57 AM CT (`2026-11-06T14:57:00Z`).

## Reviewer

An Opus-class read-only reviewer was started in a separate agent (`bc-74a1875d-ee1e-59f9-9b9e-0f6a8184a6ab`, model Claude Opus). It was told not to edit files. Its findings were not back when this note was written.

This session repaired the test and wrote this note. It is not an outside witness. The reviewer shares the same repository checkout, so even its report is not a separate runner. A human review is still required before any merge.

## What this session checked

On the working tree, using the workflow command `pytest -q` (not `python -m pytest tests`):

- 695 passed
- 1 skipped: `training/tests/test_lora_smoke.py` because `torch` is not installed
- 1 Starlette deprecation warning
- exit 0

`ruff check .` exited 0. `mypy aurex` exited 0 on 104 files. That is the CI mypy target.

`npx vitest run` in `website`: 23 files, 157 passed. `npx tsc --noEmit` exited 0. `npm run build` exited 0. Bun was not used.

`dispater-web`: `npm test` 25 passed and `npm run build` exited 0. Those steps never ran on GitHub because pytest failed first.

The golden arithmetic restated in `tests/test_ox_laboratory.py` is identified `385.00`, withheld `150.00`, confirmed `0.00`. The engine summary matched those literals, and confirmed recovery was not equal to identified exposure. The `110.00` invoice against the `100.00` rate identified `10.00` and confirmed `0.00`. No finding was `CONFIRMED_DISCREPANCY`.

The offline laboratory still rejects the empty digest, a self-approval, paid inference, a cross-tenant fixture, and the injected recovery of `50.00`. Customization does not set `training_started`. The historical proposal stays `activated: false`.

Chrome rendered `/development-status` on `127.0.0.1:5173` at about 8:56 AM CT. The page shows Production HOLD, Financial authority NONE, Historical records NOT PROCESSED, and Live model connection NOT VERIFIED. The HTML also contains Paid inference OFF. This was not a deployment.

## Not established

GitHub has not rerun CI or CLIV on the repair. A local green run does not clear those failed workflows. No submitted pull-request review exists.
