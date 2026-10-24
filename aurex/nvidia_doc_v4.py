"""NVIDIA Document Intelligence V4 module for AUREX (Project Unified Intelligence).

Disabled by default pending explicit operator consent and server credential configuration.
AI outputs are advisory and never grant financial or verification authority.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Bridge to integrations/kusanagi-xvi/backend/doc_intelligence.py
root = Path(__file__).resolve().parents[1]
bridge_path = root / "integrations" / "kusanagi-xvi" / "backend"
if str(bridge_path) not in sys.path:
    sys.path.insert(0, str(bridge_path))

from doc_intelligence import (  # type: ignore[import-not-found] # noqa: E402
    Analysis,
    AnalyzeInput,
    budget_snapshot,
    register_document_routes,
)

__all__ = [
    "Analysis",
    "AnalyzeInput",
    "budget_snapshot",
    "register_document_routes",
]
