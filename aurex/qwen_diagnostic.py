"""Diagnostic utility for local Qwen model workstation setup and RAM availability."""

import json
import os
import socket
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Any

from aurex.adapters.qwen import select_optimal_qwen_model


def check_port(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def probe_model_serving(port: int, path: str = "/v1/models") -> bool:
    if not check_port(port):
        return False
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AUREX-Diagnostic/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=0.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return isinstance(data, (dict, list))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        pass
    return False


def generate_qwen_workstation_report() -> dict[str, Any]:
    # Read-only memory estimation
    try:
        mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        total_ram_mb = int(mem_bytes / (1024 * 1024))
    except Exception:
        total_ram_mb = 4096  # Conservative fallback estimate

    optimal_spec = select_optimal_qwen_model(total_ram_mb)

    llama_cpp_port = check_port(8080)
    ollama_port = check_port(11434)

    llama_cpp_serving = probe_model_serving(8080, "/v1/models")
    ollama_serving = probe_model_serving(11434, "/api/tags")

    serving_verified = llama_cpp_serving or ollama_serving
    port_open = llama_cpp_port or ollama_port

    if serving_verified:
        status_code = "READY"
    elif port_open:
        status_code = "PORT_OPEN_UNVERIFIED"
    else:
        status_code = "INACTIVE"

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_ram_mb": total_ram_mb,
        "recommended_model": optimal_spec.name,
        "recommended_quantization": optimal_spec.quantization,
        "estimated_ram_mb": optimal_spec.estimated_ram_mb,
        "llama_cpp_port_8080_active": llama_cpp_port,
        "ollama_port_11434_active": ollama_port,
        "model_serving_verified": serving_verified,
        "status": status_code,
    }


def main() -> None:
    report = generate_qwen_workstation_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
