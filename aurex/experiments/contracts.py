"""Strict contracts for AUREX experiments."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ResultStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    HOLD = "HOLD"
    NOT_RUN = "NOT RUN"
    NOT_VERIFIED = "NOT VERIFIED"


class ArmSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    arm_id: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class VerifierSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    verifier_id: str = Field(min_length=1)
    family: str = Field(min_length=1)
    reference_access: str = Field(min_length=1)


class ExperimentManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "1"
    experiment_id: str = Field(min_length=1)
    track: str = Field(min_length=1)
    dataset_revision: str = Field(min_length=1)
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    item_ids: tuple[str, ...] = Field(min_length=1)
    baseline: ArmSpec
    experimental: ArmSpec
    verifier: VerifierSpec
    dataset_authorized: bool = False
    contamination_checked: bool = False

    @field_validator("item_ids")
    @classmethod
    def validate_item_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() for item in value):
            raise ValueError("item IDs must be non-empty")
        if len(set(value)) != len(value):
            raise ValueError("duplicate item IDs are forbidden")
        return value

    @model_validator(mode="after")
    def validate_independence(self) -> "ExperimentManifest":
        if self.baseline.arm_id == self.experimental.arm_id:
            raise ValueError("baseline and experimental arm IDs must differ")
        return self
