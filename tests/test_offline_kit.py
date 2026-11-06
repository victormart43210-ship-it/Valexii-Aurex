"""Offline ZIP kit. The script stays runnable without this repository."""

import importlib.util
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "valexii_offline_kit.py"
_SPEC = importlib.util.spec_from_file_location("valexii_offline_kit", _SCRIPT)
assert _SPEC and _SPEC.loader
kit = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(kit)


def _zip(path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in members.items():
            archive.writestr(name, text)


def test_duplicate_suffixes_stay_separate_and_a_rerun_does_not_rewrite(tmp_path: Path) -> None:
    source = tmp_path / "usb"
    source.mkdir()
    _zip(source / "DISPATER_OFFLINE_ENGINEERING_KIT.zip", {"readme.txt": "one"})
    _zip(source / "DISPATER_OFFLINE_ENGINEERING_KIT (1).zip", {"readme.txt": "two"})
    dest = tmp_path / "work"
    first = kit.build_report([source], dest, None)
    assert first["asset_status"] == "ARCHIVES_INVENTORIED"
    assert len(first["archives"]) == 2
    assert {item["status"] for item in first["archives"]} == {"EXTRACTED"}
    assert (source / "DISPATER_OFFLINE_ENGINEERING_KIT.zip").is_file()
    second = kit.build_report([source], dest, None)
    assert {item["status"] for item in second["archives"]} == {"ALREADY_PRESENT"}
    assert first["numeric_candidates_are_findings"] is False
    assert first["confirmed_recovery_usd"] == "0.00"


def test_unsafe_paths_and_source_folder_writes_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "usb"
    source.mkdir()
    hostile = source / "hostile.zip"
    _zip(hostile, {"../escape.txt": "no"})
    report = kit.build_report([source], tmp_path / "work", None)
    assert report["archives"][0]["status"] == "REJECTED_UNSAFE_PATH"
    assert not (tmp_path / "escape.txt").exists()
    safe = source / "safe.zip"
    _zip(safe, {"note.txt": "ok"})
    refused = kit.extract_archive(safe, source)
    assert refused["status"] == "REJECTED_WOULD_TOUCH_SOURCE"
    assert list(source.glob("note.txt")) == []


def test_missing_repository_and_missing_root_are_explicit(tmp_path: Path) -> None:
    absent = kit.assess_repository(tmp_path / "no-repo")
    assert absent == {"status": "REPOSITORY_ABSENT", "remote": None, "head": None}
    report = kit.build_report([tmp_path / "not-mounted"], tmp_path / "work", tmp_path / "no-repo")
    assert report["asset_status"] == "LOCAL_ASSET_ACCESS_REQUIRED"
    assert report["repository"]["status"] == "REPOSITORY_ABSENT"
    assert report["downloads"] == "NOT_STARTED"


def test_duplicate_bytes_resource_limits_and_a_bad_manifest_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "usb"
    source.mkdir()
    payload = {"readme.txt": "same"}
    _zip(source / "kit.zip", payload)
    _zip(source / "kit (1).zip", payload)
    first = kit.build_report([source], tmp_path / "work", None)
    statuses = {item["status"] for item in first["archives"]}
    assert statuses == {"EXTRACTED", "DUPLICATE_CONTENT"}
    assert kit.resource_violation(1, 5_000_000, 100) == "COMPRESSION_RATIO"
    huge = source / "huge.zip"
    _zip(huge, {"note.txt": "x" * 50})
    limited = kit.extract_archive(huge, tmp_path / "other", max_uncompressed=10)
    assert limited["status"] == "REJECTED_RESOURCE_LIMIT"
    (source / "kit.zip.sha256").write_text("0" * 64 + "\n")
    mismatch = kit.extract_archive(source / "kit.zip", tmp_path / "third")
    assert mismatch["status"] == "REJECTED_MANIFEST"


def test_interrupted_extraction_resumes_and_checkpoints_stay_unmodified(tmp_path: Path) -> None:
    source = tmp_path / "usb"
    source.mkdir()
    _zip(source / "kit.zip", {"readme.txt": "kept"})
    dest = tmp_path / "work"
    extracted = kit.extract_archive(source / "kit.zip", dest)
    target = Path(extracted["extracted_to"])
    (target / "readme.txt").unlink()
    (target / "INVENTORY.json").unlink()
    (target / ".partial").write_text("partial")
    resumed = kit.extract_archive(source / "kit.zip", dest)
    assert resumed["status"] == "RESUMED"
    assert (target / "readme.txt").read_text() == "kept"
    assert not (target / ".partial").exists()
    database = source / "checkpoint.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE failed_pages (page INTEGER)")
    connection.commit()
    connection.close()
    before = database.stat().st_mtime_ns
    found = kit.discover_sqlite([source])
    assert found[0]["status"] == "DISCOVERED_READ_ONLY"
    assert found[0]["authoritative"] is False
    assert found[0]["tables"] == ["failed_pages"]
    assert database.stat().st_mtime_ns == before
    (source / "ocr-progress.json").write_text(
        '{"pages_processed": 1, "pages_remaining": 2, "numeric_candidates": 236, "failed_pages": [4, 9]}'
    )
    progress = kit.read_ocr_progress([source])
    assert progress["numeric_candidates_are_findings"] is False
    assert progress["manifests"][0]["failed_pages_retained"] == 2
    broken = source / "broken.zip"
    broken.write_bytes(b"not a zip")
    assert kit.extract_archive(broken, tmp_path / "broken-out")["status"] == "REJECTED_INTEGRITY"


def test_hidden_directories_are_not_treated_as_checkpoints(tmp_path: Path) -> None:
    hidden = tmp_path / ".config"
    hidden.mkdir()
    connection = sqlite3.connect(hidden / "secret.db")
    connection.execute("CREATE TABLE keys (id INTEGER)")
    connection.commit()
    connection.close()
    visible = tmp_path / "checkpoint.sqlite"
    connection = sqlite3.connect(visible)
    connection.execute("CREATE TABLE pages (page INTEGER)")
    connection.commit()
    connection.close()
    found = kit.discover_sqlite([tmp_path])
    assert [item["path"] for item in found] == [str(visible)]
    assert found[0]["authoritative"] is False


def test_command_requires_a_separate_destination(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert kit.main(["--root", str(tmp_path)]) == 2
    report_path = tmp_path / "report.json"
    work = tmp_path / "work"
    code = kit.main(["--root", str(tmp_path / "missing"), "--dest", str(work), "--report", str(report_path)])
    assert code == 0
    saved = json.loads(report_path.read_text())
    assert saved["asset_status"] == "LOCAL_ASSET_ACCESS_REQUIRED"
    assert "LOCAL_ASSET_ACCESS_REQUIRED" in capsys.readouterr().out
