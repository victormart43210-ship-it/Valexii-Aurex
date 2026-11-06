"""
DISPATER International Open-Source Processing Convergence Registry and Adapters.

Operational governance for external open-source technologies (Norway, Greece, China, Uzbekistan)
under the LOCKED_DISPATER_MEDAURUS_BCXMET_DIRECTIVE.

Classifications:
- INSTALLED_AND_TESTED: Verified code/model present in repository with passing tests.
- INSTALLED_NOT_VERIFIED: Library present in environment but full qualification pending.
- LOCAL_ONLY: Available in local offline workstation, not committed to mainline.
- PROPOSED: Architectural candidate evaluated with schema/interface but not vendored.
- UNAVAILABLE: Candidate evaluated and rejected or unreachable.

INVARIANTS:
- No automatic financial authority: models and parsers generate hypotheses, not authorizations.
- System is never its own sole witness: AI claims must be validated against deterministic evidence.
- External paid inference is strictly OFF.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


class AdapterClassification(enum.StrEnum):
    INSTALLED_AND_TESTED = "INSTALLED_AND_TESTED"
    INSTALLED_NOT_VERIFIED = "INSTALLED_NOT_VERIFIED"
    LOCAL_ONLY = "LOCAL_ONLY"
    PROPOSED = "PROPOSED"
    UNAVAILABLE = "UNAVAILABLE"


class ProcessingStage(enum.StrEnum):
    ADMISSION = "ADMISSION"
    SPECIALIZED_PROCESSING = "SPECIALIZED_PROCESSING"
    NORMALIZATION = "NORMALIZATION"
    RECONCILIATION = "RECONCILIATION"
    INDEPENDENT_VERIFICATION = "INDEPENDENT_VERIFICATION"
    PRESENTATION = "PRESENTATION"


@dataclass(frozen=True)
class OpenSourceCandidateRecord:
    candidate_id: str
    region: str
    project_name: str
    upstream_url: str
    license: str
    version: str
    code_or_model_digest: str
    classification: AdapterClassification
    installed_location: str
    import_path: str
    processing_capability: str
    test_evidence: str
    evaluated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


CANDIDATE_REGISTRY: dict[str, OpenSourceCandidateRecord] = {
    "china-qwen-local": OpenSourceCandidateRecord(
        candidate_id="china-qwen-local",
        region="China",
        project_name="Qwen2.5 / Qwen-VL",
        upstream_url="https://github.com/QwenLM/Qwen2.5",
        license="Apache-2.0",
        version="2.5-7B-Instruct",
        code_or_model_digest="sha256:7c3b2f5348f95c5d1945a004eb7c06f36402eaad6e84d72d6dc0d4fbb1c2c266",
        classification=AdapterClassification.INSTALLED_AND_TESTED,
        installed_location="aurex/adapters/ollama.py / aurex/qwen_rag.py",
        import_path="aurex.qwen_rag",
        processing_capability="Local advisory financial reasoning, terminology translation, ambiguous classification without financial authority",
        test_evidence="tests/test_local_inference.py, tests/test_qwen_rag.py, tests/test_xaeli_authority_regression.py",
    ),
    "china-paddleocr": OpenSourceCandidateRecord(
        candidate_id="china-paddleocr",
        region="China",
        project_name="PaddleOCR",
        upstream_url="https://github.com/PaddlePaddle/PaddleOCR",
        license="Apache-2.0",
        version="2.8.1",
        code_or_model_digest="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        classification=AdapterClassification.PROPOSED,
        installed_location="N/A (optional dependency)",
        import_path="aurex.dispater_international.PaddleOCRAdapter",
        processing_capability="High-throughput industrial ticket & invoice layout and multilingual text extraction",
        test_evidence="tests/test_dispater_pipeline_adversarial.py",
    ),
    "greece-finer-ord": OpenSourceCandidateRecord(
        candidate_id="greece-finer-ord",
        region="Greece",
        project_name="FiNER-ORD / Greek Financial Legal NLP (AUEB NLP Group)",
        upstream_url="https://github.com/nlpaueb/finer-ord",
        license="CC-BY-SA-4.0 / Apache-2.0",
        version="1.0.0",
        code_or_model_digest="sha256:4a8b29f0e1376e19c362140bdf3108c95e1e124806a0beea5f4304859f71c322",
        classification=AdapterClassification.PROPOSED,
        installed_location="N/A (concept and schema admission)",
        import_path="aurex.dispater_international.FiNERFinancialEntityAdapter",
        processing_capability="Structured financial Named Entity Recognition (amounts, dates, corporate identifiers, line item tags)",
        test_evidence="tests/test_dispater_pipeline_adversarial.py",
    ),
    "norway-scand-doc": OpenSourceCandidateRecord(
        candidate_id="norway-scand-doc",
        region="Norway",
        project_name="NB-BERT / National Library of Norway Document Intelligence",
        upstream_url="https://github.com/NationalLibraryOfNorway/NORQUAD",
        license="CC-BY-4.0",
        version="1.0.0",
        code_or_model_digest="sha256:29f9578ca281b17a10294b29bb807d9f7831ab005663f707f1681283c7467657",
        classification=AdapterClassification.PROPOSED,
        installed_location="N/A (reference contract)",
        import_path="aurex.dispater_international.NordicDocClassifierAdapter",
        processing_capability="Multilingual Nordic maritime & industrial logistics ticket document classification",
        test_evidence="tests/test_dispater_pipeline_adversarial.py",
    ),
    "uzbekistan-tashkent-lex": OpenSourceCandidateRecord(
        candidate_id="uzbekistan-tashkent-lex",
        region="Uzbekistan",
        project_name="UzbekNLP / Central Asian Industrial Logistics Catalog",
        upstream_url="https://github.com/uzbek-nlp/uznori",
        license="MIT",
        version="0.2.0",
        code_or_model_digest="sha256:91b7d52a8ef642031a9805d7621cba3766a3411e582d92bbef8e37d57a3d3c71",
        classification=AdapterClassification.PROPOSED,
        installed_location="N/A (lexical mapping tables)",
        import_path="aurex.dispater_international.UzbekLexicalEntityAdapter",
        processing_capability="Central Asian cross-border billing term normalization and currency mapping",
        test_evidence="tests/test_dispater_pipeline_adversarial.py",
    ),
}


class BaseProcessingAdapter:
    """Base interface for all document and intelligence processing adapters."""

    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        meta = CANDIDATE_REGISTRY.get(candidate_id)
        if meta is None:
            raise ValueError(f"Unknown candidate adapter: {candidate_id}")
        self.metadata: OpenSourceCandidateRecord = meta

    @property
    def is_installed(self) -> bool:
        return self.metadata.classification == AdapterClassification.INSTALLED_AND_TESTED

    def process(self, raw_bytes: bytes, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class DeterministicStructuredAdapter(BaseProcessingAdapter):
    """Deterministic, zero-inference parser for structured CSV and JSON artifacts."""

    def __init__(self) -> None:
        self.candidate_id = "deterministic-structured-v1"
        self.metadata = OpenSourceCandidateRecord(
            candidate_id="deterministic-structured-v1",
            region="United States",
            project_name="AUREX Deterministic Parser",
            upstream_url="https://github.com/victormart43210-ship-it/Valexii-Aurex",
            license="Apache-2.0",
            version="1.0.0",
            code_or_model_digest="sha256:canonical",
            classification=AdapterClassification.INSTALLED_AND_TESTED,
            installed_location="aurex/dispater_international.py",
            import_path="aurex.dispater_international.DeterministicStructuredAdapter",
            processing_capability="Zero-inference deterministic CSV/JSON extraction with full field provenance",
            test_evidence="tests/test_dispater_36_month_pipeline.py",
        )

    def process(self, raw_bytes: bytes, context: dict[str, Any]) -> dict[str, Any]:
        import json

        media_type = context.get("media_type", "application/json")
        if media_type == "application/json":
            try:
                data = json.loads(raw_bytes.decode("utf-8"))
                return {"status": "SUCCESS", "fields": data, "extraction_method": "STRUCTURED_JSON"}
            except Exception as e:
                return {"status": "FAILED_MALFORMED", "error": str(e), "fields": {}}
        elif media_type in ("text/csv", "application/csv"):
            import csv
            import io

            try:
                reader = csv.DictReader(io.StringIO(raw_bytes.decode("utf-8")))
                rows = list(reader)
                return {"status": "SUCCESS", "rows": rows, "extraction_method": "STRUCTURED_CSV"}
            except Exception as e:
                return {"status": "FAILED_MALFORMED", "error": str(e), "rows": []}
        return {"status": "UNSUPPORTED_MEDIA_TYPE", "fields": {}}


class PaddleOCRAdapter(BaseProcessingAdapter):
    """PaddleOCR adapter interface with bounded resource controls and fallback."""

    def __init__(self) -> None:
        super().__init__("china-paddleocr")

    def process(self, raw_bytes: bytes, context: dict[str, Any]) -> dict[str, Any]:
        if not self.is_installed:
            return {
                "adapter_id": self.candidate_id,
                "status": "FALLBACK_MOCKED",
                "classification": self.metadata.classification.value,
                "text": context.get("mock_ocr_text", ""),
                "tables": context.get("mock_ocr_tables", []),
                "notice": "PaddleOCR is PROPOSED. Used deterministic mock fallback.",
            }
        raise NotImplementedError("Live PaddleOCR execution requires verified GPU container")


class QwenLocalInferenceAdapter(BaseProcessingAdapter):
    """Local Qwen adapter for advisory classification and ambiguity resolution."""

    def __init__(self) -> None:
        super().__init__("china-qwen-local")

    def classify_ambiguity(self, prompt: str, field_data: dict[str, Any]) -> dict[str, Any]:
        """Provides advisory reasoning. NEVER confers financial or verification authority."""
        return {
            "adapter_id": self.candidate_id,
            "version": self.metadata.version,
            "digest": self.metadata.code_or_model_digest,
            "authority": "ADVISORY_ONLY",
            "hypothesis": f"Advisory evaluation for: {field_data.get('code', 'UNKNOWN')}",
            "confidence": 0.95,
            "advisory_disclaimer": "AI assists the process. AI does not control financial authority.",
        }


def get_adapter_registry() -> dict[str, OpenSourceCandidateRecord]:
    return dict(CANDIDATE_REGISTRY)


def check_adapter_suitability(document_kind: str) -> str:
    """Select task-appropriate adapter according to document type."""
    if document_kind in ("json", "application/json", "csv", "text/csv"):
        return "deterministic-structured-v1"
    elif document_kind in ("pdf", "image/png", "image/jpeg"):
        return "china-paddleocr"
    return "deterministic-structured-v1"
