"""Synthetic imaging checks. A visible mark is not a recovered text."""

from __future__ import annotations

import base64
import hashlib
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from aurex.api import app
from aurex.manuscript_forensics.fixtures import blank as blank_png
from aurex.manuscript_forensics.fixtures import faint_stroke, shifted_pair, spectral_mark
from aurex.manuscript_forensics.images import AdmissionError, load_rgb
from aurex.manuscript_forensics.pipeline import examine_bytes, examine_fixture
from aurex.manuscript_forensics.pixels import grayscale
from aurex.manuscript_forensics.spectral import apply_shift, examine_bands, integer_shift


def _overlap(box: list[int], truth: dict[str, int]) -> bool:
    return box[0] < truth["x1"] and box[2] > truth["x0"] and box[1] < truth["y1"] and box[3] > truth["y0"]


def test_a_faint_bar_is_measured_and_not_read() -> None:
    data, truth = faint_stroke()
    report = examine_bytes(data)
    assert report["decision"] == "RECORDED"
    assert report["recovered_text"] is None
    assert report["decipherment"] == "NOT_CLAIMED"
    assert report["effect"] == "NONE"
    assert report["source_sha256"] == hashlib.sha256(data).hexdigest()
    methods = {layer["method"] for layer in report["layers"]}
    assert {"grayscale", "channel_red", "adaptive_threshold", "background_residual"} <= methods
    assert all(layer["limitations"] for layer in report["layers"])
    assert any(_overlap(region["bbox"], truth) for region in report["regions"])
    assert all(region["reading"] is None for region in report["regions"])
    again = examine_bytes(data)
    assert [layer["sha256"] for layer in again["layers"]] == [layer["sha256"] for layer in report["layers"]]


def test_blank_and_salt_do_not_become_symbols() -> None:
    blank = examine_fixture("blank-v1")
    noise = examine_fixture("noise-v1")
    assert blank["regions"] == []
    assert noise["regions"] == []
    assert "not a reading" in blank["observation"]
    overlap = examine_fixture("overlap-v1")
    assert any("not separated" in item for item in overlap["limitations"])
    assert overlap["recovered_text"] is None


def test_bad_files_are_refused_without_pixels() -> None:
    pdf = examine_bytes(b"%PDF-1.7\n1 0 obj\n")
    assert pdf["problems"] == ["PDF_RASTERIZATION_NOT_IN_TIER_1"]
    assert pdf["layers"] == []
    assert pdf["source_sha256"] == hashlib.sha256(b"%PDF-1.7\n1 0 obj\n").hexdigest()
    assert examine_bytes(b"GIF89a")["problems"] == ["UNSUPPORTED_TYPE"]
    assert examine_bytes(b"")["problems"] == ["EMPTY_FILE"]
    previous = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None
    try:
        huge = io.BytesIO()
        Image.new("RGB", (800, 800), (10, 10, 10)).save(huge, format="PNG")
        refused = examine_bytes(huge.getvalue())
    finally:
        Image.MAX_IMAGE_PIXELS = previous
    assert refused["problems"] == ["DECOMPRESSION_LIMIT"]
    assert refused["layers"] == []


def test_spectral_metadata_is_not_invented_and_a_shift_is_recorded() -> None:
    bands, box = spectral_mark()
    encoded = [
        {"name": f"b{index}", "image_base64": base64.b64encode(band).decode("ascii"), "wavelength_nm": None}
        for index, band in enumerate(bands)
    ]
    report = examine_bands(encoded, align=False)
    assert report["wavelength_qualification"] == "NOT_PROVIDED"
    assert "MISSING_SPECTRAL_METADATA" in report["problems"]
    assert all(value is None for value in report["wavelengths_nm"])
    component = next(layer for layer in report["layers"] if layer["method"] == "principal_component")
    width, height, pixels, _meta = load_rgb(base64.b64decode(component["png_base64"]))
    gray = grayscale(pixels)
    inside = []
    outside = []
    for y in range(height):
        for x in range(width):
            value = gray[y * width + x]
            if box["x0"] <= x < box["x1"] and box["y0"] <= y < box["y1"]:
                inside.append(value)
            else:
                outside.append(value)
    assert sum(inside) / len(inside) != sum(outside) / len(outside)
    left, right = shifted_pair()
    left_g = grayscale(load_rgb(left)[2])
    right_g = grayscale(load_rgb(right)[2])
    found = integer_shift(left_g, right_g, 40, 24)
    assert found == (-2, 0)
    moved, _absent = apply_shift(right_g, 40, 24, found[0], found[1])
    assert moved[10 * 40 + 12] == left_g[10 * 40 + 12] == 40
    mismatched = [
        encoded[0],
        {
            "name": "other-size",
            "image_base64": base64.b64encode(blank_png()).decode("ascii"),
            "wavelength_nm": None,
        },
    ]
    with pytest.raises(AdmissionError, match="BAND_DIMENSIONS_DIFFER"):
        examine_bands(mismatched, align=False)


@pytest.mark.parametrize("flag", [None, "", "disabled", "ENABLED", "1", "true", " enabled", "enabled "])
def test_only_the_exact_enabled_flag_opens_the_laboratory(monkeypatch: pytest.MonkeyPatch, flag: str | None) -> None:
    if flag is None:
        monkeypatch.delenv("AUREX_MANUSCRIPT_FORENSICS", raising=False)
    else:
        monkeypatch.setenv("AUREX_MANUSCRIPT_FORENSICS", flag)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "synthetic-cclxxiii-gate-token-123456789")
    client = TestClient(app)
    headers = {"Authorization": "Bearer synthetic-cclxxiii-gate-token-123456789"}
    examine = client.post(
        "/v1/manuscript-forensics/examine",
        json={"dataset_type": "SYNTHETIC_ONLY", "fixture": "blank-v1"},
        headers=headers,
    )
    spectral = client.post(
        "/v1/manuscript-forensics/spectral",
        json={
            "dataset_type": "SYNTHETIC_ONLY",
            "bands": [
                {"name": "a", "image_base64": "YQ=="},
                {"name": "b", "image_base64": "YQ=="},
            ],
        },
        headers=headers,
    )
    templates = client.get("/v1/manuscript-forensics/templates", headers=headers)
    status = client.get("/v1/manuscript-forensics/status", headers=headers)
    assert examine.status_code == 403
    assert spectral.status_code == 403
    assert templates.status_code == 403
    assert status.status_code == 200
    body = status.json()
    assert body["enabled"] is False
    assert "png_base64" not in body
    assert body["effect"] == "NONE"


def test_the_route_is_gated_and_cannot_act(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUREX_MANUSCRIPT_FORENSICS", raising=False)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "synthetic-cclxx-forensics-token-123456")
    client = TestClient(app)
    headers = {"Authorization": "Bearer synthetic-cclxx-forensics-token-123456"}
    denied = client.post(
        "/v1/manuscript-forensics/examine",
        json={"dataset_type": "SYNTHETIC_ONLY", "fixture": "blank-v1"},
        headers=headers,
    )
    assert denied.status_code == 403
    assert client.post(
        "/v1/manuscript-forensics/examine",
        json={"dataset_type": "SYNTHETIC_ONLY", "fixture": "blank-v1"},
    ).status_code == 401
    monkeypatch.setenv("AUREX_MANUSCRIPT_FORENSICS", "enabled")
    examined = client.post(
        "/v1/manuscript-forensics/examine",
        json={"dataset_type": "SYNTHETIC_ONLY", "fixture": "faint-stroke-v1", "effect": "DEPLOY"},
        headers=headers,
    )
    assert examined.status_code == 200
    assert examined.json()["decision"] == "REFUSED"
    assert examined.json()["effect"] == "NONE"
    assert examined.json()["layers"] == []
    customer = client.post(
        "/v1/manuscript-forensics/examine",
        json={"dataset_type": "CUSTOMER", "fixture": "blank-v1"},
        headers=headers,
    )
    assert customer.status_code == 422
    mismatch = client.post(
        "/v1/manuscript-forensics/examine",
        json={
            "dataset_type": "SYNTHETIC_ONLY",
            "image_base64": base64.b64encode(b"\xff\xd8\xffnot-a-jpeg").decode("ascii"),
            "declared_type": "PNG",
        },
        headers=headers,
    )
    assert mismatch.json()["problems"] == ["TYPE_MISMATCH"]
    labeled = client.post(
        "/v1/manuscript-forensics/examine",
        json={
            "dataset_type": "SYNTHETIC_ONLY",
            "fixture": "blank-v1",
            "filename": "../../etc/passwd",
        },
        headers=headers,
    )
    assert labeled.status_code == 200
    assert labeled.json()["filename_label"] == "passwd"
    assert labeled.json()["regions"] == []
    template = client.get("/v1/manuscript-forensics/templates/voynich", headers=headers)
    assert template.json()["scholarly_status"] == "NOT_ESTABLISHED"
    assert "a decipherment" in template.json()["must_not_claim"]
