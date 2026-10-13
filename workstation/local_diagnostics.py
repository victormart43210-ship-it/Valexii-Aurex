"""Diagnose a local llama.cpp server without exposing credentials."""
import json
import os
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

def diagnose():
    home = Path.home()
    binary = home / "llama.cpp/build/bin/llama-server"
    model_dir = home / "aurex-models"
    models = [{"name": p.name, "bytes": p.stat().st_size} for p in sorted(model_dir.glob("*.gguf")) if p.is_file()] if model_dir.exists() else []
    result = {"server_binary_present": binary.is_file(), "models": models,
              "endpoint": "http://127.0.0.1:8080/v1/models", "server": "NOT_VERIFIED"}
    try:
        with urlopen(result["endpoint"], timeout=3) as r:
            data = json.loads(r.read(200000))
            result["server"] = "RESPONDING" if isinstance(data.get("data"), list) else "UNEXPECTED_RESPONSE"
            result["loaded_model_count"] = len(data.get("data", []))
    except (OSError, ValueError, HTTPError, URLError) as exc:
        result["server"] = "UNAVAILABLE"
        result["error_type"] = type(exc).__name__
    if not result["server_binary_present"]:
        result["next_step"] = "Build llama.cpp llama-server before starting a model."
    elif not models:
        result["next_step"] = "Download a compatible GGUF model into ~/aurex-models."
    elif result["server"] != "RESPONDING":
        result["next_step"] = "Start llama-server with an existing model file; keep it running."
    else:
        result["next_step"] = "Configure AUREX_MODEL_ENDPOINT and AUREX_MODEL_NAME; restart workstation."
    return result

if __name__ == "__main__":
    print(json.dumps(diagnose(), indent=2))
