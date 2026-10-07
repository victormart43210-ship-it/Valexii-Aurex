# Evaluation Protocol

AUREX evaluates systems using paired, reproducible runs.

For any claimed governance uplift:

1. Freeze dataset/version and scoring method.
2. Freeze the base model, provider, model version, temperature, tool policy, and context budget.
3. Run a base condition.
4. Run the governed condition with only the governance layer changed.
5. Preserve raw outputs, timestamps, hashes, failures, refusals, and scoring artifacts.
6. Score blind where practical.
7. Report absolute score, percentage-point difference, and relative uplift separately.
8. Do not convert estimates into measured claims.
9. Mark incomplete or contaminated runs `HOLD`.

HLE or other licensed/restricted benchmark content must not be committed unless its license explicitly permits redistribution.
