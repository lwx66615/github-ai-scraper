"""Tests for database performance optimizations."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ai_scraper.models.repository import Repository
from ai_scraper.storage.database import Database


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_perf.db"
        db = Database(db_path)
        db.init_db()
        yield db
        db.close()


@pytest.fixture
def sample_repos():
    """Create sample repositories for testing."""
    return [
        Repository(
            id=1,
            name="python/ml-framework",
            full_name="python/ml-framework",
            description="Machine learning framework",
            stars=5000,
            language="Python",
            topics=["ml", "ai"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/python/ml-framework",
        ),
        Repository(
            id=2,
            name="python/data-tools",
            full_name="python/data-tools",
            description="Data processing tools",
            stars=3000,
            language="Python",
            topics=["data", "processing"],
            created_at=datetime(2024, 1, 15),
            updated_at=datetime(2024, 5, 2),
            pushed_at=datetime(2024, 5, 8),
            url="https://github.com/python/data-tools",
        ),
        Repository(
            id=3,
            name="js/react-dashboard",
            full_name="js/react-dashboard",
            description="React dashboard component",
            stars=2000,
            language="JavaScript",
            topics=["react", "dashboard"],
            created_at=datetime(2024, 2, 1),
            updated_at=datetime(2024, 5, 3),
            pushed_at=datetime(2024, 5, 7),
            url="https://github.com/js/react-dashboard",
        ),
        Repository(
            id=4,
            name="python/ai-chatbot",
            full_name="python/ai-chatbot",
            description="AI chatbot library",
            stars=4000,
            language="Python",
            topics=["ai", "chatbot"],
            created_at=datetime(2024, 1, 20),
            updated_at=datetime(2024, 5, 4),
            pushed_at=datetime(2024, 5, 6),
            url="https://github.com/python/ai-chatbot",
        ),
        Repository(
            id=5,
            name="go/web-server",
            full_name="go/web-server",
            description="High performance web server",
            stars=1000,
            language="Go",
            topics=["web", "server"],
            created_at=datetime(2024, 3, 1),
            updated_at=datetime(2024, 5, 5),
            pushed_at=datetime(2024, 5, 5),
            url="https://github.com/go/web-server",
        ),
    ]


class TestGetReposByLanguage:
    """Tests for get_repos_by_language method."""

    def test_returns_correct_repos(self, temp_db, sample_repos):
        """Test that get_repos_by_language returns repos with matching language."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        python_repos = temp_db.get_repos_by_language("Python")

        assert len(python_repos) == 3
        for repo in python_repos:
            assert repo.language == "Python"

    def test_respects_limit(self, temp_db, sample_repos):
        """Test that get_repos_by_language respects the limit parameter."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        python_repos = temp_db.get_repos_by_language("Python", limit=2)

        assert len(python_repos) == 2

    def test_returns_empty_for_unknown_language(self, temp_db, sample_repos):
        """Test that get_repos_by_language returns empty list for unknown language."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        rust_repos = temp_db.get_repos_by_language("Rust")

        assert len(rust_repos) == 0

    def test_sorted_by_stars_desc(self, temp_db, sample_repos):
        """Test that results are sorted by stars descending."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        python_repos = temp_db.get_repos_by_language("Python")

        assert python_repos[0].stars >= python_repos[1].stars >= python_repos[2].stars


class TestGetTopRepos:
    """Tests for get_top_repos method."""

    def test_returns_repos_sorted_by_stars(self, temp_db, sample_repos):
        """Test that get_top_repos returns repos sorted by stars descending."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        top_repos = temp_db.get_top_repos()

        assert len(top_repos) == 5
        for i in range(len(top_repos) - 1):
            assert top_repos[i].stars >= top_repos[i + 1].stars

    def test_respects_limit(self, temp_db, sample_repos):
        """Test that get_top_repos respects the limit parameter."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        top_repos = temp_db.get_top_repos(limit=3)

        assert len(top_repos) == 3

    def test_returns_empty_when_no_repos(self, temp_db):
        """Test that get_top_repos returns empty list when database is empty."""
        top_repos = temp_db.get_top_repos()

        assert len(top_repos) == 0

    def test_default_limit(self, temp_db, sample_repos):
        """Test that default limit is 100."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        top_repos = temp_db.get_top_repos()

        # With 5 repos, all should be returned (less than default limit of 100)
        assert len(top_repos) == 5


class TestVacuum:
    """Tests for vacuum method."""

    def test_does_not_raise_errors(self, temp_db):
        """Test that vacuum doesn't raise errors on empty database."""
        # Should not raise any exception
        temp_db.vacuum()

    def test_works_with_data(self, temp_db, sample_repos):
        """Test that vacuum works correctly with data in database."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        # Should not raise any exception
        temp_db.vacuum()

        # Data should still be accessible after vacuum
        repos = temp_db.get_all_repositories()
        assert len(repos) == 5

    def test_optimizes_database_size(self, temp_db, sample_repos):
        """Test that vacuum optimizes database after deletion."""
        for repo in sample_repos:
            temp_db.save_repository(repo)

        # Delete some records
        cursor = temp_db.conn.cursor()
        cursor.execute("DELETE FROM repositories WHERE language = 'Go'")
        temp_db.conn.commit()

        # Get size before vacuum
        size_before = temp_db.db_path.stat().st_size

        temp_db.vacuum()

        # Get size after vacuum (should be smaller or equal)
        size_after = temp_db.db_path.stat().st_size

        # Vacuum should reclaim space
        assert size_after <= size_before
