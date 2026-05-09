"""Tests for GitHub API client."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_scraper.api.github import GitHubClient, GitHubAPIError
from ai_scraper.api.rate_limiter import RateLimiter


@pytest.fixture
def mock_response():
    """Create mock aiohttp response."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock()
    return response


@pytest.fixture
def mock_session(mock_response):
    """Create mock aiohttp session."""
    # Create a proper async context manager mock
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_response
    async_context_manager.__aexit__.return_value = None

    session = MagicMock()
    session.get.return_value = async_context_manager
    session.closed = False
    session.close = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_search_repositories(mock_response, mock_session):
    """Test repository search."""
    mock_response.json.return_value = {
        "items": [
            {
                "id": 123,
                "name": "repo",
                "full_name": "owner/repo",
                "description": "Test repo",
                "stargazers_count": 1000,
                "language": "Python",
                "topics": ["ai"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-05-01T00:00:00Z",
                "pushed_at": "2024-05-09T00:00:00Z",
                "html_url": "https://github.com/owner/repo",
            }
        ]
    }

    with patch("ai_scraper.api.github.aiohttp.ClientSession") as mock_client_session:
        mock_client_session.return_value = mock_session
        mock_client_session.return_value.headers = {}

        client = GitHubClient()
        repos = await client.search_repositories("ai", sort="stars", order="desc")

        assert len(repos) == 1
        assert repos[0].name == "owner/repo"
        assert repos[0].stars == 1000

        await client.close()


@pytest.mark.asyncio
async def test_get_rate_limit(mock_response, mock_session):
    """Test getting rate limit info."""
    mock_response.json.return_value = {
        "resources": {
            "search": {
                "limit": 30,
                "remaining": 25,
                "reset": 1715234400,
            },
            "core": {
                "limit": 5000,
                "remaining": 4999,
                "reset": 1715234400,
            }
        }
    }

    with patch("ai_scraper.api.github.aiohttp.ClientSession") as mock_client_session:
        mock_client_session.return_value = mock_session
        mock_client_session.return_value.headers = {}

        client = GitHubClient()
        info = await client.get_rate_limit()

        assert info.search_limit == 30
        assert info.search_remaining == 25

        await client.close()


def test_rate_limiter_basic():
    """Test basic rate limiter functionality."""
    # Use a very low rate to test blocking
    limiter = RateLimiter(requests_per_hour=60)

    # Drain the bucket to test blocking
    limiter.tokens = 1.0  # Set to exactly 1 token

    # Should allow first request
    assert limiter.try_acquire() is True

    # Now tokens should be 0, should block
    assert limiter.try_acquire() is False


def test_rate_limiter_with_token():
    """Test rate limiter with higher limit."""
    limiter = RateLimiter(requests_per_hour=5000)

    # Should allow multiple requests (effective limit is 4500 with 10% margin)
    for _ in range(10):
        assert limiter.try_acquire() is True

    # Verify tokens decreased
    assert limiter.tokens < limiter.effective_limit


def test_rate_limiter_refill():
    """Test rate limiter token refill."""
    limiter = RateLimiter(requests_per_hour=3600)  # 1 per second

    # Drain the bucket
    limiter.tokens = 0.0

    # Should not allow immediately
    assert limiter.try_acquire() is False

    # Simulate time passing (manually set tokens)
    limiter.tokens = 1.0

    # Should allow now
    assert limiter.try_acquire() is True


@pytest.mark.asyncio
async def test_github_api_error():
    """Test GitHub API error handling."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value="Unauthorized")

    # Create a proper async context manager mock
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_response
    async_context_manager.__aexit__.return_value = None

    mock_session = MagicMock()
    mock_session.get.return_value = async_context_manager
    mock_session.closed = False
    mock_session.close = AsyncMock()

    with patch("ai_scraper.api.github.aiohttp.ClientSession") as mock_client_session:
        mock_client_session.return_value = mock_session
        mock_client_session.return_value.headers = {}

        client = GitHubClient()

        with pytest.raises(GitHubAPIError) as exc_info:
            await client.search_repositories("ai")

        assert exc_info.value.status == 401

        await client.close()
