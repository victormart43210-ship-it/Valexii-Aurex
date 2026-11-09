"""Regression tests for privileged /data ownership setup (no root required)."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from unittest.mock import patch

import pytest


def _load_entrypoint():
    path = Path(__file__).resolve().parents[1] / "docker" / "entrypoint.py"
    spec = importlib.util.spec_from_file_location("aurex_container_entrypoint", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_prepare_data_dir_never_fchowns_symlink_target(tmp_path: Path) -> None:
    module = _load_entrypoint()
    data = tmp_path / "data"
    data.mkdir()
    external = tmp_path / "outside"
    external.write_text("do not touch", encoding="utf-8")
    (data / "safe.db").write_text("db", encoding="utf-8")
    (data / "link.db").symlink_to(external)

    real_open = os.open
    real_makedirs = os.makedirs
    touched: list[tuple[int, int]] = []

    def redirected_open(path, flags, *args, **kwargs):
        if path == "/data":
            path = str(data)
        return real_open(path, flags, *args, **kwargs)

    def redirected_makedirs(path, *args, **kwargs):
        if path == "/data":
            path = str(data)
        return real_makedirs(path, *args, **kwargs)

    def record_fchown(fd: int, uid: int, gid: int) -> None:
        st = os.fstat(fd)
        touched.append((st.st_dev, st.st_ino))

    with (
        patch.object(module.os, "open", side_effect=redirected_open),
        patch.object(module.os, "makedirs", side_effect=redirected_makedirs),
        patch.object(module.os, "fchown", side_effect=record_fchown),
    ):
        module.prepare_data_dir()

    external_st = external.stat()
    safe_st = (data / "safe.db").stat()
    assert (external_st.st_dev, external_st.st_ino) not in touched
    assert (safe_st.st_dev, safe_st.st_ino) in touched
    assert external.read_text(encoding="utf-8") == "do not touch"


def test_prepare_data_dir_rejects_symlinked_data_directory(tmp_path: Path) -> None:
    module = _load_entrypoint()
    real_data = tmp_path / "real"
    real_data.mkdir()
    link = tmp_path / "data"
    link.symlink_to(real_data, target_is_directory=True)

    real_open = os.open

    def redirected_open(path, flags, *args, **kwargs):
        return real_open(str(link) if path == "/data" else path, flags, *args, **kwargs)

    with (
        patch.object(module.os, "open", side_effect=redirected_open),
        patch.object(module.os, "makedirs", return_value=None),
        patch.object(module.os, "fchown") as fchown,
    ):
        with pytest.raises(OSError):
            module.prepare_data_dir()
        fchown.assert_not_called()
