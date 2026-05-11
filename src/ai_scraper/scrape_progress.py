"""Scrape progress tracking for resume support."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib


class ScrapeProgress:
    """Track and persist scrape progress for resume support."""

    def __init__(self, storage_dir: Path):
        """Initialize progress tracker.

        Args:
            storage_dir: Directory for storing progress files.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _query_to_filename(self, query: str) -> str:
        """Convert query to a safe filename."""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"progress_{query_hash}.json"

    def save(
        self,
        query: str,
        last_page: int,
        total_found: int,
        timestamp: datetime,
    ) -> None:
        """Save scrape progress.

        Args:
            query: Search query.
            last_page: Last successfully fetched page.
            total_found: Total repositories found so far.
            timestamp: Timestamp of the progress.
        """
        filename = self._query_to_filename(query)
        filepath = self.storage_dir / filename

        data = {
            "query": query,
            "last_page": last_page,
            "total_found": total_found,
            "timestamp": timestamp.isoformat(),
        }

        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self, query: str) -> Optional[dict]:
        """Load scrape progress.

        Args:
            query: Search query.

        Returns:
            Progress data or None if not found.
        """
        filename = self._query_to_filename(query)
        filepath = self.storage_dir / filename

        if not filepath.exists():
            return None

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            return data
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def clear(self, query: str) -> None:
        """Clear progress for a query.

        Args:
            query: Search query.
        """
        filename = self._query_to_filename(query)
        filepath = self.storage_dir / filename

        if filepath.exists():
            filepath.unlink()

    def has_progress(self, query: str) -> bool:
        """Check if progress exists for a query.

        Args:
            query: Search query.

        Returns:
            True if progress exists.
        """
        filename = self._query_to_filename(query)
        filepath = self.storage_dir / filename
        return filepath.exists()