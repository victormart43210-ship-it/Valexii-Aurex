"""Optional document-parser inventory.

Docling is not imported. Its package license is MIT, and its model licenses
have not been reviewed, so it cannot fill an uncertain field. Scans stay
uninterpreted. Spreadsheet values keep the cell they came from.
"""

from __future__ import annotations

import importlib.util
from typing import Any

DOCLING_PACKAGE_LICENSE = "MIT"
DOCLING_MODEL_LICENSES = "NOT_REVIEWED"


def parser_inventory() -> dict[str, Any]:
    docling = importlib.util.find_spec("docling") is not None
    return {
        "schema": "valexii.document_intelligence.v1",
        "digital_pdf": {"processor": "pypdf", "installed": True, "guesses_missing_text": False},
        "spreadsheet": {
            "processor": "openpyxl",
            "installed": True,
            "provenance": "sheet_and_cell",
            "guesses_missing_text": False,
        },
        "ocr": "NOT_INSTALLED",
        "docling": {
            "installed": docling,
            "adopted": False,
            "package_license": DOCLING_PACKAGE_LICENSE,
            "model_licenses": DOCLING_MODEL_LICENSES,
            "reason": "Model licenses are not reviewed, so the adapter is not loaded.",
        },
        "effect": "NONE",
    }


def require_not_inferred(provenance: list[dict[str, Any]]) -> None:
    """Accepted field values must be copied from the source, not completed by a model."""
    for item in provenance:
        if item.get("inferred") is True or not item.get("value"):
            raise ValueError("an uncertain extracted value was presented as a completed field")
        if item.get("qualification") != "EXTRACTED":
            raise ValueError("only extracted values may enter a field")
