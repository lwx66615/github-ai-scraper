"""Tests for incremental scraping functionality."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ai_scraper.models.repository import Repository
from ai_scraper.storage.database import Database


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        db.init_db()
        yield db
        db.close()


class TestGetLastScrapeTime:
    """Tests for get_last_scrape_time method."""

    def test_returns_none_when_no_repos(self, temp_db):
        """Test that None is returned when database is empty."""
        result = temp_db.get_last_scrape_time()
        assert result is None

    def test_returns_timestamp_after_saving_repo(self, temp_db):
        """Test that timestamp is returned after saving a repository."""
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description="A test repository",
            stars=1000,
            language="Python",
            topics=["ai", "machine-learning"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )

        temp_db.save_repository(repo)
        result = temp_db.get_last_scrape_time()

        assert result is not None
        # Should be around the current time (when the scrape happened)
        now = datetime.now()
        assert abs((result - now).total_seconds()) < 5  # Within 5 seconds

    def test_returns_max_last_updated_at(self, temp_db):
        """Test that MAX(last_updated_at) is returned when multiple repos exist."""
        # Save repos - the last_updated_at is set by save_repository as datetime.now()
        # So we save them in sequence and the second one should have a later timestamp
        repo1 = Repository(
            id=1,
            name="test/repo1",
            full_name="test/repo1",
            description="First repo",
            stars=1000,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo1",
        )

        temp_db.save_repository(repo1)

        # Small delay to ensure different timestamp
        import time
        time.sleep(0.1)

        repo2 = Repository(
            id=2,
            name="test/repo2",
            full_name="test/repo2",
            description="Second repo",
            stars=2000,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 15),
            pushed_at=datetime(2024, 5, 15),
            url="https://github.com/test/repo2",
        )

        temp_db.save_repository(repo2)

        result = temp_db.get_last_scrape_time()

        assert result is not None
        # The result should be close to now (when repo2 was saved)
        now = datetime.now()
        assert abs((result - now).total_seconds()) < 5  # Within 5 seconds


class TestGetReposUpdatedSince:
    """Tests for get_repos_updated_since method."""

    def test_returns_empty_list_when_no_matches(self, temp_db):
        """Test that empty list is returned when no repos match the since time."""
        repo = Repository(
            id=1,
            name="test/repo",
            full_name="test/repo",
            description="Test",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 1),
            url="https://github.com/test/repo",
        )
        temp_db.save_repository(repo)

        # Query for repos scraped after a future date (should return empty)
        since = datetime.now() + timedelta(days=1)
        result = temp_db.get_repos_updated_since(since)

        assert result == []

    def test_returns_repos_updated_after_since(self, temp_db):
        """Test that repos scraped after the since time are returned."""
        # Save a repo, then query with a since time before it
        repo1 = Repository(
            id=1,
            name="test/old-repo",
            full_name="test/old-repo",
            description="Old repo",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 3, 1),
            pushed_at=datetime(2024, 3, 1),
            url="https://github.com/test/old-repo",
        )
        temp_db.save_repository(repo1)

        # Query with since time 1 second ago - should include this repo
        since = datetime.now() - timedelta(seconds=1)
        result = temp_db.get_repos_updated_since(since)

        assert len(result) == 1
        assert result[0].name == "test/old-repo"

    def test_includes_repos_updated_exactly_at_since(self, temp_db):
        """Test that repos scraped exactly at the since time are included."""
        # Save a repo first
        repo = Repository(
            id=1,
            name="test/repo",
            full_name="test/repo",
            description="Test",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 10),
            pushed_at=datetime(2024, 5, 10),
            url="https://github.com/test/repo",
        )
        temp_db.save_repository(repo)

        # Get the actual last_updated_at from the database
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT last_updated_at FROM repositories WHERE id = 1")
        row = cursor.fetchone()
        actual_time = datetime.fromisoformat(row["last_updated_at"])

        # Query with that exact time
        result = temp_db.get_repos_updated_since(actual_time)

        assert len(result) == 1
        assert result[0].name == "test/repo"


class TestNeedsUpdate:
    """Tests for needs_update method."""

    def test_returns_true_for_old_repo(self, temp_db):
        """Test that True is returned for repo older than max_age_days."""
        # Create a repo
        repo = Repository(
            id=1,
            name="test/old-repo",
            full_name="test/old-repo",
            description="Old repo",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 1),
            url="https://github.com/test/old-repo",
        )
        temp_db.save_repository(repo)

        # Manually update last_updated_at to be 10 days ago
        old_update_time = datetime.now() - timedelta(days=10)
        cursor = temp_db.conn.cursor()
        cursor.execute(
            "UPDATE repositories SET last_updated_at = ? WHERE id = ?",
            (old_update_time.isoformat(), 1)
        )
        temp_db.conn.commit()

        result = temp_db.needs_update(repo_id=1, max_age_days=7)

        assert result is True

    def test_returns_false_for_recent_repo(self, temp_db):
        """Test that False is returned for repo newer than max_age_days."""
        # Create repo - last_updated_at will be now
        repo = Repository(
            id=1,
            name="test/recent-repo",
            full_name="test/recent-repo",
            description="Recent repo",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime.now() - timedelta(days=3),
            pushed_at=datetime.now() - timedelta(days=3),
            url="https://github.com/test/recent-repo",
        )
        temp_db.save_repository(repo)

        # The repo was just saved, so last_updated_at is now, which is < 7 days
        result = temp_db.needs_update(repo_id=1, max_age_days=7)

        assert result is False

    def test_returns_true_for_nonexistent_repo(self, temp_db):
        """Test that True is returned for repo that doesn't exist in database."""
        result = temp_db.needs_update(repo_id=99999, max_age_days=7)

        assert result is True

    def test_default_max_age_is_seven_days(self, temp_db):
        """Test that default max_age_days is 7."""
        # Create a repo
        repo = Repository(
            id=1,
            name="test/repo",
            full_name="test/repo",
            description="Test repo",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 1),
            url="https://github.com/test/repo",
        )
        temp_db.save_repository(repo)

        # Manually update last_updated_at to be 8 days ago
        old_update_time = datetime.now() - timedelta(days=8)
        cursor = temp_db.conn.cursor()
        cursor.execute(
            "UPDATE repositories SET last_updated_at = ? WHERE id = ?",
            (old_update_time.isoformat(), 1)
        )
        temp_db.conn.commit()

        result = temp_db.needs_update(repo_id=1)  # Using default max_age_days

        assert result is True
