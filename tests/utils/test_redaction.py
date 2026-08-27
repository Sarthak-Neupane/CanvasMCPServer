"""Tests for secret redaction helpers."""

from canvas_mcp_server.utils.http_client import HTTPError
from canvas_mcp_server.utils.redaction import (
    redact_headers,
    redact_sensitive_text,
    redact_url,
)


def test_redact_sensitive_text_masks_bearer_token() -> None:
    text = "Authorization: Bearer abc.def-123_~+/="
    redacted = redact_sensitive_text(text)

    assert "abc.def-123" not in redacted
    assert "***REDACTED***" in redacted


def test_redact_url_strips_access_token_query_param() -> None:
    url = "https://canvas.example.edu/api/v1/files/1?access_token=secret123&wrap=1"
    redacted = redact_url(url)

    assert "secret123" not in redacted
    assert "access_token=" in redacted
    assert "REDACTED" in redacted
    assert "wrap=1" in redacted


def test_redact_headers_masks_authorization() -> None:
    headers = redact_headers(
        {
            "Authorization": "Bearer super-secret",
            "Accept": "application/json",
        }
    )

    assert headers["Authorization"] == "Bearer ***REDACTED***"
    assert headers["Accept"] == "application/json"


def test_http_error_str_redacts_token_in_url() -> None:
    error = HTTPError(
        "Request failed",
        status_code=401,
        url="https://canvas.example.edu/api/v1/courses?access_token=secret123",
    )

    rendered = str(error)

    assert "secret123" not in rendered
    assert "access_token=" in rendered
    assert "REDACTED" in rendered
