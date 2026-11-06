"""
AUREX-OX Worldwide Model Vault — Removable Media (USB) Preparation.

Provides safe, operator-confirmed preparation for local open-weight model archiving
on the owner's 256 GB USB or local storage.

STRICT INVARIANTS:
- No formatting, repartitioning, or automatic drive modification.
- Existing files (including THE BIG ONE or personal data) are NEVER deleted or overwritten.
- Target directory is strictly isolated under `AUREX-OX-MODEL-VAULT`.
- Default mode is DRY RUN: No bytes written without explicit confirmation.
- No network download without operator approval and license validation.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


class VaultExecutionMode(StrEnum):
    DRY_RUN = "DRY_RUN"
    LIVE_CONFIRMED = "LIVE_CONFIRMED"


@dataclass
class StorageProbeReport:
    target_path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    free_gigabytes: float
    has_existing_vault: bool
    is_writable: bool


@dataclass(frozen=True)
class VaultManifestEntry:
    model_id: str
    family: str
    revision: str
    sha256: str
    size_bytes: int
    license: str
    relative_path: str
    added_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ModelVaultManager:
    """Manages isolated model storage on removable media without touching existing records."""

    VAULT_DIR_NAME = "AUREX-OX-MODEL-VAULT"

    def __init__(self, mount_point: str | Path, mode: VaultExecutionMode = VaultExecutionMode.DRY_RUN) -> None:
        self.mount_point = Path(mount_point)
        self.mode = mode
        self.vault_path = self.mount_point / self.VAULT_DIR_NAME

    def probe_storage(self) -> StorageProbeReport:
        if not self.mount_point.exists() or not self.mount_point.is_dir():
            raise ValueError(f"Mount point does not exist or is not a directory: {self.mount_point}")

        try:
            total, used, free = shutil.disk_usage(self.mount_point)
        except OSError as exc:
            raise RuntimeError(f"Unable to query disk usage on {self.mount_point}: {exc}") from exc

        free_gb = round(free / (1024 ** 3), 2)
        has_vault = self.vault_path.exists() and self.vault_path.is_dir()
        is_writable = os.access(self.mount_point, os.W_OK)

        return StorageProbeReport(
            target_path=str(self.mount_point),
            total_bytes=total,
            used_bytes=used,
            free_bytes=free,
            free_gigabytes=free_gb,
            has_existing_vault=has_vault,
            is_writable=is_writable,
        )

    def initialize_vault(self) -> dict[str, Any]:
        """Creates isolated vault folder and manifest if in LIVE_CONFIRMED mode."""
        probe = self.probe_storage()
        if not probe.is_writable:
            raise PermissionError(f"Target mount point is not writable: {self.mount_point}")

        manifest_path = self.vault_path / "vault_manifest.json"

        if self.mode == VaultExecutionMode.DRY_RUN:
            return {
                "status": "DRY_RUN_ONLY",
                "message": "Vault initialization simulated. No disk modifications made.",
                "target_vault_dir": str(self.vault_path),
                "free_gigabytes": probe.free_gigabytes,
                "manifest_path": str(manifest_path),
            }

        # LIVE_CONFIRMED mode
        self.vault_path.mkdir(parents=True, exist_ok=True)
        if not manifest_path.exists():
            manifest_init = {
                "vault_version": "1.0.0",
                "created_at_utc": datetime.now(UTC).isoformat(),
                "models": [],
            }
            manifest_path.write_text(json.dumps(manifest_init, indent=2))

        return {
            "status": "INITIALIZED",
            "target_vault_dir": str(self.vault_path),
            "manifest_path": str(manifest_path),
            "free_gigabytes": probe.free_gigabytes,
        }
