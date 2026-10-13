# AUREX HLE-style Practice Lab V1

This is **not** Humanity's Last Exam, does not contain official HLE questions, and produces **no official HLE score**. The three bundled questions are simple synthetic smoke-test items, not a measure of expert reasoning.

## Run on Chromebook

```bash
cd ~/aurex-hle-lab
python3 workstation/hle_practice.py --dataset workstation/hle_practice_data/questions.json --responses workstation/hle_practice_data/responses.example.json
python3 -m unittest discover -s workstation/tests -p 'test_hle_practice.py' -v
```

## Data contracts

Dataset: JSON array of unique `{"id": "...", "question": "...", "answer": "..."}` objects. Responses: JSON object mapping question ID to a string response. Exact-match scoring strips surrounding whitespace and ignores case, but does not validate semantic equivalence. Missing answers count as incorrect.

Reports record input SHA-256 digests, UTC timestamp, counts, and item-level matches. They explicitly say `official_hle: false` and `independent_reference_validation: NOT_VERIFIED`.

## Limitations and next gates

- No model connector, automatic inference, official benchmark data, held-out split, or independent reference authentication.
- Example responses are supplied fixtures, **not** generated model answers.
- A high practice score cannot promote AUREX authority or establish HLE performance.
- Future dashboard integration requires a separately reviewed UI/API patch.
- Official benchmark evaluation requires authorization, appropriate dataset access, contamination safeguards, reproducible inference and scoring, and independent evidence review.
