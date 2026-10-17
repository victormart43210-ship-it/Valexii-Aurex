from aurex.bayesian_evidence import EvidenceObservation, update_bayesian_posterior


def test_bayesian_fusion_passes_increases_posterior() -> None:
    obs1 = EvidenceObservation(
        witness_id="w-01",
        lineage_id="lineage-unit-tests",
        claim="Passes unit test matrix",
        likelihood_pass_given_true=0.9,
        likelihood_pass_given_false=0.1,
        observed_pass=True,
    )
    obs2 = EvidenceObservation(
        witness_id="w-02",
        lineage_id="lineage-security-scan",
        claim="Passes security scan",
        likelihood_pass_given_true=0.9,
        likelihood_pass_given_false=0.1,
        observed_pass=True,
    )
    res = update_bayesian_posterior(0.5, (obs1, obs2))
    assert res.posterior_probability > 0.9
    assert res.unique_lineages_count == 2
    assert res.decision == "HOLD"  # Advisory estimation does not grant automatic release authority


def test_bayesian_fusion_deduplicates_same_lineage() -> None:
    obs1 = EvidenceObservation(
        witness_id="w-01",
        lineage_id="shared-witness",
        claim="Claim A",
        observed_pass=True,
    )
    obs2 = EvidenceObservation(
        witness_id="w-02",
        lineage_id="shared-witness",
        claim="Claim A duplicate",
        observed_pass=True,
    )
    res = update_bayesian_posterior(0.5, (obs1, obs2))
    assert res.unique_lineages_count == 1


def test_bayesian_fusion_fails_decreases_posterior() -> None:
    obs = EvidenceObservation(
        witness_id="w-03",
        lineage_id="lineage-adversarial",
        claim="Adversarial attack check",
        likelihood_pass_given_true=0.9,
        likelihood_pass_given_false=0.1,
        observed_pass=False,
    )
    res = update_bayesian_posterior(0.5, (obs,))
    assert res.posterior_probability < 0.2
    assert res.decision in ("HOLD", "REJECT")
