"""Admit a small image and keep the original bytes intact."""

from __future__ import annotations

import hashlib
import io
from typing import Any

from PIL import Image, UnidentifiedImageError

MAX_BYTES = 1_500_000
MAX_EDGE = 512
MAX_PIXELS = MAX_EDGE * MAX_EDGE

_PNG = b"\x89PNG\r\n\x1a\n"
_JPEG = b"\xff\xd8\xff"
_TIFF_LE = b"II*\x00"
_TIFF_BE = b"MM\x00*"
_PDF = b"%PDF"


class AdmissionError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sniff(data: bytes) -> str:
    if data.startswith(_PNG):
        return "PNG"
    if data.startswith(_JPEG):
        return "JPEG"
    if data.startswith(_TIFF_LE) or data.startswith(_TIFF_BE):
        return "TIFF"
    if data.startswith(_PDF):
        return "PDF"
    return "UNKNOWN"


def _reject_size(data: bytes) -> None:
    if not data:
        raise AdmissionError("EMPTY_FILE")
    if len(data) > MAX_BYTES:
        raise AdmissionError("FILE_TOO_LARGE")


def load_rgb(data: bytes) -> tuple[int, int, list[tuple[int, int, int]], dict[str, Any]]:
    """Decode bounded single-frame PNG or JPEG into RGB. The caller keeps the original bytes."""
    _reject_size(data)
    kind = sniff(data)
    if kind == "PDF":
        raise AdmissionError("PDF_RASTERIZATION_NOT_IN_TIER_1")
    if kind == "UNKNOWN":
        raise AdmissionError("UNSUPPORTED_TYPE")
    if kind not in {"PNG", "JPEG"}:
        raise AdmissionError("UNSUPPORTED_TYPE")
    try:
        # Restrict plugins as well as magic bytes. Image.open reads headers lazily;
        # bounds MUST be checked before load/convert allocates the decoded raster.
        with Image.open(io.BytesIO(data), formats=("PNG", "JPEG")) as incoming:
            width, height = incoming.size
            if (width < 1 or height < 1 or width > MAX_EDGE or height > MAX_EDGE
                    or width * height > MAX_PIXELS):
                raise AdmissionError("DIMENSION_LIMIT")
            if int(getattr(incoming, "n_frames", 1)) != 1:
                raise AdmissionError("MULTI_FRAME_NOT_IN_TIER_1")
            if incoming.format != kind:
                raise AdmissionError("FORMAT_MISMATCH")
            incoming.load()
            image = incoming.convert("RGB")
    except AdmissionError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise AdmissionError("DECOMPRESSION_LIMIT") from exc
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise AdmissionError("IMAGE_UNREADABLE") from exc
    raw = list(image.get_flattened_data())
    pixels: list[tuple[int, int, int]] = []
    for item in raw:
        if not isinstance(item, tuple) or len(item) < 3:
            raise AdmissionError("UNSUPPORTED_PIXEL")
        pixels.append((int(item[0]), int(item[1]), int(item[2])))
    return width, height, pixels, {"sniffed": kind, "frames": 1}


def png_gray(values: list[int], width: int, height: int) -> bytes:
    image = Image.new("L", (width, height))
    image.putdata([max(0, min(255, int(value))) for value in values])
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def png_rgb(pixels: list[tuple[int, int, int]], width: int, height: int) -> bytes:
    image = Image.new("RGB", (width, height))
    image.putdata(pixels)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
