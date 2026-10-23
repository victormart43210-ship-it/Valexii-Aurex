"""Outbound-only ORCA R8 status publisher. Opt-in; no private corpus leaves the laptop.

Read a deliberately minimal JSON status file created by ORCA. NEVER point this
script at private evidence or a directory. No tunnel or local HTTP listener.
Usage: python workstation/orca_r8_publisher.py --status-file /path/to/status.json --dry-run
       python workstation/orca_r8_publisher.py --status-file /path/to/status.json --once
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from pydantic import ValidationError

from aurex.orca_r8_sync import MAX_BODY_BYTES, PUSH_PATH, Snapshot


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _endpoint(base: str) -> str:
    parts = urllib.parse.urlsplit(base)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.port not in (None, 443)
        or parts.path not in ("", "/")
        or parts.query
        or parts.fragment
    ):
        raise ValueError("expected an HTTPS backend origin without path, credentials or custom port")
    return base.rstrip("/") + PUSH_PATH


def _read_safe_snapshot(path: Path) -> tuple[bytes, str]:
    # Do not follow symlinks. Fail if the export is not a regular, small JSON file.
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BODY_BYTES:
        raise ValueError("status source must be a small regular JSON file, not a symlink")
    payload = path.read_bytes()
    try:
        snapshot = Snapshot.model_validate_json(payload)
    except (ValidationError, ValueError):
        raise ValueError("status file does not match allowlisted ORCA R8 fields") from None
    # Serialization discards formatting; validation rejects all unapproved fields.
    sanitized = snapshot.model_dump_json(exclude_none=True).encode("utf-8")
    if len(sanitized) > MAX_BODY_BYTES:
        raise ValueError("status export exceeds upload limit")
    return sanitized, f"{snapshot.runId}:{snapshot.sequence}"


def _send(origin: str, token: str, body: bytes) -> str:
    if len(token) < 32:
        raise ValueError("AUREX_ORCA_PUSH_TOKEN must be configured (at least 32 characters)")
    req = urllib.request.Request(
        _endpoint(origin),
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(req, timeout=8) as resp:
        if resp.status != 200:
            raise ValueError("backend did not acknowledge status metadata")
        data = resp.read(1025)
        if len(data) > 1024:
            raise ValueError("oversized backend receipt")
        receipt = json.loads(data)
        if receipt.get("result") != "STORED_UNVERIFIED":
            raise ValueError("unexpected backend receipt")
        return str(receipt.get("receivedAt", "unknown"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish ORCA R8 status counters only")
    parser.add_argument("--status-file", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--once", action="store_true")
    mode.add_argument("--follow", action="store_true")
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()
    if args.follow and not 10 <= args.interval <= 300:
        parser.error("--interval must be from 10 to 300 seconds")

    previous: str | None = None
    while True:
        try:
            data, key = _read_safe_snapshot(args.status_file)
            if args.dry_run:
                print("Valid ORCA status metadata (not uploaded):", data.decode("utf-8"))
                return 0
            if previous != key:
                received = _send(
                    os.getenv("AUREX_ORCA_SYNC_URL", ""),
                    os.getenv("AUREX_ORCA_PUSH_TOKEN", ""),
                    data,
                )
                print(f"ORCA counters stored as UNVERIFIED, receipt={received}")
                previous = key
        except (ValueError, OSError, urllib.error.URLError) as exc:
            # Never print request headers, the status JSON or underlying HTTP exception body.
            print(f"Status sync refused: {type(exc).__name__}. Check source/schema, HTTPS and credentials.", file=sys.stderr)
            return 1
        if not args.follow:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
