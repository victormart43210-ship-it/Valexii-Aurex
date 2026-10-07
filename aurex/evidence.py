"""Evidence normalization and freshness checks."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class EvidenceEnvelope(BaseModel):
    evidence_id: str
    source: str
    observed_at: datetime
    content_sha256: str | None = None
    claims: list[str] = Field(default_factory=list)

    def age_seconds(self, now: datetime | None = None) -> float:
        reference = now or datetime.now(UTC)
        observed = self.observed_at
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=UTC)
        return max(0.0, (reference - observed).total_seconds())

    def is_stale(self, max_age_seconds: int, now: datetime | None = None) -> bool:
        return self.age_seconds(now) > max_age_seconds
