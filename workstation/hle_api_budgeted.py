#!/usr/bin/env python3
"""AUREX public HLE sample runner. NOT an official HLE submission."""
import argparse
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

MODEL = "gpt-4.1-mini"
# Deliberately conservative planning ceilings, USD per 1M tokens.
# Not a live price quote or billing hard cap.
INPUT_CEILING = 10.0
OUTPUT_CEILING = 40.0
MAX_INPUT_BYTES = 4000
MAX_OUTPUT_TOKENS = 256
MAX_QUESTIONS = 10
MAX_AUTHORIZED_USD = 10.0
RESERVE_USD = 1.0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Local JSONL of public, authorized HLE questions")
    parser.add_argument("--output", default="aurex_hle_api_results.json")
    parser.add_argument("--max-questions", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.max_questions <= MAX_QUESTIONS:
        parser.error("--max-questions must be between 1 and 10")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        parser.error("OPENAI_API_KEY is not set")
    dataset = pathlib.Path(args.dataset)
    if not dataset.is_file():
        parser.error("Dataset missing. Supply a licensed/public HLE JSONL file; this runner does not fabricate questions.")
    rows = []
    for line in dataset.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
        if len(rows) >= args.max_questions:
            break
    if not rows:
        parser.error("Dataset contains no questions")
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("question"), str) or not row["question"].strip():
            parser.error(f"Row {i+1} must contain a nonempty 'question' string")
        if len(row["question"].encode("utf-8")) > MAX_INPUT_BYTES:
            parser.error(f"Row {i+1} exceeds the input byte limit")
        if row.get("image") or row.get("image_url"):
            parser.error("Multimodal HLE items are unsupported; refusing to score incomplete questions")
    # Worst-case preflight deliberately overestimates input tokens as input bytes
    # plus 512 tokens of request overhead, at conservative price ceilings.
    per_call = ((MAX_INPUT_BYTES + 512) * INPUT_CEILING + MAX_OUTPUT_TOKENS * OUTPUT_CEILING) / 1_000_000
    if per_call * len(rows) > MAX_AUTHORIZED_USD - RESERVE_USD:
        parser.error("Conservative worst-case cost exceeds the reserved budget")
    if pathlib.Path(args.output).exists():
        parser.error("Output already exists; refusing to overwrite prior evidence")
    print(f"Model: {MODEL}; questions: {len(rows)}; conservative preflight ceiling: ${per_call * len(rows):.2f}")
    print("Not a guaranteed billing cap. Confirm available credit and project limits before running.")
    results = []
    estimated_usd = 0.0
    for i, row in enumerate(rows):
        if estimated_usd + per_call > MAX_AUTHORIZED_USD - RESERVE_USD:
            break
        body = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Answer the question as accurately and briefly as possible. If unsure, say so."},
                {"role": "user", "content": row["question"]},
            ],
            "max_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0,
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                data = json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Stopped on request {i+1}: {type(exc).__name__}; no automatic retry.", file=sys.stderr)
            break
        usage = data.get("usage", {})
        input_tokens = int(usage.get("prompt_tokens", MAX_INPUT_BYTES + 512))
        output_tokens = int(usage.get("completion_tokens", MAX_OUTPUT_TOKENS))
        estimated_usd += (input_tokens * INPUT_CEILING + output_tokens * OUTPUT_CEILING) / 1_000_000
        answer = data["choices"][0]["message"].get("content", "")
        results.append({
            "id": row.get("id", i + 1),
            "question_sha256": hashlib.sha256(row["question"].encode()).hexdigest(),
            "response": answer,
            "usage": usage,
            "estimated_cost_usd_at_ceiling": round(estimated_usd, 6),
            "grading": "NOT_VERIFIED",
        })
        print(f"Completed {i+1}/{len(rows)}; conservative accumulated estimate ${estimated_usd:.4f}")
    report = {
        "benchmark": "HLE public-sample practice; NOT official",
        "model": MODEL,
        "question_count": len(results),
        "estimated_total_usd_at_ceiling": round(estimated_usd, 6),
        "billing_cap_guaranteed": False,
        "results": results,
    }
    pathlib.Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {args.output}. Scoring NOT_VERIFIED; no official HLE claim.")

if __name__ == "__main__":
    main()
