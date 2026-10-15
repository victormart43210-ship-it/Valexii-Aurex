"""KUSANAGI XXII governed inference regression tests."""

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aurex.local_inference import LocalResult
from aurex_workflows.core import JobRequest, WorkflowEngine


class GovernedInferenceTests(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.db = Path(self.directory.name) / "jobs.sqlite"
        self.engine = WorkflowEngine(self.db)

    def submit(self):
        return self.engine.submit(
            JobRequest(
                kind="llm_eval",
                payload={
                    "prompt": "What is 2 + 2?",
                    "model": "local-qwen",
                    "base_url": "http://127.0.0.1:8080",
                },
            )
        )

    @staticmethod
    def fake_result():
        return LocalResult(
            provider="llama.cpp",
            model="local-qwen",
            text="4",
            sha256="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        )

    def test_unapproved_job_cannot_execute(self):
        job = self.submit()
        with patch(
            "aurex_workflows.local_executor.run_local_inference"
        ) as model:
            with self.assertRaises(PermissionError):
                self.engine.execute(job)
            model.assert_not_called()

        self.assertEqual(
            self.engine.inspect(job)["state"],
            "PENDING_APPROVAL",
        )

    def test_successful_inference_is_unverified(self):
        job = self.submit()
        self.engine.approve(job, human_approval=True)

        with patch(
            "aurex_workflows.local_executor.run_local_inference",
            return_value=self.fake_result(),
        ) as model:
            result = self.engine.execute(job)

        model.assert_called_once()
        self.assertEqual(result["text"], "4")
        self.assertFalse(result["verified"])
        self.assertFalse(result["authority_granted"])
        self.assertEqual(result["spend_usd"], 0.0)
        self.assertEqual(
            self.engine.inspect(job)["state"],
            "COMPLETED",
        )

        with sqlite3.connect(self.db) as conn:
            events = [
                row[0]
                for row in conn.execute(
                    "SELECT action FROM events WHERE job_id=? ORDER BY seq",
                    (job,),
                )
            ]

        self.assertEqual(
            events,
            [
                "SUBMITTED",
                "HUMAN_APPROVED",
                "STARTED",
                "COMPLETED",
            ],
        )

    def test_duplicate_execution_is_rejected(self):
        job = self.submit()
        self.engine.approve(job, human_approval=True)

        with patch(
            "aurex_workflows.local_executor.run_local_inference",
            return_value=self.fake_result(),
        ) as model:
            self.engine.execute(job)

            with self.assertRaises(PermissionError):
                self.engine.execute(job)

            model.assert_called_once()

    def test_model_failure_is_persisted(self):
        job = self.submit()
        self.engine.approve(job, human_approval=True)

        with patch(
            "aurex_workflows.local_executor.run_local_inference",
            side_effect=RuntimeError("simulated model failure"),
        ):
            with self.assertRaises(RuntimeError):
                self.engine.execute(job)

        self.assertEqual(
            self.engine.inspect(job)["state"],
            "FAILED",
        )

        with sqlite3.connect(self.db) as conn:
            actions = [
                row[0]
                for row in conn.execute(
                    "SELECT action FROM events WHERE job_id=? ORDER BY seq",
                    (job,),
                )
            ]

        self.assertEqual(actions[-1], "FAILED")

    def test_evidence_fingerprint_is_preserved(self):
        job = self.submit()
        self.engine.approve(job, human_approval=True)

        with patch(
            "aurex_workflows.local_executor.run_local_inference",
            return_value=self.fake_result(),
        ):
            self.engine.execute(job)

        saved = self.engine.inspect(job)["result"]

        self.assertEqual(
            saved["sha256"],
            self.fake_result().sha256,
        )
        self.assertFalse(saved["authority_granted"])


if __name__ == "__main__":
    unittest.main()
