"""Sovereign Studio Engine: Engineering, Intelligence, and Growth Division Integration (PR #36 inspired)."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MarketingClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    evidence_id: str | None = None
    verification_status: Literal["VERIFIED", "NOT VERIFIED", "REJECTED"] = "NOT VERIFIED"


class CampaignDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    brand: Literal["AUREX", "BCXMET", "VALEXII"]
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    claims: tuple[MarketingClaim, ...] = ()
    approval_status: Literal["DRAFT", "APPROVED_FOR_PUBLICATION", "REJECTED"] = "DRAFT"
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class StudioLaunchReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    studio_id: str = Field(min_length=1)
    release_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    engineering_status: Literal["PASS", "FAIL", "HOLD"]
    intelligence_status: Literal["PASS", "FAIL", "HOLD"]
    growth_status: Literal["PASS", "FAIL", "HOLD"]
    final_readiness: Literal["ADMIT", "HOLD"]


def create_campaign_draft(
    campaign_id: str,
    brand: Literal["AUREX", "BCXMET", "VALEXII"],
    title: str,
    content: str,
    claims: list[MarketingClaim] | None = None,
) -> CampaignDraft:
    return CampaignDraft(
        campaign_id=campaign_id,
        brand=brand,
        title=title,
        content=content,
        claims=tuple(claims or []),
        approval_status="DRAFT",
    )


def evaluate_launch_readiness(
    studio_id: str,
    release_sha: str,
    engineering_pass: bool,
    intelligence_pass: bool,
    growth_pass: bool,
) -> StudioLaunchReport:
    eng_status = "PASS" if engineering_pass else "HOLD"
    intel_status = "PASS" if intelligence_pass else "HOLD"
    gr_status = "PASS" if growth_pass else "HOLD"

    admit = engineering_pass and intelligence_pass and growth_pass
    return StudioLaunchReport(
        studio_id=studio_id,
        release_sha=release_sha,
        engineering_status=eng_status,  # type: ignore
        intelligence_status=intel_status,  # type: ignore
        growth_status=gr_status,  # type: ignore
        final_readiness="ADMIT" if admit else "HOLD",
    )
