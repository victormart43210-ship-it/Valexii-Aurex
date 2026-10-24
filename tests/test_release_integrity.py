"""Negative checks for release integrity identity verification."""
import unittest
from unittest.mock import patch
from scripts.verify_release_integrity import verify

class IntegrityTests(unittest.TestCase):
    def test_invalid_branch_rejected(self):
        for branch in ("--upload-pack=evil", "../main", "foo@{1}", "bad branch"):
            with self.assertRaises(ValueError):
                verify("origin", branch)

    @patch("scripts.verify_release_integrity.git")
    def test_missing_remote_is_hold(self, git):
        git.return_value.returncode = 2
        with self.assertRaises(RuntimeError):
            verify("origin", "main")

    @patch("scripts.verify_release_integrity.git")
    def test_branch_movement_is_hold(self, git):
        sha = "a" * 40
        other = "b" * 40
        def response(*args):
            class R:
                returncode = 0
                stderr = ""
            r = R()
            r.stdout = (sha + "\trefs/heads/main\n") if args[0] == "ls-remote" and response.count == 0 else ""
            if args[0] == "ls-remote":
                r.stdout = (sha if response.count == 0 else other) + "\trefs/heads/main\n"
                response.count += 1
            elif args[0] == "rev-parse":
                r.stdout = sha + "\n"
            return r
        response.count = 0
        git.side_effect = response
        with self.assertRaises(RuntimeError):
            verify("origin", "main")
