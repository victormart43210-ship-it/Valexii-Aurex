"""Offline, synthetic-only AUREX audit-packet demonstration and local replay."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from aurex.audit_pilot import _json, _read, run_packet, verify_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX — synthetic audit evidence replay; $0; HOLD")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="write report to a new file (refuses overwrite)")
    parser.add_argument("--verify", type=Path, help="replay this existing report against original documents")
    args = parser.parse_args(argv)
    if args.out and args.verify:
        parser.error("--out and --verify are mutually exclusive")
    try:
        if args.verify:
            data = _json(_read(args.verify, 131_072))
            if not verify_report(args.packet, data):
                print(json.dumps({"status": "HOLD_REPORT_MISMATCH", "authority": "NONE"}))
                return 2
            print(json.dumps({"status": "LOCAL_REPLAY_MATCH_NOT_INDEPENDENT_WITNESS", "report_sha256": data["report_sha256"], "authority": "NONE"}))
            return 0
        report = run_packet(args.packet)
        encoded = json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            if args.out.parent.resolve() == args.packet.resolve():
                raise ValueError("report must not be written inside the input packet")
            descriptor = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(encoded)
            print(json.dumps({"status": "REPORT_WRITTEN_REVIEW_ONLY", "report_sha256": report["report_sha256"], "authority": "NONE"}))
        else:
            print(encoded)
        return 0
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
