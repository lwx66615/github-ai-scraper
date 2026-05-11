"""Tests for connection pool management."""

import pytest
from ai_scraper.api.github import GitHubClient


@pytest.mark.asyncio
async def test_session_reuse():
    """Test that aiohttp session is reused across requests."""
    client = GitHubClient(token="test_token")

    # Get session twice
    session1 = await client._get_session()
    session2 = await client._get_session()

    assert session1 is session2

    await client.close()


@pytest.mark.asyncio
async def test_session_closed_after_close():
    """Test that session is properly closed."""
    client = GitHubClient(token="test_token")
    session = await client._get_session()

    await client.close()

    assert session.closed


@pytest.mark.asyncio
async def test_multiple_clients_have_separate_sessions():
    """Test that different clients have separate sessions."""
    client1 = GitHubClient(token="token1")
    client2 = GitHubClient(token="token2")

    session1 = await client1._get_session()
    session2 = await client2._get_session()

    assert session1 is not session2

    await client1.close()
    await client2.close()


@pytest.mark.asyncio
async def test_connection_pool_size():
    """Test that connection pool size is configured."""
    client = GitHubClient(token="test_token", connection_pool_size=20)

    session = await client._get_session()

    # Check connector is configured
    assert session.connector is not None
    assert session.connector.limit == 20

    await client.close()


@pytest.mark.asyncio
async def test_session_timeout_configured():
    """Test that session timeout is configured."""
    client = GitHubClient(token="test_token")

    session = await client._get_session()

    # Check timeout is configured
    assert session.timeout is not None
    assert session.timeout.total == 30

    await client.close()
