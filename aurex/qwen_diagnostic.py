"""Diagnostic utility for local Qwen model workstation setup and RAM availability."""

import json
import os
import socket
from datetime import UTC, datetime
from typing import Any

from aurex.adapters.qwen import select_optimal_qwen_model


def check_port(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def generate_qwen_workstation_report() -> dict[str, Any]:
    # Read-only memory estimation
    try:
        mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        total_ram_mb = int(mem_bytes / (1024 * 1024))
    except Exception:
        total_ram_mb = 4096  # Conservative fallback estimate

    optimal_spec = select_optimal_qwen_model(total_ram_mb)

    llama_cpp_active = check_port(8080)
    ollama_active = check_port(11434)

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_ram_mb": total_ram_mb,
        "recommended_model": optimal_spec.name,
        "recommended_quantization": optimal_spec.quantization,
        "estimated_ram_mb": optimal_spec.estimated_ram_mb,
        "llama_cpp_port_8080_active": llama_cpp_active,
        "ollama_port_11434_active": ollama_active,
        "status": "READY" if (llama_cpp_active or ollama_active) else "INACTIVE",
    }


def main() -> None:
    report = generate_qwen_workstation_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
