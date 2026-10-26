"""Real loopback frontend proxy -> canonical authenticated API; no browser claim."""
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_real_sandbox_proxy_and_replay(tmp_path):
    if not (ROOT / 'website/node_modules/vite/bin/vite.js').is_file():
        pytest.skip('Run npm ci in website for local frontend sandbox test')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    with (tmp_path / 'sandbox.log').open('w') as log:
        process = subprocess.Popen([sys.executable, 'scripts/clii_sandbox.py', '--ui-port', str(port)], cwd=ROOT, stdout=log, stderr=log, start_new_session=True)
        try:
            with httpx.Client(base_url=f'http://127.0.0.1:{port}', trust_env=False, timeout=5) as client:
                deadline = time.monotonic() + 20
                while True:
                    assert process.poll() is None, (tmp_path / 'sandbox.log').read_text()
                    try:
                        if client.get('/').status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    assert time.monotonic() < deadline
                    time.sleep(.1)
                headers = {'Origin': f'http://127.0.0.1:{port}'}
                first = client.post('/__industrial', json={'fixture':'towing_v1'}, headers=headers)
                assert first.status_code == 200, first.text
                assert first.json() == client.post('/__industrial', json={'fixture':'towing_v1'}, headers=headers).json()
                oil = client.post('/__industrial', json={'fixture':'oilfield_v1'}, headers=headers)
                assert oil.status_code == 200
                assert oil.json()['now'][0]['category'] == 'crew_qualification'
                assert first.json()['proof']['status'] == 'NOT_VERIFIED'
                assert client.post('/__industrial', json={'fixture':'towing_v1'}, headers={'Origin':'https://evil.example'}).status_code == 403
                assert client.post('/__industrial', json={'fixture':'towing_v1','records':['customer']}, headers=headers).status_code == 422
        finally:
            os.killpg(process.pid, signal.SIGINT)
            process.wait(timeout=10)
