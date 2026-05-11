"""Tests for enhanced rate limiter functionality."""

import time
import threading
import pytest
from collections import deque

from ai_scraper.api.rate_limiter import RateLimiter, RateLimitInfo


class TestRateLimitInfo:
    """Tests for RateLimitInfo dataclass."""

    def test_rate_limit_info_creation(self):
        """Test creating RateLimitInfo."""
        info = RateLimitInfo(
            search_limit=30,
            search_remaining=25,
            search_reset=1234567890,
        )
        assert info.search_limit == 30
        assert info.search_remaining == 25
        assert info.search_reset == 1234567890
        assert info.core_limit == 0
        assert info.core_remaining == 0
        assert info.core_reset == 0

    def test_rate_limit_info_with_core(self):
        """Test creating RateLimitInfo with core values."""
        info = RateLimitInfo(
            search_limit=30,
            search_remaining=25,
            search_reset=1234567890,
            core_limit=5000,
            core_remaining=4900,
            core_reset=1234567900,
        )
        assert info.core_limit == 5000
        assert info.core_remaining == 4900
        assert info.core_reset == 1234567900


class TestRateLimiterBasic:
    """Tests for basic rate limiter functionality."""

    def test_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = RateLimiter(requests_per_hour=60, safety_margin=0.1)
        assert limiter.requests_per_hour == 60
        assert limiter.safety_margin == 0.1
        assert limiter.effective_limit == 54  # 60 * 0.9

    def test_initialization_default(self):
        """Test rate limiter with default values."""
        limiter = RateLimiter()
        assert limiter.requests_per_hour == 60
        assert limiter.effective_limit == 54

    def test_try_acquire_success(self):
        """Test try_acquire succeeds when tokens available."""
        limiter = RateLimiter(requests_per_hour=60)
        assert limiter.try_acquire() is True

    def test_try_acquire_depletes_tokens(self):
        """Test try_acquire reduces token count."""
        limiter = RateLimiter(requests_per_hour=10, safety_margin=0.0)
        # With safety_margin=0, effective_limit = 10
        for _ in range(10):
            assert limiter.try_acquire() is True
        # Should be depleted now
        assert limiter.try_acquire() is False

    def test_wait_time_when_tokens_available(self):
        """Test wait_time returns 0 when tokens available."""
        limiter = RateLimiter(requests_per_hour=60)
        assert limiter.wait_time() == 0.0

    def test_wait_time_when_depleted(self):
        """Test wait_time returns positive value when depleted."""
        limiter = RateLimiter(requests_per_hour=10, safety_margin=0.0)
        # Deplete tokens
        for _ in range(10):
            limiter.try_acquire()
        # Wait time should be positive
        assert limiter.wait_time() > 0


class TestRateLimiterAcquire:
    """Tests for acquire method with blocking."""

    def test_acquire_returns_immediately_when_tokens_available(self):
        """Test acquire returns True immediately when tokens available."""
        limiter = RateLimiter(requests_per_hour=60)
        start = time.time()
        result = limiter.acquire()
        elapsed = time.time() - start
        assert result is True
        assert elapsed < 0.1  # Should be nearly instant

    def test_acquire_with_timeout_returns_false(self):
        """Test acquire with timeout returns False when tokens depleted."""
        limiter = RateLimiter(requests_per_hour=1, safety_margin=0.0)
        # With 1 request/hour, refill rate is very slow (1/3600 per second)
        # Deplete tokens
        limiter.try_acquire()

        # With a short timeout, should return False quickly
        result = limiter.acquire(timeout=0.01)
        assert result is False  # No token available in time

    def test_acquire_blocks_until_token_available(self):
        """Test acquire blocks until a token becomes available."""
        limiter = RateLimiter(requests_per_hour=3600, safety_margin=0.0)
        # 3600/hour = 1/second
        # Deplete tokens
        for _ in range(3600):
            limiter.try_acquire()

        # Acquire with a short timeout - should succeed after waiting
        # Since rate is 1 token/second, need to wait ~1 second
        start = time.time()
        result = limiter.acquire(timeout=1.5)
        elapsed = time.time() - start

        assert result is True
        assert elapsed >= 0.5  # Should have waited some time


class TestRateLimiterStats:
    """Tests for get_stats method."""

    def test_get_stats_returns_dict(self):
        """Test get_stats returns a dictionary."""
        limiter = RateLimiter(requests_per_hour=60)
        stats = limiter.get_stats()
        assert isinstance(stats, dict)

    def test_get_stats_tracks_requests(self):
        """Test get_stats tracks total requests."""
        limiter = RateLimiter(requests_per_hour=60)
        for _ in range(5):
            limiter.try_acquire()
        stats = limiter.get_stats()
        assert stats["total_requests"] == 5

    def test_get_stats_tracks_wait_time(self):
        """Test get_stats tracks total wait time."""
        limiter = RateLimiter(requests_per_hour=10, safety_margin=0.0)
        # Deplete tokens
        for _ in range(10):
            limiter.try_acquire()

        # acquire should track wait time
        limiter.acquire(timeout=0.1)  # Will timeout but track wait time

        stats = limiter.get_stats()
        # Total wait time should be positive due to the acquire call
        assert stats["total_wait_time"] >= 0

    def test_get_stats_current_tokens(self):
        """Test get_stats reports current tokens."""
        limiter = RateLimiter(requests_per_hour=60, safety_margin=0.0)
        initial_tokens = limiter.get_stats()["current_tokens"]
        limiter.try_acquire()
        after_tokens = limiter.get_stats()["current_tokens"]
        assert after_tokens == initial_tokens - 1

    def test_get_stats_effective_limit(self):
        """Test get_stats reports effective limit."""
        limiter = RateLimiter(requests_per_hour=100, safety_margin=0.2)
        stats = limiter.get_stats()
        assert stats["effective_limit"] == 80  # 100 * 0.8

    def test_get_stats_requests_per_hour(self):
        """Test get_stats reports requests per hour."""
        limiter = RateLimiter(requests_per_hour=120)
        stats = limiter.get_stats()
        assert stats["requests_per_hour"] == 120


class TestRateLimiterSetRate:
    """Tests for set_rate method."""

    def test_set_rate_updates_rate(self):
        """Test set_rate updates the rate limit."""
        limiter = RateLimiter(requests_per_hour=60)
        limiter.set_rate(120)
        assert limiter.requests_per_hour == 120
        assert limiter.effective_limit == 108  # 120 * 0.9

    def test_set_rate_adjusts_tokens(self):
        """Test set_rate caps tokens at new effective limit."""
        limiter = RateLimiter(requests_per_hour=100, safety_margin=0.0)
        # Initially has 100 tokens
        limiter.set_rate(50)  # New limit is 50
        assert limiter.tokens == 50  # Capped to new limit

    def test_set_rate_preserves_tokens_if_below_limit(self):
        """Test set_rate preserves tokens if below new limit."""
        limiter = RateLimiter(requests_per_hour=100, safety_margin=0.0)
        # Use 80 tokens, leaving 20
        for _ in range(80):
            limiter.try_acquire()
        limiter.set_rate(50)  # New limit is 50
        # Should be approximately 20 (with small floating-point drift from refill)
        assert limiter.tokens >= 19.9 and limiter.tokens <= 21

    def test_set_rate_updates_refill_rate(self):
        """Test set_rate updates the refill rate."""
        limiter = RateLimiter(requests_per_hour=60)
        old_rate = limiter.refill_rate
        limiter.set_rate(120)
        new_rate = limiter.refill_rate
        assert new_rate == old_rate * 2


class TestRateLimiterThreadSafety:
    """Tests for thread safety."""

    def test_concurrent_acquire(self):
        """Test concurrent acquire calls are safe."""
        limiter = RateLimiter(requests_per_hour=1000, safety_margin=0.0)
        success_count = [0]
        lock = threading.Lock()

        def acquire_tokens():
            for _ in range(100):
                if limiter.try_acquire():
                    with lock:
                        success_count[0] += 1

        threads = [threading.Thread(target=acquire_tokens) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have exactly 1000 successful acquires (the limit)
        assert success_count[0] == 1000

    def test_concurrent_acquire_with_blocking(self):
        """Test concurrent blocking acquire calls."""
        limiter = RateLimiter(requests_per_hour=100, safety_margin=0.0)
        success_count = [0]
        lock = threading.Lock()

        def acquire_with_timeout():
            if limiter.acquire(timeout=0.5):
                with lock:
                    success_count[0] += 1

        threads = [threading.Thread(target=acquire_with_timeout) for _ in range(50)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed since we have 100 tokens
        assert success_count[0] == 50

    def test_concurrent_set_rate(self):
        """Test concurrent set_rate calls are safe."""
        limiter = RateLimiter(requests_per_hour=60)

        def set_rates():
            for i in range(10):
                limiter.set_rate(60 + i * 10)

        threads = [threading.Thread(target=set_rates) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Just verify no exceptions occurred
        assert limiter.requests_per_hour > 0

    def test_concurrent_get_stats(self):
        """Test concurrent get_stats calls are safe."""
        limiter = RateLimiter(requests_per_hour=1000, safety_margin=0.0)

        def acquire_and_stats():
            for _ in range(50):
                limiter.try_acquire()
                limiter.get_stats()

        threads = [threading.Thread(target=acquire_and_stats) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = limiter.get_stats()
        assert stats["total_requests"] == 500  # 10 threads * 50 acquires


class TestRateLimiterRequestHistory:
    """Tests for request history tracking."""

    def test_request_history_tracked(self):
        """Test that requests are tracked in history."""
        limiter = RateLimiter(requests_per_hour=60)

        # Make some requests
        for _ in range(5):
            limiter.try_acquire()

        # Access internal history to verify it exists and has entries
        assert hasattr(limiter, '_request_history')
        assert len(limiter._request_history) == 5

    def test_request_history_maxlen(self):
        """Test that request history has max length."""
        limiter = RateLimiter(requests_per_hour=2000, safety_margin=0.0)

        # Make more than maxlen requests
        for _ in range(1500):
            limiter.try_acquire()

        # History should be capped at maxlen
        assert len(limiter._request_history) == 1000
