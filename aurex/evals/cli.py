"""Two-process original-evaluation CLI: generate without references, then score."""

import argparse
import base64
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from aurex.adapters.base import GenerationSettings, ModelAdapter
from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.adapters.llama_cpp import LlamaCppAdapter
from aurex.adapters.ollama import OllamaAdapter
from aurex.adapters.openai_compatible import OpenAICompatibleAdapter
from aurex.evals.four_arm import PromptItem, run_four_arms, score_run
from aurex.evals.governance import Witness


def build_client(config: dict[str, Any]) -> InferenceClient:
    spec = ModelSpec.model_validate(config["identity"])
    settings = GenerationSettings.model_validate(config.get("generation", {}))
    kwargs = {"model": spec.model, "base_url": config["base_url"], "generation": settings}
    adapter: ModelAdapter
    if spec.provider == "llama.cpp":
        adapter = LlamaCppAdapter(**kwargs)
    elif spec.provider == "ollama":
        adapter = OllamaAdapter(**kwargs)
    elif spec.provider == "openai-compatible":
        adapter = OpenAICompatibleAdapter(**kwargs)
    else:
        raise ValueError("Provider requires an explicit tested adapter")
    return InferenceClient(adapter, spec)


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate")
    for name in ("config", "prompts", "witnesses", "trust-store", "output"):
        g.add_argument("--" + name, required=True, type=Path)
    g.add_argument("--execute", action="store_true")
    s = sub.add_parser("score")
    for name in ("predictions", "references", "output"):
        s.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    if not a.output.parent.is_dir():
        raise ValueError("Output parent directory must exist")
    if a.output.exists():
        raise ValueError("Use a new output file")
    if a.command == "generate":
        config = json.loads(a.config.read_text())
        items = [
            PromptItem.model_validate_json(line)
            for line in a.prompts.read_text().splitlines()
            if line.strip()
        ]
        if not a.execute:
            print(
                json.dumps(
                    {"status": "NOT RUN", "items": len(items), "reason": "--execute required"}
                )
            )
            return
        base = build_client(config["base"])
        tuned = build_client(config["tuned"]) if config.get("tuned") else None
        witnesses = {
            k: tuple(Witness.model_validate(w) for w in v)
            for k, v in json.loads(a.witnesses.read_text()).items()
        }
        keys = {
            k: Ed25519PublicKey.from_public_bytes(base64.b64decode(v, validate=True))
            for k, v in json.loads(a.trust_store.read_text()).items()
        }
        result = run_four_arms(items, base, tuned, witnesses, keys, datetime.now(UTC))
    else:
        result = score_run(
            json.loads(a.predictions.read_text()), json.loads(a.references.read_text())
        )
    with a.output.open("x") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({"status": result.get("status", "RECORDED"), "output": str(a.output)}))


if __name__ == "__main__":
    main()
