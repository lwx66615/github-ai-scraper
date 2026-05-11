"""Tests for async database operations."""

import pytest
from pathlib import Path
import tempfile
from ai_scraper.storage.async_database import AsyncDatabase
from ai_scraper.models.repository import Repository
from datetime import datetime


@pytest.mark.asyncio
async def test_async_save_and_get_repository():
    """Test async save and get repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description="Test repository",
            stars=1000,
            language="Python",
            topics=["ai", "ml"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo",
        )

        await db.save_repository(repo, relevance_score=0.8)
        repos = await db.get_all_repositories(limit=10)

        assert len(repos) == 1
        assert repos[0].name == "test/repo"
        assert repos[0].stars == 1000

        await db.close()


@pytest.mark.asyncio
async def test_async_get_repository_by_id():
    """Test async get repository by ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        repo = Repository(
            id=99999,
            name="test/specific",
            full_name="test/specific",
            description="Specific repo",
            stars=500,
            language="Go",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/specific",
        )

        await db.save_repository(repo)
        found = await db.get_repository_by_id(99999)

        assert found is not None
        assert found.name == "test/specific"

        not_found = await db.get_repository_by_id(11111)
        assert not_found is None

        await db.close()


@pytest.mark.asyncio
async def test_async_get_stats():
    """Test async get database statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        # Add some repos
        for i in range(3):
            repo = Repository(
                id=10000 + i,
                name=f"test/repo{i}",
                full_name=f"test/repo{i}",
                description=f"Repo {i}",
                stars=100 * (i + 1),
                language="Python",
                topics=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                pushed_at=datetime.now(),
                url=f"https://github.com/test/repo{i}",
            )
            await db.save_repository(repo)

        stats = await db.get_stats()

        assert stats["repository_count"] == 3
        assert stats["total_stars"] == 600  # 100 + 200 + 300

        await db.close()


@pytest.mark.asyncio
async def test_async_search_local():
    """Test async local search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        repo1 = Repository(
            id=1,
            name="test/ai-project",
            full_name="test/ai-project",
            description="An AI machine learning project",
            stars=1000,
            language="Python",
            topics=["ai"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/ai-project",
        )

        repo2 = Repository(
            id=2,
            name="test/web-app",
            full_name="test/web-app",
            description="A web application",
            stars=500,
            language="JavaScript",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/web-app",
        )

        await db.save_repository(repo1)
        await db.save_repository(repo2)

        # Search for "AI"
        results = await db.search_local("ai")
        assert len(results) == 1
        assert results[0].name == "test/ai-project"

        # Search for "web"
        results = await db.search_local("web")
        assert len(results) == 1
        assert results[0].name == "test/web-app"

        await db.close()


@pytest.mark.asyncio
async def test_async_get_last_scrape_time():
    """Test async get last scrape time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        # Empty database
        last_time = await db.get_last_scrape_time()
        assert last_time is None

        # Add a repo
        repo = Repository(
            id=1,
            name="test/repo",
            full_name="test/repo",
            description="Test",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo",
        )
        await db.save_repository(repo)

        last_time = await db.get_last_scrape_time()
        assert last_time is not None

        await db.close()
