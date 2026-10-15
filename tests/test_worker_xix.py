"""Real SQLite failure-injection checks; no model output is a verified fact."""
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from aurex.database import (
    claim_job,
    create_job,
    fail_job,
    finish_job,
    get_job,
    heartbeat_job,
    job_evidence,
    update_job_state,
)


def test_concurrent_claim(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {'prompt': 'hello'})
    barrier = Barrier(8)
    def acquire(i):
        barrier.wait()
        return claim_job(db, str(i))
    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(pool.map(acquire, range(8)))
    assert sum(c is not None for c in claims) == 1


def test_fencing_recovery_and_evidence(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {'prompt': 'hello'}, owner_id='alice')
    a = claim_job(db, 'a')
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE jobs SET lease_until = ?', (time.time() - 1,))
    b = claim_job(db, 'b')
    assert b['fence'] > a['fence']
    assert not heartbeat_job(db, 'j', 'a', a['fence'])
    assert not finish_job(db, 'j', 'a', a['fence'], {'text': 'stale'})
    assert finish_job(db, 'j', 'b', b['fence'], {'text': 'answer', 'model': 'fixture'})
    assert job_evidence(db, 'j') == []
    evidence = job_evidence(db, 'j', owner_id='alice')
    assert evidence[0]['integrity'] == 'PASS'
    assert evidence[0]['verification'] == 'NOT VERIFIED'
    assert evidence[0]['authorityGranted'] is False
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE jobs SET result_json = ?', (json.dumps({'text': 'tampered'}),))
    assert job_evidence(db, 'j', owner_id='alice')[0]['integrity'] == 'FAIL'


def test_cancellation_and_retry_exhaustion(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {}, max_attempts=1)
    a = claim_job(db, 'a')
    assert fail_job(db, 'j', 'a', a['fence'], 'MODEL_UNAVAILABLE')
    assert get_job(db, 'j')['state'] == 'failed'
    assert claim_job(db, 'b') is None
    create_job(db, 'k', 'local_inference', {})
    b = claim_job(db, 'b')
    update_job_state(db, 'k', 'cancelled')
    assert not finish_job(db, 'k', 'b', b['fence'], {'text': 'late'})
    assert job_evidence(db, 'k') == []


def test_atomic_result_rollback_and_deadline(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {})
    a = claim_job(db, 'a')
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TRIGGER reject_evidence BEFORE INSERT ON evidence_records BEGIN SELECT RAISE(ABORT, 'test'); END")
    try:
        finish_job(db, 'j', 'a', a['fence'], {'text': 'answer'})
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError('Expected database injection')
    assert get_job(db, 'j')['state'] == 'running'
    assert 'result' not in get_job(db, 'j')
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE jobs SET deadline = ?', (time.time() - 1,))
    assert not finish_job(db, 'j', 'a', a['fence'], {'text': 'late'})
    assert claim_job(db, 'b') is None
    assert get_job(db, 'j')['state'] == 'expired'


def test_legacy_kinds_are_never_executed(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'regression', {})
    assert claim_job(db, 'a') is None


def test_crash_retry_exhaustion_and_restart(tmp_path):
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {}, max_attempts=2)
    first = claim_job(db, 'a')
    assert fail_job(db, 'j', 'a', first['fence'], 'MODEL_UNAVAILABLE')
    second = claim_job(db, 'b')
    assert second['attempts'] == 2
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE jobs SET lease_until = ?', (time.time() - 1,))
    assert claim_job(db, 'restart') is None
    assert get_job(db, 'j')['state'] == 'failed'
    assert get_job(db, 'j')['error_code'] == 'RETRY_EXHAUSTED'


def test_unfenced_completion_rejected_and_heartbeat(tmp_path):
    import pytest

    from aurex.database import register_worker, worker_status
    db = str(tmp_path / 'jobs.db')
    create_job(db, 'j', 'local_inference', {})
    lease = claim_job(db, 'a')
    assert heartbeat_job(db, 'j', 'a', lease['fence'])
    with pytest.raises(ValueError, match='fenced'):
        update_job_state(db, 'j', 'succeeded', {'text': 'unfenced'})
    assert worker_status(db)['active'] is False
    register_worker(db, 'a')
    assert worker_status(db) == {'active': True, 'activeWorkers': 1, 'modelConfigured': True}
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE workers SET heartbeat = ?', (time.time() - 16,))
    assert worker_status(db)['active'] is False


def test_worker_subprocess_transport_fixture(tmp_path):
    """Actual HTTP + spawned worker + SQLite; synthetic provider, not native Qwen."""
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from threading import Thread

    from aurex.worker import execute_claim

    class Fixture(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            assert payload['model'] == 'synthetic-fixture'
            body = json.dumps({'model': 'synthetic-fixture', 'choices': [{'message': {'content': 'SYNTHETIC TEST RESPONSE'}}]}).encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        db = str(tmp_path / 'jobs.db')
        create_job(db, 'j', 'local_inference', {'prompt': 'test'})
        job = claim_job(db, 'fixture-worker')
        assert execute_claim(db, 'fixture-worker', job, f'http://127.0.0.1:{server.server_port}/v1', 'synthetic-fixture')
        stored = get_job(db, 'j')
        assert stored['state'] == 'succeeded'
        assert stored['result']['text'] == 'SYNTHETIC TEST RESPONSE'
        assert stored['result']['modelIdentity'] == 'DECLARED'
        assert job_evidence(db, 'j')[0]['integrity'] == 'PASS'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_unicode_result_does_not_exceed_utf8_budget(tmp_path):
    db=str(tmp_path/'unicode.db')
    create_job(db,'unicode','local_inference',{'prompt':'test'})
    claim=claim_job(db,'worker')
    text='界'*15000
    assert finish_job(db,'unicode','worker',claim['fence'],{'text':text,'model':'fixture','provider':'fixture'})
    assert get_job(db,'unicode')['result']['text']==text
    assert job_evidence(db,'unicode')[0]['integrity']=='PASS'
