"""Tests for API authentication."""

import pytest
from ai_scraper.auth import (
    create_api_key,
    verify_api_key,
    hash_token,
    load_api_keys_from_env,
    clear_api_keys,
    get_valid_api_keys,
)


def test_create_api_key():
    """Test API key creation."""
    clear_api_keys()
    api_key = create_api_key()

    assert api_key.startswith("as_")
    assert len(api_key) == 35  # "as_" + 32 hex chars


def test_verify_api_key():
    """Test API key verification."""
    clear_api_keys()
    api_key = create_api_key()

    assert verify_api_key(api_key) is True
    assert verify_api_key("invalid_key") is False
    assert verify_api_key("") is False
    assert verify_api_key(None) is False


def test_hash_token():
    """Test token hashing."""
    token = "test_token_123"
    hashed = hash_token(token)

    assert hashed != token
    assert len(hashed) == 64  # SHA256 hex digest


def test_load_api_keys_from_env():
    """Test loading API keys from environment."""
    import os

    clear_api_keys()
    os.environ["AI_SCRAPER_API_KEYS"] = "as_key1,as_key2"

    load_api_keys_from_env()

    keys = get_valid_api_keys()
    assert "as_key1" in keys
    assert "as_key2" in keys

    # Cleanup
    del os.environ["AI_SCRAPER_API_KEYS"]
    clear_api_keys()


def test_multiple_api_keys():
    """Test multiple API keys."""
    clear_api_keys()

    key1 = create_api_key()
    key2 = create_api_key()

    assert key1 != key2
    assert verify_api_key(key1) is True
    assert verify_api_key(key2) is True


def test_clear_api_keys():
    """Test clearing API keys."""
    create_api_key()
    create_api_key()

    assert len(get_valid_api_keys()) >= 2

    clear_api_keys()

    assert len(get_valid_api_keys()) == 0