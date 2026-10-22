"""24/7 *deterministic* on-host observer, NOT an AI model or an independent witness.

Writes bounded operational snapshots to the same SQLite file as the API and
worker. No network calls, paid inference, actions, or security authority.
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from . import store

INTERVAL_MIN = 10
INTERVAL_MAX = 300
FRESH_S = 180

def _now() -> str:
    return datetime.now(UTC).isoformat()

def ensure_schema(db: str) -> None:
    store.initialize(db)
    with store.connect(db) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS agent_cycles (
          id INTEGER PRIMARY KEY AUTOINCREMENT, observed_at TEXT NOT NULL,
          db_ok INTEGER NOT NULL, worker_fresh INTEGER NOT NULL,
          verification TEXT NOT NULL DEFAULT 'NOT_VERIFIED'
        )''')

def once(db: str | None = None) -> dict[str, object]:
    target = db or store.path_from_env()
    ensure_schema(target)
    # SQLite connection errors must be visible as failures, not silently healthy.
    with store.connect(target) as c:
        integrity = c.execute('PRAGMA quick_check(1)').fetchone()[0]
        db_ok = integrity == 'ok'
        cutoff=(datetime.now(UTC)-timedelta(seconds=store.HEARTBEAT_S)).isoformat()
        worker_fresh = c.execute('SELECT 1 FROM workers WHERE last_seen>=? LIMIT 1',(cutoff,)).fetchone() is not None
        observed_at = _now()
        c.execute('''INSERT INTO agent_cycles(observed_at,db_ok,worker_fresh,verification)
                     VALUES (?,?,?, 'NOT_VERIFIED')''', (observed_at,int(db_ok),int(worker_fresh)))
        c.execute('''DELETE FROM agent_cycles WHERE id NOT IN
                      (SELECT id FROM agent_cycles ORDER BY id DESC LIMIT 1000)''')
    return {'observedAt':observed_at,'database':'OBSERVED_OK' if db_ok else 'FAIL',
            'worker':'RECENT' if worker_fresh else 'NOT_VERIFIED',
            'authority':'NONE','independentVerification':'NOT_VERIFIED'}

def snapshot(db: str | None = None) -> dict[str,object]:
    target=db or store.path_from_env()
    # Fail closed if table doesn't exist (previous version / not running agent).
    try:
        with store.connect(target) as c:
            row=c.execute('SELECT * FROM agent_cycles ORDER BY id DESC LIMIT 1').fetchone()
            if row is None: return {'running':False,'checkedAt':None,'database':'UNKNOWN','worker':'UNKNOWN','authority':'NONE','verification':'NOT_VERIFIED'}
            t=datetime.fromisoformat(row['observed_at'])
            fresh= datetime.now(UTC)-timedelta(seconds=FRESH_S) <= t <= datetime.now(UTC)+timedelta(seconds=60)
            return {'running':fresh,'checkedAt':row['observed_at'],
                    'database':'OBSERVED_OK' if fresh and row['db_ok'] else 'UNKNOWN',
                    'worker':'RECENT' if fresh and row['worker_fresh'] else 'NOT_VERIFIED',
                    'authority':'NONE','verification':'NOT_VERIFIED'}
    except sqlite3.Error:
        return {'running':False,'checkedAt':None,'database':'UNKNOWN','worker':'UNKNOWN','authority':'NONE','verification':'NOT_VERIFIED'}

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['once','loop']);p.add_argument('--interval',type=int,default=60);a=p.parse_args()
    if not INTERVAL_MIN <= a.interval <= INTERVAL_MAX:p.error('interval must be 10..300 seconds')
    if a.mode=='once':print(json.dumps(once()));return
    while True:
        print(json.dumps(once()),flush=True)
        time.sleep(a.interval)

if __name__=='__main__':main()
