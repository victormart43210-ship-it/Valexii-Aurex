"""Opt-in instrumentation. Never export traces without operator approval."""
import os


def instrument_fastapi(app):
    if os.environ.get("AUREX_OTEL_ENABLED", "false").lower() != "true":
        return "DISABLED"
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        return "HOLD_MISSING_DEPENDENCY"
    # No exporter or provider is configured by this module. Host config controls telemetry.
    FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/docs,/openapi.json")
    return "INSTRUMENTED_NO_EXPORTER_CONFIGURED"
