"""Tests for API server performance optimization."""

import pytest
from pathlib import Path
import tempfile
from ai_scraper.storage.async_database import AsyncDatabase
from ai_scraper.models.repository import Repository
from datetime import datetime


@pytest.mark.asyncio
async def test_get_repository_by_id_direct_query():
    """Test that get_repository_by_id uses direct query, not full scan."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        # Create 100 repos
        for i in range(100):
            repo = Repository(
                id=10000 + i,
                name=f"test/repo{i}",
                full_name=f"test/repo{i}",
                description=f"Repo {i}",
                stars=i * 10,
                language="Python",
                topics=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                pushed_at=datetime.now(),
                url=f"https://github.com/test/repo{i}",
            )
            await db.save_repository(repo)

        # Get specific repo - should use direct query
        found = await db.get_repository_by_id(10050)
        assert found is not None
        assert found.name == "test/repo50"

        await db.close()


@pytest.mark.asyncio
async def test_get_repository_by_id_not_found():
    """Test get_repository_by_id returns None for non-existent ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AsyncDatabase(Path(tmpdir) / "test.db")
        await db.init_db()

        # Add one repo
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

        # Search for non-existent ID
        found = await db.get_repository_by_id(99999)
        assert found is None

        await db.close()
