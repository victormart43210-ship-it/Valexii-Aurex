import hashlib
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from sovereign_intake.storage import initialize, register, get_for_tenant


class SovereignIntakeR13Tests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "intake.sqlite3")

        with self.connection() as conn:
            initialize(conn)

        self.digest = hashlib.sha256(b"synthetic towing").hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def connection(self):
        conn = sqlite3.connect(self.db, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def payload(self, **changes):
        data = {
            "tenant_id": "tenant-alpha",
            "source_label": "synthetic-towing",
            "content_sha256": self.digest,
            "size_bytes": 16,
            "idempotency_key": "synthetic-idempotency-key",
        }
        data.update(changes)
        return data

    def test_quarantined_registration(self):
        with self.connection() as conn:
            record = register(conn, **self.payload())

        self.assertEqual(record["status"], "QUARANTINED")
        self.assertEqual(record["authority"], "NONE")

    def test_tenant_isolation(self):
        with self.connection() as conn:
            record = register(conn, **self.payload())
            self.assertIsNone(
                get_for_tenant(conn, "tenant-beta", record["id"])
            )
            self.assertIsNotNone(
                get_for_tenant(conn, "tenant-alpha", record["id"])
            )

    def test_idempotent_replay(self):
        with self.connection() as conn:
            first = register(conn, **self.payload())
            second = register(conn, **self.payload())

        self.assertEqual(first["id"], second["id"])

    def test_conflicting_replay(self):
        with self.connection() as conn:
            register(conn, **self.payload())

            with self.assertRaises(ValueError):
                register(
                    conn,
                    **self.payload(source_label="different"),
                )

    def test_invalid_digest(self):
        with self.connection() as conn:
            with self.assertRaises(ValueError):
                register(
                    conn,
                    **self.payload(content_sha256="invalid"),
                )

    def test_concurrent_replay(self):
        barrier = threading.Barrier(2)
        results = []
        errors = []

        def worker():
            try:
                with self.connection() as conn:
                    barrier.wait(timeout=5)
                    record = register(conn, **self.payload())
                    results.append(record["id"])
            except Exception as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=worker)
            for _ in range(2)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=15)

        self.assertFalse(errors, errors)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], results[1])

    def test_database_constraint(self):
        with self.connection() as conn:
            register(conn, **self.payload())

            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    """
                    UPDATE intake_records
                    SET authority = 'APPROVED'
                    """
                )

    def test_failed_registration_does_not_modify_record(self):
        with self.connection() as conn:
            original = register(conn, **self.payload())

            with self.assertRaises(ValueError):
                register(
                    conn,
                    **self.payload(source_label="conflict"),
                )

            recovered = get_for_tenant(
                conn, "tenant-alpha", original["id"]
            )

        self.assertEqual(recovered, original)


if __name__ == "__main__":
    unittest.main()
