"""Tests for ToolError serialization."""

from canvas_mcp_server.errors import ErrorCode, ToolError, is_tool_error, tool_error


def test_tool_error_to_response_includes_legacy_error_key() -> None:
    payload = tool_error(
        ErrorCode.RESOURCE_NOT_FOUND,
        "Assignment 200001 was not found.",
        status_code=404,
        source="canvas_rest",
    ).to_response()

    assert payload["code"] == "resource_not_found"
    assert payload["title"] == "Not Found"
    assert payload["error"] == "Not Found"
    assert payload["retryable"] is False
    assert payload["status_code"] == 404
    assert payload["source"] == "canvas_rest"


def test_tool_error_promotes_known_detail_keys() -> None:
    payload = tool_error(
        ErrorCode.DISCUSSION_LOCKED,
        "Post before viewing replies.",
        status_code=403,
        details={"lock_reason": "require_initial_post"},
    ).to_response()

    assert payload["lock_reason"] == "require_initial_post"
    assert payload["details"]["lock_reason"] == "require_initial_post"


def test_is_tool_error() -> None:
    payload = ToolError.build(ErrorCode.NETWORK_ERROR, "boom").to_response()
    assert is_tool_error(payload) is True
    assert is_tool_error({"error": "Network Error", "message": "boom"}) is False
