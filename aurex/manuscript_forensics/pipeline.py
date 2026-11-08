"""Traceable enhancements for one admitted image. No step replaces the source."""

from __future__ import annotations

import base64
from importlib.metadata import version
from typing import Any

from aurex.manuscript_forensics.fixtures import blank, faint_stroke, overlap, salt_noise
from aurex.manuscript_forensics.images import AdmissionError, load_rgb, png_gray, png_rgb, sha256
from aurex.manuscript_forensics.pixels import (
    box_mean,
    channel,
    close_ink,
    components,
    crop,
    darker_than_background,
    gradient,
    grayscale,
    median3,
    stretch,
)

_NOT_A_READING = "These pixels are a measurement of the scan. They are not a transcription."
_MINIMUM_COMPONENT = 12
_COMPONENT_LIMIT = 24


def _envelope(**extra: Any) -> dict[str, Any]:
    return {
        "schema": "aurex.manuscript_forensics.report.v1",
        "effect": "NONE",
        "authority": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "launch": "NOT_STARTED",
        "recovered_text": None,
        "decipherment": "NOT_CLAIMED",
        "tool": {"name": "aurex.manuscript_forensics", "pillow": version("pillow")},
        **extra,
    }


def _refused(code: str, source_sha256: str | None) -> dict[str, Any]:
    return _envelope(
        decision="REFUSED",
        problems=[code],
        source_sha256=source_sha256,
        layers=[],
        regions=[],
        limitations=[_NOT_A_READING],
    )


def _layer(
    method: str,
    encoded: bytes,
    width: int,
    height: int,
    parameters: dict[str, Any],
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "id": method,
        "method": method,
        "parameters": parameters,
        "limitations": limitations,
        "sha256": sha256(encoded),
        "png_base64": base64.b64encode(encoded).decode("ascii"),
        "width": width,
        "height": height,
    }


def examine_bytes(data: bytes) -> dict[str, Any]:
    digest = sha256(data)
    try:
        width, height, pixels, meta = load_rgb(data)
    except AdmissionError as exc:
        return _refused(exc.code, digest)
    gray = grayscale(pixels)
    background = box_mean(gray, width, height, 3)
    residual = [max(0, min(255, background[index] - gray[index])) for index in range(len(gray))]
    threshold = darker_than_background(gray, background, 12)
    closed = close_ink(threshold, width, height)
    groups = components(closed, width, height, minimum=_MINIMUM_COMPONENT, limit=_COMPONENT_LIMIT)
    original = png_rgb(pixels, width, height)
    layers = [
        _layer(
            "original_rgb",
            original,
            width,
            height,
            {"source": "decoded RGB, not a replacement of the admitted bytes"},
            ["The admitted file is unchanged. This PNG is a decoded copy."],
        ),
        _layer(
            "grayscale",
            png_gray(gray, width, height),
            width,
            height,
            {"weights": "299,587,114 per 1000"},
            ["Grayscale discards hue. It does not reveal ink that was not in the file."],
        ),
        _layer(
            "channel_red",
            png_gray(channel(pixels, 0), width, height),
            width,
            height,
            {"channel": 0},
            ["One recorded channel. An ordinary RGB file has no infrared band."],
        ),
        _layer(
            "channel_green",
            png_gray(channel(pixels, 1), width, height),
            width,
            height,
            {"channel": 1},
            ["One recorded channel. An ordinary RGB file has no infrared band."],
        ),
        _layer(
            "channel_blue",
            png_gray(channel(pixels, 2), width, height),
            width,
            height,
            {"channel": 2},
            ["One recorded channel. An ordinary RGB file has no ultraviolet band."],
        ),
        _layer(
            "local_contrast",
            png_gray(stretch(gray, 2, 98), width, height),
            width,
            height,
            {"low_percent": 2, "high_percent": 98},
            ["Contrast stretch can amplify noise and compression. A darker pixel is not recovered writing."],
        ),
        _layer(
            "background_residual",
            png_gray(residual, width, height),
            width,
            height,
            {"background": "box mean", "radius": 3},
            ["Bright values are darker than the local mean. They are not identified strokes."],
        ),
        _layer(
            "adaptive_threshold",
            png_gray(threshold, width, height),
            width,
            height,
            {"margin": 12, "ink": 0, "background": 255},
            ["The threshold is a pixel rule. It is not a transcription."],
        ),
        _layer(
            "median_denoise",
            png_gray(median3(gray, width, height), width, height),
            width,
            height,
            {"window": 3},
            ["A 3x3 median removes isolated points and also removes real single-pixel marks."],
        ),
        _layer(
            "gradient",
            png_gray(gradient(gray, width, height), width, height),
            width,
            height,
            {"kernel": "absolute neighbor difference"},
            ["Edges include paper texture, cracks, and compression. An edge is not a glyph."],
        ),
        _layer(
            "morphological_close",
            png_gray(closed, width, height),
            width,
            height,
            {"operation": "3x3 dilate then erode on ink"},
            ["Closing can join separate marks. The joined shape is not evidence they were one sign."],
        ),
    ]
    regions: list[dict[str, Any]] = []
    for index, box in enumerate(groups):
        values, crop_w, crop_h = crop(gray, width, box)
        encoded = png_gray(values, crop_w, crop_h)
        regions.append(
            {
                "id": f"component-{index + 1}",
                "classification": "UNVERIFIED_COMPONENT",
                "bbox": [box["x0"], box["y0"], box["x1"], box["y1"]],
                "pixels": box["pixels"],
                "sha256": sha256(encoded),
                "png_base64": base64.b64encode(encoded).decode("ascii"),
                "reading": None,
            }
        )
    observation = (
        "No component passed the 12-pixel minimum. This is not a reading."
        if not regions
        else "Components are pixel groups. None is a letter, a word, or a decipherment."
    )
    return _envelope(
        decision="RECORDED",
        problems=[],
        source_sha256=digest,
        decoded_png_sha256=sha256(original),
        sniffed=meta["sniffed"],
        width=width,
        height=height,
        layers=layers,
        regions=regions,
        observation=observation,
        limitations=[
            _NOT_A_READING,
            "Embedded text metadata in the file was not treated as writing.",
            "No spectral wavelength was assigned to this RGB image.",
        ],
    )


def examine_fixture(name: str) -> dict[str, Any]:
    if name == "faint-stroke-v1":
        data, _box = faint_stroke()
    elif name == "blank-v1":
        data = blank()
    elif name == "noise-v1":
        data = salt_noise()
    elif name == "overlap-v1":
        data = overlap()
    else:
        return _refused("UNKNOWN_FIXTURE", None)
    report = examine_bytes(data)
    report["fixture"] = name
    if name == "overlap-v1":
        report["limitations"] = [
            *report["limitations"],
            "Overlapping bars were not separated into two readings.",
        ]
    return report
