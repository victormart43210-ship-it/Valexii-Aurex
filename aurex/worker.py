"""Single-host durable local inference worker: python -m aurex.worker.

The subprocess deadline bounds total inference time, including trickled responses.
A worker and API must share the same local durable SQLite volume. No remote effects.
"""
import multiprocessing
import os
import signal
import time
import uuid
from multiprocessing.connection import Connection
from typing import Any

from aurex.adapters.openai_compatible import OpenAICompatibleAdapter
from aurex.database import (
    DEFAULT_DB_PATH,
    claim_job,
    fail_job,
    finish_job,
    heartbeat_job,
    register_worker,
)


def _infer(connection: Connection, base_url: str, model: str, prompt: str) -> None:
    try:
        answer = OpenAICompatibleAdapter(
            base_url=base_url, model=model, local_loopback=True,
            provider='native-local', timeout_seconds=60,
        ).answer(prompt)
        result = answer.model_dump()
        result['modelIdentity'] = 'DECLARED'
        # Pipe is polled and drained by the parent, never waiting on a full queue join.
        if len(answer.text.encode()) > 48_000:
            raise ValueError('Bounded model response')
        connection.send({'result': result})
    except TimeoutError:
        connection.send({'error': 'MODEL_TIMEOUT'})
    except (ValueError, TypeError, KeyError):
        connection.send({'error': 'MODEL_INVALID_RESPONSE'})
    except Exception:
        connection.send({'error': 'MODEL_UNAVAILABLE'})
    finally:
        connection.close()


def execute_claim(db_path: str, worker_id: str, job: dict[str, Any], base_url: str, model: str) -> bool:
    """Bounded subprocess, lease heartbeats and fenced finalization; no network tools."""
    context = multiprocessing.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    child = context.Process(target=_infer, args=(sender, base_url, model, job['params'].get('prompt', '')))
    child.start()
    sender.close()
    end = time.monotonic() + min(120, max(0, (job['deadline'] or time.time() + 120) - time.time()))
    next_heartbeat = 0.0
    try:
        while time.monotonic() < end:
            if time.monotonic() >= next_heartbeat:
                register_worker(db_path, worker_id)
                if not heartbeat_job(db_path, job['id'], worker_id, job['fence']):
                    return False
                next_heartbeat = time.monotonic() + 5
            if receiver.poll(0.2):
                try:
                    payload = receiver.recv()
                except EOFError:
                    return fail_job(db_path, job['id'], worker_id, job['fence'], 'WORKER_FAILURE')
                if 'result' in payload:
                    try:
                        return finish_job(db_path, job['id'], worker_id, job['fence'], payload['result'])
                    except (ValueError, TypeError):
                        return fail_job(db_path, job['id'], worker_id, job['fence'], 'MODEL_INVALID_RESPONSE')
                return fail_job(db_path, job['id'], worker_id, job['fence'], payload['error'])
            if not child.is_alive():
                return fail_job(db_path, job['id'], worker_id, job['fence'], 'WORKER_FAILURE')
        return fail_job(db_path, job['id'], worker_id, job['fence'], 'MODEL_TIMEOUT')
    finally:
        receiver.close()
        if child.is_alive():
            child.terminate()
        child.join(timeout=2)
        if child.is_alive():
            child.kill()
            child.join(timeout=2)


def main() -> None:
    model = os.environ.get('AUREX_LOCAL_MODEL', '')
    url = os.environ.get('AUREX_LOCAL_MODEL_URL', 'http://127.0.0.1:8080/v1')
    # Validate configuration before accepting any work. No paid/provider fallback.
    OpenAICompatibleAdapter(base_url=url, model=model, local_loopback=True)
    db_path = os.environ.get('AUREX_DB_PATH', DEFAULT_DB_PATH)
    worker_id = str(uuid.uuid4())
    stopping = False

    def stop(_signum: int, _frame: Any) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    while not stopping:
        register_worker(db_path, worker_id)
        job = claim_job(db_path, worker_id)
        if job:
            execute_claim(db_path, worker_id, job, url, model)
        else:
            time.sleep(1)


if __name__ == '__main__':
    main()
