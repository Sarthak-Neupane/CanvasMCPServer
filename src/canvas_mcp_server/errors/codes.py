"""Stable machine-readable error codes for Canvas MCP tools."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Mapping


class ErrorCode(StrEnum):
    """Canonical error codes returned by MCP tools on failure."""

    # Local configuration
    CONFIG_MISSING = "config_missing"
    CONFIG_INVALID = "config_invalid"

    # Canvas authentication and authorization
    CANVAS_UNAUTHORIZED = "canvas_unauthorized"
    CANVAS_FORBIDDEN = "canvas_forbidden"

    # Caller input and Canvas client errors
    INVALID_ARGUMENT = "invalid_argument"
    INVALID_REQUEST = "invalid_request"
    RESOURCE_NOT_FOUND = "resource_not_found"
    CANVAS_BAD_REQUEST = "canvas_bad_request"

    # Canvas availability (often retryable)
    CANVAS_RATE_LIMITED = "canvas_rate_limited"
    CANVAS_UNAVAILABLE = "canvas_unavailable"

    # Transport-layer failures (retryable)
    REQUEST_TIMEOUT = "request_timeout"
    NETWORK_ERROR = "network_error"

    # API response handling
    GRAPHQL_ERROR = "graphql_error"
    UNEXPECTED_RESPONSE = "unexpected_response"
    UNEXPECTED_ERROR = "unexpected_error"

    # File downloads
    DOWNLOAD_FAILED = "download_failed"
    DOWNLOAD_TOO_LARGE = "download_too_large"
    DOWNLOAD_URL_REJECTED = "download_url_rejected"

    # Discussion-specific
    DISCUSSION_LOCKED = "discussion_locked"
    DISCUSSION_UNAVAILABLE = "discussion_unavailable"

    # Domain-specific not-found cases (HTTP 200 with empty payload)
    RUBRIC_NOT_FOUND = "rubric_not_found"


@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    """Metadata for one :class:`ErrorCode`."""

    title: str
    retryable: bool = False
    description: str = ""


ERROR_DEFINITIONS: Final[Mapping[ErrorCode, ErrorDefinition]] = {
    ErrorCode.CONFIG_MISSING: ErrorDefinition(
        title="Configuration Error",
        description="Required environment variables are missing.",
    ),
    ErrorCode.CONFIG_INVALID: ErrorDefinition(
        title="Configuration Error",
        description="Environment variables are present but invalid.",
    ),
    ErrorCode.CANVAS_UNAUTHORIZED: ErrorDefinition(
        title="Authentication Failed",
        description="Canvas rejected the API token (HTTP 401).",
    ),
    ErrorCode.CANVAS_FORBIDDEN: ErrorDefinition(
        title="Access Forbidden",
        description="The token is valid but lacks permission for this resource (HTTP 403).",
    ),
    ErrorCode.INVALID_ARGUMENT: ErrorDefinition(
        title="Invalid Argument",
        description="A tool argument or local path validation failed before calling Canvas.",
    ),
    ErrorCode.INVALID_REQUEST: ErrorDefinition(
        title="Invalid Request",
        description="The request parameters are invalid for this tool or Canvas rejected them.",
    ),
    ErrorCode.RESOURCE_NOT_FOUND: ErrorDefinition(
        title="Not Found",
        description="The requested Canvas resource does not exist or is not visible (HTTP 404).",
    ),
    ErrorCode.CANVAS_BAD_REQUEST: ErrorDefinition(
        title="Bad Request",
        description="Canvas rejected the request as malformed (HTTP 400).",
    ),
    ErrorCode.CANVAS_RATE_LIMITED: ErrorDefinition(
        title="Rate Limited",
        retryable=True,
        description="Canvas rate limit exceeded (HTTP 429). Retry after a short delay.",
    ),
    ErrorCode.CANVAS_UNAVAILABLE: ErrorDefinition(
        title="Canvas Unavailable",
        retryable=True,
        description="Canvas returned a server error (HTTP 5xx). Retry later.",
    ),
    ErrorCode.REQUEST_TIMEOUT: ErrorDefinition(
        title="Request Timeout",
        retryable=True,
        description="The HTTP request timed out before Canvas responded.",
    ),
    ErrorCode.NETWORK_ERROR: ErrorDefinition(
        title="Network Error",
        retryable=True,
        description="A network failure occurred while contacting Canvas.",
    ),
    ErrorCode.GRAPHQL_ERROR: ErrorDefinition(
        title="GraphQL Error",
        description="Canvas GraphQL returned errors for the query.",
    ),
    ErrorCode.UNEXPECTED_RESPONSE: ErrorDefinition(
        title="Unexpected Response",
        description="Canvas returned a response shape this tool could not parse.",
    ),
    ErrorCode.UNEXPECTED_ERROR: ErrorDefinition(
        title="Unexpected Error",
        description="An unhandled internal error occurred.",
    ),
    ErrorCode.DOWNLOAD_FAILED: ErrorDefinition(
        title="Download Error",
        description="A file download failed.",
    ),
    ErrorCode.DOWNLOAD_TOO_LARGE: ErrorDefinition(
        title="Download Error",
        description="A file exceeds the configured download size limit.",
    ),
    ErrorCode.DOWNLOAD_URL_REJECTED: ErrorDefinition(
        title="Download Error",
        description="A file download URL failed local security validation.",
    ),
    ErrorCode.DISCUSSION_LOCKED: ErrorDefinition(
        title="Discussion Locked",
        description="You must post before viewing other replies in this discussion.",
    ),
    ErrorCode.DISCUSSION_UNAVAILABLE: ErrorDefinition(
        title="Discussion Unavailable",
        retryable=True,
        description="Canvas has not built the discussion view yet (HTTP 503).",
    ),
    ErrorCode.RUBRIC_NOT_FOUND: ErrorDefinition(
        title="Not Found",
        description="The assignment exists but has no rubric attached.",
    ),
}


def error_title(code: ErrorCode) -> str:
    """Return the short human title for an error code."""
    return ERROR_DEFINITIONS[code].title


def error_retryable(code: ErrorCode) -> bool:
    """Return whether agents should retry after this error code."""
    return ERROR_DEFINITIONS[code].retryable
