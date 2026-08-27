"""Map exceptions and Canvas failures to :class:`ToolError`."""

from __future__ import annotations

from typing import Any, Optional

from ..utils.http_client import HTTPError
from ..utils.retry_policy import should_retry_status
from .codes import ErrorCode
from .tool_error import ErrorSource, ToolError, tool_error


def _discussion_error_from_http(error: HTTPError) -> Optional[ToolError]:
    """Map Canvas discussion-specific HTTP failures."""
    if error.status_code == 403:
        body = error.response_data
        if body == "require_initial_post" or (
            isinstance(body, str) and "require_initial_post" in body
        ):
            return tool_error(
                ErrorCode.DISCUSSION_LOCKED,
                (
                    "You must post a reply before viewing other posts in this "
                    "discussion."
                ),
                status_code=403,
                source="canvas_rest",
                details={"lock_reason": "require_initial_post"},
            )
    return None


def discussion_tool_error_from_http(error: HTTPError) -> Optional[ToolError]:
    """Map discussion-only HTTP failures (including view-build 503)."""
    mapped = _discussion_error_from_http(error)
    if mapped is not None:
        return mapped
    if error.status_code == 503:
        return tool_error(
            ErrorCode.DISCUSSION_UNAVAILABLE,
            "Canvas has not built the discussion view yet. Retry in a moment.",
            status_code=503,
            source="canvas_rest",
        )
    return None


def as_discussion_tool_error(
    error: BaseException,
    *,
    source: ErrorSource = "canvas_rest",
) -> dict[str, Any]:
    """Serialize discussion tool exceptions, including domain-specific HTTP codes."""
    if isinstance(error, HTTPError):
        mapped = discussion_tool_error_from_http(error)
        if mapped is not None:
            return mapped.to_response()
    return as_tool_error(error, source=source)


def _code_for_http_status(status_code: int) -> ErrorCode:
    if status_code == 400:
        return ErrorCode.CANVAS_BAD_REQUEST
    if status_code == 401:
        return ErrorCode.CANVAS_UNAUTHORIZED
    if status_code == 403:
        return ErrorCode.CANVAS_FORBIDDEN
    if status_code == 404:
        return ErrorCode.RESOURCE_NOT_FOUND
    if status_code == 429:
        return ErrorCode.CANVAS_RATE_LIMITED
    if 500 <= status_code < 600:
        return ErrorCode.CANVAS_UNAVAILABLE
    return ErrorCode.UNEXPECTED_ERROR


def tool_error_from_http(
    error: HTTPError,
    *,
    source: Optional[ErrorSource] = None,
) -> ToolError:
    """Convert an :class:`HTTPError` from the Canvas client into a :class:`ToolError`."""
    discussion_error = _discussion_error_from_http(error)
    if discussion_error is not None:
        return discussion_error

    message = str(error)
    status_code = error.status_code

    if status_code is not None and "GraphQL error" in message:
        return tool_error(
            ErrorCode.GRAPHQL_ERROR,
            message,
            status_code=status_code,
            source=source or "canvas_graphql",
        )

    if status_code is not None and "timeout" in message.lower():
        return tool_error(
            ErrorCode.REQUEST_TIMEOUT,
            message,
            status_code=status_code,
            source=source,
        )

    if status_code is not None and message.lower().startswith("network error"):
        return tool_error(
            ErrorCode.NETWORK_ERROR,
            message,
            status_code=status_code,
            source=source,
        )

    if status_code is not None:
        code = _code_for_http_status(status_code)
        retryable = should_retry_status(status_code)
        return tool_error(
            code,
            message,
            status_code=status_code,
            retryable=retryable,
            source=source,
        )

    if "GraphQL error" in message:
        return tool_error(
            ErrorCode.GRAPHQL_ERROR,
            message,
            source=source or "canvas_graphql",
        )
    if "timeout" in message.lower():
        return tool_error(
            ErrorCode.REQUEST_TIMEOUT,
            message,
            source=source,
        )
    if message.lower().startswith("network error"):
        return tool_error(
            ErrorCode.NETWORK_ERROR,
            message,
            source=source,
        )

    return tool_error(
        ErrorCode.UNEXPECTED_ERROR,
        message,
        source=source,
    )


def tool_error_from_value_error(
    error: ValueError,
    *,
    source: ErrorSource = "local",
) -> ToolError:
    """Map local validation failures to :class:`ToolError`."""
    message = str(error)
    code = ErrorCode.INVALID_ARGUMENT
    lowered = message.lower()

    if "download url" in lowered or "canvas_base_url" in lowered:
        code = ErrorCode.DOWNLOAD_URL_REJECTED
    elif "exceeds maximum download size" in lowered or "download limit" in lowered:
        code = ErrorCode.DOWNLOAD_TOO_LARGE
    elif "required" in lowered and (
        "canvas_api_token" in lowered or "canvas_base_url" in lowered
    ):
        code = ErrorCode.CONFIG_MISSING

    return tool_error(code, message, source=source)


def tool_error_from_exception(
    error: BaseException,
    *,
    source: Optional[ErrorSource] = None,
) -> ToolError:
    """Map any exception raised inside a tool to :class:`ToolError`."""
    if isinstance(error, HTTPError):
        return tool_error_from_http(error, source=source)
    if isinstance(error, ValueError):
        return tool_error_from_value_error(error, source=source or "local")

    message = str(error)
    lowered = message.lower()
    if "response was not" in lowered or "not a dictionary" in lowered:
        return tool_error(
            ErrorCode.UNEXPECTED_RESPONSE,
            message,
            source=source,
        )
    if "no course found" in lowered or "not found for id" in lowered:
        return tool_error(
            ErrorCode.RESOURCE_NOT_FOUND,
            message,
            source=source,
        )

    return tool_error(
        ErrorCode.UNEXPECTED_ERROR,
        message,
        source=source,
    )


def as_tool_error(
    error: BaseException,
    *,
    source: Optional[ErrorSource] = None,
) -> dict[str, Any]:
    """Serialize any tool exception as an MCP error response dict."""
    return tool_error_from_exception(error, source=source).to_response()
