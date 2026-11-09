# KUSANAGI LXIII — Savant-to-Bayesian Evidence Math

**Research → executable Python foundation. NOT a validated statistical model.**

> LXVIII repair provenance: re-applied to fresh canonical `main`, rather than merging the older PR #51 branch. Fixed Ruff's UTC issue, bounded identifiers and CLI input, rejected naive `now`, and stabilized extreme likelihood arithmetic. These changes are **not** evidence that caller-supplied `qualification`, `independent`, or `calibration` labels have been independently authenticated.

## Convergence of our methods

1. **Savant-style pattern recognition**: propose patterns/hypotheses, never declare truth. Here “savant” is descriptive, not a verified algorithm or special capability.
2. **Bayesian inference**: update odds using calibrated likelihood ratios. `logit(posterior)=logit(prior)+Σ log(P(E|H)/P(E|¬H))`.
3. **Dependency graph**: evidence sources that share a model, dataset, process, toolchain, or upstream signal must be assigned the same cluster. Each cluster contributes at most one bounded update; this implementation uses the least favorable log-likelihood ratio per cluster.
4. **Adversarial challenger**: independent qualification and calibration evidence required *outside* this script; string flags are merely input claims and must not be treated as cryptographic attestations.
5. **ROTAS**: Result → Authority → Truth → Admissibility → Source, with independent audit of timestamps, hashes, and source identity.
6. **CUSTOS**: unknown/stale/unqualified/uncalibrated evidence contributes zero; failure remains HOLD.
7. **Effect**: Bayesian posterior is a research diagnostic only, not an authorization or product security decision.

## Math and limitations

Prior and likelihoods are strictly between zero and one; each cluster log-likelihood contribution is bounded to ±ln(10). Time-to-live defaults to seven days for input acceptance. No inference from absent evidence. The model assumes **conditional independence between distinct clusters**; the supplied cluster names are NOT validated by code. Without actual labeled calibration data, likelihoods and resulting posterior are hypothetical. Do not publish confidence percentages as real-world probabilities until calibrated and externally evaluated. For contradictory observations within one cluster, the least favorable observation wins: intentionally conservative, not a universally optimal statistical estimator.

## Example

```json
{
  "hypothesis": "api_contract_holds",
  "prior": 0.5,
  "observations": [
    {
      "id": "independent-contract-suite",
      "cluster": "external-test-runner-1",
      "qualification": "PASS",
      "independent": true,
      "status": "OBSERVED",
      "calibration": "INDEPENDENTLY_VALIDATED",
      "observed_at": "2026-10-16T12:00:00+00:00",
      "p_given_h": 0.8,
      "p_given_not_h": 0.2
    }
  ]
}
```

**The example probabilities and calibration labels are illustrative, not evidence.**

`python -m aurex.bayesian_evidence example.json`

## Next scientific gates

- Validate source identity, calibration datasets, provenance, and evidence hashes independently; never trust booleans from a browser or agent.
- Measure calibration via Brier score, log loss, reliability curves and holdout data; compare to prior-only and simple deterministic baselines.
- Validate conditional dependence and cluster construction; compare sensitivity to prior and LR caps.
- Add hypothesis registries, bounded feature extraction, deterministic seeds and blinded adversarial review.
- Connect to the existing AUREX evidence ledger as **read-only analysis**, never to the Authority or Effect gates.
- Combine with the LXI workflow tools (uv, Hypothesis, Schemathesis, tracing) only after exact-SHA tests and independent review.
- No deployment or model download authorized by this PR.
