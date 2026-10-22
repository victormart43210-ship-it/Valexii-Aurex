"""NVIDIA Document Intelligence V4 module for AUREX (Project Unified Intelligence).

Disabled by default pending explicit operator consent and server credential configuration.
AI outputs are advisory and never grant financial or verification authority.
"""
from __future__ import annotations

from aurex.doc_intelligence import (
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
