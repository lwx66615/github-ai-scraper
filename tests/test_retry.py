"""Tests for retry logic."""

import pytest
import asyncio
from ai_scraper.retry import RetryHandler, with_retry


@pytest.mark.asyncio
async def test_retry_on_transient_error():
    """Test retry on transient errors."""
    handler = RetryHandler(max_retries=3, base_delay=0.1)

    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    result = await handler.execute(failing_func)

    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_exhausted():
    """Test that retry raises after max retries."""
    handler = RetryHandler(max_retries=2, base_delay=0.1)

    async def always_fail():
        raise ConnectionError("Always fails")

    with pytest.raises(ConnectionError):
        await handler.execute(always_fail)


@pytest.mark.asyncio
async def test_retry_with_decorator():
    """Test retry decorator."""

    call_count = 0

    @with_retry(max_retries=3, base_delay=0.1)
    async def decorated_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise TimeoutError("Timeout")
        return "ok"

    result = await decorated_func()
    assert result == "ok"
    assert call_count == 2


@pytest.mark.asyncio
async def test_exponential_backoff():
    """Test exponential backoff delays."""
    import time

    handler = RetryHandler(max_retries=3, base_delay=0.1, exponential_base=2, jitter=False)

    call_count = 0
    start_time = time.time()

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("fail")
        return "success"

    await handler.execute(failing_func)

    elapsed = time.time() - start_time
    # Should have waited at least 0.1 + 0.2 = 0.3 seconds
    assert elapsed >= 0.25


@pytest.mark.asyncio
async def test_non_retryable_exception():
    """Test that non-retryable exceptions are not retried."""
    handler = RetryHandler(max_retries=3, base_delay=0.1)

    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Not retryable")

    with pytest.raises(ValueError):
        await handler.execute(failing_func)

    # Should not retry
    assert call_count == 1


@pytest.mark.asyncio
async def test_custom_retryable_exceptions():
    """Test custom retryable exceptions."""
    handler = RetryHandler(
        max_retries=2,
        base_delay=0.1,
        retryable_exceptions=(ValueError,),
    )

    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Retry this")
        return "success"

    result = await handler.execute(failing_func)
    assert result == "success"


@pytest.mark.asyncio
async def test_max_delay_cap():
    """Test that delay is capped at max_delay."""
    handler = RetryHandler(max_retries=5, base_delay=10, max_delay=1.0, jitter=False)

    # All delays should be capped at 1.0
    for attempt in range(5):
        delay = handler._calculate_delay(attempt)
        assert delay <= 1.0
