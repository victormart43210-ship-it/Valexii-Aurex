# KUSANAGI XLI — Resource-conscious verification execution

Status: IMPLEMENTED IN ISOLATED DRAFT BRANCH; NOT RUN; NOT INTEGRATED; RELEASE HOLD.

## Architecture invariant

**Linux owns process lifetime and CPU scheduling. AUREX owns durable job state, evidence, qualification, reality, authority and effects.** A background test is not a worker claim, durable execution, trusted signature, or hosted CI result.

## Existing-system implementation

`scripts/run-verification-background.sh` wraps existing Python/Ruff/Mypy/pytest checks. It uses `nohup`, `nice -n 10`, sequential execution, redirected stdin/stdout/stderr, a SHA snapshot, a per-run PID, UTC timestamps, explicit per-check exit codes, and logs outside the repository by default. It does not introduce a service, daemon, dependency, or new AUREX authority path.

Use from a clean checkout with dev dependencies installed:

```bash
bash scripts/run-verification-background.sh
```

The command prints a private log directory. Read `verification.log`, `exit-codes.txt`, and `exit.status` there. Missing `exit.status` is UNKNOWN, **never PASS** (e.g. process killed, container stopped, or host shutdown). A zero exit code is only a LOCAL PASS, never a hosted-CI PASS. Check the commit SHA in `candidate.sha`.

The wrapper does not claim the Chromebook Linux container survives shutdown. If `nice` is unsupported or verification dependencies are absent, record FAIL/UNKNOWN, not PASS. The tool versions and test counts must be read from the captured output.

## Follow-on independent admission gates

1. Reconcile Jules's real integration candidate and freeze its exact SHA.
2. Run baseline on separate clean `main` and candidate worktrees.
3. Run CUSTOS auth, trust-key, lease-fencing, immutable-evidence and synthetic-success tests.
4. Run real local API -> worker -> SQLite -> evidence -> verifier and frontend separately; do not substitute mocks.
5. Require GitHub Actions success on the **same final candidate SHA**, independent review of changes, and explicit owner authorization before merge/deploy.

## Limits

No verification command was executed by the GitHub file-edit connector. No claim is made that the script passes `bash -n`, works on the user's machine, or verifies the live website. Independent execution is mandatory.
