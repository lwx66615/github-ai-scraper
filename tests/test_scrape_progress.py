"""Tests for scrape progress tracking."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime
from ai_scraper.scrape_progress import ScrapeProgress


def test_save_and_load_progress():
    """Test saving and loading scrape progress."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        # Save progress
        progress.save(
            query="stars:>100 topic:ai",
            last_page=3,
            total_found=250,
            timestamp=datetime.now(),
        )

        # Load progress
        loaded = progress.load("stars:>100 topic:ai")

        assert loaded is not None
        assert loaded["last_page"] == 3
        assert loaded["total_found"] == 250


def test_clear_progress():
    """Test clearing progress."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        progress.save("test_query", 5, 100, datetime.now())
        progress.clear("test_query")

        loaded = progress.load("test_query")
        assert loaded is None


def test_has_progress():
    """Test checking if progress exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        assert not progress.has_progress("test_query")

        progress.save("test_query", 1, 50, datetime.now())
        assert progress.has_progress("test_query")


def test_different_queries_have_different_files():
    """Test that different queries create different progress files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        progress.save("query1", 1, 10, datetime.now())
        progress.save("query2", 2, 20, datetime.now())

        loaded1 = progress.load("query1")
        loaded2 = progress.load("query2")

        assert loaded1["last_page"] == 1
        assert loaded2["last_page"] == 2


def test_load_nonexistent_progress():
    """Test loading progress that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        loaded = progress.load("nonexistent_query")
        assert loaded is None


def test_progress_timestamp_is_datetime():
    """Test that loaded timestamp is datetime object."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress = ScrapeProgress(Path(tmpdir))

        now = datetime.now()
        progress.save("test_query", 1, 10, now)

        loaded = progress.load("test_query")
        assert isinstance(loaded["timestamp"], datetime)
