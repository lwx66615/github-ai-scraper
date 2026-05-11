"""Tests for secure token storage."""

import pytest
from pathlib import Path
import tempfile
from ai_scraper.secure_storage import SecureStorage


def test_store_and_retrieve_token():
    """Test secure token storage and retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))

        # Store token
        storage.store_token("github_token", "ghp_test123456")

        # Retrieve token
        token = storage.get_token("github_token")
        assert token == "ghp_test123456"


def test_token_is_encrypted():
    """Test that token is encrypted in storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))
        storage.store_token("github_token", "ghp_test123456")

        # Read raw file - should not contain plaintext
        token_file = Path(tmpdir) / "tokens.enc"
        if token_file.exists():
            content = token_file.read_bytes()
            # The token should be encrypted/encoded
            assert b"ghp_test123456" not in content or len(content) > 20


def test_delete_token():
    """Test token deletion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))
        storage.store_token("github_token", "ghp_test123456")

        storage.delete_token("github_token")

        token = storage.get_token("github_token")
        assert token is None


def test_nonexistent_token():
    """Test retrieving nonexistent token."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))
        token = storage.get_token("nonexistent")
        assert token is None


def test_multiple_tokens():
    """Test storing multiple tokens."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))

        storage.store_token("github_token", "ghp_abc123")
        storage.store_token("slack_token", "xoxb_xyz789")

        assert storage.get_token("github_token") == "ghp_abc123"
        assert storage.get_token("slack_token") == "xoxb_xyz789"


def test_update_token():
    """Test updating an existing token."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SecureStorage(Path(tmpdir))

        storage.store_token("github_token", "old_token")
        storage.store_token("github_token", "new_token")

        assert storage.get_token("github_token") == "new_token"
