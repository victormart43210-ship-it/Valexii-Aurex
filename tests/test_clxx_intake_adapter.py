"""Offline AUREX/R13 adapter regression tests."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for directory in (
    ROOT / "integrations" / "kusanagi-xvi",
    ROOT / "integrations" / "sovereign_intake",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from backend import intake_adapter, store


class IntakeAdapterTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / "aurex.sqlite3")
        store.initialize(self.db)

        self.params = {
            "tenant_id": "synthetic-towing",
            "source_label": "synthetic-ticket",
            "content_sha256": "a" * 64,
            "size_bytes": 100,
            "idempotency_key": "ticket-001",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_registration_and_tenant_isolation(self):
        record = intake_adapter.register_intake(
            self.db, **self.params
        )

        self.assertEqual(record["status"], "QUARANTINED")
        self.assertEqual(record["authority"], "NONE")

        replay = intake_adapter.register_intake(
            self.db, **self.params
        )
        self.assertEqual(replay["id"], record["id"])

        found = intake_adapter.get_intake(
            self.db,
            tenant_id="synthetic-towing",
            record_id=record["id"],
        )
        self.assertEqual(found, record)

        denied = intake_adapter.get_intake(
            self.db,
            tenant_id="other-tenant",
            record_id=record["id"],
        )
        self.assertIsNone(denied)

    def test_conflicting_replay_rejected(self):
        intake_adapter.register_intake(
            self.db, **self.params
        )

        changed = {**self.params, "size_bytes": 200}

        with self.assertRaisesRegex(
            ValueError, "idempotency conflict"
        ):
            intake_adapter.register_intake(
                self.db, **changed
            )


if __name__ == "__main__":
    unittest.main()
