"""Opt-in CLI for local APK SHA -> MobSF report -> fail-closed AUREX witness.

Usage:
    python -m aurex.adapters.oss_cli --apk candidate.apk --mobsf-report report.json
    python -m aurex.adapters.oss_cli --moon-utc 2026-10-07T00:00:00Z

No network transfers, API tokens, model downloads or security authority decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from aurex.adapters.oss_witnesses import astronomy_moon_witness, mobsf_json_witness

MAX_REPORT_BYTES = 16 * 1024 * 1024


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX optional OSS evidence witnesses")
    parser.add_argument("--apk", type=Path, help="Local APK path for independent SHA-256")
    parser.add_argument("--mobsf-report", type=Path, help="Locally exported MobSF JSON report")
    parser.add_argument("--moon-utc", help="Explicit UTC ISO timestamp to compute moon phase")
    args = parser.parse_args(argv)
    if not args.moon_utc and not (args.apk and args.mobsf_report):
        parser.error("Use --moon-utc or both --apk and --mobsf-report")
    result = []
    try:
        if args.apk or args.mobsf_report:
            if not args.apk or not args.mobsf_report:
                parser.error("--apk and --mobsf-report must be supplied together")
            if args.mobsf_report.stat().st_size > MAX_REPORT_BYTES:
                raise ValueError("MobSF JSON report exceeds 16 MiB limit")
            with args.mobsf_report.open("r", encoding="utf-8") as source:
                report = json.load(source)
            if not isinstance(report, dict):
                raise ValueError("MobSF JSON report must be an object")
            result.append(mobsf_json_witness(report, file_sha256(args.apk)).json_ready())
        if args.moon_utc:
            result.append(astronomy_moon_witness(args.moon_utc).json_ready())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "HOLD", "error_class": type(exc).__name__}),
              file=sys.stderr)
        return 2
    print(json.dumps({"witnesses": result}, indent=2, sort_keys=True))
    return 0 if all(w["status"] == "INSUFFICIENT" for w in result) else 3


if __name__ == "__main__":
    sys.exit(main())
