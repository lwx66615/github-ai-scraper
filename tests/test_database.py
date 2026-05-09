"""Tests for database storage."""

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
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        db.init_db()
        yield db
        db.close()


def test_init_db(temp_db):
    """Test database initialization."""
    assert temp_db.db_path.exists()


def test_save_repository(temp_db):
    """Test saving a repository."""
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

    repos = temp_db.get_all_repositories()
    assert len(repos) == 1
    assert repos[0].name == "test/repo"
    assert repos[0].stars == 1000


def test_update_repository(temp_db):
    """Test updating an existing repository."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="A test repository",
        stars=1000,
        language="Python",
        topics=["ai"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo)

    # Update with same ID but different stars
    repo_updated = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="Updated description",
        stars=1500,
        language="Python",
        topics=["ai"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 10),
        pushed_at=datetime(2024, 5, 10),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo_updated)

    repos = temp_db.get_all_repositories()
    assert len(repos) == 1
    assert repos[0].stars == 1500
    assert repos[0].description == "Updated description"


def test_save_snapshot(temp_db):
    """Test saving repository snapshot."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="Test",
        stars=1000,
        language="Python",
        topics=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo)
    temp_db.save_snapshot(12345, 1000, datetime(2024, 5, 9, 10, 0))
    temp_db.save_snapshot(12345, 1100, datetime(2024, 5, 10, 10, 0))

    snapshots = temp_db.get_snapshots(12345)
    assert len(snapshots) == 2


def test_get_trending(temp_db):
    """Test getting trending repositories."""
    from datetime import timedelta

    now = datetime.now()
    earlier = now - timedelta(days=1)

    # Create repos with different star growth
    for i, (repo_id, initial_stars, later_stars) in enumerate([
        (1, 100, 150),   # 50% growth
        (2, 100, 200),   # 100% growth
        (3, 100, 120),   # 20% growth
    ]):
        repo = Repository(
            id=repo_id,
            name=f"test/repo{i}",
            full_name=f"test/repo{i}",
            description="Test",
            stars=later_stars,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url=f"https://github.com/test/repo{i}",
        )
        temp_db.save_repository(repo)
        # Use recent dates for snapshots
        temp_db.save_snapshot(repo_id, initial_stars, earlier)
        temp_db.save_snapshot(repo_id, later_stars, now)

    trending = temp_db.get_trending(days=7)
    assert len(trending) == 3
    # Should be sorted by growth
    assert trending[0].repo_id == 2  # 100% growth
    assert trending[1].repo_id == 1  # 50% growth
    assert trending[2].repo_id == 3  # 20% growth


def test_search_local(temp_db):
    """Test local search functionality."""
    repos = [
        Repository(
            id=i,
            name=f"test/{name}",
            full_name=f"test/{name}",
            description=desc,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url=f"https://github.com/test/{name}",
        )
        for i, (name, desc) in enumerate([
            ("ai-toolkit", "AI toolkit"),
            ("ml-lib", "Machine learning library"),
            ("web-app", "Web application"),
        ])
    ]

    for repo in repos:
        temp_db.save_repository(repo)

    results = temp_db.search_local("ai")
    assert len(results) == 1
    assert results[0].name == "test/ai-toolkit"
