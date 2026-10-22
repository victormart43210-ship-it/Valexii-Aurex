"""Fail-closed single-volume process supervisor for Railway.

Runs API always, optional offline probe worker + operational observer in same
container on the SAME /data mount. If any child exits, stop all so Railway's
restart policy can restart the service. Explicit flags gate optional loops.
"""
from __future__ import annotations
import os
import signal
import subprocess
import sys
import time

children:list[subprocess.Popen]=[]
stopping=False

def stop(*_args):
    global stopping
    stopping=True
    for child in children:
        if child.poll() is None: child.terminate()

def main() -> int:
    db=os.environ.get('AUREX_DB_PATH','')
    if not db or not os.path.isabs(db) or db==':memory:':
        print('FATAL: set absolute AUREX_DB_PATH on durable storage',file=sys.stderr)
        return 2
    if os.environ.get('AUREX_REQUIRED_VOLUME')=='true' and not (db.startswith('/data/') and os.path.ismount('/data')):
        print('FATAL: production durable /data mount not detected; refusing start',file=sys.stderr)
        return 2
    from . import store
    store.initialize(db)
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    env=os.environ.copy()
    if env.get('AUREX_ENABLE_OFFLINE_LAB')=='true':
        children.append(subprocess.Popen([sys.executable,'-m','backend.worker','loop','--interval','10'],env=env))
    if env.get('AUREX_OBSERVER_ENABLED')=='true':
        children.append(subprocess.Popen([sys.executable,'-m','backend.agent','loop','--interval','60'],env=env))
    children.append(subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app','--host','0.0.0.0','--port',env.get('PORT','8080'),'--no-access-log'],env=env))
    try:
        while not stopping:
            for child in children:
                rc=child.poll()
                if rc is not None:
                    print(f'FATAL: AUREX child exited (code={rc}); stopping service',file=sys.stderr)
                    stop();return 1
            time.sleep(2)
        return 0
    finally:
        stop()
        for child in children:
            try:child.wait(timeout=8)
            except subprocess.TimeoutExpired:child.kill();child.wait()

if __name__=='__main__':raise SystemExit(main())
