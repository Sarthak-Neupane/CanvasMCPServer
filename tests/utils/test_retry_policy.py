"""Unit tests for HTTP retry policy helpers."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from canvas_mcp_server.utils.retry_policy import (
    compute_retry_delay,
    parse_retry_after,
    should_retry_status,
    sleep_before_retry,
)


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (400, False),
        (401, False),
        (403, False),
        (404, False),
        (429, True),
        (500, True),
        (502, True),
        (503, True),
        (200, False),
        (418, False),
    ],
)
def test_should_retry_status(status_code: int, expected: bool) -> None:
    assert should_retry_status(status_code) is expected


def test_parse_retry_after_seconds() -> None:
    assert parse_retry_after("2.5") == 2.5
    assert parse_retry_after("0") == 0.0


def test_parse_retry_after_http_date() -> None:
    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    header_value = future.strftime("%a, %d %b %Y %H:%M:%S GMT")
    delay = parse_retry_after(header_value)
    assert delay is not None
    assert 25 <= delay <= 35


def test_parse_retry_after_invalid() -> None:
    assert parse_retry_after(None) is None
    assert parse_retry_after("not-a-date") is None


def test_compute_retry_delay_exponential() -> None:
    assert compute_retry_delay(0, None, base_delay=1.0) == 1.0
    assert compute_retry_delay(1, None, base_delay=1.0) == 2.0
    assert compute_retry_delay(2, None, base_delay=1.0) == 4.0


def test_compute_retry_delay_honors_retry_after() -> None:
    delay = compute_retry_delay(0, "10", base_delay=1.0)
    assert delay == 10.0


async def test_sleep_before_retry_skips_zero_delay() -> None:
    with patch(
        "canvas_mcp_server.utils.retry_policy.asyncio.sleep",
        new_callable=AsyncMock,
    ) as mock_sleep:
        await sleep_before_retry(0)
    mock_sleep.assert_not_called()

    with patch(
        "canvas_mcp_server.utils.retry_policy.asyncio.sleep",
        new_callable=AsyncMock,
    ) as mock_sleep:
        await sleep_before_retry(0.5)
    mock_sleep.assert_awaited_once_with(0.5)
