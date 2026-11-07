"""Bounded PDF and spreadsheet extraction.

Digital PDF text is extracted with pypdf. Spreadsheets are read with openpyxl.
Neither library executes macros, fetches URLs, or becomes a financial authority.
Image-only pages and PNG/JPEG scans are rejected when no OCR runtime is installed.
A failed parse is never returned as an empty successful extraction.
"""

from __future__ import annotations

import io
import zipfile
from typing import Any, NoReturn

import openpyxl  # type: ignore[import-untyped]
import pypdf
from pypdf.errors import PdfReadError

from aurex.dispater_ingest import FIELDS, REQUIRED, TABLES, IngestError, _cell

MAX_PAGES = 40
MAX_SHEETS = 8
MAX_UNCOMPRESSED = 4_000_000
MAX_EDGE = 4000
MAX_PIXELS = 8_000_000
PDF_PROCESSOR = f"pypdf@{pypdf.__version__}"
XLSX_PROCESSOR = f"openpyxl@{openpyxl.__version__}"


def _pages_from_text(text: str, page_number: int, source_sha256: str) -> tuple[str, dict[str, str], list[dict[str, Any]]]:
    rows: dict[str, str] = {}
    provenance: list[dict[str, Any]] = []
    table = ""
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key == "table":
            table = _cell(value)
            continue
        if not key:
            continue
        cleaned = _cell(value)
        rows[key] = cleaned
        provenance.append(
            {
                "field": key,
                "value": cleaned,
                "qualification": "EXTRACTED",
                "method": "pdf_text",
                "processor": PDF_PROCESSOR,
                "page": page_number,
                "source_sha256": source_sha256,
                "inferred": False,
                "review_required": False,
            }
        )
    if table not in TABLES and table not in ("equipment", "labor"):
        raise IngestError(f"page {page_number} has no supported table label")
    return table, rows, provenance


def extract_pdf(raw: bytes, source_sha256: str) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, Any]]]:
    try:
        reader = pypdf.PdfReader(io.BytesIO(raw))
        if reader.is_encrypted:
            raise IngestError("encrypted pdf rejected")
        pages = reader.pages
    except IngestError:
        raise
    except (PdfReadError, ValueError, TypeError) as exc:
        raise IngestError("malformed pdf rejected") from exc
    if len(pages) == 0 or len(pages) > MAX_PAGES:
        raise IngestError("pdf page count is outside the limit")
    tables: dict[str, list[dict[str, str]]] = {name: [] for name in (*TABLES, "equipment", "labor")}
    provenance: list[dict[str, Any]] = []
    for index, page in enumerate(pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            raise IngestError(f"page {index} could not be read") from exc
        if not text.strip():
            raise IngestError(
                f"page {index} has no extractable text; OCR runtime is not installed and the page was not interpreted"
            )
        table, fields, fields_provenance = _pages_from_text(text, index, source_sha256)
        expected = REQUIRED[table]
        if any(not fields.get(key) for key in expected):
            raise IngestError(f"page {index} is missing a required field")
        record = {key: fields[key] for key in FIELDS[table] if key in fields}
        record["_row"] = str(index)
        tables[table].append(record)
        provenance.extend(fields_provenance)
    return tables, provenance


def extract_xlsx(raw: bytes) -> dict[str, list[dict[str, str]]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile as exc:
        raise IngestError("xlsx is not a readable workbook") from exc
    names = archive.namelist()
    if any("vbaProject" in name for name in names):
        raise IngestError("spreadsheet macros are rejected")
    total = 0
    for info in archive.infolist():
        if info.file_size > MAX_UNCOMPRESSED:
            raise IngestError("spreadsheet entry exceeds the size limit")
        total += info.file_size
        if total > MAX_UNCOMPRESSED:
            raise IngestError("spreadsheet uncompressed size exceeds the limit")
    archive.close()
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=False, keep_vba=False)
    except Exception as exc:
        raise IngestError("malformed spreadsheet rejected") from exc
    try:
        if len(workbook.sheetnames) > MAX_SHEETS:
            raise IngestError("spreadsheet has too many sheets")
        tables: dict[str, list[dict[str, str]]] = {name: [] for name in (*TABLES, "equipment", "labor")}
        for sheet_name in workbook.sheetnames:
            if sheet_name not in tables:
                raise IngestError(f"sheet {sheet_name} is not a supported table")
            sheet = workbook[sheet_name]
            rows = sheet.iter_rows(values_only=True)
            try:
                header = next(rows)
            except StopIteration as exc:
                raise IngestError(f"sheet {sheet_name} is empty") from exc
            columns = [str(cell).strip() if cell is not None else "" for cell in header]
            expected = REQUIRED[sheet_name]
            if any(key not in columns for key in expected):
                raise IngestError(f"sheet {sheet_name} is missing required columns")
            for index, row in enumerate(rows, start=2):
                if index - 1 > 2000:
                    raise IngestError("spreadsheet exceeds the row limit")
                if row is None or all(cell is None or str(cell).strip() == "" for cell in row):
                    continue
                record: dict[str, str] = {}
                for key, cell in zip(columns, row, strict=False):
                    if key not in FIELDS[sheet_name] or cell is None:
                        continue
                    if isinstance(cell, bool | int | float):
                        raise IngestError(f"sheet {sheet_name} row {index} uses a numeric cell; money must be text")
                    text = "" if cell is None else str(cell)
                    if text.startswith("="):
                        text = "'" + text
                    record[key] = _cell(text)
                if any(not record.get(key) for key in expected):
                    raise IngestError(f"sheet {sheet_name} row {index} is missing a required value")
                record["_row"] = str(index)
                tables[sheet_name].append(record)
        return tables
    finally:
        workbook.close()


def _png_size(raw: bytes) -> tuple[int, int]:
    if len(raw) < 24 or not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise IngestError("malformed png rejected")
    width = int.from_bytes(raw[16:20], "big")
    height = int.from_bytes(raw[20:24], "big")
    if width <= 0 or height <= 0 or width > MAX_EDGE or height > MAX_EDGE or width * height > MAX_PIXELS:
        raise IngestError("image dimensions exceed the limit")
    return width, height


def _jpeg_size(raw: bytes) -> tuple[int, int]:
    if not raw.startswith(b"\xff\xd8"):
        raise IngestError("malformed jpeg rejected")
    index = 2
    while index + 8 < len(raw) and index < 200_000:
        if raw[index] != 0xFF:
            raise IngestError("malformed jpeg rejected")
        while index < len(raw) and raw[index] == 0xFF:
            index += 1
        if index >= len(raw):
            break
        marker = raw[index]
        index += 1
        if marker in (0xD8, 0xD9) or index + 2 > len(raw):
            continue
        length = int.from_bytes(raw[index : index + 2], "big")
        if length < 2:
            raise IngestError("malformed jpeg rejected")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if index + 7 > len(raw):
                raise IngestError("malformed jpeg rejected")
            height = int.from_bytes(raw[index + 3 : index + 5], "big")
            width = int.from_bytes(raw[index + 5 : index + 7], "big")
            if width <= 0 or height <= 0 or width > MAX_EDGE or height > MAX_EDGE or width * height > MAX_PIXELS:
                raise IngestError("image dimensions exceed the limit")
            return width, height
        index += length
    raise IngestError("jpeg dimensions were not found; the image was not interpreted")


def reject_unparsed_image(raw: bytes, kind: str) -> NoReturn:
    """Validate the image, then stop. No OCR runtime is invoked."""
    if kind == "png":
        _png_size(raw)
    elif kind == "jpeg":
        _jpeg_size(raw)
    else:
        raise IngestError("unsupported image type")
    raise IngestError("OCR runtime is not installed; the image was not interpreted")
