"""Rate limiter for GitHub API."""

import time
import threading
from dataclasses import dataclass
from typing import Optional
from collections import deque


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""

    search_limit: int
    search_remaining: int
    search_reset: int
    core_limit: int = 0
    core_remaining: int = 0
    core_reset: int = 0


class RateLimiter:
    """Token bucket rate limiter with adaptive control."""

    def __init__(self, requests_per_hour: int = 60, safety_margin: float = 0.1):
        """Initialize rate limiter.

        Args:
            requests_per_hour: Maximum requests per hour.
            safety_margin: Fraction of requests to reserve.
        """
        self.requests_per_hour = requests_per_hour
        self.safety_margin = safety_margin
        self.effective_limit = int(requests_per_hour * (1 - safety_margin))
        self.refill_rate = self.effective_limit / 3600.0
        self.tokens = float(self.effective_limit)
        self.last_update = time.time()

        # Statistics
        self._total_requests = 0
        self._total_wait_time = 0.0
        self._request_history: deque = deque(maxlen=1000)
        self._lock = threading.RLock()

    def try_acquire(self) -> bool:
        """Try to acquire a token without blocking."""
        with self._lock:
            self._refill()

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                self._total_requests += 1
                self._request_history.append(time.time())
                return True

            return False

    def wait_time(self) -> float:
        """Get time to wait for next token."""
        with self._lock:
            self._refill()
            if self.tokens >= 1.0:
                return 0.0
            return (1.0 - self.tokens) / self.refill_rate

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire a token, blocking if necessary.

        Args:
            timeout: Maximum time to wait (None = forever).

        Returns:
            True if token acquired, False if timeout.
        """
        start_time = time.time()

        while True:
            if self.try_acquire():
                wait_duration = time.time() - start_time
                with self._lock:
                    self._total_wait_time += wait_duration
                return True

            wait = min(self.wait_time(), 0.1)

            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait > timeout:
                    return False

            time.sleep(wait)

    def set_rate(self, requests_per_hour: int) -> None:
        """Update the rate limit dynamically."""
        with self._lock:
            self.requests_per_hour = requests_per_hour
            self.effective_limit = int(requests_per_hour * (1 - self.safety_margin))
            self.refill_rate = self.effective_limit / 3600.0
            self.tokens = min(self.tokens, float(self.effective_limit))

    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "total_requests": self._total_requests,
                "total_wait_time": self._total_wait_time,
                "current_tokens": self.tokens,
                "effective_limit": self.effective_limit,
                "requests_per_hour": self.requests_per_hour,
            }

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            float(self.effective_limit),
            self.tokens + elapsed * self.refill_rate
        )
        self.last_update = now
