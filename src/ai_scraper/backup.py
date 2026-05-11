"""Database backup management."""

import gzip
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BackupManager:
    """Manage database backups."""

    def __init__(
        self,
        backup_dir: Path,
        max_backups: int = 10,
        compress: bool = True,
    ):
        """Initialize backup manager.

        Args:
            backup_dir: Directory for storing backups.
            max_backups: Maximum number of backups to keep.
            compress: Whether to compress backups.
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = max_backups
        self.compress = compress

    def create_backup(self, db_path: Path, name: Optional[str] = None) -> Path:
        """Create a backup of the database.

        Args:
            db_path: Path to database file.
            name: Optional custom name for backup.

        Returns:
            Path to created backup file.
        """
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_name += ".db.gz" if self.compress else ".db"

        backup_path = self.backup_dir / backup_name

        if self.compress:
            with open(db_path, "rb") as f_in:
                with gzip.open(backup_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(db_path, backup_path)

        logger.info(f"Created backup: {backup_path}")

        # Cleanup old backups
        self._cleanup_old_backups()

        return backup_path

    def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        """Restore database from backup.

        Args:
            backup_path: Path to backup file.
            target_path: Path to restore database to.
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        if backup_path.suffix == ".gz":
            with gzip.open(backup_path, "rb") as f_in:
                with open(target_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup_path, target_path)

        logger.info(f"Restored backup to: {target_path}")

    def list_backups(self) -> list[Path]:
        """List all available backups.

        Returns:
            List of backup file paths, sorted by modification time (newest first).
        """
        backups = list(self.backup_dir.glob("backup_*.db*"))
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups

    def delete_backup(self, backup_path: Path) -> None:
        """Delete a backup file.

        Args:
            backup_path: Path to backup file.
        """
        if backup_path.exists():
            backup_path.unlink()
            logger.info(f"Deleted backup: {backup_path}")

    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding max_backups limit."""
        backups = self.list_backups()

        while len(backups) > self.max_backups:
            old_backup = backups.pop()
            self.delete_backup(old_backup)
