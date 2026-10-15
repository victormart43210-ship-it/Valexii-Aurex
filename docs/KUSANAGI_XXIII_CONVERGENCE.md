# VALEXII.AI — AUREX/OX KUSANAGI XXIII convergence

## Objective
One existing GitHub repository (`Valexii-Aurex`), one evidence-oriented backend, separately governed website and app clients. Consolidate previous ZIPs **by their verified effects**, not by blindly copying all historical files into the repository.

## Highest-impact order (engineering estimates, not measured business outcomes)

| Priority | Previously delivered work | Evidence in conversation | Impact | Immediate gate |
|---|---|---|---|---|
| P0 | KUSANAGI XVI–XVII Railway bridge / website contract | 8 contract tests and a prior authenticated owner diagnostic; current production deployment unchanged | Website reachability; shared API boundary | Verify deployed SHA, auth, OpenAPI contract, website origin and current CI |
| P0 | KUSANAGI XIX–XXII SQLite workflows + Qwen local adapter | 48 local tests; live Qwen answer `4` through guarded adapter; live **workflow** not yet tested | Turns local inference into controlled, auditable jobs | Live approved workflow, crash recovery, adversarial tests, durable evidence |
| P0 | CI/convergence/provenance work | Recent GitHub CI failures reported on multiple branches; exact failure cause not yet diagnosed | Trustworthy deploy/release path | Inspect Actions job logs; fix actual root cause; green exact-SHA CI |
| P1 | Phase 45–48 authority/evidence/overlay and supervisor ZIPs | Artifacts exist, no evidence here that all were installed or merged | Prevents model self-witness, keeps evidence distinct from authority | Contract comparison, source inventory, independent tests before selective porting |
| P1 | Phase 52–53 website backend access/private gateway | ZIP artifacts exist; current deployed admission unknown | Secure browser-to-backend connection | Auth boundary, CORS, no public bearer secret, fail-closed responses |
| P1 | Phase 57 website workspace + website source handoffs | Website bundles present; deployment and feature state not proven | UX discoverability, XAELI experiences | Verify current Lovable source and exact deployed version; stage changes only |
| P2 | Phase 29–30 local proxy and 43–44 native inference gate | Prior artifacts exist; local inference is now independently demonstrated | Dev ergonomics / local execution | Avoid parallel competing proxy/adapter stacks |
| P2 | Command center, training, Archify/Ubertooth/Brain Trust proposals | Bundles/handoffs exist, implementation status varies | Future app/industrial capabilities | Require permissions, threat model, measured efficacy and model-independent adjudication |

**Important:** The ranking is a prioritization judgment based on available evidence. No production speed, retention, revenue, or security efficacy uplift has been measured.

## Canonical architecture

`Client (website or BCXMET/MEDAURUS app) → authenticated gateway → approved workflow → local or authorized model → immutable evidence fingerprint → independent qualification → reality check → authority decision → effect`.

- **Evidence → Qualification → Reality → Authority → Effect** governs every action.
- **ROTAS** reverse audit: Result → Authority → Truth → Admissibility → Source.
- No system or model can be its own sole witness. `verified=False`, `authority_granted=False` for raw Qwen output.
- Browser must never receive backend secrets, localhost URLs, or privileged job-approval tokens.
- A local llama.cpp server on Chromebook is **not reachable by Railway/VALEXII.COM**. Hosted model access requires a separately designed, authenticated, reachable inference deployment or owner-mediated path.
- Railway production must not inherit an implicit zero-auth public inference endpoint.
- Website should show capability availability honestly; never label unavailable inference as operational.
- Keep single repository; avoid automatic merging of older ZIPs with overlapping code.

## XXIII installer scope

- Confirms the exact development branch and required XXII integration markers.
- Runs existing tests first; installs only new recovery, regression, audit and docs files.
- Runs full suite again; emits a local readiness report.
- Optional `--live` executes **one explicitly approved** local Qwen workflow in a temporary database. No live inference by default.
- Does **not** install packages, download models, run training, use paid APIs, commit, push, merge, alter website, alter Railway or rewrite the current workflow engine.
- Does not delete the backup `aurex_workflows/core.py.kusanagi_xxii.bak` or touch `website-tools/` / egg-info.

## Test matrix

| Gate | Method | Required |
|---|---|---|
| T1 repository integrity | branch, prerequisites, non-overwrite, git diff --check | PASS |
| T2 existing regression | `pytest tests/ integrations/kusanagi-xvi/tests/ -q` | PASS |
| T3 approval | pending jobs cannot execute; no model call | PASS (existing tests) |
| T4 duplicate execution | one claim only | PASS (existing tests) |
| T5 failure persistence | FAILED and event durable | PASS (existing tests) |
| T6 model evidence | SHA-256 and false authority | PASS (existing tests) |
| T7 interrupted execution | operator-only stale RUNNING demotion, idempotent, never auto-retry | PASS (new tests) |
| T8 live local workflow | approved job, actual model output, stored SHA | OPTIONAL, must be measured |
| T9 hosted CI | exact-SHA Actions runs and logs | NOT VERIFIED |
| T10 website | deployed owner auth, browser-to-Railway, CORS and UI | NOT VERIFIED |
| T11 XAELI/Brain Trust | independent challenger and arbiter evidence | NOT VERIFIED |
| T12 app integration | real device authorization, API contract and UI | NOT VERIFIED |

## Next highest-leverage engineering actions

1. Complete optional local approved workflow smoke test; do not treat a correct arithmetic answer as independent verification.
2. Resolve failed GitHub Actions workflows with exact job logs. Local green tests do not imply CI green.
3. Implement process-safe lease/heartbeat and recovery rules; XXIII recovery is an **explicit operator tool**, not automatic liveness detection.
4. Define one versioned OpenAPI contract for browser/mobile clients, authenticated user identity, and capability discovery.
5. Verify Railway deployment commit, bridge health, auth and read-only contract before enabling any write endpoint.
6. Create independently testable XAELI and Brain Trust evaluation gates; keep model output untrusted until independent checks.
7. Integrate website UI with deployed authenticated API, not the Chromebook's `127.0.0.1` model endpoint.
8. Integrate BCXMET/MEDAURUS only after mobile threat model, permission boundary and independent Android device tests.
9. Selectively port useful previous ZIP code after file-level diff, provenance and contract review; never mass-extract old bundles into live source.

## Run from Linux files (one paste)

```bash
cd ~ && mkdir -p AUREX_KUSANAGI_XXIII && python3 -m zipfile -e AUREX_KUSANAGI_XXIII_Convergence.zip AUREX_KUSANAGI_XXIII && python3 AUREX_KUSANAGI_XXIII/install.py
```

To explicitly run one local approved Qwen workflow as part of the batch, append `--live` to the final command (only if local server on port 8080 is running). The default is intentionally offline and safe.

If files already exist, the installer refuses to overwrite them. To re-audit without modifications: `python3 ~/AUREX_KUSANAGI_XXIII/install.py --audit-only`.
