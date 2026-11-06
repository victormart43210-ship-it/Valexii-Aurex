"""
Tests for AUREX-OX Removable Media Model Vault Preparation.

Verifies:
1. Storage probe queries disk usage safely.
2. Dry-run mode writes zero bytes to target directory.
3. Live confirmed mode creates isolated AUREX-OX-MODEL-VAULT directory and manifest.
4. Existing files in directory are never overwritten, touched, or deleted.
"""

from pathlib import Path

from aurex.ox.vault import ModelVaultManager, VaultExecutionMode


def test_vault_dry_run_does_not_modify_disk(tmp_path: Path) -> None:
    # Existing mock USB content (e.g. personal records or THE BIG ONE)
    existing_file = tmp_path / "important_records.txt"
    existing_file.write_text("pre-existing inviolable data")

    manager = ModelVaultManager(tmp_path, mode=VaultExecutionMode.DRY_RUN)
    probe = manager.probe_storage()
    assert probe.free_gigabytes >= 0.0
    assert not probe.has_existing_vault

    result = manager.initialize_vault()
    assert result["status"] == "DRY_RUN_ONLY"
    assert not (tmp_path / "AUREX-OX-MODEL-VAULT").exists()
    assert existing_file.read_text() == "pre-existing inviolable data"


def test_vault_live_confirmed_creates_isolated_vault(tmp_path: Path) -> None:
    existing_file = tmp_path / "the_big_one_archive.dat"
    existing_file.write_bytes(b"protected binary")

    manager = ModelVaultManager(tmp_path, mode=VaultExecutionMode.LIVE_CONFIRMED)
    result = manager.initialize_vault()
    assert result["status"] == "INITIALIZED"

    vault_dir = tmp_path / "AUREX-OX-MODEL-VAULT"
    assert vault_dir.exists()
    assert (vault_dir / "vault_manifest.json").exists()

    # Inviolable check
    assert existing_file.read_bytes() == b"protected binary"
