# AUREX / CUSTOS PRIME Ω — Acceptance Matrix

This matrix defines **required checks**, not claims that the checks have run. Report each test as PASS, FAIL, NOT RUN, or NOT VERIFIED with the exact code SHA and evidence link.

Canonical flow: **Evidence → Qualification → Reality → Authority → Effect**. AUREX is an **external witness**, not BCXMET/VALEXII runtime authority.

| ID | Boundary | Adversarial input / scenario | Required observation | Current status |
| --- | --- | --- | --- | --- |
| C01 | Source | No independent challenger configured | HOLD; no authority | NOT VERIFIED |
| C02 | Authority | Challenger sets authority_granted=true | Rejected; no downstream effect | NOT VERIFIED |
| C03 | Evidence | Missing source or malformed claim evidence | INSUFFICIENT/HOLD; never implicit PASS | NOT VERIFIED |
| C04 | Freshness | Expired/replayed evidence | STALE or withheld authority | NOT VERIFIED |
| C05 | Provenance | Tamper with content hash or receipt | CONTESTED/FAIL, with original preserved | NOT VERIFIED |
| C06 | Reproducibility | Repeat benchmark against frozen SHA, seed, dataset | Raw results and variance recorded | NOT RUN |
| C07 | Independence | Generator and verifier share hidden test answers | Detect circular witness; withhold conclusion | NOT RUN |
| C08 | Confidentiality | Secret/credential injected into public fixture | Block before commit, issue, artifact, or log | NOT RUN |
| C09 | CI trust | Untrusted fork PR attempts to access secrets | No privileged checkout, credential, write token | NOT RUN |
| C10 | Resource limits | Excessive sample size, recursion, large archive | Bounded time, memory, filesystem, and costs | NOT RUN |
| C11 | Portable source | Duplicate/case-colliding names, traversal, symlink | Reject before extraction; no overwrite | NOT RUN |
| C12 | Cross-platform | Chromebook to PC/external-drive interruption | Verified restore or explicit recoverable FAIL | NOT RUN |
| C13 | Model execution | Local inference backend absent/unreachable | NOT RUN/NOT VERIFIED; no fabricated result | NOT RUN |
| C14 | Mobile scans | MobSF unavailable or partial APK scan | NOT RUN/PARTIAL, never security PASS | NOT RUN |
| C15 | Claims | Claimed score with no raw benchmark artifact | WITHHELD, not published as measured | NOT RUN |

## Evidence record

Each run should record source artifact SHA-256, tool and runtime version, test ID, timestamp, environment, input provenance, expected condition, observed output, independent witness, failure reason, and any authorization boundary. Distinguish a local SHA-256 consistency check from an independent third-party witness.

## Promotion gate

A UI task marked DONE or a scan marked completed is not security proof. The verifier must not create security authority from its own output. Evidence is append-only where possible, revocation does not rewrite history, and stale evidence cannot authorize current action.

Before claiming release readiness: run local unit/adversarial tests, verify on target Windows/ChromeOS hardware, review dependencies and licenses, scan the full intended public Git history for secrets, and obtain independent CUSTOS review. Every unrun check remains NOT RUN. Do not merge or publish automatically.
