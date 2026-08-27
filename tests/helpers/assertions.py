"""Shared test assertions."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from canvas_mcp_server.errors import ErrorCode


def assert_tool_error(
    result: Any,
    code: Union[ErrorCode, str],
    *,
    status_code: Optional[int] = None,
    title: Optional[str] = None,
    retryable: Optional[bool] = None,
    message_contains: Optional[str] = None,
) -> Dict[str, Any]:
    """Assert that a tool returned a structured error payload."""
    assert isinstance(result, dict)
    expected_code = code.value if isinstance(code, ErrorCode) else code
    assert result["code"] == expected_code
    assert isinstance(result["message"], str)
    assert "title" in result
    assert result["error"] == result["title"]
    assert isinstance(result["retryable"], bool)
    if status_code is not None:
        assert result["status_code"] == status_code
    if title is not None:
        assert result["title"] == title
        assert result["error"] == title
    if retryable is not None:
        assert result["retryable"] is retryable
    if message_contains is not None:
        assert message_contains in result["message"]
    return result


def assert_http_error(result: Any, status_code: int) -> Dict[str, Any]:
    """Backward-compatible helper mapping HTTP status to canonical error codes."""
    code_by_status = {
        400: ErrorCode.CANVAS_BAD_REQUEST,
        401: ErrorCode.CANVAS_UNAUTHORIZED,
        403: ErrorCode.CANVAS_FORBIDDEN,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        429: ErrorCode.CANVAS_RATE_LIMITED,
    }
    if 500 <= status_code < 600:
        code = ErrorCode.CANVAS_UNAVAILABLE
    else:
        code = code_by_status.get(status_code, ErrorCode.UNEXPECTED_ERROR)
    retryable = status_code == 429 or 500 <= status_code < 600
    return assert_tool_error(
        result,
        code,
        status_code=status_code,
        retryable=retryable,
    )
