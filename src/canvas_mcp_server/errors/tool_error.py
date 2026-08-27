"""Structured error payload returned by MCP tools."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .codes import ERROR_DEFINITIONS, ErrorCode, error_retryable, error_title

ErrorSource = Literal["local", "canvas_rest", "canvas_graphql", "download"]


class ToolError(BaseModel):
    """
    Canonical tool failure object.

    Serialized responses always include ``code``, ``message``, ``title`` (short
    label), and ``retryable``. The legacy ``error`` key mirrors ``title`` for
    backward compatibility with earlier tool versions.
    """

    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    message: str
    title: str = Field(description="Short human-readable error category.")
    status_code: Optional[int] = Field(
        default=None,
        description="HTTP status from Canvas when applicable.",
    )
    retryable: bool = Field(
        default=False,
        description="Whether the caller should retry the same request later.",
    )
    source: Optional[ErrorSource] = Field(
        default=None,
        description="Where the failure originated.",
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional structured context (ids, lock reasons, etc.).",
    )

    @classmethod
    def build(
        cls,
        code: ErrorCode,
        message: str,
        *,
        status_code: Optional[int] = None,
        retryable: Optional[bool] = None,
        source: Optional[ErrorSource] = None,
        details: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
    ) -> "ToolError":
        """Create a :class:`ToolError` using registry defaults."""
        definition = ERROR_DEFINITIONS[code]
        return cls(
            code=code,
            message=message,
            title=title or definition.title,
            status_code=status_code,
            retryable=definition.retryable if retryable is None else retryable,
            source=source,
            details=details,
        )

    def to_response(self) -> Dict[str, Any]:
        """Serialize for MCP tool return values."""
        payload: Dict[str, Any] = {
            "code": self.code.value,
            "message": self.message,
            "title": self.title,
            "error": self.title,
            "retryable": self.retryable,
        }
        if self.status_code is not None:
            payload["status_code"] = self.status_code
        if self.source is not None:
            payload["source"] = self.source
        if self.details:
            payload["details"] = self.details
            for key in ("lock_reason", "course_id", "resource_id", "file_id"):
                if key in self.details and key not in payload:
                    payload[key] = self.details[key]
        return payload


def tool_error(
    code: ErrorCode,
    message: str,
    *,
    status_code: Optional[int] = None,
    retryable: Optional[bool] = None,
    source: Optional[ErrorSource] = None,
    details: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
) -> ToolError:
    """Convenience wrapper around :meth:`ToolError.build`."""
    return ToolError.build(
        code,
        message,
        status_code=status_code,
        retryable=retryable,
        source=source,
        details=details,
        title=title,
    )


def is_tool_error(value: Any) -> bool:
    """Return True when ``value`` looks like a serialized :class:`ToolError`."""
    return (
        isinstance(value, dict)
        and isinstance(value.get("code"), str)
        and isinstance(value.get("message"), str)
        and "retryable" in value
    )


def ensure_error_title(code: ErrorCode, title: Optional[str] = None) -> str:
    """Resolve the display title for an error code."""
    return title or error_title(code)


def ensure_error_retryable(code: ErrorCode, retryable: Optional[bool] = None) -> bool:
    """Resolve the retryable flag for an error code."""
    return error_retryable(code) if retryable is None else retryable
