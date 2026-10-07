"""Machine-readable experiment reports with measured/inferred/unverified state attribution."""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.evals.statistical import PairedStatisticalReport
from aurex.experiments.admission import AdmissionDecision
from aurex.experiments.contracts import ExperimentManifest, ResultStatus
from aurex.experiments.runner import RunReport
from aurex.provenance import fingerprint


class MetricAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    value: Any
    attribution_type: Literal["measured", "inferred", "unverified"]
    notes: str = ""


class ExperimentReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    manifest: ExperimentManifest
    manifest_sha256: str
    run_report: RunReport | None
    admission_decision: AdmissionDecision
    statistical_report: PairedStatisticalReport | None
    attributions: tuple[MetricAttribution, ...]
    overall_status: ResultStatus
    report_digest: str


def build_experiment_report(
    manifest: ExperimentManifest,
    manifest_sha256: str,
    run_report: RunReport | None,
    admission_decision: AdmissionDecision,
    statistical_report: PairedStatisticalReport | None = None,
) -> ExperimentReport:
    attributions: list[MetricAttribution] = []

    if run_report and run_report.complete:
        attributions.append(
            MetricAttribution(
                name="item_outputs",
                value=len(run_report.items),
                attribution_type="measured",
                notes="Direct execution output",
            )
        )
    elif run_report:
        attributions.append(
            MetricAttribution(
                name="item_outputs",
                value=len(run_report.items),
                attribution_type="unverified",
                notes="Incomplete run execution",
            )
        )

    if statistical_report:
        attributions.append(
            MetricAttribution(
                name="baseline_score",
                value=statistical_report.baseline_score,
                attribution_type="measured",
            )
        )
        attributions.append(
            MetricAttribution(
                name="experimental_score",
                value=statistical_report.experimental_score,
                attribution_type="measured",
            )
        )
        if statistical_report.relative_uplift is not None:
            attributions.append(
                MetricAttribution(
                    name="relative_uplift",
                    value=statistical_report.relative_uplift,
                    attribution_type="inferred",
                    notes="Calculated relative uplift ratio",
                )
            )

    body = {
        "manifest_sha256": manifest_sha256,
        "experiment_id": manifest.experiment_id,
        "run_sha256": run_report.run_sha256 if run_report else None,
        "admission_status": admission_decision.status.value,
    }
    report_digest = fingerprint(body)

    return ExperimentReport(
        manifest=manifest,
        manifest_sha256=manifest_sha256,
        run_report=run_report,
        admission_decision=admission_decision,
        statistical_report=statistical_report,
        attributions=tuple(attributions),
        overall_status=admission_decision.status,
        report_digest=report_digest,
    )
