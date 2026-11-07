"""Tests for OpenTelemetry admission controls."""

from aurex_foundation.otel import instrument_fastapi


def test_otel_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AUREX_OTEL_ENABLED", raising=False)
    monkeypatch.delenv("AUREX_OTEL_OPERATOR_APPROVED", raising=False)

    assert instrument_fastapi(object()) == "DISABLED"


def test_otel_requires_operator_approval(monkeypatch):
    monkeypatch.setenv("AUREX_OTEL_ENABLED", "true")
    monkeypatch.delenv("AUREX_OTEL_OPERATOR_APPROVED", raising=False)

    assert (
        instrument_fastapi(object())
        == "HOLD_OPERATOR_APPROVAL_REQUIRED"
    )


def test_otel_remains_on_hold_after_approval(monkeypatch):
    monkeypatch.setenv("AUREX_OTEL_ENABLED", "true")
    monkeypatch.setenv("AUREX_OTEL_OPERATOR_APPROVED", "true")

    assert (
        instrument_fastapi(object())
        == "HOLD_EXPORTER_AND_REDACTION_NOT_VERIFIED"
    )
