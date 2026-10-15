# OPERATION KUSANAGI XIX — PROJECT SOVEREIGN BACKBONE

Follow-up: [owner analytics repair and current Lovable reconciliation](dashboard-follow-up.md). The original baseline and evidence below remain historical.

Date: 2026-10-15. **FINAL STATUS: PARTIAL — HOLD production qualification.**

Working code is implemented on an isolated branch in the existing repository. There is one canonical API/SQLite worker path in this candidate. The browser-to-native-Qwen success condition has NOT been demonstrated. No merge, production deployment, DNS change, live migration, credential rotation, public tunnel or paid infrastructure was performed.

## Sources and recovered topology

| Item | Exact evidence |
|---|---|
| Canonical backend | `victormart43210-ship-it/Valexii-Aurex` |
| Starting SHA | `c98ca176ee0fb0e2f4a79427d0ee225eca6b0305` |
| Final tested implementation SHA | `183ebffdab99d51c6f5874e307ffedc083f3ead3`; later documentation-only publication commit may differ |
| Website | Same repository, `website/`; React/TypeScript, TanStack Start, Vite; imported in PR21 |
| Website starting SHA | Same c98ca17 baseline |
| Website implementation commit | Local `e980eb5` cherry-picks reviewed lane `fd04e77d1899ad0c4ffc5dfcb480f47ba6f4a216`; included in tested implementation SHA |
| Earlier repairs reused | PR20 source `f78be71ece48f9721c30685c4f6d4abd494e0e20`, inference lane `aa3f866e108e44f8fe0e0f8ce1e12869e98044bc`, website adapter `a989789` |
| Railway project | VALEXII-AUREX `78095d3d-5911-41c8-aa3e-f9ebf5d81054` |
| Railway service | aurex-api `2b51dfe6-2175-4cb0-aac2-eb40ecbc3a1d`, one sfo replica |
| Railway observed source | `integration/kusanagi-xvi-railway` (`57a079f93b947594f1a6f854aa46a6f606f86f76`) — read-only bridge, not this worker |
| Railway observed deployment | `59ca0ec7-e1db-481f-984e-1aadbcfcc15d`, SUCCESS, created 2026-10-14T23:28:34Z; deployed SHA NOT VERIFIED |
| Railway persistence | Connector inventory: NO volumes, NO buckets. No durable production database located |
| Railway domain | `aurex-api-production-c535.up.railway.app`; no custom domains on this service |
| Lovable | `811ffc43-2c8b-4c88-ab4c-4de668d089cb`, Valexii Ai, published; observed latest SHA `24a5328ec63309b4bb0fdb335a0967acbfdfe32d` |
| Website sync | NOT VERIFIED. Newer Lovable /aurex source materially differs from GitHub import; deployment reconciliation required |
| VALEXII.COM DNS | NOT VERIFIED in this operation; not changed |
| Model runtime | No reachable runtime on this environment's loopback 8080/8944; user's Linux host is not accessible. Actual model/version/hardware NOT VERIFIED |

Newer competing convergence branches were recovered without overwriting them. Their incompatible jobs schemas, terminal-result overwrite and evidence replacement were reproduced independently. See `branch-reconciliation.md`. This candidate does not claim all branches consolidated or ownership of unsynchronized Linux work.

## Verification matrix

| Required area | Status | Evidence / limits |
|---|---|---|
| Backend startup | PASS local | Real uvicorn process, HTTP200 liveness; `evidence/local-process-smoke.json` |
| API gateway | PASS controlled | Create/status/result/evidence/cancel contracts tested; current live Railway bridge unchanged |
| Authentication / authorization | PASS controlled | Invalid bearer401, other-owner404, explicit server-derived scope; static credential expiry not implemented |
| Durable job engine | PASS controlled | Real SQLite concurrency, idempotency, transitions, restart/lease recovery tests |
| Worker leases / fencing | PASS controlled | One winner under contention; old fence cannot heartbeat/finalize |
| Crash recovery / retries | PASS controlled | Expired lease reassignment, bounded attempts, failed rows retained; deployment recovery NOT VERIFIED |
| Native Qwen | NOT VERIFIED | No real model request/response/model version obtained |
| Evidence vault | PASS scoped | Atomic result+digest+link, immutable helper, owner filtering, tampering withheld409. Digest proves consistency, not truth or tamperproof disk |
| Website API integration | PASS automated | Server-only client, owner guard, strict schemas, prompt bounds, polling/cancel/results/evidence |
| Owner authentication in browser | NOT RUN | No authenticated preview session exercised |
| Standalone frontend build | PASS | 149 tests/22 files, TypeScript, Vite production build outside Lovable |
| End-to-end real model execution | NOT RUN | Synthetic HTTP transport fixture is separately labeled; unavailable-model real-process smoke passes |
| Independent analytics | PASS bounded helpers/API | Allowlisted events, retention, owner-only aggregation; job counts derived from DB. No live events collected |
| Owner analytics dashboard | NOT RUN / unfinished | Backend endpoint exists; UI lane stopped at usage limit; no visitor claims |
| Structured logging | PASS scoped test | Server-generated correlation ID, route/status/duration; validation input redacted |
| Metrics | PARTIAL | Recorded event/job counts and request elapsed time; capacity/percentiles/SLOs not measured |
| Distributed tracing | NOT RUN / unimplemented | No complete frontend-to-worker trace propagation |
| Backend unit/integration/adversarial suite | PASS | **208 passed, 1 skipped**, one Starlette/httpx deprecation warning; `evidence/backend-tests.txt` |
| Ruff | PASS | `evidence/ruff.txt` |
| Strict Mypy | PASS | 43 source files; `evidence/mypy.txt` |
| Frontend production dependency audit | PASS at run time | 0 reported vulnerabilities; not an assurance of vulnerability absence |
| Hosted CI / deployment previews | NOT VERIFIED / NOT RUN | PR checks prepared; no hosted run result claimed |
| Production backup/restore | NOT RUN | Operator procedure prepared, no live data touched |

The main baseline independently ran 124 tests with 1 skip; recovered XIV repairs ran170. Added coverage is not a claim of increased model intelligence or performance. Native tokens/sec, first-token latency, memory use, p95/p99 and sustainable concurrency were NOT measured.

## Confirmed repairs and implementations

- Eliminated fabricated job success and unsupported PASS evidence from earlier baseline; unavailable legacy jobs remain closed.
- Added atomic owner-scoped idempotency, collision rejection, bounded pagination, non-destructive schema migration and immutable evidence insertion.
- Added worker ownership, lease renewal, monotonic fencing, cancellation fencing, deadlines and bounded retries on existing SQLite jobs.
- Added literal-loopback inference subprocess with total time limit and no paid fallback or tool execution.
- Added credential-derived API scopes, size limits, redacted validation errors, bounded per-process rate controls and honest readiness.
- Added owner-only website command interface and standalone frontend CI checks without replacing artwork/navigation.
- Independent review found and verified repairs for Unicode response serialization crash, corrupted result exposure, invalid auth readiness, and disabled-execution readiness.
- Coordinator final contract check fixed evidence capability spelling (`local-inference`). This narrow repair passed regression/full tests and coordinator rerun; no additional independent review is claimed.

## Evidence and review limits

See `independent-review.md`, before/after JSON, focused test log and final coordinator probe. Native review was a separate agent with distinct probes, not a third-party audit or proven different-model review. Astral managed route was blocked by `sessions-directory-unavailable`; no verified Astral execution is claimed. The reviewer wrote its report and passed31 focused tests before a later usage-limit error stopped further work. Final coordinator checks are labeled separately.

Implementation lanes and repairs are committed locally. Publication is a draft-review action only; the PR URL and remote commit are reported with the delivery. There is no merge/deployment authorization. Changed-file inventory is in `evidence/changed-files.txt`; reproducible commands and release gates in `operations.md`.

## Remaining blockers and next wave

1. Reconcile the newer Lovable source and the competing API/workflow branch schemas into one accepted source. Do not overwrite either or merge incompatible jobs tables.
2. Obtain access to the owner-controlled native Qwen runtime, verify model identity, then run the requested real prompt through API→worker→evidence→authenticated website. Keep loopback ports private.
3. Select and approve a persistent single-host deployment topology. Current Railway has no volume; no cross-host SQLite coordination is supported.
4. Finish owner dashboard and consent-controlled website collection; keep event counts distinct from visitors/cohorts.
5. Verify expiring owner sessions, production token lifecycle, proxy-aware rate controls, backup/restore, outage recovery, and controlled preview/rollback. CI success is not deployment approval.

**PRODUCTION MIGRATION READINESS: HOLD.** Acknowledged-job persistence, fencing and no false completion have controlled-test evidence; live service objectives remain unqualified. BCXMET protection authority is unchanged; ORB MOTION AUTHORITY = NONE.
