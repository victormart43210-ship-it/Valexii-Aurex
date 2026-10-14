"""Run: python3 -m unittest examples/aurex-backend/test_budget.py (stdlib only)."""
import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import budget  # noqa: E402


class BudgetTests(unittest.TestCase):
    def test_no_spend_default(self):
        con = budget.connect()
        self.assertEqual(budget.reserve(con, 0.01), (None, "no_spend_default"))

    def test_invalid_amount(self):
        con = budget.connect(limit_usd=10)
        self.assertEqual(budget.reserve(con, -1)[1], "invalid_amount")
        self.assertEqual(budget.reserve(con, 0)[1], "invalid_amount")

    def test_commit_cannot_exceed_reservation(self):
        con = budget.connect(limit_usd=10)
        rid, _ = budget.reserve(con, 5)
        self.assertFalse(budget.commit(con, rid, 6))
        self.assertTrue(budget.commit(con, rid, 4))
        self.assertFalse(budget.commit(con, rid, 1))

    def test_release_frees_budget(self):
        con = budget.connect(limit_usd=5)
        rid, _ = budget.reserve(con, 5)
        self.assertEqual(budget.reserve(con, 1)[1], "budget_exceeded")
        self.assertTrue(budget.release(con, rid))
        self.assertEqual(budget.reserve(con, 1)[1], "ok")

    def test_concurrent_reservations_never_overspend(self):
        path = os.path.join(tempfile.mkdtemp(), "b.db")
        budget.connect(path, limit_usd=10).close()
        results = []
        lock = threading.Lock()

        def worker():
            con = budget.connect(path)
            r = budget.reserve(con, 1)
            with lock:
                results.append(r[1])
            con.close()

        threads = [threading.Thread(target=worker) for _ in range(40)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(results.count("ok"), 10)
        self.assertEqual(results.count("budget_exceeded"), 30)


if __name__ == "__main__":
    unittest.main()
