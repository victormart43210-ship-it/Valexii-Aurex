# XIX branch reconciliation — 2026-10-15

Verdict: **HOLD wholesale convergence; publish only a clearly scoped draft after local verification.** No repository modifications or production actions were performed by this review.

## Exact sources

- Main: `c98ca176ee0fb0e2f4a79427d0ee225eca6b0305`.
- Local XIX committed parent: `246231f50152ece3ff6d172a4634bb822bf2f779`; API, database, worker and HTTP controls additionally have uncommitted changes, so this SHA does not identify final XIX behavior.
- `integration/sovereign-convergence-audit-20261015`: `745520d9fca9f258fb4ba6029ca0a51e6d09bd68`.
- `integration/kusanagi-xxix-sovereign-pipeline`: `ca55d1f6d126173c32ad81e7a9321b541ce16057`.
- `integration/one-mainline-merge`: `382320e6c53d40cd4603d531623683f2f52c1b58`.
- Merge-base local parent versus audit: main above. Committed divergence: 4 local / 33 audit commits. Audit already contains a merge of one-mainline, but merge history does not establish preserved functionality.

## Source findings and independently reproduced failures

The audit branch itself says HOLD, inventory only, in `docs/SOVEREIGN_CONVERGENCE_20261015.md`. Its `docs/kusanagi-xxvi/branch-reconciliation.md` explicitly warns against wholesale merges and duplicate engines.

| Boundary | Audit branch | Current local XIX | Consequence |
|---|---|---|---|
| Durable jobs | `aurex/database.py`: params_json, ISO timestamps, lowercase states | Same baseline evolved to schema version 2, scoped owner IDs, unique idempotency, fenced leases | Preserve tested local path rather than replace with audit metadata-only leases |
| Second engine | `aurex_workflows/core.py`: payload_json, REAL timestamps, uppercase states, same table name jobs | No second workflow engine | Not a compatible shared database or automatic merge |
| Recovery | Workflow engine operator-confirmed RUNNING to FAILED_INTERRUPTED, requires stopped workers | Worker lease expiry, fence advancement, bounded attempts | Different semantics; do not run both recovery paths on same DB |
| API | Audit POST jobs remains 503 fail-closed; single service auth | Local enabled local_inference plus scoped token mapping | API and auth contracts must be reconciled explicitly |
| Evidence | Audit INSERT OR REPLACE, no ownership | Local immutable helper, owner scope, job links | Audit would regress integrity protections |
| Website | Audit includes separate read-only xxv bridge and fixture frontend | Existing React website plus protected integration | Do not deploy second bridge/frontend as canonical website |

A standard-library Python probe loaded exact audit files using `git show`, executed modules in isolation, and used temporary SQLite files. Results:

```
API database -> Workflow submit: OperationalError table jobs has 16 columns but 7 values were supplied
Workflow database -> API create: OperationalError table jobs has no column named idempotency_key
Terminal overwrite: cancelled None
Evidence replacement: new
```

These are observed failures, not inferred from documentation. Reproduction: load audit `aurex/database.py` and `aurex_workflows/core.py`; initialize one DB via get_db then call WorkflowEngine.submit, reverse initialization order then call create_job; on a fresh API DB update a job to succeeded with a result then cancelled; record the same evidence ID twice with different digest/summary.

One-mainline's terminal-state guard is absent in audit's final database implementation despite its merge ancestry. It also allows queued directly to succeeded and same-terminal-state rewrites; its select/update is not one fenced transaction. Do not substitute it for local guarded transitions.

One-mainline additionally removes model_forge CLI behavior (`demo` becomes pass, manifest branch and main entry removed), Witness dataclass/json_ready, madlad_text_candidate and optional_trace. These are real deletions, not useful convergence fixes. Preserve existing behavior unless independently justified.

## Safe consolidation approach

1. Finish and independently test one local canonical API/database/worker path; record final committed SHA. Draft PR must disclose the unresolved competing branch, not claim all branches consolidated.
2. Keep audit and one-mainline remote branches untouched. Preserve their SHA provenance in PR documentation. A local whole-branch merge is technically possible with conflict resolution, but accepting both engines would violate the one-engine requirement and break database interoperability; do not do it merely for merge-history appearance.
3. Selectively reuse compatible content: workflow failure/negative-test scenarios, local inference redirect-denial tests, read-only pagination constraints, Chromebook environment inventory, workflow_dispatch CI entry. Existing local implementation already supplies several protections; avoid duplicate modules.
4. `ExecutionRecord`/trace metadata can inform a later canonical schema contract, but is scaffolding, not an operational distributed trace. Audit trace_context sets contextvars without token/reset lifecycle; review before reuse.
5. Map useful workflow kinds/planning into the canonical worker only when explicitly supported and tested. Retain their history/source, but do not activate legacy WorkflowEngine or introduce another SQLite jobs schema.
6. Before any migration of actual legacy workflow DB, require read-only inventory and a tested non-destructive import procedure preserving IDs/events and distinguishing historical evidence. No such migration was executed here.
7. Preserve full existing website and server-only credential boundary. The xxv bridge is read-only and has a different capability schema; it is not a drop-in replacement for the protected React integration.

## Scope limits

Only repository source and isolated temporary SQLite probes were inspected. No live Railway, Qwen, production website, CI execution, or deployed-schema verification was performed by this reviewer. Audit deployment statements remain prior branch claims requiring coordinator-side verification. Current local XIX correctness still requires its assigned independent verification and final tests; this comparison is not a release approval.
