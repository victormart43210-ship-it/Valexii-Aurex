"""Restore-copy checks against real SQLite, including uncheckpointed WAL data."""
import sqlite3
import subprocess
import sys

from aurex.database import create_job


def run_backup(source, destination):
    return subprocess.run(
        [sys.executable, '-m', 'aurex.backup', str(source), str(destination)],
        capture_output=True, text=True, timeout=10,
    )


def test_backup_includes_wal_and_preserves_owner_on_restore(tmp_path):
    source, dest = tmp_path / 'source.db', tmp_path / 'backup.db'
    create_job(str(source), 'job-one', 'local_inference', {'prompt': 'private'}, owner_id='alice')
    with sqlite3.connect(source) as live:
        live.execute('PRAGMA journal_mode=WAL')
        live.execute("UPDATE jobs SET state='cancelled' WHERE id='job-one'")
        live.commit()
        result = run_backup(source, dest)
        assert result.returncode == 0, result.stderr
        with sqlite3.connect(dest) as restored:
            assert restored.execute('SELECT id, owner_id, state FROM jobs').fetchall() == [
                ('job-one', 'alice', 'cancelled')]
            assert restored.execute('PRAGMA integrity_check').fetchone() == ('ok',)
    assert dest.stat().st_mode & 0o777 == 0o600
    assert 'private' not in result.stdout + result.stderr


def test_backup_refuses_overwrite(tmp_path):
    source, dest = tmp_path / 'source.db', tmp_path / 'backup.db'
    create_job(str(source), 'j', 'local_inference', {})
    dest.write_bytes(b'preserve-existing')
    result = run_backup(source, dest)
    assert result.returncode != 0
    assert "Backup refused" in result.stderr
    assert dest.read_bytes() == b'preserve-existing'


def test_missing_source_does_not_create_database(tmp_path):
    source, dest = tmp_path / 'missing.db', tmp_path / 'backup.db'
    result = run_backup(source, dest)
    assert result.returncode != 0
    assert "Backup refused" in result.stderr
    assert not source.exists() and not dest.exists()


def test_unsupported_schema_not_published(tmp_path):
    source, dest = tmp_path / 'future.db', tmp_path / 'backup.db'
    with sqlite3.connect(source) as conn:
        conn.execute('PRAGMA user_version=999')
    result = run_backup(source, dest)
    assert result.returncode != 0
    assert "Backup refused" in result.stderr
    assert not dest.exists()
    assert set(tmp_path.iterdir()) == {source}


def test_version_marker_without_aurex_tables_is_rejected(tmp_path):
    source, dest = tmp_path / 'empty.db', tmp_path / 'backup.db'
    with sqlite3.connect(source) as conn:
        conn.execute('PRAGMA user_version=2')
    result = run_backup(source, dest)
    assert result.returncode != 0
    assert 'Backup refused' in result.stderr
    assert not dest.exists()
