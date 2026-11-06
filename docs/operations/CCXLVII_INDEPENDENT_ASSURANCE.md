# CCXLVII independent assurance

Recorded 2026-11-06 8:57 AM CT (`2026-11-06T14:57:00Z`).

## Reviewer

[Independent contract review](bc-74a1875d-ee1e-59f9-9b9e-0f6a8184a6ab) read the contracts at `b5b935763f8c7658dcc1f8aa54d221a4fb7a5a50` and did not edit files. It used the same checkout and interpreter as this session, so it is not a separate runner. Its verdict was NO-GO for merging pull request 180 to `main`.

Findings it reported, and what happened after:

| Finding | Result |
|---|---|
| Confirmed recovery stays `0.00`. The engine has no `CONFIRMED_DISCREPANCY` qualification. | Accepted. Still true. |
| A misapplied payment added dollars on an invoice that already had a rate gap, a duplicate, or an orphan finding. | Reproduced. The payment finding remains, and its exposure is `0.00` when that invoice already holds the dollar event. A lone misapplied payment on a matched invoice is still `100.00` once. |
| An orphan `REVERSAL` was booked as positive exposure. | Reproduced. A reversal with no invoice now has exposure `0.00`. |
| Registry checks were a denylist. `HUMAN_APPROVED`, `LIVE`, and `training=STARTED` could pass. | Reproduced. The registry now allows only `CANDIDATE`, `NOT_VERIFIED`, `NOT_EVALUATED`, `NOT_INSTALLED`, and `training=NOT_STARTED`. |
| An extra `recovered_usd` of `50.00` still passed the scorer. | Reproduced. Any money string that is not in the answer key, other than `0.00`, fails the case. |
| `byte_length` is range-checked and reported `byte_length_verified: false`. The digest covers normalized rows, not source bytes. `HUMAN`, the clock, and `SYNTHETIC_ONLY` are caller-supplied strings. | Still true. Not changed. A caller can label rows synthetic. |
| An unbilled job and a separate orphan invoice can both carry dollars when the invoice does not name that job. | Still true. The engine does not invent that join. |
| `verify_receipt` is an unkeyed SHA-256. `get_model` returned a live registry object. | The lookup now returns a copy. The receipt hash is unchanged. |
| CI was red at `b5b9357`. | The collection repair is `aa49c56`. GitHub `CI` / `test` was SUCCESS on that commit. CLII and CLIV were still running when this note was updated. This later repair has not been rerun on GitHub. |

The reviewer has not re-reviewed these repairs. This session wrote them.

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
