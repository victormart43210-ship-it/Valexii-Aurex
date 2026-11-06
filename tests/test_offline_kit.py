"""Offline ZIP kit. The script stays runnable without this repository."""

import importlib.util
import json
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


def test_command_requires_a_separate_destination(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert kit.main(["--root", str(tmp_path)]) == 2
    report_path = tmp_path / "report.json"
    work = tmp_path / "work"
    code = kit.main(["--root", str(tmp_path / "missing"), "--dest", str(work), "--report", str(report_path)])
    assert code == 0
    saved = json.loads(report_path.read_text())
    assert saved["asset_status"] == "LOCAL_ASSET_ACCESS_REQUIRED"
    assert "LOCAL_ASSET_ACCESS_REQUIRED" in capsys.readouterr().out
