"""Tests for RequestCache."""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_scraper.cache import RequestCache


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory."""
    return tmp_path / "cache"


@pytest.fixture
def cache(temp_cache_dir):
    """Create a RequestCache instance."""
    return RequestCache(cache_dir=temp_cache_dir, ttl=3600)


def test_get_returns_none_for_missing_key(cache):
    """Test get returns None for missing key."""
    result = cache.get("https://api.github.com/test", {"page": 1})
    assert result is None


def test_set_and_get_work_correctly(cache):
    """Test set and get work correctly."""
    url = "https://api.github.com/repos/test/repo"
    params = {"per_page": 100}
    data = {"id": 123, "name": "test/repo", "stars": 1000}

    # Set the cache
    cache.set(url, params, data)

    # Get from cache
    result = cache.get(url, params)

    assert result is not None
    assert result["id"] == 123
    assert result["name"] == "test/repo"
    assert result["stars"] == 1000


def test_cache_key_is_consistent(cache):
    """Test that cache key is consistent for same URL and params."""
    url = "https://api.github.com/test"
    params = {"q": "ai", "sort": "stars"}

    cache.set(url, params, {"result": "data1"})
    result = cache.get(url, params)

    assert result == {"result": "data1"}


def test_different_params_different_cache(cache):
    """Test that different params result in different cache entries."""
    url = "https://api.github.com/search/repositories"

    cache.set(url, {"q": "python"}, {"items": ["python"]})
    cache.set(url, {"q": "javascript"}, {"items": ["javascript"]})

    result_python = cache.get(url, {"q": "python"})
    result_js = cache.get(url, {"q": "javascript"})

    assert result_python["items"] == ["python"]
    assert result_js["items"] == ["javascript"]


def test_set_without_params(cache):
    """Test set and get without params."""
    url = "https://api.github.com/rate_limit"
    data = {"resources": {"core": {"limit": 5000}}}

    cache.set(url, None, data)
    result = cache.get(url, None)

    assert result == data


def test_ttl_expiration(temp_cache_dir):
    """Test TTL expiration."""
    # Create cache with 1 second TTL
    short_cache = RequestCache(cache_dir=temp_cache_dir, ttl=1)

    url = "https://api.github.com/test"
    data = {"test": "data"}

    short_cache.set(url, None, data)

    # Should be available immediately
    assert short_cache.get(url, None) == data

    # Wait for TTL to expire
    time.sleep(1.5)

    # Should return None after expiration
    result = short_cache.get(url, None)
    assert result is None


def test_ttl_expired_file_deleted(temp_cache_dir):
    """Test that expired cache files are deleted."""
    short_cache = RequestCache(cache_dir=temp_cache_dir, ttl=1)

    url = "https://api.github.com/test"
    short_cache.set(url, None, {"data": "test"})

    # Verify file exists
    cache_files = list(temp_cache_dir.glob("*.json"))
    assert len(cache_files) == 1

    # Wait for expiration and access
    time.sleep(1.5)
    short_cache.get(url, None)

    # File should be deleted
    cache_files = list(temp_cache_dir.glob("*.json"))
    assert len(cache_files) == 0


def test_clear_removes_all_files(cache, temp_cache_dir):
    """Test clear removes all cache files."""
    # Create multiple cache entries
    cache.set("https://api.github.com/test1", None, {"data": 1})
    cache.set("https://api.github.com/test2", None, {"data": 2})
    cache.set("https://api.github.com/test3", {"page": 1}, {"data": 3})

    # Verify files exist
    assert len(list(temp_cache_dir.glob("*.json"))) == 3

    # Clear cache
    count = cache.clear()

    assert count == 3
    assert len(list(temp_cache_dir.glob("*.json"))) == 0


def test_clear_empty_cache(cache, temp_cache_dir):
    """Test clear on empty cache returns 0."""
    count = cache.clear()
    assert count == 0


def test_get_stats_empty_cache(cache):
    """Test get_stats on empty cache."""
    stats = cache.get_stats()

    assert stats["file_count"] == 0
    assert stats["total_size_bytes"] == 0
    assert stats["total_size_mb"] == 0.0


def test_get_stats_with_files(cache):
    """Test get_stats returns correct info."""
    # Create some cache entries
    cache.set("https://api.github.com/test1", None, {"data": "x" * 100})
    cache.set("https://api.github.com/test2", None, {"data": "y" * 200})

    stats = cache.get_stats()

    assert stats["file_count"] == 2
    assert stats["total_size_bytes"] > 0
    # total_size_mb may be 0.0 for small files, just check it's a float
    assert isinstance(stats["total_size_mb"], float)


def test_corrupted_cache_file_returns_none(cache, temp_cache_dir):
    """Test that corrupted cache file returns None."""
    url = "https://api.github.com/test"

    # Create a corrupted cache file manually
    key = cache._get_cache_key(url, None)
    cache_file = temp_cache_dir / f"{key}.json"

    with open(cache_file, "w") as f:
        f.write("not valid json {{{")

    result = cache.get(url, None)
    assert result is None


def test_cache_file_without_timestamp_returns_none(cache, temp_cache_dir):
    """Test cache file without timestamp returns None."""
    url = "https://api.github.com/test"

    # Create cache file without timestamp
    key = cache._get_cache_key(url, None)
    cache_file = temp_cache_dir / f"{key}.json"

    with open(cache_file, "w") as f:
        json.dump({"data": {"test": "value"}}, f)

    result = cache.get(url, None)
    assert result is None


def test_cache_dir_created_if_not_exists(tmp_path):
    """Test that cache directory is created if it doesn't exist."""
    cache_dir = tmp_path / "new_cache_dir"

    # Directory shouldn't exist yet
    assert not cache_dir.exists()

    # Creating cache should create directory
    cache = RequestCache(cache_dir=cache_dir)

    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_cache_key_order_independence(cache):
    """Test that cache key is independent of param order."""
    url = "https://api.github.com/search"

    # Same params in different order
    cache.set(url, {"a": 1, "b": 2}, {"result": "data"})

    # Should get same result regardless of order
    result = cache.get(url, {"b": 2, "a": 1})

    assert result == {"result": "data"}
