# AUREX Sovereign Studio — KUSANAGI XLVI

Three connected divisions, one governance boundary:

- **Engineering:** build, bounded evaluation, regression tests, and draft PRs.
- **Intelligence:** independent adversarial review, evidence provenance, and launch gate assessment.
- **Growth:** evidence-linked campaign briefs, owner-reviewed publication, and later analytics.

Canonical flow: Evidence → Qualification → Reality → Authority → Effect.

## First executable increment

The local, read-only scorecard is runnable with Python 3.12+:

```sh
python -m aurex.sovereign_studio --gates gates.json
```

Example `gates.json`:

```json
{
  "engineering_tests": {"status": "PASS", "evidence_ref": "ci:actual-run-id"},
  "security_review": {"status": "NOT RUN"},
  "independent_verification": {"status": "NOT RUN"},
  "frontend_backend_e2e": {"status": "NOT RUN"},
  "privacy_review": {"status": "NOT RUN"},
  "owner_release_approval": {"status": "NOT RUN"}
}
```

Unsubstantiated PASS is demoted to NOT VERIFIED. The system never grants merge, deployment, or publication authority. Even REVIEW_ELIGIBLE is a review state, not a release command.

## Integration boundaries

AUREX backend remains the execution and evidence authority. VALEXII.COM is a presentation/client surface. Never expose backend service credentials to the browser. Do not add public job execution until worker admission, authenticated request routing, budget enforcement, authorization, and independent E2E checks are verified.

The Growth division must not automatically publish or represent drafts as verified claims. Campaign measurement must use consent-aware analytics. Avoid invented traffic, retention, conversion, and performance metrics.

## Next milestones (not completed here)

1. Verify existing KUSANAGI XLV code against current SQLite API and full CI.
2. Wire approved local worker to authenticated backend, preserving HTTP 503 when unavailable.
3. Add evidence-backed studio API views with owner-scoped access.
4. Connect VALEXII.COM frontend and prove live end-to-end operation.
5. Add draft-only marketing workflows and real analytics integrations.
