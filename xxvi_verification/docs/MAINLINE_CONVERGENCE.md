# One-mainline convergence and independent verification

**Canonical target:** `victormart43210-ship-it/Valexii-Aurex`, primary `main`. Confirm `git remote -v`, `git branch -avv`, `git status --short`, and `git fetch --prune` before touching anything. Do not assume local `integration/kusanagi-xxii-governed-execution` is identical to GitHub `main`.

## Required inventory and provenance
1. Record main SHA, local integration SHA, all remote branch names and tips, open PRs, commits, changed file paths, CI statuses, and ownership. Compare by `git merge-base`, `git log --left-right --cherry-pick`, and `git diff --stat`.
2. Reconcile merged website PR #21 and security PR #22 independently by actual commit SHA and file content; prior reports are not proof of integration. Compare Copilot's `web_adapter.py` and tests, Jules adversarial findings, Lovable website source, and existing Railway service. **No wholesale blind cherry-picks**.
3. Freeze contracts: one API contract, one job authority owner, one durable database, zero-dollar default, no synthetic evidence, no self-signed user-provided trust root, one release provenance ledger. Resolve ownership and tenant scoping before any public jobs endpoint.
4. Apply changes in a temporary branch based on the current main, keep independent verifier worktree, serialize merges, and require green CI plus exact-SHA verification before asking for permission to merge. Never delete branches before verifying reachable commits and recording their SHAs.
5. GitHub Actions should test Python, JavaScript build (where relevant), auth, bad-token, missing DB, pagination after deletion, replay/idempotency, concurrent jobs, signature verification with trusted keys, worker absent returns 503, evidence immutability, accessibility, and privacy leaks. Label unexecuted tests NOT RUN.
6. Deploy only after explicit approval, with rollback instructions, migration strategy, Railway volume or managed DB, secret provisioning, rate limits, observability, and authenticated server-side website proxy.

## Git safety
Never use `git add .`, `git clean -fd`, `git push --force`, delete untracked directories, merge unreviewed branches, or mutate secrets. Existing `docs/superpowers`, `website-tools`, local backups, and staged XXV files may be user work. Preserve them.

## Roles
Copilot: implementation in the canonical repo on scoped branch. Jules: independent adversarial verification, not sole witness. ChatGPT: reconcile contracts, CI and evidence. Lovable: website UI changes only against confirmed canonical website source; no secret in browser. Independent security reviewer: checks signer trust, concurrency, tenancy, and no synthetic success. All report PASS/FAIL/NOT RUN/NOT VERIFIED by exact SHA.

## Production gate
Blocked until proven: website session→server-side proxy→Railway bearer authentication→persisted workflow metadata, with real durable DB, no client-exposed bearer, correct tenancy and non-mutating access. The existing XXV browser token input is a local preview only.
