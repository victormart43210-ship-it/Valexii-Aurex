"""Bayesian Evidence Fusion Engine for AUREX (PR #51 & KUSANAGI LXIX reconciled)."""

import math
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    witness_id: str = Field(min_length=1)
    lineage_id: str = "default_lineage"
    claim: str = Field(min_length=1)
    likelihood_pass_given_true: float = Field(default=0.9, ge=0.5, le=0.99)
    likelihood_pass_given_false: float = Field(default=0.1, ge=0.01, le=0.5)
    observed_pass: bool
    observed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class BayesianFusionState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    prior_probability: float = Field(default=0.5, ge=0.001, le=0.999)
    posterior_probability: float = Field(default=0.5, ge=0.001, le=0.999)
    unique_lineages_count: int = Field(default=0, ge=0)
    decision: Literal["ADMIT", "HOLD", "REJECT"] = "HOLD"


def update_bayesian_posterior(
    prior: float,
    observations: tuple[EvidenceObservation, ...],
) -> BayesianFusionState:
    if not observations:
        return BayesianFusionState(
            prior_probability=prior,
            posterior_probability=prior,
            unique_lineages_count=0,
            decision="HOLD",
        )

    # Deduplicate observations by lineage_id to prevent correlated likelihood amplification
    seen_lineages: set[str] = set()
    unique_obs: list[EvidenceObservation] = []
    for obs in observations:
        if obs.lineage_id not in seen_lineages:
            seen_lineages.add(obs.lineage_id)
            unique_obs.append(obs)

    log_odds = math.log(prior / (1.0 - prior))
    for obs in unique_obs:
        if obs.observed_pass:
            lr = obs.likelihood_pass_given_true / obs.likelihood_pass_given_false
        else:
            lr = (1.0 - obs.likelihood_pass_given_true) / (1.0 - obs.likelihood_pass_given_false)
        log_odds += math.log(lr)

    posterior = 1.0 / (1.0 + math.exp(-log_odds))
    posterior = max(0.001, min(0.999, posterior))

    # Probability estimation is advisory only; release authority remains gated (HOLD)
    decision: Literal["ADMIT", "HOLD", "REJECT"] = "HOLD"
    if posterior <= 0.05:
        decision = "REJECT"

    return BayesianFusionState(
        prior_probability=prior,
        posterior_probability=posterior,
        unique_lineages_count=len(unique_obs),
        decision=decision,
    )
