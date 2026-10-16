"""Bayesian Evidence Fusion Engine for AUREX (PR #51 reconciled)."""

import math
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    witness_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    likelihood_pass_given_true: float = Field(default=0.9, ge=0.5, le=0.99)
    likelihood_pass_given_false: float = Field(default=0.1, ge=0.01, le=0.5)
    observed_pass: bool
    observed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class BayesianFusionState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    prior_probability: float = Field(default=0.5, ge=0.001, le=0.999)
    posterior_probability: float = Field(default=0.5, ge=0.001, le=0.999)
    observations_count: int = Field(default=0, ge=0)
    decision: Literal["ADMIT", "HOLD", "REJECT"] = "HOLD"


def update_bayesian_posterior(
    prior: float,
    observations: tuple[EvidenceObservation, ...],
) -> BayesianFusionState:
    if not observations:
        return BayesianFusionState(
            prior_probability=prior,
            posterior_probability=prior,
            observations_count=0,
            decision="HOLD",
        )

    log_odds = math.log(prior / (1.0 - prior))
    for obs in observations:
        if obs.observed_pass:
            lr = obs.likelihood_pass_given_true / obs.likelihood_pass_given_false
        else:
            lr = (1.0 - obs.likelihood_pass_given_true) / (1.0 - obs.likelihood_pass_given_false)
        log_odds += math.log(lr)

    posterior = 1.0 / (1.0 + math.exp(-log_odds))
    posterior = max(0.001, min(0.999, posterior))

    decision: Literal["ADMIT", "HOLD", "REJECT"] = "HOLD"
    if posterior >= 0.95:
        decision = "ADMIT"
    elif posterior <= 0.05:
        decision = "REJECT"

    return BayesianFusionState(
        prior_probability=prior,
        posterior_probability=posterior,
        observations_count=len(observations),
        decision=decision,
    )
