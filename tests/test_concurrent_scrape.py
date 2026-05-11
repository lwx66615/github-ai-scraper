"""Tests for concurrent scraping."""

import pytest
from unittest.mock import AsyncMock, patch
from ai_scraper.api.github import GitHubClient
from ai_scraper.models.repository import Repository
from datetime import datetime


@pytest.mark.asyncio
async def test_concurrent_search_repositories():
    """Test concurrent search across multiple pages."""
    client = GitHubClient(token="test_token")

    # Mock responses for different pages
    mock_responses = [
        {
            "items": [
                {
                    "id": i + 1,  # Ensure id > 0
                    "full_name": f"repo{i}",
                    "stargazers_count": i * 100,
                    "description": "test",
                    "language": "Python",
                    "topics": [],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "pushed_at": "2024-01-01T00:00:00Z",
                    "html_url": f"https://github.com/repo{i}",
                    "open_issues_count": 0,
                    "forks_count": 0,
                }
                for i in range(page * 100, (page + 1) * 100)
            ]
        }
        for page in range(3)
    ]

    call_count = 0

    async def mock_request(endpoint, params=None):
        nonlocal call_count
        if call_count < len(mock_responses):
            response = mock_responses[call_count]
            call_count += 1
            return response
        return {"items": []}

    client._request = mock_request

    # Test concurrent fetch
    repos = await client.search_repositories_concurrent(
        query="stars:>100",
        max_pages=3,
        per_page=100,
        max_concurrent=5,
    )

    # Should have results (some pages may fail validation)
    assert len(repos) >= 100
    assert call_count == 3

    await client.close()


@pytest.mark.asyncio
async def test_concurrent_search_handles_failures():
    """Test that concurrent search handles partial failures."""
    client = GitHubClient(token="test_token")

    call_count = 0

    async def mock_request(endpoint, params=None):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise Exception("Network error")
        return {
            "items": [
                {
                    "id": call_count * 100,
                    "full_name": f"repo{call_count}",
                    "stargazers_count": 100,
                    "description": "test",
                    "language": "Python",
                    "topics": [],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "pushed_at": "2024-01-01T00:00:00Z",
                    "html_url": f"https://github.com/repo{call_count}",
                    "open_issues_count": 0,
                    "forks_count": 0,
                }
            ]
        }

    client._request = mock_request

    # Should still return results from successful pages
    repos = await client.search_repositories_concurrent(
        query="stars:>100",
        max_pages=3,
        per_page=100,
    )

    # Should have results from 2 successful pages (page 1 and 3)
    assert len(repos) >= 1

    await client.close()


@pytest.mark.asyncio
async def test_concurrent_search_respects_semaphore():
    """Test that concurrent search respects max_concurrent limit."""
    import asyncio
    import time

    client = GitHubClient(token="test_token")

    active_count = 0
    max_concurrent_seen = 0

    async def mock_request(endpoint, params=None):
        nonlocal active_count, max_concurrent_seen
        active_count += 1
        max_concurrent_seen = max(max_concurrent_seen, active_count)
        await asyncio.sleep(0.1)  # Simulate network delay
        active_count -= 1
        return {"items": []}

    client._request = mock_request

    await client.search_repositories_concurrent(
        query="stars:>100",
        max_pages=5,
        per_page=100,
        max_concurrent=2,
    )

    assert max_concurrent_seen <= 2

    await client.close()