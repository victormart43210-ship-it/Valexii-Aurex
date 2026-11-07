# CCLXXIII Cursor assurance report

Pull request 193. Production HOLD. Financial authority NONE. The manuscript laboratory was not activated.

## Git state

| Item | SHA or value |
| --- | --- |
| Branch | `cursor/kusanagi-cclxx-forensic-ascendancy-4082` |
| PR base | `cursor/kusanagi-cclxix-fullstack-ascendancy-4082` at `f381db7cd121d76f0df9f67a8a5e2547733fe33d` |
| Implementation | `64dadbfd673186fbe65bc653a4658d866178ca8a` |
| Evidence note | `2812c8a4f22bf66d4b1e87d11527abf4fbfce32c` |
| Tested tree | `b6c35efbb8514f6b64c948c852cbb5fda48ac0a0` |
| `main` | `061b97022797013ccd1395a377b9489e59ba83f3` |
| Merge base with `main` | `f381db7cd121d76f0df9f67a8a5e2547733fe33d` |

`2812c8a` differs from `353430a` only in four documentation files. It does not change the laboratory. GitHub Actions on `2812c8a` completed success by 6:35 PM CT: offline-practice at 6:33 PM, both CI test jobs and integration at 6:34 PM, docker-build-and-smoke at 6:34 PM, and verify at 6:35 PM. Each run's `headSha` is `2812c8a4f22bf66d4b1e87d11527abf4fbfce32c`. That pass is not a pass for `353430a` and it is not a pass for `b6c35ef`.

`b6c35ef` adds the gate tests and does not change the laboratory implementation. `main` moved through pull request 194. `git merge-tree --write-tree` against that `main` exited 0. The result was not checked out, and this branch was not rebased.

The working tree was clean at the test run.

## Review

No route returns a decipherment. `recovered_text` stays null. Templates say `NOT_ESTABLISHED`. The laboratory does not call a model. It does not store an image and it does not read DISPATER tenants. A filename is kept only as a label after the last slash. PDF bytes are hashed and not rasterized. An oversized PNG is refused. The service token remains server-side.

`GET /v1/manuscript-forensics/status` answers while the laboratory is off. The body says `enabled: false` and contains no image. Examine, spectral, and template routes return HTTP 403 unless the variable is exactly `enabled`.

No production defect was demonstrated, so no production code was changed.

## Gate

Values covered on `b6c35ef`: unset, empty, `disabled`, `ENABLED`, `1`, `true`, leading space, and trailing space. Examine, spectral, and templates all returned 403. Status stayed enabled false. The exact value `enabled` remains the only opener, and it was not set in this session.

The Docker image workflow does not set `AUREX_MANUSCRIPT_FORENSICS`. No startup command in the canonical Dockerfile enables it.

## Qwen

Status: `LIVE_QWEN_NOT_VERIFIED`.

Staging and operator flags were unset. `AUREX_QWEN_BASE_URL` was unset. `http://127.0.0.1:8080/v1/models` and `http://127.0.0.1:8080/health` returned `URLError`. The private Railway host was not called. No model text was received. Paid inference stayed off.

## Tests on `b6c35ef`

About 7:03 PM CT, clean tree:

- `python3 -m ruff check .` exit 0
- `python3 -m mypy aurex` exit 0
- `python3 -m pytest -q --tb=line` exit 0: 789 passed, 1 skipped
- website `npx tsc --noEmit` exit 0
- website `npx vitest run` exit 0: 169 passed
- `docker` is not installed here

GitHub Actions on `b6c35ef` had not run at the time of this report.

## Decision

`HOLD_WITH_BLOCKERS`. Do not merge. Do not deploy. Do not set the laboratory flag.
