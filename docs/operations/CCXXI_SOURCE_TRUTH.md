# CCXXI Source Truth

Revalidated with `git` on 2026-11-05. Canonical repo: `victormart43210-ship-it/Valexii-Aurex`.

| Ref | SHA |
|---|---|
| `origin/main` | `99af5fd8a2c1340bcf5d2eda03bb6dbe65e5a661` |
| PR #159 head (moved since CCXIX) | `a1d4856c0145ce46727bf178f0f3178de4ad1f22` ("CCXVIII storage and oracle hardening") |
| PR #160 head | `e377e614286eac327a94458c404192161692c166` |
| PR #161 head (CCXIX) | `62f2f4c9c5d42dfda6488f0b0932d25cc62ded96` |

Ancestry: #159 and #160 fork from `df7db18` (siblings; #160 is not stacked on #159).
#161 is stacked on #159 `17a6cbf`; #159 has since gained `a1d4856`.
The CCXVIII commit referenced earlier **is** now retrievable: it is `a1d4856` on #159.
No separate CCXX branch/PR was found.

## What each branch actually contributes (diffed, not assumed)

| Area | #159 | #160 | #161 |
|---|---|---|---|
| `dispater_intelligence.py` | engine | **identical** to #159 | – |
| Auth/tenant code in `dispater_api.py` | present | **identical** to #159 | – |
| `limit_body` | body cached into memory (bypassable) | header-only check | raw-ASGI `BodyLimitMiddleware` |
| `dispater_store.py` | mount validation, checkpoint, `/data` default | **regression:** hard-coded `/tmp`, no validation | inherits #159 |
| Tests | oracle + authority invariants | `tests/test_dispater_security.py` (24 tests) | `test_dispater_body_limit.py` |

So the "five-file conflict" is smaller than it looked: auth and engine are the same code in both.
Real choices were only the store and the limiter.

## Decisions (by verified behaviour, not ownership)

1. **Store:** #159's version (strictly more protective than #160's `/tmp` default), then hardened (below).
2. **Limiter:** #161's middleware. Both prior `limit_body` variants were bypassable; the #159 cached-body
   variant buffers up to the entire upload before checking.
3. **Tests:** keep all of #160's security tests and #159's oracle tests; they pass on the merged code.
4. **Docs conflicts** (`E2E_VERIFICATION`, `SECURITY_GATES`, `JULES_CHATGPT_HANDOFF.json`): took #159's
   versions; #160's non-conflicting docs were retained. #160's differing doc text for those 3 files was not carried over.

## New defects found and fixed in CCXXI (each with regression tests)

- **D-2** Ephemeral-path guard used unresolved `startswith("/tmp")` (missed `/var/tmp`, `/dev/shm`, symlinks), and was opt-in only. Now uses `realpath`; a Railway runtime (`RAILWAY_ENVIRONMENT[_NAME]`) requires persistence unless `AUREX_DISPATER_REQUIRE_PERSISTENT=0`. **Behaviour change:** a Railway deploy with no volume now fails closed.
- **D-3** Schema init cache keyed by path: a replaced/deleted DB file was never re-initialised. Removed.
- **D-4** `synchronous` not set under WAL. Now `FULL`; WAL mode is verified.

## Known limitations (not fixed)

- Receipt hash is unkeyed; someone with DB write access can recompute it. Needs HMAC/signing.
- No wall-clock slow-upload timeout in the app (proxy/server concern).
- Railway env-var heuristic not verified against Railway docs this session.
- #160's own commit history for store/tests is preserved via merge; its store file content is not.
