"""XXIII fail-closed recovery matrix; no model calls or network access."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from aurex_workflows.core import JobRequest, WorkflowEngine
from aurex_workflows.recovery import recover_interrupted_jobs


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/'jobs.sqlite'
        self.engine=WorkflowEngine(self.db)
        self.job=self.engine.submit(JobRequest(kind='llm_eval',payload={'prompt':'test'}))
        self.engine.approve(self.job,human_approval=True)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE jobs SET state='RUNNING',updated_at=100 WHERE id=?",(self.job,))
    def test_operator_confirmation_required(self):
        with self.assertRaises(PermissionError):
            recover_interrupted_jobs(self.db,older_than_seconds=60,now=1000)
    def test_stale_job_is_demoted_and_audited(self):
        self.assertEqual(recover_interrupted_jobs(self.db,older_than_seconds=60,now=1000,operator_confirmed_no_active_workers=True),[self.job])
        self.assertEqual(self.engine.inspect(self.job)['state'],'FAILED_INTERRUPTED')
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute('SELECT action FROM events WHERE job_id=? ORDER BY seq DESC LIMIT 1',(self.job,)).fetchone()[0],'FAILED_INTERRUPTED')
        with self.assertRaises(PermissionError):
            self.engine.execute(self.job)
    def test_recent_job_unchanged(self):
        self.assertEqual(recover_interrupted_jobs(self.db,older_than_seconds=60,now=120,operator_confirmed_no_active_workers=True),[])
        self.assertEqual(self.engine.inspect(self.job)['state'],'RUNNING')
    def test_idempotent(self):
        kw=dict(older_than_seconds=60,now=1000,operator_confirmed_no_active_workers=True)
        recover_interrupted_jobs(self.db,**kw)
        self.assertEqual(recover_interrupted_jobs(self.db,**kw),[])
    def test_invalid_cutoff_rejected(self):
        with self.assertRaises(ValueError):
            recover_interrupted_jobs(self.db,older_than_seconds=0,now=1000,operator_confirmed_no_active_workers=True)
    def test_missing_db_does_not_create_one(self):
        missing=Path(self.temp.name)/'missing.sqlite'
        with self.assertRaises(FileNotFoundError):
            recover_interrupted_jobs(missing,older_than_seconds=60,now=1000,operator_confirmed_no_active_workers=True)
        self.assertFalse(missing.exists())
