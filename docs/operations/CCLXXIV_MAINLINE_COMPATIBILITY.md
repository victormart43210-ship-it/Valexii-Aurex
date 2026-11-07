# CCLXXIV mainline compatibility

Verified tree `c403bf99e07e22c576174b494a37a6177924dbed`. Canonical `main` `061b97022797013ccd1395a377b9489e59ba83f3` (merge of pull request 194). Merge base `f381db7cd121d76f0df9f67a8a5e2547733fe33d`.

`git merge-tree --write-tree HEAD origin/main` exited 0. The resulting tree was not checked out. The branch was not rebased and history was not rewritten. `main` was not updated.

The pull request base remains `cursor/kusanagi-cclxix-fullstack-ascendancy-4082`. GitHub reports the pull request mergeable. Bringing `main` into this branch is not required: there is no content conflict, and doing so would put pull request 194's other files into a review whose base is not `main`.

Compared with `main` at that SHA:

- `aurex/dispater_api.py`, `aurex/dispater_intelligence.py`, `aurex/xaeli_staging.py`, and `aurex/adapters/` are the same bytes.
- This branch adds `pillow>=13.0.0,<14` and the `/v1/manuscript-forensics` router. `main` has neither, so there is no second imaging package and no second financial engine.
- Authentication for the new router is the existing service bearer. The laboratory flag is a separate switch and defaults off.

No route collision, missing import, or authority-boundary change was found in that comparison. This is a tree comparison by the implementing session, not an independent review.
