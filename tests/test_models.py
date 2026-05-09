"""Tests for data models."""

from datetime import datetime

from ai_scraper.models.repository import Repository, RepoSnapshot, FilterConfig, ScrapeConfig


def test_repository_creation():
    """Test Repository model creation."""
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
    assert repo.id == 12345
    assert repo.name == "test/repo"
    assert repo.stars == 1000
    assert "ai" in repo.topics


def test_repository_optional_fields():
    """Test Repository with optional fields."""
    repo = Repository(
        id=1,
        name="test/repo",
        full_name="test/repo",
        description=None,
        stars=100,
        language=None,
        topics=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
        open_issues=10,
        forks=5,
        contributors=20,
    )
    assert repo.description is None
    assert repo.open_issues == 10
    assert repo.forks == 5
    assert repo.contributors == 20


def test_repo_snapshot():
    """Test RepoSnapshot model."""
    snapshot = RepoSnapshot(
        repo_id=12345,
        stars=1000,
        snapshot_at=datetime(2024, 5, 9, 10, 30),
    )
    assert snapshot.repo_id == 12345
    assert snapshot.stars == 1000


def test_filter_config_defaults():
    """Test FilterConfig default values."""
    config = FilterConfig(
        keywords=["ai"],
        topics=["machine-learning"],
        languages=[],
        exclude_keywords=[],
    )
    assert config.min_stars == 100
    assert "ai" in config.keywords


def test_scrape_config_defaults():
    """Test ScrapeConfig default values."""
    config = ScrapeConfig(
        data_fields=["stars", "language"],
        max_results=100,
        concurrency=5,
        cache_ttl=3600,
    )
    assert config.max_results == 100
    assert config.concurrency == 5
