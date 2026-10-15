"""Regression tests for durable AUREX workflow failures."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from aurex_workflows.core import JobRequest, WorkflowEngine


class WorkflowFailureTests(unittest.TestCase):

    def test_failed_execution_persists_and_cannot_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "workflow.db"
            engine = WorkflowEngine(db)

            job = engine.submit(
                JobRequest(
                    kind="dataset_validate",
                    payload={"examples": "invalid"},
                )
            )

            engine.approve(job, human_approval=True)

            with self.assertRaises(ValueError):
                engine.execute(job)

            self.assertEqual(engine.inspect(job)["state"], "FAILED")

            with sqlite3.connect(db) as conn:
                events = [
                    row[0]
                    for row in conn.execute(
                        "SELECT action FROM events WHERE job_id=? ORDER BY seq",
                        (job,),
                    )
                ]

            self.assertEqual(
                events,
                ["SUBMITTED", "HUMAN_APPROVED", "STARTED", "FAILED"],
            )

            with self.assertRaises(PermissionError):
                engine.execute(job)
