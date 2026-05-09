"""Rate limiter for GitHub API."""

import time
from dataclasses import dataclass


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
    """Token bucket rate limiter."""

    def __init__(self, requests_per_hour: int = 60, safety_margin: float = 0.1):
        """Initialize rate limiter.

        Args:
            requests_per_hour: Maximum requests per hour.
            safety_margin: Fraction of requests to reserve (default 10%).
        """
        self.requests_per_hour = requests_per_hour
        self.safety_margin = safety_margin
        self.effective_limit = int(requests_per_hour * (1 - safety_margin))

        # Calculate refill rate (requests per second)
        self.refill_rate = self.effective_limit / 3600.0

        # Token bucket state
        self.tokens = float(self.effective_limit)
        self.last_update = time.time()

    def try_acquire(self) -> bool:
        """Try to acquire a token without blocking.

        Returns:
            True if token was acquired, False otherwise.
        """
        self._refill()

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True

        return False

    def wait_time(self) -> float:
        """Get time to wait for next token.

        Returns:
            Seconds to wait.
        """
        self._refill()

        if self.tokens >= 1.0:
            return 0.0

        return (1.0 - self.tokens) / self.refill_rate

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update

        self.tokens = min(
            float(self.effective_limit),
            self.tokens + elapsed * self.refill_rate
        )
        self.last_update = now

    def set_rate(self, requests_per_hour: int) -> None:
        """Update the rate limit.

        Args:
            requests_per_hour: New maximum requests per hour.
        """
        self.requests_per_hour = requests_per_hour
        self.effective_limit = int(requests_per_hour * (1 - self.safety_margin))
        self.refill_rate = self.effective_limit / 3600.0
        self.tokens = min(self.tokens, float(self.effective_limit))
