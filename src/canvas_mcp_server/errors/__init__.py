"""Structured error model for Canvas MCP tools."""

from .codes import ERROR_DEFINITIONS, ErrorCode, error_retryable, error_title
from .mappers import (
    as_discussion_tool_error,
    as_tool_error,
    discussion_tool_error_from_http,
    tool_error_from_exception,
    tool_error_from_http,
)
from .tool_error import ToolError, is_tool_error, tool_error

__all__ = [
    "ERROR_DEFINITIONS",
    "ErrorCode",
    "ToolError",
    "as_discussion_tool_error",
    "as_tool_error",
    "discussion_tool_error_from_http",
    "error_retryable",
    "error_title",
    "is_tool_error",
    "tool_error",
    "tool_error_from_exception",
    "tool_error_from_http",
]
