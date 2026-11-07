"""Authenticated, feature-gated imaging routes. They do not touch DISPATER."""

from __future__ import annotations

import base64
import binascii
import os
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from aurex.customer_sovereignty import assert_no_effect
from aurex.manuscript_forensics.images import AdmissionError, sniff
from aurex.manuscript_forensics.pipeline import examine_bytes, examine_fixture
from aurex.manuscript_forensics.spectral import examine_bands
from aurex.manuscript_forensics.templates import research_template, template_names

router = APIRouter(prefix="/v1/manuscript-forensics", tags=["manuscript-forensics"])


def forensics_enabled() -> bool:
    return os.environ.get("AUREX_MANUSCRIPT_FORENSICS") == "enabled"


def _require_enabled() -> None:
    assert_no_effect()
    if not forensics_enabled():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "FORENSICS_DISABLED")


class ExamineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_type: Literal["SYNTHETIC_ONLY"]
    fixture: Literal["faint-stroke-v1", "blank-v1", "noise-v1", "overlap-v1"] | None = None
    image_base64: str | None = Field(default=None, max_length=2_000_000)
    declared_type: Literal["PNG", "JPEG", "TIFF", "PDF"] | None = None
    filename: str = Field(default="synthetic.png", max_length=80)
    effect: str = Field(default="NONE", max_length=40)


class BandInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=40)
    image_base64: str = Field(min_length=1, max_length=2_000_000)
    wavelength_nm: float | None = Field(default=None, ge=1, le=100000)


class SpectralRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_type: Literal["SYNTHETIC_ONLY"]
    bands: list[BandInput] = Field(min_length=2, max_length=6)
    align: bool = False
    effect: str = Field(default="NONE", max_length=40)


def _label(filename: str) -> str:
    cleaned = filename.replace("\\", "/").split("/")[-1]
    if not cleaned or any(ord(char) < 32 for char in cleaned):
        return "unnamed"
    return cleaned


def _decode(payload: str) -> bytes:
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "IMAGE_ENCODING") from exc


def _refused(code: str) -> dict[str, Any]:
    return {
        "schema": "aurex.manuscript_forensics.report.v1",
        "decision": "REFUSED",
        "effect": "NONE",
        "authority": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "launch": "NOT_STARTED",
        "recovered_text": None,
        "decipherment": "NOT_CLAIMED",
        "problems": [code],
        "layers": [],
        "regions": [],
    }


@router.get("/status")
def get_status() -> dict[str, Any]:
    assert_no_effect()
    return {
        "schema": "aurex.manuscript_forensics.status.v1",
        "enabled": forensics_enabled(),
        "tier": 1,
        "effect": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "decipherment": "NOT_CLAIMED",
        "optional_workers": "DISABLED",
    }


@router.post("/examine")
def post_examine(payload: ExamineRequest) -> dict[str, Any]:
    _require_enabled()
    if payload.effect != "NONE":
        return _refused("EFFECT_REFUSED")
    if payload.fixture and payload.image_base64:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "FIXTURE_OR_IMAGE")
    if payload.fixture:
        report = examine_fixture(payload.fixture)
    elif payload.image_base64:
        data = _decode(payload.image_base64)
        if payload.declared_type and sniff(data) != payload.declared_type:
            return _refused("TYPE_MISMATCH")
        report = examine_bytes(data)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "IMAGE_REQUIRED")
    report["filename_label"] = _label(payload.filename)
    return report


@router.post("/spectral")
def post_spectral(payload: SpectralRequest) -> dict[str, Any]:
    _require_enabled()
    if payload.effect != "NONE":
        return _refused("EFFECT_REFUSED")
    try:
        return examine_bands([band.model_dump() for band in payload.bands], align=payload.align)
    except AdmissionError as exc:
        return _refused(exc.code)
    except (binascii.Error, ValueError):
        return _refused("IMAGE_ENCODING")


@router.get("/templates")
def get_templates() -> dict[str, Any]:
    _require_enabled()
    return {"templates": template_names(), "effect": "NONE", "decipherment": "NOT_CLAIMED"}


@router.get("/templates/{name}")
def get_template(name: str) -> dict[str, Any]:
    _require_enabled()
    if name not in template_names():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "UNKNOWN_TEMPLATE")
    return research_template(name)
