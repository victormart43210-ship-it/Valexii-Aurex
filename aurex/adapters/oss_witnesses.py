"""Opt-in independent open-source witnesses. None can grant BCXMET runtime authority.

The adapters intentionally perform no network requests, imports of heavyweight
model weights, or telemetry exports at import time.
"""
from __future__ import annotations

import hashlib
import json
import re
from contextlib import contextmanager, nullcontext
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Witness:
    source: str
    status: str
    observed_at: str
    content_sha256: str | None
    claims: tuple[str, ...]
    qualification: str

    def json_ready(self) -> dict[str, Any]:
        result = asdict(self)
        result["claims"] = list(self.claims)
        return result


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
    if "security_score" not in report and "code_analysis" not in report and "manifest_analysis" not in report:
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
    except (ValueError, TypeError, OverflowError) as exc:
        return Witness("Astronomy Engine", "HOLD", _now(), None, (),
                       f"Input/calculation not qualified ({type(exc).__name__})")


def madlad_text_candidate(
    text: str, target_language_tag: str, tokenizer: Any, model: Any
) -> Witness:
    """Generate a candidate with a caller-provided *locally loaded* MADLAD model.

    No weights are downloaded here; no remote inference endpoint is called.
    Tokenizer/model provenance, permission and license must be checked by caller.
    """
    if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", target_language_tag):
        raise ValueError("Invalid language tag")
    if not text or len(text) > 4000:
        raise ValueError("text must be 1..4000 characters")
    prompt = f"<2{target_language_tag}> {text}"
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        tokens = model.generate(**inputs, max_new_tokens=128, do_sample=False)
        output = tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
        if not isinstance(output, str) or not output.strip():
            raise ValueError("empty model output")
    except Exception as exc:  # untrusted optional model backend must fail closed
        return Witness("MADLAD-400 candidate", "HOLD", _now(), None, (),
                       f"Local model execution not qualified ({type(exc).__name__})")
    return Witness("MADLAD-400 candidate", "HOLD", _now(),
                   hashlib.sha256(output.encode("utf-8")).hexdigest(),
                   ("Generated output requires independent comparison and language anchors",),
                   "Machine translation proposal only; not decipherment or a validated reading")


@contextmanager
def optional_trace(operation: str, *, enabled: bool = False) -> Iterator[None]:
    """Optional OpenTelemetry trace with no secrets, manuscript text or user identifiers."""
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,64}", operation):
        raise ValueError("Invalid trace operation name")
    if not enabled:
        with nullcontext():
            yield
        return
    try:
        from opentelemetry import trace  # type: ignore[import-not-found]
    except ImportError:
        with nullcontext():
            yield
        return
    tracer = trace.get_tracer("valexii-aurex.oss-witnesses")
    with tracer.start_as_current_span(operation):
        yield
