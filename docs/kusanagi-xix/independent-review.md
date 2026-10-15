# KUSANAGI XIX independent backend review

Reviewed 2026-10-15 UTC by a separate native review agent. This is a code and controlled-fixture review, not Astral execution, a third-party audit, or evidence of model-family diversity. No production files were changed by this reviewer.

## Verdict

PARTIAL: the specifically attacked backend integrity boundaries pass the post-repair probes. Production readiness and real native Qwen execution are NOT VERIFIED. The reviewed worktree contained uncommitted changes; `extra-after.json` records its HEAD and SHA-256 for each reviewed implementation file. HEAD alone does not identify the reviewed content.

## Independently reproduced defects and repairs

| Finding | Before | After | Evidence |
|---|---|---|---|
| Stored result tampering was returned by results API despite failed digest | HTTP 200 with altered text | HTTP 409, no result returned | probe-before.json / probe-after.json |
| Invalid user-token configuration reported ready while requests failed | readiness 200 / auth 503 | readiness 503 / auth 503 | same |
| A 45KB UTF-8 model answer exceeded ASCII-escaped serialization budget and escaped worker handling | uncaught ValueError; job running | worker returns true; job succeeded | same; actual spawned subprocess and synthetic local HTTP fixture |
| Disabled execution advertised ready | readiness 200 / submission 503 | both 503 | extra-after.json; independently rerun readiness regression |

## Positive adversarial results

- PASS: twelve simultaneous worker acquisition attempts produce exactly one claim.
- PASS: an expired worker cannot commit after a replacement acquires a higher fence.
- PASS: other user's result endpoint returns 404; invalid bearer returns 401.
- PASS: result-byte tampering is detected as evidence integrity FAIL; result retrieval rejects it.
- PASS: disabled execution and a worker without model configuration both make readiness return 503.
- PASS: focused existing regression suite independently rerun: **31 passed**, one dependency deprecation warning; see focused-after.txt. This includes atomic evidence failure rollback, cancellation fencing, retry exhaustion, owner-scoped idempotency, legacy migration rollback, and bounded request controls.

Independent probe command (run from repository):

```sh
PYTHONPATH=. /workspace/scratch/9b8b721f1090/aurex-xix-venv/bin/python /workspace/scratch/9b8b721f1090/xix-independent-review/probe.py
```

## Remaining limitations and deployment gates

1. P2 operational: process-local rate limiting keys socket peer IP and covers health routes. Reverse-proxy clients can share a 120/min bucket; multi-process limits are independent. Configure and test actual proxy topology and probe frequency before production.
2. NOT VERIFIED: native Qwen model identity, inference quality, live model availability, cloud-to-local connectivity, and browser-to-real-model execution. Test fixture output is synthetic. Readiness explicitly reports model NOT VERIFIED; configured worker is not a live model probe.
3. PARTIAL: static configured credentials map to owner scopes and can be removed by an operator; token expiry, managed rotation, and authenticated browser session lifecycle are outside this backend review.
4. PARTIAL: SQLite worker coordination requires one shared local durable database. Cross-host SQLite sharing and production backup/restore have not been validated. Default temporary database path is not a production persistence configuration.
5. PARTIAL: evidence digest binds stored result bytes, not factual truth or independent witness authority. An attacker able to rewrite both database result and digest is outside this digest-only integrity boundary. Model outputs remain explicitly advisory.
6. PARTIAL: retries are bounded but immediate, with no backoff; terminal failed rows retain failure codes rather than providing a separate dead-letter operations UI. Active-job graceful shutdown may wait on the bounded inference cycle.
7. NOT RUN: full production deployment, DNS migration, production data migration, paid providers, and public inference exposure. None is authorized by this review.

No additional high-severity defect was demonstrated in this bounded review after the repairs. This is not a claim that all security flaws are absent. Frontend implementation and full-suite release checks belong to the coordinator's separate evidence.
