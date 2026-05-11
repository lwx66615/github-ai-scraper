"""API authentication module."""

import hashlib
import os
import secrets
from typing import Optional


# In-memory store for API keys (in production, use secure storage)
_api_keys: set[str] = set()


def create_api_key() -> str:
    """Generate a new API key.

    Returns:
        API key string starting with 'as_'.
    """
    key = secrets.token_hex(16)
    api_key = f"as_{key}"
    _api_keys.add(api_key)
    return api_key


def verify_api_key(api_key: Optional[str]) -> bool:
    """Verify an API key.

    Args:
        api_key: API key to verify.

    Returns:
        True if valid, False otherwise.
    """
    if not api_key:
        return False
    return api_key in _api_keys


def hash_token(token: str) -> str:
    """Hash a token for secure storage.

    Args:
        token: Token to hash.

    Returns:
        Hashed token.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def load_api_keys_from_env() -> None:
    """Load API keys from environment variable."""
    env_keys = os.environ.get("AI_SCRAPER_API_KEYS", "")
    if env_keys:
        for key in env_keys.split(","):
            key = key.strip()
            if key:
                _api_keys.add(key)


def get_valid_api_keys() -> set[str]:
    """Get all valid API keys (for testing)."""
    return _api_keys.copy()


def clear_api_keys() -> None:
    """Clear all API keys (for testing)."""
    _api_keys.clear()
