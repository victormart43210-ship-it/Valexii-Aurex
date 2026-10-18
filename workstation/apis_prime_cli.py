"""Single-panel APIS PRIME offline research CLI; not an HTTP or model service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aurex.apis_prime_spine import unified_research
from workstation.huruf_llull_cli import read_local_text


def research_file(
    path: Path, *, details: bool = False,
    approve_local_model: bool = False, model: str | None = None,
    backend: str = "ollama", port: int | None = None,
) -> dict[str, Any]:
    """Run one governed request; local Qwen is opt-in and receives only stats."""
    if model is not None and not approve_local_model:
        raise ValueError("model selection requires --approve-local-model")
    text = read_local_text(path)
    resolved_port = port if port is not None else (11434 if backend == "ollama" else 8080)
    result = unified_research(
        text, kind="python" if path.suffix.lower() == ".py" else "document",
        local_model_approved=approve_local_model, local_model=model,
        local_backend=backend, local_port=resolved_port,
    )
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
    parser.add_argument("--approve-local-model", action="store_true", help="permit one local loopback inference")
    parser.add_argument("--model", help="exact already installed model identifier")
    parser.add_argument("--backend", choices=("ollama", "llama.cpp"), default="ollama")
    parser.add_argument("--port", type=int, help="numeric local model port")
    args = parser.parse_args(argv)
    try:
        result = research_file(
            args.file, details=args.details,
            approve_local_model=args.approve_local_model,
            model=args.model, backend=args.backend, port=args.port,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    # Research diagnostics can succeed while promotion and authority remain HOLD.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
