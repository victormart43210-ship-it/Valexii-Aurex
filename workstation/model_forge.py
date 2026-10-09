"""Model Forge v1: offline, dependency-free experiment and provenance helpers.

No model downloads, code execution from model cards, or training of third-party
weights happens automatically. All candidate entries require license review.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import random

@dataclass(frozen=True)
class ModelCandidate:
    name: str
    source: str
    revision: str
    license: str
    permission_reviewed: bool = False

    def eligible(self):
        return bool(self.revision and self.license and self.permission_reviewed)

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def write_manifest(candidate, weights, destination):
    if not candidate.eligible():
        raise ValueError("Specific revision, license, and affirmative permission review required")
    weights = Path(weights).resolve(strict=True)
    if not weights.is_file():
        raise ValueError("Weights path must be a file")
    manifest = {
        "schema": "aurex.model-forge.provenance.v1",
        "model": asdict(candidate),
        "weights_filename": weights.name,
        "weights_sha256": sha256(weights),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "verification": "PROVENANCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED",
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

def tiny_training_demo(steps=200, seed=42):
    """Train a character bigram frequency model on synthetic strings.

    Educational only: NOT an LLM, fine-tuning, or benchmark.
    """
    if not 1 <= steps <= 10000:
        raise ValueError("steps must be 1..10000")
    rng = random.Random(seed)
    alphabet = "abc "
    transitions = {a: {b: 1 for b in alphabet} for a in alphabet}
    examples = ("ab cab", "abc abc", "cab abc", "bac cab")
    for _ in range(steps):
        sample = rng.choice(examples)
        for a, b in zip(sample, sample[1:]):
            transitions[a][b] += 1
    return {
        "experiment": "synthetic_character_bigram_demo",
        "steps": steps,
        "seed": seed,
        "transition_counts": transitions,
        "benchmark": "NOT_RUN",
        "independent_verification": "NOT_RUN",
    }

def main():
    parser = argparse.ArgumentParser(description="AUREX Model Forge offline starter")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run tiny educational training example")
    demo.add_argument("--steps", type=int, default=200)
    demo.add_argument("--seed", type=int, default=42)
    manifest = sub.add_parser("manifest", help="Record reviewed model provenance")
    for name in ("name", "source", "revision", "license", "weights", "output"):
        manifest.add_argument("--" + name, required=True)
    manifest.add_argument("--permission-reviewed", action="store_true")
    args = parser.parse_args()
    if args.command == "demo":
        print(json.dumps(tiny_training_demo(args.steps, args.seed), indent=2))
    else:
        model = ModelCandidate(args.name, args.source, args.revision, args.license,
                               args.permission_reviewed)
        print(json.dumps(write_manifest(model, args.weights, args.output), indent=2))

if __name__ == "__main__":
    main()
