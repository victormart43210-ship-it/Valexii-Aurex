"""AUREX XIX: bounded, auditable, local-first workflow engine.

No arbitrary shell, network probing, model training, or autonomous deployment.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import hashlib, json, os, sqlite3, time, uuid

ALLOWED_KINDS = frozenset({'llm_eval', 'dataset_validate', 'cyber_defense_review', 'brain_trust_review', 'xaeli_eval', 'training_plan'})
MAX_INPUT_BYTES = 32_768

@dataclass(frozen=True)
class JobRequest:
    kind: str
    payload: dict[str, Any]
    approved: bool = False
    budget_usd: float = 0.0

class WorkflowEngine:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with self._db() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, kind TEXT NOT NULL,
                state TEXT NOT NULL, payload_json TEXT NOT NULL, result_json TEXT,
                created_at REAL NOT NULL, updated_at REAL NOT NULL)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL, action TEXT NOT NULL, data_json TEXT NOT NULL, at REAL NOT NULL)''')

    def _db(self):
        return sqlite3.connect(self.db_path)

    def submit(self, request: JobRequest) -> str:
        if request.kind not in ALLOWED_KINDS:
            raise ValueError('unsupported workflow')
        if request.budget_usd != 0:
            raise ValueError('spending disabled: budget must be $0.00')
        raw = json.dumps(request.payload, sort_keys=True, allow_nan=False)
        if len(raw.encode()) > MAX_INPUT_BYTES:
            raise ValueError('payload too large')
        job_id = str(uuid.uuid4())
        now = time.time()
        with self._db() as conn:
            conn.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?)',
                         (job_id, request.kind, 'PENDING_APPROVAL', raw, None, now, now))
            self._event(conn, job_id, 'SUBMITTED', {'approved_on_submit_ignored': request.approved})
        return job_id

    @staticmethod
    def _event(conn, job_id, action, data):
        conn.execute('INSERT INTO events (job_id,action,data_json,at) VALUES (?,?,?,?)',
                     (job_id, action, json.dumps(data, sort_keys=True), time.time()))

    def approve(self, job_id: str, *, human_approval: bool):
        if not human_approval:
            raise PermissionError('explicit human approval required')
        with self._db() as conn:
            changed = conn.execute("UPDATE jobs SET state='APPROVED',updated_at=? WHERE id=? AND state='PENDING_APPROVAL'",
                                   (time.time(), job_id)).rowcount
            if changed != 1:
                raise ValueError('job not pending approval')
            self._event(conn, job_id, 'HUMAN_APPROVED', {})

    def execute(self, job_id: str) -> dict[str, Any]:
        # Claim the job atomically before invoking any external model.
        with self._db() as conn:
            changed = conn.execute(
                "UPDATE jobs SET state='RUNNING',updated_at=? WHERE id=? AND state='APPROVED'",
                (time.time(), job_id),
            ).rowcount
            if changed != 1:
                raise PermissionError('job not approved or already claimed')
            row = conn.execute(
                'SELECT kind,payload_json FROM jobs WHERE id=?', (job_id,)
            ).fetchone()
            kind, raw = row
            self._event(conn, job_id, 'STARTED', {})

        # No SQLite write transaction remains open during inference.
        try:
            payload = json.loads(raw)
            if kind == 'llm_eval':
                from aurex_workflows.local_executor import execute_local_model
                result = execute_local_model(payload=payload, approved=True)
            else:
                result = self._local_evaluation(kind, payload)
        except Exception as exc:
            with self._db() as conn:
                changed = conn.execute(
                    "UPDATE jobs SET state='FAILED',updated_at=? WHERE id=? AND state='RUNNING'",
                    (time.time(), job_id),
                ).rowcount
                if changed != 1:
                    raise RuntimeError('failed job state transition') from exc
                self._event(conn, job_id, 'FAILED', {'error_type': type(exc).__name__})
            raise

        serialized = json.dumps(result, sort_keys=True, allow_nan=False)
        digest = hashlib.sha256(serialized.encode()).hexdigest()
        with self._db() as conn:
            changed = conn.execute(
                "UPDATE jobs SET state='COMPLETED',result_json=?,updated_at=? WHERE id=? AND state='RUNNING'",
                (serialized, time.time(), job_id),
            ).rowcount
            if changed != 1:
                raise RuntimeError('completed job state transition failed')
            self._event(conn, job_id, 'COMPLETED', {'result_sha256': digest})
        return result

    @staticmethod
    def _local_evaluation(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        # This is an offline validation/plan-only executor, not an LLM or security scanner.
        if kind == 'dataset_validate':
            examples = payload.get('examples', [])
            if not isinstance(examples, list) or len(examples) > 100:
                raise ValueError('examples must be a list of at most 100 items')
            valid = sum(isinstance(x, dict) and isinstance(x.get('input'), str) and isinstance(x.get('expected'), str) for x in examples)
            return {'status': 'LOCAL_VALIDATION_ONLY', 'total': len(examples), 'valid': valid, 'invalid': len(examples)-valid}
        return {'status': 'PLAN_ONLY_NOT_EXECUTED', 'kind': kind,
                'next_gate': 'Connect an explicitly approved local adapter and independent evaluator',
                'external_actions': 0, 'model_calls': 0, 'spend_usd': 0.0}

    def inspect(self, job_id: str) -> dict[str, Any]:
        with self._db() as conn:
            row = conn.execute('SELECT id,kind,state,result_json FROM jobs WHERE id=?', (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            return {'id': row[0], 'kind': row[1], 'state': row[2], 'result': json.loads(row[3]) if row[3] else None}
