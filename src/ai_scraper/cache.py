"""Request caching for GitHub API."""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional


class RequestCache:
    """File-based cache for API responses."""

    def __init__(self, cache_dir: Path, ttl: int = 3600):
        """Initialize cache.

        Args:
            cache_dir: Directory for cache files.
            ttl: Time-to-live in seconds.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _get_cache_key(self, url: str, params: Optional[dict] = None) -> str:
        """Generate cache key from URL and params."""
        key_data = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        """Get cached response.

        Args:
            url: Request URL.
            params: Request parameters.

        Returns:
            Cached data or None.
        """
        key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)

            # Check TTL
            if time.time() - cached.get("timestamp", 0) > self.ttl:
                cache_file.unlink()
                return None

            return cached.get("data")
        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, url: str, params: Optional[dict], data: dict) -> None:
        """Cache response.

        Args:
            url: Request URL.
            params: Request parameters.
            data: Response data to cache.
        """
        key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.time(),
                "data": data,
            }, f)

    def clear(self) -> int:
        """Clear all cached data.

        Returns:
            Number of files deleted.
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    def get_stats(self) -> dict:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
        }
