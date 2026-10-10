"""AUREX V4: bounded, append-only local observations. Not a trust authority."""
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def append_observation(question, result, path=None):
    if not isinstance(question, str) or not isinstance(result, dict):
        raise ValueError("Invalid observation")
    target = Path(path or os.environ.get("AUREX_LEDGER_PATH", str(Path.home() / "aurex-evidence-ledger.jsonl"))).expanduser()
    if target.is_symlink():
        raise ValueError("Ledger must not be a symlink")
    target.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "schema": "aurex.observation.v1",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "question_sha256": digest(question),
        "answer_sha256": digest(result.get("answer", "")),
        "model": str(result.get("model", "UNKNOWN"))[:500],
        "generation_status": str(result.get("status", "ERROR")),
        "qualification": "INSUFFICIENT",
        "reality": "NOT_VERIFIED",
        "authority": "HOLD",
        "effect": "NONE",
        "independent_validation": "NOT_VERIFIED",
        "official_hle": False
    }
    # Atomic append per process; local journal is not tamper-evident or independently attested.
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "a", encoding="utf-8") as out:
            out.write(json.dumps(entry, sort_keys=True) + "\n")
            out.flush()
            os.fsync(out.fileno())
    except Exception:
        raise
    return entry

def score_reference(answer, expected, reference_origin):
    """Exact-match comparison only; caller must separately authenticate reference."""
    if not isinstance(answer, str) or not isinstance(expected, str):
        raise ValueError("Expected text inputs")
    matched = answer.strip().casefold() == expected.strip().casefold()
    return {
        "exact_match": matched,
        "reference_origin": reference_origin,
        "qualification": "INSUFFICIENT",
        "independent_reference_validation": "NOT_VERIFIED",
        "authority": "HOLD",
        "effect": "NONE"
    }
