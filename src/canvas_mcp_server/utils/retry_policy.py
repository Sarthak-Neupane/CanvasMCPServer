"""Retry helpers for transient Canvas HTTP failures."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional


DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_DELAY_SECONDS = 1.0


def should_retry_status(status_code: int) -> bool:
    """Return True for rate limits and server errors; never for 400/401/403/404."""
    if status_code in (400, 401, 403, 404):
        return False
    return status_code == 429 or 500 <= status_code < 600


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parse a Retry-After header value into seconds to wait."""
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError, OverflowError):
        return None


def compute_retry_delay(
    attempt: int,
    retry_after: Optional[str],
    *,
    base_delay: float = DEFAULT_RETRY_BASE_DELAY_SECONDS,
) -> float:
    """
    Compute delay before the next retry attempt.

    Uses exponential backoff and honors Retry-After when Canvas sends it.
    """
    backoff = base_delay * (2**attempt)
    header_delay = parse_retry_after(retry_after)
    if header_delay is not None:
        return max(backoff, header_delay)
    return backoff


async def sleep_before_retry(delay_seconds: float) -> None:
    """Pause between retry attempts."""
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
