# KUSANAGI CXXXI — Resume

Branch: `work/kusanagi-cxxxi-copilot-continuity` (base `6adc1936d09534b134182e769f88fea9c5a0125a`).
Find the latest checkpoint: `git log -1 --format=%H -- docs/operations/KUSANAGI_CXXXI_RECOVERY.json`.

## State at checkpoint 001
- Done: receipt verifier + mutation tests (authored, **NOT RUN**), partial contract matrix.
- Not done: e2e harness, staging preflight, CI workflow, draft PR, remaining contract inventory.

## Resume commands
```bash
git fetch origin && git checkout work/kusanagi-cxxxi-copilot-continuity
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_cxxxi_receipt_verify.py
ruff check scripts tests/test_cxxxi_receipt_verify.py
```
Record real outcomes in `KUSANAGI_CXXXI_RECOVERY.json`, then continue with its `next_three_actions`.

Limits: no production deploy, no merge, no customer data, no paid inference, no staging writes until Work confirms isolation.
