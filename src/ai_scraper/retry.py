"""Retry logic with exponential backoff."""

import asyncio
import functools
import logging
import random
from typing import Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handle retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (
            ConnectionError,
            TimeoutError,
        ),
    ):
        """Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts.
            base_delay: Initial delay in seconds.
            exponential_base: Base for exponential backoff.
            max_delay: Maximum delay in seconds.
            jitter: Add random jitter to delays.
            retryable_exceptions: Exceptions that trigger retry.
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add up to 25% jitter
            delay = delay * (1 + random.random() * 0.25)

        return delay

    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs,
    ):
        """Execute a function with retry logic.

        Args:
            func: Async function to execute.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            Result of the function.

        Raises:
            Last exception after all retries exhausted.
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retries exhausted")

        raise last_exception


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
    ),
):
    """Decorator for retry logic.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        exponential_base: Base for exponential backoff.
        max_delay: Maximum delay in seconds.
        jitter: Add random jitter to delays.
        retryable_exceptions: Exceptions that trigger retry.

    Returns:
        Decorated function.
    """
    handler = RetryHandler(
        max_retries=max_retries,
        base_delay=base_delay,
        exponential_base=exponential_base,
        max_delay=max_delay,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await handler.execute(func, *args, **kwargs)

        return wrapper

    return decorator
