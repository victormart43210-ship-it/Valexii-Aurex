"""Local-only, non-deploying XXVI verification runner."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
checks = [
    ('existing_regressions', [sys.executable, '-m', 'pytest', 'tests/', 'integrations/kusanagi-xvi/tests/', '-q']),
    ('xxvi_security', [sys.executable, '-m', 'pytest', 'xxvi_verification/tests/test_xxvi_bridge.py', '-q']),
    ('ruff', [sys.executable, '-m', 'ruff', 'check', 'aurex_workflows/read_model.py', 'xxv_website_bridge/backend.py', 'xxvi_verification/tests/test_xxvi_bridge.py']),
    ('whitespace', ['git', 'diff', '--check']),
]
results = {}
for label, command in checks:
    print(f'\n=== {label} ===', flush=True)
    proc = subprocess.run(command, cwd=root, check=False)
    results[label] = 'PASS' if proc.returncode == 0 else 'FAIL'
print('\n' + json.dumps({'checks': results, 'production_deployed': False, 'remote_branches_reconciled': 'NOT VERIFIED'}, indent=2))
sys.exit(0 if all(x == 'PASS' for x in results.values()) else 1)
