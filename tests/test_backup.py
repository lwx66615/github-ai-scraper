"""Tests for database backup."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime
from ai_scraper.backup import BackupManager


def test_create_backup():
    """Test creating a database backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create a simple database
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir)
        backup_path = manager.create_backup(db_path)

        assert backup_path.exists()
        assert ".db" in backup_path.name
        assert "backup_" in backup_path.name


def test_list_backups():
    """Test listing available backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create database
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir)

        # Create multiple backups
        manager.create_backup(db_path)
        manager.create_backup(db_path)

        backups = manager.list_backups()
        assert len(backups) >= 2


def test_restore_backup():
    """Test restoring from backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create database with data
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'original')")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir)
        backup_path = manager.create_backup(db_path)

        # Modify database
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE test SET value = 'modified'")
        conn.commit()
        conn.close()

        # Restore
        manager.restore_backup(backup_path, db_path)

        # Verify restored data
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT value FROM test")
        row = cursor.fetchone()
        conn.close()

        assert row[0] == "original"


def test_cleanup_old_backups():
    """Test cleaning up old backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create database
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir, max_backups=2)

        # Create more backups than max
        manager.create_backup(db_path)
        manager.create_backup(db_path)
        manager.create_backup(db_path)

        backups = manager.list_backups()
        assert len(backups) <= 2


def test_compressed_backup():
    """Test compressed backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create database
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir, compress=True)
        backup_path = manager.create_backup(db_path)

        assert backup_path.suffix == ".gz"


def test_uncompressed_backup():
    """Test uncompressed backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        backup_dir = Path(tmpdir) / "backups"

        # Create database
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        manager = BackupManager(backup_dir, compress=False)
        backup_path = manager.create_backup(db_path)

        assert backup_path.suffix == ".db"
        assert ".gz" not in backup_path.name


def test_backup_nonexistent_database():
    """Test backup of nonexistent database raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "nonexistent.db"
        backup_dir = Path(tmpdir) / "backups"

        manager = BackupManager(backup_dir)

        with pytest.raises(FileNotFoundError):
            manager.create_backup(db_path)
