"""Single-panel APIS PRIME offline research CLI; not an HTTP or model service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aurex.apis_prime_spine import unified_research
from workstation.huruf_llull_cli import read_local_text


def research_file(path: Path, *, details: bool = False) -> dict[str, Any]:
    """Run one governed research request; no user text is echoed by default."""
    text = read_local_text(path)
    result = unified_research(text, kind="python" if path.suffix.lower() == ".py" else "document")
    if details:
        return result
    return {
        "spine_status": result["spine_status"],
        "authority": result["authority"],
        "independent_verification": result["independent_verification"],
        "one_view": result["one_view"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX APIS PRIME — one reasoning spine / one view")
    parser.add_argument("--file", required=True, type=Path, help="existing UTF-8 text, no PDF or images")
    parser.add_argument("--details", action="store_true", help="include all 14 technical evidence receipts")
    args = parser.parse_args(argv)
    try:
        result = research_file(args.file, details=args.details)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    # Research diagnostics can succeed while promotion and authority remain HOLD.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
