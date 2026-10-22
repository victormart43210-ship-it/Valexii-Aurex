#!/usr/bin/env python3
"""AUREX XXV: find a downloaded release ZIP by its checksum, not its filename.

Read-only unless --extract-to is explicit. Never runs scripts inside archives.
Downloads renamed by ChromeOS ("-1", " (1)", etc.) are supported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

MAX_DEPTH = 6
MAX_ENTRIES = 300
MAX_ARCHIVE_BYTES = 150 * 1024 * 1024
MAX_EXPANDED_BYTES = 350 * 1024 * 1024
PRUNE = frozenset({".git", ".cache", ".venv", ".npm", "node_modules", "__pycache__"})


class Hold(Exception):
    """A fail-closed, user-safe archive condition."""


def _digest(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            d.update(block)
    return d.hexdigest()


def find_verified(fragment: str, expected: str, roots: list[Path]) -> Path:
    """Return first exact-digest, regular, non-symlink ZIP under bounded search roots."""
    if not 6 <= len(fragment) <= 180 or "/" in fragment or "\\" in fragment:
        raise Hold("invalid filename fragment")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise Hold("expected SHA-256 must be 64 lowercase hexadecimal characters")
    examined: set[tuple[int, int]] = set()
    matches: list[Path] = []
    for root in roots:
        root = root.expanduser()
        if not root.is_dir() or root.is_symlink():
            continue
        for directory, subdirs, files in os.walk(root, topdown=True, followlinks=False):
            folder = Path(directory)
            depth = len(folder.relative_to(root).parts)
            subdirs[:] = sorted(
                name for name in subdirs
                if depth < MAX_DEPTH and name not in PRUNE and not (folder / name).is_symlink()
            )
            for name in sorted(files):
                if fragment.casefold() not in name.casefold() or not name.lower().endswith(".zip"):
                    continue
                p = folder / name
                try:
                    st = p.lstat()
                    if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_ARCHIVE_BYTES:
                        continue
                    identity = (st.st_dev, st.st_ino)
                    if identity in examined:
                        continue
                    examined.add(identity)
                    if _digest(p) == expected:
                        matches.append(p)
                except OSError:
                    continue
    if not matches:
        raise Hold("no downloaded ZIP matched the provided SHA-256; do not bypass verification")
    return sorted(matches, key=lambda p: (len(p.parts), len(str(p)), str(p)))[0]


def _valid_members(z: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = z.infolist()
    if not members or len(members) > MAX_ENTRIES:
        raise Hold("ZIP entry count outside safe bounds")
    total = 0
    seen: set[str] = set()
    roots: set[str] = set()
    for item in members:
        name = item.filename
        path = PurePosixPath(name)
        if (
            "\\" in name or "\x00" in name or not name or path.is_absolute()
            or any(p in {".", "..", ""} for p in name.rstrip("/").split("/"))
            or len(path.parts) < 2 or name in seen
        ):
            raise Hold("ZIP contains duplicate, absolute or unsafe member names")
        seen.add(name)
        roots.add(path.parts[0])
        mode = item.external_attr >> 16
        if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFDIR, stat.S_IFREG)):
            raise Hold("ZIP contains a symlink or unsafe filesystem object")
        if item.flag_bits & 1:
            raise Hold("ZIP contains encrypted entries")
        if item.file_size > MAX_EXPANDED_BYTES:
            raise Hold("ZIP member exceeds allowed size")
        total += item.file_size
        if total > MAX_EXPANDED_BYTES:
            raise Hold("ZIP expanded size exceeds allowed bound")
    if len(roots) != 1 or not next(iter(roots)).startswith("AUREX_"):
        raise Hold("ZIP must contain one AUREX release directory")
    if z.testzip() is not None:
        raise Hold("ZIP CRC validation failed")
    return members


def safe_extract(archive: Path, destination: Path) -> tuple[str, int, int]:
    """Preflight all entries and conflicts BEFORE writing, then create new files only."""
    if not destination.is_dir() or destination.is_symlink():
        raise Hold("extraction destination must be a real existing directory")
    destination = destination.resolve(strict=True)
    with zipfile.ZipFile(archive, "r") as z:
        members = _valid_members(z)
        paths: list[tuple[zipfile.ZipInfo, Path]] = []
        matches = 0
        dirs: set[Path] = set()
        for item in members:
            parts = PurePosixPath(item.filename).parts
            target = destination.joinpath(*parts)
            for parent in (target, *target.parents):
                if parent == destination:
                    break
                if parent.is_symlink():
                    raise Hold("symlink in extraction path")
            if item.is_dir():
                if target.exists() and not target.is_dir():
                    raise Hold("existing path conflicts with a ZIP directory")
                dirs.add(target)
                continue
            if target.exists():
                if not target.is_file() or _digest(target) != hashlib.sha256(z.read(item)).hexdigest():
                    raise Hold("existing file differs; refusing to overwrite")
                matches += 1
            else:
                paths.append((item, target))
            dirs.add(target.parent)
        for d in dirs:
            for parent in (d, *d.parents):
                if parent == destination:
                    break
                if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                    raise Hold("unsafe parent directory")
        for d in sorted(dirs, key=lambda p: len(p.parts)):
            d.mkdir(mode=0o700, parents=True, exist_ok=True)
        count = 0
        for item, target in paths:
            fd = os.open(
                target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600
            )
            try:
                with os.fdopen(fd, "wb") as out, z.open(item) as src:
                    while block := src.read(1024 * 1024):
                        out.write(block)
            except Exception:
                try:
                    target.unlink()
                except OSError:
                    pass
                raise
            count += 1
        return PurePosixPath(members[0].filename).parts[0], count, matches


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fragment", required=True, help="Stable part of ZIP name, ignoring ChromeOS suffixes")
    p.add_argument("--sha256", required=True, help="Published full-archive SHA-256 checksum")
    p.add_argument("--search-root", action="append", type=Path, help="Explicit search root; repeat as needed")
    p.add_argument("--extract-to", type=Path, help="Extract verified ZIP without overwriting existing files")
    args = p.parse_args(argv)
    try:
        roots = args.search_root or [Path.home(), Path("/mnt/chromeos/MyFiles/Downloads")]
        archive = find_verified(args.fragment, args.sha256, roots)
        root, written, existing = None, 0, 0
        if args.extract_to is not None:
            root, written, existing = safe_extract(archive, args.extract_to.expanduser())
        print(json.dumps({
            "status": "PASS", "zipPath": str(archive), "sha256": args.sha256,
            "bundleDirectory": str(args.extract_to.expanduser() / root) if root else None,
            "newFiles": written, "identicalFilesSkipped": existing,
            "authority": "NONE", "release": "HOLD",
        }, sort_keys=True))
        return 0
    except (Hold, OSError, zipfile.BadZipFile) as exc:
        print(json.dumps({
            "status": "HOLD",
            "reason": type(exc).__name__ if not isinstance(exc, Hold) else str(exc),
            "authority": "NONE", "release": "HOLD",
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
