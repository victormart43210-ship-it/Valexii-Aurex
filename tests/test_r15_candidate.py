"""R15 candidate static security gates; API behavior needs FastAPI integration tests."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / 'integrations/kusanagi-xvi/backend/r15_intake_api.py'

class R15CandidateStaticTests(unittest.TestCase):
    def test_syntax(self):
        ast.parse(MODULE.read_text())

    def test_no_upload_routes(self):
        code = MODULE.read_text()
        self.assertNotIn('UploadFile', code)
        self.assertNotIn('File(', code)

    def test_default_disabled(self):
        self.assertIn('AUREX_R15_INTAKE_ENABLED', MODULE.read_text())

    def test_server_controlled_mapping(self):
        self.assertIn('AUREX_R15_TENANT_TOKEN_MAP', MODULE.read_text())

    def test_r14_principal_resolution(self):
        self.assertIn('resolve_principal(', MODULE.read_text())

if __name__ == '__main__':
    unittest.main()
