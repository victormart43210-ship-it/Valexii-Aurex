import tempfile
import unittest
from pathlib import Path

from aurex_workflows import JobRequest, WorkflowEngine


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.engine = WorkflowEngine(Path(self.temp.name)/'test.db')
    def tearDown(self):
        self.temp.cleanup()
    def test_approval_required(self):
        jid = self.engine.submit(JobRequest('xaeli_eval', {}))
        with self.assertRaises(PermissionError):
            self.engine.execute(jid)
        self.engine.approve(jid, human_approval=True)
        self.assertEqual(self.engine.execute(jid)['status'], 'PLAN_ONLY_NOT_EXECUTED')
    def test_no_paid_execution(self):
        with self.assertRaises(ValueError):
            self.engine.submit(JobRequest('llm_eval', {}, budget_usd=0.01))
    def test_no_unknown_tools(self):
        with self.assertRaises(ValueError):
            self.engine.submit(JobRequest('arbitrary_shell', {}))
    def test_dataset_validation(self):
        jid = self.engine.submit(JobRequest('dataset_validate', {'examples':[{'input':'a','expected':'b'}, {'input':'x'}]}))
        self.engine.approve(jid, human_approval=True)
        self.assertEqual(self.engine.execute(jid)['valid'], 1)
    def test_no_repeat_approval(self):
        jid = self.engine.submit(JobRequest('training_plan', {}))
        self.engine.approve(jid, human_approval=True)
        with self.assertRaises(ValueError):
            self.engine.approve(jid, human_approval=True)

if __name__ == '__main__':
    unittest.main()
