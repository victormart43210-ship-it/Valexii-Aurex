"""Synthetic images with known geometry. They are not manuscripts."""

from __future__ import annotations

import io

from PIL import Image


def _png(pixels: list[tuple[int, int, int]], width: int, height: int) -> bytes:
    image = Image.new("RGB", (width, height))
    image.putdata(pixels)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _canvas(width: int, height: int, tone: int) -> list[tuple[int, int, int]]:
    return [(tone, tone, tone) for _ in range(width * height)]


def paint(
    pixels: list[tuple[int, int, int]],
    width: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    tone: int,
) -> None:
    height = len(pixels) // width
    for y in range(max(0, y0), min(height, y1)):
        for x in range(max(0, x0), min(width, x1)):
            pixels[y * width + x] = (tone, tone, tone)


def faint_stroke() -> tuple[bytes, dict[str, int]]:
    """A gray bar on a lighter field. The box is the ground truth, not a reading."""
    width, height = 96, 64
    pixels = _canvas(width, height, 214)
    box = {"x0": 18, "y0": 28, "x1": 70, "y1": 34}
    paint(pixels, width, box["x0"], box["y0"], box["x1"], box["y1"], 150)
    return _png(pixels, width, height), box


def blank() -> bytes:
    return _png(_canvas(96, 64, 214), 96, 64)


def salt_noise() -> bytes:
    pixels = _canvas(96, 64, 214)
    # Isolated dark pixels. Each is below the component minimum.
    for index in (10, 40, 80, 200, 500, 900, 1400, 2000, 3000, 4000):
        pixels[index] = (40, 40, 40)
    return _png(pixels, 96, 64)


def overlap() -> bytes:
    pixels = _canvas(96, 64, 214)
    paint(pixels, 96, 16, 20, 78, 26, 80)
    paint(pixels, 96, 40, 10, 48, 52, 120)
    return _png(pixels, 96, 64)

