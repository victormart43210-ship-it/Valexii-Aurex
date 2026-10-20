# OPERATION KUSANAGI CVI — MAINLINE PR CONVERGENCE
**October 19, 2026 · ONE canonical AUREX repository · SOURCE STAGED / RELEASE HOLD**

## Current inventory and authority
- Canonical target `main` baseline: `df0654390049118a142ec3b3356f0f40b4789fe4`.
- GitHub returned **55 open PRs** in `docs/convergence/open_pr_inventory_20261019.json`.
- **17/55 reported unmergeable** at inventory time; **7/55 were not drafts**. GitHub mergeability is NOT independent test evidence.
- Three explicit stacked dependencies (must not flatten blindly): `#72 → #82`, `#84 → #85 → #86`.
- All remaining PRs are *unadmitted*, regardless of mergeability. Historical draft claims of ADMIT, 100%, or passed tests require new exact-SHA independent witness.
- **NO merge into main, no CI green claim, no Railway/Lovable/Cloudflare deploy, no Hetzner changes, no model inference or paid credits** performed in this convergence operation.

## Source actually staged on THIS integration branch
The following PRs were selectively staged as candidate changes without merging the original PR heads, and their original branches remain open:

| PR | Stage type | Relevant changes |
| --- | --- | --- |
| #43 | exact-blob additive docs | Platform waves, governance, release gates |
| #45 | exact-blob additive docs | CI/exact-SHA mainline merge policy |
| #73 | exact-blob additive docs | Speed/Altitude/Depth/Range outcome lock |
| #92 | exact-blob additive source | Hetzner GitLab CI proposal, **NOT active** |
| #93 | source snapshot/mirror changes | Strict five-GET frontend transport tests and schemas in **historical GitHub website mirror** |
| #95 | source snapshot, API | Public /health, service-authenticated /v1/health, Docker smoke tests |
| #94 | selective API synthesis plus source snapshot | Owner-only, opt-in ORCA R8 metadata sync (disabled by default) |
| #60 | selective API synthesis plus exact tests | ASCII/length/whitespace-safe Bearer authentication |
| #83 | selective API synthesis plus exact source snapshot | Lease-scoped persisted worker failure, redacted errors |
| #61 | source snapshot plus selective dependency | Server-token egress origin pinning, strict destination and token checks |
| #62 | exact additive source | Offline CI preflight script and tests; no privileged actions |
| #79 | exact additive source | Read-only Railway five-GET operator probe and tests |

**12 PRs have contributed source to this candidate. This is NOT 12 successfully merged PRs.**
Some snapshots may still contain integration failures, especially across source-only website, persisted-worker state, and authentication defaults. The original PR titles and bodies must remain accessible until independent verification closes these gates. Other 43 open PRs have **not** been integrated into this branch.

### Reconciled overlap
`aurex/api.py` is ONE file in the candidate. It combines:
- PR #60's fail-closed Unicode-safe Bearer handling;
- PR #95's authenticated application health, public infrastructure health;
- PR #94's separate status-ingest writer and auth-protected owner-read router;
- PR #83's lease-scoped `fail_job` persistence on probe failure.
Do not wholesale copy another PR's `aurex/api.py` over this synthesis.

`pyproject.toml` includes PR #61's optional server-only website HTTPX extra, with other main dependencies preserved.

The GitHub `website/` tree is **not the authoritative Lovable published source**. This branch only reconciles a historical source copy and must not be pushed into Lovable wholesale. Real Lovable project last checked at `73f800bc43e32b3ebb907131480658262bc460ef`, publication-to-source identity unproven.

## Remaining PR groups: admission path
1. **Core authentication / reliability / deployment:** #72 (bridge) → #82 (stacked), #66, #56, #37, #44, #41, #39, #38, #32, #30, #29, #28, #27, #20. Check main features first to avoid overwriting already merged corrected code.
2. **Qwen/APIS and experimental model research:** #84 → #85 → #86, #81, #63, #51, #50, #13, #12, #11, #8, #5, #4, #3. Branch `aurex-mainline-convergence-5126581965977077235` is **29 ahead / 117 behind main** and contains known weak Qwen evaluator semantics; no wholesale merge.
3. **Financial / enterprise evidence:** #77, #80, #70, #67, #89, #90, #88. #89 and #88 share `aurex/folio_index.py` and its tests. Finance must remain synthetic, typed, Decimal-based, source-linked, human-review HOLD.
4. **Docs and source alignment:** #78, #76, #42, #34, #31, #36 and remaining older documentary change surfaces. Avoid merging obsolete progress assertions as if current.

## Exact next verification and integration sequence
**G0 — Scope:** Freeze this candidate head SHA, write a deterministic file-level ownership manifest, and compare every staged source file to the original PR SHA; record deliberately synthesized API/pyproject exceptions.
**G1 — Offline exact-head tests on isolated runner:**
```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  tests/test_authentication_boundary.py \
  tests/test_worker_failure_persistence.py \
  tests/test_orca_r8_sync.py \
  tests/test_kusanagi_workflow.py \
  tests/test_aurex_readonly_probe.py \
  tests/test_offline_preflight.py \
  integrations/kusanagi-xvi/tests/test_five_get_frontend_contract.py
ruff check .
mypy aurex
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
# On trusted isolated runner, separate canonical Docker build + smoke:
docker build --tag aurex-cvi-candidate:verify .
# In historical website mirror:
cd website && bun install --frozen-lockfile && bunx vitest run && bunx tsc --noEmit && bun run build
```
These commands are **NOT RUN at this candidate SHA**. Never mark PASS without actual exit codes and provenance.

**G2 — Test fixes / adversarial witness:** Resolve errors on this candidate only. Require unrelated reviewer/instrument for untrusted content, ACL/auth bypass, replay, race, wrong egress domain, SQLite restart, malformed JSON, source clock skew, and cached owner-only metadata. No self witness.

**G3 — Review launch:** Activate existing Hetzner GitLab Runner only after the owner has verified billing/power/runner auth. GitHub hosted runs previously showed zero allocated runner steps; that is not code-test execution. CI template in #92 is a *proposal*, not an activated job.

**G4 — Serialized mainline:** Each accepted module must be committed at verified exact SHA; one merge at a time after approved independent CI, current-main recheck and tests. After admission, close/reconcile superseded PRs explicitly, preserving their history. NEVER force merge the whole 55-PR backlog.

**G5 — Separate production deployment:** Railway is still running the older five-GET read-only bridge (source `57a079f93b947594f1a6f854aa46a6f606f86f76`). Persistent DB volume changes are staged, not live. Cloudflare website-to-Railway attribution, Qwen model response, and ORCA exporter sync remain NOT VERIFIED. Deploy only after independent exact-SHA/rollback proof and a separate owner-approved release.

## Known claims requiring care
- GH source/PR SHA is not a CI test receipt.
- Separate local synthetic Python runs are not merged-head independent witness.
- A healthy HTTP 200 is not frontend-origin attribution or verified AUREX intelligence.
- Cloud-hosted/website source must not display local private ORCA financial records.
- No paid inference, uploads, DNS changes, private file exports, or public exposure.

**Governing rules:** Evidence → Qualification → Reality → Authority → Effect.
The system may never be its own sole witness. Unknown ≠ PASS. Stale ≠ healthy.
**Current gate: SOURCE STAGED / TEST NOT RUN / MAIN MERGE HOLD / PRODUCTION HOLD.**
