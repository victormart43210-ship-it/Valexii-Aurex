# Prioritized findings

| ID / severity | Exact issue and evidence | Remediation / verification |
|---|---|---|
| K13-01 P0 | main api.py create_job_endpoint writes PASS and succeeded without worker; new test failed | Repaired to 503 with zero side effects; requires independent review; real worker still missing |
| K13-02 P0 | admission.py accepts self-supplied Ed25519 key as independent verification | Default HOLD + operator pin + signed freshness; test unknown/revoked/stale/tamper; operational trust governance outstanding |
| K13-03 P1 | database.py permits arbitrary/terminal transitions and erases prior result | Transactional transition allowlist; restart/result preservation tests pass; concurrency expansion still required |
| K13-04 P1 | health endpoint accepted no bearer | Authenticate both aliases; invalid/missing/valid tests |
| K13-05 P1 | Unbounded nested job input / body | Scalar constraints and 16KiB streamed request bound; adversarial input tests pass |
| K13-06 P1 | Website CapId regex rejects backend underscores | Backend hyphen IDs; actual payload-to-schema probe accepts corrected result |
| K13-07 P1 | Website old health checker expects nonexistent health.capabilities | Unapplied website patch uses canonical health + capabilities endpoints; focused test passes |
| K13-08 P1 | Website reads full body before checking size; 16-char token minimum disagrees with backend | Unapplied patch bounds stream bytes and uses 32-char minimum; 3 tests pass |
| K13-09 P1 | No principal ownership in shared-token backend | BLOCKED for public/multi-user operation; design authenticated identity propagation before new jobs |
| K13-10 P1 | No unique idempotency constraint; evidence INSERT OR REPLACE; /tmp database default | Still open; do not enable worker before durable transactional job/evidence design |
| K13-11 P1 | Website upstream URL guard is lexical, not DNS/egress-enforced | Still open; constrain approved host and resolved network destinations before deployment |
| K13-12 P1 | External adapters do not universally call BudgetGuard | Still open; no universal $0.00 guarantee; no paid calls executed |
| K13-13 P1 | Candidate website repo is LICENSE-only; sync/published SHA unproved | Obtain exact linked GitHub owner/repo/branch and reconcile Lovable SHA before applying patch |
| K13-14 P1 | No reachable Linux/native Qwen, no API→model worker | BLOCKED; recover phases 44/45 and run local/staging tests |
| K13-15 P2 | OpenAPI errors/status/pagination/security metadata differ from website draft | Reconcile contract and consumer tests; avoid claiming OpenAPI compliance |
| K13-16 P2 | VIII/IX/X commit descriptions claim repairs but trees are identical | Retain tree evidence; qualify progress from diffs/tests, not messages |

P0 here denotes a release-blocking integrity defect, not a claim of an exploited production service. No production penetration test or customer-data access occurred.
