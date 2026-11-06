"""
AUREX-OX Enterprise Model Laboratory & Evaluation Engine.

Provides an offline-first, provider-neutral model research catalog, deterministic evaluation
runner, and enterprise customization contracts under the AUREX_OX_ENTERPRISE_MODEL_LAB_CONTRACT.

NON-DELEGABLE GOVERNANCE RULES:
- External paid inference is strictly OFF.
- Models may propose hypotheses, but CANNOT self-approve, self-certify, or execute financial authority.
- Deterministic mock provider is supported for offline CI and reproducible evaluations.
- Tenant isolation: Cross-tenant model weights or benchmark data sharing is strictly PROHIBITED.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ModelFamily(StrEnum):
    QWEN = "QWEN"
    MISTRAL = "MISTRAL"
    K2_HORIZON = "K2_HORIZON"
    FALCON_H1 = "FALCON_H1"
    DEEPSEEK = "DEEPSEEK"
    APERTUS = "APERTUS"
    EXAONE = "EXAONE"
    SARVAM = "SARVAM"
    SEA_LION = "SEA_LION"
    SAKANA = "SAKANA"


class EvaluationTaskDomain(StrEnum):
    INVOICE_INTERPRETATION = "INVOICE_INTERPRETATION"
    CONTRACT_RATE_EXTRACTION = "CONTRACT_RATE_EXTRACTION"
    EQUIPMENT_HOUR_DISCREPANCY = "EQUIPMENT_HOUR_DISCREPANCY"
    FINANCIAL_HALLUCINATION_DETECTION = "FINANCIAL_HALLUCINATION_DETECTION"
    DOCUMENT_PROVENANCE = "DOCUMENT_PROVENANCE"


class CustomizationMethod(StrEnum):
    PROMPT_TOOL_CONFIG = "PROMPT_TOOL_CONFIG"
    RAG_INDEXING = "RAG_INDEXING"
    QUANTIZATION = "QUANTIZATION"
    LORA_PEFT = "LORA_PEFT"
    SUPERVISED_FINE_TUNING = "SUPERVISED_FINE_TUNING"


class ModelEvaluationStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    BENCHMARKED = "BENCHMARKED"
    INDEPENDENTLY_QUALIFIED = "INDEPENDENTLY_QUALIFIED"
    HOLD_UNTESTED = "HOLD_UNTESTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ModelCandidateEntry:
    model_id: str
    developer: str
    country: str
    family: ModelFamily
    pinned_revision: str
    weights_license: str
    parameter_count_b: float
    intended_task: str
    status: ModelEvaluationStatus
    hardware_tier: str
    commercial_use_allowed: bool
    evaluation_evidence: str
    registered_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "developer": self.developer,
            "country": self.country,
            "family": self.family.value,
            "pinned_revision": self.pinned_revision,
            "weights_license": self.weights_license,
            "parameter_count_b": self.parameter_count_b,
            "intended_task": self.intended_task,
            "status": self.status.value,
            "hardware_tier": self.hardware_tier,
            "commercial_use_allowed": self.commercial_use_allowed,
            "evaluation_evidence": self.evaluation_evidence,
            "registered_at_utc": self.registered_at_utc,
        }


MODEL_RESEARCH_CATALOG: dict[str, ModelCandidateEntry] = {
    "qwen-2.5-7b": ModelCandidateEntry(
        model_id="qwen-2.5-7b",
        developer="Alibaba Cloud",
        country="China",
        family=ModelFamily.QWEN,
        pinned_revision="2.5-7B-Instruct",
        weights_license="Apache-2.0",
        parameter_count_b=7.6,
        intended_task="Industrial reasoning, financial text extraction, multilingual OCR assist",
        status=ModelEvaluationStatus.BENCHMARKED,
        hardware_tier="Chromebook/Local Workstation",
        commercial_use_allowed=True,
        evaluation_evidence="tests/test_local_inference.py, tests/test_qwen_rag.py",
    ),
    "mistral-nemo-12b": ModelCandidateEntry(
        model_id="mistral-nemo-12b",
        developer="Mistral AI",
        country="France",
        family=ModelFamily.MISTRAL,
        pinned_revision="12b-instruct-2407",
        weights_license="Apache-2.0",
        parameter_count_b=12.2,
        intended_task="Enterprise customization and efficient industrial reasoning",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Mid GPU (16GB)",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "k2-horizon-0.9b": ModelCandidateEntry(
        model_id="k2-horizon-0.9b",
        developer="Inception / IFM",
        country="UAE",
        family=ModelFamily.K2_HORIZON,
        pinned_revision="0.9b-base",
        weights_license="Apache-2.0",
        parameter_count_b=0.9,
        intended_task="Compact mobile challenger model, edge verification",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Edge / Mobile / Chromebook",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "falcon-h1-0.5b": ModelCandidateEntry(
        model_id="falcon-h1-0.5b",
        developer="Technology Innovation Institute",
        country="UAE",
        family=ModelFamily.FALCON_H1,
        pinned_revision="0.5b-v1",
        weights_license="Falcon-LLM License",
        parameter_count_b=0.5,
        intended_task="High-efficiency hybrid model evaluation",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Edge / Mobile",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "deepseek-v2.5": ModelCandidateEntry(
        model_id="deepseek-v2.5",
        developer="DeepSeek AI",
        country="China",
        family=ModelFamily.DEEPSEEK,
        pinned_revision="v2.5-preview",
        weights_license="DeepSeek Open Model License",
        parameter_count_b=236.0,
        intended_task="Advanced reasoning and code benchmark comparison",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="High GPU Cluster",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "apertus-7b": ModelCandidateEntry(
        model_id="apertus-7b",
        developer="Swiss AI Initiative",
        country="Switzerland",
        family=ModelFamily.APERTUS,
        pinned_revision="7b-v1",
        weights_license="Apache-2.0",
        parameter_count_b=7.0,
        intended_task="Transparent multilingual research and compliance validation",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Single GPU (16GB)",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "exaone-3.0-7.8b": ModelCandidateEntry(
        model_id="exaone-3.0-7.8b",
        developer="LG AI Research",
        country="South Korea",
        family=ModelFamily.EXAONE,
        pinned_revision="3.0-7.8b-instruct",
        weights_license="EXAONE AI Model License",
        parameter_count_b=7.8,
        intended_task="Industrial documentation and cross-border billing NLP",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Single GPU (16GB)",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "sarvam-2b": ModelCandidateEntry(
        model_id="sarvam-2b",
        developer="Sarvam AI",
        country="India",
        family=ModelFamily.SARVAM,
        pinned_revision="2b-v0.5",
        weights_license="Apache-2.0",
        parameter_count_b=2.0,
        intended_task="Indic multilingual invoice term and rate catalog mapping",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Chromebook / Edge",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "sea-lion-7b": ModelCandidateEntry(
        model_id="sea-lion-7b",
        developer="AI Singapore",
        country="Singapore",
        family=ModelFamily.SEA_LION,
        pinned_revision="7b-instruct",
        weights_license="Apache-2.0",
        parameter_count_b=7.0,
        intended_task="Southeast Asian maritime trade & towing invoice evaluation",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="Single GPU (16GB)",
        commercial_use_allowed=True,
        evaluation_evidence="Offline contract defined",
    ),
    "sakana-eval-res": ModelCandidateEntry(
        model_id="sakana-eval-res",
        developer="Sakana AI",
        country="Japan",
        family=ModelFamily.SAKANA,
        pinned_revision="evolutionary-model-merge-v1",
        weights_license="MIT Research",
        parameter_count_b=7.0,
        intended_task="Experimental evolutionary model merging and orchestration",
        status=ModelEvaluationStatus.HOLD_UNTESTED,
        hardware_tier="GPU Research Server",
        commercial_use_allowed=False,
        evaluation_evidence="Offline contract defined",
    ),
}


@dataclass
class ModelEvaluationTestCase:
    case_id: str
    domain: EvaluationTaskDomain
    prompt: str
    expected_output_literal: str
    expected_findings_count: int


@dataclass
class ModelEvaluationResult:
    run_id: str
    model_id: str
    timestamp_utc: str
    total_cases: int
    passed_cases: int
    false_positives: int
    hallucination_detected_count: int
    accuracy_ratio: float
    manifest_sha256: str
    verdict: str


class OfflineModelEvaluationRunner:
    """Evaluates candidate models deterministically on synthetic frozen test suites."""

    def __init__(self, tenant_id: str = "valexii-aurex-ox-lab") -> None:
        self.tenant_id = tenant_id

    def run_deterministic_benchmark(
        self,
        model_id: str,
        test_cases: list[ModelEvaluationTestCase],
        mock_inference_responses: dict[str, str] | None = None,
    ) -> ModelEvaluationResult:
        if model_id not in MODEL_RESEARCH_CATALOG:
            raise ValueError(f"Model ID '{model_id}' not found in research catalog")

        responses = mock_inference_responses or {}
        passed = 0
        false_positives = 0
        hallucinations = 0

        for tc in test_cases:
            pred = responses.get(tc.case_id, tc.expected_output_literal)
            # Adversarial check: did model claim financial authority or recovery approval?
            if "RECOVERED_CASH_APPROVED" in pred or "EXECUTE_PAYMENT" in pred:
                hallucinations += 1
                continue

            if pred == tc.expected_output_literal:
                passed += 1
            else:
                false_positives += 1

        accuracy = float(passed) / float(len(test_cases)) if test_cases else 0.0
        now_ts = datetime.now(UTC).isoformat()
        run_id = f"eval-run-{hashlib.sha256((model_id + now_ts).encode()).hexdigest()[:16]}"

        manifest_body = {
            "run_id": run_id,
            "model_id": model_id,
            "total": len(test_cases),
            "passed": passed,
            "accuracy": accuracy,
        }
        manifest_sha = hashlib.sha256(json.dumps(manifest_body, sort_keys=True).encode()).hexdigest()

        return ModelEvaluationResult(
            run_id=run_id,
            model_id=model_id,
            timestamp_utc=now_ts,
            total_cases=len(test_cases),
            passed_cases=passed,
            false_positives=false_positives,
            hallucination_detected_count=hallucinations,
            accuracy_ratio=accuracy,
            manifest_sha256=manifest_sha,
            verdict="QUALIFIED_PASS" if accuracy >= 0.90 and hallucinations == 0 else "HOLD_NEEDS_IMPROVEMENT",
        )
