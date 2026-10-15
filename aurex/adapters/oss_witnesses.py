"""Ingest and normalise OSS witnesses and small optional integrations."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Mapping


_HEX64 = None


class Witness:
    def __init__(self, source: str, status: str, observed: str, digest: str | None, claims: tuple[str, ...], note: str):
        self.source = source
        self.status = status
        self.observed = observed
        self.digest = digest
        self.claims = claims
        self.note = note


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def mobsf_json_witness(report: Mapping[str, Any], expected_apk_sha256: str) -> Witness:
    """Ingest a locally exported MobSF report; never treat tool output as an authority.

    Important: MobSF API's generic 'hash' field may be MD5, not SHA-256.
    Only a verified explicit sha256 field is accepted as an APK link here.
    """
    observed = _now()
    apk_digest = expected_apk_sha256.lower().strip()
    if not _HEX64.fullmatch(apk_digest):
        raise ValueError("expected_apk_sha256 must be exactly 64 hex characters")
    if not isinstance(report, Mapping):
        raise TypeError("MobSF report must be a mapping")
    report_hash = _digest(report)
    reported = str(report.get("sha256", "")).lower().strip()
    if not _HEX64.fullmatch(reported):
        return Witness("MobSF", "HOLD", observed, report_hash, (),
                       "No explicit trusted SHA-256 binding to the APK")
    if reported != apk_digest:
        return Witness("MobSF", "CONTESTED", observed, report_hash, (),
                       "MobSF report SHA-256 does not match the expected APK")
    if (
        "security_score" not in report
        and "code_analysis" not in report
        and "manifest_analysis" not in report
    ):
        return Witness("MobSF", "INSUFFICIENT", observed, report_hash, (),
                       "Digest matches, but security result fields were not supplied")
    return Witness("MobSF", "INSUFFICIENT", observed, report_hash,
                   ("External report ingested and explicitly APK-bound",),
                   "Requires independent report/source verification and finding review")


def astronomy_moon_witness(utc_iso: str) -> Witness:
    """Run Astronomy Engine on a caller-supplied UTC instant; observational context only.

    Optional dependency: pip install astronomy-engine
    """
    try:
        from astronomy import MoonPhase, Time  # type: ignore[import-not-found]
    except ImportError:
        return Witness("Astronomy Engine", "HOLD", _now(), None, (),
                       "astronomy-engine dependency not installed")
    try:
        value = utc_iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            raise ValueError("UTC offset required")
        dt = dt.astimezone(timezone.utc)
        phase_degrees = float(MoonPhase(Time.Parse(dt.strftime("%Y-%m-%dT%H:%M:%SZ"))))
        if not (0.0 <= phase_degrees < 360.0):
            raise ValueError("phase outside expected range")
        result = {"utc": dt.isoformat(), "moon_phase_degrees": round(phase_degrees, 7)}
        return Witness("Astronomy Engine", "INSUFFICIENT", _now(), _digest(result),
                       (f"Moon phase angle: {phase_degrees:.4f} degrees UTC",),
                       "Computed astronomical context, not proof of manuscript semantics")
    except Exception:
        return Witness("Astronomy Engine", "HOLD", _now(), None, (), "astronomy engine error")
