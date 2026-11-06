"""
DISPATER.AI Real-Company Industrial Validation Tooling — THE BIG ONE.

Provides secure, private, read-only discovery, inventorying, and controlled
ingestion for complex historical industrial records.

GOVERNANCE & PRIVACY SAFEGUARDS:
- Customer data in public repository: PROHIBITED.
- Unauthorized external transmission: PROHIBITED.
- External paid inference: OFF.
- Financial authority: NONE.
- Read-only processing: Original files are never modified, renamed, or deleted.
- Non-delegable: System is never its own sole witness.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {
    ".pdf": "PDF",
    ".xlsx": "XLSX",
    ".xlsm": "XLSM",
    ".csv": "CSV",
    ".json": "JSON",
    ".png": "IMAGE_PNG",
    ".jpg": "IMAGE_JPEG",
    ".jpeg": "IMAGE_JPEG",
}


class FileProcessingEligibility(StrEnum):
    ELIGIBLE_DIGITAL = "ELIGIBLE_DIGITAL"
    REQUIRES_OCR = "REQUIRES_OCR"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    REJECTED_MACRO = "REJECTED_MACRO"
    OVERSIZED = "OVERSIZED"
    UNREADABLE = "UNREADABLE"


@dataclass(frozen=True)
class DiscoveredRecordEntry:
    relative_path: str
    file_extension: str
    format_type: str
    byte_count: int
    content_sha256: str
    eligibility: FileProcessingEligibility
    discovered_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "file_extension": self.file_extension,
            "format_type": self.format_type,
            "byte_count": self.byte_count,
            "content_sha256": self.content_sha256,
            "eligibility": self.eligibility.value,
            "discovered_at_utc": self.discovered_at_utc,
        }


@dataclass
class TheBigOneInventoryReport:
    root_directory: str
    tenant_id: str
    scanned_at_utc: str
    total_files_discovered: int
    eligible_digital_files: int
    files_requiring_ocr: int
    rejected_files: int
    total_bytes_scanned: int
    inventory_manifest_sha256: str
    records: list[DiscoveredRecordEntry]

    def to_summary(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "scanned_at_utc": self.scanned_at_utc,
            "total_files_discovered": self.total_files_discovered,
            "eligible_digital_files": self.eligible_digital_files,
            "files_requiring_ocr": self.files_requiring_ocr,
            "rejected_files": self.rejected_files,
            "total_bytes_scanned": self.total_bytes_scanned,
            "inventory_manifest_sha256": self.inventory_manifest_sha256,
        }


def scan_local_directory(root_dir: str | Path, tenant_id: str) -> TheBigOneInventoryReport:
    """Read-only discovery of company directory. Never alters or exposes original files."""
    root = Path(root_dir)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory not found: {root}")

    discovered: list[DiscoveredRecordEntry] = []
    total_bytes = 0
    now_ts = datetime.now(UTC).isoformat()

    for dirpath, _, filenames in os.walk(root):
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            rel = str(fpath.relative_to(root))
            ext = fpath.suffix.lower()
            try:
                st = fpath.stat()
                size = st.st_size
                total_bytes += size
            except OSError:
                continue

            # Read file bytes for hash
            try:
                raw = fpath.read_bytes()
                h = hashlib.sha256(raw).hexdigest()
            except Exception:
                discovered.append(
                    DiscoveredRecordEntry(
                        relative_path=rel,
                        file_extension=ext,
                        format_type="UNKNOWN",
                        byte_count=size,
                        content_sha256="UNREADABLE",
                        eligibility=FileProcessingEligibility.UNREADABLE,
                    )
                )
                continue

            format_type = SUPPORTED_EXTENSIONS.get(ext, "UNSUPPORTED")
            if ext == ".xlsm":
                elig = FileProcessingEligibility.REJECTED_MACRO
            elif ext in (".png", ".jpg", ".jpeg"):
                elig = FileProcessingEligibility.REQUIRES_OCR
            elif ext in (".pdf", ".xlsx", ".csv", ".json"):
                if size > 10 * 1024 * 1024:
                    elig = FileProcessingEligibility.OVERSIZED
                else:
                    elig = FileProcessingEligibility.ELIGIBLE_DIGITAL
            else:
                elig = FileProcessingEligibility.UNSUPPORTED_FORMAT

            discovered.append(
                DiscoveredRecordEntry(
                    relative_path=rel,
                    file_extension=ext,
                    format_type=format_type,
                    byte_count=size,
                    content_sha256=h,
                    eligibility=elig,
                )
            )

    eligible_count = sum(1 for d in discovered if d.eligibility == FileProcessingEligibility.ELIGIBLE_DIGITAL)
    ocr_count = sum(1 for d in discovered if d.eligibility == FileProcessingEligibility.REQUIRES_OCR)
    rejected_count = len(discovered) - eligible_count - ocr_count

    manifest_bytes = json.dumps([d.to_dict() for d in discovered], sort_keys=True).encode("utf-8")
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

    return TheBigOneInventoryReport(
        root_directory=str(root),
        tenant_id=tenant_id,
        scanned_at_utc=now_ts,
        total_files_discovered=len(discovered),
        eligible_digital_files=eligible_count,
        files_requiring_ocr=ocr_count,
        rejected_files=rejected_count,
        total_bytes_scanned=total_bytes,
        inventory_manifest_sha256=manifest_sha,
        records=discovered,
    )
