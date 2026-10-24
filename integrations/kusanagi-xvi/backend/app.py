"""AUREX Railway Staging Backend Application Entrypoint."""

from __future__ import annotations

import os
import sys

# Ensure repository root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from aurex.api import app  # noqa: E402

__all__ = ["app"]
