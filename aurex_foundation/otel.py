"""AUREX OpenTelemetry admission boundary.

Instrumentation is disabled until independently reviewed.
No automatic exporter configuration is permitted here.
"""

import os
from typing import Any


def instrument_fastapi(app: Any) -> str:
    """Return admission status without modifying the application."""

    if os.environ.get("AUREX_OTEL_ENABLED") != "true":
        return "DISABLED"

    if os.environ.get("AUREX_OTEL_OPERATOR_APPROVED") != "true":
        return "HOLD_OPERATOR_APPROVAL_REQUIRED"

    # Even with operator approval, runtime instrumentation remains
    # disabled until exporter and redaction behavior are verified.
    return "HOLD_EXPORTER_AND_REDACTION_NOT_VERIFIED"
