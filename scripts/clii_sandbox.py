"""Launch canonical API and shared frontend on loopback with fresh synthetic secrets."""
from __future__ import annotations

import argparse
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ui-port', type=int, default=4173)
    args = parser.parse_args()
    if not 1024 <= args.ui_port <= 65535:
        parser.error('Use an unprivileged local port')
    root = Path(__file__).resolve().parents[1]
    node = shutil.which('node')
    if not node or not (root / 'website/node_modules/vite/bin/vite.js').is_file():
        parser.error('Install website dependencies with npm ci first')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        api_port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix='aurex-clii-') as scratch:
        token = secrets.token_urlsafe(40)
        # Explicit allowlist: no production credentials, database paths, proxy or model keys inherited.
        env = {'PATH': os.environ.get('PATH', ''), 'HOME': scratch,
               'PYTHONPATH': str(root), 'AUREX_SERVICE_TOKEN': token,
               'AUREX_ENABLE_INDUSTRIAL_DEMO': '1', 'AUREX_DEPLOYMENT_SCOPE': 'sandbox',
               'AUREX_DB_PATH': str(Path(scratch) / 'synthetic.sqlite3'),
               'AUREX_LLM_ENABLED': 'false', 'AUREX_LLM_ALLOW_BILLING': 'false',
               'AUREX_SANDBOX_TOKEN': token, 'AUREX_SANDBOX_API_PORT': str(api_port),
               'AUREX_SANDBOX_UI_PORT': str(args.ui_port)}
        processes = []
        try:
            processes.append(subprocess.Popen([sys.executable, '-m', 'uvicorn', 'aurex.api:app',
                '--host', '127.0.0.1', '--port', str(api_port), '--no-access-log'], cwd=root, env=env))
            processes.append(subprocess.Popen([node, 'node_modules/vite/bin/vite.js', '--config',
                'sandbox-industrial/vite.config.ts'], cwd=root / 'website', env=env))
            print(f'LOCAL SANDBOX http://127.0.0.1:{args.ui_port} — stateless; production HOLD', flush=True)
            while all(p.poll() is None for p in processes):
                try:
                    processes[0].wait(timeout=1)
                except subprocess.TimeoutExpired:
                    continue
        except KeyboardInterrupt:
            pass
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            for process in processes:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
