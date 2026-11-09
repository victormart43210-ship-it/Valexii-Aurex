"""Offline synthetic raster checks; none establish a historical reading."""
from __future__ import annotations

import base64
import hashlib
import io
from unittest.mock import patch

import pytest
from PIL import Image, PngImagePlugin

from aurex.manuscript_forensics.fixtures import faint_stroke
from aurex.manuscript_forensics.images import MAX_BYTES, MAX_EDGE, AdmissionError, load_rgb
from aurex.manuscript_forensics.pipeline import examine_bytes, examine_fixture


def encoded(width: int, height: int, kind: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (210, 210, 210)).save(buffer, format=kind)
    return buffer.getvalue()


@pytest.mark.parametrize("kind", ["PNG", "JPEG"])
def test_offline_formats_and_read_only_report_contract(kind: str) -> None:
    data = encoded(12, 8, kind)
    report = examine_bytes(data)
    assert report["schema"] == "aurex.manuscript_forensics.report.v1"
    assert report["decision"] == "RECORDED"
    assert report["source_sha256"] == hashlib.sha256(data).hexdigest()
    assert report["sniffed"] == kind
    assert (report["width"], report["height"]) == (12, 8)
    assert report["authority"] == report["effect"] == report["financial_authority"] == "NONE"
    assert report["production"] == "HOLD"
    assert report["recovered_text"] is None
    assert report["decipherment"] == "NOT_CLAIMED"
    for layer in report["layers"]:
        blob = base64.b64decode(layer["png_base64"], validate=True)
        assert layer["sha256"] == hashlib.sha256(blob).hexdigest()
        assert load_rgb(blob)[:2] == (12, 8)
        assert layer["parameters"] and layer["limitations"]


def test_component_geometry_and_transform_reproducibility() -> None:
    data, truth = faint_stroke()
    untouched = bytes(data)
    report = examine_bytes(data)
    assert data == untouched
    assert report == examine_bytes(data)
    assert report["source_sha256"] != report["layers"][1]["sha256"]
    assert report["regions"]
    for region in report["regions"]:
        x0, y0, x1, y1 = region["bbox"]
        assert 0 <= x0 < x1 <= report["width"]
        assert 0 <= y0 < y1 <= report["height"]
        assert x0 < truth["x1"] and x1 > truth["x0"]
        assert y0 < truth["y1"] and y1 > truth["y0"]
        assert region["reading"] is None
        assert region["classification"] == "UNVERIFIED_COMPONENT"
        blob = base64.b64decode(region["png_base64"])
        assert region["sha256"] == hashlib.sha256(blob).hexdigest()
        assert load_rgb(blob)[:2] == (x1 - x0, y1 - y0)


@pytest.mark.parametrize("name", ["blank-v1", "noise-v1"])
def test_blank_or_isolated_noise_does_not_become_reading(name: str) -> None:
    report = examine_fixture(name)
    assert report["regions"] == []
    assert report["recovered_text"] is None


def test_overlapping_bars_are_not_separated_into_readings() -> None:
    report = examine_fixture("overlap-v1")
    assert any("not separated" in entry for entry in report["limitations"])
    assert report["recovered_text"] is None


@pytest.mark.parametrize(("data", "reason"), [
    (b"", "EMPTY_FILE"),
    (b"x" * (MAX_BYTES + 1), "FILE_TOO_LARGE"),
    (b"GIF89a", "UNSUPPORTED_TYPE"),
    (b"II*\x00", "UNSUPPORTED_TYPE"),
    (b"%PDF-1.7", "PDF_RASTERIZATION_NOT_IN_TIER_1"),
    (b"\x89PNG\r\n\x1a\n", "IMAGE_UNREADABLE"),
    (b"\xff\xd8\xff", "IMAGE_UNREADABLE"),
])
def test_refused_files_have_no_outputs(data: bytes, reason: str) -> None:
    report = examine_bytes(data)
    assert report["decision"] == "REFUSED"
    assert report["problems"] == [reason]
    assert report["layers"] == report["regions"] == []
    assert report["authority"] == "NONE"


@pytest.mark.parametrize("size", [(MAX_EDGE + 1, 1), (1, MAX_EDGE + 1), (800, 800)])
def test_header_bounds_precede_decode_and_do_not_mutate_global(size: tuple[int, int]) -> None:
    data = encoded(*size)
    previous = Image.MAX_IMAGE_PIXELS
    with patch.object(PngImagePlugin.PngImageFile, "load", side_effect=AssertionError("decoded")):
        with pytest.raises(AdmissionError, match="DIMENSION_LIMIT"):
            load_rgb(data)
    assert Image.MAX_IMAGE_PIXELS == previous


def test_multiframe_png_is_refused_and_global_is_unchanged() -> None:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "white").save(
        buffer, format="PNG", save_all=True,
        append_images=[Image.new("RGB", (8, 8), "black")], duration=100,
    )
    previous = Image.MAX_IMAGE_PIXELS
    assert examine_bytes(buffer.getvalue())["problems"] == ["MULTI_FRAME_NOT_IN_TIER_1"]
    assert Image.MAX_IMAGE_PIXELS == previous


def test_embedded_metadata_is_not_a_reading() -> None:
    buffer = io.BytesIO()
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("recovered_text", "invented translation")
    Image.new("RGB", (8, 8), "white").save(buffer, format="PNG", pnginfo=metadata)
    report = examine_bytes(buffer.getvalue())
    assert report["recovered_text"] is None
    assert "invented translation" not in str(report)


def test_unknown_fixture_is_refused() -> None:
    assert examine_fixture("../private")["problems"] == ["UNKNOWN_FIXTURE"]


def test_decoder_never_temporarily_changes_pillow_global() -> None:
    data = encoded(8, 8)
    previous = Image.MAX_IMAGE_PIXELS
    original_load = PngImagePlugin.PngImageFile.load

    def checked_load(image: PngImagePlugin.PngImageFile, *args: object, **kwargs: object) -> object:
        assert Image.MAX_IMAGE_PIXELS == previous
        return original_load(image, *args, **kwargs)

    with patch.object(PngImagePlugin.PngImageFile, "load", checked_load):
        assert load_rgb(data)[:2] == (8, 8)
    assert Image.MAX_IMAGE_PIXELS == previous
