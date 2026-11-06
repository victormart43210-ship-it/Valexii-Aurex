# CCXIX Source Reconciliation

Verified with `git` against `victormart43210-ship-it/Valexii-Aurex` on 2026-11-05.

| Ref | SHA |
|---|---|
| `origin/main` | `99af5fd8a2c1340bcf5d2eda03bb6dbe65e5a661` |
| PR #159 head | `17a6cbf2a502f46f866d0fe1693d4c2a7f26ef70` |
| `b12490bc` (stream limit) | ancestor of PR #159 head: **yes** |
| PR #160 head | `e377e614286eac327a94458c404192161692c166` |
| `b12490bc` ancestor of PR #160: | **no** |

## Ancestry (verified)

```
main 99af5fd
 └─ 1888aa1 ─ df7db18   (shared base of #159 and #160)
      ├─ d6da58e ─ df71cc9 ─ 01b4209 ─ b12490b ─ 17a6cbf   PR #159 (Jules)
      └─ f35a9bf ─ e377e61                                 PR #160 (Copilot, draft)
```

**Correction to the stated dependency chain:** #160 is *not* stacked on #159. They are siblings
that diverge at `df7db18`. Both are 100% unmerged into main (#159 merge-base with main is main).

## Conflicts (`git merge-tree pr159 pr160`)

Content conflicts: `aurex/dispater_api.py`, `aurex/dispater_store.py` (add/add),
`docs/dispater/DISPATER_E2E_VERIFICATION.md`, `docs/dispater/DISPATER_SECURITY_GATES.md`,
`docs/operations/JULES_CHATGPT_HANDOFF.json`.

Both PRs independently implement tenant authorization and a durable store, so reconciling them is a
design decision (which store/auth implementation is canonical), not a mechanical merge.
**Not resolved in this branch; owner/Jules decision required.**

## CCXVIII

No CCXVIII PR or branch was found. `origin/jules-15884507567797505787-a31f191f` exists but is
unreviewed and not identified as CCXVIII.

## This branch

`copilot/kusanagi-ccxix-mainline`, based on PR #159 head `17a6cbf`, plus one commit:
the D-1 fix (below). PR #160 was **not** merged in.

## Defect D-1 (confirmed, fixed)

`limit_body` was a router dependency. FastAPI parses the body before dependencies run, so a 20 MB
chunked upload was fully consumed (20,971,520 bytes read) and answered **422**, not 413.
Fix: `BodyLimitMiddleware` (pure ASGI) bounds the raw stream, also for dishonest/missing
Content-Length. Tests: `tests/test_dispater_body_limit.py` (7).
