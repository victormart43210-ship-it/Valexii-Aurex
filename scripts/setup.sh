#!/usr/bin/env bash
set -euo pipefail

echo "=== AUREX Environment Setup ==="
python3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
echo "[OK] Python version 3.12+ verified"

echo "Installing dependencies in editable mode..."
python3 -m pip install -e ".[dev]"
echo "[OK] Dependencies installed"

if [ ! -f .env.example ]; then
    cat << 'EOF' > .env.example
AUREX_SERVICE_TOKEN=aurex_service_token_example_32chars_long_123456789
AUREX_ADMIN_TOKEN=aurex_service_token_example_32chars_long_123456789
AUREX_DB_PATH=/tmp/aurex_jobs.db
EOF
    echo "[OK] Created .env.example"
fi

echo "=== Setup Completed Successfully ==="
