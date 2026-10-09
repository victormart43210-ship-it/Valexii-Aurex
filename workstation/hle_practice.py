"""Offline HLE-style practice harness. NOT an official HLE evaluation."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

def evaluate(dataset, responses):
    """Exact-match practice scoring; never implies independently verified answers."""
    questions = json.loads(Path(dataset).read_text(encoding="utf-8"))
    answers = json.loads(Path(responses).read_text(encoding="utf-8"))
    if not isinstance(questions, list) or not questions:
        raise ValueError("Dataset must be a nonempty JSON array")
    if not isinstance(answers, dict):
        raise ValueError("Responses must be a JSON object keyed by question ID")
    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate question IDs")
    results = []
    for q in questions:
        expected = q["answer"]
        actual = answers.get(q["id"])
        correct = isinstance(actual, str) and actual.strip().casefold() == expected.strip().casefold()
        results.append({"id": q["id"], "answered": isinstance(actual, str), "exact_match": correct})
    matched = sum(r["exact_match"] for r in results)
    return {
        "kind": "LOCAL_PRACTICE_ONLY",
        "official_hle": False,
        "independent_reference_validation": "NOT_VERIFIED",
        "questions": len(results),
        "answered": sum(r["answered"] for r in results),
        "exact_matches": matched,
        "exact_match_rate": matched / len(results),
        "results": results,
        "dataset_sha256": hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),
        "responses_sha256": hashlib.sha256(Path(responses).read_bytes()).hexdigest(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

def main():
    p = argparse.ArgumentParser(description="Local HLE-style practice scorer (not official HLE)")
    p.add_argument("--dataset", required=True)
    p.add_argument("--responses", required=True)
    p.add_argument("--output", help="Optional report JSON path")
    a = p.parse_args()
    report = evaluate(a.dataset, a.responses)
    rendered = json.dumps(report, indent=2)
    if a.output:
        Path(a.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

if __name__ == "__main__":
    main()
