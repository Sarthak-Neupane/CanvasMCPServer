"""Tests for exception -> ToolError mapping."""

import pytest

from canvas_mcp_server.errors import (
    ErrorCode,
    as_tool_error,
    discussion_tool_error_from_http,
    tool_error_from_http,
)
from canvas_mcp_server.utils.http_client import HTTPError


@pytest.mark.parametrize(
    ("status_code", "code", "retryable"),
    [
        (400, ErrorCode.CANVAS_BAD_REQUEST, False),
        (401, ErrorCode.CANVAS_UNAUTHORIZED, False),
        (403, ErrorCode.CANVAS_FORBIDDEN, False),
        (404, ErrorCode.RESOURCE_NOT_FOUND, False),
        (429, ErrorCode.CANVAS_RATE_LIMITED, True),
        (503, ErrorCode.CANVAS_UNAVAILABLE, True),
    ],
)
def test_tool_error_from_http_status(
    status_code: int,
    code: ErrorCode,
    retryable: bool,
) -> None:
    error = HTTPError(
        f"HTTP {status_code} error",
        status_code=status_code,
        response_data="body",
    )
    payload = tool_error_from_http(error, source="canvas_rest").to_response()

    assert payload["code"] == code.value
    assert payload["status_code"] == status_code
    assert payload["retryable"] is retryable


def test_tool_error_from_http_discussion_locked() -> None:
    error = HTTPError(
        "HTTP 403 error",
        status_code=403,
        response_data="require_initial_post",
    )
    payload = tool_error_from_http(error).to_response()

    assert payload["code"] == ErrorCode.DISCUSSION_LOCKED.value
    assert payload["lock_reason"] == "require_initial_post"


def test_discussion_tool_error_from_http_503() -> None:
    error = HTTPError("HTTP 503 error", status_code=503)
    payload = discussion_tool_error_from_http(error).to_response()

    assert payload["code"] == ErrorCode.DISCUSSION_UNAVAILABLE.value
    assert payload["retryable"] is True


def test_tool_error_from_http_503_is_canvas_unavailable() -> None:
    error = HTTPError("HTTP 503 error", status_code=503)
    payload = tool_error_from_http(error).to_response()

    assert payload["code"] == ErrorCode.CANVAS_UNAVAILABLE.value
    assert payload["retryable"] is True


def test_as_tool_error_from_value_error_download_url() -> None:
    payload = as_tool_error(
        ValueError("Download URL host 'evil.com' does not match CANVAS_BASE_URL"),
        source="download",
    )

    assert payload["code"] == ErrorCode.DOWNLOAD_URL_REJECTED.value
    assert payload["source"] == "download"


def test_as_tool_error_unexpected_response() -> None:
    payload = as_tool_error(
        Exception("Canvas discussion response was not an object"),
        source="canvas_rest",
    )

    assert payload["code"] == ErrorCode.UNEXPECTED_RESPONSE.value
