"""Band arithmetic for supplied captures. Wavelengths are never invented."""

from __future__ import annotations

import base64
from typing import Any

from aurex.manuscript_forensics.images import AdmissionError, load_rgb, png_gray, png_rgb, sha256
from aurex.manuscript_forensics.pixels import grayscale


def _gray_band(data: bytes) -> tuple[int, int, list[int], str]:
    width, height, pixels, meta = load_rgb(data)
    return width, height, grayscale(pixels), str(meta["sniffed"])


def integer_shift(reference: list[int], moving: list[int], width: int, height: int) -> tuple[int, int]:
    """Search a +/-4 pixel window. This is not sub-pixel registration."""
    best = (0, 0)
    best_score: int | None = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            score = 0
            counted = 0
            for y in range(height):
                sy = y - dy
                if not 0 <= sy < height:
                    continue
                for x in range(width):
                    sx = x - dx
                    if not 0 <= sx < width:
                        continue
                    score += abs(reference[y * width + x] - moving[sy * width + sx])
                    counted += 1
            if counted == 0:
                continue
            mean = score // counted
            if best_score is None or mean < best_score:
                best_score = mean
                best = (dx, dy)
    return best


def apply_shift(values: list[int], width: int, height: int, dx: int, dy: int) -> tuple[list[int], int]:
    """Move a band by an integer offset. Pixels with no source sample stay absent (0)."""
    out: list[int] = []
    absent = 0
    for y in range(height):
        for x in range(width):
            sx = x - dx
            sy = y - dy
            if 0 <= sx < width and 0 <= sy < height:
                out.append(values[sy * width + sx])
            else:
                out.append(0)
                absent += 1
    return out, absent


def band_difference(left: list[int], right: list[int]) -> list[int]:
    return [max(0, min(255, 128 + (right[index] - left[index]) // 2)) for index in range(len(left))]


def guarded_ratio(denominator: list[int], numerator: list[int], floor: int) -> tuple[list[int], int]:
    out: list[int] = []
    absent = 0
    for index, base in enumerate(denominator):
        if base < floor:
            out.append(0)
            absent += 1
        else:
            out.append(max(0, min(255, numerator[index] * 255 // base)))
    return out, absent


def principal_component(bands: list[list[int]]) -> list[int]:
    count = len(bands)
    length = len(bands[0])
    means = [sum(band) / length for band in bands]
    centered = [[float(value) - means[index] for value in bands[index]] for index in range(count)]
    covariance = [[0.0 for _ in range(count)] for _ in range(count)]
    for row in range(count):
        for col in range(row, count):
            dot = sum(centered[row][index] * centered[col][index] for index in range(length))
            covariance[row][col] = covariance[col][row] = dot / length
    vector = [1.0 / (count**0.5) for _ in range(count)]
    for _ in range(24):
        nxt = [
            sum(covariance[row][col] * vector[col] for col in range(count)) for row in range(count)
        ]
        norm = sum(value * value for value in nxt) ** 0.5
        if norm < 1e-9:
            return [0 for _ in range(length)]
        vector = [value / norm for value in nxt]
    projected = [
        sum(vector[band] * centered[band][index] for band in range(count)) for index in range(length)
    ]
    low = min(projected)
    high = max(projected)
    if high - low < 1e-6:
        return [0 for _ in range(length)]
    return [max(0, min(255, round((value - low) * 255 / (high - low)))) for value in projected]


def _layer(method: str, values: list[int], width: int, height: int, parameters: dict[str, Any], limits: list[str]) -> dict[str, Any]:
    encoded = png_gray(values, width, height)
    return {
        "id": method,
        "method": method,
        "parameters": parameters,
        "limitations": limits,
        "sha256": sha256(encoded),
        "png_base64": base64.b64encode(encoded).decode("ascii"),
        "width": width,
        "height": height,
    }


def examine_bands(
    bands: list[dict[str, Any]], *, align: bool
) -> dict[str, Any]:
    decoded: list[tuple[int, int, list[int]]] = []
    sniffed: list[str] = []
    wavelengths: list[float | None] = []
    names: list[str] = []
    for band in bands:
        raw = base64.b64decode(str(band["image_base64"]), validate=True)
        width, height, values, kind = _gray_band(raw)
        decoded.append((width, height, values))
        sniffed.append(kind)
        wavelength = band.get("wavelength_nm")
        wavelengths.append(float(wavelength) if isinstance(wavelength, (int, float)) else None)
        names.append(str(band.get("name", "band")))
    width, height, _ = decoded[0]
    if any(item[0] != width or item[1] != height for item in decoded):
        raise AdmissionError("BAND_DIMENSIONS_DIFFER")
    grays = [item[2] for item in decoded]
    problems: list[str] = []
    if any(value is None for value in wavelengths):
        problems.append("MISSING_SPECTRAL_METADATA")
    shifts: list[dict[str, int]] = [{"dx": 0, "dy": 0, "absent_pixels": 0} for _ in grays]
    aligned = grays
    if align:
        aligned = [grays[0]]
        for index, values in enumerate(grays[1:], start=1):
            dx, dy = integer_shift(grays[0], values, width, height)
            moved, absent = apply_shift(values, width, height, dx, dy)
            aligned.append(moved)
            shifts[index] = {"dx": dx, "dy": dy, "absent_pixels": absent}
    layers: list[dict[str, Any]] = []
    if len(aligned) >= 2:
        layers.append(
            _layer(
                "band_difference",
                band_difference(aligned[0], aligned[1]),
                width,
                height,
                {"left": names[0], "right": names[1], "encoding": "128 + (right-left)/2"},
                ["This is a pixel difference, not a reflectance measurement or a recovered text."],
            )
        )
        ratio, absent = guarded_ratio(aligned[0], aligned[1], 8)
        layers.append(
            _layer(
                "guarded_band_ratio",
                ratio,
                width,
                height,
                {"denominator_floor": 8, "absent_pixels": absent},
                ["Where the denominator is below 8, the pixel is 0 because the ratio is undefined."],
            )
        )
    if len(aligned) >= 3:
        composite_pixels = [
            (aligned[0][index], aligned[1][index], aligned[2][index]) for index in range(width * height)
        ]
        encoded = png_rgb(composite_pixels, width, height)
        label = (
            "caller_asserted_wavelength_composite"
            if all(value is not None for value in wavelengths[:3])
            else "index_composite"
        )
        layers.append(
            {
                "id": "false_color",
                "method": label,
                "parameters": {
                    "red": names[0],
                    "green": names[1],
                    "blue": names[2],
                    "wavelengths_nm": [wavelengths[0], wavelengths[1], wavelengths[2]],
                    "wavelength_qualification": (
                        "CALLER_ASSERTED_NOT_INDEPENDENTLY_VERIFIED"
                        if label.startswith("caller")
                        else "NOT_PROVIDED"
                    ),
                },
                "limitations": [
                    "The colors are assigned band indices or caller-supplied numbers. They are not a spectroscopic identification."
                ],
                "sha256": sha256(encoded),
                "png_base64": base64.b64encode(encoded).decode("ascii"),
                "width": width,
                "height": height,
            }
        )
    layers.append(
        _layer(
            "principal_component",
            principal_component(aligned),
            width,
            height,
            {"components": 1, "iterations": 24, "aligned": align},
            ["The first component is a variance direction. It is not a material identification or a letter."],
        )
    )
    return {
        "schema": "aurex.manuscript_forensics.spectral.v1",
        "decision": "RECORDED",
        "effect": "NONE",
        "authority": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "launch": "NOT_STARTED",
        "recovered_text": None,
        "decipherment": "NOT_CLAIMED",
        "wavelengths_nm": wavelengths,
        "wavelength_qualification": (
            "NOT_PROVIDED" if "MISSING_SPECTRAL_METADATA" in problems else "CALLER_ASSERTED_NOT_INDEPENDENTLY_VERIFIED"
        ),
        "shifts": shifts,
        "problems": problems,
        "layers": layers,
        "source_sha256": [sha256(base64.b64decode(str(band["image_base64"]), validate=True)) for band in bands],
        "sniffed": sniffed,
    }
